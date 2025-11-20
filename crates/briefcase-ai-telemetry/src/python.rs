#![allow(clippy::useless_conversion)]

#[cfg(feature = "python")]
use pyo3::prelude::*;
use std::time::Duration;

use crate::{
    compliance::{
        ComplianceConfig, ComplianceManager, ComplianceReport, ComplianceStatus, DataCategory,
    },
    cost::{
        count_tokens_approximate, estimate_cost, format_cost, format_tokens, CostCalculator,
        CostEstimate,
    },
    drift::{
        calculate_drift_metrics, calculate_enhanced_drift_metrics, ComplianceFramework,
        ConfidenceInterval, DriftCalculator, DriftMetrics, DriftSeverity, EnhancedDriftMetrics,
        StatisticalDrift, StructuralDrift, TemporalDrift, TrendDirection,
    },
    instrumentation::{AgentInstrument, InstrumentationConfig},
    Event, EventBuilder, EventLevel, EventMetadata, Session, TelemetryClient, TelemetryConfig,
};

#[pyclass]
#[derive(Clone)]
pub struct PyTelemetryConfig {
    inner: TelemetryConfig,
}

#[pymethods]
impl PyTelemetryConfig {
    #[new]
    fn new(api_key: String) -> Self {
        Self {
            inner: TelemetryConfig::new(api_key),
        }
    }

    fn with_endpoint(&mut self, endpoint: String) {
        self.inner = self.inner.clone().with_endpoint(endpoint);
    }

    fn with_timeout_seconds(&mut self, timeout_seconds: u64) {
        self.inner = self
            .inner
            .clone()
            .with_timeout(Duration::from_secs(timeout_seconds));
    }

    fn with_retry_attempts(&mut self, retry_attempts: u32) {
        self.inner = self.inner.clone().with_retry_attempts(retry_attempts);
    }

    fn with_batch_size(&mut self, batch_size: usize) {
        self.inner = self.inner.clone().with_batch_size(batch_size);
    }

    fn with_flush_interval_seconds(&mut self, flush_interval_seconds: u64) {
        self.inner = self
            .inner
            .clone()
            .with_flush_interval(Duration::from_secs(flush_interval_seconds));
    }

    fn with_enabled(&mut self, enabled: bool) {
        self.inner = self.inner.clone().with_enabled(enabled);
    }

    #[getter]
    fn api_key(&self) -> String {
        self.inner.api_key.clone()
    }

    #[getter]
    fn endpoint(&self) -> String {
        self.inner.endpoint.clone()
    }

    #[getter]
    fn enabled(&self) -> bool {
        self.inner.enabled
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyEventLevel {
    inner: EventLevel,
}

#[pymethods]
impl PyEventLevel {
    #[new]
    fn new() -> Self {
        Self {
            inner: EventLevel::Info,
        }
    }

    #[staticmethod]
    fn debug() -> Self {
        Self {
            inner: EventLevel::Debug,
        }
    }

    #[staticmethod]
    fn info() -> Self {
        Self {
            inner: EventLevel::Info,
        }
    }

    #[staticmethod]
    fn warning() -> Self {
        Self {
            inner: EventLevel::Warning,
        }
    }

    #[staticmethod]
    fn error() -> Self {
        Self {
            inner: EventLevel::Error,
        }
    }

    #[staticmethod]
    fn critical() -> Self {
        Self {
            inner: EventLevel::Critical,
        }
    }

    fn __str__(&self) -> String {
        match self.inner {
            EventLevel::Debug => "Debug".to_string(),
            EventLevel::Info => "Info".to_string(),
            EventLevel::Warning => "Warning".to_string(),
            EventLevel::Error => "Error".to_string(),
            EventLevel::Critical => "Critical".to_string(),
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyEventMetadata {
    inner: EventMetadata,
}

#[pymethods]
impl PyEventMetadata {
    #[new]
    fn new() -> Self {
        Self {
            inner: EventMetadata::new(),
        }
    }

    fn with_user_id(&mut self, user_id: String) {
        self.inner = self.inner.clone().with_user_id(user_id);
    }

    fn with_trace_id(&mut self, trace_id: String) {
        self.inner = self.inner.clone().with_trace_id(trace_id);
    }

    fn add_tag(&mut self, key: String, value: String) {
        self.inner = self.inner.clone().with_tag(key, value);
    }

    fn add_custom_data(&mut self, key: String, value: String) {
        let json_value = serde_json::Value::String(value);
        self.inner = self.inner.clone().with_custom_data(key, json_value);
    }

    #[getter]
    fn user_id(&self) -> Option<String> {
        self.inner.user_id.clone()
    }

    #[getter]
    fn trace_id(&self) -> Option<String> {
        self.inner.trace_id.clone()
    }
}

#[pyclass]
pub struct PyEventBuilder {
    inner: EventBuilder,
}

#[pymethods]
impl PyEventBuilder {
    #[new]
    fn new(name: String) -> Self {
        Self {
            inner: EventBuilder::new(name),
        }
    }

    fn level(&mut self, level: PyEventLevel) {
        self.inner = std::mem::replace(&mut self.inner, EventBuilder::new("temp".to_string()))
            .level(level.inner);
    }

    fn message(&mut self, message: String) {
        self.inner = std::mem::replace(&mut self.inner, EventBuilder::new("temp".to_string()))
            .message(message);
    }

    fn user_id(&mut self, user_id: String) {
        self.inner = std::mem::replace(&mut self.inner, EventBuilder::new("temp".to_string()))
            .user_id(user_id);
    }

    fn tag(&mut self, key: String, value: String) {
        self.inner = std::mem::replace(&mut self.inner, EventBuilder::new("temp".to_string()))
            .tag(key, value);
    }

    fn custom_data(&mut self, key: String, value: String) {
        let json_value = serde_json::Value::String(value);
        self.inner = std::mem::replace(&mut self.inner, EventBuilder::new("temp".to_string()))
            .custom_data(key, json_value);
    }

    fn duration_ms(&mut self, duration_ms: u64) {
        self.inner = std::mem::replace(&mut self.inner, EventBuilder::new("temp".to_string()))
            .duration(duration_ms);
    }

    fn error(&mut self, error: String) {
        self.inner =
            std::mem::replace(&mut self.inner, EventBuilder::new("temp".to_string())).error(error);
    }

    fn build(&mut self) -> PyEvent {
        let builder = std::mem::replace(&mut self.inner, EventBuilder::new("temp".to_string()));
        PyEvent {
            inner: builder.build(),
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyEvent {
    inner: Event,
}

#[pymethods]
impl PyEvent {
    #[getter]
    fn id(&self) -> String {
        self.inner.id.to_string()
    }

    #[getter]
    fn name(&self) -> String {
        self.inner.name.clone()
    }

    #[getter]
    fn level(&self) -> PyEventLevel {
        PyEventLevel {
            inner: self.inner.level.clone(),
        }
    }

    #[getter]
    fn timestamp(&self) -> String {
        self.inner.timestamp.to_rfc3339()
    }

    #[getter]
    fn message(&self) -> Option<String> {
        self.inner.message.clone()
    }

    #[getter]
    fn duration_ms(&self) -> Option<u64> {
        self.inner.duration_ms
    }

    #[getter]
    fn error(&self) -> Option<String> {
        self.inner.error.clone()
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PySession {
    inner: Session,
}

#[pymethods]
impl PySession {
    #[new]
    fn new() -> Self {
        Self {
            inner: Session::new(),
        }
    }

    fn with_user_id(&mut self, user_id: String) {
        self.inner = self.inner.clone().with_user_id(user_id);
    }

    fn add_metadata(&mut self, key: String, value: String) {
        let json_value = serde_json::Value::String(value);
        self.inner = self.inner.clone().with_metadata(key, json_value);
    }

    #[getter]
    fn id(&self) -> String {
        self.inner.id.to_string()
    }

    #[getter]
    fn user_id(&self) -> Option<String> {
        self.inner.user_id.clone()
    }

    #[getter]
    fn started_at(&self) -> String {
        self.inner.started_at.to_rfc3339()
    }
}

#[pyclass]
pub struct PyTelemetryClient {
    inner: Option<TelemetryClient>,
    rt: tokio::runtime::Runtime,
}

#[pymethods]
impl PyTelemetryClient {
    #[new]
    fn new(config: PyTelemetryConfig) -> PyResult<Self> {
        let rt = tokio::runtime::Runtime::new().map_err(|e| {
            pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to create runtime: {}",
                e
            ))
        })?;

        let client = rt.block_on(async {
            TelemetryClient::new(config.inner).map_err(|e| {
                pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to create client: {}",
                    e
                ))
            })
        })?;

        Ok(Self {
            inner: Some(client),
            rt,
        })
    }

    fn with_session(&mut self, session: PySession) {
        if let Some(ref mut client) = self.inner {
            *client = client.clone().with_session(session.inner);
        }
    }

    fn track_event(&self, event: PyEvent) -> PyResult<()> {
        if let Some(ref client) = self.inner {
            self.rt.block_on(async {
                client.track_event(event.inner).await.map_err(|e| {
                    pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                        "Failed to track event: {}",
                        e
                    ))
                })
            })
        } else {
            Ok(())
        }
    }

    fn flush(&self) -> PyResult<()> {
        if let Some(ref client) = self.inner {
            self.rt.block_on(async {
                client.flush().await.map_err(|e| {
                    pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                        "Failed to flush: {}",
                        e
                    ))
                })
            })
        } else {
            Ok(())
        }
    }

    fn start_background_flush(&self) -> PyResult<()> {
        if let Some(ref client) = self.inner {
            self.rt.block_on(async {
                client.start_background_flush().await.map_err(|e| {
                    pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                        "Failed to start background flush: {}",
                        e
                    ))
                })
            })
        } else {
            Ok(())
        }
    }

    fn buffer_size(&self) -> usize {
        if let Some(ref client) = self.inner {
            self.rt.block_on(async { client.buffer_size().await })
        } else {
            0
        }
    }

    fn session(&self) -> PyResult<PySession> {
        if let Some(ref client) = self.inner {
            Ok(PySession {
                inner: client.session().clone(),
            })
        } else {
            Err(pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Client not initialized",
            ))
        }
    }

    fn record_agent_run(
        &self,
        agent_run_data: std::collections::HashMap<String, pyo3::PyObject>,
    ) -> PyResult<()> {
        if let Some(ref client) = self.inner {
            // Convert HashMap to serde_json::Value
            let mut json_map = serde_json::Map::new();

            pyo3::Python::with_gil(|py| -> PyResult<()> {
                for (key, value) in agent_run_data {
                    let val: serde_json::Value = if let Ok(s) = value.extract::<String>(py) {
                        serde_json::Value::String(s)
                    } else if let Ok(i) = value.extract::<i64>(py) {
                        serde_json::Value::Number(serde_json::Number::from(i))
                    } else if let Ok(f) = value.extract::<f64>(py) {
                        if let Some(n) = serde_json::Number::from_f64(f) {
                            serde_json::Value::Number(n)
                        } else {
                            serde_json::Value::Null
                        }
                    } else if let Ok(b) = value.extract::<bool>(py) {
                        serde_json::Value::Bool(b)
                    } else {
                        // Fallback: convert to string
                        let s = value.to_string();
                        serde_json::Value::String(s)
                    };
                    json_map.insert(key, val);
                }
                Ok(())
            })?;

            let json_data = serde_json::Value::Object(json_map);

            self.rt.block_on(async {
                client.record_agent_run(&json_data).await.map_err(|e| {
                    pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                        "Failed to record agent run: {}",
                        e
                    ))
                })
            })
        } else {
            Ok(())
        }
    }

    fn send_batch(
        &self,
        records: Vec<std::collections::HashMap<String, pyo3::PyObject>>,
    ) -> PyResult<()> {
        if let Some(ref client) = self.inner {
            let mut json_records = Vec::new();

            pyo3::Python::with_gil(|py| -> PyResult<()> {
                for record in records {
                    let mut json_map = serde_json::Map::new();

                    for (key, value) in record {
                        let val: serde_json::Value = if let Ok(s) = value.extract::<String>(py) {
                            serde_json::Value::String(s)
                        } else if let Ok(i) = value.extract::<i64>(py) {
                            serde_json::Value::Number(serde_json::Number::from(i))
                        } else if let Ok(f) = value.extract::<f64>(py) {
                            if let Some(n) = serde_json::Number::from_f64(f) {
                                serde_json::Value::Number(n)
                            } else {
                                serde_json::Value::Null
                            }
                        } else if let Ok(b) = value.extract::<bool>(py) {
                            serde_json::Value::Bool(b)
                        } else {
                            let s = value.to_string();
                            serde_json::Value::String(s)
                        };
                        json_map.insert(key, val);
                    }

                    json_records.push(serde_json::Value::Object(json_map));
                }
                Ok(())
            })?;

            self.rt.block_on(async {
                client.send_batch(json_records).await.map_err(|e| {
                    pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                        "Failed to send batch: {}",
                        e
                    ))
                })
            })
        } else {
            Ok(())
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyInstrumentationConfig {
    inner: InstrumentationConfig,
}

#[pymethods]
impl PyInstrumentationConfig {
    #[new]
    fn new() -> Self {
        Self {
            inner: InstrumentationConfig::default(),
        }
    }

    fn with_auto_submit(&mut self, auto_submit: bool) {
        self.inner.auto_submit = auto_submit;
    }

    #[pyo3(signature = (enabled, runs=None, threshold=None))]
    fn with_consensus_mode(&mut self, enabled: bool, runs: Option<u32>, threshold: Option<f64>) {
        self.inner.consensus_mode = enabled;
        if let Some(runs) = runs {
            self.inner.consensus_runs = runs;
        }
        if let Some(threshold) = threshold {
            self.inner.consensus_threshold = threshold;
        }
    }

    #[pyo3(signature = (input=None, output=None))]
    fn with_max_lengths(&mut self, input: Option<usize>, output: Option<usize>) {
        if let Some(input) = input {
            self.inner.max_input_length = input;
        }
        if let Some(output) = output {
            self.inner.max_output_length = output;
        }
    }

    #[getter]
    fn auto_submit(&self) -> bool {
        self.inner.auto_submit
    }

    #[getter]
    fn consensus_mode(&self) -> bool {
        self.inner.consensus_mode
    }
}

#[pyclass]
pub struct PyAgentInstrument {
    inner: Option<AgentInstrument>,
}

#[pymethods]
impl PyAgentInstrument {
    #[new]
    #[pyo3(signature = (agent_id, client, config=None))]
    fn new(
        agent_id: u64,
        client: &PyTelemetryClient,
        config: Option<PyInstrumentationConfig>,
    ) -> PyResult<Self> {
        let config = config.map(|c| c.inner).unwrap_or_default();
        let client_inner = client.inner.as_ref().ok_or_else(|| {
            pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Client not initialized")
        })?;

        let instrument = AgentInstrument::new(agent_id, client_inner.clone(), config);
        Ok(Self {
            inner: Some(instrument),
        })
    }

    fn start(&mut self) {
        if let Some(ref mut instrument) = self.inner {
            instrument.start();
        }
    }

    fn set_accuracy(&mut self, accuracy: f64) {
        if let Some(ref mut instrument) = self.inner {
            instrument.set_accuracy(accuracy);
        }
    }

    fn set_cost(&mut self, cost: f64) {
        if let Some(ref mut instrument) = self.inner {
            instrument.set_cost(cost);
        }
    }

    fn set_input(&mut self, input_data: String) {
        if let Some(ref mut instrument) = self.inner {
            instrument.set_input(input_data);
        }
    }

    fn set_output(&mut self, output_data: String) {
        if let Some(ref mut instrument) = self.inner {
            instrument.set_output(output_data);
        }
    }

    fn set_error(&mut self, error_message: String) {
        if let Some(ref mut instrument) = self.inner {
            instrument.set_error(error_message);
        }
    }

    #[pyo3(signature = (tool_name, arguments, result=None))]
    fn add_tool_call(&mut self, tool_name: String, arguments: String, result: Option<String>) {
        if let Some(ref mut instrument) = self.inner {
            use std::collections::HashMap;

            let args: HashMap<String, serde_json::Value> = serde_json::from_str(&arguments)
                .unwrap_or_else(|_| {
                    let mut map = HashMap::new();
                    map.insert("raw".to_string(), serde_json::Value::String(arguments));
                    map
                });

            let result_json = result.map(serde_json::Value::String);
            instrument.add_tool_call(tool_name, args, result_json);
        }
    }

    fn add_reasoning_step(&mut self, step: String) {
        if let Some(ref mut instrument) = self.inner {
            instrument.add_reasoning_step(step);
        }
    }

    fn set_metadata(&mut self, key: String, value: String) {
        if let Some(ref mut instrument) = self.inner {
            let json_value = serde_json::Value::String(value);
            instrument.set_metadata(key, json_value);
        }
    }

    #[pyo3(signature = (model_name, temperature=None))]
    fn set_model_info(&mut self, model_name: String, temperature: Option<f64>) {
        if let Some(ref mut instrument) = self.inner {
            instrument.set_model_info(model_name, temperature);
        }
    }

    fn set_token_usage(&mut self, input_tokens: u64, output_tokens: u64) {
        if let Some(ref mut instrument) = self.inner {
            instrument.set_token_usage(input_tokens, output_tokens);
        }
    }

    fn submit_telemetry(&mut self) -> PyResult<()> {
        if let Some(instrument) = self.inner.take() {
            let rt = tokio::runtime::Runtime::new().map_err(|e| {
                pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to create runtime: {}",
                    e
                ))
            })?;

            rt.block_on(async {
                instrument.submit_telemetry().await.map_err(|e| {
                    pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                        "Failed to submit telemetry: {}",
                        e
                    ))
                })
            })
        } else {
            Err(pyo3::PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "Instrument already consumed",
            ))
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyDriftMetrics {
    inner: DriftMetrics,
}

#[pymethods]
impl PyDriftMetrics {
    #[getter]
    fn total_agreement_rate(&self) -> f64 {
        self.inner.total_agreement_rate
    }

    #[getter]
    fn normalized_edit_distance(&self) -> f64 {
        self.inner.normalized_edit_distance
    }

    #[getter]
    fn factual_drift_count(&self) -> u32 {
        self.inner.factual_drift_count
    }

    #[getter]
    fn consistency_score(&self) -> f64 {
        self.inner.consistency_score
    }

    #[getter]
    fn temperature_sensitivity(&self) -> f64 {
        self.inner.temperature_sensitivity
    }

    #[getter]
    fn consensus_confidence(&self) -> String {
        self.inner.consensus_confidence.clone()
    }

    #[getter]
    fn consensus_output(&self) -> Option<String> {
        self.inner.consensus_output.clone()
    }

    fn __str__(&self) -> String {
        format!(
            "DriftMetrics(tar={:.1}%, ned={:.3}, factual_drift={}, consistency={:.1}%, confidence={})",
            self.inner.total_agreement_rate,
            self.inner.normalized_edit_distance,
            self.inner.factual_drift_count,
            self.inner.consistency_score,
            self.inner.consensus_confidence
        )
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyCostEstimate {
    inner: CostEstimate,
}

#[pymethods]
impl PyCostEstimate {
    #[getter]
    fn input_tokens(&self) -> u64 {
        self.inner.input_tokens
    }

    #[getter]
    fn output_tokens(&self) -> u64 {
        self.inner.output_tokens
    }

    #[getter]
    fn total_tokens(&self) -> u64 {
        self.inner.total_tokens
    }

    #[getter]
    fn input_cost(&self) -> f64 {
        self.inner.input_cost
    }

    #[getter]
    fn output_cost(&self) -> f64 {
        self.inner.output_cost
    }

    #[getter]
    fn total_cost(&self) -> f64 {
        self.inner.total_cost
    }

    #[getter]
    fn model_name(&self) -> String {
        self.inner.model_name.clone()
    }

    #[getter]
    fn provider(&self) -> String {
        self.inner.provider.clone()
    }

    fn __str__(&self) -> String {
        format!(
            "CostEstimate({} tokens, ${:.6} for {})",
            self.inner.total_tokens, self.inner.total_cost, self.inner.model_name
        )
    }
}

#[pyclass]
pub struct PyDriftCalculator {
    inner: DriftCalculator,
}

#[pymethods]
impl PyDriftCalculator {
    #[new]
    fn new() -> Self {
        Self {
            inner: DriftCalculator::new(),
        }
    }

    fn calculate_metrics(&self, outputs: Vec<String>) -> PyDriftMetrics {
        let metrics = self.inner.calculate_metrics(&outputs);
        PyDriftMetrics { inner: metrics }
    }

    fn levenshtein_distance(&self, str1: String, str2: String) -> usize {
        DriftCalculator::levenshtein_distance(&str1, &str2)
    }

    fn normalized_edit_distance(&self, str1: String, str2: String) -> f64 {
        DriftCalculator::normalized_edit_distance(&str1, &str2)
    }

    fn calculate_total_agreement_rate(&self, outputs: Vec<String>) -> f64 {
        DriftCalculator::calculate_total_agreement_rate(&outputs)
    }

    // Enhanced drift detection methods

    #[pyo3(signature = (outputs, context=None))]
    fn calculate_enhanced_metrics(
        &self,
        outputs: Vec<String>,
        context: Option<String>,
    ) -> PyEnhancedDriftMetrics {
        let context_ref = context.as_deref();
        let metrics = self.inner.calculate_enhanced_metrics(&outputs, context_ref);
        PyEnhancedDriftMetrics { inner: metrics }
    }

    fn calculate_temporal_drift(
        &self,
        historical_metrics: Vec<(f64, PyDriftMetrics)>,
    ) -> Option<PyTemporalDrift> {
        let rust_metrics: Vec<(f64, DriftMetrics)> = historical_metrics
            .into_iter()
            .map(|(timestamp, py_metrics)| (timestamp, py_metrics.inner))
            .collect();

        self.inner
            .calculate_temporal_drift(&rust_metrics)
            .map(|temporal| PyTemporalDrift { inner: temporal })
    }
}

#[pyclass]
pub struct PyCostCalculator {
    inner: CostCalculator,
}

#[pymethods]
impl PyCostCalculator {
    #[new]
    fn new() -> Self {
        Self {
            inner: CostCalculator::new(),
        }
    }

    #[pyo3(signature = (model_name, input_text, output_text, input_tokens=None, output_tokens=None))]
    fn estimate_cost(
        &self,
        model_name: String,
        input_text: String,
        output_text: String,
        input_tokens: Option<u64>,
        output_tokens: Option<u64>,
    ) -> Option<PyCostEstimate> {
        let exact_tokens = if let (Some(input), Some(output)) = (input_tokens, output_tokens) {
            Some((input, output))
        } else {
            None
        };

        self.inner
            .estimate_cost(&model_name, &input_text, &output_text, exact_tokens)
            .map(|estimate| PyCostEstimate { inner: estimate })
    }

    fn count_tokens_approximate(&self, text: String) -> u64 {
        CostCalculator::count_tokens_approximate(&text)
    }

    fn calculate_monthly_cost(
        &self,
        model_name: String,
        daily_input_tokens: u64,
        daily_output_tokens: u64,
    ) -> Option<f64> {
        self.inner
            .calculate_monthly_cost(&model_name, daily_input_tokens, daily_output_tokens)
    }
}

// Enhanced drift metrics Python classes

#[pyclass]
pub struct PyEnhancedDriftMetrics {
    inner: EnhancedDriftMetrics,
}

#[pymethods]
impl PyEnhancedDriftMetrics {
    #[getter]
    fn basic_metrics(&self) -> PyDriftMetrics {
        PyDriftMetrics {
            inner: self.inner.basic_metrics.clone(),
        }
    }

    #[getter]
    fn semantic_similarity(&self) -> f64 {
        self.inner.semantic_similarity
    }

    #[getter]
    fn statistical_drift(&self) -> PyStatisticalDrift {
        PyStatisticalDrift {
            inner: self.inner.statistical_drift.clone(),
        }
    }

    #[getter]
    fn structural_drift(&self) -> PyStructuralDrift {
        PyStructuralDrift {
            inner: self.inner.structural_drift.clone(),
        }
    }

    #[getter]
    fn temporal_drift(&self) -> Option<PyTemporalDrift> {
        self.inner
            .temporal_drift
            .as_ref()
            .map(|temporal| PyTemporalDrift {
                inner: temporal.clone(),
            })
    }

    #[getter]
    fn ensemble_score(&self) -> f64 {
        self.inner.ensemble_score
    }

    #[getter]
    fn confidence_interval(&self) -> PyConfidenceInterval {
        PyConfidenceInterval {
            inner: self.inner.confidence_interval.clone(),
        }
    }

    #[getter]
    fn drift_severity(&self) -> String {
        match &self.inner.drift_severity {
            DriftSeverity::None => "none".to_string(),
            DriftSeverity::Low => "low".to_string(),
            DriftSeverity::Moderate => "moderate".to_string(),
            DriftSeverity::High => "high".to_string(),
            DriftSeverity::Critical => "critical".to_string(),
        }
    }

    #[getter]
    fn recommendations(&self) -> Vec<String> {
        self.inner.recommendations.clone()
    }

    fn __str__(&self) -> String {
        format!(
            "EnhancedDriftMetrics(ensemble_score={:.3}, severity={}, recommendations={})",
            self.inner.ensemble_score,
            self.drift_severity(),
            self.inner.recommendations.len()
        )
    }
}

#[pyclass]
pub struct PyStatisticalDrift {
    inner: StatisticalDrift,
}

#[pymethods]
impl PyStatisticalDrift {
    #[getter]
    fn mean_length_change(&self) -> f64 {
        self.inner.mean_length_change
    }

    #[getter]
    fn variance_change(&self) -> f64 {
        self.inner.variance_change
    }

    #[getter]
    fn distribution_shift(&self) -> f64 {
        self.inner.distribution_shift
    }

    #[getter]
    fn outlier_count(&self) -> u32 {
        self.inner.outlier_count
    }

    #[getter]
    fn p_value(&self) -> Option<f64> {
        self.inner.p_value
    }
}

#[pyclass]
pub struct PyStructuralDrift {
    inner: StructuralDrift,
}

#[pymethods]
impl PyStructuralDrift {
    #[getter]
    fn format_consistency(&self) -> f64 {
        self.inner.format_consistency
    }

    #[getter]
    fn entity_drift(&self) -> f64 {
        self.inner.entity_drift
    }

    #[getter]
    fn sentiment_drift(&self) -> f64 {
        self.inner.sentiment_drift
    }

    #[getter]
    fn complexity_drift(&self) -> f64 {
        self.inner.complexity_drift
    }

    #[getter]
    fn punctuation_drift(&self) -> f64 {
        self.inner.punctuation_drift
    }
}

#[pyclass]
pub struct PyTemporalDrift {
    inner: TemporalDrift,
}

#[pymethods]
impl PyTemporalDrift {
    #[getter]
    fn drift_velocity(&self) -> f64 {
        self.inner.drift_velocity
    }

    #[getter]
    fn drift_acceleration(&self) -> f64 {
        self.inner.drift_acceleration
    }

    #[getter]
    fn trend_direction(&self) -> String {
        match &self.inner.trend_direction {
            TrendDirection::Stable => "stable".to_string(),
            TrendDirection::Improving => "improving".to_string(),
            TrendDirection::Degrading => "degrading".to_string(),
            TrendDirection::Oscillating => "oscillating".to_string(),
            TrendDirection::Unknown => "unknown".to_string(),
        }
    }

    #[getter]
    fn seasonality_detected(&self) -> bool {
        self.inner.seasonality_detected
    }

    #[getter]
    fn stability_score(&self) -> f64 {
        self.inner.stability_score
    }
}

#[pyclass]
pub struct PyConfidenceInterval {
    inner: ConfidenceInterval,
}

#[pymethods]
impl PyConfidenceInterval {
    #[getter]
    fn lower_bound(&self) -> f64 {
        self.inner.lower_bound
    }

    #[getter]
    fn upper_bound(&self) -> f64 {
        self.inner.upper_bound
    }

    #[getter]
    fn confidence_level(&self) -> f64 {
        self.inner.confidence_level
    }

    #[getter]
    fn margin_of_error(&self) -> f64 {
        self.inner.margin_of_error
    }
}

// Compliance framework Python classes

#[pyclass]
pub struct PyComplianceManager {
    inner: ComplianceManager,
}

#[pymethods]
impl PyComplianceManager {
    #[new]
    #[pyo3(signature = (config=None))]
    fn new(config: Option<PyComplianceConfig>) -> Self {
        let rust_config = config.map(|c| c.inner).unwrap_or_default();

        Self {
            inner: ComplianceManager::new(rust_config),
        }
    }

    fn check_compliance(&self, context: PyComplianceContext) -> Vec<PyComplianceReport> {
        let reports = self.inner.check_compliance(&context.inner);
        reports
            .into_iter()
            .map(|report| PyComplianceReport { inner: report })
            .collect()
    }

    fn generate_summary(&self) -> PyComplianceSummary {
        let summary = self.inner.generate_compliance_summary();
        PyComplianceSummary { inner: summary }
    }

    fn __str__(&self) -> String {
        "ComplianceManager(frameworks=active)".to_string()
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyComplianceConfig {
    inner: ComplianceConfig,
}

#[pymethods]
impl PyComplianceConfig {
    #[new]
    fn new() -> Self {
        Self {
            inner: ComplianceConfig::default(),
        }
    }

    #[getter]
    fn frameworks(&self) -> Vec<String> {
        self.inner
            .frameworks
            .iter()
            .map(|f| match f {
                ComplianceFramework::Gdpr => "gdpr".to_string(),
                ComplianceFramework::Soc2 => "soc2".to_string(),
                ComplianceFramework::Hipaa => "hipaa".to_string(),
                ComplianceFramework::Fsb => "fsb".to_string(),
                ComplianceFramework::Bis => "bis".to_string(),
                ComplianceFramework::Cftc => "cftc".to_string(),
            })
            .collect()
    }

    #[getter]
    fn enable_audit_logging(&self) -> bool {
        self.inner.enable_audit_logging
    }

    #[getter]
    fn data_retention_days(&self) -> u32 {
        self.inner.data_retention_days
    }

    #[getter]
    fn anonymization_enabled(&self) -> bool {
        self.inner.anonymization_enabled
    }

    fn set_frameworks(&mut self, frameworks: Vec<String>) {
        self.inner.frameworks = frameworks
            .into_iter()
            .filter_map(|f| match f.as_str() {
                "gdpr" => Some(ComplianceFramework::Gdpr),
                "soc2" => Some(ComplianceFramework::Soc2),
                "hipaa" => Some(ComplianceFramework::Hipaa),
                "fsb" => Some(ComplianceFramework::Fsb),
                "bis" => Some(ComplianceFramework::Bis),
                "cftc" => Some(ComplianceFramework::Cftc),
                _ => None,
            })
            .collect();
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyComplianceContext {
    inner: crate::compliance::ComplianceContext,
}

#[pymethods]
impl PyComplianceContext {
    #[new]
    #[pyo3(signature = (agent_id, data_categories, processing_purpose, user_id=None))]
    fn new(
        agent_id: u64,
        data_categories: Vec<String>,
        processing_purpose: String,
        user_id: Option<String>,
    ) -> Self {
        let rust_data_categories = data_categories
            .into_iter()
            .filter_map(|cat| match cat.as_str() {
                "personal_data" => Some(DataCategory::PersonalData),
                "sensitive_personal_data" => Some(DataCategory::SensitivePersonalData),
                "health_data" => Some(DataCategory::HealthData),
                "financial_data" => Some(DataCategory::FinancialData),
                "biometric_data" => Some(DataCategory::BiometricData),
                "non_personal_data" => Some(DataCategory::NonPersonalData),
                "anonymized_data" => Some(DataCategory::AnonymizedData),
                "pseudonymized_data" => Some(DataCategory::PseudonymizedData),
                _ => None,
            })
            .collect();

        Self {
            inner: crate::compliance::ComplianceContext {
                agent_id,
                user_id,
                data_categories: rust_data_categories,
                processing_purpose,
                data_retention_period: None,
                cross_border_transfer: false,
                consent_status: None,
                security_measures: crate::compliance::SecurityMeasures {
                    encryption_enabled: true,
                    access_controls: true,
                    audit_logging: true,
                    data_minimization: true,
                    anonymization: false,
                },
            },
        }
    }

    #[getter]
    fn agent_id(&self) -> u64 {
        self.inner.agent_id
    }

    #[getter]
    fn processing_purpose(&self) -> String {
        self.inner.processing_purpose.clone()
    }

    #[getter]
    fn data_categories(&self) -> Vec<String> {
        self.inner
            .data_categories
            .iter()
            .map(|cat| match cat {
                DataCategory::PersonalData => "personal_data".to_string(),
                DataCategory::SensitivePersonalData => "sensitive_personal_data".to_string(),
                DataCategory::HealthData => "health_data".to_string(),
                DataCategory::FinancialData => "financial_data".to_string(),
                DataCategory::BiometricData => "biometric_data".to_string(),
                DataCategory::NonPersonalData => "non_personal_data".to_string(),
                DataCategory::AnonymizedData => "anonymized_data".to_string(),
                DataCategory::PseudonymizedData => "pseudonymized_data".to_string(),
            })
            .collect()
    }
}

#[pyclass]
pub struct PyComplianceReport {
    inner: ComplianceReport,
}

#[pymethods]
impl PyComplianceReport {
    #[getter]
    fn framework(&self) -> String {
        match self.inner.framework {
            ComplianceFramework::Gdpr => "gdpr".to_string(),
            ComplianceFramework::Soc2 => "soc2".to_string(),
            ComplianceFramework::Hipaa => "hipaa".to_string(),
            ComplianceFramework::Fsb => "fsb".to_string(),
            ComplianceFramework::Bis => "bis".to_string(),
            ComplianceFramework::Cftc => "cftc".to_string(),
        }
    }

    #[getter]
    fn overall_status(&self) -> String {
        match self.inner.overall_status {
            ComplianceStatus::Compliant => "compliant".to_string(),
            ComplianceStatus::NonCompliant => "non_compliant".to_string(),
            ComplianceStatus::RequiresReview => "requires_review".to_string(),
            ComplianceStatus::PendingApproval => "pending_approval".to_string(),
            ComplianceStatus::Exempted => "exempted".to_string(),
        }
    }

    #[getter]
    fn compliance_score(&self) -> f64 {
        self.inner.compliance_score
    }

    #[getter]
    fn requirements_checked(&self) -> u32 {
        self.inner.requirements_checked
    }

    #[getter]
    fn requirements_met(&self) -> u32 {
        self.inner.requirements_met
    }

    #[getter]
    fn violations_count(&self) -> usize {
        self.inner.violations.len()
    }

    #[getter]
    fn recommendations_count(&self) -> usize {
        self.inner.recommendations.len()
    }

    fn __str__(&self) -> String {
        format!(
            "ComplianceReport(framework={}, status={}, score={:.2})",
            self.framework(),
            self.overall_status(),
            self.inner.compliance_score
        )
    }
}

#[pyclass]
pub struct PyComplianceSummary {
    inner: crate::compliance::ComplianceSummary,
}

#[pymethods]
impl PyComplianceSummary {
    #[getter]
    fn total_frameworks(&self) -> u32 {
        self.inner.total_frameworks
    }

    #[getter]
    fn compliant_frameworks(&self) -> u32 {
        self.inner.compliant_frameworks
    }

    #[getter]
    fn non_compliant_frameworks(&self) -> u32 {
        self.inner.non_compliant_frameworks
    }

    #[getter]
    fn audit_events_count(&self) -> u32 {
        self.inner.audit_events_count
    }

    fn __str__(&self) -> String {
        format!(
            "ComplianceSummary(frameworks={}, compliant={}, events={})",
            self.inner.total_frameworks,
            self.inner.compliant_frameworks,
            self.inner.audit_events_count
        )
    }
}

// Convenience functions
#[pyfunction]
fn calculate_drift_metrics_py(outputs: Vec<String>) -> PyDriftMetrics {
    let metrics = calculate_drift_metrics(&outputs);
    PyDriftMetrics { inner: metrics }
}

#[pyfunction]
#[pyo3(signature = (outputs, context=None))]
fn calculate_enhanced_drift_metrics_py(
    outputs: Vec<String>,
    context: Option<String>,
) -> PyEnhancedDriftMetrics {
    let context_ref = context.as_deref();
    let metrics = calculate_enhanced_drift_metrics(&outputs, context_ref);
    PyEnhancedDriftMetrics { inner: metrics }
}

#[pyfunction]
#[pyo3(signature = (model_name, input_text, output_text, input_tokens=None, output_tokens=None))]
fn estimate_cost_py(
    model_name: String,
    input_text: String,
    output_text: String,
    input_tokens: Option<u64>,
    output_tokens: Option<u64>,
) -> Option<PyCostEstimate> {
    let exact_tokens = if let (Some(input), Some(output)) = (input_tokens, output_tokens) {
        Some((input, output))
    } else {
        None
    };

    estimate_cost(&model_name, &input_text, &output_text, exact_tokens)
        .map(|estimate| PyCostEstimate { inner: estimate })
}

#[pyfunction]
fn count_tokens_approximate_py(text: String) -> u64 {
    count_tokens_approximate(&text)
}

#[pyfunction]
fn format_cost_py(cost_usd: f64) -> String {
    format_cost(cost_usd)
}

#[pyfunction]
fn format_tokens_py(tokens: u64) -> String {
    format_tokens(tokens)
}

#[pymodule]
fn _internal(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Original classes
    m.add_class::<PyTelemetryConfig>()?;
    m.add_class::<PyEventLevel>()?;
    m.add_class::<PyEventMetadata>()?;
    m.add_class::<PyEventBuilder>()?;
    m.add_class::<PyEvent>()?;
    m.add_class::<PySession>()?;
    m.add_class::<PyTelemetryClient>()?;

    // New instrumentation classes
    m.add_class::<PyInstrumentationConfig>()?;
    m.add_class::<PyAgentInstrument>()?;
    m.add_class::<PyDriftMetrics>()?;
    m.add_class::<PyCostEstimate>()?;
    m.add_class::<PyDriftCalculator>()?;
    m.add_class::<PyCostCalculator>()?;

    // Enhanced drift detection classes
    m.add_class::<PyEnhancedDriftMetrics>()?;
    m.add_class::<PyStatisticalDrift>()?;
    m.add_class::<PyStructuralDrift>()?;
    m.add_class::<PyTemporalDrift>()?;
    m.add_class::<PyConfidenceInterval>()?;

    // Compliance framework classes
    m.add_class::<PyComplianceManager>()?;
    m.add_class::<PyComplianceConfig>()?;
    m.add_class::<PyComplianceContext>()?;
    m.add_class::<PyComplianceReport>()?;
    m.add_class::<PyComplianceSummary>()?;

    // Convenience functions
    m.add_function(wrap_pyfunction!(calculate_drift_metrics_py, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_enhanced_drift_metrics_py, m)?)?;
    m.add_function(wrap_pyfunction!(estimate_cost_py, m)?)?;
    m.add_function(wrap_pyfunction!(count_tokens_approximate_py, m)?)?;
    m.add_function(wrap_pyfunction!(format_cost_py, m)?)?;
    m.add_function(wrap_pyfunction!(format_tokens_py, m)?)?;

    Ok(())
}
