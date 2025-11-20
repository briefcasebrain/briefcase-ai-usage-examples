use crate::{Event, Session, TelemetryConfig, TelemetryData};
use anyhow::Result;
use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::time::{interval, Duration};
use tracing::{debug, error, info, warn};

#[derive(Clone)]
pub struct TelemetryClient {
    config: TelemetryConfig,
    session: Session,
    http_client: reqwest::Client,
    buffer: Arc<Mutex<Vec<Event>>>,
}

impl TelemetryClient {
    pub fn new(config: TelemetryConfig) -> Result<Self> {
        let session = Session::new();
        let http_client = reqwest::Client::builder().timeout(config.timeout).build()?;

        Ok(Self {
            config,
            session,
            http_client,
            buffer: Arc::new(Mutex::new(Vec::new())),
        })
    }

    pub fn with_session(mut self, session: Session) -> Self {
        self.session = session;
        self
    }

    pub async fn track_event(&self, event: Event) -> Result<()> {
        if !self.config.enabled {
            debug!("Telemetry disabled, skipping event: {}", event.name);
            return Ok(());
        }

        debug!("Tracking event: {}", event.name);
        let mut buffer = self.buffer.lock().await;
        buffer.push(event);

        if buffer.len() >= self.config.batch_size {
            let events = buffer.drain(..).collect();
            drop(buffer);
            self.flush_events(events).await?;
        }

        Ok(())
    }

    pub async fn flush(&self) -> Result<()> {
        let mut buffer = self.buffer.lock().await;
        if buffer.is_empty() {
            return Ok(());
        }

        let events = buffer.drain(..).collect();
        drop(buffer);
        self.flush_events(events).await
    }

    async fn flush_events(&self, events: Vec<Event>) -> Result<()> {
        if events.is_empty() {
            return Ok(());
        }

        info!("Flushing {} events", events.len());

        let mut telemetry_data = TelemetryData::new(self.session.clone());
        telemetry_data.add_events(events);

        let payload = telemetry_data.serialize_json()?;

        for attempt in 1..=self.config.retry_attempts {
            match self.send_telemetry(&payload).await {
                Ok(_) => {
                    info!("Successfully sent telemetry data");
                    return Ok(());
                }
                Err(e) => {
                    warn!(
                        "Attempt {}/{} failed: {}",
                        attempt, self.config.retry_attempts, e
                    );
                    if attempt < self.config.retry_attempts {
                        tokio::time::sleep(Duration::from_millis(100 * attempt as u64)).await;
                    }
                }
            }
        }

        error!(
            "Failed to send telemetry data after {} attempts",
            self.config.retry_attempts
        );
        Err(anyhow::anyhow!("Failed to send telemetry data"))
    }

    async fn send_telemetry(&self, payload: &str) -> Result<()> {
        // Parse the payload to add apiKey and wrap in correct tRPC format
        let mut payload_data = serde_json::from_str::<serde_json::Value>(payload)?;

        // Add apiKey to the payload data
        if let Some(obj) = payload_data.as_object_mut() {
            obj.insert(
                "apiKey".to_string(),
                serde_json::Value::String(self.config.api_key.clone()),
            );
        }

        // Wrap in correct tRPC format (just "json", not "0.json")
        let trpc_payload = serde_json::json!({
            "json": payload_data
        });

        // Determine authentication method based on API key format
        let auth_header = if self.config.api_key.starts_with("bca_") {
            // API Key authentication for telemetry ingestion
            format!("ApiKey {}", self.config.api_key)
        } else {
            // Bearer token authentication
            format!("Bearer {}", self.config.api_key)
        };

        let response = self
            .http_client
            .post(&self.config.endpoint)
            .header("Content-Type", "application/json")
            .header("Authorization", auth_header)
            .header(
                "User-Agent",
                format!("briefcase-ai-telemetry-sdk/{}", env!("CARGO_PKG_VERSION")),
            )
            .json(&trpc_payload)
            .send()
            .await?;

        if response.status().is_success() {
            debug!("Telemetry sent successfully: {}", response.status());

            // Parse tRPC response to check for errors
            let response_text = response.text().await?;
            if let Ok(trpc_response) = serde_json::from_str::<serde_json::Value>(&response_text) {
                if let Some(error) = trpc_response.get("0").and_then(|v| v.get("error")) {
                    let error_msg = error
                        .get("message")
                        .and_then(|m| m.as_str())
                        .unwrap_or("Unknown tRPC error");
                    return Err(anyhow::anyhow!("tRPC error: {}", error_msg));
                }
            }
            Ok(())
        } else {
            let status = response.status();

            // Handle rate limiting before consuming response
            let retry_after = if status == 429 {
                response
                    .headers()
                    .get("retry-after")
                    .and_then(|h| h.to_str().ok())
                    .and_then(|s| s.parse::<u64>().ok())
            } else {
                None
            };

            let error_body = response.text().await.unwrap_or_default();

            if let Some(retry_after_value) = retry_after {
                return Err(anyhow::anyhow!(
                    "Rate limited. Retry after {} seconds",
                    retry_after_value
                ));
            }

            Err(anyhow::anyhow!("HTTP error {}: {}", status, error_body))
        }
    }

    pub async fn start_background_flush(&self) -> Result<()> {
        let client = self.clone();
        let flush_interval = self.config.flush_interval;

        tokio::spawn(async move {
            let mut interval = interval(flush_interval);

            loop {
                interval.tick().await;
                if let Err(e) = client.flush().await {
                    error!("Background flush failed: {}", e);
                }
            }
        });

        info!(
            "Started background flush with interval: {:?}",
            flush_interval
        );
        Ok(())
    }

    pub fn session(&self) -> &Session {
        &self.session
    }

    pub async fn record_agent_run(&self, agent_run_data: &serde_json::Value) -> Result<()> {
        if !self.config.enabled {
            debug!("Telemetry disabled, skipping agent run recording");
            return Ok(());
        }

        // Construct agent run recording endpoint
        let agent_run_endpoint = self
            .config
            .endpoint
            .replace("/api/trpc/ingest.telemetry", "/api/trpc/agents.recordRun");

        // Add apiKey to agent run data and wrap in correct tRPC format
        let mut agent_data = agent_run_data.clone();
        if let Some(obj) = agent_data.as_object_mut() {
            obj.insert(
                "apiKey".to_string(),
                serde_json::Value::String(self.config.api_key.clone()),
            );
        }

        let trpc_payload = serde_json::json!({
            "json": agent_data
        });

        // Determine authentication method
        let auth_header = if self.config.api_key.starts_with("bca_") {
            format!("ApiKey {}", self.config.api_key)
        } else {
            format!("Bearer {}", self.config.api_key)
        };

        for attempt in 1..=self.config.retry_attempts {
            match self
                .http_client
                .post(&agent_run_endpoint)
                .header("Content-Type", "application/json")
                .header("Authorization", &auth_header)
                .header(
                    "User-Agent",
                    format!("briefcase-ai-telemetry-sdk/{}", env!("CARGO_PKG_VERSION")),
                )
                .json(&trpc_payload)
                .send()
                .await
            {
                Ok(response) => {
                    if response.status().is_success() {
                        debug!("Agent run recorded successfully: {}", response.status());
                        return Ok(());
                    } else {
                        let status = response.status();

                        // Handle rate limiting before consuming response
                        let retry_after = if status == 429 {
                            response
                                .headers()
                                .get("retry-after")
                                .and_then(|h| h.to_str().ok())
                                .and_then(|s| s.parse::<u64>().ok())
                        } else {
                            None
                        };

                        let error_body = response.text().await.unwrap_or_default();

                        if let Some(retry_after_value) = retry_after {
                            tokio::time::sleep(Duration::from_secs(retry_after_value)).await;
                            continue;
                        }

                        if attempt < self.config.retry_attempts {
                            tokio::time::sleep(Duration::from_millis(100 * attempt as u64)).await;
                        } else {
                            return Err(anyhow::anyhow!(
                                "Failed to record agent run: HTTP {} {}",
                                status,
                                error_body
                            ));
                        }
                    }
                }
                Err(e) => {
                    if attempt < self.config.retry_attempts {
                        tokio::time::sleep(Duration::from_millis(100 * attempt as u64)).await;
                    } else {
                        return Err(anyhow::anyhow!("Failed to record agent run: {}", e));
                    }
                }
            }
        }

        Err(anyhow::anyhow!(
            "Failed to record agent run after {} attempts",
            self.config.retry_attempts
        ))
    }

    pub fn config(&self) -> &TelemetryConfig {
        &self.config
    }

    pub async fn buffer_size(&self) -> usize {
        self.buffer.lock().await.len()
    }

    pub async fn send_batch(&self, records: Vec<serde_json::Value>) -> Result<()> {
        if !self.config.enabled {
            debug!("Telemetry disabled, skipping batch send");
            return Ok(());
        }

        if records.is_empty() {
            return Ok(());
        }

        info!("Sending batch of {} records", records.len());

        // Construct batch endpoint URL
        let batch_endpoint = self
            .config
            .endpoint
            .replace("/api/trpc/ingest.telemetry", "/api/trpc/ingest.batch");

        // Create batch payload with apiKey
        let batch_payload = serde_json::json!({
            "json": {
                "apiKey": self.config.api_key,
                "records": records
            }
        });

        // Determine authentication method
        let auth_header = if self.config.api_key.starts_with("bca_") {
            format!("ApiKey {}", self.config.api_key)
        } else {
            format!("Bearer {}", self.config.api_key)
        };

        for attempt in 1..=self.config.retry_attempts {
            match self
                .http_client
                .post(&batch_endpoint)
                .header("Content-Type", "application/json")
                .header("Authorization", &auth_header)
                .header(
                    "User-Agent",
                    format!("briefcase-ai-telemetry-sdk/{}", env!("CARGO_PKG_VERSION")),
                )
                .json(&batch_payload)
                .send()
                .await
            {
                Ok(response) => {
                    if response.status().is_success() {
                        info!("Batch sent successfully: {}", response.status());
                        return Ok(());
                    } else {
                        let status = response.status();
                        let error_body = response.text().await.unwrap_or_default();

                        if attempt < self.config.retry_attempts {
                            warn!(
                                "Batch attempt {}/{} failed: HTTP {}",
                                attempt, self.config.retry_attempts, status
                            );
                            tokio::time::sleep(Duration::from_millis(100 * attempt as u64)).await;
                        } else {
                            return Err(anyhow::anyhow!(
                                "Failed to send batch: HTTP {} {}",
                                status,
                                error_body
                            ));
                        }
                    }
                }
                Err(e) => {
                    if attempt < self.config.retry_attempts {
                        warn!(
                            "Batch attempt {}/{} failed: {}",
                            attempt, self.config.retry_attempts, e
                        );
                        tokio::time::sleep(Duration::from_millis(100 * attempt as u64)).await;
                    } else {
                        return Err(anyhow::anyhow!("Failed to send batch: {}", e));
                    }
                }
            }
        }

        Err(anyhow::anyhow!(
            "Failed to send batch after {} attempts",
            self.config.retry_attempts
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{EventBuilder, EventLevel};
    use std::time::Duration;

    fn create_test_config() -> TelemetryConfig {
        TelemetryConfig::new("test_key".to_string())
            .with_endpoint("http://localhost:8080/telemetry".to_string())
            .with_timeout(Duration::from_secs(1))
            .with_batch_size(2)
    }

    #[tokio::test]
    async fn test_client_creation() {
        let config = create_test_config();
        let client = TelemetryClient::new(config).unwrap();

        assert_eq!(client.config.api_key, "test_key");
        assert_eq!(client.buffer_size().await, 0);
    }

    #[tokio::test]
    async fn test_track_event() {
        let config = create_test_config();
        let client = TelemetryClient::new(config).unwrap();

        let event = EventBuilder::new("test_event".to_string())
            .level(EventLevel::Info)
            .build();

        let result = client.track_event(event).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_disabled_client() {
        let config = create_test_config().with_enabled(false);
        let client = TelemetryClient::new(config).unwrap();

        let event = EventBuilder::new("test_event".to_string()).build();
        let result = client.track_event(event).await;

        assert!(result.is_ok());
        assert_eq!(client.buffer_size().await, 0);
    }

    #[tokio::test]
    async fn test_flush_empty_buffer() {
        let config = create_test_config();
        let client = TelemetryClient::new(config).unwrap();

        let result = client.flush().await;
        assert!(result.is_ok());
    }
}
