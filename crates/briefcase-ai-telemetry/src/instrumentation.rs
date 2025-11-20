use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{Duration, Instant};
use uuid::Uuid;

use crate::{EventBuilder, EventLevel, TelemetryClient};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentMetrics {
    pub latency: Option<Duration>,
    pub cost: Option<f64>,
    pub accuracy: Option<f64>,
    pub input_data: Option<String>,
    pub output_data: Option<String>,
    pub error_message: Option<String>,
    pub tool_calls: Vec<ToolCall>,
    pub reasoning_path: Vec<ReasoningStep>,
    pub metadata: HashMap<String, serde_json::Value>,
    pub model_name: Option<String>,
    pub temperature: Option<f64>,
    pub status: ExecutionStatus,
    pub token_usage: Option<TokenUsage>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCall {
    pub tool_name: String,
    pub arguments: HashMap<String, serde_json::Value>,
    pub result: Option<serde_json::Value>,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReasoningStep {
    pub step: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenUsage {
    pub input_tokens: u64,
    pub output_tokens: u64,
    pub total_tokens: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExecutionStatus {
    Success,
    Failure,
    Partial,
}

#[derive(Debug, Clone)]
pub struct InstrumentationConfig {
    pub auto_submit: bool,
    pub consensus_mode: bool,
    pub consensus_runs: u32,
    pub consensus_threshold: f64,
    pub max_input_length: usize,
    pub max_output_length: usize,
    pub sanitization_enabled: bool,
}

impl Default for InstrumentationConfig {
    fn default() -> Self {
        Self {
            auto_submit: true,
            consensus_mode: false,
            consensus_runs: 3,
            consensus_threshold: 80.0,
            max_input_length: 10000,
            max_output_length: 10000,
            sanitization_enabled: true,
        }
    }
}

impl Default for AgentMetrics {
    fn default() -> Self {
        Self {
            latency: None,
            cost: None,
            accuracy: None,
            input_data: None,
            output_data: None,
            error_message: None,
            tool_calls: Vec::new(),
            reasoning_path: Vec::new(),
            metadata: HashMap::new(),
            model_name: None,
            temperature: None,
            status: ExecutionStatus::Success,
            token_usage: None,
        }
    }
}

pub struct InstrumentationSession {
    pub agent_id: u64,
    pub run_id: String,
    pub metrics: AgentMetrics,
    pub start_time: Option<Instant>,
    pub session_start: Option<chrono::DateTime<chrono::Utc>>,
    pub session_end: Option<chrono::DateTime<chrono::Utc>>,
    pub config: InstrumentationConfig,
    pub consensus_outputs: Vec<String>,
    pub client: Option<TelemetryClient>,
}

impl InstrumentationSession {
    pub fn new(agent_id: u64, config: InstrumentationConfig) -> Self {
        Self {
            agent_id,
            run_id: Uuid::new_v4().to_string(),
            metrics: AgentMetrics::default(),
            start_time: None,
            session_start: None,
            session_end: None,
            config,
            consensus_outputs: Vec::new(),
            client: None,
        }
    }

    pub fn with_client(mut self, client: TelemetryClient) -> Self {
        self.client = Some(client);
        self
    }

    pub fn start(&mut self) {
        self.start_time = Some(Instant::now());
        self.session_start = Some(chrono::Utc::now());
    }

    pub fn finish(&mut self) {
        if let Some(start_time) = self.start_time {
            self.metrics.latency = Some(start_time.elapsed());
        }
        self.session_end = Some(chrono::Utc::now());
    }

    pub fn set_accuracy(&mut self, accuracy: f64) {
        self.metrics.accuracy = Some(accuracy.clamp(0.0, 100.0));
    }

    pub fn set_cost(&mut self, cost: f64) {
        self.metrics.cost = Some(cost);
    }

    pub fn set_input(&mut self, input_data: String) {
        let truncated = if self.config.sanitization_enabled {
            truncate_and_sanitize(input_data, self.config.max_input_length)
        } else {
            truncate_string(input_data, self.config.max_input_length)
        };
        self.metrics.input_data = Some(truncated);
    }

    pub fn set_output(&mut self, output_data: String) {
        let truncated = if self.config.sanitization_enabled {
            truncate_and_sanitize(output_data, self.config.max_output_length)
        } else {
            truncate_string(output_data, self.config.max_output_length)
        };

        self.metrics.output_data = Some(truncated.clone());

        // Store for consensus mode
        if self.config.consensus_mode {
            self.consensus_outputs.push(truncated);
        }
    }

    pub fn set_error(&mut self, error_message: String) {
        self.metrics.status = ExecutionStatus::Failure;
        self.metrics.error_message = Some(error_message);
    }

    pub fn add_tool_call(
        &mut self,
        tool_name: String,
        arguments: HashMap<String, serde_json::Value>,
        result: Option<serde_json::Value>,
    ) {
        self.metrics.tool_calls.push(ToolCall {
            tool_name,
            arguments,
            result,
            timestamp: chrono::Utc::now(),
        });
    }

    pub fn add_reasoning_step(&mut self, step: String) {
        self.metrics.reasoning_path.push(ReasoningStep {
            step,
            timestamp: chrono::Utc::now(),
        });
    }

    pub fn set_metadata(&mut self, key: String, value: serde_json::Value) {
        self.metrics.metadata.insert(key, value);
    }

    pub fn set_model_info(&mut self, model_name: String, temperature: Option<f64>) {
        self.metrics.model_name = Some(model_name);
        self.metrics.temperature = temperature;
    }

    pub fn set_token_usage(&mut self, input_tokens: u64, output_tokens: u64) {
        self.metrics.token_usage = Some(TokenUsage {
            input_tokens,
            output_tokens,
            total_tokens: input_tokens + output_tokens,
        });
    }

    pub async fn submit_telemetry(&mut self) -> anyhow::Result<()> {
        // Handle consensus mode metadata before borrowing client
        if self.config.consensus_mode
            && self.consensus_outputs.len() >= self.config.consensus_runs as usize
        {
            let drift_metrics = crate::drift::calculate_drift_metrics(&self.consensus_outputs);
            self.set_metadata(
                "consensus_outputs".to_string(),
                serde_json::to_value(&self.consensus_outputs)?,
            );
            self.set_metadata(
                "drift_metrics".to_string(),
                serde_json::to_value(&drift_metrics)?,
            );
        }

        if let Some(ref client) = self.client {
            // Build event
            let mut event_builder = EventBuilder::new(format!("agent_execution_{}", self.run_id));
            event_builder = event_builder.level(match self.metrics.status {
                ExecutionStatus::Success => EventLevel::Info,
                ExecutionStatus::Failure => EventLevel::Error,
                ExecutionStatus::Partial => EventLevel::Warning,
            });

            if let Some(ref error_msg) = self.metrics.error_message {
                event_builder = event_builder.error(error_msg.clone());
            }

            if let Some(ref input_data) = self.metrics.input_data {
                let preview = if input_data.len() > 200 {
                    format!("{}...", &input_data[..200])
                } else {
                    input_data.clone()
                };
                event_builder = event_builder.message(format!("Input: {}", preview));
            }

            // Add all metrics as custom data
            for (key, value) in &self.metrics.metadata {
                event_builder = event_builder.custom_data(key.clone(), value.clone());
            }

            // Add core metrics
            event_builder = event_builder
                .custom_data("agent_id".to_string(), serde_json::to_value(self.agent_id)?);
            event_builder = event_builder
                .custom_data("run_id".to_string(), serde_json::to_value(&self.run_id)?);
            event_builder = event_builder.custom_data(
                "status".to_string(),
                serde_json::to_value(&self.metrics.status)?,
            );

            if let Some(accuracy) = self.metrics.accuracy {
                event_builder = event_builder
                    .custom_data("accuracy".to_string(), serde_json::to_value(accuracy)?);
            }

            if let Some(cost) = self.metrics.cost {
                event_builder =
                    event_builder.custom_data("cost".to_string(), serde_json::to_value(cost)?);
            }

            if let Some(ref model_name) = self.metrics.model_name {
                event_builder = event_builder
                    .custom_data("model_name".to_string(), serde_json::to_value(model_name)?);
            }

            if let Some(temperature) = self.metrics.temperature {
                event_builder = event_builder.custom_data(
                    "temperature".to_string(),
                    serde_json::to_value(temperature)?,
                );
            }

            if let Some(ref token_usage) = self.metrics.token_usage {
                event_builder = event_builder.custom_data(
                    "token_usage".to_string(),
                    serde_json::to_value(token_usage)?,
                );
            }

            if !self.metrics.tool_calls.is_empty() {
                event_builder = event_builder.custom_data(
                    "tool_calls".to_string(),
                    serde_json::to_value(&self.metrics.tool_calls)?,
                );
            }

            if !self.metrics.reasoning_path.is_empty() {
                event_builder = event_builder.custom_data(
                    "reasoning_path".to_string(),
                    serde_json::to_value(&self.metrics.reasoning_path)?,
                );
            }

            // Set duration if available
            if let Some(latency) = self.metrics.latency {
                event_builder = event_builder.duration(latency.as_millis() as u64);
            }

            let event = event_builder.build();
            client.track_event(event).await?;
        }

        Ok(())
    }

    pub async fn submit_agent_run(&mut self) -> anyhow::Result<()> {
        if let Some(ref client) = self.client {
            // Create agent run data structure
            let agent_run_data = serde_json::json!({
                "agent_id": self.agent_id,
                "run_id": self.run_id.to_string(),
                "session_start": self.session_start.map(|t| t.to_rfc3339()),
                "session_end": self.session_end.map(|t| t.to_rfc3339()),
                "status": match self.metrics.status {
                    ExecutionStatus::Success => "success",
                    ExecutionStatus::Failure => "failure",
                    ExecutionStatus::Partial => "partial"
                },
                "metrics": {
                    "latency_ms": self.metrics.latency.map(|d| d.as_millis()),
                    "cost": self.metrics.cost,
                    "accuracy": self.metrics.accuracy,
                    "token_usage": self.metrics.token_usage
                },
                "input_data": self.metrics.input_data,
                "output_data": self.metrics.output_data,
                "error_message": self.metrics.error_message,
                "tool_calls": self.metrics.tool_calls,
                "reasoning_path": self.metrics.reasoning_path,
                "model_name": self.metrics.model_name,
                "temperature": self.metrics.temperature,
                "metadata": self.metrics.metadata
            });

            client.record_agent_run(&agent_run_data).await?;
        }

        Ok(())
    }
}

pub struct AgentInstrument {
    session: InstrumentationSession,
}

impl AgentInstrument {
    pub fn new(agent_id: u64, client: TelemetryClient, config: InstrumentationConfig) -> Self {
        let session = InstrumentationSession::new(agent_id, config).with_client(client);
        Self { session }
    }

    pub fn start(&mut self) {
        self.session.start();
    }

    pub fn finish(mut self) -> InstrumentationSession {
        self.session.finish();
        self.session
    }

    pub fn set_accuracy(&mut self, accuracy: f64) {
        self.session.set_accuracy(accuracy);
    }

    pub fn set_cost(&mut self, cost: f64) {
        self.session.set_cost(cost);
    }

    pub fn set_input(&mut self, input_data: String) {
        self.session.set_input(input_data);
    }

    pub fn set_output(&mut self, output_data: String) {
        self.session.set_output(output_data);
    }

    pub fn set_error(&mut self, error_message: String) {
        self.session.set_error(error_message);
    }

    pub fn add_tool_call(
        &mut self,
        tool_name: String,
        arguments: HashMap<String, serde_json::Value>,
        result: Option<serde_json::Value>,
    ) {
        self.session.add_tool_call(tool_name, arguments, result);
    }

    pub fn add_reasoning_step(&mut self, step: String) {
        self.session.add_reasoning_step(step);
    }

    pub fn set_metadata(&mut self, key: String, value: serde_json::Value) {
        self.session.set_metadata(key, value);
    }

    pub fn set_model_info(&mut self, model_name: String, temperature: Option<f64>) {
        self.session.set_model_info(model_name, temperature);
    }

    pub fn set_token_usage(&mut self, input_tokens: u64, output_tokens: u64) {
        self.session.set_token_usage(input_tokens, output_tokens);
    }

    pub async fn submit_telemetry(mut self) -> anyhow::Result<()> {
        self.session.submit_telemetry().await
    }

    pub async fn submit_agent_run(mut self) -> anyhow::Result<()> {
        self.session.submit_agent_run().await
    }

    pub async fn submit_all(mut self) -> anyhow::Result<()> {
        // Submit both telemetry events and agent run data
        self.session.submit_telemetry().await?;
        self.session.submit_agent_run().await?;
        Ok(())
    }
}

// Helper functions for text processing
fn truncate_string(text: String, max_length: usize) -> String {
    if text.len() <= max_length {
        text
    } else {
        format!("{}...", &text[..max_length.saturating_sub(3)])
    }
}

fn truncate_and_sanitize(text: String, max_length: usize) -> String {
    let sanitized = sanitize_sensitive_data(text);
    truncate_string(sanitized, max_length)
}

fn sanitize_sensitive_data(text: String) -> String {
    use regex::Regex;

    let mut sanitized = text;

    // Common PII patterns
    let patterns = vec![
        (
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "[EMAIL]",
        ),
        (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),
        (
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "[CREDIT_CARD]",
        ),
        (r"sk-[A-Za-z0-9]{48}", "[API_KEY]"),
        (r"Bearer [A-Za-z0-9._-]+", "Bearer [TOKEN]"),
        (
            r"\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "[PHONE]",
        ),
    ];

    for (pattern, replacement) in patterns {
        if let Ok(re) = Regex::new(pattern) {
            sanitized = re.replace_all(&sanitized, replacement).to_string();
        }
    }

    sanitized
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::client::TelemetryClient;
    use crate::config::TelemetryConfig;
    use std::thread::sleep;
    use std::time::Duration;

    #[test]
    fn test_agent_metrics_default() {
        let metrics = AgentMetrics::default();
        assert!(metrics.latency.is_none());
        assert!(metrics.cost.is_none());
        assert!(metrics.accuracy.is_none());
        assert!(matches!(metrics.status, ExecutionStatus::Success));
        assert!(metrics.tool_calls.is_empty());
        assert!(metrics.reasoning_path.is_empty());
        assert!(metrics.metadata.is_empty());
    }

    #[test]
    fn test_token_usage() {
        let usage = TokenUsage {
            input_tokens: 100,
            output_tokens: 50,
            total_tokens: 150,
        };

        assert_eq!(usage.input_tokens, 100);
        assert_eq!(usage.output_tokens, 50);
        assert_eq!(usage.total_tokens, 150);
    }

    #[test]
    fn test_tool_call_creation() {
        let mut args = HashMap::new();
        args.insert(
            "param1".to_string(),
            serde_json::Value::String("value1".to_string()),
        );

        let tool_call = ToolCall {
            tool_name: "test_tool".to_string(),
            arguments: args.clone(),
            result: Some(serde_json::Value::String("success".to_string())),
            timestamp: chrono::Utc::now(),
        };

        assert_eq!(tool_call.tool_name, "test_tool");
        assert_eq!(tool_call.arguments.len(), 1);
        assert!(tool_call.result.is_some());
    }

    #[test]
    fn test_reasoning_step() {
        let step = ReasoningStep {
            step: "Analyzing input data".to_string(),
            timestamp: chrono::Utc::now(),
        };

        assert_eq!(step.step, "Analyzing input data");
    }

    #[test]
    fn test_instrumentation_config_default() {
        let config = InstrumentationConfig::default();
        assert!(config.auto_submit);
        assert!(!config.consensus_mode);
        assert_eq!(config.consensus_runs, 3);
        assert_eq!(config.consensus_threshold, 80.0);
        assert_eq!(config.max_input_length, 10000);
        assert_eq!(config.max_output_length, 10000);
        assert!(config.sanitization_enabled);
    }

    #[test]
    fn test_instrumentation_session_creation() {
        let config = InstrumentationConfig::default();
        let session = InstrumentationSession::new(12345, config);

        assert_eq!(session.agent_id, 12345);
        assert!(!session.run_id.is_empty());
        assert!(session.start_time.is_none());
        assert!(session.consensus_outputs.is_empty());
        assert!(session.client.is_none());
    }

    #[test]
    fn test_instrumentation_session_timing() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        // Test starting
        session.start();
        assert!(session.start_time.is_some());

        // Sleep a bit to ensure some time passes
        sleep(Duration::from_millis(10));

        // Test finishing
        session.finish();
        assert!(session.metrics.latency.is_some());
        assert!(session.metrics.latency.unwrap().as_millis() >= 10);
    }

    #[test]
    fn test_set_accuracy() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        session.set_accuracy(85.5);
        assert_eq!(session.metrics.accuracy, Some(85.5));

        // Test clamping
        session.set_accuracy(-5.0);
        assert_eq!(session.metrics.accuracy, Some(0.0));

        session.set_accuracy(105.0);
        assert_eq!(session.metrics.accuracy, Some(100.0));
    }

    #[test]
    fn test_set_cost() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        session.set_cost(0.05);
        assert_eq!(session.metrics.cost, Some(0.05));
    }

    #[test]
    fn test_set_input_output() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        session.set_input("Test input data".to_string());
        assert_eq!(
            session.metrics.input_data,
            Some("Test input data".to_string())
        );

        session.set_output("Test output data".to_string());
        assert_eq!(
            session.metrics.output_data,
            Some("Test output data".to_string())
        );
    }

    #[test]
    fn test_set_error() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        session.set_error("Test error message".to_string());
        assert_eq!(
            session.metrics.error_message,
            Some("Test error message".to_string())
        );
        assert!(matches!(session.metrics.status, ExecutionStatus::Failure));
    }

    #[test]
    fn test_add_tool_call() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        let mut args = HashMap::new();
        args.insert(
            "param1".to_string(),
            serde_json::Value::String("value1".to_string()),
        );

        session.add_tool_call(
            "test_tool".to_string(),
            args,
            Some(serde_json::Value::String("result".to_string())),
        );

        assert_eq!(session.metrics.tool_calls.len(), 1);
        assert_eq!(session.metrics.tool_calls[0].tool_name, "test_tool");
        assert!(session.metrics.tool_calls[0].result.is_some());
    }

    #[test]
    fn test_add_reasoning_step() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        session.add_reasoning_step("Step 1: Analyze input".to_string());
        session.add_reasoning_step("Step 2: Generate output".to_string());

        assert_eq!(session.metrics.reasoning_path.len(), 2);
        assert_eq!(
            session.metrics.reasoning_path[0].step,
            "Step 1: Analyze input"
        );
        assert_eq!(
            session.metrics.reasoning_path[1].step,
            "Step 2: Generate output"
        );
    }

    #[test]
    fn test_set_metadata() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        session.set_metadata(
            "key1".to_string(),
            serde_json::Value::String("value1".to_string()),
        );
        session.set_metadata(
            "key2".to_string(),
            serde_json::Value::Number(serde_json::Number::from(42)),
        );

        assert_eq!(session.metrics.metadata.len(), 2);
        assert_eq!(
            session.metrics.metadata["key1"],
            serde_json::Value::String("value1".to_string())
        );
        assert_eq!(
            session.metrics.metadata["key2"],
            serde_json::Value::Number(serde_json::Number::from(42))
        );
    }

    #[test]
    fn test_set_model_info() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        session.set_model_info("gpt-4".to_string(), Some(0.7));
        assert_eq!(session.metrics.model_name, Some("gpt-4".to_string()));
        assert_eq!(session.metrics.temperature, Some(0.7));
    }

    #[test]
    fn test_set_token_usage() {
        let config = InstrumentationConfig::default();
        let mut session = InstrumentationSession::new(123, config);

        session.set_token_usage(150, 75);
        let usage = session.metrics.token_usage.unwrap();
        assert_eq!(usage.input_tokens, 150);
        assert_eq!(usage.output_tokens, 75);
        assert_eq!(usage.total_tokens, 225);
    }

    #[test]
    fn test_truncate_string() {
        assert_eq!(truncate_string("hello".to_string(), 10), "hello");
        assert_eq!(truncate_string("hello world".to_string(), 8), "hello...");
        assert_eq!(truncate_string("hi".to_string(), 5), "hi");
    }

    #[test]
    fn test_sanitize_sensitive_data() {
        let input = "My email is john@example.com and my SSN is 123-45-6789".to_string();
        let sanitized = sanitize_sensitive_data(input);
        assert!(sanitized.contains("[EMAIL]"));
        assert!(sanitized.contains("[SSN]"));
        assert!(!sanitized.contains("john@example.com"));
        assert!(!sanitized.contains("123-45-6789"));
    }

    #[test]
    fn test_sanitize_api_key() {
        let input = "API key: sk-abcdefghijklmnopqrstuvwxyz1234567890123456789012".to_string();
        let sanitized = sanitize_sensitive_data(input);
        assert!(sanitized.contains("[API_KEY]"));
        assert!(!sanitized.contains("sk-abcdefghijklmnopqrstuvwxyz"));
    }

    #[test]
    fn test_sanitize_phone_number() {
        let input = "Call me at (555) 123-4567 or +1-555-123-4567".to_string();
        let sanitized = sanitize_sensitive_data(input);
        assert!(sanitized.contains("[PHONE]"));
        assert!(!sanitized.contains("555-123-4567"));
    }

    #[test]
    fn test_sanitize_credit_card() {
        let input = "My card is 1234 5678 9012 3456".to_string();
        let sanitized = sanitize_sensitive_data(input);
        assert!(sanitized.contains("[CREDIT_CARD]"));
        assert!(!sanitized.contains("1234 5678 9012 3456"));
    }

    #[test]
    fn test_consensus_mode() {
        let mut config = InstrumentationConfig::default();
        config.consensus_mode = true;
        config.consensus_runs = 2;

        let mut session = InstrumentationSession::new(123, config);

        session.set_output("Output 1".to_string());
        session.set_output("Output 2".to_string());

        assert_eq!(session.consensus_outputs.len(), 2);
        assert_eq!(session.consensus_outputs[0], "Output 1");
        assert_eq!(session.consensus_outputs[1], "Output 2");
    }

    #[test]
    fn test_input_output_truncation() {
        let mut config = InstrumentationConfig::default();
        config.max_input_length = 10;
        config.max_output_length = 8;
        config.sanitization_enabled = false;

        let mut session = InstrumentationSession::new(123, config);

        session.set_input("This is a very long input string that should be truncated".to_string());
        session.set_output("This is a long output".to_string());

        let input_data = session.metrics.input_data.unwrap();
        let output_data = session.metrics.output_data.unwrap();
        assert_eq!(input_data.len(), 10); // "This is..."
        assert_eq!(output_data.len(), 8); // "This ..."
        assert!(input_data.ends_with("..."));
        assert!(output_data.ends_with("..."));
    }

    #[test]
    fn test_agent_instrument_wrapper() {
        let config = TelemetryConfig::new("test-key".to_string()).with_enabled(false);
        let client = TelemetryClient::new(config).unwrap();
        let instrumentation_config = InstrumentationConfig::default();

        let mut instrument = AgentInstrument::new(123, client, instrumentation_config);

        instrument.start();
        instrument.set_accuracy(95.0);
        instrument.set_cost(0.02);
        instrument.add_reasoning_step("Testing step".to_string());

        let session = instrument.finish();
        assert_eq!(session.agent_id, 123);
        assert_eq!(session.metrics.accuracy, Some(95.0));
        assert_eq!(session.metrics.cost, Some(0.02));
        assert!(!session.metrics.reasoning_path.is_empty());
        assert!(session.metrics.latency.is_some());
    }
}
