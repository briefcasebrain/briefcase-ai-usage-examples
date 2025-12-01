//! REST API Protocol Client Implementation
//!
//! This module provides the REST API protocol client for modern HTTP integrations
//! with JWT authentication support.

use super::{ProtocolClient, ProtocolError, ProtocolResult};
use crate::config::{AuthMode, EndpointType, EnhancedTelemetryConfig};
use async_trait::async_trait;
use reqwest::Client as HttpClient;
use serde_json::json;
use std::time::Duration;
use tracing::{debug, info, warn};

/// REST API protocol client for modern HTTP integrations
#[derive(Debug)]
pub struct RestApiClient {
    config: EnhancedTelemetryConfig,
    http_client: HttpClient,
}

impl RestApiClient {
    /// Creates a new REST API client
    pub fn new(config: &EnhancedTelemetryConfig) -> ProtocolResult<Self> {
        // Validate configuration
        if config.endpoint_type != EndpointType::RestApi {
            return Err(ProtocolError::ConfigurationError(
                "Invalid endpoint type for REST API client".to_string(),
            ));
        }

        // Validate authentication mode (JWT or API key)
        match &config.auth {
            AuthMode::JwtToken { token } => {
                if token.is_empty() {
                    return Err(ProtocolError::ConfigurationError(
                        "JWT token cannot be empty for REST API client".to_string(),
                    ));
                }
            }
            AuthMode::ApiKey { key } => {
                if key.is_empty() {
                    return Err(ProtocolError::ConfigurationError(
                        "API key cannot be empty for REST API client".to_string(),
                    ));
                }
            }
            AuthMode::StsCredentials { .. } => {
                return Err(ProtocolError::ConfigurationError(
                    "STS credentials not supported for REST API client".to_string(),
                ));
            }
        }

        let http_client = HttpClient::builder()
            .timeout(config.timeout)
            .build()
            .map_err(ProtocolError::NetworkError)?;

        Ok(Self {
            config: config.clone(),
            http_client,
        })
    }

    /// Gets the authorization header for requests
    fn get_auth_header(&self) -> ProtocolResult<String> {
        match &self.config.auth {
            AuthMode::JwtToken { token } => Ok(format!("Bearer {}", token)),
            AuthMode::ApiKey { key } => {
                if key.starts_with("bca_") {
                    Ok(format!("ApiKey {}", key))
                } else {
                    Ok(format!("Bearer {}", key))
                }
            }
            _ => Err(ProtocolError::AuthenticationError(
                "Invalid authentication mode for REST API client".to_string(),
            )),
        }
    }

    /// Formats data in REST API payload structure
    fn format_rest_payload(&self, data: serde_json::Value) -> ProtocolResult<serde_json::Value> {
        let mut payload = data;

        // Add organization context if present
        if let Some(org) = &self.config.organization {
            if let Some(obj) = payload.as_object_mut() {
                obj.insert("organization".to_string(), serde_json::to_value(org)?);
            }
        }

        // Add experiment context if present
        if !self.config.experiments.is_empty() {
            if let Some(obj) = payload.as_object_mut() {
                obj.insert(
                    "experiments".to_string(),
                    serde_json::to_value(&self.config.experiments)?,
                );
            }
        }

        // Add timestamp
        if let Some(obj) = payload.as_object_mut() {
            obj.insert(
                "timestamp".to_string(),
                serde_json::to_value(chrono::Utc::now())?,
            );
        }

        Ok(payload)
    }

    /// Makes an HTTP request with retry logic
    async fn make_request(
        &self,
        endpoint: &str,
        payload: &serde_json::Value,
    ) -> ProtocolResult<()> {
        let auth_header = self.get_auth_header()?;

        for attempt in 1..=self.config.retry_attempts {
            let request_result = self
                .http_client
                .post(endpoint)
                .header("Content-Type", "application/json")
                .header("Authorization", &auth_header)
                .header(
                    "User-Agent",
                    format!("briefcase-ai-telemetry-sdk/{}", env!("CARGO_PKG_VERSION")),
                )
                .json(payload)
                .send()
                .await;

            match request_result {
                Ok(response) => {
                    if response.status().is_success() {
                        debug!("REST API request successful: {}", response.status());
                        return Ok(());
                    } else {
                        let status = response.status();

                        // Handle rate limiting
                        let retry_after = if status == 429 {
                            response
                                .headers()
                                .get("retry-after")
                                .and_then(|h| h.to_str().ok())
                                .and_then(|s| s.parse::<u64>().ok())
                        } else {
                            None
                        };

                        let error_body = response.text().await.unwrap_or_default();

                        if let Some(retry_after_value) = retry_after {
                            if attempt < self.config.retry_attempts {
                                warn!(
                                    "Rate limited, retrying after {} seconds (attempt {}/{})",
                                    retry_after_value, attempt, self.config.retry_attempts
                                );
                                tokio::time::sleep(Duration::from_secs(retry_after_value)).await;
                                continue;
                            } else {
                                return Err(ProtocolError::ProtocolSpecific {
                                    protocol: EndpointType::RestApi,
                                    message: format!(
                                        "Rate limited. Retry after {} seconds",
                                        retry_after_value
                                    ),
                                });
                            }
                        }

                        // Handle authentication errors
                        if status == 401 {
                            return Err(ProtocolError::AuthenticationError(format!(
                                "Authentication failed: {}",
                                error_body
                            )));
                        }

                        if attempt < self.config.retry_attempts {
                            warn!(
                                "HTTP error {}, retrying (attempt {}/{})",
                                status, attempt, self.config.retry_attempts
                            );
                            tokio::time::sleep(Duration::from_millis(100 * attempt as u64)).await;
                            continue;
                        } else {
                            return Err(ProtocolError::ProtocolSpecific {
                                protocol: EndpointType::RestApi,
                                message: format!("HTTP error {}: {}", status, error_body),
                            });
                        }
                    }
                }
                Err(e) => {
                    if attempt < self.config.retry_attempts {
                        warn!(
                            "Network error, retrying (attempt {}/{}): {}",
                            attempt, self.config.retry_attempts, e
                        );
                        tokio::time::sleep(Duration::from_millis(100 * attempt as u64)).await;
                        continue;
                    } else {
                        return Err(ProtocolError::NetworkError(e));
                    }
                }
            }
        }

        Err(ProtocolError::ProtocolSpecific {
            protocol: EndpointType::RestApi,
            message: format!("Failed after {} attempts", self.config.retry_attempts),
        })
    }
}

#[async_trait]
impl ProtocolClient for RestApiClient {
    async fn send_telemetry(&self, data: &[u8]) -> ProtocolResult<()> {
        debug!("Sending telemetry data via REST API protocol");

        // Parse the data
        let payload_data = serde_json::from_slice::<serde_json::Value>(data)
            .map_err(ProtocolError::SerializationError)?;

        // Format as REST payload
        let rest_payload = self.format_rest_payload(payload_data)?;

        // Make the request
        self.make_request(&self.config.endpoint_url, &rest_payload)
            .await?;

        info!("Telemetry data sent successfully via REST API");
        Ok(())
    }

    async fn send_agent_run(&self, data: &serde_json::Value) -> ProtocolResult<()> {
        debug!("Sending agent run data via REST API protocol");

        // Construct agent run endpoint
        let agent_run_endpoint = format!(
            "{}/agent-runs",
            self.config.endpoint_url.trim_end_matches('/')
        );

        // Format as REST payload
        let rest_payload = self.format_rest_payload(data.clone())?;

        // Make the request
        self.make_request(&agent_run_endpoint, &rest_payload)
            .await?;

        info!("Agent run data sent successfully via REST API");
        Ok(())
    }

    async fn send_batch(&self, records: &[serde_json::Value]) -> ProtocolResult<()> {
        debug!("Sending batch data via REST API protocol");

        if records.is_empty() {
            return Ok(());
        }

        // Construct batch endpoint
        let batch_endpoint = format!("{}/batch", self.config.endpoint_url.trim_end_matches('/'));

        // Create batch payload
        let batch_data = json!({
            "records": records,
            "batch_size": records.len(),
            "batch_timestamp": chrono::Utc::now()
        });

        // Format as REST payload
        let rest_payload = self.format_rest_payload(batch_data)?;

        // Make the request
        self.make_request(&batch_endpoint, &rest_payload).await?;

        info!(
            "Batch data ({} records) sent successfully via REST API",
            records.len()
        );
        Ok(())
    }

    fn validate_config(&self, config: &EnhancedTelemetryConfig) -> ProtocolResult<()> {
        // Check endpoint type
        if config.endpoint_type != EndpointType::RestApi {
            return Err(ProtocolError::ConfigurationError(
                "Invalid endpoint type for REST API client".to_string(),
            ));
        }

        // Check authentication mode
        match &config.auth {
            AuthMode::JwtToken { token } => {
                if token.is_empty() {
                    return Err(ProtocolError::ConfigurationError(
                        "JWT token cannot be empty".to_string(),
                    ));
                }
            }
            AuthMode::ApiKey { key } => {
                if key.is_empty() {
                    return Err(ProtocolError::ConfigurationError(
                        "API key cannot be empty".to_string(),
                    ));
                }
            }
            AuthMode::StsCredentials { .. } => {
                return Err(ProtocolError::ConfigurationError(
                    "STS credentials not supported for REST API client".to_string(),
                ));
            }
        }

        // Check endpoint URL
        if config.endpoint_url.is_empty() {
            return Err(ProtocolError::ConfigurationError(
                "Endpoint URL cannot be empty for REST API client".to_string(),
            ));
        }

        // Validate URL format
        if !config.endpoint_url.starts_with("http://")
            && !config.endpoint_url.starts_with("https://")
        {
            return Err(ProtocolError::ConfigurationError(
                "Endpoint URL must be a valid HTTP/HTTPS URL".to_string(),
            ));
        }

        Ok(())
    }

    fn protocol_type(&self) -> EndpointType {
        EndpointType::RestApi
    }

    async fn health_check(&self) -> ProtocolResult<()> {
        debug!("Performing health check for REST API client");

        // Create health endpoint
        let health_endpoint = format!("{}/health", self.config.endpoint_url.trim_end_matches('/'));

        // Use a shorter timeout for health checks
        let health_client = HttpClient::builder()
            .timeout(Duration::from_secs(5))
            .build()
            .map_err(ProtocolError::NetworkError)?;

        let auth_header = self.get_auth_header()?;

        let response = health_client
            .get(&health_endpoint)
            .header("Authorization", auth_header.clone())
            .header(
                "User-Agent",
                format!("briefcase-ai-telemetry-sdk/{}", env!("CARGO_PKG_VERSION")),
            )
            .send()
            .await
            .map_err(ProtocolError::NetworkError)?;

        if response.status().is_success() {
            debug!("REST API health check passed");
            Ok(())
        } else if response.status() == 404 {
            // Health endpoint might not exist, try a HEAD request to main endpoint
            let response = health_client
                .head(&self.config.endpoint_url)
                .header("Authorization", auth_header.clone())
                .send()
                .await
                .map_err(ProtocolError::NetworkError)?;

            if response.status().is_success() {
                debug!("REST API health check passed (fallback)");
                Ok(())
            } else {
                Err(ProtocolError::ProtocolSpecific {
                    protocol: EndpointType::RestApi,
                    message: format!("Health check failed: HTTP {}", response.status()),
                })
            }
        } else {
            Err(ProtocolError::ProtocolSpecific {
                protocol: EndpointType::RestApi,
                message: format!("Health check failed: HTTP {}", response.status()),
            })
        }
    }

    async fn shutdown(&mut self) -> ProtocolResult<()> {
        debug!("Shutting down REST API client");
        // HTTP client cleanup is handled automatically by Drop trait
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::*;

    fn create_test_config_jwt() -> EnhancedTelemetryConfig {
        EnhancedTelemetryConfig::with_jwt_token("jwt_token_123")
            .with_endpoint(
                EndpointType::RestApi,
                "https://api.example.com/v1/telemetry",
            )
            .with_timeout(Duration::from_secs(5))
            .with_retry_attempts(2)
    }

    fn create_test_config_api_key() -> EnhancedTelemetryConfig {
        EnhancedTelemetryConfig::with_api_key("bca_test_key")
            .with_endpoint(
                EndpointType::RestApi,
                "https://api.example.com/v1/telemetry",
            )
            .with_timeout(Duration::from_secs(5))
            .with_retry_attempts(2)
    }

    #[test]
    fn test_rest_client_creation_jwt() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config);
        assert!(client.is_ok());
    }

    #[test]
    fn test_rest_client_creation_api_key() {
        let config = create_test_config_api_key();
        let client = RestApiClient::new(&config);
        assert!(client.is_ok());
    }

    #[test]
    fn test_rest_client_invalid_endpoint_type() {
        let config = EnhancedTelemetryConfig::with_jwt_token("token").with_endpoint(
            EndpointType::TrpcLegacy,
            "https://api.example.com/api/trpc/telemetry",
        );

        let client = RestApiClient::new(&config);
        assert!(client.is_err());
        assert!(matches!(
            client.unwrap_err(),
            ProtocolError::ConfigurationError(_)
        ));
    }

    #[test]
    fn test_rest_client_invalid_auth_sts() {
        let config =
            EnhancedTelemetryConfig::with_sts_credentials("access", "secret", "region", "stream")
                .with_endpoint(
                    EndpointType::RestApi,
                    "https://api.example.com/v1/telemetry",
                );

        let client = RestApiClient::new(&config);
        assert!(client.is_err());
        assert!(matches!(
            client.unwrap_err(),
            ProtocolError::ConfigurationError(_)
        ));
    }

    #[test]
    fn test_get_auth_header_jwt() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config).unwrap();

        let auth_header = client.get_auth_header().unwrap();
        assert_eq!(auth_header, "Bearer jwt_token_123");
    }

    #[test]
    fn test_get_auth_header_api_key_bca() {
        let config = create_test_config_api_key();
        let client = RestApiClient::new(&config).unwrap();

        let auth_header = client.get_auth_header().unwrap();
        assert_eq!(auth_header, "ApiKey bca_test_key");
    }

    #[test]
    fn test_get_auth_header_api_key_bearer() {
        let config = EnhancedTelemetryConfig {
            auth: AuthMode::ApiKey {
                key: "bearer_token".to_string(),
            },
            endpoint_type: EndpointType::RestApi,
            endpoint_url: "https://api.example.com/v1/telemetry".to_string(),
            ..create_test_config_jwt()
        };

        let client = RestApiClient::new(&config).unwrap();
        let auth_header = client.get_auth_header().unwrap();
        assert_eq!(auth_header, "Bearer bearer_token");
    }

    #[test]
    fn test_format_rest_payload() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config).unwrap();

        let test_data = json!({
            "test": "data",
            "number": 42
        });

        let formatted = client.format_rest_payload(test_data).unwrap();

        // Check that original data is preserved
        assert_eq!(formatted.get("test").unwrap(), "data");
        assert_eq!(formatted.get("number").unwrap(), 42);

        // Check that timestamp was added
        assert!(formatted.get("timestamp").is_some());
    }

    #[test]
    fn test_format_rest_payload_with_organization() {
        let org_context = OrganizationContext::new("org_123", "ml_agents");
        let config = create_test_config_jwt().with_organization(org_context);
        let client = RestApiClient::new(&config).unwrap();

        let test_data = json!({ "test": "data" });
        let formatted = client.format_rest_payload(test_data).unwrap();

        // Check organization context was added
        assert!(formatted.get("organization").is_some());
        let org = formatted.get("organization").unwrap();
        assert_eq!(org.get("org_id").unwrap(), "org_123");
        assert_eq!(org.get("agent_group").unwrap(), "ml_agents");
    }

    #[test]
    fn test_format_rest_payload_with_experiments() {
        let experiment = ExperimentContext::new("exp_123", "variant_a");
        let config = create_test_config_jwt().with_experiment(experiment);
        let client = RestApiClient::new(&config).unwrap();

        let test_data = json!({ "test": "data" });
        let formatted = client.format_rest_payload(test_data).unwrap();

        // Check experiments were added
        assert!(formatted.get("experiments").is_some());
        let experiments = formatted.get("experiments").unwrap().as_array().unwrap();
        assert_eq!(experiments.len(), 1);
        assert_eq!(experiments[0].get("experiment_id").unwrap(), "exp_123");
    }

    #[test]
    fn test_validate_config_valid_jwt() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config).unwrap();

        let result = client.validate_config(&config);
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_config_valid_api_key() {
        let config = create_test_config_api_key();
        let client = RestApiClient::new(&config).unwrap();

        let result = client.validate_config(&config);
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_config_invalid_endpoint_type() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            endpoint_type: EndpointType::KinesisStream,
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_config_empty_jwt_token() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            auth: AuthMode::JwtToken {
                token: "".to_string(),
            },
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_config_empty_endpoint_url() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            endpoint_url: "".to_string(),
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_config_invalid_url_format() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            endpoint_url: "not-a-url".to_string(),
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_protocol_type() {
        let config = create_test_config_jwt();
        let client = RestApiClient::new(&config).unwrap();

        assert_eq!(client.protocol_type(), EndpointType::RestApi);
    }
}
