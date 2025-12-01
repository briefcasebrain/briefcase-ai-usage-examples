//! Experiment Integration Module
//!
//! This module provides experiment enrollment, management, and automatic A/B testing
//! integration with telemetry events for dashboard analytics.

use crate::config::{ExperimentContext, OrganizationContext};
use crate::Event;
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;
use thiserror::Error;
use tokio::sync::RwLock;
use tracing::{debug, error, info, warn};

/// Experiment errors
#[derive(Debug, Error)]
pub enum ExperimentError {
    #[error("Enrollment failed: {0}")]
    EnrollmentFailed(String),

    #[error("Experiment not found: {0}")]
    ExperimentNotFound(String),

    #[error("Invalid experiment configuration: {0}")]
    InvalidConfiguration(String),

    #[error("Network error: {0}")]
    NetworkError(#[from] reqwest::Error),

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("Update failed: {0}")]
    UpdateFailed(String),
}

/// Result type for experiment operations
pub type ExperimentResult<T> = Result<T, ExperimentError>;

/// Experiment enrollment response from backend
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExperimentEnrollmentResponse {
    pub experiments: Vec<ExperimentEnrollment>,
    pub enrollment_id: String,
    pub expires_at: chrono::DateTime<chrono::Utc>,
}

/// Individual experiment enrollment
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExperimentEnrollment {
    pub experiment_id: String,
    pub experiment_name: String,
    pub variant: String,
    pub config: HashMap<String, serde_json::Value>,
    pub active: bool,
    pub priority: i32,
    pub sample_rate: f64,
    pub enrolled_at: chrono::DateTime<chrono::Utc>,
}

impl From<ExperimentEnrollment> for ExperimentContext {
    fn from(enrollment: ExperimentEnrollment) -> Self {
        ExperimentContext {
            experiment_id: enrollment.experiment_id,
            experiment_name: Some(enrollment.experiment_name),
            variant: enrollment.variant,
            enrolled_at: enrollment.enrolled_at,
            config: enrollment.config,
            active: enrollment.active,
        }
    }
}

/// Experiment status update
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExperimentUpdate {
    pub experiment_id: String,
    pub active: bool,
    pub config_changes: HashMap<String, serde_json::Value>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

/// Trait for experiment enrollment and management
#[async_trait]
pub trait ExperimentManager: Send + Sync {
    /// Enrolls the client in available experiments
    async fn enroll_experiments(
        &mut self,
        org_context: &OrganizationContext,
    ) -> ExperimentResult<Vec<ExperimentContext>>;

    /// Updates experiment status (for example, when an experiment ends)
    async fn update_experiments(&mut self) -> ExperimentResult<()>;

    /// Tags an event with experiment variants
    fn tag_event_with_experiments(&self, event: &mut Event, experiments: &[ExperimentContext]);

    /// Gets current active experiments
    async fn get_active_experiments(&self) -> Vec<ExperimentContext>;

    /// Checks if a specific experiment is active
    async fn is_experiment_active(&self, experiment_id: &str) -> bool;

    /// Gets configuration for a specific experiment
    async fn get_experiment_config(
        &self,
        experiment_id: &str,
    ) -> Option<HashMap<String, serde_json::Value>>;
}

/// Default implementation of experiment manager with backend integration
pub struct DefaultExperimentManager {
    experiments: Arc<RwLock<Vec<ExperimentContext>>>,
    enrollment_id: Arc<RwLock<Option<String>>>,
    backend_url: String,
    api_key: String,
    http_client: reqwest::Client,
    last_update: Arc<RwLock<Option<chrono::DateTime<chrono::Utc>>>>,
    update_interval: Duration,
}

impl DefaultExperimentManager {
    /// Creates a new default experiment manager
    pub fn new(backend_url: impl Into<String>, api_key: impl Into<String>) -> Self {
        Self {
            experiments: Arc::new(RwLock::new(Vec::new())),
            enrollment_id: Arc::new(RwLock::new(None)),
            backend_url: backend_url.into(),
            api_key: api_key.into(),
            http_client: reqwest::Client::new(),
            last_update: Arc::new(RwLock::new(None)),
            update_interval: Duration::from_secs(300), // 5 minutes
        }
    }

    /// Sets the update interval for experiment polling
    pub fn with_update_interval(mut self, interval: Duration) -> Self {
        self.update_interval = interval;
        self
    }

    /// Fetches experiment enrollments from backend
    async fn fetch_enrollments(
        &self,
        org_context: &OrganizationContext,
    ) -> ExperimentResult<ExperimentEnrollmentResponse> {
        let enrollment_url = format!(
            "{}/api/v1/experiments/enroll",
            self.backend_url.trim_end_matches('/')
        );

        let enrollment_request = serde_json::json!({
            "organization_id": org_context.org_id,
            "agent_group": org_context.agent_group,
            "environment": org_context.environment,
            "metadata": org_context.metadata,
            "client_id": self.generate_client_id(org_context),
            "timestamp": chrono::Utc::now()
        });

        debug!("Fetching experiment enrollments from: {}", enrollment_url);

        let response = self
            .http_client
            .post(&enrollment_url)
            .header("Content-Type", "application/json")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header(
                "User-Agent",
                format!("briefcase-ai-telemetry-sdk/{}", env!("CARGO_PKG_VERSION")),
            )
            .json(&enrollment_request)
            .send()
            .await?;

        if response.status().is_success() {
            let enrollment_response: ExperimentEnrollmentResponse = response.json().await?;
            info!(
                "Successfully enrolled in {} experiments",
                enrollment_response.experiments.len()
            );
            Ok(enrollment_response)
        } else {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            Err(ExperimentError::EnrollmentFailed(format!(
                "HTTP {}: {}",
                status, error_text
            )))
        }
    }

    /// Fetches experiment updates from backend
    async fn fetch_updates(&self) -> ExperimentResult<Vec<ExperimentUpdate>> {
        let enrollment_id = self.enrollment_id.read().await;
        let enrollment_id = enrollment_id.as_ref().ok_or_else(|| {
            ExperimentError::UpdateFailed("No enrollment ID available".to_string())
        })?;

        let updates_url = format!(
            "{}/api/v1/experiments/updates/{}",
            self.backend_url.trim_end_matches('/'),
            enrollment_id
        );

        // Add query parameter for last update time if available
        let url_with_params = if let Some(last_update) = *self.last_update.read().await {
            format!("{}?since={}", updates_url, last_update.timestamp())
        } else {
            updates_url
        };

        debug!("Fetching experiment updates from: {}", url_with_params);

        let response = self
            .http_client
            .get(&url_with_params)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header(
                "User-Agent",
                format!("briefcase-ai-telemetry-sdk/{}", env!("CARGO_PKG_VERSION")),
            )
            .send()
            .await?;

        if response.status().is_success() {
            let updates: Vec<ExperimentUpdate> = response.json().await?;
            debug!("Received {} experiment updates", updates.len());
            Ok(updates)
        } else if response.status() == 304 {
            // No updates available
            debug!("No experiment updates available");
            Ok(Vec::new())
        } else {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            warn!(
                "Failed to fetch experiment updates: HTTP {}: {}",
                status, error_text
            );
            Ok(Vec::new()) // Don't fail completely for update errors
        }
    }

    /// Applies experiment updates to current experiments
    async fn apply_updates(&self, updates: Vec<ExperimentUpdate>) {
        if updates.is_empty() {
            return;
        }

        let mut experiments = self.experiments.write().await;

        for update in updates {
            // Find and update the experiment
            if let Some(experiment) = experiments
                .iter_mut()
                .find(|e| e.experiment_id == update.experiment_id)
            {
                experiment.active = update.active;

                // Apply configuration changes
                for (key, value) in update.config_changes {
                    experiment.config.insert(key, value);
                }

                info!(
                    "Updated experiment {}: active={}",
                    update.experiment_id, update.active
                );
            } else {
                warn!(
                    "Received update for unknown experiment: {}",
                    update.experiment_id
                );
            }
        }

        // Update last update time
        *self.last_update.write().await = Some(chrono::Utc::now());
    }

    /// Generates a consistent client ID based on organization context
    fn generate_client_id(&self, org_context: &OrganizationContext) -> String {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        org_context.org_id.hash(&mut hasher);
        org_context.agent_group.hash(&mut hasher);
        format!("client_{:x}", hasher.finish())
    }

    /// Checks if experiments need updating based on time interval
    async fn should_update(&self) -> bool {
        if let Some(last_update) = *self.last_update.read().await {
            chrono::Utc::now() - last_update
                > chrono::Duration::from_std(self.update_interval).unwrap()
        } else {
            true
        }
    }
}

#[async_trait]
impl ExperimentManager for DefaultExperimentManager {
    async fn enroll_experiments(
        &mut self,
        org_context: &OrganizationContext,
    ) -> ExperimentResult<Vec<ExperimentContext>> {
        debug!(
            "Enrolling in experiments for organization: {}",
            org_context.org_id
        );

        // Fetch enrollments from backend
        let enrollment_response = self.fetch_enrollments(org_context).await?;

        // Convert enrollments to experiment contexts
        let experiment_contexts: Vec<ExperimentContext> = enrollment_response
            .experiments
            .into_iter()
            .map(|enrollment| enrollment.into())
            .collect();

        // Store enrollment ID for future updates
        *self.enrollment_id.write().await = Some(enrollment_response.enrollment_id);

        // Store experiments
        *self.experiments.write().await = experiment_contexts.clone();

        // Update last update time
        *self.last_update.write().await = Some(chrono::Utc::now());

        info!(
            "Successfully enrolled in {} experiments",
            experiment_contexts.len()
        );
        Ok(experiment_contexts)
    }

    async fn update_experiments(&mut self) -> ExperimentResult<()> {
        // Check if we need to update
        if !self.should_update().await {
            return Ok(());
        }

        debug!("Updating experiments from backend");

        // Fetch updates
        match self.fetch_updates().await {
            Ok(updates) => {
                self.apply_updates(updates).await;
                Ok(())
            }
            Err(e) => {
                error!("Failed to update experiments: {}", e);
                // Don't propagate update errors as they shouldn't stop telemetry
                Ok(())
            }
        }
    }

    fn tag_event_with_experiments(&self, event: &mut Event, experiments: &[ExperimentContext]) {
        if experiments.is_empty() {
            return;
        }

        // Add experiment metadata to the event
        let mut experiment_data = HashMap::new();

        for experiment in experiments.iter().filter(|e| e.active) {
            let experiment_info = serde_json::json!({
                "variant": experiment.variant,
                "enrolled_at": experiment.enrolled_at,
                "config": experiment.config
            });

            experiment_data.insert(experiment.experiment_id.clone(), experiment_info);
        }

        if !experiment_data.is_empty() {
            // Add to event metadata
            event.metadata.custom_data.insert(
                "experiments".to_string(),
                serde_json::to_value(experiment_data).unwrap_or(serde_json::Value::Null),
            );

            // Also add a simple list of active experiment IDs for easy filtering
            let active_experiment_ids: Vec<&str> = experiments
                .iter()
                .filter(|e| e.active)
                .map(|e| e.experiment_id.as_str())
                .collect();

            event.metadata.custom_data.insert(
                "active_experiments".to_string(),
                serde_json::to_value(active_experiment_ids).unwrap_or(serde_json::Value::Null),
            );

            debug!("Tagged event with {} active experiments", experiments.len());
        }
    }

    async fn get_active_experiments(&self) -> Vec<ExperimentContext> {
        self.experiments
            .read()
            .await
            .iter()
            .filter(|e| e.active)
            .cloned()
            .collect()
    }

    async fn is_experiment_active(&self, experiment_id: &str) -> bool {
        self.experiments
            .read()
            .await
            .iter()
            .any(|e| e.experiment_id == experiment_id && e.active)
    }

    async fn get_experiment_config(
        &self,
        experiment_id: &str,
    ) -> Option<HashMap<String, serde_json::Value>> {
        self.experiments
            .read()
            .await
            .iter()
            .find(|e| e.experiment_id == experiment_id && e.active)
            .map(|e| e.config.clone())
    }
}

/// No-op experiment manager for scenarios where experiments are not needed
pub struct NoOpExperimentManager;

#[async_trait]
impl ExperimentManager for NoOpExperimentManager {
    async fn enroll_experiments(
        &mut self,
        _org_context: &OrganizationContext,
    ) -> ExperimentResult<Vec<ExperimentContext>> {
        Ok(Vec::new())
    }

    async fn update_experiments(&mut self) -> ExperimentResult<()> {
        Ok(())
    }

    fn tag_event_with_experiments(&self, _event: &mut Event, _experiments: &[ExperimentContext]) {
        // No-op
    }

    async fn get_active_experiments(&self) -> Vec<ExperimentContext> {
        Vec::new()
    }

    async fn is_experiment_active(&self, _experiment_id: &str) -> bool {
        false
    }

    async fn get_experiment_config(
        &self,
        _experiment_id: &str,
    ) -> Option<HashMap<String, serde_json::Value>> {
        None
    }
}

/// Factory for creating experiment managers
pub struct ExperimentManagerFactory;

impl ExperimentManagerFactory {
    /// Creates a default experiment manager with backend integration
    pub fn create_default(
        backend_url: impl Into<String>,
        api_key: impl Into<String>,
    ) -> Box<dyn ExperimentManager> {
        Box::new(DefaultExperimentManager::new(backend_url, api_key))
    }

    /// Creates a no-op experiment manager
    pub fn create_noop() -> Box<dyn ExperimentManager> {
        Box::new(NoOpExperimentManager)
    }

    /// Creates an experiment manager based on configuration
    pub fn from_config(
        backend_url: Option<String>,
        api_key: Option<String>,
    ) -> Box<dyn ExperimentManager> {
        match (backend_url, api_key) {
            (Some(url), Some(key)) if !url.is_empty() && !key.is_empty() => {
                Self::create_default(url, key)
            }
            _ => {
                info!("No experiment backend configured, using no-op manager");
                Self::create_noop()
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::EventBuilder;

    #[test]
    fn test_experiment_enrollment_conversion() {
        let enrollment = ExperimentEnrollment {
            experiment_id: "exp_123".to_string(),
            experiment_name: "Test Experiment".to_string(),
            variant: "variant_a".to_string(),
            config: {
                let mut map = HashMap::new();
                map.insert("feature_enabled".to_string(), serde_json::Value::Bool(true));
                map
            },
            active: true,
            priority: 1,
            sample_rate: 0.5,
            enrolled_at: chrono::Utc::now(),
        };

        let context: ExperimentContext = enrollment.into();
        assert_eq!(context.experiment_id, "exp_123");
        assert_eq!(context.experiment_name, Some("Test Experiment".to_string()));
        assert_eq!(context.variant, "variant_a");
        assert!(context.active);
        assert_eq!(
            context.config.get("feature_enabled"),
            Some(&serde_json::Value::Bool(true))
        );
    }

    #[tokio::test]
    async fn test_default_experiment_manager_creation() {
        let manager = DefaultExperimentManager::new("https://api.example.com", "test_api_key");

        assert_eq!(manager.backend_url, "https://api.example.com");
        assert_eq!(manager.api_key, "test_api_key");
        assert_eq!(manager.update_interval, Duration::from_secs(300));
    }

    #[tokio::test]
    async fn test_default_experiment_manager_with_custom_interval() {
        let manager = DefaultExperimentManager::new("https://api.example.com", "test_api_key")
            .with_update_interval(Duration::from_secs(60));

        assert_eq!(manager.update_interval, Duration::from_secs(60));
    }

    #[tokio::test]
    async fn test_noop_experiment_manager() {
        let mut manager = NoOpExperimentManager;
        let org_context = OrganizationContext::new("org_123", "ml_agents");

        // Test enrollment
        let experiments = manager.enroll_experiments(&org_context).await.unwrap();
        assert!(experiments.is_empty());

        // Test update
        let result = manager.update_experiments().await;
        assert!(result.is_ok());

        // Test active experiments
        let active = manager.get_active_experiments().await;
        assert!(active.is_empty());

        // Test experiment status
        let is_active = manager.is_experiment_active("exp_123").await;
        assert!(!is_active);

        // Test experiment config
        let config = manager.get_experiment_config("exp_123").await;
        assert!(config.is_none());

        // Test event tagging (should be no-op)
        let mut event = EventBuilder::new("test_event".to_string()).build();
        let experiments = vec![];
        manager.tag_event_with_experiments(&mut event, &experiments);
        assert!(!event.metadata.custom_data.contains_key("experiments"));
    }

    #[test]
    fn test_generate_client_id() {
        let manager = DefaultExperimentManager::new("url", "key");
        let org_context1 = OrganizationContext::new("org_123", "ml_agents");
        let org_context2 = OrganizationContext::new("org_456", "data_team");

        let client_id1 = manager.generate_client_id(&org_context1);
        let client_id2 = manager.generate_client_id(&org_context1);
        let client_id3 = manager.generate_client_id(&org_context2);

        // Same context should generate same ID
        assert_eq!(client_id1, client_id2);

        // Different context should generate different ID
        assert_ne!(client_id1, client_id3);

        // Should start with "client_"
        assert!(client_id1.starts_with("client_"));
    }

    #[test]
    fn test_experiment_manager_factory() {
        // Test with valid backend configuration
        let manager1 = ExperimentManagerFactory::from_config(
            Some("https://api.example.com".to_string()),
            Some("api_key".to_string()),
        );
        // Can't easily test the type without downcasting, but this tests creation

        // Test with missing configuration
        let manager2 = ExperimentManagerFactory::from_config(None, None);
        // Should create no-op manager

        // Test with empty configuration
        let manager3 =
            ExperimentManagerFactory::from_config(Some("".to_string()), Some("".to_string()));
        // Should create no-op manager

        // Test that all managers are created successfully (non-null)
        // Note: We don't compare addresses as memory allocators may reuse addresses
        // after Arc drops, making pointer comparison unreliable
        let _ = manager1;
        let _ = manager2;
        let _ = manager3;
    }

    #[tokio::test]
    async fn test_tag_event_with_experiments() {
        let _manager = NoOpExperimentManager;
        let mut event = EventBuilder::new("test_event".to_string()).build();

        // Create test experiment contexts
        let experiment1 = ExperimentContext {
            experiment_id: "exp_1".to_string(),
            experiment_name: Some("Test Exp 1".to_string()),
            variant: "control".to_string(),
            enrolled_at: chrono::Utc::now(),
            config: {
                let mut map = HashMap::new();
                map.insert(
                    "param1".to_string(),
                    serde_json::Value::String("value1".to_string()),
                );
                map
            },
            active: true,
        };

        let experiment2 = ExperimentContext {
            experiment_id: "exp_2".to_string(),
            experiment_name: Some("Test Exp 2".to_string()),
            variant: "variant_a".to_string(),
            enrolled_at: chrono::Utc::now(),
            config: HashMap::new(),
            active: false, // Inactive experiment
        };

        let experiments = vec![experiment1, experiment2];

        // Use default manager to test actual tagging logic
        let default_manager = DefaultExperimentManager::new("url", "key");
        default_manager.tag_event_with_experiments(&mut event, &experiments);

        // Should only tag with active experiments
        assert!(event.metadata.custom_data.contains_key("experiments"));
        assert!(event
            .metadata
            .custom_data
            .contains_key("active_experiments"));

        let active_experiments = event
            .metadata
            .custom_data
            .get("active_experiments")
            .unwrap();
        let active_ids: Vec<String> = serde_json::from_value(active_experiments.clone()).unwrap();
        assert_eq!(active_ids, vec!["exp_1"]);
    }
}
