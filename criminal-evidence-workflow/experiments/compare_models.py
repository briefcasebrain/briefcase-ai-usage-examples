#!/usr/bin/env python3
"""Side-by-side GPT-4o vs Claude Sonnet comparison.

Runs all 5 reports through both models (mocked) and produces
a detailed comparison table with guardrail scores.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation import run_full_evaluation, print_comparison_table


async def main():
    print("Running model comparison (mocked, no latency)...\n")
    eval_data = await run_full_evaluation(simulate_latency=False)
    print_comparison_table(eval_data)


if __name__ == "__main__":
    asyncio.run(main())
