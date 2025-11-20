use serde::{Deserialize, Serialize};
use std::time::Duration;

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

impl TelemetryConfig {
    pub fn new(api_key: String) -> Self {
        Self {
            api_key,
            endpoint: "https://your-telemetry-endpoint.com/api/trpc/ingest.telemetry".to_string(),
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

    #[test]
    fn test_config_creation() {
        let config = TelemetryConfig::new("test_key".to_string());
        assert_eq!(config.api_key, "test_key");
        assert_eq!(
            config.endpoint,
            "https://your-telemetry-endpoint.com/api/trpc/ingest.telemetry"
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
}
