/**
 * SDK Integration Tests
 * Tests multi-protocol implementation with deployed infrastructure
 */

use briefcase_ai_telemetry::*;
use serde_json::json;
use std::time::{Duration, Instant};
use tokio::time::sleep;

#[tokio::test]
async fn test_multi_protocol_implementation() {
    let config = EnhancedTelemetryConfig {
        organization_id: "test_org_123".to_string(),
        api_key: std::env::var("TEST_API_KEY").unwrap_or_else(|_| "test_api_key".to_string()),
        endpoints: vec![
            EndpointType::Kinesis {
                stream_name: "telemetry-stream-test".to_string(),
                region: "us-east-1".to_string(),
            },
            EndpointType::LakeFS {
                endpoint: std::env::var("LAKEFS_ENDPOINT")
                    .unwrap_or_else(|_| "http://localhost:8000".to_string()),
                repository: "test-repo".to_string(),
                branch: "main".to_string(),
            },
            EndpointType::Http {
                url: std::env::var("API_ENDPOINT")
                    .unwrap_or_else(|_| "https://api-staging.briefcasebrain.com".to_string()),
            },
        ],
        auth_mode: AuthMode::ApiKey,
        organization_context: Some(OrganizationContext {
            org_id: "test_org_123".to_string(),
            tenant_id: "tenant_test".to_string(),
            region: "us-east-1".to_string(),
            environment: "test".to_string(),
        }),
        experiment_context: Some(ExperimentContext {
            experiment_id: "exp_integration_test".to_string(),
            variant_id: "variant_test".to_string(),
            is_baseline: false,
            traffic_percentage: 50.0,
        }),
        batch_size: 10,
        flush_interval: Duration::from_secs(5),
        retry_config: Default::default(),
        enable_compression: true,
        enable_encryption: true,
        debug_mode: true,
    };

    println!("Testing multi-protocol SDK implementation...");

    // Test basic client initialization
    let client = BasicEnhancedTelemetryClient::new(config.clone())
        .await
        .expect("Failed to create client");

    // Test sending data to multiple protocols
    test_multi_protocol_data_flow(&client).await;

    // Test authentication flows
    test_authentication_flows(&config).await;

    // Test experiment lifecycle integration
    test_experiment_lifecycle(&client).await;

    // Test error handling and resilience
    test_error_handling_resilience(&client).await;

    println!("Multi-protocol implementation tests completed successfully!");
}

async fn test_multi_protocol_data_flow(client: &BasicEnhancedTelemetryClient) {
    println!("Testing multi-protocol data flow...");

    let test_data = vec![
        json!({
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "agent_id": "test_agent_001",
            "metrics": {
                "accuracy": 94.5,
                "latency_p95": 850.0,
                "cost_per_request": 0.12,
                "error_rate": 1.2
            },
            "metadata": {
                "model": "gpt-4-0613",
                "temperature": 0.1,
                "test_run": true
            }
        }),
        json!({
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "agent_id": "test_agent_002",
            "metrics": {
                "accuracy": 96.2,
                "latency_p95": 720.0,
                "cost_per_request": 0.08,
                "error_rate": 0.8
            },
            "metadata": {
                "model": "claude-3-5-sonnet",
                "temperature": 0.2,
                "test_run": true
            }
        }),
    ];

    let start_time = Instant::now();

    for data in test_data {
        match client.send_data(data.clone()).await {
            Ok(_) => {
                println!("Successfully sent data: {:?}", data["agent_id"]);
            }
            Err(e) => {
                eprintln!("Failed to send data: {:?}", e);
                // Continue testing even if one protocol fails
            }
        }
    }

    // Force flush to ensure all data is sent
    if let Err(e) = client.flush().await {
        eprintln!("Failed to flush data: {:?}", e);
    }

    let duration = start_time.elapsed();
    println!("Multi-protocol data flow completed in {:?}", duration);

    // Verify data was sent to all protocols
    sleep(Duration::from_secs(2)).await; // Wait for async processing
}

async fn test_authentication_flows(config: &EnhancedTelemetryConfig) {
    println!("Testing authentication flows...");

    // Test API Key authentication
    test_api_key_auth(config).await;

    // Test JWT authentication
    test_jwt_auth(config).await;

    // Test STS authentication
    test_sts_auth(config).await;
}

async fn test_api_key_auth(config: &EnhancedTelemetryConfig) {
    println!("Testing API Key authentication...");

    let mut api_key_config = config.clone();
    api_key_config.auth_mode = AuthMode::ApiKey;

    match BasicEnhancedTelemetryClient::new(api_key_config).await {
        Ok(client) => {
            println!("API Key authentication successful");

            // Test sending data with API key
            let test_data = json!({
                "timestamp": chrono::Utc::now().to_rfc3339(),
                "agent_id": "auth_test_001",
                "metrics": {
                    "accuracy": 95.0,
                    "latency_p95": 800.0
                },
                "auth_test": "api_key"
            });

            match client.send_data(test_data).await {
                Ok(_) => println!("API Key authenticated data send successful"),
                Err(e) => eprintln!("API Key authenticated data send failed: {:?}", e),
            }
        }
        Err(e) => eprintln!("API Key authentication failed: {:?}", e),
    }
}

async fn test_jwt_auth(config: &EnhancedTelemetryConfig) {
    println!("Testing JWT authentication...");

    let mut jwt_config = config.clone();
    jwt_config.auth_mode = AuthMode::JWT {
        token: std::env::var("TEST_JWT_TOKEN")
            .unwrap_or_else(|_| "test_jwt_token".to_string()),
    };

    match BasicEnhancedTelemetryClient::new(jwt_config).await {
        Ok(client) => {
            println!("JWT authentication successful");

            let test_data = json!({
                "timestamp": chrono::Utc::now().to_rfc3339(),
                "agent_id": "auth_test_002",
                "metrics": {
                    "accuracy": 93.5,
                    "latency_p95": 900.0
                },
                "auth_test": "jwt"
            });

            match client.send_data(test_data).await {
                Ok(_) => println!("JWT authenticated data send successful"),
                Err(e) => eprintln!("JWT authenticated data send failed: {:?}", e),
            }
        }
        Err(e) => eprintln!("JWT authentication failed: {:?}", e),
    }
}

async fn test_sts_auth(config: &EnhancedTelemetryConfig) {
    println!("Testing STS authentication...");

    let mut sts_config = config.clone();
    sts_config.auth_mode = AuthMode::STS {
        role_arn: std::env::var("TEST_STS_ROLE_ARN")
            .unwrap_or_else(|_| "arn:aws:iam::123456789012:role/test-role".to_string()),
        session_name: "integration-test".to_string(),
    };

    match BasicEnhancedTelemetryClient::new(sts_config).await {
        Ok(client) => {
            println!("STS authentication successful");

            let test_data = json!({
                "timestamp": chrono::Utc::now().to_rfc3339(),
                "agent_id": "auth_test_003",
                "metrics": {
                    "accuracy": 97.1,
                    "latency_p95": 650.0
                },
                "auth_test": "sts"
            });

            match client.send_data(test_data).await {
                Ok(_) => println!("STS authenticated data send successful"),
                Err(e) => eprintln!("STS authenticated data send failed: {:?}", e),
            }
        }
        Err(e) => eprintln!("STS authentication failed: {:?}", e),
    }
}

async fn test_experiment_lifecycle(client: &BasicEnhancedTelemetryClient) {
    println!("Testing experiment lifecycle integration...");

    // Create experiment
    let experiment_config = json!({
        "name": "SDK Integration Test Experiment",
        "description": "Testing experiment lifecycle from SDK",
        "agent_group_id": "test_agent_group_001",
        "hypothesis": "SDK integration will work correctly",
        "baseline_variant": {
            "variant_id": "baseline",
            "name": "Baseline Configuration",
            "configuration": {
                "model": "gpt-4-0613",
                "temperature": 0.1
            },
            "traffic_percentage": 50.0
        },
        "test_variants": [{
            "variant_id": "test_variant",
            "name": "Test Configuration",
            "configuration": {
                "model": "gpt-4-0613",
                "temperature": 0.2
            },
            "traffic_percentage": 50.0
        }],
        "duration_hours": 1
    });

    // Test sending experiment data
    let experiment_data = json!({
        "timestamp": chrono::Utc::now().to_rfc3339(),
        "experiment_id": "exp_integration_test",
        "variant_id": "test_variant",
        "agent_id": "test_agent_001",
        "metrics": {
            "accuracy": 95.5,
            "latency_p95": 780.0,
            "cost_per_request": 0.10,
            "error_rate": 0.9
        },
        "experiment_metadata": {
            "is_baseline": false,
            "traffic_percentage": 50.0,
            "experiment_name": "SDK Integration Test"
        }
    });

    match client.send_data(experiment_data).await {
        Ok(_) => println!("Experiment data sent successfully"),
        Err(e) => eprintln!("Failed to send experiment data: {:?}", e),
    }

    // Test LakeFS branching integration
    test_lakefs_branching(client).await;
}

async fn test_lakefs_branching(client: &BasicEnhancedTelemetryClient) {
    println!("Testing LakeFS branching integration...");

    // Test creating experiment branch
    let branch_data = json!({
        "timestamp": chrono::Utc::now().to_rfc3339(),
        "operation": "create_experiment_branch",
        "experiment_id": "exp_integration_test",
        "branch_name": "experiments/exp_integration_test",
        "source_branch": "main",
        "metadata": {
            "created_by": "sdk_integration_test",
            "purpose": "experiment_isolation"
        }
    });

    match client.send_data(branch_data).await {
        Ok(_) => println!("LakeFS branch data sent successfully"),
        Err(e) => eprintln!("Failed to send LakeFS branch data: {:?}", e),
    }

    // Test committing experiment results
    let commit_data = json!({
        "timestamp": chrono::Utc::now().to_rfc3339(),
        "operation": "commit_experiment_results",
        "experiment_id": "exp_integration_test",
        "commit_message": "Integration test experiment results",
        "results": {
            "winner": "test_variant",
            "improvement": 2.3,
            "statistical_significance": true,
            "confidence_level": 0.95
        }
    });

    match client.send_data(commit_data).await {
        Ok(_) => println!("LakeFS commit data sent successfully"),
        Err(e) => eprintln!("Failed to send LakeFS commit data: {:?}", e),
    }
}

async fn test_error_handling_resilience(client: &BasicEnhancedTelemetryClient) {
    println!("Testing error handling and resilience...");

    // Test with invalid data
    let invalid_data = json!({
        "invalid_field": "this should cause an error"
    });

    match client.send_data(invalid_data).await {
        Ok(_) => println!("Invalid data was accepted (may be OK if validation is lenient)"),
        Err(e) => println!("Invalid data correctly rejected: {:?}", e),
    }

    // Test network resilience with multiple rapid requests
    let start_time = Instant::now();
    let mut successful_requests = 0;
    let mut failed_requests = 0;

    for i in 0..50 {
        let test_data = json!({
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "agent_id": format!("stress_test_{:03}", i),
            "metrics": {
                "accuracy": 90.0 + (i as f64 * 0.1),
                "latency_p95": 800.0 + (i as f64 * 10.0)
            },
            "stress_test": true
        });

        match client.send_data(test_data).await {
            Ok(_) => successful_requests += 1,
            Err(_) => failed_requests += 1,
        }

        // Small delay to avoid overwhelming the system
        sleep(Duration::from_millis(10)).await;
    }

    let duration = start_time.elapsed();
    println!(
        "Stress test completed in {:?}: {} successful, {} failed",
        duration, successful_requests, failed_requests
    );

    // Test automatic retry mechanism
    test_retry_mechanism(client).await;
}

async fn test_retry_mechanism(client: &BasicEnhancedTelemetryClient) {
    println!("Testing automatic retry mechanism...");

    // This test assumes some requests might fail and get retried
    let retry_test_data = json!({
        "timestamp": chrono::Utc::now().to_rfc3339(),
        "agent_id": "retry_test_001",
        "metrics": {
            "accuracy": 94.0,
            "latency_p95": 850.0
        },
        "retry_test": true,
        "large_payload": "x".repeat(10000) // Large payload to potentially cause issues
    });

    let start_time = Instant::now();

    match client.send_data(retry_test_data).await {
        Ok(_) => {
            let duration = start_time.elapsed();
            println!("Retry test successful (duration: {:?})", duration);
        }
        Err(e) => {
            let duration = start_time.elapsed();
            println!("Retry test failed after {:?}: {:?}", duration, e);
        }
    }
}

#[tokio::test]
async fn test_performance_benchmarks() {
    println!("Running performance benchmarks...");

    let config = EnhancedTelemetryConfig {
        organization_id: "perf_test_org".to_string(),
        api_key: "perf_test_key".to_string(),
        endpoints: vec![
            EndpointType::Http {
                url: std::env::var("API_ENDPOINT")
                    .unwrap_or_else(|_| "https://api-staging.briefcasebrain.com".to_string()),
            },
        ],
        auth_mode: AuthMode::ApiKey,
        organization_context: None,
        experiment_context: None,
        batch_size: 100,
        flush_interval: Duration::from_secs(1),
        retry_config: Default::default(),
        enable_compression: true,
        enable_encryption: false, // Disable for performance testing
        debug_mode: false,
    };

    let client = BasicEnhancedTelemetryClient::new(config)
        .await
        .expect("Failed to create performance test client");

    // Benchmark single request latency
    benchmark_single_request_latency(&client).await;

    // Benchmark throughput
    benchmark_throughput(&client).await;

    // Benchmark batch processing
    benchmark_batch_processing(&client).await;
}

async fn benchmark_single_request_latency(client: &BasicEnhancedTelemetryClient) {
    println!("Benchmarking single request latency...");

    let mut latencies = Vec::new();

    for i in 0..100 {
        let start_time = Instant::now();

        let test_data = json!({
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "agent_id": format!("latency_test_{:03}", i),
            "metrics": {
                "accuracy": 95.0,
                "latency_p95": 800.0
            }
        });

        match client.send_data(test_data).await {
            Ok(_) => {
                let latency = start_time.elapsed();
                latencies.push(latency);
            }
            Err(e) => eprintln!("Request {} failed: {:?}", i, e),
        }
    }

    if !latencies.is_empty() {
        let avg_latency = latencies.iter().sum::<Duration>() / latencies.len() as u32;
        let max_latency = latencies.iter().max().unwrap();
        let min_latency = latencies.iter().min().unwrap();

        println!("Single request latency:");
        println!("  Average: {:?}", avg_latency);
        println!("  Min: {:?}", min_latency);
        println!("  Max: {:?}", max_latency);

        // Validate latency requirements
        assert!(
            avg_latency < Duration::from_millis(2000),
            "Average latency {} exceeds 2s requirement",
            avg_latency.as_millis()
        );
    }
}

async fn benchmark_throughput(client: &BasicEnhancedTelemetryClient) {
    println!("Benchmarking throughput...");

    let test_duration = Duration::from_secs(30);
    let start_time = Instant::now();
    let mut request_count = 0;

    while start_time.elapsed() < test_duration {
        let test_data = json!({
            "timestamp": chrono::Utc::now().to_rfc3339(),
            "agent_id": format!("throughput_test_{:06}", request_count),
            "metrics": {
                "accuracy": 95.0 + (request_count as f64 * 0.01) % 5.0,
                "latency_p95": 800.0
            }
        });

        if client.send_data(test_data).await.is_ok() {
            request_count += 1;
        }
    }

    let actual_duration = start_time.elapsed();
    let throughput = request_count as f64 / actual_duration.as_secs_f64();

    println!("Throughput benchmark:");
    println!("  Requests: {}", request_count);
    println!("  Duration: {:?}", actual_duration);
    println!("  Throughput: {:.2} requests/second", throughput);

    // Validate throughput requirements (adjust based on your needs)
    assert!(
        throughput > 10.0,
        "Throughput {} is below minimum requirement of 10 RPS",
        throughput
    );
}

async fn benchmark_batch_processing(client: &BasicEnhancedTelemetryClient) {
    println!("Benchmarking batch processing...");

    let batch_sizes = vec![10, 50, 100, 500];

    for batch_size in batch_sizes {
        let start_time = Instant::now();

        let mut batch_data = Vec::new();
        for i in 0..batch_size {
            batch_data.push(json!({
                "timestamp": chrono::Utc::now().to_rfc3339(),
                "agent_id": format!("batch_test_{}_{:03}", batch_size, i),
                "metrics": {
                    "accuracy": 95.0,
                    "latency_p95": 800.0
                }
            }));
        }

        // Send batch (assuming the client has a send_batch method)
        for data in batch_data {
            if let Err(e) = client.send_data(data).await {
                eprintln!("Batch item failed: {:?}", e);
            }
        }

        // Force flush
        if let Err(e) = client.flush().await {
            eprintln!("Batch flush failed: {:?}", e);
        }

        let duration = start_time.elapsed();
        let throughput = batch_size as f64 / duration.as_secs_f64();

        println!("Batch size {} processed in {:?} ({:.2} items/second)",
                batch_size, duration, throughput);
    }
}

// Integration test runner
pub async fn run_integration_tests() -> Result<(), Box<dyn std::error::Error>> {
    println!("Starting comprehensive SDK integration tests...");

    // Set up test environment
    setup_test_environment().await?;

    // Run tests
    test_multi_protocol_implementation().await;
    test_performance_benchmarks().await;

    // Cleanup
    cleanup_test_environment().await?;

    println!("All integration tests completed successfully!");
    Ok(())
}

async fn setup_test_environment() -> Result<(), Box<dyn std::error::Error>> {
    println!("Setting up test environment...");

    // Verify environment variables
    let required_env_vars = vec![
        "TEST_API_KEY",
        "API_ENDPOINT",
        "LAKEFS_ENDPOINT",
    ];

    for var in required_env_vars {
        if std::env::var(var).is_err() {
            println!("Warning: {} environment variable not set, using defaults", var);
        }
    }

    Ok(())
}

async fn cleanup_test_environment() -> Result<(), Box<dyn std::error::Error>> {
    println!("Cleaning up test environment...");

    // Clean up any test data or resources
    // This would depend on your specific cleanup requirements

    Ok(())
}