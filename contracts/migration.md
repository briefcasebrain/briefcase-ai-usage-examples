# Backward Compatibility and Migration Strategy

## Overview

This document outlines the strategy for maintaining 100% backward compatibility while modernizing the briefcase-ai-telemetry-sdk with multi-protocol support, organization context, and experiment integration.

## Backward Compatibility Guarantee

### Core Principles

1. **Zero Breaking Changes**: Existing client code will continue to work without modifications
2. **Legacy API Preservation**: All existing TelemetryConfig and TelemetryClient APIs remain functional
3. **Seamless Migration Path**: Optional migration to new features without forced updates
4. **Data Format Compatibility**: Legacy tRPC format continues to be supported

### Compatibility Matrix

| SDK Version | Legacy tRPC | Enhanced Config | Multi-Protocol | Organization Context | Experiments |
|-------------|-------------|-----------------|-----------------|---------------------|-------------|
| 0.1.x       | ✅          | ❌              | ❌              | ❌                  | ❌          |
| 1.0.x       | ✅          | ✅              | ✅              | ✅                  | ✅          |
| 2.0.x       | ✅          | ✅              | ✅              | ✅                  | ✅          |

## Legacy API Support

### TelemetryConfig Backward Compatibility

The existing `TelemetryConfig` struct remains fully functional with automatic migration to the enhanced configuration:

```rust
// Legacy configuration (continues to work)
let legacy_config = TelemetryConfig::new("bca_your_api_key".to_string())
    .with_endpoint("https://telemetry.briefcasebrain.com/api/trpc/ingest.telemetry".to_string())
    .with_timeout(Duration::from_secs(10))
    .with_batch_size(100);

// Automatic internal migration to EnhancedTelemetryConfig
let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);

// Client creation remains the same
let client = TelemetryClient::new(legacy_config)?;
```

### TelemetryClient API Preservation

All existing `TelemetryClient` methods continue to work with identical signatures:

```rust
impl TelemetryClient {
    // Existing methods - no changes
    pub fn new(config: TelemetryConfig) -> Result<Self>;
    pub async fn track_event(&self, event: Event) -> Result<()>;
    pub async fn flush(&self) -> Result<()>;
    pub async fn record_agent_run(&self, agent_run_data: &serde_json::Value) -> Result<()>;
    pub async fn send_batch(&self, records: Vec<serde_json::Value>) -> Result<()>;

    // New enhanced constructor (opt-in)
    pub fn new_enhanced(config: EnhancedTelemetryConfig) -> Result<Self>;
}
```

## Migration Strategy

### Phase 1: Legacy Wrapper Implementation

The enhanced SDK wraps the legacy configuration seamlessly:

```rust
pub struct TelemetryClient {
    // Internal implementation uses enhanced config
    enhanced_config: EnhancedTelemetryConfig,
    protocol_client: Box<dyn ProtocolClient>,
    experiment_manager: Option<Box<dyn ExperimentManager>>,

    // Legacy compatibility fields
    legacy_mode: bool,
    legacy_config: Option<TelemetryConfig>,
}

impl TelemetryClient {
    pub fn new(legacy_config: TelemetryConfig) -> Result<Self> {
        // Convert legacy config to enhanced config
        let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);

        // Create appropriate protocol client (defaults to TrpcLegacy)
        let protocol_client = ProtocolClientFactory::create_client(&enhanced_config);

        Ok(Self {
            enhanced_config,
            protocol_client,
            experiment_manager: None,  // Disabled in legacy mode
            legacy_mode: true,
            legacy_config: Some(legacy_config),
        })
    }
}
```

### Phase 2: Data Format Migration

Legacy data format is preserved with optional enhancement:

```rust
impl DataTransformer for LegacyCompatibilityTransformer {
    fn transform_telemetry_data(&self, data: &TelemetryData, target_protocol: EndpointType) -> Result<Vec<u8>, Box<dyn std::error::Error + Send + Sync>> {
        match target_protocol {
            EndpointType::TrpcLegacy => {
                // Preserve exact legacy format
                let legacy_payload = TrpcPayload {
                    json: LegacyTelemetryPayload {
                        api_key: self.get_legacy_api_key()?,
                        session: data.session.clone(),
                        events: data.events.clone(),
                        metadata: data.metadata.clone(),
                        timestamp: data.timestamp,
                        sdk_version: data.sdk_version.clone(),
                        platform: data.platform.clone(),
                        environment: data.environment.clone(),
                        // Optional enhancement (only if organization context is available)
                        organization: data.organization.clone(),
                        experiments: data.experiments.clone(),
                    }
                };

                Ok(serde_json::to_vec(&legacy_payload)?)
            }
            _ => {
                // Use new format transformers for other protocols
                DefaultDataTransformer::new().transform_telemetry_data(data, target_protocol)
            }
        }
    }
}
```

### Phase 3: Gradual Feature Adoption

Users can gradually adopt new features without breaking existing functionality:

```rust
// Step 1: Continue using legacy config
let legacy_config = TelemetryConfig::new("bca_key".to_string());
let client = TelemetryClient::new(legacy_config)?;

// Step 2: Migrate to enhanced config with same behavior
let enhanced_config = EnhancedTelemetryConfig::with_api_key("bca_key");
let client = TelemetryClient::new_enhanced(enhanced_config)?;

// Step 3: Add organization context
let enhanced_config = EnhancedTelemetryConfig::with_api_key("bca_key")
    .with_organization(OrganizationContext::new("org_123", "ml_agents"));
let client = TelemetryClient::new_enhanced(enhanced_config)?;

// Step 4: Add experiments
let enhanced_config = EnhancedTelemetryConfig::with_api_key("bca_key")
    .with_organization(OrganizationContext::new("org_123", "ml_agents"))
    .with_experiment(ExperimentContext::new("exp_456", "variant_a"));
let client = TelemetryClient::new_enhanced(enhanced_config)?;

// Step 5: Switch to modern protocols
let enhanced_config = EnhancedTelemetryConfig::with_jwt_token("jwt_token")
    .with_endpoint(EndpointType::RestApi, "https://telemetry.briefcasebrain.com/api/v1/telemetry")
    .with_organization(OrganizationContext::new("org_123", "ml_agents"));
let client = TelemetryClient::new_enhanced(enhanced_config)?;
```

## Data Migration Patterns

### Legacy tRPC to Enhanced Format

```rust
pub struct LegacyDataMigrator;

impl LegacyDataMigrator {
    pub fn migrate_telemetry_data(legacy_data: &LegacyTelemetryData) -> EnhancedTelemetryData {
        EnhancedTelemetryData {
            // Direct mappings
            session: legacy_data.session.clone(),
            events: legacy_data.events.clone(),
            metadata: legacy_data.metadata.clone(),
            timestamp: legacy_data.timestamp,
            sdk_version: legacy_data.sdk_version.clone(),
            platform: legacy_data.platform.clone(),
            environment: legacy_data.environment.clone(),

            // New fields with defaults
            organization: None,  // Will be populated if available
            experiments: vec![], // Will be populated if available

            // Enhanced metadata
            enhanced_metadata: HashMap::new(),
        }
    }

    pub fn extract_organization_from_metadata(metadata: &HashMap<String, serde_json::Value>) -> Option<OrganizationContext> {
        // Try to extract organization info from legacy metadata
        let org_id = metadata.get("organization_id")?.as_str()?;
        let agent_group = metadata.get("agent_group")?.as_str().unwrap_or("default");

        Some(OrganizationContext::new(org_id, agent_group))
    }
}
```

### Repository Naming Migration

When migrating to LakeFS, legacy data gets organized into a structured format:

```rust
pub struct RepositoryNamingMigrator;

impl RepositoryNamingMigrator {
    pub fn generate_legacy_path(session_id: &str, timestamp: &DateTime<Utc>) -> String {
        // Legacy sessions without organization context go into a special path
        format!("/legacy/{}/{}/session_{}.json",
            timestamp.format("%Y-%m"),
            timestamp.format("%d"),
            session_id
        )
    }

    pub fn generate_enhanced_path(org_context: &OrganizationContext, session_id: &str, timestamp: &DateTime<Utc>) -> String {
        format!("/telemetry/{}/{}/{}/session_{}.json",
            org_context.org_id,
            org_context.agent_group,
            timestamp.format("%Y-%m-%d"),
            session_id
        )
    }

    pub fn migrate_legacy_data_to_organized_structure(&self) -> Result<()> {
        // Migration script for existing data
        // 1. Scan legacy paths
        // 2. Extract organization info from metadata
        // 3. Move to organized structure
        // 4. Update indices
        Ok(())
    }
}
```

## Authentication Migration

### API Key to JWT Migration

```rust
pub struct AuthenticationMigrator;

impl AuthenticationMigrator {
    pub async fn migrate_api_key_to_jwt(api_key: &str) -> Result<String, Box<dyn std::error::Error + Send + Sync>> {
        // Exchange API key for JWT token via admin endpoint
        let client = reqwest::Client::new();
        let response = client
            .post("https://telemetry.briefcasebrain.com/api/auth/exchange")
            .header("Authorization", format!("ApiKey {}", api_key))
            .send()
            .await?;

        if response.status().is_success() {
            let auth_response: AuthExchangeResponse = response.json().await?;
            Ok(auth_response.jwt_token)
        } else {
            Err("Failed to exchange API key for JWT token".into())
        }
    }

    pub fn create_migration_config(legacy_config: &TelemetryConfig, jwt_token: String) -> EnhancedTelemetryConfig {
        EnhancedTelemetryConfig::with_jwt_token(jwt_token)
            .with_endpoint(EndpointType::RestApi, "https://telemetry.briefcasebrain.com/api/v1/telemetry")
            .with_batch_size(legacy_config.batch_size)
            .with_timeout(legacy_config.timeout)
            .with_retry_attempts(legacy_config.retry_attempts)
            .with_flush_interval(legacy_config.flush_interval)
            .with_enabled(legacy_config.enabled)
    }
}
```

### STS Credentials Setup

```rust
pub struct AwsCredentialsMigrator;

impl AwsCredentialsMigrator {
    pub async fn setup_sts_credentials_from_api_key(api_key: &str, region: &str) -> Result<EnhancedTelemetryConfig, Box<dyn std::error::Error + Send + Sync>> {
        // Request STS credentials from Briefcase AI platform
        let client = reqwest::Client::new();
        let response = client
            .post("https://telemetry.briefcasebrain.com/api/aws/credentials")
            .header("Authorization", format!("ApiKey {}", api_key))
            .json(&serde_json::json!({
                "region": region,
                "purpose": "telemetry_ingestion"
            }))
            .send()
            .await?;

        if response.status().is_success() {
            let creds: StsCredentialsResponse = response.json().await?;

            let config = EnhancedTelemetryConfig::with_sts_credentials(
                creds.access_key_id,
                creds.secret_access_key,
                region,
                "briefcase-telemetry-stream"
            );

            Ok(config)
        } else {
            Err("Failed to obtain STS credentials".into())
        }
    }
}
```

## Version Detection and Feature Flags

### SDK Version Detection

```rust
pub struct CompatibilityManager;

impl CompatibilityManager {
    pub fn detect_client_version(user_agent: &str) -> SdkVersion {
        // Parse User-Agent header to determine SDK version
        if user_agent.contains("briefcase-ai-telemetry-sdk/0.1") {
            SdkVersion::Legacy
        } else if user_agent.contains("briefcase-ai-telemetry-sdk/1.") {
            SdkVersion::Enhanced
        } else {
            SdkVersion::Unknown
        }
    }

    pub fn get_supported_features(version: SdkVersion) -> Vec<Feature> {
        match version {
            SdkVersion::Legacy => vec![Feature::TrpcProtocol, Feature::BasicTelemetry],
            SdkVersion::Enhanced => vec![
                Feature::TrpcProtocol,
                Feature::RestApiProtocol,
                Feature::KinesisStreamProtocol,
                Feature::LakeFSDirectProtocol,
                Feature::OrganizationContext,
                Feature::ExperimentTracking,
                Feature::MultiTenant,
            ],
            SdkVersion::Unknown => vec![Feature::TrpcProtocol], // Safe fallback
        }
    }
}
```

### Server-Side Feature Flags

```rust
pub struct FeatureFlags {
    pub enable_enhanced_features: bool,
    pub enable_organization_context: bool,
    pub enable_experiment_tracking: bool,
    pub enable_multi_protocol: bool,
    pub force_legacy_mode: bool,
}

impl FeatureFlags {
    pub fn from_client_version(version: SdkVersion) -> Self {
        match version {
            SdkVersion::Legacy => Self {
                enable_enhanced_features: false,
                enable_organization_context: false,
                enable_experiment_tracking: false,
                enable_multi_protocol: false,
                force_legacy_mode: true,
            },
            SdkVersion::Enhanced => Self {
                enable_enhanced_features: true,
                enable_organization_context: true,
                enable_experiment_tracking: true,
                enable_multi_protocol: true,
                force_legacy_mode: false,
            },
            SdkVersion::Unknown => Self::legacy_safe_defaults(),
        }
    }

    pub fn legacy_safe_defaults() -> Self {
        Self {
            enable_enhanced_features: false,
            enable_organization_context: false,
            enable_experiment_tracking: false,
            enable_multi_protocol: false,
            force_legacy_mode: true,
        }
    }
}
```

## Testing Strategy

### Backward Compatibility Tests

```rust
#[cfg(test)]
mod backward_compatibility_tests {
    use super::*;

    #[tokio::test]
    async fn test_legacy_config_still_works() {
        let legacy_config = TelemetryConfig::new("bca_test_key".to_string())
            .with_endpoint("https://test.api.com/api/trpc/ingest.telemetry".to_string());

        let client = TelemetryClient::new(legacy_config);
        assert!(client.is_ok());

        let event = EventBuilder::new("test_event".to_string()).build();
        let result = client.unwrap().track_event(event).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_legacy_data_format_preserved() {
        let legacy_config = TelemetryConfig::new("bca_test_key".to_string());
        let client = TelemetryClient::new(legacy_config).unwrap();

        // Verify that the client uses TrpcLegacy protocol by default
        assert_eq!(client.enhanced_config.endpoint_type, EndpointType::TrpcLegacy);
        assert!(client.legacy_mode);
    }

    #[tokio::test]
    async fn test_migration_preserves_behavior() {
        let legacy_config = TelemetryConfig::new("bca_test_key".to_string());
        let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);

        // Verify that behavior is preserved
        assert_eq!(enhanced_config.endpoint_type, EndpointType::TrpcLegacy);
        assert!(matches!(enhanced_config.auth, AuthMode::ApiKey { .. }));
        assert_eq!(enhanced_config.timeout, legacy_config.timeout);
        assert_eq!(enhanced_config.batch_size, legacy_config.batch_size);
        assert_eq!(enhanced_config.enabled, legacy_config.enabled);
    }

    #[test]
    fn test_data_transformation_backward_compatibility() {
        let legacy_data = create_legacy_telemetry_data();
        let migrated_data = LegacyDataMigrator::migrate_telemetry_data(&legacy_data);

        // Verify that essential fields are preserved
        assert_eq!(migrated_data.session, legacy_data.session);
        assert_eq!(migrated_data.events, legacy_data.events);
        assert_eq!(migrated_data.metadata, legacy_data.metadata);
    }
}
```

### Migration Path Testing

```rust
#[cfg(test)]
mod migration_tests {
    #[tokio::test]
    async fn test_gradual_feature_adoption() {
        // Step 1: Legacy
        let legacy_config = TelemetryConfig::new("bca_test".to_string());
        let legacy_client = TelemetryClient::new(legacy_config).unwrap();

        // Step 2: Enhanced with same behavior
        let enhanced_config = EnhancedTelemetryConfig::with_api_key("bca_test");
        let enhanced_client = TelemetryClient::new_enhanced(enhanced_config).unwrap();

        // Both clients should behave identically
        let event = EventBuilder::new("test".to_string()).build();

        let legacy_result = legacy_client.track_event(event.clone()).await;
        let enhanced_result = enhanced_client.track_event(event).await;

        assert_eq!(legacy_result.is_ok(), enhanced_result.is_ok());
    }

    #[tokio::test]
    async fn test_organization_context_addition() {
        let mut enhanced_config = EnhancedTelemetryConfig::with_api_key("bca_test");

        // Should work without organization context
        let client_without_org = TelemetryClient::new_enhanced(enhanced_config.clone()).unwrap();

        // Should work with organization context
        enhanced_config = enhanced_config.with_organization(
            OrganizationContext::new("org_123", "ml_agents")
        );
        let client_with_org = TelemetryClient::new_enhanced(enhanced_config).unwrap();

        // Both should work
        let event = EventBuilder::new("test".to_string()).build();
        assert!(client_without_org.track_event(event.clone()).await.is_ok());
        assert!(client_with_org.track_event(event).await.is_ok());
    }
}
```

## Rollback Strategy

### Automatic Rollback Triggers

```rust
pub struct RollbackManager {
    error_threshold: f64,
    monitoring_window: Duration,
    error_counts: Arc<RwLock<HashMap<String, u32>>>,
}

impl RollbackManager {
    pub async fn check_rollback_conditions(&self) -> bool {
        let error_rate = self.calculate_error_rate().await;

        if error_rate > self.error_threshold {
            tracing::error!("Error rate {} exceeds threshold {}, triggering rollback",
                           error_rate, self.error_threshold);
            true
        } else {
            false
        }
    }

    pub async fn execute_rollback(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        // 1. Disable enhanced features
        // 2. Force legacy mode for all clients
        // 3. Notify operations team
        // 4. Update feature flags

        tracing::info!("Executing rollback to legacy mode");

        // Update global feature flags
        let feature_flags = FeatureFlags::legacy_safe_defaults();
        self.update_feature_flags(feature_flags).await?;

        Ok(())
    }
}
```

### Manual Rollback Procedures

```bash
#!/bin/bash
# rollback-to-legacy.sh

echo "Rolling back briefcase-ai-telemetry-sdk to legacy mode..."

# 1. Update feature flags in configuration service
curl -X POST https://telemetry.briefcasebrain.com/api/admin/feature-flags \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "enable_enhanced_features": false,
    "enable_organization_context": false,
    "enable_experiment_tracking": false,
    "enable_multi_protocol": false,
    "force_legacy_mode": true
  }'

# 2. Restart services with legacy configuration
kubectl set env deployment/telemetry-service FORCE_LEGACY_MODE=true

# 3. Verify rollback
kubectl get pods -l app=telemetry-service
kubectl logs -l app=telemetry-service --tail=50

echo "Rollback completed. All clients will use legacy tRPC protocol."
```

## Documentation Migration

### API Documentation Updates

```markdown
## Migration Guide

### For Existing Users (v0.1.x)

Your existing code will continue to work without any changes:

```rust
// This still works exactly as before
let config = TelemetryConfig::new("bca_your_api_key".to_string());
let client = TelemetryClient::new(config)?;
client.track_event(event).await?;
```

### For New Users (v1.0.x+)

New users can leverage enhanced features:

```rust
// Modern configuration with organization context
let config = EnhancedTelemetryConfig::with_api_key("bca_your_api_key")
    .with_organization(OrganizationContext::new("your_org", "agent_group"));
let client = TelemetryClient::new_enhanced(config)?;
```

### Migration Timeline

- **v1.0.x**: Enhanced features available, legacy fully supported
- **v1.x.x**: Continued support for both legacy and enhanced modes
- **v2.0.x**: Legacy mode still supported, enhanced mode is default
```

This comprehensive migration strategy ensures that existing users experience zero disruption while providing a clear path for adopting new features and capabilities.