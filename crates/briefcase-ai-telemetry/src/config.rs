use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;

/// Legacy configuration structure - maintained for backward compatibility
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryConfig {
    pub api_key: String,
    pub endpoint: String,
    pub timeout: Duration,
    pub retry_attempts: u32,
    pub batch_size: usize,
    pub flush_interval: Duration,
    pub enabled: bool,
}

/// Enumeration of supported endpoint types for multi-protocol architecture
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash, Default)]
pub enum EndpointType {
    /// Legacy tRPC protocol (maintains backward compatibility)
    #[default]
    TrpcLegacy,
    /// REST API protocol for standardized HTTP endpoints
    RestApi,
    /// AWS Kinesis Stream for high-throughput real-time data ingestion
    KinesisStream,
    /// Direct LakeFS integration for data versioning and lineage
    LakefsDirect,
}

/// Authentication modes for different protocol types and use cases
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
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
        Self::JwtToken {
            token: token.into(),
        }
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
            endpoint_type: EndpointType::RestApi,
            endpoint_url: "https://telemetry.briefcasebrain.com/api/v1/telemetry".to_string(),
            fallback_endpoints: vec![
                // Fallback to legacy tRPC endpoint for backward compatibility
                (
                    EndpointType::TrpcLegacy,
                    "https://telemetry.briefcasebrain.com/api/trpc/ingest.telemetry".to_string(),
                ),
            ],
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
            endpoint_url: "https://telemetry.briefcasebrain.com/api/v1/telemetry".to_string(),
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
            }),
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
    pub fn with_fallback_endpoint(
        mut self,
        endpoint_type: EndpointType,
        url: impl Into<String>,
    ) -> Self {
        self.fallback_endpoints.push((endpoint_type, url.into()));
        self
    }

    /// Sets protocol-specific configuration
    pub fn with_protocol_config(
        mut self,
        endpoint_type: EndpointType,
        config: serde_json::Value,
    ) -> Self {
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
    pub fn from_legacy(legacy_config: &TelemetryConfig) -> Self {
        Self::with_api_key(legacy_config.api_key.clone())
            .with_endpoint(EndpointType::TrpcLegacy, legacy_config.endpoint.clone())
            .with_timeout(legacy_config.timeout)
            .with_retry_attempts(legacy_config.retry_attempts)
            .with_batch_size(legacy_config.batch_size)
            .with_flush_interval(legacy_config.flush_interval)
            .with_enabled(legacy_config.enabled)
    }
}

impl TelemetryConfig {
    pub fn new(api_key: String) -> Self {
        Self {
            api_key,
            endpoint: "https://telemetry.briefcasebrain.com/api/v1/telemetry".to_string(),
            timeout: Duration::from_secs(10),
            retry_attempts: 3,
            batch_size: 100,
            flush_interval: Duration::from_secs(5),
            enabled: true,
        }
    }

    pub fn with_endpoint(mut self, endpoint: String) -> Self {
        self.endpoint = endpoint;
        self
    }

    pub fn with_timeout(mut self, timeout: Duration) -> Self {
        self.timeout = timeout;
        self
    }

    pub fn with_retry_attempts(mut self, retry_attempts: u32) -> Self {
        self.retry_attempts = retry_attempts;
        self
    }

    pub fn with_batch_size(mut self, batch_size: usize) -> Self {
        self.batch_size = batch_size;
        self
    }

    pub fn with_flush_interval(mut self, flush_interval: Duration) -> Self {
        self.flush_interval = flush_interval;
        self
    }

    pub fn with_enabled(mut self, enabled: bool) -> Self {
        self.enabled = enabled;
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // Legacy TelemetryConfig tests (backward compatibility)
    #[test]
    fn test_config_creation() {
        let config = TelemetryConfig::new("test_key".to_string());
        assert_eq!(config.api_key, "test_key");
        assert_eq!(
            config.endpoint,
            "https://telemetry.briefcasebrain.com/api/v1/telemetry"
        );
        assert!(config.enabled);
    }

    #[test]
    fn test_config_with_custom_endpoint() {
        let config = TelemetryConfig::new("test_key".to_string())
            .with_endpoint("https://custom.endpoint.com/telemetry".to_string());
        assert_eq!(config.endpoint, "https://custom.endpoint.com/telemetry");
    }

    #[test]
    fn test_config_disabled() {
        let config = TelemetryConfig::new("test_key".to_string()).with_enabled(false);
        assert!(!config.enabled);
    }

    // EnhancedTelemetryConfig tests (new features)
    #[test]
    fn test_enhanced_config_creation_with_api_key() {
        let config = EnhancedTelemetryConfig::with_api_key("bca_test_key");

        assert!(matches!(config.auth, AuthMode::ApiKey { .. }));
        assert_eq!(config.endpoint_type, EndpointType::RestApi);
        assert_eq!(
            config.endpoint_url,
            "https://telemetry.briefcasebrain.com/api/v1/telemetry"
        );
        assert!(config.enabled);
        assert_eq!(config.legacy_api_key, Some("bca_test_key".to_string()));
        // Verify fallback endpoint is configured
        assert_eq!(config.fallback_endpoints.len(), 1);
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
            "telemetry-stream",
        );

        assert!(matches!(config.auth, AuthMode::StsCredentials { .. }));
        assert_eq!(config.endpoint_type, EndpointType::KinesisStream);
        assert!(config
            .protocol_configs
            .contains_key(&EndpointType::KinesisStream));
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
        assert_eq!(
            org_context.metadata.get("region"),
            Some(&"us-west-2".to_string())
        );
    }

    #[test]
    fn test_experiment_context() {
        let experiment = ExperimentContext::new("exp_123", "variant_a")
            .with_name("Feature Flag Test")
            .with_config("feature_enabled", serde_json::Value::Bool(true));

        assert_eq!(experiment.experiment_id, "exp_123");
        assert_eq!(experiment.variant, "variant_a");
        assert_eq!(
            experiment.experiment_name,
            Some("Feature Flag Test".to_string())
        );
        assert!(experiment.active);
        assert_eq!(
            experiment.config.get("feature_enabled"),
            Some(&serde_json::Value::Bool(true))
        );
    }

    #[test]
    fn test_enhanced_config_with_organization_and_experiments() {
        let org_context = OrganizationContext::new("org_456", "data_team");
        let experiment = ExperimentContext::new("exp_789", "control");

        let config = EnhancedTelemetryConfig::with_api_key("bca_test")
            .with_organization(org_context)
            .with_experiment(experiment);

        assert!(config.organization.is_some());
        assert_eq!(config.experiments.len(), 1);
        assert_eq!(config.experiments[0].experiment_id, "exp_789");
    }

    #[test]
    fn test_enhanced_config_from_legacy() {
        let legacy_config = TelemetryConfig::new("legacy_key".to_string())
            .with_endpoint("https://legacy.endpoint.com".to_string())
            .with_batch_size(50);

        let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);

        assert!(matches!(enhanced_config.auth, AuthMode::ApiKey { .. }));
        assert_eq!(enhanced_config.endpoint_type, EndpointType::TrpcLegacy);
        assert_eq!(enhanced_config.endpoint_url, "https://legacy.endpoint.com");
        assert_eq!(enhanced_config.batch_size, 50);
        assert_eq!(
            enhanced_config.legacy_api_key,
            Some("legacy_key".to_string())
        );
    }

    #[test]
    fn test_auth_mode_constructors() {
        let api_key_auth = AuthMode::api_key("bca_123");
        assert!(matches!(api_key_auth, AuthMode::ApiKey { .. }));

        let jwt_auth = AuthMode::jwt_token("jwt_456");
        assert!(matches!(jwt_auth, AuthMode::JwtToken { .. }));

        let sts_auth = AuthMode::sts_credentials("access", "secret", "us-east-1");
        assert!(matches!(sts_auth, AuthMode::StsCredentials { .. }));

        let sts_auth_with_session =
            AuthMode::sts_credentials_with_session("access", "secret", "session", "us-west-2");
        if let AuthMode::StsCredentials { session_token, .. } = sts_auth_with_session {
            assert_eq!(session_token, Some("session".to_string()));
        } else {
            panic!("Expected StsCredentials with session token");
        }
    }

    #[test]
    fn test_endpoint_type_default() {
        let default_endpoint = EndpointType::default();
        assert_eq!(default_endpoint, EndpointType::TrpcLegacy);
    }

    #[test]
    fn test_enhanced_config_fallback_endpoints() {
        let config = EnhancedTelemetryConfig::with_jwt_token("token")
            .with_fallback_endpoint(EndpointType::TrpcLegacy, "https://backup.example.com")
            .with_fallback_endpoint(EndpointType::KinesisStream, "kinesis-backup");

        assert_eq!(config.fallback_endpoints.len(), 2);
        assert_eq!(config.fallback_endpoints[0].0, EndpointType::TrpcLegacy);
        assert_eq!(config.fallback_endpoints[0].1, "https://backup.example.com");
    }

    #[test]
    fn test_enhanced_config_protocol_configs() {
        let kinesis_config = serde_json::json!({
            "stream_name": "test-stream",
            "batch_size": 250
        });

        let config = EnhancedTelemetryConfig::with_api_key("test")
            .with_protocol_config(EndpointType::KinesisStream, kinesis_config.clone());

        assert_eq!(
            config.protocol_configs.get(&EndpointType::KinesisStream),
            Some(&kinesis_config)
        );
    }
}
