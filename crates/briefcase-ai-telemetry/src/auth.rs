//! Authentication Module
//!
//! This module provides multi-authentication mode support including API keys,
//! JWT tokens, and AWS STS credentials with automatic token refresh and validation.

use crate::config::AuthMode;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use thiserror::Error;
use tokio::sync::RwLock;
use tracing::{debug, error, info, warn};

/// Authentication errors
#[derive(Debug, Error)]
pub enum AuthError {
    #[error("Token validation failed: {0}")]
    TokenValidationError(String),

    #[error("Token expired")]
    TokenExpired,

    #[error("Token refresh failed: {0}")]
    TokenRefreshError(String),

    #[error("Invalid credentials: {0}")]
    InvalidCredentials(String),

    #[error("Network error: {0}")]
    NetworkError(#[from] reqwest::Error),

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("AWS error: {0}")]
    AwsError(String),
}

/// Result type for authentication operations
pub type AuthResult<T> = Result<T, AuthError>;

/// JWT token claims structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JwtClaims {
    pub sub: String, // Subject (user ID)
    pub exp: u64,    // Expiration time
    pub iat: u64,    // Issued at
    pub aud: String, // Audience
    pub iss: String, // Issuer
    #[serde(flatten)]
    pub extra: std::collections::HashMap<String, serde_json::Value>,
}

/// AWS STS credentials structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StsCredentials {
    pub access_key_id: String,
    pub secret_access_key: String,
    pub session_token: Option<String>,
    pub region: String,
    pub expiration: Option<SystemTime>,
}

impl StsCredentials {
    /// Creates new STS credentials
    pub fn new(
        access_key_id: impl Into<String>,
        secret_access_key: impl Into<String>,
        region: impl Into<String>,
    ) -> Self {
        Self {
            access_key_id: access_key_id.into(),
            secret_access_key: secret_access_key.into(),
            session_token: None,
            region: region.into(),
            expiration: None,
        }
    }

    /// Sets session token and expiration
    pub fn with_session_token(
        mut self,
        session_token: impl Into<String>,
        expiration: SystemTime,
    ) -> Self {
        self.session_token = Some(session_token.into());
        self.expiration = Some(expiration);
        self
    }

    /// Checks if credentials are expired
    pub fn is_expired(&self) -> bool {
        if let Some(expiration) = self.expiration {
            SystemTime::now() >= expiration
        } else {
            false
        }
    }

    /// Gets time until expiration
    pub fn time_until_expiration(&self) -> Option<Duration> {
        self.expiration
            .and_then(|exp| exp.duration_since(SystemTime::now()).ok())
    }
}

/// Authentication provider trait
#[async_trait::async_trait]
pub trait AuthProvider: Send + Sync {
    /// Gets the current authentication header value
    async fn get_auth_header(&self) -> AuthResult<String>;

    /// Validates and refreshes authentication if needed
    async fn refresh_if_needed(&mut self) -> AuthResult<()>;

    /// Gets the authentication mode this provider handles
    fn auth_mode(&self) -> &AuthMode;
}

/// API Key authentication provider
pub struct ApiKeyProvider {
    auth_mode: AuthMode,
}

impl ApiKeyProvider {
    /// Creates a new API key provider
    pub fn new(api_key: impl Into<String>) -> Self {
        Self {
            auth_mode: AuthMode::ApiKey {
                key: api_key.into(),
            },
        }
    }
}

#[async_trait::async_trait]
impl AuthProvider for ApiKeyProvider {
    async fn get_auth_header(&self) -> AuthResult<String> {
        match &self.auth_mode {
            AuthMode::ApiKey { key } => {
                if key.starts_with("bca_") {
                    Ok(format!("ApiKey {}", key))
                } else {
                    Ok(format!("Bearer {}", key))
                }
            }
            _ => Err(AuthError::InvalidCredentials(
                "Invalid auth mode for API key provider".to_string(),
            )),
        }
    }

    async fn refresh_if_needed(&mut self) -> AuthResult<()> {
        // API keys don't need refresh
        Ok(())
    }

    fn auth_mode(&self) -> &AuthMode {
        &self.auth_mode
    }
}

/// JWT token authentication provider with automatic refresh
pub struct JwtProvider {
    auth_mode: AuthMode,
    token_cache: Arc<RwLock<Option<String>>>,
    refresh_client: reqwest::Client,
    refresh_endpoint: Option<String>,
}

impl JwtProvider {
    /// Creates a new JWT provider
    pub fn new(token: impl Into<String>) -> Self {
        Self {
            auth_mode: AuthMode::JwtToken {
                token: token.into(),
            },
            token_cache: Arc::new(RwLock::new(None)),
            refresh_client: reqwest::Client::new(),
            refresh_endpoint: None,
        }
    }

    /// Creates a new JWT provider with refresh capability
    pub fn with_refresh_endpoint(
        token: impl Into<String>,
        refresh_endpoint: impl Into<String>,
    ) -> Self {
        Self {
            auth_mode: AuthMode::JwtToken {
                token: token.into(),
            },
            token_cache: Arc::new(RwLock::new(None)),
            refresh_client: reqwest::Client::new(),
            refresh_endpoint: Some(refresh_endpoint.into()),
        }
    }

    /// Parses JWT claims (simplified - would use proper JWT library in production)
    fn parse_jwt_claims(&self, token: &str) -> AuthResult<JwtClaims> {
        // This is a simplified implementation for demonstration
        // In production, use a proper JWT library like `jsonwebtoken`

        let parts: Vec<&str> = token.split('.').collect();
        if parts.len() != 3 {
            return Err(AuthError::TokenValidationError(
                "Invalid JWT format".to_string(),
            ));
        }

        // Decode payload (base64url)
        let payload = parts[1];
        // Simplified base64 decoding - would use proper base64url decoding
        let decoded = base64::decode(payload)
            .map_err(|_| AuthError::TokenValidationError("Invalid base64 encoding".to_string()))?;

        let claims: JwtClaims = serde_json::from_slice(&decoded)
            .map_err(|e| AuthError::TokenValidationError(format!("Invalid JSON: {}", e)))?;

        Ok(claims)
    }

    /// Checks if token is expired
    fn is_token_expired(&self, token: &str) -> bool {
        match self.parse_jwt_claims(token) {
            Ok(claims) => {
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs();
                claims.exp <= now
            }
            Err(_) => true, // Treat invalid tokens as expired
        }
    }

    /// Refreshes the JWT token
    async fn refresh_token(&self, current_token: &str) -> AuthResult<String> {
        let refresh_endpoint = self.refresh_endpoint.as_ref().ok_or_else(|| {
            AuthError::TokenRefreshError("No refresh endpoint configured".to_string())
        })?;

        debug!("Refreshing JWT token");

        let refresh_payload = serde_json::json!({
            "token": current_token,
            "grant_type": "refresh_token"
        });

        let response = self
            .refresh_client
            .post(refresh_endpoint)
            .header("Content-Type", "application/json")
            .json(&refresh_payload)
            .send()
            .await?;

        if response.status().is_success() {
            let refresh_response: serde_json::Value = response.json().await?;
            let new_token = refresh_response
                .get("access_token")
                .and_then(|t| t.as_str())
                .ok_or_else(|| {
                    AuthError::TokenRefreshError("No access_token in response".to_string())
                })?;

            info!("JWT token refreshed successfully");
            Ok(new_token.to_string())
        } else {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            Err(AuthError::TokenRefreshError(format!(
                "HTTP {}: {}",
                status, error_text
            )))
        }
    }
}

#[async_trait::async_trait]
impl AuthProvider for JwtProvider {
    async fn get_auth_header(&self) -> AuthResult<String> {
        // Check if we have a cached token
        if let Some(cached_token) = self.token_cache.read().await.as_ref() {
            if !self.is_token_expired(cached_token) {
                return Ok(format!("Bearer {}", cached_token));
            }
        }

        // Use the original token from auth_mode
        match &self.auth_mode {
            AuthMode::JwtToken { token } => {
                if self.is_token_expired(token) {
                    return Err(AuthError::TokenExpired);
                }
                Ok(format!("Bearer {}", token))
            }
            _ => Err(AuthError::InvalidCredentials(
                "Invalid auth mode for JWT provider".to_string(),
            )),
        }
    }

    async fn refresh_if_needed(&mut self) -> AuthResult<()> {
        let current_token = match &self.auth_mode {
            AuthMode::JwtToken { token } => token.clone(),
            _ => return Ok(()),
        };

        // Check if token needs refresh
        if !self.is_token_expired(&current_token) {
            return Ok(());
        }

        // Refresh token if endpoint is configured
        if self.refresh_endpoint.is_some() {
            match self.refresh_token(&current_token).await {
                Ok(new_token) => {
                    // Update cached token
                    *self.token_cache.write().await = Some(new_token.clone());

                    // Update auth_mode with new token
                    self.auth_mode = AuthMode::JwtToken { token: new_token };

                    info!("JWT token refreshed and updated");
                    Ok(())
                }
                Err(e) => {
                    warn!("Failed to refresh JWT token: {}", e);
                    Err(e)
                }
            }
        } else {
            Err(AuthError::TokenExpired)
        }
    }

    fn auth_mode(&self) -> &AuthMode {
        &self.auth_mode
    }
}

/// AWS STS credentials provider with automatic refresh
pub struct StsCredentialProvider {
    auth_mode: AuthMode,
    credentials: Arc<RwLock<StsCredentials>>,
    role_arn: Option<String>,
    http_client: reqwest::Client,
}

impl StsCredentialProvider {
    /// Creates a new STS credential provider
    pub fn new(
        access_key_id: impl Into<String>,
        secret_access_key: impl Into<String>,
        region: impl Into<String>,
    ) -> Self {
        let credentials = StsCredentials::new(access_key_id, secret_access_key, region);

        Self {
            auth_mode: AuthMode::StsCredentials {
                access_key_id: credentials.access_key_id.clone(),
                secret_access_key: credentials.secret_access_key.clone(),
                session_token: credentials.session_token.clone(),
                region: credentials.region.clone(),
            },
            credentials: Arc::new(RwLock::new(credentials)),
            role_arn: None,
            http_client: reqwest::Client::new(),
        }
    }

    /// Creates a new STS credential provider with role assumption
    pub fn with_role_arn(
        access_key_id: impl Into<String>,
        secret_access_key: impl Into<String>,
        region: impl Into<String>,
        role_arn: impl Into<String>,
    ) -> Self {
        let mut provider = Self::new(access_key_id, secret_access_key, region);
        provider.role_arn = Some(role_arn.into());
        provider
    }

    /// Assumes IAM role and gets temporary credentials
    async fn assume_role(&self, role_arn: &str) -> AuthResult<StsCredentials> {
        debug!("Assuming IAM role: {}", role_arn);

        // This is a simplified implementation
        // In production, use the AWS SDK for STS operations

        // TODO: Implement actual STS AssumeRole API call
        // Example structure:
        // let sts_client = aws_sdk_sts::Client::new(&aws_config);
        // let assume_role_output = sts_client
        //     .assume_role()
        //     .role_arn(role_arn)
        //     .role_session_name("briefcase-ai-telemetry-session")
        //     .send()
        //     .await?;

        // For now, simulate the response
        warn!("STS AssumeRole not fully implemented - using placeholder credentials");

        let creds = self.credentials.read().await.clone();
        let expiration = SystemTime::now() + Duration::from_secs(3600); // 1 hour

        Ok(creds.with_session_token("simulated_session_token", expiration))
    }

    /// Refreshes session token
    async fn refresh_session_token(&self) -> AuthResult<StsCredentials> {
        debug!("Refreshing STS session token");

        // This is a simplified implementation
        // In production, use the AWS SDK for STS operations

        // TODO: Implement actual STS GetSessionToken API call
        // Example structure:
        // let sts_client = aws_sdk_sts::Client::new(&aws_config);
        // let session_token_output = sts_client
        //     .get_session_token()
        //     .duration_seconds(3600)
        //     .send()
        //     .await?;

        // For now, simulate the response
        warn!("STS GetSessionToken not fully implemented - using placeholder credentials");

        let creds = self.credentials.read().await.clone();
        let expiration = SystemTime::now() + Duration::from_secs(3600); // 1 hour

        Ok(creds.with_session_token("refreshed_session_token", expiration))
    }

    /// Gets AWS signature for requests (simplified)
    fn generate_aws_signature(&self, credentials: &StsCredentials) -> String {
        // This is a simplified implementation
        // In production, use proper AWS Signature Version 4 implementation

        format!(
            "AWS4-HMAC-SHA256 Credential={}/{}/us-east-1/kinesis/aws4_request",
            credentials.access_key_id,
            chrono::Utc::now().format("%Y%m%d")
        )
    }
}

#[async_trait::async_trait]
impl AuthProvider for StsCredentialProvider {
    async fn get_auth_header(&self) -> AuthResult<String> {
        let credentials = self.credentials.read().await;

        // Generate AWS signature
        let signature = self.generate_aws_signature(&*credentials);

        Ok(signature)
    }

    async fn refresh_if_needed(&mut self) -> AuthResult<()> {
        let credentials = self.credentials.read().await;

        // Check if credentials are expired
        if !credentials.is_expired() {
            return Ok(());
        }

        drop(credentials); // Release read lock

        // Refresh credentials
        let new_credentials = if let Some(role_arn) = &self.role_arn {
            self.assume_role(role_arn).await?
        } else {
            self.refresh_session_token().await?
        };

        // Update stored credentials
        *self.credentials.write().await = new_credentials.clone();

        // Update auth_mode
        self.auth_mode = AuthMode::StsCredentials {
            access_key_id: new_credentials.access_key_id,
            secret_access_key: new_credentials.secret_access_key,
            session_token: new_credentials.session_token,
            region: new_credentials.region,
        };

        info!("STS credentials refreshed successfully");
        Ok(())
    }

    fn auth_mode(&self) -> &AuthMode {
        &self.auth_mode
    }
}

/// Authentication manager that handles multiple auth providers
pub struct AuthManager {
    provider: Box<dyn AuthProvider>,
}

impl AuthManager {
    /// Creates a new authentication manager
    pub fn new(auth_mode: &AuthMode) -> AuthResult<Self> {
        let provider: Box<dyn AuthProvider> = match auth_mode {
            AuthMode::ApiKey { key } => Box::new(ApiKeyProvider::new(key.clone())),
            AuthMode::JwtToken { token } => Box::new(JwtProvider::new(token.clone())),
            AuthMode::StsCredentials {
                access_key_id,
                secret_access_key,
                region,
                ..
            } => Box::new(StsCredentialProvider::new(
                access_key_id.clone(),
                secret_access_key.clone(),
                region.clone(),
            )),
        };

        Ok(Self { provider })
    }

    /// Creates a new authentication manager with JWT refresh capability
    pub fn new_with_jwt_refresh(
        token: impl Into<String>,
        refresh_endpoint: impl Into<String>,
    ) -> AuthResult<Self> {
        let provider = Box::new(JwtProvider::with_refresh_endpoint(token, refresh_endpoint));
        Ok(Self { provider })
    }

    /// Creates a new authentication manager with STS role assumption
    pub fn new_with_sts_role(
        access_key_id: impl Into<String>,
        secret_access_key: impl Into<String>,
        region: impl Into<String>,
        role_arn: impl Into<String>,
    ) -> AuthResult<Self> {
        let provider = Box::new(StsCredentialProvider::with_role_arn(
            access_key_id,
            secret_access_key,
            region,
            role_arn,
        ));
        Ok(Self { provider })
    }

    /// Gets the current authentication header
    pub async fn get_auth_header(&self) -> AuthResult<String> {
        self.provider.get_auth_header().await
    }

    /// Refreshes authentication if needed
    pub async fn refresh_if_needed(&mut self) -> AuthResult<()> {
        self.provider.refresh_if_needed().await
    }

    /// Gets the authentication mode
    pub fn auth_mode(&self) -> &AuthMode {
        self.provider.auth_mode()
    }
}

// Add base64 as a simple placeholder - in production use proper base64url crate
mod base64 {
    pub fn decode(_input: &str) -> Result<Vec<u8>, &'static str> {
        // Simplified base64 decoding for demonstration
        // In production, use a proper base64 library
        Err("Base64 decoding not implemented in demo")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sts_credentials_creation() {
        let creds = StsCredentials::new("access_key", "secret_key", "us-east-1");

        assert_eq!(creds.access_key_id, "access_key");
        assert_eq!(creds.secret_access_key, "secret_key");
        assert_eq!(creds.region, "us-east-1");
        assert!(creds.session_token.is_none());
        assert!(!creds.is_expired());
    }

    #[test]
    fn test_sts_credentials_with_session_token() {
        let expiration = SystemTime::now() + Duration::from_secs(3600);
        let creds = StsCredentials::new("access_key", "secret_key", "us-east-1")
            .with_session_token("session_token", expiration);

        assert_eq!(creds.session_token, Some("session_token".to_string()));
        assert!(!creds.is_expired());
    }

    #[test]
    fn test_sts_credentials_expired() {
        let expiration = SystemTime::now() - Duration::from_secs(1); // 1 second ago
        let creds = StsCredentials::new("access_key", "secret_key", "us-east-1")
            .with_session_token("session_token", expiration);

        assert!(creds.is_expired());
    }

    #[tokio::test]
    async fn test_api_key_provider() {
        let provider = ApiKeyProvider::new("bca_test_key");

        let auth_header = provider.get_auth_header().await.unwrap();
        assert_eq!(auth_header, "ApiKey bca_test_key");

        // Test non-bca key
        let provider2 = ApiKeyProvider::new("other_key");
        let auth_header2 = provider2.get_auth_header().await.unwrap();
        assert_eq!(auth_header2, "Bearer other_key");
    }

    #[tokio::test]
    async fn test_jwt_provider() {
        let provider = JwtProvider::new("jwt_token_123");

        let auth_header = provider.get_auth_header().await.unwrap();
        assert_eq!(auth_header, "Bearer jwt_token_123");
    }

    #[tokio::test]
    async fn test_sts_credential_provider() {
        let provider = StsCredentialProvider::new("access_key", "secret_key", "us-east-1");

        let auth_header = provider.get_auth_header().await.unwrap();
        assert!(auth_header.starts_with("AWS4-HMAC-SHA256"));
    }

    #[tokio::test]
    async fn test_auth_manager_api_key() {
        let auth_mode = AuthMode::ApiKey {
            key: "test_key".to_string(),
        };
        let manager = AuthManager::new(&auth_mode).unwrap();

        let auth_header = manager.get_auth_header().await.unwrap();
        assert_eq!(auth_header, "Bearer test_key");
    }

    #[tokio::test]
    async fn test_auth_manager_jwt() {
        let auth_mode = AuthMode::JwtToken {
            token: "jwt_token".to_string(),
        };
        let manager = AuthManager::new(&auth_mode).unwrap();

        let auth_header = manager.get_auth_header().await.unwrap();
        assert_eq!(auth_header, "Bearer jwt_token");
    }

    #[tokio::test]
    async fn test_auth_manager_sts() {
        let auth_mode = AuthMode::StsCredentials {
            access_key_id: "access_key".to_string(),
            secret_access_key: "secret_key".to_string(),
            session_token: None,
            region: "us-east-1".to_string(),
        };
        let manager = AuthManager::new(&auth_mode).unwrap();

        let auth_header = manager.get_auth_header().await.unwrap();
        assert!(auth_header.starts_with("AWS4-HMAC-SHA256"));
    }
}
