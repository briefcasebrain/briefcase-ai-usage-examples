//! Multi-Protocol Architecture Implementation
//!
//! This module provides trait definitions and implementations for the
//! multi-protocol telemetry architecture supporting tRPC, REST, Kinesis, and LakeFS.

use crate::config::{EndpointType, EnhancedTelemetryConfig};
use crate::TelemetryData;
use async_trait::async_trait;
use std::collections::HashMap;
use std::sync::Arc;
use thiserror::Error;

pub mod kinesis;
pub mod lakefs;
pub mod rest;
pub mod trpc;

/// Error types for protocol operations
#[derive(Debug, Error)]
pub enum ProtocolError {
    #[error("Authentication failed: {0}")]
    AuthenticationError(String),

    #[error("Network error: {0}")]
    NetworkError(#[from] reqwest::Error),

    #[error("Protocol-specific error: {protocol:?} - {message}")]
    ProtocolSpecific {
        protocol: EndpointType,
        message: String,
    },

    #[error("Configuration error: {0}")]
    ConfigurationError(String),

    #[error("Data transformation error: {0}")]
    TransformationError(String),

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("AWS SDK error: {0}")]
    AwsError(String),

    #[error("Circuit breaker is open")]
    CircuitBreakerOpen,
}

/// Result type for protocol operations
pub type ProtocolResult<T> = Result<T, ProtocolError>;

/// Trait for protocol-specific client implementations
#[async_trait]
pub trait ProtocolClient: Send + Sync {
    /// Sends telemetry data using the protocol-specific implementation
    async fn send_telemetry(&self, data: &[u8]) -> ProtocolResult<()>;

    /// Sends agent run data
    async fn send_agent_run(&self, data: &serde_json::Value) -> ProtocolResult<()>;

    /// Sends batch data
    async fn send_batch(&self, records: &[serde_json::Value]) -> ProtocolResult<()>;

    /// Validates the configuration for this protocol
    fn validate_config(&self, config: &EnhancedTelemetryConfig) -> ProtocolResult<()>;

    /// Returns the protocol type this client handles
    fn protocol_type(&self) -> EndpointType;

    /// Health check for the protocol endpoint
    async fn health_check(&self) -> ProtocolResult<()>;

    /// Graceful shutdown for cleanup
    async fn shutdown(&mut self) -> ProtocolResult<()> {
        Ok(()) // Default implementation - no-op
    }
}

// Note: ExperimentManager trait is defined in experiment module to avoid conflicts

/// Trait for data format transformation between protocols
pub trait DataTransformer: Send + Sync {
    /// Transforms telemetry data to protocol-specific format
    fn transform_telemetry_data(
        &self,
        data: &TelemetryData,
        target_protocol: EndpointType,
    ) -> ProtocolResult<Vec<u8>>;

    /// Transforms agent run data to protocol-specific format
    fn transform_agent_run_data(
        &self,
        data: &serde_json::Value,
        target_protocol: EndpointType,
    ) -> ProtocolResult<Vec<u8>>;

    /// Transforms batch data to protocol-specific format
    fn transform_batch_data(
        &self,
        records: &[serde_json::Value],
        target_protocol: EndpointType,
    ) -> ProtocolResult<Vec<u8>>;
}

/// Circuit breaker state for resilience
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CircuitState {
    Closed,
    Open,
    HalfOpen,
}

/// Circuit breaker implementation for protocol resilience
#[derive(Debug)]
pub struct CircuitBreaker {
    failure_count: std::sync::atomic::AtomicUsize,
    last_failure: std::sync::atomic::AtomicU64,
    state: std::sync::atomic::AtomicU8, // 0=Closed, 1=Open, 2=HalfOpen
    failure_threshold: usize,
    timeout_duration: std::time::Duration,
}

impl CircuitBreaker {
    pub fn new(failure_threshold: usize, timeout_duration: std::time::Duration) -> Self {
        Self {
            failure_count: std::sync::atomic::AtomicUsize::new(0),
            last_failure: std::sync::atomic::AtomicU64::new(0),
            state: std::sync::atomic::AtomicU8::new(0), // Closed
            failure_threshold,
            timeout_duration,
        }
    }

    pub fn state(&self) -> CircuitState {
        match self.state.load(std::sync::atomic::Ordering::Relaxed) {
            0 => CircuitState::Closed,
            1 => CircuitState::Open,
            2 => CircuitState::HalfOpen,
            _ => CircuitState::Closed,
        }
    }

    pub async fn call<F, T>(&self, f: F) -> ProtocolResult<T>
    where
        F: std::future::Future<Output = ProtocolResult<T>>,
    {
        match self.state() {
            CircuitState::Open => {
                if self.should_attempt_reset() {
                    self.set_state(CircuitState::HalfOpen);
                } else {
                    return Err(ProtocolError::CircuitBreakerOpen);
                }
            }
            _ => {}
        }

        match f.await {
            Ok(result) => {
                self.on_success();
                Ok(result)
            }
            Err(e) => {
                self.on_failure();
                Err(e)
            }
        }
    }

    fn should_attempt_reset(&self) -> bool {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        let last_failure = self.last_failure.load(std::sync::atomic::Ordering::Relaxed);

        (now - last_failure) >= self.timeout_duration.as_secs()
    }

    fn set_state(&self, state: CircuitState) {
        let state_value = match state {
            CircuitState::Closed => 0,
            CircuitState::Open => 1,
            CircuitState::HalfOpen => 2,
        };
        self.state
            .store(state_value, std::sync::atomic::Ordering::Relaxed);
    }

    fn on_success(&self) {
        self.failure_count
            .store(0, std::sync::atomic::Ordering::Relaxed);
        self.set_state(CircuitState::Closed);
    }

    fn on_failure(&self) {
        let count = self
            .failure_count
            .fetch_add(1, std::sync::atomic::Ordering::Relaxed)
            + 1;

        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        self.last_failure
            .store(now, std::sync::atomic::Ordering::Relaxed);

        if count >= self.failure_threshold {
            self.set_state(CircuitState::Open);
        }
    }
}

/// Factory for creating protocol clients
pub struct ProtocolClientFactory;

impl ProtocolClientFactory {
    /// Creates a protocol client based on the configuration
    pub fn create_client(
        config: &EnhancedTelemetryConfig,
    ) -> ProtocolResult<Box<dyn ProtocolClient>> {
        match config.endpoint_type {
            EndpointType::TrpcLegacy => {
                let client = trpc::TrpcLegacyClient::new(config)?;
                Ok(Box::new(client))
            }
            EndpointType::RestApi => {
                let client = rest::RestApiClient::new(config)?;
                Ok(Box::new(client))
            }
            EndpointType::KinesisStream => {
                let client = kinesis::KinesisStreamClient::new(config)?;
                Ok(Box::new(client))
            }
            EndpointType::LakefsDirect => {
                let client = lakefs::LakeFSDirectClient::new(config)?;
                Ok(Box::new(client))
            }
        }
    }

    /// Creates fallback clients for redundancy
    pub fn create_fallback_clients(
        config: &EnhancedTelemetryConfig,
    ) -> ProtocolResult<Vec<Box<dyn ProtocolClient>>> {
        let mut clients = Vec::new();

        for (endpoint_type, _url) in &config.fallback_endpoints {
            let fallback_config = EnhancedTelemetryConfig {
                endpoint_type: endpoint_type.clone(),
                ..config.clone()
            };

            let client = Self::create_client(&fallback_config)?;
            clients.push(client);
        }

        Ok(clients)
    }
}

/// Multi-protocol client manager that routes requests to appropriate protocols
pub struct MultiProtocolClient {
    primary_client: Box<dyn ProtocolClient>,
    fallback_clients: Vec<Box<dyn ProtocolClient>>,
    transformer: Arc<dyn DataTransformer>,
    circuit_breaker: Arc<CircuitBreaker>,
}

impl MultiProtocolClient {
    /// Creates a new multi-protocol client
    pub fn new(
        config: &EnhancedTelemetryConfig,
        transformer: Arc<dyn DataTransformer>,
    ) -> ProtocolResult<Self> {
        let primary_client = ProtocolClientFactory::create_client(config)?;
        let fallback_clients = ProtocolClientFactory::create_fallback_clients(config)?;

        let circuit_breaker = Arc::new(CircuitBreaker::new(
            5,                                  // 5 failures before opening
            std::time::Duration::from_secs(60), // 1 minute timeout
        ));

        Ok(Self {
            primary_client,
            fallback_clients,
            transformer,
            circuit_breaker,
        })
    }

    /// Sends telemetry data with fallback support
    pub async fn send_telemetry(&self, data: &TelemetryData) -> ProtocolResult<()> {
        // Transform data for primary protocol
        let transformed = self
            .transformer
            .transform_telemetry_data(data, self.primary_client.protocol_type())?;

        // Try primary client with circuit breaker
        let result = self
            .circuit_breaker
            .call(async { self.primary_client.send_telemetry(&transformed).await })
            .await;

        match result {
            Ok(_) => return Ok(()),
            Err(e) => {
                tracing::warn!("Primary client failed: {}", e);

                // Try fallback clients
                for fallback_client in &self.fallback_clients {
                    let fallback_data = self
                        .transformer
                        .transform_telemetry_data(data, fallback_client.protocol_type())?;
                    if fallback_client.send_telemetry(&fallback_data).await.is_ok() {
                        tracing::info!(
                            "Fallback client {} succeeded",
                            fallback_client.protocol_type().to_string()
                        );
                        return Ok(());
                    }
                }

                return Err(e);
            }
        }
    }

    /// Sends agent run data with fallback support
    pub async fn send_agent_run(&self, data: &serde_json::Value) -> ProtocolResult<()> {
        // Transform data for primary protocol
        let _transformed = self
            .transformer
            .transform_agent_run_data(data, self.primary_client.protocol_type())?;

        // Try primary client with circuit breaker
        let result = self
            .circuit_breaker
            .call(async { self.primary_client.send_agent_run(data).await })
            .await;

        match result {
            Ok(_) => return Ok(()),
            Err(e) => {
                tracing::warn!("Primary client failed for agent run: {}", e);

                // Try fallback clients
                for fallback_client in &self.fallback_clients {
                    if fallback_client.send_agent_run(data).await.is_ok() {
                        tracing::info!(
                            "Fallback client {} succeeded for agent run",
                            fallback_client.protocol_type().to_string()
                        );
                        return Ok(());
                    }
                }

                return Err(e);
            }
        }
    }

    /// Sends batch data with fallback support
    pub async fn send_batch(&self, records: &[serde_json::Value]) -> ProtocolResult<()> {
        // Transform data for primary protocol
        let _transformed = self
            .transformer
            .transform_batch_data(records, self.primary_client.protocol_type())?;

        // Try primary client with circuit breaker
        let result = self
            .circuit_breaker
            .call(async { self.primary_client.send_batch(records).await })
            .await;

        match result {
            Ok(_) => return Ok(()),
            Err(e) => {
                tracing::warn!("Primary client failed for batch: {}", e);

                // Try fallback clients
                for fallback_client in &self.fallback_clients {
                    if fallback_client.send_batch(records).await.is_ok() {
                        tracing::info!(
                            "Fallback client {} succeeded for batch",
                            fallback_client.protocol_type().to_string()
                        );
                        return Ok(());
                    }
                }

                return Err(e);
            }
        }
    }

    /// Performs health check on all clients
    pub async fn health_check(&self) -> HashMap<EndpointType, ProtocolResult<()>> {
        let mut results = HashMap::new();

        // Check primary client
        let primary_result = self.primary_client.health_check().await;
        results.insert(self.primary_client.protocol_type(), primary_result);

        // Check fallback clients
        for fallback_client in &self.fallback_clients {
            let fallback_result = fallback_client.health_check().await;
            results.insert(fallback_client.protocol_type(), fallback_result);
        }

        results
    }

    /// Graceful shutdown
    pub async fn shutdown(&mut self) -> ProtocolResult<()> {
        // Shutdown primary client
        self.primary_client.shutdown().await?;

        // Shutdown fallback clients
        for fallback_client in &mut self.fallback_clients {
            if let Err(e) = fallback_client.shutdown().await {
                tracing::warn!("Error shutting down fallback client: {}", e);
            }
        }

        Ok(())
    }
}

impl ToString for EndpointType {
    fn to_string(&self) -> String {
        match self {
            EndpointType::TrpcLegacy => "TrpcLegacy".to_string(),
            EndpointType::RestApi => "RestApi".to_string(),
            EndpointType::KinesisStream => "KinesisStream".to_string(),
            EndpointType::LakefsDirect => "LakefsDirect".to_string(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::*;
    use std::time::Duration;

    #[test]
    fn test_circuit_breaker_states() {
        let cb = CircuitBreaker::new(3, Duration::from_secs(60));

        // Initial state should be closed
        assert_eq!(cb.state(), CircuitState::Closed);

        // Simulate failures
        for _ in 0..3 {
            cb.on_failure();
        }

        // Should be open after threshold failures
        assert_eq!(cb.state(), CircuitState::Open);

        // Success should reset to closed
        cb.on_success();
        assert_eq!(cb.state(), CircuitState::Closed);
    }

    #[test]
    fn test_protocol_error_display() {
        let auth_error = ProtocolError::AuthenticationError("Invalid token".to_string());
        assert!(auth_error.to_string().contains("Authentication failed"));

        let config_error = ProtocolError::ConfigurationError("Missing endpoint".to_string());
        assert!(config_error.to_string().contains("Configuration error"));

        let protocol_error = ProtocolError::ProtocolSpecific {
            protocol: EndpointType::RestApi,
            message: "HTTP 500".to_string(),
        };
        assert!(protocol_error
            .to_string()
            .contains("Protocol-specific error"));
    }

    #[test]
    fn test_endpoint_type_to_string() {
        assert_eq!(EndpointType::TrpcLegacy.to_string(), "TrpcLegacy");
        assert_eq!(EndpointType::RestApi.to_string(), "RestApi");
        assert_eq!(EndpointType::KinesisStream.to_string(), "KinesisStream");
        assert_eq!(EndpointType::LakefsDirect.to_string(), "LakefsDirect");
    }
}
