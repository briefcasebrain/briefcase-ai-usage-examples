//! Data Transformation Pipeline
//!
//! This module provides data format transformation between different protocols,
//! handling organization context injection, experiment tagging, and protocol-specific formatting.

use crate::config::{EndpointType, ExperimentContext, OrganizationContext};
use crate::protocols::{DataTransformer, ProtocolError, ProtocolResult};
use crate::TelemetryData;
use chrono::{Datelike, Timelike};
use serde_json::{json, Value as JsonValue};
use std::collections::HashMap;
use tracing::debug;

/// Default data transformer implementation
pub struct DefaultDataTransformer {
    /// Whether to include debug metadata in transformations
    include_debug_metadata: bool,
}

impl DefaultDataTransformer {
    /// Creates a new default data transformer
    pub fn new() -> Self {
        Self {
            include_debug_metadata: false,
        }
    }

    /// Creates a new data transformer with debug metadata enabled
    pub fn with_debug_metadata(mut self) -> Self {
        self.include_debug_metadata = true;
        self
    }

    /// Injects organization context into data
    fn inject_organization_context(
        &self,
        mut data: JsonValue,
        organization: &OrganizationContext,
    ) -> ProtocolResult<JsonValue> {
        if let Some(obj) = data.as_object_mut() {
            obj.insert(
                "organization".to_string(),
                serde_json::to_value(organization)?,
            );

            // Add flattened organization fields for easy querying
            obj.insert(
                "org_id".to_string(),
                JsonValue::String(organization.org_id.clone()),
            );
            obj.insert(
                "agent_group".to_string(),
                JsonValue::String(organization.agent_group.clone()),
            );

            if let Some(env) = &organization.environment {
                obj.insert("environment".to_string(), JsonValue::String(env.clone()));
            }
        }

        Ok(data)
    }

    /// Injects experiment context into data
    fn inject_experiment_context(
        &self,
        mut data: JsonValue,
        experiments: &[ExperimentContext],
    ) -> ProtocolResult<JsonValue> {
        if experiments.is_empty() {
            return Ok(data);
        }

        if let Some(obj) = data.as_object_mut() {
            // Add full experiment details
            obj.insert(
                "experiments".to_string(),
                serde_json::to_value(experiments)?,
            );

            // Add simplified experiment mapping for easy querying
            let active_experiments: Vec<&ExperimentContext> =
                experiments.iter().filter(|e| e.active).collect();
            if !active_experiments.is_empty() {
                let experiment_map: HashMap<String, JsonValue> = active_experiments
                    .iter()
                    .map(|exp| {
                        (
                            exp.experiment_id.clone(),
                            json!({
                                "variant": exp.variant,
                                "enrolled_at": exp.enrolled_at
                            }),
                        )
                    })
                    .collect();

                obj.insert(
                    "active_experiment_variants".to_string(),
                    serde_json::to_value(experiment_map)?,
                );

                // Add list of active experiment IDs for filtering
                let experiment_ids: Vec<&str> = active_experiments
                    .iter()
                    .map(|e| e.experiment_id.as_str())
                    .collect();

                obj.insert(
                    "active_experiment_ids".to_string(),
                    serde_json::to_value(experiment_ids)?,
                );
            }
        }

        Ok(data)
    }

    /// Adds common metadata to all transformations
    fn add_common_metadata(
        &self,
        mut data: JsonValue,
        target_protocol: EndpointType,
    ) -> ProtocolResult<JsonValue> {
        if let Some(obj) = data.as_object_mut() {
            // Add transformation metadata
            obj.insert(
                "transformation_timestamp".to_string(),
                serde_json::to_value(chrono::Utc::now())?,
            );
            obj.insert(
                "target_protocol".to_string(),
                serde_json::to_value(target_protocol)?,
            );

            if self.include_debug_metadata {
                obj.insert(
                    "sdk_version".to_string(),
                    JsonValue::String(env!("CARGO_PKG_VERSION").to_string()),
                );
                obj.insert("transformation_debug".to_string(), JsonValue::Bool(true));
            }
        }

        Ok(data)
    }

    /// Transforms data to tRPC Legacy format
    fn transform_to_trpc_legacy(&self, data: &TelemetryData) -> ProtocolResult<JsonValue> {
        debug!("Transforming data to tRPC Legacy format");

        // Start with the telemetry data
        let payload = data.serialize_json().map_err(|e| {
            ProtocolError::TransformationError(format!("Failed to serialize telemetry data: {}", e))
        })?;

        let mut json_data: JsonValue =
            serde_json::from_str(&payload).map_err(ProtocolError::SerializationError)?;

        // Inject organization context if available
        if let Some(org) = data.session.metadata.get("organization") {
            let org_context: OrganizationContext =
                serde_json::from_value(org.clone()).map_err(|e| {
                    ProtocolError::TransformationError(format!(
                        "Invalid organization context: {}",
                        e
                    ))
                })?;
            json_data = self.inject_organization_context(json_data, &org_context)?;
        }

        // Inject experiment context if available
        if let Some(experiments) = data.session.metadata.get("experiments") {
            let experiment_contexts: Vec<ExperimentContext> =
                serde_json::from_value(experiments.clone()).map_err(|e| {
                    ProtocolError::TransformationError(format!("Invalid experiment context: {}", e))
                })?;
            json_data = self.inject_experiment_context(json_data, &experiment_contexts)?;
        }

        // Add common metadata
        json_data = self.add_common_metadata(json_data, EndpointType::TrpcLegacy)?;

        // Wrap in tRPC format - the API key will be added by the protocol client
        let trpc_payload = json!({
            "json": json_data
        });

        Ok(trpc_payload)
    }

    /// Transforms data to REST API format
    fn transform_to_rest_api(&self, data: &TelemetryData) -> ProtocolResult<JsonValue> {
        debug!("Transforming data to REST API format");

        // Start with the telemetry data
        let payload = data.serialize_json().map_err(|e| {
            ProtocolError::TransformationError(format!("Failed to serialize telemetry data: {}", e))
        })?;

        let mut json_data: JsonValue =
            serde_json::from_str(&payload).map_err(ProtocolError::SerializationError)?;

        // Inject organization context if available
        if let Some(org) = data.session.metadata.get("organization") {
            let org_context: OrganizationContext =
                serde_json::from_value(org.clone()).map_err(|e| {
                    ProtocolError::TransformationError(format!(
                        "Invalid organization context: {}",
                        e
                    ))
                })?;
            json_data = self.inject_organization_context(json_data, &org_context)?;
        }

        // Inject experiment context if available
        if let Some(experiments) = data.session.metadata.get("experiments") {
            let experiment_contexts: Vec<ExperimentContext> =
                serde_json::from_value(experiments.clone()).map_err(|e| {
                    ProtocolError::TransformationError(format!("Invalid experiment context: {}", e))
                })?;
            json_data = self.inject_experiment_context(json_data, &experiment_contexts)?;
        }

        // Add REST API specific fields
        if let Some(obj) = json_data.as_object_mut() {
            obj.insert(
                "api_version".to_string(),
                JsonValue::String("v1".to_string()),
            );
            obj.insert("format".to_string(), JsonValue::String("rest".to_string()));
        }

        // Add common metadata
        json_data = self.add_common_metadata(json_data, EndpointType::RestApi)?;

        Ok(json_data)
    }

    /// Transforms data to Kinesis Stream format
    fn transform_to_kinesis_stream(&self, data: &TelemetryData) -> ProtocolResult<Vec<JsonValue>> {
        debug!("Transforming data to Kinesis Stream format");

        let payload = data.serialize_json().map_err(|e| {
            ProtocolError::TransformationError(format!("Failed to serialize telemetry data: {}", e))
        })?;

        let json_data: JsonValue =
            serde_json::from_str(&payload).map_err(ProtocolError::SerializationError)?;

        // Get organization and experiment contexts
        let org_context = data
            .session
            .metadata
            .get("organization")
            .and_then(|org| serde_json::from_value::<OrganizationContext>(org.clone()).ok());

        let experiment_contexts = data
            .session
            .metadata
            .get("experiments")
            .and_then(|exp| serde_json::from_value::<Vec<ExperimentContext>>(exp.clone()).ok())
            .unwrap_or_default();

        // Convert each event to a Kinesis record
        let mut kinesis_records = Vec::new();

        if let Some(events) = json_data.get("events").and_then(|e| e.as_array()) {
            for event in events {
                let mut kinesis_record = json!({
                    "record_type": "telemetry",
                    "session_id": data.session.id,
                    "timestamp": chrono::Utc::now(),
                    "event": event,
                    "session": data.session
                });

                // Add organization context
                if let Some(org) = &org_context {
                    if let Some(obj) = kinesis_record.as_object_mut() {
                        obj.insert(
                            "organization_id".to_string(),
                            JsonValue::String(org.org_id.clone()),
                        );
                        obj.insert(
                            "agent_group".to_string(),
                            JsonValue::String(org.agent_group.clone()),
                        );

                        if let Some(env) = &org.environment {
                            obj.insert("environment".to_string(), JsonValue::String(env.clone()));
                        }
                    }
                }

                // Add experiment context
                if !experiment_contexts.is_empty() {
                    if let Some(obj) = kinesis_record.as_object_mut() {
                        obj.insert(
                            "experiments".to_string(),
                            serde_json::to_value(&experiment_contexts)?,
                        );
                    }
                }

                // Add common metadata
                kinesis_record =
                    self.add_common_metadata(kinesis_record, EndpointType::KinesisStream)?;

                kinesis_records.push(kinesis_record);
            }
        }

        // If no events, create a single session record
        if kinesis_records.is_empty() {
            let mut session_record = json!({
                "record_type": "session",
                "session_id": data.session.id,
                "timestamp": chrono::Utc::now(),
                "session": data.session
            });

            // Add organization context
            if let Some(org) = &org_context {
                if let Some(obj) = session_record.as_object_mut() {
                    obj.insert(
                        "organization_id".to_string(),
                        JsonValue::String(org.org_id.clone()),
                    );
                    obj.insert(
                        "agent_group".to_string(),
                        JsonValue::String(org.agent_group.clone()),
                    );

                    if let Some(env) = &org.environment {
                        obj.insert("environment".to_string(), JsonValue::String(env.clone()));
                    }
                }
            }

            // Add experiment context
            if !experiment_contexts.is_empty() {
                if let Some(obj) = session_record.as_object_mut() {
                    obj.insert(
                        "experiments".to_string(),
                        serde_json::to_value(&experiment_contexts)?,
                    );
                }
            }

            session_record =
                self.add_common_metadata(session_record, EndpointType::KinesisStream)?;
            kinesis_records.push(session_record);
        }

        debug!("Created {} Kinesis records", kinesis_records.len());
        Ok(kinesis_records)
    }

    /// Transforms data to LakeFS Direct format
    fn transform_to_lakefs_direct(&self, data: &TelemetryData) -> ProtocolResult<JsonValue> {
        debug!("Transforming data to LakeFS Direct format");

        let payload = data.serialize_json().map_err(|e| {
            ProtocolError::TransformationError(format!("Failed to serialize telemetry data: {}", e))
        })?;

        let mut json_data: JsonValue =
            serde_json::from_str(&payload).map_err(ProtocolError::SerializationError)?;

        // Inject organization context if available
        if let Some(org) = data.session.metadata.get("organization") {
            let org_context: OrganizationContext =
                serde_json::from_value(org.clone()).map_err(|e| {
                    ProtocolError::TransformationError(format!(
                        "Invalid organization context: {}",
                        e
                    ))
                })?;
            json_data = self.inject_organization_context(json_data, &org_context)?;
        }

        // Inject experiment context if available
        if let Some(experiments) = data.session.metadata.get("experiments") {
            let experiment_contexts: Vec<ExperimentContext> =
                serde_json::from_value(experiments.clone()).map_err(|e| {
                    ProtocolError::TransformationError(format!("Invalid experiment context: {}", e))
                })?;
            json_data = self.inject_experiment_context(json_data, &experiment_contexts)?;
        }

        // Add LakeFS specific metadata
        if let Some(obj) = json_data.as_object_mut() {
            obj.insert(
                "lakefs_object_type".to_string(),
                JsonValue::String("telemetry_data".to_string()),
            );
            obj.insert(
                "data_version".to_string(),
                JsonValue::String("v1".to_string()),
            );

            // Add partitioning information for efficient querying
            let now = chrono::Utc::now();
            obj.insert("year".to_string(), JsonValue::Number(now.year().into()));
            obj.insert("month".to_string(), JsonValue::Number(now.month().into()));
            obj.insert("day".to_string(), JsonValue::Number(now.day().into()));
            obj.insert("hour".to_string(), JsonValue::Number(now.hour().into()));
        }

        // Add common metadata
        json_data = self.add_common_metadata(json_data, EndpointType::LakefsDirect)?;

        Ok(json_data)
    }
}

impl Default for DefaultDataTransformer {
    fn default() -> Self {
        Self::new()
    }
}

impl DataTransformer for DefaultDataTransformer {
    fn transform_telemetry_data(
        &self,
        data: &TelemetryData,
        target_protocol: EndpointType,
    ) -> ProtocolResult<Vec<u8>> {
        let transformed_data = match target_protocol {
            EndpointType::TrpcLegacy => self.transform_to_trpc_legacy(data)?,
            EndpointType::RestApi => self.transform_to_rest_api(data)?,
            EndpointType::KinesisStream => {
                let records = self.transform_to_kinesis_stream(data)?;
                // For single telemetry data, take the first record
                records.into_iter().next().unwrap_or_else(|| json!({}))
            }
            EndpointType::LakefsDirect => self.transform_to_lakefs_direct(data)?,
        };

        let serialized =
            serde_json::to_vec(&transformed_data).map_err(ProtocolError::SerializationError)?;

        debug!(
            "Transformed telemetry data to {} format ({} bytes)",
            target_protocol.to_string(),
            serialized.len()
        );

        Ok(serialized)
    }

    fn transform_agent_run_data(
        &self,
        data: &JsonValue,
        target_protocol: EndpointType,
    ) -> ProtocolResult<Vec<u8>> {
        let mut agent_data = data.clone();

        // Add agent run specific metadata
        if let Some(obj) = agent_data.as_object_mut() {
            obj.insert(
                "data_type".to_string(),
                JsonValue::String("agent_run".to_string()),
            );
        }

        // Transform based on protocol
        let transformed_data = match target_protocol {
            EndpointType::TrpcLegacy => {
                // Wrap in tRPC format
                json!({
                    "json": agent_data
                })
            }
            EndpointType::RestApi => {
                // Add REST API metadata
                if let Some(obj) = agent_data.as_object_mut() {
                    obj.insert(
                        "api_version".to_string(),
                        JsonValue::String("v1".to_string()),
                    );
                    obj.insert(
                        "endpoint".to_string(),
                        JsonValue::String("agent_runs".to_string()),
                    );
                }
                agent_data
            }
            EndpointType::KinesisStream => {
                // Convert to Kinesis record format
                json!({
                    "record_type": "agent_run",
                    "timestamp": chrono::Utc::now(),
                    "data": agent_data
                })
            }
            EndpointType::LakefsDirect => {
                // Add LakeFS metadata
                if let Some(obj) = agent_data.as_object_mut() {
                    obj.insert(
                        "lakefs_object_type".to_string(),
                        JsonValue::String("agent_run".to_string()),
                    );

                    let now = chrono::Utc::now();
                    obj.insert("year".to_string(), JsonValue::Number(now.year().into()));
                    obj.insert("month".to_string(), JsonValue::Number(now.month().into()));
                    obj.insert("day".to_string(), JsonValue::Number(now.day().into()));
                }
                agent_data
            }
        };

        // Add common metadata
        let final_data = self.add_common_metadata(transformed_data, target_protocol.clone())?;

        let serialized =
            serde_json::to_vec(&final_data).map_err(ProtocolError::SerializationError)?;

        debug!(
            "Transformed agent run data to {} format ({} bytes)",
            target_protocol.to_string(),
            serialized.len()
        );

        Ok(serialized)
    }

    fn transform_batch_data(
        &self,
        records: &[JsonValue],
        target_protocol: EndpointType,
    ) -> ProtocolResult<Vec<u8>> {
        if records.is_empty() {
            return Ok(Vec::new());
        }

        let transformed_data = match target_protocol {
            EndpointType::TrpcLegacy => {
                // Wrap records in tRPC batch format
                json!({
                    "json": {
                        "records": records,
                        "batch_size": records.len(),
                        "batch_timestamp": chrono::Utc::now()
                    }
                })
            }
            EndpointType::RestApi => {
                // REST API batch format
                json!({
                    "records": records,
                    "batch_size": records.len(),
                    "batch_timestamp": chrono::Utc::now(),
                    "api_version": "v1",
                    "endpoint": "batch"
                })
            }
            EndpointType::KinesisStream => {
                // Convert each record to Kinesis format
                let kinesis_records: Result<Vec<JsonValue>, ProtocolError> = records
                    .iter()
                    .enumerate()
                    .map(|(i, record)| -> Result<JsonValue, ProtocolError> {
                        Ok(json!({
                            "record_type": "batch",
                            "batch_index": i,
                            "timestamp": chrono::Utc::now(),
                            "data": record
                        }))
                    })
                    .collect();

                json!({
                    "records": kinesis_records?,
                    "batch_metadata": {
                        "total_records": records.len(),
                        "batch_timestamp": chrono::Utc::now()
                    }
                })
            }
            EndpointType::LakefsDirect => {
                // LakeFS batch format with partitioning metadata
                let now = chrono::Utc::now();
                json!({
                    "records": records,
                    "batch_size": records.len(),
                    "batch_timestamp": now,
                    "lakefs_object_type": "batch_data",
                    "year": now.year(),
                    "month": now.month(),
                    "day": now.day(),
                    "hour": now.hour()
                })
            }
        };

        // Add common metadata
        let final_data = self.add_common_metadata(transformed_data, target_protocol.clone())?;

        let serialized =
            serde_json::to_vec(&final_data).map_err(ProtocolError::SerializationError)?;

        debug!(
            "Transformed batch data ({} records) to {} format ({} bytes)",
            records.len(),
            target_protocol.to_string(),
            serialized.len()
        );

        Ok(serialized)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{EventBuilder, EventLevel, EventMetadata, Session};

    fn create_test_telemetry_data() -> TelemetryData {
        let mut session = Session::new();

        // Add organization context to session metadata
        let org_context = OrganizationContext::new("org_123", "ml_agents").with_environment("test");
        session.metadata.insert(
            "organization".to_string(),
            serde_json::to_value(&org_context).unwrap(),
        );

        // Add experiment context to session metadata
        let experiment =
            ExperimentContext::new("exp_456", "variant_a").with_name("Test Experiment");
        session.metadata.insert(
            "experiments".to_string(),
            serde_json::to_value(vec![experiment]).unwrap(),
        );

        let mut data = TelemetryData::new(session);

        let mut event_metadata = EventMetadata::new();
        event_metadata.custom_data.insert(
            "key".to_string(),
            serde_json::Value::String("value".to_string()),
        );

        let event = EventBuilder::new("test_event".to_string())
            .level(EventLevel::Info)
            .metadata(event_metadata)
            .build();

        data.add_event(event);
        data
    }

    #[test]
    fn test_transformer_creation() {
        let transformer = DefaultDataTransformer::new();
        assert!(!transformer.include_debug_metadata);

        let transformer_debug = DefaultDataTransformer::new().with_debug_metadata();
        assert!(transformer_debug.include_debug_metadata);
    }

    #[test]
    fn test_inject_organization_context() {
        let transformer = DefaultDataTransformer::new();
        let org_context = OrganizationContext::new("org_123", "ml_agents").with_environment("test");

        let data = json!({ "test": "data" });
        let result = transformer
            .inject_organization_context(data, &org_context)
            .unwrap();

        assert!(result.get("organization").is_some());
        assert_eq!(result.get("org_id").unwrap(), "org_123");
        assert_eq!(result.get("agent_group").unwrap(), "ml_agents");
        assert_eq!(result.get("environment").unwrap(), "test");
        assert_eq!(result.get("test").unwrap(), "data");
    }

    #[test]
    fn test_inject_experiment_context() {
        let transformer = DefaultDataTransformer::new();
        let experiment =
            ExperimentContext::new("exp_123", "variant_a").with_name("Test Experiment");
        let experiments = vec![experiment];

        let data = json!({ "test": "data" });
        let result = transformer
            .inject_experiment_context(data, &experiments)
            .unwrap();

        assert!(result.get("experiments").is_some());
        assert!(result.get("active_experiment_variants").is_some());
        assert!(result.get("active_experiment_ids").is_some());
        assert_eq!(result.get("test").unwrap(), "data");

        let experiment_ids: Vec<String> =
            serde_json::from_value(result.get("active_experiment_ids").unwrap().clone()).unwrap();
        assert_eq!(experiment_ids, vec!["exp_123"]);
    }

    #[test]
    fn test_inject_experiment_context_empty() {
        let transformer = DefaultDataTransformer::new();
        let experiments = vec![];

        let data = json!({ "test": "data" });
        let result = transformer
            .inject_experiment_context(data, &experiments)
            .unwrap();

        assert!(!result.get("experiments").is_some());
        assert_eq!(result.get("test").unwrap(), "data");
    }

    #[test]
    fn test_add_common_metadata() {
        let transformer = DefaultDataTransformer::new().with_debug_metadata();
        let data = json!({ "test": "data" });

        let result = transformer
            .add_common_metadata(data, EndpointType::RestApi)
            .unwrap();

        assert!(result.get("transformation_timestamp").is_some());
        assert_eq!(result.get("target_protocol").unwrap(), "RestApi");
        assert_eq!(result.get("transformation_debug").unwrap(), true);
        assert!(result.get("sdk_version").is_some());
    }

    #[test]
    fn test_transform_to_trpc_legacy() {
        let transformer = DefaultDataTransformer::new();
        let data = create_test_telemetry_data();

        let result = transformer.transform_to_trpc_legacy(&data).unwrap();

        assert!(result.get("json").is_some());
        let json_data = result.get("json").unwrap();

        assert!(json_data.get("organization").is_some());
        assert!(json_data.get("experiments").is_some());
        assert!(json_data.get("transformation_timestamp").is_some());
        assert_eq!(json_data.get("target_protocol").unwrap(), "TrpcLegacy");
    }

    #[test]
    fn test_transform_to_rest_api() {
        let transformer = DefaultDataTransformer::new();
        let data = create_test_telemetry_data();

        let result = transformer.transform_to_rest_api(&data).unwrap();

        assert!(result.get("organization").is_some());
        assert!(result.get("experiments").is_some());
        assert_eq!(result.get("api_version").unwrap(), "v1");
        assert_eq!(result.get("format").unwrap(), "rest");
        assert_eq!(result.get("target_protocol").unwrap(), "RestApi");
    }

    #[test]
    fn test_transform_to_kinesis_stream() {
        let transformer = DefaultDataTransformer::new();
        let data = create_test_telemetry_data();

        let records = transformer.transform_to_kinesis_stream(&data).unwrap();

        assert!(!records.is_empty());
        let first_record = &records[0];

        assert_eq!(first_record.get("record_type").unwrap(), "telemetry");
        assert!(first_record.get("session_id").is_some());
        assert!(first_record.get("organization_id").is_some());
        assert!(first_record.get("experiments").is_some());
        assert_eq!(
            first_record.get("target_protocol").unwrap(),
            "KinesisStream"
        );
    }

    #[test]
    fn test_transform_to_lakefs_direct() {
        let transformer = DefaultDataTransformer::new();
        let data = create_test_telemetry_data();

        let result = transformer.transform_to_lakefs_direct(&data).unwrap();

        assert!(result.get("organization").is_some());
        assert!(result.get("experiments").is_some());
        assert_eq!(result.get("lakefs_object_type").unwrap(), "telemetry_data");
        assert_eq!(result.get("data_version").unwrap(), "v1");
        assert!(result.get("year").is_some());
        assert!(result.get("month").is_some());
        assert!(result.get("day").is_some());
        assert!(result.get("hour").is_some());
        assert_eq!(result.get("target_protocol").unwrap(), "LakefsDirect");
    }

    #[test]
    fn test_transform_telemetry_data_all_protocols() {
        let transformer = DefaultDataTransformer::new();
        let data = create_test_telemetry_data();

        // Test all protocols
        let protocols = [
            EndpointType::TrpcLegacy,
            EndpointType::RestApi,
            EndpointType::KinesisStream,
            EndpointType::LakefsDirect,
        ];

        for protocol in protocols.iter() {
            let result = transformer.transform_telemetry_data(&data, protocol.clone());
            assert!(
                result.is_ok(),
                "Failed to transform for protocol: {:?}",
                protocol
            );

            let bytes = result.unwrap();
            assert!(
                !bytes.is_empty(),
                "Empty result for protocol: {:?}",
                protocol
            );
        }
    }

    #[test]
    fn test_transform_agent_run_data() {
        let transformer = DefaultDataTransformer::new();
        let agent_data = json!({
            "agent_id": "agent_123",
            "run_id": "run_456",
            "status": "completed"
        });

        let result = transformer
            .transform_agent_run_data(&agent_data, EndpointType::RestApi)
            .unwrap();
        let parsed: JsonValue = serde_json::from_slice(&result).unwrap();

        assert_eq!(parsed.get("data_type").unwrap(), "agent_run");
        assert_eq!(parsed.get("api_version").unwrap(), "v1");
        assert_eq!(parsed.get("endpoint").unwrap(), "agent_runs");
        assert_eq!(parsed.get("agent_id").unwrap(), "agent_123");
    }

    #[test]
    fn test_transform_batch_data() {
        let transformer = DefaultDataTransformer::new();
        let records = vec![
            json!({ "id": 1, "data": "first" }),
            json!({ "id": 2, "data": "second" }),
        ];

        let result = transformer
            .transform_batch_data(&records, EndpointType::RestApi)
            .unwrap();
        let parsed: JsonValue = serde_json::from_slice(&result).unwrap();

        assert_eq!(parsed.get("batch_size").unwrap(), 2);
        assert_eq!(parsed.get("api_version").unwrap(), "v1");
        assert_eq!(parsed.get("endpoint").unwrap(), "batch");

        let parsed_records = parsed.get("records").unwrap().as_array().unwrap();
        assert_eq!(parsed_records.len(), 2);
        assert_eq!(parsed_records[0].get("id").unwrap(), 1);
        assert_eq!(parsed_records[1].get("id").unwrap(), 2);
    }

    #[test]
    fn test_transform_empty_batch_data() {
        let transformer = DefaultDataTransformer::new();
        let records: Vec<JsonValue> = vec![];

        let result = transformer
            .transform_batch_data(&records, EndpointType::RestApi)
            .unwrap();
        assert!(result.is_empty());
    }
}
