use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum EventLevel {
    Debug,
    Info,
    Warning,
    Error,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventMetadata {
    pub user_id: Option<String>,
    pub session_id: Option<Uuid>,
    pub trace_id: Option<String>,
    pub span_id: Option<String>,
    pub tags: HashMap<String, String>,
    pub custom_data: HashMap<String, serde_json::Value>,
}

impl EventMetadata {
    pub fn new() -> Self {
        Self {
            user_id: None,
            session_id: None,
            trace_id: None,
            span_id: None,
            tags: HashMap::new(),
            custom_data: HashMap::new(),
        }
    }

    pub fn with_user_id(mut self, user_id: String) -> Self {
        self.user_id = Some(user_id);
        self
    }

    pub fn with_session_id(mut self, session_id: Uuid) -> Self {
        self.session_id = Some(session_id);
        self
    }

    pub fn with_trace_id(mut self, trace_id: String) -> Self {
        self.trace_id = Some(trace_id);
        self
    }

    pub fn with_tag(mut self, key: String, value: String) -> Self {
        self.tags.insert(key, value);
        self
    }

    pub fn with_custom_data(mut self, key: String, value: serde_json::Value) -> Self {
        self.custom_data.insert(key, value);
        self
    }
}

impl Default for EventMetadata {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub id: Uuid,
    pub name: String,
    pub level: EventLevel,
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub message: Option<String>,
    pub metadata: EventMetadata,
    pub duration_ms: Option<u64>,
    pub error: Option<String>,
}

impl Event {
    pub fn new(name: String, level: EventLevel) -> Self {
        Self {
            id: Uuid::new_v4(),
            name,
            level,
            timestamp: chrono::Utc::now(),
            message: None,
            metadata: EventMetadata::new(),
            duration_ms: None,
            error: None,
        }
    }

    pub fn with_message(mut self, message: String) -> Self {
        self.message = Some(message);
        self
    }

    pub fn with_metadata(mut self, metadata: EventMetadata) -> Self {
        self.metadata = metadata;
        self
    }

    pub fn with_duration(mut self, duration_ms: u64) -> Self {
        self.duration_ms = Some(duration_ms);
        self
    }

    pub fn with_error(mut self, error: String) -> Self {
        self.error = Some(error);
        self
    }
}

pub struct EventBuilder {
    name: String,
    level: EventLevel,
    message: Option<String>,
    metadata: EventMetadata,
    duration_ms: Option<u64>,
    error: Option<String>,
}

impl EventBuilder {
    pub fn new(name: String) -> Self {
        Self {
            name,
            level: EventLevel::Info,
            message: None,
            metadata: EventMetadata::new(),
            duration_ms: None,
            error: None,
        }
    }

    pub fn level(mut self, level: EventLevel) -> Self {
        self.level = level;
        self
    }

    pub fn message(mut self, message: String) -> Self {
        self.message = Some(message);
        self
    }

    pub fn metadata(mut self, metadata: EventMetadata) -> Self {
        self.metadata = metadata;
        self
    }

    pub fn user_id(mut self, user_id: String) -> Self {
        self.metadata.user_id = Some(user_id);
        self
    }

    pub fn session_id(mut self, session_id: Uuid) -> Self {
        self.metadata.session_id = Some(session_id);
        self
    }

    pub fn tag(mut self, key: String, value: String) -> Self {
        self.metadata.tags.insert(key, value);
        self
    }

    pub fn custom_data(mut self, key: String, value: serde_json::Value) -> Self {
        self.metadata.custom_data.insert(key, value);
        self
    }

    pub fn duration(mut self, duration_ms: u64) -> Self {
        self.duration_ms = Some(duration_ms);
        self
    }

    pub fn error(mut self, error: String) -> Self {
        self.error = Some(error);
        self.level = EventLevel::Error;
        self
    }

    pub fn build(self) -> Event {
        Event {
            id: Uuid::new_v4(),
            name: self.name,
            level: self.level,
            timestamp: chrono::Utc::now(),
            message: self.message,
            metadata: self.metadata,
            duration_ms: self.duration_ms,
            error: self.error,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_event_creation() {
        let event = Event::new("test_event".to_string(), EventLevel::Info);
        assert_eq!(event.name, "test_event");
        assert_eq!(event.level, EventLevel::Info);
        assert!(event.message.is_none());
    }

    #[test]
    fn test_event_builder() {
        let event = EventBuilder::new("test_event".to_string())
            .level(EventLevel::Warning)
            .message("Test message".to_string())
            .user_id("test_user".to_string())
            .tag("component".to_string(), "auth".to_string())
            .build();

        assert_eq!(event.name, "test_event");
        assert_eq!(event.level, EventLevel::Warning);
        assert_eq!(event.message, Some("Test message".to_string()));
        assert_eq!(event.metadata.user_id, Some("test_user".to_string()));
        assert_eq!(
            event.metadata.tags.get("component"),
            Some(&"auth".to_string())
        );
    }

    #[test]
    fn test_event_with_error() {
        let event = EventBuilder::new("error_event".to_string())
            .error("Something went wrong".to_string())
            .build();

        assert_eq!(event.level, EventLevel::Error);
        assert_eq!(event.error, Some("Something went wrong".to_string()));
    }
}
