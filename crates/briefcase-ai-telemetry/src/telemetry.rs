use crate::{Event, Session};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryData {
    pub session: Session,
    pub events: Vec<Event>,
    pub metadata: HashMap<String, serde_json::Value>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub sdk_version: String,
    pub platform: String,
    pub environment: Option<String>,
    // New agent-focused fields to support the API schema
    #[serde(skip_serializing_if = "Option::is_none")]
    pub agent_id: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub latency: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cost: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub accuracy: Option<f64>,
}

impl TelemetryData {
    pub fn new(session: Session) -> Self {
        Self {
            session,
            events: Vec::new(),
            metadata: HashMap::new(),
            timestamp: chrono::Utc::now(),
            sdk_version: env!("CARGO_PKG_VERSION").to_string(),
            platform: std::env::consts::OS.to_string(),
            environment: std::env::var("ENVIRONMENT").ok(),
            agent_id: None,
            status: None,
            latency: None,
            cost: None,
            accuracy: None,
        }
    }

    pub fn with_agent_metrics(mut self, agent_id: u64, status: String) -> Self {
        // Validate status values according to API spec
        let valid_statuses = ["success", "failure", "partial"];
        let normalized_status = if valid_statuses.contains(&status.as_str()) {
            status
        } else {
            // Map common status values to valid ones
            match status.to_lowercase().as_str() {
                "ok" | "completed" | "done" => "success".to_string(),
                "error" | "failed" | "err" => "failure".to_string(),
                "warning" | "warn" | "incomplete" => "partial".to_string(),
                _ => "partial".to_string(), // Default fallback
            }
        };

        self.agent_id = Some(agent_id);
        self.status = Some(normalized_status);
        self
    }

    pub fn with_performance_metrics(
        mut self,
        latency: Option<f64>,
        cost: Option<f64>,
        accuracy: Option<f64>,
    ) -> Self {
        self.latency = latency;
        self.cost = cost;
        self.accuracy = accuracy;
        self
    }

    pub fn add_event(&mut self, event: Event) {
        self.events.push(event);
    }

    pub fn add_events(&mut self, events: Vec<Event>) {
        self.events.extend(events);
    }

    pub fn add_metadata(&mut self, key: String, value: serde_json::Value) {
        self.metadata.insert(key, value);
    }

    pub fn with_environment(mut self, environment: String) -> Self {
        self.environment = Some(environment);
        self
    }

    pub fn event_count(&self) -> usize {
        self.events.len()
    }

    pub fn clear_events(&mut self) {
        self.events.clear();
    }

    pub fn serialize_json(&self) -> anyhow::Result<String> {
        serde_json::to_string(self)
            .map_err(|e| anyhow::anyhow!("Failed to serialize telemetry data: {}", e))
    }

    pub fn serialize_json_pretty(&self) -> anyhow::Result<String> {
        serde_json::to_string_pretty(self)
            .map_err(|e| anyhow::anyhow!("Failed to serialize telemetry data: {}", e))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{EventBuilder, EventLevel};

    #[test]
    fn test_telemetry_data_creation() {
        let session = Session::new();
        let telemetry_data = TelemetryData::new(session);

        assert_eq!(telemetry_data.events.len(), 0);
        assert_eq!(telemetry_data.platform, std::env::consts::OS);
        assert_eq!(telemetry_data.sdk_version, env!("CARGO_PKG_VERSION"));
    }

    #[test]
    fn test_add_event() {
        let session = Session::new();
        let mut telemetry_data = TelemetryData::new(session);

        let event = EventBuilder::new("test_event".to_string())
            .level(EventLevel::Info)
            .build();

        telemetry_data.add_event(event);
        assert_eq!(telemetry_data.event_count(), 1);
    }

    #[test]
    fn test_add_metadata() {
        let session = Session::new();
        let mut telemetry_data = TelemetryData::new(session);

        telemetry_data.add_metadata(
            "app_name".to_string(),
            serde_json::Value::String("test_app".to_string()),
        );

        assert_eq!(
            telemetry_data.metadata.get("app_name"),
            Some(&serde_json::Value::String("test_app".to_string()))
        );
    }

    #[test]
    fn test_clear_events() {
        let session = Session::new();
        let mut telemetry_data = TelemetryData::new(session);

        let event = EventBuilder::new("test_event".to_string()).build();
        telemetry_data.add_event(event);

        assert_eq!(telemetry_data.event_count(), 1);

        telemetry_data.clear_events();
        assert_eq!(telemetry_data.event_count(), 0);
    }

    #[test]
    fn test_serialize_json() {
        let session = Session::new();
        let telemetry_data = TelemetryData::new(session);

        let json = telemetry_data.serialize_json();
        assert!(json.is_ok());

        let parsed: serde_json::Value = serde_json::from_str(&json.unwrap()).unwrap();
        assert!(parsed.get("session").is_some());
        assert!(parsed.get("events").is_some());
        assert!(parsed.get("timestamp").is_some());
    }
}
