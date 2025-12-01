//! LakeFS Direct Protocol Client Implementation
//!
//! This module provides the LakeFS Direct protocol client for data versioning
//! and lineage tracking with direct LakeFS integration.

use super::{ProtocolClient, ProtocolError, ProtocolResult};
use crate::config::{AuthMode, EndpointType, EnhancedTelemetryConfig};
use async_trait::async_trait;
use reqwest::Client as HttpClient;
use serde::{Deserialize, Serialize};
use serde_json::json;
use tracing::{debug, error, info, warn};

/// Base64 encoding helper (simple implementation without external dependency)
fn base64_encode(input: &str) -> String {
    const CHARSET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let bytes = input.as_bytes();
    let mut result = String::new();

    for chunk in bytes.chunks(3) {
        let b0 = chunk[0] as usize;
        let b1 = chunk.get(1).copied().unwrap_or(0) as usize;
        let b2 = chunk.get(2).copied().unwrap_or(0) as usize;

        result.push(CHARSET[b0 >> 2] as char);
        result.push(CHARSET[((b0 & 0x03) << 4) | (b1 >> 4)] as char);

        if chunk.len() > 1 {
            result.push(CHARSET[((b1 & 0x0f) << 2) | (b2 >> 6)] as char);
        } else {
            result.push('=');
        }

        if chunk.len() > 2 {
            result.push(CHARSET[b2 & 0x3f] as char);
        } else {
            result.push('=');
        }
    }

    result
}

/// LakeFS API response for object upload
#[derive(Debug, Deserialize)]
struct LakeFSObjectResponse {
    #[allow(dead_code)]
    path: String,
    #[allow(dead_code)]
    physical_address: Option<String>,
    #[allow(dead_code)]
    checksum: String,
    #[allow(dead_code)]
    size_bytes: i64,
    #[allow(dead_code)]
    mtime: i64,
}

/// LakeFS API response for commit
#[derive(Debug, Deserialize)]
struct LakeFSCommitResponse {
    #[allow(dead_code)]
    id: String,
    #[allow(dead_code)]
    parents: Vec<String>,
    #[allow(dead_code)]
    committer: String,
    #[allow(dead_code)]
    message: String,
}

/// LakeFS commit request payload
#[derive(Debug, Serialize)]
struct LakeFSCommitRequest {
    message: String,
    metadata: Option<serde_json::Value>,
}

/// LakeFS repository info
#[derive(Debug, Deserialize)]
struct LakeFSRepositoryInfo {
    #[allow(dead_code)]
    id: String,
    #[allow(dead_code)]
    default_branch: String,
    #[allow(dead_code)]
    storage_namespace: String,
}

/// LakeFS Direct protocol client for data versioning and lineage tracking
#[derive(Debug)]
pub struct LakeFSDirectClient {
    config: EnhancedTelemetryConfig,
    http_client: HttpClient,
    repository: String,
    branch: String,
    base_path: String,
    auto_commit: bool,
}

impl LakeFSDirectClient {
    /// Creates a new LakeFS Direct client
    pub fn new(config: &EnhancedTelemetryConfig) -> ProtocolResult<Self> {
        // Validate configuration
        if config.endpoint_type != EndpointType::LakefsDirect {
            return Err(ProtocolError::ConfigurationError(
                "Invalid endpoint type for LakeFS Direct client".to_string(),
            ));
        }

        // Validate authentication mode (STS credentials for S3 backend, or LakeFS access keys)
        let _credentials = match &config.auth {
            AuthMode::StsCredentials {
                access_key_id,
                secret_access_key,
                region,
                ..
            } => {
                if access_key_id.is_empty() || secret_access_key.is_empty() || region.is_empty() {
                    return Err(ProtocolError::ConfigurationError(
                        "AWS credentials cannot be empty for LakeFS Direct client".to_string(),
                    ));
                }
                (access_key_id, secret_access_key, region)
            }
            AuthMode::ApiKey { key } => {
                if key.is_empty() {
                    return Err(ProtocolError::ConfigurationError(
                        "LakeFS access key cannot be empty".to_string(),
                    ));
                }
                (key, &"".to_string(), &"".to_string())
            }
            _ => {
                return Err(ProtocolError::ConfigurationError(
                    "LakeFS Direct client requires STS credentials or API key authentication".to_string(),
                ));
            }
        };

        // Validate endpoint URL
        if config.endpoint_url.is_empty() {
            return Err(ProtocolError::ConfigurationError(
                "LakeFS endpoint URL cannot be empty".to_string(),
            ));
        }

        // Extract LakeFS-specific configuration
        let lakefs_config = config.protocol_configs
            .get(&EndpointType::LakefsDirect)
            .ok_or_else(|| ProtocolError::ConfigurationError(
                "Missing LakeFS Direct protocol configuration".to_string(),
            ))?;

        let repository = lakefs_config
            .get("repository")
            .and_then(|v| v.as_str())
            .ok_or_else(|| ProtocolError::ConfigurationError(
                "Missing repository in LakeFS configuration".to_string(),
            ))?
            .to_string();

        let branch = lakefs_config
            .get("branch")
            .and_then(|v| v.as_str())
            .unwrap_or("main")
            .to_string();

        let base_path = lakefs_config
            .get("base_path")
            .and_then(|v| v.as_str())
            .unwrap_or("/telemetry")
            .to_string();

        let auto_commit = lakefs_config
            .get("auto_commit")
            .and_then(|v| v.as_bool())
            .unwrap_or(true);

        let http_client = HttpClient::builder()
            .timeout(config.timeout)
            .build()
            .map_err(ProtocolError::NetworkError)?;

        Ok(Self {
            config: config.clone(),
            http_client,
            repository,
            branch,
            base_path,
            auto_commit,
        })
    }

    /// Gets the authorization header for LakeFS requests
    fn get_auth_header(&self) -> ProtocolResult<(String, String)> {
        match &self.config.auth {
            AuthMode::ApiKey { key } => {
                // For LakeFS API key auth, use Basic auth with access_key:secret_key format
                // The key is expected to be in "access_key_id:secret_access_key" format
                let encoded = base64_encode(key);
                Ok(("Authorization".to_string(), format!("Basic {}", encoded)))
            }
            AuthMode::StsCredentials { access_key_id, secret_access_key, .. } => {
                // For LakeFS with STS credentials, use Basic auth
                let credentials = format!("{}:{}", access_key_id, secret_access_key);
                let encoded = base64_encode(&credentials);
                Ok(("Authorization".to_string(), format!("Basic {}", encoded)))
            }
            _ => Err(ProtocolError::AuthenticationError(
                "Invalid authentication mode for LakeFS Direct client".to_string(),
            )),
        }
    }

    /// Constructs the LakeFS API base URL
    fn api_base_url(&self) -> String {
        format!("{}/api/v1", self.config.endpoint_url.trim_end_matches('/'))
    }

    /// Generates file path for telemetry data
    fn generate_file_path(&self, data: &serde_json::Value) -> String {
        let now = chrono::Utc::now();
        let date_path = now.format("%Y/%m/%d").to_string();

        let session_id = data.get("session")
            .and_then(|s| s.get("id"))
            .and_then(|id| id.as_str())
            .unwrap_or("unknown");

        let org_id = self.config.organization
            .as_ref()
            .map(|org| org.org_id.as_str())
            .unwrap_or("default");

        format!("{}/{}/{}/session_{}.json", self.base_path, org_id, date_path, session_id)
    }

    /// Formats data for LakeFS commit
    fn format_lakefs_commit(&self, data: serde_json::Value, file_path: String) -> ProtocolResult<serde_json::Value> {
        let commit_metadata = json!({
            "message": format!("Telemetry data from {} at {}",
                self.config.organization
                    .as_ref()
                    .map(|org| org.agent_group.as_str())
                    .unwrap_or("unknown"),
                chrono::Utc::now()
            ),
            "committer": "briefcase-ai-sdk"
        });

        let mut enhanced_data = data;

        // Add organization context if present
        if let Some(org) = &self.config.organization {
            if let Some(obj) = enhanced_data.as_object_mut() {
                obj.insert("organization".to_string(), serde_json::to_value(org)?);
            }
        }

        // Add experiment context if present
        if !self.config.experiments.is_empty() {
            if let Some(obj) = enhanced_data.as_object_mut() {
                obj.insert("experiments".to_string(), serde_json::to_value(&self.config.experiments)?);
            }
        }

        Ok(json!({
            "lakefs_metadata": {
                "repository": self.repository,
                "branch": self.branch,
                "path": file_path,
                "commit_metadata": commit_metadata
            },
            "telemetry_data": enhanced_data
        }))
    }

    /// Uploads data to LakeFS using the LakeFS API
    async fn upload_to_lakefs(&self, commits: Vec<serde_json::Value>) -> ProtocolResult<()> {
        debug!("Uploading {} commits to LakeFS repository: {}", commits.len(), self.repository);

        let (auth_header_name, auth_header_value) = self.get_auth_header()?;
        let base_url = self.api_base_url();

        let mut uploaded_paths: Vec<String> = Vec::new();

        for (i, commit) in commits.iter().enumerate() {
            let lakefs_metadata = commit.get("lakefs_metadata")
                .ok_or_else(|| ProtocolError::ConfigurationError(
                    "Missing lakefs_metadata in commit data".to_string()
                ))?;
            let file_path = lakefs_metadata.get("path")
                .and_then(|v| v.as_str())
                .ok_or_else(|| ProtocolError::ConfigurationError(
                    "Missing path in lakefs_metadata".to_string()
                ))?;
            let telemetry_data = commit.get("telemetry_data")
                .ok_or_else(|| ProtocolError::ConfigurationError(
                    "Missing telemetry_data in commit data".to_string()
                ))?;

            // Serialize telemetry data to JSON bytes
            let content = serde_json::to_vec_pretty(telemetry_data)
                .map_err(ProtocolError::SerializationError)?;

            debug!("Uploading object {}: path={}, size={} bytes", i, file_path, content.len());

            // Upload object to LakeFS
            // PUT /repositories/{repository}/branches/{branch}/objects?path={path}
            let upload_url = format!(
                "{}/repositories/{}/branches/{}/objects?path={}",
                base_url,
                self.repository,
                self.branch,
                urlencoding::encode(file_path)
            );

            let response = self.http_client
                .post(&upload_url)
                .header(&auth_header_name, &auth_header_value)
                .header("Content-Type", "application/octet-stream")
                .body(content)
                .send()
                .await
                .map_err(ProtocolError::NetworkError)?;

            if !response.status().is_success() {
                let status = response.status();
                let error_text = response.text().await.unwrap_or_default();
                error!("Failed to upload object to LakeFS: {} - {}", status, error_text);
                return Err(ProtocolError::ConfigurationError(
                    format!("LakeFS upload failed with status {}: {}", status, error_text)
                ));
            }

            // Parse response to confirm upload
            let _upload_response: LakeFSObjectResponse = response.json().await
                .map_err(|e| {
                    warn!("Could not parse LakeFS response, continuing: {}", e);
                    e
                })
                .unwrap_or(LakeFSObjectResponse {
                    path: file_path.to_string(),
                    physical_address: None,
                    checksum: String::new(),
                    size_bytes: 0,
                    mtime: 0,
                });

            uploaded_paths.push(file_path.to_string());
            info!("Successfully uploaded to LakeFS: {}/{}{}", self.repository, self.branch, file_path);
        }

        // Create commit if auto_commit is enabled and we uploaded files
        if self.auto_commit && !uploaded_paths.is_empty() {
            debug!("Auto-commit enabled, creating commit for {} objects", uploaded_paths.len());

            let commit_url = format!(
                "{}/repositories/{}/branches/{}/commits",
                base_url,
                self.repository,
                self.branch
            );

            let commit_message = format!(
                "Telemetry upload: {} objects from {}",
                uploaded_paths.len(),
                self.config.organization
                    .as_ref()
                    .map(|org| org.agent_group.as_str())
                    .unwrap_or("briefcase-sdk")
            );

            let commit_request = LakeFSCommitRequest {
                message: commit_message,
                metadata: Some(json!({
                    "source": "briefcase-ai-telemetry-sdk",
                    "timestamp": chrono::Utc::now().to_rfc3339(),
                    "object_count": uploaded_paths.len(),
                    "paths": uploaded_paths
                })),
            };

            let commit_response = self.http_client
                .post(&commit_url)
                .header(&auth_header_name, &auth_header_value)
                .header("Content-Type", "application/json")
                .json(&commit_request)
                .send()
                .await
                .map_err(ProtocolError::NetworkError)?;

            if !commit_response.status().is_success() {
                let status = commit_response.status();
                let error_text = commit_response.text().await.unwrap_or_default();
                warn!("Failed to create commit in LakeFS: {} - {}", status, error_text);
                // Don't fail the whole operation if commit fails, objects are already uploaded
            } else {
                let commit_info: LakeFSCommitResponse = commit_response.json().await
                    .unwrap_or(LakeFSCommitResponse {
                        id: String::new(),
                        parents: vec![],
                        committer: String::new(),
                        message: String::new(),
                    });
                info!("Created LakeFS commit: {}", commit_info.id);
            }
        }

        info!("Successfully uploaded {} commits to LakeFS repository: {}", commits.len(), self.repository);
        Ok(())
    }
}

#[async_trait]
impl ProtocolClient for LakeFSDirectClient {
    async fn send_telemetry(&self, data: &[u8]) -> ProtocolResult<()> {
        debug!("Sending telemetry data via LakeFS Direct protocol");

        // Parse the data
        let payload_data = serde_json::from_slice::<serde_json::Value>(data)
            .map_err(ProtocolError::SerializationError)?;

        // Generate file path
        let file_path = self.generate_file_path(&payload_data);

        // Format as LakeFS commit
        let lakefs_commit = self.format_lakefs_commit(payload_data, file_path)?;

        // Upload to LakeFS
        self.upload_to_lakefs(vec![lakefs_commit]).await?;

        info!("Telemetry data sent successfully via LakeFS Direct");
        Ok(())
    }

    async fn send_agent_run(&self, data: &serde_json::Value) -> ProtocolResult<()> {
        debug!("Sending agent run data via LakeFS Direct protocol");

        // Add record type for agent runs
        let mut agent_data = data.clone();
        if let Some(obj) = agent_data.as_object_mut() {
            obj.insert("record_type".to_string(), serde_json::Value::String("agent_run".to_string()));
        }

        // Generate file path
        let file_path = self.generate_file_path(&agent_data);

        // Format as LakeFS commit
        let lakefs_commit = self.format_lakefs_commit(agent_data, file_path)?;

        // Upload to LakeFS
        self.upload_to_lakefs(vec![lakefs_commit]).await?;

        info!("Agent run data sent successfully via LakeFS Direct");
        Ok(())
    }

    async fn send_batch(&self, records: &[serde_json::Value]) -> ProtocolResult<()> {
        debug!("Sending batch data via LakeFS Direct protocol");

        if records.is_empty() {
            return Ok(());
        }

        // Convert all records to LakeFS commits
        let mut lakefs_commits = Vec::new();
        for (i, record) in records.iter().enumerate() {
            let mut batch_record = record.clone();
            if let Some(obj) = batch_record.as_object_mut() {
                obj.insert("record_type".to_string(), serde_json::Value::String("batch".to_string()));
                obj.insert("batch_index".to_string(), serde_json::Value::Number(i.into()));
            }

            let file_path = format!("{}_batch_{}.json", self.generate_file_path(&batch_record), i);
            let lakefs_commit = self.format_lakefs_commit(batch_record, file_path)?;
            lakefs_commits.push(lakefs_commit);
        }

        // Upload batch to LakeFS
        self.upload_to_lakefs(lakefs_commits).await?;

        info!("Batch data ({} records) sent successfully via LakeFS Direct", records.len());
        Ok(())
    }

    fn validate_config(&self, config: &EnhancedTelemetryConfig) -> ProtocolResult<()> {
        // Check endpoint type
        if config.endpoint_type != EndpointType::LakefsDirect {
            return Err(ProtocolError::ConfigurationError(
                "Invalid endpoint type for LakeFS Direct client".to_string(),
            ));
        }

        // Check authentication mode
        match &config.auth {
            AuthMode::StsCredentials { access_key_id, secret_access_key, region, .. } => {
                if access_key_id.is_empty() || secret_access_key.is_empty() || region.is_empty() {
                    return Err(ProtocolError::ConfigurationError(
                        "AWS credentials cannot be empty".to_string(),
                    ));
                }
            }
            AuthMode::ApiKey { key } => {
                if key.is_empty() {
                    return Err(ProtocolError::ConfigurationError(
                        "LakeFS access key cannot be empty".to_string(),
                    ));
                }
            }
            _ => {
                return Err(ProtocolError::ConfigurationError(
                    "LakeFS Direct client requires STS credentials or API key authentication".to_string(),
                ));
            }
        }

        // Check endpoint URL
        if config.endpoint_url.is_empty() {
            return Err(ProtocolError::ConfigurationError(
                "LakeFS endpoint URL cannot be empty".to_string(),
            ));
        }

        // Check for LakeFS-specific configuration
        let lakefs_config = config.protocol_configs
            .get(&EndpointType::LakefsDirect)
            .ok_or_else(|| ProtocolError::ConfigurationError(
                "Missing LakeFS Direct protocol configuration".to_string(),
            ))?;

        // Validate repository
        let repository = lakefs_config
            .get("repository")
            .and_then(|v| v.as_str())
            .ok_or_else(|| ProtocolError::ConfigurationError(
                "Missing repository in LakeFS configuration".to_string(),
            ))?;

        if repository.is_empty() {
            return Err(ProtocolError::ConfigurationError(
                "LakeFS repository cannot be empty".to_string(),
            ));
        }

        Ok(())
    }

    fn protocol_type(&self) -> EndpointType {
        EndpointType::LakefsDirect
    }

    async fn health_check(&self) -> ProtocolResult<()> {
        debug!("Performing health check for LakeFS Direct client");

        // Validate configuration first
        self.validate_config(&self.config)?;

        // Get auth header
        let (auth_header_name, auth_header_value) = self.get_auth_header()?;
        let base_url = self.api_base_url();

        // Check repository exists and is accessible
        let repo_url = format!("{}/repositories/{}", base_url, self.repository);

        debug!("Checking LakeFS repository at: {}", repo_url);

        let response = self.http_client
            .get(&repo_url)
            .header(&auth_header_name, &auth_header_value)
            .send()
            .await
            .map_err(ProtocolError::NetworkError)?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();

            if status.as_u16() == 404 {
                return Err(ProtocolError::ConfigurationError(
                    format!("LakeFS repository '{}' not found", self.repository)
                ));
            } else if status.as_u16() == 401 || status.as_u16() == 403 {
                return Err(ProtocolError::AuthenticationError(
                    format!("Authentication failed for LakeFS repository '{}': {}", self.repository, error_text)
                ));
            } else {
                return Err(ProtocolError::ConfigurationError(
                    format!("LakeFS health check failed with status {}: {}", status, error_text)
                ));
            }
        }

        // Parse repository info to verify it's a valid response
        let _repo_info: LakeFSRepositoryInfo = response.json().await
            .map_err(|e| ProtocolError::ConfigurationError(
                format!("Invalid repository info response: {}", e)
            ))?;

        // Check branch exists
        let branch_url = format!("{}/repositories/{}/branches/{}", base_url, self.repository, self.branch);
        let branch_response = self.http_client
            .get(&branch_url)
            .header(&auth_header_name, &auth_header_value)
            .send()
            .await
            .map_err(ProtocolError::NetworkError)?;

        if !branch_response.status().is_success() {
            let status = branch_response.status();
            if status.as_u16() == 404 {
                warn!("Branch '{}' not found in repository '{}', will be created on first commit", self.branch, self.repository);
                // Don't fail - branch might be created on first write
            }
        }

        info!("LakeFS Direct health check passed - repository '{}' accessible", self.repository);
        Ok(())
    }

    async fn shutdown(&mut self) -> ProtocolResult<()> {
        debug!("Shutting down LakeFS Direct client");

        // Log shutdown for tracing purposes
        info!("LakeFS Direct client shutting down - repository: {}, branch: {}",
            self.repository, self.branch);

        // HTTP client connections are managed automatically by reqwest
        // No explicit cleanup needed for connection pool

        debug!("LakeFS Direct client shutdown complete");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::*;

    fn create_test_config_sts() -> EnhancedTelemetryConfig {
        let mut config = EnhancedTelemetryConfig::with_sts_credentials(
            "AKIA123456789",
            "secret_access_key",
            "us-east-1",
            "stream" // Not used for LakeFS
        );

        // Override endpoint type and add LakeFS config
        config.endpoint_type = EndpointType::LakefsDirect;
        config.endpoint_url = "https://lakefs.example.com".to_string();
        config.protocol_configs.insert(
            EndpointType::LakefsDirect,
            serde_json::json!({
                "repository": "briefcase-telemetry",
                "branch": "main",
                "base_path": "/telemetry",
                "auto_commit": true
            })
        );

        config
    }

    fn create_test_config_api_key() -> EnhancedTelemetryConfig {
        let mut config = EnhancedTelemetryConfig::with_api_key("lakefs_access_key");
        config.endpoint_type = EndpointType::LakefsDirect;
        config.endpoint_url = "https://lakefs.example.com".to_string();
        config.protocol_configs.insert(
            EndpointType::LakefsDirect,
            serde_json::json!({
                "repository": "briefcase-telemetry",
                "branch": "main",
                "base_path": "/telemetry",
                "auto_commit": false
            })
        );

        config
    }

    #[test]
    fn test_lakefs_client_creation_sts() {
        let config = create_test_config_sts();
        let client = LakeFSDirectClient::new(&config);
        assert!(client.is_ok());
    }

    #[test]
    fn test_lakefs_client_creation_api_key() {
        let config = create_test_config_api_key();
        let client = LakeFSDirectClient::new(&config);
        assert!(client.is_ok());
    }

    #[test]
    fn test_lakefs_client_invalid_endpoint_type() {
        let config = EnhancedTelemetryConfig::with_api_key("key")
            .with_endpoint(EndpointType::RestApi, "https://example.com");

        let client = LakeFSDirectClient::new(&config);
        assert!(client.is_err());
        assert!(matches!(client.unwrap_err(), ProtocolError::ConfigurationError(_)));
    }

    #[test]
    fn test_lakefs_client_invalid_auth_mode() {
        let config = EnhancedTelemetryConfig::with_jwt_token("token")
            .with_endpoint(EndpointType::LakefsDirect, "https://lakefs.example.com");

        let client = LakeFSDirectClient::new(&config);
        assert!(client.is_err());
        assert!(matches!(client.unwrap_err(), ProtocolError::ConfigurationError(_)));
    }

    #[test]
    fn test_generate_file_path() {
        let org_context = OrganizationContext::new("org_123", "ml_agents");
        let config = create_test_config_sts().with_organization(org_context);
        let client = LakeFSDirectClient::new(&config).unwrap();

        let data = json!({
            "session": {
                "id": "session_456"
            }
        });

        let file_path = client.generate_file_path(&data);
        assert!(file_path.contains("org_123"));
        assert!(file_path.contains("session_456"));
        assert!(file_path.starts_with("/telemetry"));
        assert!(file_path.ends_with(".json"));
    }

    #[test]
    fn test_format_lakefs_commit() {
        let config = create_test_config_sts();
        let client = LakeFSDirectClient::new(&config).unwrap();

        let test_data = json!({
            "test": "data",
            "number": 42
        });

        let file_path = "/telemetry/test/session_123.json".to_string();
        let formatted = client.format_lakefs_commit(test_data, file_path).unwrap();

        // Check structure
        assert!(formatted.get("lakefs_metadata").is_some());
        assert!(formatted.get("telemetry_data").is_some());

        let metadata = formatted.get("lakefs_metadata").unwrap();
        assert_eq!(metadata.get("repository").unwrap(), "briefcase-telemetry");
        assert_eq!(metadata.get("branch").unwrap(), "main");
        assert_eq!(metadata.get("path").unwrap(), "/telemetry/test/session_123.json");

        let data = formatted.get("telemetry_data").unwrap();
        assert_eq!(data.get("test").unwrap(), "data");
        assert_eq!(data.get("number").unwrap(), 42);
    }

    #[test]
    fn test_format_lakefs_commit_with_organization() {
        let org_context = OrganizationContext::new("org_123", "ml_agents");
        let config = create_test_config_sts().with_organization(org_context);
        let client = LakeFSDirectClient::new(&config).unwrap();

        let test_data = json!({ "test": "data" });
        let file_path = "/test.json".to_string();
        let formatted = client.format_lakefs_commit(test_data, file_path).unwrap();

        let data = formatted.get("telemetry_data").unwrap();
        assert!(data.get("organization").is_some());

        let org = data.get("organization").unwrap();
        assert_eq!(org.get("org_id").unwrap(), "org_123");
        assert_eq!(org.get("agent_group").unwrap(), "ml_agents");
    }

    #[test]
    fn test_validate_config_valid_sts() {
        let config = create_test_config_sts();
        let client = LakeFSDirectClient::new(&config).unwrap();

        let result = client.validate_config(&config);
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_config_valid_api_key() {
        let config = create_test_config_api_key();
        let client = LakeFSDirectClient::new(&config).unwrap();

        let result = client.validate_config(&config);
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_config_missing_repository() {
        let config = create_test_config_sts();
        let client = LakeFSDirectClient::new(&config).unwrap();

        // Remove the protocol config to simulate missing repository
        let mut invalid_config = config.clone();
        invalid_config.protocol_configs.clear();

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_config_empty_endpoint_url() {
        let config = create_test_config_sts();
        let client = LakeFSDirectClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            endpoint_url: "".to_string(),
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_protocol_type() {
        let config = create_test_config_sts();
        let client = LakeFSDirectClient::new(&config).unwrap();

        assert_eq!(client.protocol_type(), EndpointType::LakefsDirect);
    }
}