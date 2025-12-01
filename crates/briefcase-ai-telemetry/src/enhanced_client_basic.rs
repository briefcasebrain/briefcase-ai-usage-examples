//! Basic Enhanced Telemetry Client
//!
//! A simplified version of the enhanced client that maintains backward compatibility
//! while providing access to new features.

use crate::config::{EnhancedTelemetryConfig, TelemetryConfig};
use crate::{Event, Session, TelemetryClient};
use anyhow::Result;

/// Enhanced telemetry client that wraps the legacy client for backward compatibility
pub struct BasicEnhancedTelemetryClient {
    legacy_client: TelemetryClient,
    config: EnhancedTelemetryConfig,
}

impl BasicEnhancedTelemetryClient {
    /// Creates a new basic enhanced telemetry client from enhanced config
    pub fn new(config: EnhancedTelemetryConfig) -> Result<Self> {
        // Convert enhanced config to legacy config for compatibility
        let legacy_config = match &config.auth {
            crate::config::AuthMode::ApiKey { key } => TelemetryConfig::new(key.clone())
                .with_endpoint(config.endpoint_url.clone())
                .with_timeout(config.timeout)
                .with_retry_attempts(config.retry_attempts)
                .with_batch_size(config.batch_size)
                .with_flush_interval(config.flush_interval)
                .with_enabled(config.enabled),
            _ => {
                // For non-API key auth, use a placeholder key
                TelemetryConfig::new("placeholder_key".to_string())
                    .with_endpoint(config.endpoint_url.clone())
                    .with_timeout(config.timeout)
                    .with_retry_attempts(config.retry_attempts)
                    .with_batch_size(config.batch_size)
                    .with_flush_interval(config.flush_interval)
                    .with_enabled(config.enabled)
            }
        };

        let legacy_client = TelemetryClient::new(legacy_config)?;

        Ok(Self {
            legacy_client,
            config,
        })
    }

    /// Creates from legacy config for backward compatibility
    pub fn from_legacy_config(legacy_config: TelemetryConfig) -> Result<Self> {
        let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);
        let legacy_client = TelemetryClient::new(legacy_config)?;

        Ok(Self {
            legacy_client,
            config: enhanced_config,
        })
    }

    /// Tracks an event (delegates to legacy client)
    pub async fn track_event(&self, event: Event) -> Result<()> {
        self.legacy_client.track_event(event).await
    }

    /// Flushes events (delegates to legacy client)
    pub async fn flush(&self) -> Result<()> {
        self.legacy_client.flush().await
    }

    /// Records agent run (delegates to legacy client)
    pub async fn record_agent_run(&self, agent_run_data: &serde_json::Value) -> Result<()> {
        self.legacy_client.record_agent_run(agent_run_data).await
    }

    /// Sends batch data (delegates to legacy client)
    pub async fn send_batch(&self, records: Vec<serde_json::Value>) -> Result<()> {
        self.legacy_client.send_batch(records).await
    }

    /// Starts background flush (delegates to legacy client)
    pub async fn start_background_flush(&self) -> Result<()> {
        self.legacy_client.start_background_flush().await
    }

    /// Gets session (delegates to legacy client)
    pub fn session(&self) -> &Session {
        self.legacy_client.session()
    }

    /// Gets enhanced config
    pub fn enhanced_config(&self) -> &EnhancedTelemetryConfig {
        &self.config
    }

    /// Gets legacy config
    pub fn legacy_config(&self) -> &TelemetryConfig {
        self.legacy_client.config()
    }

    /// Gets buffer size (delegates to legacy client)
    pub async fn buffer_size(&self) -> usize {
        self.legacy_client.buffer_size().await
    }
}

impl Clone for BasicEnhancedTelemetryClient {
    fn clone(&self) -> Self {
        Self {
            legacy_client: self.legacy_client.clone(),
            config: self.config.clone(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{EventBuilder, EventLevel};
    use std::time::Duration;

    #[tokio::test]
    async fn test_basic_enhanced_client_creation() {
        let config = EnhancedTelemetryConfig::with_api_key("bca_test_key")
            .with_timeout(Duration::from_secs(1))
            .with_batch_size(2)
            .with_enabled(false);

        let client = BasicEnhancedTelemetryClient::new(config).unwrap();
        assert_eq!(client.enhanced_config().batch_size, 2);
        assert!(!client.enhanced_config().enabled);
    }

    #[tokio::test]
    async fn test_from_legacy_config() {
        let legacy_config = TelemetryConfig::new("test_key".to_string())
            .with_endpoint("https://test.example.com".to_string())
            .with_batch_size(50);

        let client = BasicEnhancedTelemetryClient::from_legacy_config(legacy_config).unwrap();
        assert_eq!(client.enhanced_config().batch_size, 50);
    }

    #[tokio::test]
    async fn test_track_event() {
        let config = EnhancedTelemetryConfig::with_api_key("bca_test_key").with_enabled(false);

        let client = BasicEnhancedTelemetryClient::new(config).unwrap();

        let event = EventBuilder::new("test_event".to_string())
            .level(EventLevel::Info)
            .build();

        let result = client.track_event(event).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_flush() {
        let config = EnhancedTelemetryConfig::with_api_key("bca_test_key").with_enabled(false);

        let client = BasicEnhancedTelemetryClient::new(config).unwrap();

        let result = client.flush().await;
        assert!(result.is_ok());
    }
}
