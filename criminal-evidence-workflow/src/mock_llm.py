"""Fixture-backed LLM provider. No API calls, no API keys.

Returns pre-generated responses from data/fixtures/ with simulated
latency and token counts. Supports model switching and temperature
variation to demonstrate the SDK's multi-model comparison features.
"""

import json
import asyncio
import random
from pathlib import Path
from typing import Optional


class MockLLMProvider:
    def __init__(
        self,
        fixtures_dir: str = "data/fixtures",
        model: str = "gpt-4o",
        provider: str = "openai",
        temperature: float = 0.0,
        simulate_latency: bool = True,
    ):
        self.fixtures_dir = Path(fixtures_dir)
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.simulate_latency = simulate_latency
        self._fixtures = {}
        self._load_fixtures()

    def _load_fixtures(self):
        for f in self.fixtures_dir.glob("*.json"):
            data = json.loads(f.read_text())
            self._fixtures[f.stem] = data

    def _fixture_key(self, report_id: str, replay: bool = False) -> str:
        temp_suffix = f"_t{self.temperature}" if self.temperature > 0 else ""
        replay_suffix = "_replay" if replay else ""
        return f"{report_id}_{self.model}{temp_suffix}{replay_suffix}"

    async def generate(self, report_id: str, query: str, replay: bool = False) -> dict:
        key = self._fixture_key(report_id, replay)
        if key not in self._fixtures:
            # Fall back to temperature=0.0 fixture
            key = f"{report_id}_{self.model}"

        if key not in self._fixtures:
            raise KeyError(f"No fixture found for key '{key}'. Available: {list(self._fixtures.keys())}")

        fixture = self._fixtures[key]

        if self.simulate_latency:
            base_ms = 1200 if self.provider == "openai" else 950
            jitter = random.uniform(0.7, 1.4)
            await asyncio.sleep((base_ms * jitter) / 1000)

        return {
            "summary": fixture["summary"],
            "confidence": fixture["confidence"],
            "token_usage": fixture["token_usage"],
            "model": self.model,
            "provider": self.provider,
            "temperature": self.temperature,
        }

    @property
    def model_config(self) -> dict:
        return {
            "model": self.model,
            "provider": self.provider,
            "temperature": self.temperature,
        }


# ── Model presets ──

GPT4O = MockLLMProvider(model="gpt-4o", provider="openai", temperature=0.0)
GPT4O_STOCHASTIC = MockLLMProvider(model="gpt-4o", provider="openai", temperature=0.7)
CLAUDE_SONNET = MockLLMProvider(model="claude-sonnet", provider="anthropic", temperature=0.0)

ALL_MODELS = [GPT4O, CLAUDE_SONNET]
