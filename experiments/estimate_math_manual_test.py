#!/usr/bin/env python3
"""Estimate full MATH manual_v1 test resource needs from tracked evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

DEFAULT_MANUAL_RUN = Path("report/evidence/math_validate50/manual_v1")
DEFAULT_DIRECT_RUN = Path("report/evidence/math_test_baselines/direct")
DEFAULT_COT_RUN = Path("report/evidence/math_test_baselines/cot")
DEFAULT_OUTPUT = Path("report/tables/math_manual_test_estimate.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manual-run", type=Path, default=DEFAULT_MANUAL_RUN)
    parser.add_argument("--direct-run", type=Path, default=DEFAULT_DIRECT_RUN)
    parser.add_argument("--cot-run", type=Path, default=DEFAULT_COT_RUN)
    parser.add_argument("--chunk-size", type=int, default=20)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sample_count(config: dict[str, Any]) -> int:
    if config.get("sample_size"):
        return int(config["sample_size"])
    indices = config.get("indices")
    if indices is not None:
        return len(indices)
    raise ValueError("Run config does not contain sample_size or indices")


def format_int(value: float) -> str:
    return f"{round(value):,}"


def format_float(value: float) -> str:
    return f"{value:.2f}"


def render_estimate(
    manual_config: dict[str, Any],
    direct_config: dict[str, Any],
    cot_config: dict[str, Any],
    chunk_size: int,
) -> str:
    validation_samples = sample_count(manual_config)
    test_samples = sample_count(direct_config)
    if sample_count(cot_config) != test_samples:
        raise ValueError("Direct and CoT test runs use different sample counts")

    calls_per_problem = manual_config["llm_call_count"] / validation_samples
    tokens_per_problem = manual_config["total_tokens"] / validation_samples
    estimated_calls = calls_per_problem * test_samples
    estimated_tokens = tokens_per_problem * test_samples
    chunk_count = math.ceil(test_samples / chunk_size)
    last_chunk_samples = test_samples - chunk_size * (chunk_count - 1)

    rows = [
        ("validation source", f"{validation_samples} MATH validation examples"),
        ("test examples", f"{test_samples}"),
        ("planned chunk size", f"{chunk_size} examples"),
        ("planned chunks", f"{chunk_count} chunks; last chunk has {last_chunk_samples} examples"),
        ("manual calls per example", format_float(calls_per_problem)),
        ("manual tokens per example", format_int(tokens_per_problem)),
        ("estimated full-test calls", format_int(estimated_calls)),
        ("estimated full-test tokens", format_int(estimated_tokens)),
        ("estimated tokens per full chunk", format_int(tokens_per_problem * chunk_size)),
        ("estimated calls per full chunk", format_int(calls_per_problem * chunk_size)),
        ("token multiplier vs direct test", f"{estimated_tokens / direct_config['total_tokens']:.2f}x"),
        ("token multiplier vs CoT test", f"{estimated_tokens / cot_config['total_tokens']:.2f}x"),
    ]

    lines = [
        "# MATH Manual Workflow Full-Test Resource Estimate",
        "",
        "This estimate uses the tracked 50-sample MATH `manual_v1` validation run as the per-example cost source.",
        "It is a planning estimate, not a measured full-test result.",
        "",
        "| item | estimate |",
        "| --- | --- |",
    ]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    if args.chunk_size <= 0:
        raise ValueError("--chunk-size must be positive")

    manual_config = read_json(args.manual_run / "run_config.json")
    direct_config = read_json(args.direct_run / "run_config.json")
    cot_config = read_json(args.cot_run / "run_config.json")
    output = render_estimate(manual_config, direct_config, cot_config, args.chunk_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
