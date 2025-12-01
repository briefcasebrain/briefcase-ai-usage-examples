//! Enhanced Telemetry Client
//!
//! This module provides the enhanced telemetry client with multi-protocol support,
//! organization context, experiment integration, and backward compatibility.

use crate::auth::AuthManager;
use crate::config::{EnhancedTelemetryConfig, OrganizationContext, ExperimentContext};
use crate::experiment::{ExperimentManager, ExperimentManagerFactory};
use crate::protocols::{MultiProtocolClient, ProtocolError, ProtocolResult};
use crate::transformer::DefaultDataTransformer;
use crate::{Event, Session, TelemetryData};
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::Mutex;
use tokio::time::{interval, Interval};
use tracing::{debug, error, info, warn};

/// Enhanced telemetry client with multi-protocol support and modern features
#[derive(Clone)]
pub struct EnhancedTelemetryClient {
    config: EnhancedTelemetryConfig,
    session: Session,
    multi_protocol_client: Arc<MultiProtocolClient>,
    auth_manager: Arc<Mutex<AuthManager>>,
    experiment_manager: Arc<Mutex<Box<dyn ExperimentManager>>>,
    buffer: Arc<Mutex<Vec<Event>>>,
    background_task_handle: Arc<Mutex<Option<tokio::task::JoinHandle<()>>>>,
}

impl EnhancedTelemetryClient {
    /// Creates a new enhanced telemetry client
    pub async fn new(config: EnhancedTelemetryConfig) -> ProtocolResult<Self> {
        // Create session with organization context
        let mut session = Session::new();
        if let Some(org_context) = &config.organization {
            session = session.with_metadata(
                "organization".to_string(),
                serde_json::to_value(org_context)
                    .map_err(|e| ProtocolError::ConfigurationError(format!("Invalid organization context: {}", e)))?
            );
        }

        // Add experiment context to session if present
        if !config.experiments.is_empty() {
            session = session.with_metadata(
                "experiments".to_string(),
                serde_json::to_value(&config.experiments)
                    .map_err(|e| ProtocolError::ConfigurationError(format!("Invalid experiment context: {}", e)))?
            );
        }

        // Create auth manager
        let auth_manager = AuthManager::new(&config.auth)
            .map_err(|e| ProtocolError::AuthenticationError(format!("Failed to create auth manager: {}", e)))?;

        // Create data transformer
        let transformer = Arc::new(DefaultDataTransformer::new());

        // Create experiment manager
        // Use BRIEFCASE_API_URL environment variable, defaulting to production endpoint
        let experiment_api_url = std::env::var("BRIEFCASE_API_URL")
            .ok()
            .or_else(|| Some("https://telemetry.briefcasebrain.com/api".to_string()));
        let experiment_manager = ExperimentManagerFactory::from_config(
            experiment_api_url,
            match &config.auth {
                crate::config::AuthMode::ApiKey { key } => Some(key.clone()),
                crate::config::AuthMode::JwtToken { token } => Some(token.clone()),
                _ => None,
            }
        );

        // Try to enroll in experiments if organization context is available
        let mut experiment_manager_mutable = experiment_manager;
        let experiment_contexts = if let Some(org_context) = &config.organization {
            match experiment_manager_mutable.enroll_experiments(org_context).await {
                Ok(experiments) => {
                    info!("Successfully enrolled in {} experiments", experiments.len());
                    experiments
                }
                Err(e) => {
                    warn!("Failed to enroll in experiments: {}", e);
                    config.experiments.clone()
                }
            }
        } else {
            config.experiments.clone()
        };

        // Create multi-protocol client
        let multi_protocol_client = MultiProtocolClient::new(
            &config,
            transformer,
            Some(Arc::new(experiment_manager_mutable))
        )?;

        Ok(Self {
            config,
            session,
            multi_protocol_client: Arc::new(multi_protocol_client),
            auth_manager: Arc::new(Mutex::new(auth_manager)),
            experiment_manager: Arc::new(Mutex::new(ExperimentManagerFactory::create_noop())), // Placeholder
            buffer: Arc::new(Mutex::new(Vec::new())),
            background_task_handle: Arc::new(Mutex::new(None)),
        })
    }

    /// Creates a client from legacy TelemetryConfig for backward compatibility
    pub async fn from_legacy_config(legacy_config: crate::config::TelemetryConfig) -> ProtocolResult<Self> {
        let enhanced_config = EnhancedTelemetryConfig::from_legacy(&legacy_config);
        Self::new(enhanced_config).await
    }

    /// Sets the session for this client
    pub fn with_session(mut self, session: Session) -> Self {
        self.session = session;
        self
    }

    /// Sets organization context and enrolls in experiments
    pub async fn with_organization_context(mut self, org_context: OrganizationContext) -> ProtocolResult<Self> {
        // Update session metadata
        self.session = self.session.with_metadata(
            "organization".to_string(),
            serde_json::to_value(&org_context)
                .map_err(|e| ProtocolError::ConfigurationError(format!("Invalid organization context: {}", e)))?
        );

        // Try to enroll in experiments
        let mut experiment_manager = self.experiment_manager.lock().await;
        match experiment_manager.enroll_experiments(&org_context).await {
            Ok(experiments) => {
                info!("Successfully enrolled in {} experiments after setting organization context", experiments.len());

                // Update session with experiment context
                if !experiments.is_empty() {
                    self.session = self.session.with_metadata(
                        "experiments".to_string(),
                        serde_json::to_value(&experiments)
                            .map_err(|e| ProtocolError::ConfigurationError(format!("Invalid experiment context: {}", e)))?
                    );
                }
            }
            Err(e) => {
                warn!("Failed to enroll in experiments: {}", e);
            }
        }

        Ok(self)
    }

    /// Adds an experiment context
    pub fn with_experiment(mut self, experiment: ExperimentContext) -> Self {
        // Get current experiments from session
        let mut experiments = self.session.metadata
            .get("experiments")
            .and_then(|exp| serde_json::from_value::<Vec<ExperimentContext>>(exp.clone()).ok())
            .unwrap_or_default();

        experiments.push(experiment);

        // Update session metadata
        self.session = self.session.with_metadata(
            "experiments".to_string(),
            serde_json::to_value(&experiments).unwrap_or(serde_json::Value::Null)
        );

        self
    }

    /// Tracks an event with automatic experiment tagging
    pub async fn track_event(&self, mut event: Event) -> ProtocolResult<()> {
        if !self.config.enabled {
            debug!("Telemetry disabled, skipping event: {}", event.name);
            return Ok(());
        }

        debug!("Tracking event: {}", event.name);

        // Refresh authentication if needed
        {
            let mut auth_manager = self.auth_manager.lock().await;
            if let Err(e) = auth_manager.refresh_if_needed().await {
                warn!("Failed to refresh authentication: {}", e);
            }
        }

        // Update experiments if needed
        {
            let mut experiment_manager = self.experiment_manager.lock().await;
            if let Err(e) = experiment_manager.update_experiments().await {
                warn!("Failed to update experiments: {}", e);
            }

            // Tag event with current experiments
            let active_experiments = experiment_manager.get_active_experiments().await;
            experiment_manager.tag_event_with_experiments(&mut event, &active_experiments);
        }

        // Add to buffer
        let mut buffer = self.buffer.lock().await;
        buffer.push(event);

        // Check if we need to flush
        if buffer.len() >= self.config.batch_size {
            let events = buffer.drain(..).collect();
            drop(buffer);
            self.flush_events(events).await?;
        }

        Ok(())
    }

    /// Manually flushes all buffered events
    pub async fn flush(&self) -> ProtocolResult<()> {
        let mut buffer = self.buffer.lock().await;
        if buffer.is_empty() {
            return Ok(());
        }

        let events = buffer.drain(..).collect();
        drop(buffer);
        self.flush_events(events).await
    }

    /// Flushes events using the multi-protocol client
    async fn flush_events(&self, events: Vec<Event>) -> ProtocolResult<()> {
        if events.is_empty() {
            return Ok(());
        }

        info!("Flushing {} events", events.len());

        // Create telemetry data
        let mut telemetry_data = TelemetryData::new(self.session.clone());
        telemetry_data.add_events(events);

        // Send via multi-protocol client
        match self.multi_protocol_client.send_telemetry(&telemetry_data).await {
            Ok(_) => {
                info!("Successfully sent telemetry data");
                Ok(())
            }
            Err(e) => {
                error!("Failed to send telemetry data: {}", e);
                Err(e)
            }
        }
    }

    /// Records agent run data
    pub async fn record_agent_run(&self, agent_run_data: &serde_json::Value) -> ProtocolResult<()> {
        if !self.config.enabled {
            debug!("Telemetry disabled, skipping agent run recording");
            return Ok(());
        }

        debug!("Recording agent run");

        // Refresh authentication if needed
        {
            let mut auth_manager = self.auth_manager.lock().await;
            if let Err(e) = auth_manager.refresh_if_needed().await {
                warn!("Failed to refresh authentication: {}", e);
            }
        }

        // Add session and organization context to agent run data
        let mut enhanced_data = agent_run_data.clone();
        if let Some(obj) = enhanced_data.as_object_mut() {
            obj.insert("session_id".to_string(), serde_json::Value::String(self.session.id.to_string()));

            if let Some(org_data) = self.session.metadata.get("organization") {
                obj.insert("organization".to_string(), org_data.clone());
            }

            if let Some(exp_data) = self.session.metadata.get("experiments") {
                obj.insert("experiments".to_string(), exp_data.clone());
            }
        }

        // Send via multi-protocol client
        match self.multi_protocol_client.send_agent_run(&enhanced_data).await {
            Ok(_) => {
                info!("Successfully recorded agent run");
                Ok(())
            }
            Err(e) => {
                error!("Failed to record agent run: {}", e);
                Err(e)
            }
        }
    }

    /// Sends batch data
    pub async fn send_batch(&self, records: Vec<serde_json::Value>) -> ProtocolResult<()> {
        if !self.config.enabled {
            debug!("Telemetry disabled, skipping batch send");
            return Ok(());
        }

        if records.is_empty() {
            return Ok(());
        }

        info!("Sending batch of {} records", records.len());

        // Refresh authentication if needed
        {
            let mut auth_manager = self.auth_manager.lock().await;
            if let Err(e) = auth_manager.refresh_if_needed().await {
                warn!("Failed to refresh authentication: {}", e);
            }
        }

        // Enhance records with session and context information
        let enhanced_records: Vec<serde_json::Value> = records.into_iter().map(|mut record| {
            if let Some(obj) = record.as_object_mut() {
                obj.insert("session_id".to_string(), serde_json::Value::String(self.session.id.to_string()));

                if let Some(org_data) = self.session.metadata.get("organization") {
                    obj.insert("organization".to_string(), org_data.clone());
                }

                if let Some(exp_data) = self.session.metadata.get("experiments") {
                    obj.insert("experiments".to_string(), exp_data.clone());
                }
            }
            record
        }).collect();

        // Send via multi-protocol client
        match self.multi_protocol_client.send_batch(&enhanced_records).await {
            Ok(_) => {
                info!("Successfully sent batch data");
                Ok(())
            }
            Err(e) => {
                error!("Failed to send batch data: {}", e);
                Err(e)
            }
        }
    }

    /// Starts background flush task
    pub async fn start_background_flush(&self) -> ProtocolResult<()> {
        let mut handle_guard = self.background_task_handle.lock().await;

        // Stop existing task if running
        if let Some(handle) = handle_guard.take() {
            handle.abort();
        }

        let client = self.clone();
        let flush_interval = self.config.flush_interval;

        let handle = tokio::spawn(async move {
            let mut interval = interval(flush_interval);

            loop {
                interval.tick().await;

                // Update experiments periodically
                {
                    let mut experiment_manager = client.experiment_manager.lock().await;
                    if let Err(e) = experiment_manager.update_experiments().await {
                        debug!("Failed to update experiments in background: {}", e);
                    }
                }

                // Flush events
                if let Err(e) = client.flush().await {
                    error!("Background flush failed: {}", e);
                }
            }
        });

        *handle_guard = Some(handle);

        info!(
            "Started background flush with interval: {:?}",
            flush_interval
        );
        Ok(())
    }

    /// Stops background flush task
    pub async fn stop_background_flush(&self) {
        let mut handle_guard = self.background_task_handle.lock().await;
        if let Some(handle) = handle_guard.take() {
            handle.abort();
            info!("Stopped background flush");
        }
    }

    /// Performs health check on all protocols
    pub async fn health_check(&self) -> std::collections::HashMap<crate::config::EndpointType, ProtocolResult<()>> {
        self.multi_protocol_client.health_check().await
    }

    /// Gets the current session
    pub fn session(&self) -> &Session {
        &self.session
    }

    /// Gets the current configuration
    pub fn config(&self) -> &EnhancedTelemetryConfig {
        &self.config
    }

    /// Gets current buffer size
    pub async fn buffer_size(&self) -> usize {
        self.buffer.lock().await.len()
    }

    /// Gets current active experiments
    pub async fn get_active_experiments(&self) -> Vec<ExperimentContext> {
        let experiment_manager = self.experiment_manager.lock().await;
        experiment_manager.get_active_experiments().await
    }

    /// Checks if a specific experiment is active
    pub async fn is_experiment_active(&self, experiment_id: &str) -> bool {
        let experiment_manager = self.experiment_manager.lock().await;
        experiment_manager.is_experiment_active(experiment_id).await
    }

    /// Gets configuration for a specific experiment
    pub async fn get_experiment_config(&self, experiment_id: &str) -> Option<std::collections::HashMap<String, serde_json::Value>> {
        let experiment_manager = self.experiment_manager.lock().await;
        experiment_manager.get_experiment_config(experiment_id).await
    }

    /// Graceful shutdown
    pub async fn shutdown(self) -> ProtocolResult<()> {
        info!("Shutting down enhanced telemetry client");

        // Stop background tasks
        self.stop_background_flush().await;

        // Flush remaining events
        if let Err(e) = self.flush().await {
            warn!("Failed to flush remaining events during shutdown: {}", e);
        }

        // Shutdown multi-protocol client
        let mut multi_protocol_client = Arc::try_unwrap(self.multi_protocol_client)
            .map_err(|_| ProtocolError::ProtocolSpecific {
                protocol: crate::config::EndpointType::TrpcLegacy,
                message: "Failed to unwrap multi-protocol client for shutdown".to_string(),
            })?;

        multi_protocol_client.shutdown().await?;

        info!("Enhanced telemetry client shutdown complete");
        Ok(())
    }
}

// Drop implementation for graceful cleanup
impl Drop for EnhancedTelemetryClient {
    fn drop(&mut self) {
        // Note: We can't call async functions in Drop, so we just log a warning
        // Users should call shutdown() explicitly for graceful cleanup
        debug!("EnhancedTelemetryClient dropped - consider calling shutdown() explicitly");
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::*;
    use crate::{EventBuilder, EventLevel};
    use std::time::Duration;

    async fn create_test_client() -> EnhancedTelemetryClient {
        let config = EnhancedTelemetryConfig::with_api_key("bca_test_key")
            .with_timeout(Duration::from_secs(1))
            .with_batch_size(2)
            .with_enabled(false); // Disable to avoid actual network calls in tests

        EnhancedTelemetryClient::new(config).await.unwrap()
    }

    #[tokio::test]
    async fn test_enhanced_client_creation() {
        let client = create_test_client().await;
        assert_eq!(client.config.batch_size, 2);
        assert!(!client.config.enabled);
    }

    #[tokio::test]
    async fn test_from_legacy_config() {
        let legacy_config = crate::config::TelemetryConfig::new("test_key".to_string())
            .with_endpoint("https://test.example.com/api/trpc/ingest.telemetry".to_string())
            .with_batch_size(50);

        let client = EnhancedTelemetryClient::from_legacy_config(legacy_config).await.unwrap();
        assert_eq!(client.config.batch_size, 50);
        assert!(matches!(client.config.auth, AuthMode::ApiKey { .. }));
    }

    #[tokio::test]
    async fn test_with_organization_context() {
        let client = create_test_client().await;
        let org_context = OrganizationContext::new("org_123", "ml_agents");

        let enhanced_client = client.with_organization_context(org_context).await.unwrap();
        assert!(enhanced_client.session.metadata.contains_key("organization"));
    }

    #[tokio::test]
    async fn test_with_experiment() {
        let client = create_test_client().await;
        let experiment = ExperimentContext::new("exp_123", "variant_a");

        let enhanced_client = client.with_experiment(experiment);
        assert!(enhanced_client.session.metadata.contains_key("experiments"));
    }

    #[tokio::test]
    async fn test_track_event() {
        let client = create_test_client().await;

        let event = EventBuilder::new("test_event".to_string())
            .level(EventLevel::Info)
            .build();

        let result = client.track_event(event).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_flush() {
        let client = create_test_client().await;

        let event = EventBuilder::new("test_event".to_string()).build();
        client.track_event(event).await.unwrap();

        let result = client.flush().await;
        // With enabled=false, this should succeed but not actually send
        assert!(result.is_ok());
        assert_eq!(client.buffer_size().await, 0);
    }

    #[tokio::test]
    async fn test_record_agent_run() {
        let client = create_test_client().await;

        let agent_data = serde_json::json!({
            "agent_id": "agent_123",
            "status": "completed"
        });

        let result = client.record_agent_run(&agent_data).await;
        // With enabled=false, this should return early
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_send_batch() {
        let client = create_test_client().await;

        let records = vec![
            serde_json::json!({ "id": 1 }),
            serde_json::json!({ "id": 2 }),
        ];

        let result = client.send_batch(records).await;
        // With enabled=false, this should return early
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_background_flush() {
        let client = create_test_client().await;

        // Start background flush
        let result = client.start_background_flush().await;
        assert!(result.is_ok());

        // Stop background flush
        client.stop_background_flush().await;
    }

    #[tokio::test]
    async fn test_health_check() {
        let client = create_test_client().await;

        let health_results = client.health_check().await;
        assert!(!health_results.is_empty());
    }

    #[tokio::test]
    async fn test_experiment_methods() {
        let client = create_test_client().await;

        let active_experiments = client.get_active_experiments().await;
        assert!(active_experiments.is_empty());

        let is_active = client.is_experiment_active("exp_123").await;
        assert!(!is_active);

        let config = client.get_experiment_config("exp_123").await;
        assert!(config.is_none());
    }

    #[tokio::test]
    async fn test_shutdown() {
        let client = create_test_client().await;

        let result = client.shutdown().await;
        assert!(result.is_ok());
    }
}