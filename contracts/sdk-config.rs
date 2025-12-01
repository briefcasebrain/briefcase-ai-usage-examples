//! SDK Configuration Contracts for Multi-Protocol Architecture
//!
//! This module defines the trait contracts and configuration structures for the
//! modernized briefcase-ai-telemetry-sdk that supports multiple protocols,
//! organization context, and experiment integration while maintaining 100%
//! backward compatibility.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;
use uuid::Uuid;

/// Enumeration of supported endpoint types for multi-protocol architecture
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum EndpointType {
    /// Legacy tRPC protocol (maintains backward compatibility)
    TrpcLegacy,
    /// REST API protocol for standardized HTTP endpoints
    RestApi,
    /// AWS Kinesis Stream for high-throughput real-time data ingestion
    KinesisStream,
    /// Direct LakeFS integration for data versioning and lineage
    LakefsDirect,
}

impl Default for EndpointType {
    fn default() -> Self {
        // Default to legacy tRPC for backward compatibility
        EndpointType::TrpcLegacy
    }
}

/// Authentication modes for different protocol types and use cases
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum AuthMode {
    /// Traditional API key authentication (bca_ prefixed keys)
    ApiKey { key: String },
    /// JWT token authentication for dashboard users
    JwtToken { token: String },
    /// AWS STS credentials for Kinesis and LakeFS integration
    StsCredentials {
        access_key_id: String,
        secret_access_key: String,
        session_token: Option<String>,
        region: String,
    },
}

impl AuthMode {
    /// Creates an API key authentication mode
    pub fn api_key(key: impl Into<String>) -> Self {
        Self::ApiKey { key: key.into() }
    }

    /// Creates a JWT token authentication mode
    pub fn jwt_token(token: impl Into<String>) -> Self {
        Self::JwtToken { token: token.into() }
    }

    /// Creates STS credentials authentication mode
    pub fn sts_credentials(
        access_key_id: impl Into<String>,
        secret_access_key: impl Into<String>,
        region: impl Into<String>,
    ) -> Self {
        Self::StsCredentials {
            access_key_id: access_key_id.into(),
            secret_access_key: secret_access_key.into(),
            session_token: None,
            region: region.into(),
        }
    }

    /// Creates STS credentials with session token
    pub fn sts_credentials_with_session(
        access_key_id: impl Into<String>,
        secret_access_key: impl Into<String>,
        session_token: impl Into<String>,
        region: impl Into<String>,
    ) -> Self {
        Self::StsCredentials {
            access_key_id: access_key_id.into(),
            secret_access_key: secret_access_key.into(),
            session_token: Some(session_token.into()),
            region: region.into(),
        }
    }
}

/// Organization context for multi-tenant support
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct OrganizationContext {
    /// Organization identifier
    pub org_id: String,
    /// Optional organization name for display purposes
    pub org_name: Option<String>,
    /// Agent group within the organization
    pub agent_group: String,
    /// Optional environment (dev, staging, prod)
    pub environment: Option<String>,
    /// Additional organization metadata
    pub metadata: HashMap<String, String>,
}

impl OrganizationContext {
    /// Creates a new organization context
    pub fn new(org_id: impl Into<String>, agent_group: impl Into<String>) -> Self {
        Self {
            org_id: org_id.into(),
            org_name: None,
            agent_group: agent_group.into(),
            environment: None,
            metadata: HashMap::new(),
        }
    }

    /// Sets the organization name
    pub fn with_org_name(mut self, name: impl Into<String>) -> Self {
        self.org_name = Some(name.into());
        self
    }

    /// Sets the environment
    pub fn with_environment(mut self, env: impl Into<String>) -> Self {
        self.environment = Some(env.into());
        self
    }

    /// Adds metadata
    pub fn with_metadata(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }
}

/// Experiment context for A/B testing integration
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ExperimentContext {
    /// Unique experiment identifier
    pub experiment_id: String,
    /// Experiment name for display purposes
    pub experiment_name: Option<String>,
    /// Variant assigned to this instance (control, variant_a, variant_b, etc.)
    pub variant: String,
    /// Experiment enrollment timestamp
    pub enrolled_at: chrono::DateTime<chrono::Utc>,
    /// Experiment configuration parameters
    pub config: HashMap<String, serde_json::Value>,
    /// Whether this experiment is active
    pub active: bool,
}

impl ExperimentContext {
    /// Creates a new experiment context
    pub fn new(experiment_id: impl Into<String>, variant: impl Into<String>) -> Self {
        Self {
            experiment_id: experiment_id.into(),
            experiment_name: None,
            variant: variant.into(),
            enrolled_at: chrono::Utc::now(),
            config: HashMap::new(),
            active: true,
        }
    }

    /// Sets the experiment name
    pub fn with_name(mut self, name: impl Into<String>) -> Self {
        self.experiment_name = Some(name.into());
        self
    }

    /// Adds configuration parameter
    pub fn with_config(mut self, key: impl Into<String>, value: serde_json::Value) -> Self {
        self.config.insert(key.into(), value);
        self
    }

    /// Sets the active status
    pub fn with_active(mut self, active: bool) -> Self {
        self.active = active;
        self
    }
}

/// Enhanced telemetry configuration with multi-protocol support
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnhancedTelemetryConfig {
    /// Authentication configuration
    pub auth: AuthMode,
    /// Primary endpoint type and configuration
    pub endpoint_type: EndpointType,
    /// Primary endpoint URL
    pub endpoint_url: String,
    /// Fallback endpoints for redundancy
    pub fallback_endpoints: Vec<(EndpointType, String)>,
    /// Organization context for multi-tenant support
    pub organization: Option<OrganizationContext>,
    /// Active experiments for this client
    pub experiments: Vec<ExperimentContext>,
    /// Request timeout
    pub timeout: Duration,
    /// Retry attempts for failed requests
    pub retry_attempts: u32,
    /// Batch size for event batching
    pub batch_size: usize,
    /// Flush interval for automatic event flushing
    pub flush_interval: Duration,
    /// Whether telemetry collection is enabled
    pub enabled: bool,
    /// Protocol-specific configurations
    pub protocol_configs: HashMap<EndpointType, serde_json::Value>,
    /// Backward compatibility: legacy API key (deprecated)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub legacy_api_key: Option<String>,
}

impl EnhancedTelemetryConfig {
    /// Creates a new enhanced configuration with API key authentication (backward compatible)
    pub fn with_api_key(api_key: impl Into<String>) -> Self {
        let key = api_key.into();
        Self {
            auth: AuthMode::api_key(key.clone()),
            endpoint_type: EndpointType::TrpcLegacy,
            endpoint_url: "https://your-telemetry-endpoint.com/api/trpc/ingest.telemetry".to_string(),
            fallback_endpoints: vec![],
            organization: None,
            experiments: vec![],
            timeout: Duration::from_secs(10),
            retry_attempts: 3,
            batch_size: 100,
            flush_interval: Duration::from_secs(5),
            enabled: true,
            protocol_configs: HashMap::new(),
            legacy_api_key: Some(key),
        }
    }

    /// Creates a new enhanced configuration with JWT authentication
    pub fn with_jwt_token(token: impl Into<String>) -> Self {
        Self {
            auth: AuthMode::jwt_token(token),
            endpoint_type: EndpointType::RestApi,
            endpoint_url: "https://your-telemetry-endpoint.com/api/v1/telemetry".to_string(),
            fallback_endpoints: vec![],
            organization: None,
            experiments: vec![],
            timeout: Duration::from_secs(10),
            retry_attempts: 3,
            batch_size: 100,
            flush_interval: Duration::from_secs(5),
            enabled: true,
            protocol_configs: HashMap::new(),
            legacy_api_key: None,
        }
    }

    /// Creates a new enhanced configuration with AWS STS credentials
    pub fn with_sts_credentials(
        access_key_id: impl Into<String>,
        secret_access_key: impl Into<String>,
        region: impl Into<String>,
        stream_name: impl Into<String>,
    ) -> Self {
        let mut protocol_configs = HashMap::new();
        protocol_configs.insert(
            EndpointType::KinesisStream,
            serde_json::json!({
                "stream_name": stream_name.into(),
                "partition_key_field": "session_id"
            })
        );

        Self {
            auth: AuthMode::sts_credentials(access_key_id, secret_access_key, region),
            endpoint_type: EndpointType::KinesisStream,
            endpoint_url: "".to_string(), // Kinesis doesn't use URLs
            fallback_endpoints: vec![],
            organization: None,
            experiments: vec![],
            timeout: Duration::from_secs(10),
            retry_attempts: 3,
            batch_size: 100,
            flush_interval: Duration::from_secs(5),
            enabled: true,
            protocol_configs,
            legacy_api_key: None,
        }
    }

    /// Sets the organization context
    pub fn with_organization(mut self, org_context: OrganizationContext) -> Self {
        self.organization = Some(org_context);
        self
    }

    /// Adds an experiment context
    pub fn with_experiment(mut self, experiment: ExperimentContext) -> Self {
        self.experiments.push(experiment);
        self
    }

    /// Sets the endpoint type and URL
    pub fn with_endpoint(mut self, endpoint_type: EndpointType, url: impl Into<String>) -> Self {
        self.endpoint_type = endpoint_type;
        self.endpoint_url = url.into();
        self
    }

    /// Adds a fallback endpoint
    pub fn with_fallback_endpoint(mut self, endpoint_type: EndpointType, url: impl Into<String>) -> Self {
        self.fallback_endpoints.push((endpoint_type, url.into()));
        self
    }

    /// Sets protocol-specific configuration
    pub fn with_protocol_config(mut self, endpoint_type: EndpointType, config: serde_json::Value) -> Self {
        self.protocol_configs.insert(endpoint_type, config);
        self
    }

    /// Sets the batch size
    pub fn with_batch_size(mut self, batch_size: usize) -> Self {
        self.batch_size = batch_size;
        self
    }

    /// Sets the flush interval
    pub fn with_flush_interval(mut self, flush_interval: Duration) -> Self {
        self.flush_interval = flush_interval;
        self
    }

    /// Sets the timeout
    pub fn with_timeout(mut self, timeout: Duration) -> Self {
        self.timeout = timeout;
        self
    }

    /// Sets the retry attempts
    pub fn with_retry_attempts(mut self, retry_attempts: u32) -> Self {
        self.retry_attempts = retry_attempts;
        self
    }

    /// Sets the enabled status
    pub fn with_enabled(mut self, enabled: bool) -> Self {
        self.enabled = enabled;
        self
    }

    /// Migrates from legacy TelemetryConfig for backward compatibility
    pub fn from_legacy(legacy_config: &super::TelemetryConfig) -> Self {
        Self::with_api_key(legacy_config.api_key.clone())
            .with_endpoint(EndpointType::TrpcLegacy, legacy_config.endpoint.clone())
            .with_timeout(legacy_config.timeout)
            .with_retry_attempts(legacy_config.retry_attempts)
            .with_batch_size(legacy_config.batch_size)
            .with_flush_interval(legacy_config.flush_interval)
            .with_enabled(legacy_config.enabled)
    }
}

/// Trait for protocol-specific client implementations
pub trait ProtocolClient: Send + Sync {
    /// Sends telemetry data using the protocol-specific implementation
    fn send_telemetry(&self, data: &[u8]) -> impl std::future::Future<Output = Result<(), Box<dyn std::error::Error + Send + Sync>>>;

    /// Sends agent run data
    fn send_agent_run(&self, data: &serde_json::Value) -> impl std::future::Future<Output = Result<(), Box<dyn std::error::Error + Send + Sync>>>;

    /// Sends batch data
    fn send_batch(&self, records: &[serde_json::Value]) -> impl std::future::Future<Output = Result<(), Box<dyn std::error::Error + Send + Sync>>>;

    /// Validates the configuration for this protocol
    fn validate_config(&self, config: &EnhancedTelemetryConfig) -> Result<(), Box<dyn std::error::Error + Send + Sync>>;

    /// Returns the protocol type this client handles
    fn protocol_type(&self) -> EndpointType;
}

/// Trait for experiment enrollment and management
pub trait ExperimentManager: Send + Sync {
    /// Enrolls the client in available experiments
    fn enroll_experiments(&mut self, org_context: &OrganizationContext) -> impl std::future::Future<Output = Result<Vec<ExperimentContext>, Box<dyn std::error::Error + Send + Sync>>>;

    /// Updates experiment status (for example, when an experiment ends)
    fn update_experiments(&mut self) -> impl std::future::Future<Output = Result<(), Box<dyn std::error::Error + Send + Sync>>>;

    /// Tags an event with experiment variants
    fn tag_event_with_experiments(&self, event: &mut super::Event, experiments: &[ExperimentContext]);
}

/// Trait for data format transformation between protocols
pub trait DataTransformer: Send + Sync {
    /// Transforms telemetry data to protocol-specific format
    fn transform_telemetry_data(&self, data: &super::TelemetryData, target_protocol: EndpointType) -> Result<Vec<u8>, Box<dyn std::error::Error + Send + Sync>>;

    /// Transforms agent run data to protocol-specific format
    fn transform_agent_run_data(&self, data: &serde_json::Value, target_protocol: EndpointType) -> Result<Vec<u8>, Box<dyn std::error::Error + Send + Sync>>;

    /// Transforms batch data to protocol-specific format
    fn transform_batch_data(&self, records: &[serde_json::Value], target_protocol: EndpointType) -> Result<Vec<u8>, Box<dyn std::error::Error + Send + Sync>>;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_enhanced_config_creation_with_api_key() {
        let config = EnhancedTelemetryConfig::with_api_key("bca_test_key");

        assert!(matches!(config.auth, AuthMode::ApiKey { .. }));
        assert_eq!(config.endpoint_type, EndpointType::TrpcLegacy);
        assert!(config.enabled);
        assert_eq!(config.legacy_api_key, Some("bca_test_key".to_string()));
    }

    #[test]
    fn test_enhanced_config_creation_with_jwt() {
        let config = EnhancedTelemetryConfig::with_jwt_token("jwt_token_123");

        assert!(matches!(config.auth, AuthMode::JwtToken { .. }));
        assert_eq!(config.endpoint_type, EndpointType::RestApi);
        assert!(config.enabled);
        assert!(config.legacy_api_key.is_none());
    }

    #[test]
    fn test_enhanced_config_creation_with_sts() {
        let config = EnhancedTelemetryConfig::with_sts_credentials(
            "access_key",
            "secret_key",
            "us-east-1",
            "telemetry-stream"
        );

        assert!(matches!(config.auth, AuthMode::StsCredentials { .. }));
        assert_eq!(config.endpoint_type, EndpointType::KinesisStream);
        assert!(config.protocol_configs.contains_key(&EndpointType::KinesisStream));
    }

    #[test]
    fn test_organization_context() {
        let org_context = OrganizationContext::new("org_123", "ml_agents")
            .with_org_name("Test Org")
            .with_environment("prod")
            .with_metadata("region", "us-west-2");

        assert_eq!(org_context.org_id, "org_123");
        assert_eq!(org_context.agent_group, "ml_agents");
        assert_eq!(org_context.org_name, Some("Test Org".to_string()));
        assert_eq!(org_context.environment, Some("prod".to_string()));
        assert_eq!(org_context.metadata.get("region"), Some(&"us-west-2".to_string()));
    }

    #[test]
    fn test_experiment_context() {
        let experiment = ExperimentContext::new("exp_123", "variant_a")
            .with_name("Feature Flag Test")
            .with_config("feature_enabled", serde_json::Value::Bool(true));

        assert_eq!(experiment.experiment_id, "exp_123");
        assert_eq!(experiment.variant, "variant_a");
        assert_eq!(experiment.experiment_name, Some("Feature Flag Test".to_string()));
        assert!(experiment.active);
        assert_eq!(experiment.config.get("feature_enabled"), Some(&serde_json::Value::Bool(true)));
    }
}