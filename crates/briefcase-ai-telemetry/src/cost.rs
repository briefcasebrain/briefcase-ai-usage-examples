use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelInfo {
    pub name: String,
    pub provider: String,
    pub parameter_count: Option<u64>,
    pub input_cost_per_1k: Option<f64>,  // USD per 1K tokens
    pub output_cost_per_1k: Option<f64>, // USD per 1K tokens
    pub context_length: Option<u64>,
    pub supports_function_calling: bool,
    pub supports_streaming: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CostEstimate {
    pub input_tokens: u64,
    pub output_tokens: u64,
    pub total_tokens: u64,
    pub input_cost: f64,
    pub output_cost: f64,
    pub total_cost: f64,
    pub model_name: String,
    pub provider: String,
}

pub struct CostCalculator {
    models: HashMap<String, ModelInfo>,
}

impl Default for CostCalculator {
    fn default() -> Self {
        Self::new()
    }
}

impl CostCalculator {
    pub fn new() -> Self {
        let mut models = HashMap::new();

        // OpenAI Models (2024 pricing)
        models.insert(
            "gpt-4".to_string(),
            ModelInfo {
                name: "gpt-4".to_string(),
                provider: "openai".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.03),
                output_cost_per_1k: Some(0.06),
                context_length: Some(8192),
                supports_function_calling: true,
                supports_streaming: true,
            },
        );

        models.insert(
            "gpt-4-turbo".to_string(),
            ModelInfo {
                name: "gpt-4-turbo".to_string(),
                provider: "openai".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.01),
                output_cost_per_1k: Some(0.03),
                context_length: Some(128000),
                supports_function_calling: true,
                supports_streaming: true,
            },
        );

        models.insert(
            "gpt-4o".to_string(),
            ModelInfo {
                name: "gpt-4o".to_string(),
                provider: "openai".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.005),
                output_cost_per_1k: Some(0.015),
                context_length: Some(128000),
                supports_function_calling: true,
                supports_streaming: true,
            },
        );

        models.insert(
            "gpt-4o-mini".to_string(),
            ModelInfo {
                name: "gpt-4o-mini".to_string(),
                provider: "openai".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.00015),
                output_cost_per_1k: Some(0.0006),
                context_length: Some(128000),
                supports_function_calling: true,
                supports_streaming: true,
            },
        );

        models.insert(
            "gpt-3.5-turbo".to_string(),
            ModelInfo {
                name: "gpt-3.5-turbo".to_string(),
                provider: "openai".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.0005),
                output_cost_per_1k: Some(0.0015),
                context_length: Some(16385),
                supports_function_calling: true,
                supports_streaming: true,
            },
        );

        // Anthropic Models
        models.insert(
            "claude-3-5-sonnet-20241022".to_string(),
            ModelInfo {
                name: "claude-3-5-sonnet-20241022".to_string(),
                provider: "anthropic".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.003),
                output_cost_per_1k: Some(0.015),
                context_length: Some(200000),
                supports_function_calling: true,
                supports_streaming: true,
            },
        );

        models.insert(
            "claude-3-haiku-20240307".to_string(),
            ModelInfo {
                name: "claude-3-haiku-20240307".to_string(),
                provider: "anthropic".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.00025),
                output_cost_per_1k: Some(0.00125),
                context_length: Some(200000),
                supports_function_calling: false,
                supports_streaming: true,
            },
        );

        // Google Models
        models.insert(
            "gemini-1.5-pro".to_string(),
            ModelInfo {
                name: "gemini-1.5-pro".to_string(),
                provider: "google".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.0035),
                output_cost_per_1k: Some(0.0105),
                context_length: Some(2000000),
                supports_function_calling: true,
                supports_streaming: true,
            },
        );

        models.insert(
            "gemini-1.5-flash".to_string(),
            ModelInfo {
                name: "gemini-1.5-flash".to_string(),
                provider: "google".to_string(),
                parameter_count: None,
                input_cost_per_1k: Some(0.000075),
                output_cost_per_1k: Some(0.0003),
                context_length: Some(1000000),
                supports_function_calling: true,
                supports_streaming: true,
            },
        );

        // Meta Llama Models (estimated costs for hosted versions)
        models.insert(
            "llama-3.1-8b".to_string(),
            ModelInfo {
                name: "llama-3.1-8b".to_string(),
                provider: "meta".to_string(),
                parameter_count: Some(8_000_000_000),
                input_cost_per_1k: Some(0.0001),
                output_cost_per_1k: Some(0.0002),
                context_length: Some(128000),
                supports_function_calling: false,
                supports_streaming: true,
            },
        );

        models.insert(
            "llama-3.1-70b".to_string(),
            ModelInfo {
                name: "llama-3.1-70b".to_string(),
                provider: "meta".to_string(),
                parameter_count: Some(70_000_000_000),
                input_cost_per_1k: Some(0.0005),
                output_cost_per_1k: Some(0.001),
                context_length: Some(128000),
                supports_function_calling: false,
                supports_streaming: true,
            },
        );

        models.insert(
            "llama-3.1-405b".to_string(),
            ModelInfo {
                name: "llama-3.1-405b".to_string(),
                provider: "meta".to_string(),
                parameter_count: Some(405_000_000_000),
                input_cost_per_1k: Some(0.003),
                output_cost_per_1k: Some(0.006),
                context_length: Some(128000),
                supports_function_calling: false,
                supports_streaming: true,
            },
        );

        // Hugging Face Models (estimated costs for Inference Endpoints)
        // Note: Most open-source HF models are free when run locally,
        // but these estimates are for hosted inference endpoints
        models.insert(
            "distilbert-base-uncased".to_string(),
            ModelInfo {
                name: "distilbert-base-uncased".to_string(),
                provider: "huggingface".to_string(),
                parameter_count: Some(66_000_000),
                input_cost_per_1k: Some(0.00001), // Very low cost estimate for small BERT model
                output_cost_per_1k: Some(0.00001),
                context_length: Some(512),
                supports_function_calling: false,
                supports_streaming: false,
            },
        );

        models.insert(
            "distilgpt2".to_string(),
            ModelInfo {
                name: "distilgpt2".to_string(),
                provider: "huggingface".to_string(),
                parameter_count: Some(82_000_000),
                input_cost_per_1k: Some(0.00002),
                output_cost_per_1k: Some(0.00002),
                context_length: Some(1024),
                supports_function_calling: false,
                supports_streaming: true,
            },
        );

        models.insert(
            "facebook/bart-large-cnn".to_string(),
            ModelInfo {
                name: "facebook/bart-large-cnn".to_string(),
                provider: "huggingface".to_string(),
                parameter_count: Some(406_000_000),
                input_cost_per_1k: Some(0.00005),
                output_cost_per_1k: Some(0.00005),
                context_length: Some(1024),
                supports_function_calling: false,
                supports_streaming: false,
            },
        );

        models.insert(
            "t5-base".to_string(),
            ModelInfo {
                name: "t5-base".to_string(),
                provider: "huggingface".to_string(),
                parameter_count: Some(220_000_000),
                input_cost_per_1k: Some(0.00003),
                output_cost_per_1k: Some(0.00003),
                context_length: Some(512),
                supports_function_calling: false,
                supports_streaming: false,
            },
        );

        models.insert(
            "sentence-transformers/all-MiniLM-L6-v2".to_string(),
            ModelInfo {
                name: "sentence-transformers/all-MiniLM-L6-v2".to_string(),
                provider: "huggingface".to_string(),
                parameter_count: Some(22_000_000),
                input_cost_per_1k: Some(0.00001),
                output_cost_per_1k: Some(0.00001),
                context_length: Some(256),
                supports_function_calling: false,
                supports_streaming: false,
            },
        );

        models.insert(
            "Helsinki-NLP/opus-mt-en-fr".to_string(),
            ModelInfo {
                name: "Helsinki-NLP/opus-mt-en-fr".to_string(),
                provider: "huggingface".to_string(),
                parameter_count: Some(77_000_000),
                input_cost_per_1k: Some(0.00002),
                output_cost_per_1k: Some(0.00002),
                context_length: Some(512),
                supports_function_calling: false,
                supports_streaming: false,
            },
        );

        // Popular large HF models (for hosted inference)
        models.insert(
            "microsoft/DialoGPT-large".to_string(),
            ModelInfo {
                name: "microsoft/DialoGPT-large".to_string(),
                provider: "huggingface".to_string(),
                parameter_count: Some(762_000_000),
                input_cost_per_1k: Some(0.0001),
                output_cost_per_1k: Some(0.0001),
                context_length: Some(1000),
                supports_function_calling: false,
                supports_streaming: true,
            },
        );

        models.insert(
            "bigscience/bloom-560m".to_string(),
            ModelInfo {
                name: "bigscience/bloom-560m".to_string(),
                provider: "huggingface".to_string(),
                parameter_count: Some(560_000_000),
                input_cost_per_1k: Some(0.00008),
                output_cost_per_1k: Some(0.00008),
                context_length: Some(2048),
                supports_function_calling: false,
                supports_streaming: true,
            },
        );

        Self { models }
    }

    pub fn count_tokens_approximate(text: &str) -> u64 {
        // Rough approximation: ~4 characters per token for English text
        if text.is_empty() {
            return 0;
        }
        // Use ceiling division to ensure proper rounding
        std::cmp::max(1, (text.len() as u64 + 3) / 4)
    }

    pub fn get_model_info(&self, model_name: &str) -> Option<&ModelInfo> {
        let model_name_lower = model_name.to_lowercase();

        // Try exact match first
        if let Some(info) = self.models.get(&model_name_lower) {
            return Some(info);
        }

        // Try partial match
        for (key, info) in &self.models {
            if key.to_lowercase().contains(&model_name_lower)
                || model_name_lower.contains(&key.to_lowercase())
            {
                return Some(info);
            }
        }

        None
    }

    pub fn estimate_cost(
        &self,
        model_name: &str,
        input_text: &str,
        output_text: &str,
        exact_tokens: Option<(u64, u64)>,
    ) -> Option<CostEstimate> {
        let model_info = self.get_model_info(model_name)?;

        let input_cost_per_1k = model_info.input_cost_per_1k?;
        let output_cost_per_1k = model_info.output_cost_per_1k?;

        let (input_tokens, output_tokens) = if let Some((input, output)) = exact_tokens {
            (input, output)
        } else {
            (
                Self::count_tokens_approximate(input_text),
                Self::count_tokens_approximate(output_text),
            )
        };

        let input_cost = (input_tokens as f64 / 1000.0) * input_cost_per_1k;
        let output_cost = (output_tokens as f64 / 1000.0) * output_cost_per_1k;
        let total_cost = input_cost + output_cost;

        Some(CostEstimate {
            input_tokens,
            output_tokens,
            total_tokens: input_tokens + output_tokens,
            input_cost,
            output_cost,
            total_cost,
            model_name: model_info.name.clone(),
            provider: model_info.provider.clone(),
        })
    }

    pub fn add_model(&mut self, model: ModelInfo) {
        self.models.insert(model.name.clone(), model);
    }

    pub fn list_models(&self) -> Vec<&ModelInfo> {
        self.models.values().collect()
    }

    pub fn list_models_by_provider(&self, provider: &str) -> Vec<&ModelInfo> {
        self.models
            .values()
            .filter(|model| model.provider == provider)
            .collect()
    }

    pub fn get_cheapest_model(&self) -> Option<&ModelInfo> {
        self.models
            .values()
            .filter(|model| model.input_cost_per_1k.is_some() && model.output_cost_per_1k.is_some())
            .min_by(|a, b| {
                let cost_a = a.input_cost_per_1k.unwrap() + a.output_cost_per_1k.unwrap();
                let cost_b = b.input_cost_per_1k.unwrap() + b.output_cost_per_1k.unwrap();
                cost_a
                    .partial_cmp(&cost_b)
                    .unwrap_or(std::cmp::Ordering::Equal)
            })
    }

    pub fn get_models_under_cost(&self, max_cost_per_1k: f64) -> Vec<&ModelInfo> {
        self.models
            .values()
            .filter(|model| {
                if let (Some(input_cost), Some(output_cost)) =
                    (model.input_cost_per_1k, model.output_cost_per_1k)
                {
                    (input_cost + output_cost) <= max_cost_per_1k
                } else {
                    false
                }
            })
            .collect()
    }

    pub fn calculate_monthly_cost(
        &self,
        model_name: &str,
        daily_input_tokens: u64,
        daily_output_tokens: u64,
    ) -> Option<f64> {
        let model_info = self.get_model_info(model_name)?;

        let input_cost_per_1k = model_info.input_cost_per_1k?;
        let output_cost_per_1k = model_info.output_cost_per_1k?;

        let daily_input_cost = (daily_input_tokens as f64 / 1000.0) * input_cost_per_1k;
        let daily_output_cost = (daily_output_tokens as f64 / 1000.0) * output_cost_per_1k;
        let daily_total = daily_input_cost + daily_output_cost;

        Some(daily_total * 30.0) // Approximate month
    }

    pub fn compare_models(
        &self,
        model_names: &[&str],
        input_tokens: u64,
        output_tokens: u64,
    ) -> Vec<CostEstimate> {
        model_names
            .iter()
            .filter_map(|&model_name| {
                self.estimate_cost(model_name, "", "", Some((input_tokens, output_tokens)))
            })
            .collect()
    }
}

// Convenience functions
pub fn estimate_cost(
    model_name: &str,
    input_text: &str,
    output_text: &str,
    exact_tokens: Option<(u64, u64)>,
) -> Option<CostEstimate> {
    let calculator = CostCalculator::new();
    calculator.estimate_cost(model_name, input_text, output_text, exact_tokens)
}

pub fn get_model_info(model_name: &str) -> Option<ModelInfo> {
    let calculator = CostCalculator::new();
    calculator.get_model_info(model_name).cloned()
}

pub fn count_tokens_approximate(text: &str) -> u64 {
    CostCalculator::count_tokens_approximate(text)
}

// Cost formatting utilities
pub fn format_cost(cost_usd: f64) -> String {
    if cost_usd < 0.01 {
        format!("${:.6}", cost_usd)
    } else if cost_usd < 1.0 {
        format!("${:.4}", cost_usd)
    } else {
        format!("${:.2}", cost_usd)
    }
}

pub fn format_tokens(tokens: u64) -> String {
    if tokens < 1_000 {
        format!("{} tokens", tokens)
    } else if tokens < 1_000_000 {
        format!("{:.1}K tokens", tokens as f64 / 1_000.0)
    } else {
        format!("{:.1}M tokens", tokens as f64 / 1_000_000.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cost_calculator_creation() {
        let calculator = CostCalculator::new();
        assert!(!calculator.list_models().is_empty());
        assert!(calculator.get_model_info("gpt-4").is_some());
    }

    #[test]
    fn test_model_info_retrieval() {
        let calculator = CostCalculator::new();

        // Test exact match
        let gpt4_info = calculator.get_model_info("gpt-4").unwrap();
        assert_eq!(gpt4_info.name, "gpt-4");
        assert_eq!(gpt4_info.provider, "openai");

        // Test partial match
        let claude_info = calculator.get_model_info("claude-3-5-sonnet").unwrap();
        assert!(claude_info.name.contains("claude-3-5-sonnet"));
        assert_eq!(claude_info.provider, "anthropic");

        // Test non-existent model
        assert!(calculator.get_model_info("non-existent-model").is_none());
    }

    #[test]
    fn test_token_counting() {
        assert_eq!(CostCalculator::count_tokens_approximate(""), 0);
        assert_eq!(CostCalculator::count_tokens_approximate("hello"), 2); // 5/4 rounded up
        assert_eq!(CostCalculator::count_tokens_approximate("hello world"), 3); // 11/4 rounded up
        assert_eq!(CostCalculator::count_tokens_approximate("a"), 1); // minimum 1 token
    }

    #[test]
    fn test_cost_estimation() {
        let calculator = CostCalculator::new();

        // Test with GPT-4 (known pricing)
        let estimate = calculator
            .estimate_cost("gpt-4", "test input", "test output", Some((1000, 500)))
            .unwrap();

        assert_eq!(estimate.input_tokens, 1000);
        assert_eq!(estimate.output_tokens, 500);
        assert_eq!(estimate.total_tokens, 1500);
        assert_eq!(estimate.model_name, "gpt-4");
        assert_eq!(estimate.provider, "openai");

        // Check cost calculation (GPT-4: $0.03/$0.06 per 1K tokens)
        assert!((estimate.input_cost - 0.03).abs() < 0.001);
        assert!((estimate.output_cost - 0.03).abs() < 0.001);
        assert!((estimate.total_cost - 0.06).abs() < 0.001);
    }

    #[test]
    fn test_cost_estimation_with_text() {
        let calculator = CostCalculator::new();

        let estimate = calculator
            .estimate_cost(
                "gpt-4o-mini",
                "This is a test input with multiple words",
                "This is a test output",
                None,
            )
            .unwrap();

        assert!(estimate.input_tokens > 0);
        assert!(estimate.output_tokens > 0);
        assert_eq!(
            estimate.total_tokens,
            estimate.input_tokens + estimate.output_tokens
        );
        assert!(estimate.total_cost > 0.0);
    }

    #[test]
    fn test_add_custom_model() {
        let mut calculator = CostCalculator::new();

        let custom_model = ModelInfo {
            name: "custom-model".to_string(),
            provider: "custom".to_string(),
            parameter_count: Some(1_000_000_000),
            input_cost_per_1k: Some(0.001),
            output_cost_per_1k: Some(0.002),
            context_length: Some(4096),
            supports_function_calling: false,
            supports_streaming: true,
        };

        calculator.add_model(custom_model);

        let retrieved = calculator.get_model_info("custom-model").unwrap();
        assert_eq!(retrieved.name, "custom-model");
        assert_eq!(retrieved.provider, "custom");
    }

    #[test]
    fn test_list_models_by_provider() {
        let calculator = CostCalculator::new();

        let openai_models = calculator.list_models_by_provider("openai");
        let anthropic_models = calculator.list_models_by_provider("anthropic");
        let google_models = calculator.list_models_by_provider("google");

        assert!(!openai_models.is_empty());
        assert!(!anthropic_models.is_empty());
        assert!(!google_models.is_empty());

        // Verify all returned models have correct provider
        for model in openai_models {
            assert_eq!(model.provider, "openai");
        }
    }

    #[test]
    fn test_get_cheapest_model() {
        let calculator = CostCalculator::new();

        let cheapest = calculator.get_cheapest_model().unwrap();
        assert!(cheapest.input_cost_per_1k.is_some());
        assert!(cheapest.output_cost_per_1k.is_some());

        // Should be a very low cost model
        let total_cost = cheapest.input_cost_per_1k.unwrap() + cheapest.output_cost_per_1k.unwrap();
        assert!(total_cost < 0.01); // Less than 1 cent per 1K tokens combined
    }

    #[test]
    fn test_get_models_under_cost() {
        let calculator = CostCalculator::new();

        let cheap_models = calculator.get_models_under_cost(0.001);
        let expensive_models = calculator.get_models_under_cost(0.1);

        assert!(cheap_models.len() <= expensive_models.len());

        // All returned models should be under the cost threshold
        for model in cheap_models {
            if let (Some(input), Some(output)) = (model.input_cost_per_1k, model.output_cost_per_1k)
            {
                assert!(input + output <= 0.001);
            }
        }
    }

    #[test]
    fn test_monthly_cost_calculation() {
        let calculator = CostCalculator::new();

        let monthly_cost = calculator
            .calculate_monthly_cost(
                "gpt-4o-mini",
                10000, // 10K input tokens per day
                5000,  // 5K output tokens per day
            )
            .unwrap();

        assert!(monthly_cost > 0.0);

        // Should be approximately: ((10/1000 * 0.00015) + (5/1000 * 0.0006)) * 30
        let expected = ((10.0 * 0.00015) + (5.0 * 0.0006)) * 30.0;
        assert!((monthly_cost - expected).abs() < 0.001);
    }

    #[test]
    fn test_compare_models() {
        let calculator = CostCalculator::new();

        let models = ["gpt-4", "gpt-4o-mini", "claude-3-haiku-20240307"];
        let comparisons = calculator.compare_models(&models, 1000, 500);

        assert_eq!(comparisons.len(), 3);

        // Should be sorted by cost (cheapest first when we look at the results)
        let costs: Vec<f64> = comparisons.iter().map(|c| c.total_cost).collect();
        assert!(costs.iter().all(|&cost| cost > 0.0));
    }

    #[test]
    fn test_convenience_functions() {
        // Test standalone cost estimation
        let estimate = estimate_cost("gpt-4", "", "", Some((1000, 500))).unwrap();
        assert_eq!(estimate.input_tokens, 1000);
        assert_eq!(estimate.output_tokens, 500);

        // Test standalone model info retrieval
        let info = get_model_info("gpt-4").unwrap();
        assert_eq!(info.name, "gpt-4");

        // Test standalone token counting
        assert_eq!(count_tokens_approximate("hello world"), 3);
    }

    #[test]
    fn test_cost_formatting() {
        assert_eq!(format_cost(0.000123), "$0.000123");
        assert_eq!(format_cost(0.0123), "$0.0123");
        assert_eq!(format_cost(1.234), "$1.23");
        assert_eq!(format_cost(12.345), "$12.35");
    }

    #[test]
    fn test_token_formatting() {
        assert_eq!(format_tokens(123), "123 tokens");
        assert_eq!(format_tokens(1234), "1.2K tokens");
        assert_eq!(format_tokens(1234567), "1.2M tokens");
    }

    #[test]
    fn test_model_capabilities() {
        let calculator = CostCalculator::new();

        let gpt4 = calculator.get_model_info("gpt-4").unwrap();
        assert!(gpt4.supports_function_calling);
        assert!(gpt4.supports_streaming);
        assert!(gpt4.context_length.unwrap() > 0);

        let distilbert = calculator
            .get_model_info("distilbert-base-uncased")
            .unwrap();
        assert!(!distilbert.supports_function_calling);
        assert!(!distilbert.supports_streaming);
    }

    #[test]
    fn test_edge_cases() {
        let calculator = CostCalculator::new();

        // Test with zero tokens
        let estimate = calculator
            .estimate_cost("gpt-4", "", "", Some((0, 0)))
            .unwrap();
        assert_eq!(estimate.total_cost, 0.0);

        // Test with missing cost info (this should return None for estimation)
        // We'll create a model without cost info
        let mut calc = CostCalculator::new();
        let no_cost_model = ModelInfo {
            name: "no-cost-model".to_string(),
            provider: "test".to_string(),
            parameter_count: None,
            input_cost_per_1k: None,
            output_cost_per_1k: None,
            context_length: Some(1024),
            supports_function_calling: false,
            supports_streaming: false,
        };
        calc.add_model(no_cost_model);

        assert!(calc
            .estimate_cost("no-cost-model", "test", "test", None)
            .is_none());
    }
}
