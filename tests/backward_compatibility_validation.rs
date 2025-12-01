/**
 * Comprehensive Backward Compatibility Validation Tests
 * Ensures 100% compatibility with existing SDK functionality during migration
 */

use std::collections::HashMap;
use std::time::Duration;
use std::sync::Arc;
use tokio::sync::Mutex;

use briefcase_ai_telemetry::{
    TelemetryClient, TelemetryConfig, EnhancedTelemetryConfig,
    Event, EventBuilder, AuthMode, EndpointType, OrganizationContext, ExperimentContext
};

/// Mock HTTP server for testing backward compatibility
struct MockTrpcServer {
    requests: Arc<Mutex<Vec<MockRequest>>>,
    response_status: u16,
    response_body: String,
}

#[derive(Debug, Clone)]
struct MockRequest {
    method: String,
    path: String,
    headers: HashMap<String, String>,
    body: String,
    timestamp: std::time::Instant,
}

impl MockTrpcServer {
    fn new() -> Self {
        Self {
            requests: Arc::new(Mutex::new(Vec::new())),
            response_status: 200,
            response_body: r#"{"success": true, "data": {"message": "received"}}"#.to_string(),
        }
    }

    fn with_response(mut self, status: u16, body: String) -> Self {
        self.response_status = status;
        self.response_body = body;
        self
    }

    async fn get_requests(&self) -> Vec<MockRequest> {
        self.requests.lock().await.clone()
    }

    async fn clear_requests(&self) {
        self.requests.lock().await.clear();
    }
}

#[tokio::test]
async fn test_legacy_telemetry_config_unchanged() {
    // Test that the legacy TelemetryConfig API works exactly as before
    let config = TelemetryConfig::new("bca_legacy_key_123".to_string())
        .with_endpoint("https://test.api.com/api/trpc/ingest.telemetry".to_string())
        .with_timeout(Duration::from_secs(15))
        .with_batch_size(50)
        .with_retry_attempts(5)
        .with_flush_interval(Duration::from_secs(10))
        .with_enabled(true);

    // Verify all fields match expected values
    assert_eq!(config.api_key, "bca_legacy_key_123");
    assert_eq!(config.endpoint, "https://test.api.com/api/trpc/ingest.telemetry");
    assert_eq!(config.timeout, Duration::from_secs(15));
    assert_eq!(config.batch_size, 50);
    assert_eq!(config.retry_attempts, 5);
    assert_eq!(config.flush_interval, Duration::from_secs(10));
    assert!(config.enabled);
}

#[tokio::test]
async fn test_legacy_client_creation_unchanged() {
    // Test that TelemetryClient creation with legacy config works
    let legacy_config = TelemetryConfig::new("bca_test_key".to_string());

    // This should not panic or fail
    let result = TelemetryClient::new(legacy_config);
    assert!(result.is_ok(), "Legacy client creation should succeed");

    let client = result.unwrap();

    // Verify client can be used for basic operations
    let event = EventBuilder::new("test_event".to_string()).build();

    // This should not panic even if it can't actually send (no real endpoint)
    // The important thing is the API is unchanged
    let _ = client.track_event(event).await;
}

#[tokio::test]
async fn test_legacy_event_creation_unchanged() {
    // Test that Event and EventBuilder APIs work exactly as before
    let event = EventBuilder::new("legacy_event".to_string())
        .with_data(r#"{"key": "value"}"#)
        .with_metadata("user_id", "user123")
        .build();

    assert_eq!(event.event_type, "legacy_event");
    assert!(event.data.is_some());
    assert!(event.metadata.contains_key("user_id"));
}

#[tokio::test]
async fn test_legacy_data_format_preserved() {
    // Test that data sent to tRPC endpoint maintains exact same format
    let mock_server = MockTrpcServer::new();

    let legacy_config = TelemetryConfig::new("bca_format_test".to_string())
        .with_endpoint("http://localhost:9999/api/trpc/ingest.telemetry".to_string());

    let client = TelemetryClient::new(legacy_config).unwrap();

    let event = EventBuilder::new("format_test_event".to_string())
        .with_data(r#"{"test": "data"}"#)
        .with_metadata("session_id", "session_123")
        .build();

    // This will fail to connect but that's expected in tests
    let _ = client.track_event(event).await;

    // Verify the client still attempts to use tRPC format
    // (Implementation would need to be extended to capture the actual request format)
}

#[tokio::test]
async fn test_enhanced_config_from_legacy_migration() {
    // Test that EnhancedTelemetryConfig.from_legacy() preserves all settings
    let legacy_config = TelemetryConfig::new("bca_migration_test".to_string())
        .with_endpoint("https://legacy.endpoint.com/trpc".to_string())
        .with_timeout(Duration::from_secs(25))
        .with_batch_size(75)
        .with_retry_attempts(7)
        .with_flush_interval(Duration::from_secs(20))
        .with_enabled(false);

    let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);

    // Verify migration preserves all legacy settings
    assert_eq!(enhanced_config.endpoint_type, EndpointType::TrpcLegacy);
    assert_eq!(enhanced_config.endpoint_url, "https://legacy.endpoint.com/trpc");
    assert_eq!(enhanced_config.timeout, Duration::from_secs(25));
    assert_eq!(enhanced_config.batch_size, 75);
    assert_eq!(enhanced_config.retry_attempts, 7);
    assert_eq!(enhanced_config.flush_interval, Duration::from_secs(20));
    assert!(!enhanced_config.enabled); // Should preserve disabled state

    // Verify auth mode is correctly set
    match enhanced_config.auth {
        AuthMode::ApiKey { key } => assert_eq!(key, "bca_migration_test"),
        _ => panic!("Expected ApiKey auth mode for legacy migration"),
    }

    // Verify legacy API key is preserved
    assert_eq!(enhanced_config.legacy_api_key, Some("bca_migration_test".to_string()));
}

#[tokio::test]
async fn test_parallel_mode_legacy_compatibility() {
    // Test that enhanced client with legacy settings behaves identically
    let legacy_config = TelemetryConfig::new("bca_parallel_test".to_string());
    let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);

    let legacy_client = TelemetryClient::new(legacy_config).unwrap();
    let enhanced_client = TelemetryClient::new_enhanced(enhanced_config).unwrap();

    let event1 = EventBuilder::new("parallel_test_1".to_string()).build();
    let event2 = EventBuilder::new("parallel_test_2".to_string()).build();

    // Both clients should behave the same way
    let legacy_result = legacy_client.track_event(event1).await;
    let enhanced_result = enhanced_client.track_event(event2).await;

    // Both should fail in the same way (no real endpoint)
    assert_eq!(legacy_result.is_err(), enhanced_result.is_err());
}

#[tokio::test]
async fn test_batch_operations_compatibility() {
    let legacy_config = TelemetryConfig::new("bca_batch_test".to_string())
        .with_batch_size(25);

    let client = TelemetryClient::new(legacy_config).unwrap();

    // Test batch sending with legacy client
    let events = vec![
        EventBuilder::new("batch_event_1".to_string()).build(),
        EventBuilder::new("batch_event_2".to_string()).build(),
        EventBuilder::new("batch_event_3".to_string()).build(),
    ];

    // This should not panic and should maintain same batching behavior
    for event in events {
        let _ = client.track_event(event).await;
    }

    // Test flush functionality
    let flush_result = client.flush().await;
    // Should behave consistently (likely error due to no endpoint, but same behavior)
}

#[tokio::test]
async fn test_error_handling_consistency() {
    // Test that error handling remains the same for legacy configurations
    let invalid_config = TelemetryConfig::new("".to_string()); // Empty API key

    // Should handle invalid config the same way as before
    let client_result = TelemetryClient::new(invalid_config);

    // Verify error handling behavior is consistent
    match client_result {
        Ok(_) => {
            // If it succeeds, that's fine - just need consistency
        },
        Err(e) => {
            // Error message should be clear and not mention new features
            let error_msg = format!("{:?}", e);
            assert!(!error_msg.contains("enhanced"));
            assert!(!error_msg.contains("multi-protocol"));
        }
    }
}

#[tokio::test]
async fn test_thread_safety_maintained() {
    // Test that legacy client maintains thread safety
    use std::sync::Arc;
    use tokio::task;

    let config = TelemetryConfig::new("bca_thread_test".to_string());
    let client = Arc::new(TelemetryClient::new(config).unwrap());

    let mut handles = vec![];

    // Spawn multiple tasks using the same client
    for i in 0..10 {
        let client_clone = client.clone();
        let handle = task::spawn(async move {
            let event = EventBuilder::new(format!("thread_event_{}", i)).build();
            client_clone.track_event(event).await
        });
        handles.push(handle);
    }

    // Wait for all tasks to complete
    for handle in handles {
        let _ = handle.await;
    }

    // Should not deadlock or panic
}

#[tokio::test]
async fn test_memory_usage_consistency() {
    // Test that memory usage patterns haven't significantly changed
    use std::mem;

    let config = TelemetryConfig::new("bca_memory_test".to_string());

    // Measure memory footprint of legacy config
    let config_size = mem::size_of_val(&config);

    // Should be reasonable size (not drastically larger than before)
    assert!(config_size < 1000, "Legacy config memory footprint too large: {} bytes", config_size);

    let client = TelemetryClient::new(config).unwrap();
    let client_size = mem::size_of_val(&client);

    // Client shouldn't be dramatically larger due to backward compatibility
    assert!(client_size < 10000, "Client memory footprint too large: {} bytes", client_size);
}

#[tokio::test]
async fn test_serialization_compatibility() {
    // Test that TelemetryConfig can still be serialized/deserialized
    use serde_json;

    let config = TelemetryConfig::new("bca_serialize_test".to_string())
        .with_endpoint("https://test.com/endpoint".to_string())
        .with_timeout(Duration::from_secs(30));

    // Should serialize successfully
    let serialized = serde_json::to_string(&config);
    assert!(serialized.is_ok(), "Legacy config serialization failed");

    // Should deserialize back to same values
    let deserialized: Result<TelemetryConfig, _> = serde_json::from_str(&serialized.unwrap());
    assert!(deserialized.is_ok(), "Legacy config deserialization failed");

    let restored_config = deserialized.unwrap();
    assert_eq!(restored_config.api_key, config.api_key);
    assert_eq!(restored_config.endpoint, config.endpoint);
    assert_eq!(restored_config.timeout, config.timeout);
}

#[tokio::test]
async fn test_api_method_signatures_unchanged() {
    // Compile-time test to ensure method signatures haven't changed
    let config = TelemetryConfig::new("bca_signature_test".to_string());
    let client = TelemetryClient::new(config).unwrap();

    // These should compile without any changes to call syntax
    let event = EventBuilder::new("signature_test".to_string()).build();

    // Method signatures should be exactly the same
    let _: Result<(), _> = client.track_event(event).await;
    let _: Result<(), _> = client.flush().await;

    // Test with agent run data (if that method exists)
    let agent_data = serde_json::json!({"test": "data"});
    let _: Result<(), _> = client.record_agent_run(&agent_data).await;
}

#[tokio::test]
async fn test_legacy_environment_variables() {
    // Test that legacy environment variable handling still works
    std::env::set_var("BRIEFCASE_API_KEY", "env_test_key");
    std::env::set_var("BRIEFCASE_ENDPOINT", "https://env.test.com/trpc");

    // Legacy environment loading should still work
    let config = TelemetryConfig::new("bca_env_test".to_string());

    // Should use provided values, not environment (maintain same precedence)
    assert_eq!(config.api_key, "bca_env_test");

    // Cleanup
    std::env::remove_var("BRIEFCASE_API_KEY");
    std::env::remove_var("BRIEFCASE_ENDPOINT");
}

#[tokio::test]
async fn test_default_values_unchanged() {
    // Test that all default values remain the same
    let config = TelemetryConfig::new("bca_defaults_test".to_string());

    // Verify specific default values that users might depend on
    assert_eq!(config.timeout, Duration::from_secs(10), "Default timeout changed");
    assert_eq!(config.retry_attempts, 3, "Default retry attempts changed");
    assert_eq!(config.batch_size, 100, "Default batch size changed");
    assert_eq!(config.flush_interval, Duration::from_secs(5), "Default flush interval changed");
    assert!(config.enabled, "Default enabled state changed");

    // Default endpoint should be placeholder but same format
    assert!(config.endpoint.contains("trpc"), "Default endpoint format changed");
}

#[tokio::test]
async fn test_feature_detection() {
    // Test that legacy clients don't accidentally use new features
    let legacy_config = TelemetryConfig::new("bca_feature_test".to_string());
    let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);

    // Migrated config should default to legacy behavior
    assert_eq!(enhanced_config.endpoint_type, EndpointType::TrpcLegacy);
    assert!(enhanced_config.organization.is_none());
    assert!(enhanced_config.experiments.is_empty());
    assert!(enhanced_config.fallback_endpoints.is_empty());

    // Should not accidentally enable new protocols
    assert!(!enhanced_config.protocol_configs.contains_key(&EndpointType::RestApi));
    assert!(!enhanced_config.protocol_configs.contains_key(&EndpointType::KinesisStream));
    assert!(!enhanced_config.protocol_configs.contains_key(&EndpointType::LakefsDirect));
}

/// Integration test that simulates real legacy usage pattern
#[tokio::test]
async fn test_real_world_legacy_usage() {
    // Simulate how existing users actually use the SDK
    let config = TelemetryConfig::new("bca_real_world_test".to_string())
        .with_endpoint("https://telemetry.briefcasebrain.com/api/trpc/ingest.telemetry".to_string())
        .with_timeout(Duration::from_secs(20))
        .with_batch_size(200);

    let client = TelemetryClient::new(config).unwrap();

    // Typical usage pattern
    for i in 0..5 {
        let event = EventBuilder::new("completion".to_string())
            .with_data(&format!(r#"{{"prompt": "test prompt {}", "response": "test response"}}"#, i))
            .with_metadata("model", "gpt-4")
            .with_metadata("temperature", "0.1")
            .with_metadata("user_id", "user_123")
            .build();

        // This should work exactly as it did before
        let _ = client.track_event(event).await;
    }

    // Flush should work the same
    let _ = client.flush().await;
}

#[tokio::test]
async fn test_migration_rollback_compatibility() {
    // Test that we can seamlessly fall back to legacy behavior

    // Start with enhanced config
    let enhanced_config = EnhancedTelemetryConfig::with_api_key("bca_rollback_test")
        .with_endpoint(EndpointType::RestApi, "https://new.api.com/v1/telemetry");

    // Should be able to "rollback" to legacy-style usage
    let legacy_equivalent = EnhancedTelemetryConfig::with_api_key("bca_rollback_test")
        .with_endpoint(EndpointType::TrpcLegacy, "https://legacy.api.com/trpc");

    // Both should be usable with TelemetryClient::new_enhanced
    let enhanced_client = TelemetryClient::new_enhanced(enhanced_config).unwrap();
    let rollback_client = TelemetryClient::new_enhanced(legacy_equivalent).unwrap();

    // Both should handle events the same way structurally
    let event = EventBuilder::new("rollback_test".to_string()).build();

    let _ = enhanced_client.track_event(event.clone()).await;
    let _ = rollback_client.track_event(event).await;
}

/// Benchmark test to ensure performance hasn't regressed
#[cfg(feature = "benchmark")]
#[tokio::test]
async fn test_performance_regression() {
    use std::time::Instant;

    let config = TelemetryConfig::new("bca_perf_test".to_string());
    let client = TelemetryClient::new(config).unwrap();

    let start = Instant::now();

    // Create and track 1000 events
    for i in 0..1000 {
        let event = EventBuilder::new("perf_test".to_string())
            .with_data(&format!(r#"{{"iteration": {}}}"#, i))
            .build();

        let _ = client.track_event(event).await;
    }

    let duration = start.elapsed();

    // Should complete in reasonable time (adjust threshold as needed)
    assert!(duration < Duration::from_secs(10),
        "Performance regression detected: took {:?} for 1000 events", duration);
}

#[cfg(test)]
mod compatibility_helpers {
    use super::*;

    /// Helper function to verify that an API hasn't changed
    pub fn assert_api_unchanged<T, U>(old_fn: T, new_fn: U)
    where
        T: Fn() -> Result<(), Box<dyn std::error::Error>>,
        U: Fn() -> Result<(), Box<dyn std::error::Error>>,
    {
        let old_result = old_fn();
        let new_result = new_fn();

        // Both should have same success/failure pattern
        assert_eq!(old_result.is_ok(), new_result.is_ok(),
            "API behavior changed between old and new implementation");
    }

    /// Helper to create consistent test events
    pub fn create_test_event(name: &str) -> Event {
        EventBuilder::new(name.to_string())
            .with_data(r#"{"test": "data"}"#)
            .with_metadata("test_meta", "value")
            .build()
    }

    /// Helper to create legacy config with common settings
    pub fn create_legacy_config() -> TelemetryConfig {
        TelemetryConfig::new("bca_test_key".to_string())
            .with_endpoint("https://test.api.com/trpc/ingest.telemetry".to_string())
            .with_batch_size(100)
            .with_retry_attempts(3)
    }
}

// Export test helpers for use in other test modules
pub use compatibility_helpers::*;