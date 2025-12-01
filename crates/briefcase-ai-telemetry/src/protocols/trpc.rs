//! Legacy tRPC Protocol Client Implementation
//!
//! This module provides the tRPC protocol client that maintains 100% backward
//! compatibility with existing SDK installations.

use super::{ProtocolClient, ProtocolError, ProtocolResult};
use crate::config::{AuthMode, EndpointType, EnhancedTelemetryConfig};
use async_trait::async_trait;
use reqwest::Client as HttpClient;
use serde_json::json;
use std::time::Duration;
use tracing::{debug, info, warn};

/// tRPC Legacy protocol client for backward compatibility
#[derive(Debug)]
pub struct TrpcLegacyClient {
    config: EnhancedTelemetryConfig,
    http_client: HttpClient,
}

impl TrpcLegacyClient {
    /// Creates a new tRPC Legacy client
    pub fn new(config: &EnhancedTelemetryConfig) -> ProtocolResult<Self> {
        // Validate configuration
        if config.endpoint_type != EndpointType::TrpcLegacy {
            return Err(ProtocolError::ConfigurationError(
                "Invalid endpoint type for tRPC Legacy client".to_string(),
            ));
        }

        // Validate authentication mode
        let api_key = match &config.auth {
            AuthMode::ApiKey { key } => key.clone(),
            _ => {
                return Err(ProtocolError::ConfigurationError(
                    "tRPC Legacy client requires API key authentication".to_string(),
                ));
            }
        };

        if api_key.is_empty() {
            return Err(ProtocolError::ConfigurationError(
                "API key cannot be empty for tRPC Legacy client".to_string(),
            ));
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

    /// Gets the API key from configuration
    fn get_api_key(&self) -> ProtocolResult<String> {
        match &self.config.auth {
            AuthMode::ApiKey { key } => Ok(key.clone()),
            _ => Err(ProtocolError::AuthenticationError(
                "Invalid authentication mode for tRPC Legacy client".to_string(),
            )),
        }
    }

    /// Determines the correct authentication header based on API key format
    fn get_auth_header(&self) -> ProtocolResult<String> {
        let api_key = self.get_api_key()?;

        // Determine authentication method based on API key format
        if api_key.starts_with("bca_") {
            // API Key authentication for telemetry ingestion
            Ok(format!("ApiKey {}", api_key))
        } else {
            // Bearer token authentication
            Ok(format!("Bearer {}", api_key))
        }
    }

    /// Wraps data in tRPC format with API key
    fn wrap_in_trpc_format(
        &self,
        mut data: serde_json::Value,
    ) -> ProtocolResult<serde_json::Value> {
        let api_key = self.get_api_key()?;

        // Add apiKey to the payload data
        if let Some(obj) = data.as_object_mut() {
            obj.insert("apiKey".to_string(), serde_json::Value::String(api_key));
        }

        // Add organization context if present
        if let Some(org) = &self.config.organization {
            if let Some(obj) = data.as_object_mut() {
                obj.insert("organization".to_string(), serde_json::to_value(org)?);
            }
        }

        // Add experiment context if present
        if !self.config.experiments.is_empty() {
            if let Some(obj) = data.as_object_mut() {
                obj.insert(
                    "experiments".to_string(),
                    serde_json::to_value(&self.config.experiments)?,
                );
            }
        }

        // Wrap in correct tRPC format (just "json", not "0.json")
        Ok(json!({
            "json": data
        }))
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
                        debug!("tRPC request successful: {}", response.status());

                        // Parse tRPC response to check for errors
                        let response_text =
                            response.text().await.map_err(ProtocolError::NetworkError)?;
                        if let Ok(trpc_response) =
                            serde_json::from_str::<serde_json::Value>(&response_text)
                        {
                            if let Some(error) = trpc_response.get("0").and_then(|v| v.get("error"))
                            {
                                let error_msg = error
                                    .get("message")
                                    .and_then(|m| m.as_str())
                                    .unwrap_or("Unknown tRPC error");
                                return Err(ProtocolError::ProtocolSpecific {
                                    protocol: EndpointType::TrpcLegacy,
                                    message: error_msg.to_string(),
                                });
                            }
                        }
                        return Ok(());
                    } else {
                        let status = response.status();

                        // Handle rate limiting before consuming response
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
                                    protocol: EndpointType::TrpcLegacy,
                                    message: format!(
                                        "Rate limited. Retry after {} seconds",
                                        retry_after_value
                                    ),
                                });
                            }
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
                                protocol: EndpointType::TrpcLegacy,
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
            protocol: EndpointType::TrpcLegacy,
            message: format!("Failed after {} attempts", self.config.retry_attempts),
        })
    }
}

#[async_trait]
impl ProtocolClient for TrpcLegacyClient {
    async fn send_telemetry(&self, data: &[u8]) -> ProtocolResult<()> {
        debug!("Sending telemetry data via tRPC Legacy protocol");

        // Parse the data
        let payload_data = serde_json::from_slice::<serde_json::Value>(data)
            .map_err(ProtocolError::SerializationError)?;

        // Wrap in tRPC format
        let trpc_payload = self.wrap_in_trpc_format(payload_data)?;

        // Make the request
        self.make_request(&self.config.endpoint_url, &trpc_payload)
            .await?;

        info!("Telemetry data sent successfully via tRPC Legacy");
        Ok(())
    }

    async fn send_agent_run(&self, data: &serde_json::Value) -> ProtocolResult<()> {
        debug!("Sending agent run data via tRPC Legacy protocol");

        // Construct agent run recording endpoint
        let agent_run_endpoint = self
            .config
            .endpoint_url
            .replace("/api/trpc/ingest.telemetry", "/api/trpc/agents.recordRun");

        // Wrap in tRPC format
        let trpc_payload = self.wrap_in_trpc_format(data.clone())?;

        // Make the request
        self.make_request(&agent_run_endpoint, &trpc_payload)
            .await?;

        info!("Agent run data sent successfully via tRPC Legacy");
        Ok(())
    }

    async fn send_batch(&self, records: &[serde_json::Value]) -> ProtocolResult<()> {
        debug!("Sending batch data via tRPC Legacy protocol");

        if records.is_empty() {
            return Ok(());
        }

        // Construct batch endpoint URL
        let batch_endpoint = self
            .config
            .endpoint_url
            .replace("/api/trpc/ingest.telemetry", "/api/trpc/ingest.batch");

        // Create batch payload
        let batch_data = json!({
            "records": records
        });

        // Wrap in tRPC format
        let trpc_payload = self.wrap_in_trpc_format(batch_data)?;

        // Make the request
        self.make_request(&batch_endpoint, &trpc_payload).await?;

        info!(
            "Batch data ({} records) sent successfully via tRPC Legacy",
            records.len()
        );
        Ok(())
    }

    fn validate_config(&self, config: &EnhancedTelemetryConfig) -> ProtocolResult<()> {
        // Check endpoint type
        if config.endpoint_type != EndpointType::TrpcLegacy {
            return Err(ProtocolError::ConfigurationError(
                "Invalid endpoint type for tRPC Legacy client".to_string(),
            ));
        }

        // Check authentication mode
        if !matches!(config.auth, AuthMode::ApiKey { .. }) {
            return Err(ProtocolError::ConfigurationError(
                "tRPC Legacy client requires API key authentication".to_string(),
            ));
        }

        // Check endpoint URL
        if config.endpoint_url.is_empty() {
            return Err(ProtocolError::ConfigurationError(
                "Endpoint URL cannot be empty for tRPC Legacy client".to_string(),
            ));
        }

        // Validate endpoint URL format
        if !config.endpoint_url.contains("/api/trpc/") {
            return Err(ProtocolError::ConfigurationError(
                "Invalid tRPC endpoint URL format".to_string(),
            ));
        }

        Ok(())
    }

    fn protocol_type(&self) -> EndpointType {
        EndpointType::TrpcLegacy
    }

    async fn health_check(&self) -> ProtocolResult<()> {
        debug!("Performing health check for tRPC Legacy client");

        // Simple health check - try to send an empty telemetry payload
        let health_data = json!({
            "health_check": true,
            "timestamp": chrono::Utc::now(),
        });

        let trpc_payload = self.wrap_in_trpc_format(health_data)?;

        // Use a shorter timeout for health checks
        let health_client = HttpClient::builder()
            .timeout(Duration::from_secs(5))
            .build()
            .map_err(ProtocolError::NetworkError)?;

        let auth_header = self.get_auth_header()?;

        let response = health_client
            .post(&self.config.endpoint_url)
            .header("Content-Type", "application/json")
            .header("Authorization", auth_header)
            .header(
                "User-Agent",
                format!("briefcase-ai-telemetry-sdk/{}", env!("CARGO_PKG_VERSION")),
            )
            .json(&trpc_payload)
            .send()
            .await
            .map_err(ProtocolError::NetworkError)?;

        if response.status().is_success() {
            debug!("tRPC Legacy health check passed");
            Ok(())
        } else {
            Err(ProtocolError::ProtocolSpecific {
                protocol: EndpointType::TrpcLegacy,
                message: format!("Health check failed: HTTP {}", response.status()),
            })
        }
    }

    async fn shutdown(&mut self) -> ProtocolResult<()> {
        debug!("Shutting down tRPC Legacy client");
        // HTTP client cleanup is handled automatically by Drop trait
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::*;

    fn create_test_config() -> EnhancedTelemetryConfig {
        EnhancedTelemetryConfig::with_api_key("bca_test_key")
            .with_endpoint(
                EndpointType::TrpcLegacy,
                "https://test.example.com/api/trpc/ingest.telemetry",
            )
            .with_timeout(Duration::from_secs(5))
            .with_retry_attempts(2)
    }

    #[test]
    fn test_trpc_client_creation() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config);
        assert!(client.is_ok());
    }

    #[test]
    fn test_trpc_client_invalid_endpoint_type() {
        let config = EnhancedTelemetryConfig::with_jwt_token("token").with_endpoint(
            EndpointType::RestApi,
            "https://test.example.com/api/v1/telemetry",
        );

        let client = TrpcLegacyClient::new(&config);
        assert!(client.is_err());
        assert!(matches!(
            client.unwrap_err(),
            ProtocolError::ConfigurationError(_)
        ));
    }

    #[test]
    fn test_trpc_client_invalid_auth_mode() {
        let config = EnhancedTelemetryConfig::with_jwt_token("token").with_endpoint(
            EndpointType::TrpcLegacy,
            "https://test.example.com/api/trpc/ingest.telemetry",
        );

        let client = TrpcLegacyClient::new(&config);
        assert!(client.is_err());
        assert!(matches!(
            client.unwrap_err(),
            ProtocolError::ConfigurationError(_)
        ));
    }

    #[test]
    fn test_get_auth_header_bca_key() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config).unwrap();

        let auth_header = client.get_auth_header().unwrap();
        assert_eq!(auth_header, "ApiKey bca_test_key");
    }

    #[test]
    fn test_get_auth_header_bearer_token() {
        let config = EnhancedTelemetryConfig {
            auth: AuthMode::ApiKey {
                key: "bearer_token".to_string(),
            },
            endpoint_type: EndpointType::TrpcLegacy,
            endpoint_url: "https://test.example.com/api/trpc/ingest.telemetry".to_string(),
            ..create_test_config()
        };

        let client = TrpcLegacyClient::new(&config).unwrap();
        let auth_header = client.get_auth_header().unwrap();
        assert_eq!(auth_header, "Bearer bearer_token");
    }

    #[test]
    fn test_wrap_in_trpc_format() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config).unwrap();

        let test_data = json!({
            "test": "data",
            "number": 42
        });

        let wrapped = client.wrap_in_trpc_format(test_data).unwrap();

        // Check structure
        assert!(wrapped.get("json").is_some());
        let json_data = wrapped.get("json").unwrap();
        assert_eq!(json_data.get("test").unwrap(), "data");
        assert_eq!(json_data.get("number").unwrap(), 42);
        assert_eq!(json_data.get("apiKey").unwrap(), "bca_test_key");
    }

    #[test]
    fn test_wrap_in_trpc_format_with_organization() {
        let org_context = OrganizationContext::new("org_123", "ml_agents");
        let config = create_test_config().with_organization(org_context);
        let client = TrpcLegacyClient::new(&config).unwrap();

        let test_data = json!({ "test": "data" });
        let wrapped = client.wrap_in_trpc_format(test_data).unwrap();

        let json_data = wrapped.get("json").unwrap();
        assert!(json_data.get("organization").is_some());

        let org = json_data.get("organization").unwrap();
        assert_eq!(org.get("org_id").unwrap(), "org_123");
        assert_eq!(org.get("agent_group").unwrap(), "ml_agents");
    }

    #[test]
    fn test_validate_config_valid() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config).unwrap();

        let result = client.validate_config(&config);
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_config_invalid_endpoint_type() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            endpoint_type: EndpointType::RestApi,
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_config_invalid_auth_mode() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            auth: AuthMode::JwtToken {
                token: "token".to_string(),
            },
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_config_empty_endpoint_url() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            endpoint_url: "".to_string(),
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validate_config_invalid_endpoint_url_format() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config).unwrap();

        let invalid_config = EnhancedTelemetryConfig {
            endpoint_url: "https://example.com/api/v1/telemetry".to_string(),
            ..config
        };

        let result = client.validate_config(&invalid_config);
        assert!(result.is_err());
    }

    #[test]
    fn test_protocol_type() {
        let config = create_test_config();
        let client = TrpcLegacyClient::new(&config).unwrap();

        assert_eq!(client.protocol_type(), EndpointType::TrpcLegacy);
    }
}
