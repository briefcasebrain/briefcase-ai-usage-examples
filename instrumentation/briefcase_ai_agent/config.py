"""
Configuration management for Briefcase AI instrumentation.
"""

import os
import yaml
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

@dataclass
class SanitizationRule:
    """Rule for sanitizing sensitive data."""
    pattern: str
    replacement: str = "[REDACTED]"
    rule_type: str = "regex"  # regex, keyword, pii

@dataclass
class BriefcaseConfig:
    """Configuration for Briefcase AI instrumentation."""

    # Authentication
    api_key: Optional[str] = None
    endpoint: Optional[str] = None

    # Telemetry settings
    batch_size: int = 100
    flush_interval_seconds: int = 5
    max_retries: int = 3
    timeout_seconds: int = 10
    enabled: bool = True

    # Data handling
    max_input_length: int = 10000
    max_output_length: int = 10000
    sanitization_rules: List[SanitizationRule] = field(default_factory=list)

    # Development
    debug: bool = False
    dry_run: bool = False
    raise_on_telemetry_error: bool = False

    # Consensus mode defaults
    default_consensus_runs: int = 3
    default_consensus_threshold: int = 80

    # Framework integrations
    auto_instrument_openai: bool = False
    auto_instrument_anthropic: bool = False
    auto_instrument_langchain: bool = False

    def __post_init__(self):
        """Load configuration from environment and config files."""
        self._load_from_env()
        self._load_from_config_file()
        self._setup_default_sanitization()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'BRIEFCASE_API_KEY': 'api_key',
            'BRIEFCASE_ENDPOINT': 'endpoint',
            'BRIEFCASE_BATCH_SIZE': ('batch_size', int),
            'BRIEFCASE_FLUSH_INTERVAL': ('flush_interval_seconds', int),
            'BRIEFCASE_MAX_RETRIES': ('max_retries', int),
            'BRIEFCASE_TIMEOUT': ('timeout_seconds', int),
            'BRIEFCASE_ENABLED': ('enabled', lambda x: x.lower() == 'true'),
            'BRIEFCASE_DEBUG': ('debug', lambda x: x.lower() == 'true'),
            'BRIEFCASE_DRY_RUN': ('dry_run', lambda x: x.lower() == 'true'),
            'BRIEFCASE_MAX_INPUT_LENGTH': ('max_input_length', int),
            'BRIEFCASE_MAX_OUTPUT_LENGTH': ('max_output_length', int),
            'BRIEFCASE_RAISE_ON_ERROR': ('raise_on_telemetry_error', lambda x: x.lower() == 'true'),
        }

        for env_var, config_attr in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                if isinstance(config_attr, tuple):
                    attr_name, converter = config_attr
                    try:
                        setattr(self, attr_name, converter(env_value))
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Invalid value for {env_var}: {env_value} ({e})")
                else:
                    setattr(self, config_attr, env_value)

    def _load_from_config_file(self):
        """Load configuration from YAML or JSON config files."""
        config_paths = [
            '.briefcase.yml',
            '.briefcase.yaml',
            '.briefcase.json',
            os.path.expanduser('~/.briefcase.yml'),
            os.path.expanduser('~/.briefcase.yaml'),
            os.path.expanduser('~/.briefcase.json'),
        ]

        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        if config_path.endswith('.json'):
                            config_data = json.load(f)
                        else:
                            config_data = yaml.safe_load(f)

                    if config_data:
                        self._apply_config_data(config_data)
                    break

                except Exception as e:
                    print(f"Warning: Failed to load config from {config_path}: {e}")

    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data from file."""
        for key, value in config_data.items():
            if key == 'sanitization_rules' and isinstance(value, list):
                rules = []
                for rule_data in value:
                    if isinstance(rule_data, dict):
                        rules.append(SanitizationRule(**rule_data))
                self.sanitization_rules.extend(rules)
            elif hasattr(self, key):
                setattr(self, key, value)

    def _setup_default_sanitization(self):
        """Setup default sanitization rules for common PII."""
        if not self.sanitization_rules:
            default_rules = [
                # Common PII patterns
                SanitizationRule(
                    pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    replacement="[EMAIL]",
                    rule_type="pii"
                ),
                SanitizationRule(
                    pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                    replacement="[SSN]",
                    rule_type="pii"
                ),
                SanitizationRule(
                    pattern=r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                    replacement="[CREDIT_CARD]",
                    rule_type="pii"
                ),
                SanitizationRule(
                    pattern=r'\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
                    replacement="[PHONE]",
                    rule_type="pii"
                ),
                # API keys and tokens
                SanitizationRule(
                    pattern=r'sk-[A-Za-z0-9]{48}',
                    replacement="[API_KEY]",
                    rule_type="api_key"
                ),
                SanitizationRule(
                    pattern=r'Bearer [A-Za-z0-9._-]+',
                    replacement="Bearer [TOKEN]",
                    rule_type="api_key"
                ),
            ]
            self.sanitization_rules.extend(default_rules)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if isinstance(value, list) and value and isinstance(value[0], SanitizationRule):
                result[key] = [rule.__dict__ for rule in value]
            else:
                result[key] = value
        return result

    def save(self, path: str):
        """Save configuration to file."""
        config_dict = self.to_dict()

        if path.endswith('.json'):
            with open(path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        else:
            with open(path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)

    @classmethod
    def from_file(cls, path: str) -> 'BriefcaseConfig':
        """Load configuration from file."""
        config = cls()

        try:
            with open(path, 'r') as f:
                if path.endswith('.json'):
                    config_data = json.load(f)
                else:
                    config_data = yaml.safe_load(f)

            if config_data:
                config._apply_config_data(config_data)

        except Exception as e:
            raise ValueError(f"Failed to load configuration from {path}: {e}")

        return config

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []

        if not self.api_key and self.enabled:
            issues.append("API key is required when telemetry is enabled")

        if self.batch_size <= 0:
            issues.append("Batch size must be positive")

        if self.flush_interval_seconds <= 0:
            issues.append("Flush interval must be positive")

        if self.max_retries < 0:
            issues.append("Max retries cannot be negative")

        if self.timeout_seconds <= 0:
            issues.append("Timeout must be positive")

        if self.max_input_length <= 0:
            issues.append("Max input length must be positive")

        if self.max_output_length <= 0:
            issues.append("Max output length must be positive")

        if self.default_consensus_runs < 1:
            issues.append("Consensus runs must be at least 1")

        if not (0 <= self.default_consensus_threshold <= 100):
            issues.append("Consensus threshold must be between 0 and 100")

        return issues

# Example configuration files
EXAMPLE_YAML_CONFIG = """
# Briefcase AI Configuration

# Authentication
api_key: "bca_your_api_key_here"
endpoint: "https://observe.briefcasebrain.io"

# Telemetry settings
batch_size: 50
flush_interval_seconds: 10
enabled: true
debug: false

# Data handling
max_input_length: 5000
max_output_length: 5000

# Custom sanitization rules
sanitization_rules:
  - pattern: "\\\\b(password|secret|key)\\\\s*[:=]\\\\s*\\\\S+"
    replacement: "[SENSITIVE]"
    rule_type: "keyword"

  - pattern: "\\\\buser_\\\\d+\\\\b"
    replacement: "[USER_ID]"
    rule_type: "regex"

# Framework integrations
auto_instrument_openai: true
auto_instrument_langchain: true
"""

EXAMPLE_JSON_CONFIG = """{
  "api_key": "bca_your_api_key_here",
  "endpoint": "https://observe.briefcasebrain.io",
  "batch_size": 50,
  "flush_interval_seconds": 10,
  "enabled": true,
  "debug": false,
  "max_input_length": 5000,
  "max_output_length": 5000,
  "sanitization_rules": [
    {
      "pattern": "\\\\b(password|secret|key)\\\\s*[:=]\\\\s*\\\\S+",
      "replacement": "[SENSITIVE]",
      "rule_type": "keyword"
    }
  ],
  "auto_instrument_openai": true,
  "auto_instrument_langchain": true
}"""