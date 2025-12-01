#![allow(clippy::result_large_err)]
#![allow(clippy::new_without_default)]
#![allow(clippy::single_match)]
#![allow(clippy::needless_range_loop)]
#![allow(clippy::field_reassign_with_default)]
#![allow(clippy::manual_div_ceil)]

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

// Core modules
pub mod client;
pub mod compliance;
pub mod config;
pub mod cost;
pub mod drift;
pub mod event;
pub mod instrumentation;
pub mod telemetry;

// New modernization modules
pub mod auth;
pub mod enhanced_client_basic;
pub mod experiment;
pub mod protocols;
pub mod transformer;

#[cfg(feature = "python")]
pub mod python;

// Legacy exports (backward compatibility)
pub use client::TelemetryClient;
pub use config::TelemetryConfig;
pub use event::{Event, EventBuilder, EventLevel, EventMetadata};
pub use telemetry::TelemetryData;

// New exports for enhanced functionality
pub use auth::{AuthError, AuthManager};
pub use config::{
    AuthMode, EndpointType, EnhancedTelemetryConfig, ExperimentContext, OrganizationContext,
};
pub use enhanced_client_basic::BasicEnhancedTelemetryClient;
pub use experiment::{ExperimentError, ExperimentManager, ExperimentManagerFactory};
pub use protocols::{
    MultiProtocolClient, ProtocolClient, ProtocolClientFactory, ProtocolError, ProtocolResult,
};
pub use transformer::DefaultDataTransformer;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub id: Uuid,
    pub user_id: Option<String>,
    pub started_at: chrono::DateTime<chrono::Utc>,
    pub metadata: HashMap<String, serde_json::Value>,
}

impl Session {
    pub fn new() -> Self {
        Self {
            id: Uuid::new_v4(),
            user_id: None,
            started_at: chrono::Utc::now(),
            metadata: HashMap::new(),
        }
    }

    pub fn with_user_id(mut self, user_id: String) -> Self {
        self.user_id = Some(user_id);
        self
    }

    pub fn with_metadata(mut self, key: String, value: serde_json::Value) -> Self {
        self.metadata.insert(key, value);
        self
    }
}

impl Default for Session {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_session_creation() {
        let session = Session::new();
        assert!(!session.id.to_string().is_empty());
        assert!(session.user_id.is_none());
        assert!(session.metadata.is_empty());
    }

    #[test]
    fn test_session_with_user_id() {
        let session = Session::new().with_user_id("test_user".to_string());
        assert_eq!(session.user_id, Some("test_user".to_string()));
    }

    #[test]
    fn test_session_with_metadata() {
        let session = Session::new().with_metadata(
            "app_version".to_string(),
            serde_json::Value::String("1.0.0".to_string()),
        );
        assert_eq!(
            session.metadata.get("app_version"),
            Some(&serde_json::Value::String("1.0.0".to_string()))
        );
    }
}
