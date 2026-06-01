#!/usr/bin/env python3
"""Summarize recorded API token usage and remaining Kimi budget needs."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_RUNS_DIR = Path("experiments/runs")
DEFAULT_MANUAL_VALIDATE_RUN = Path("report/evidence/math_validate50/manual_v1")
DEFAULT_DIRECT_TEST_RUN = Path("report/evidence/math_test_baselines/direct")
DEFAULT_MANUAL_TEST_RUN = Path("experiments/chunked_runs/MATH/manual_v1/math-test-manual-v1")
DEFAULT_OUTPUT = Path("report/tables/api_budget_summary.md")

INPUT_CACHE_HIT_CNY_PER_MILLION = 0.70
INPUT_CACHE_MISS_CNY_PER_MILLION = 4.00
OUTPUT_CNY_PER_MILLION = 21.00


@dataclass
class UsageRow:
    group: str
    runs: int = 0
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    parser.add_argument("--manual-validate-run", type=Path, default=DEFAULT_MANUAL_VALIDATE_RUN)
    parser.add_argument("--direct-test-run", type=Path, default=DEFAULT_DIRECT_TEST_RUN)
    parser.add_argument("--manual-test-run", type=Path, default=DEFAULT_MANUAL_TEST_RUN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def method_name(config: dict[str, Any]) -> str:
    return str(config.get("baseline") or config.get("workflow") or "unknown")


def recorded_group(config: dict[str, Any]) -> str:
    dataset = str(config.get("dataset", "unknown"))
    split = str(config.get("split", "unknown"))
    method = method_name(config)
    sample_size = int(config.get("sample_size") or 0)

    if dataset == "MATH" and split == "test" and method in {"direct", "cot"}:
        return "MATH full direct/CoT baselines"
    if dataset == "HumanEval" and split == "test":
        return "HumanEval full test experiments"
    if dataset == "MATH" and split == "validate" and sample_size == 50:
        return "MATH 50-example validation experiments"
    if split == "validate" and sample_size == 20:
        return "20-example validation experiments"
    if split == "validate" and sample_size == 3:
        return "3-example smoke and ablation checks"
    return "Other recorded API runs"


def add_usage(row: UsageRow, calls: int, input_tokens: int, output_tokens: int) -> None:
    row.runs += 1
    row.calls += calls
    row.input_tokens += input_tokens
    row.output_tokens += output_tokens


def load_recorded_usage(runs_dir: Path) -> tuple[list[UsageRow], int]:
    grouped: dict[str, UsageRow] = defaultdict(lambda: UsageRow(group=""))
    unmetered_runs = 0
    for path in sorted(runs_dir.glob("*/*/*/run_config.json")):
        config = read_json(path)
        calls = int(config.get("llm_call_count") or 0)
        input_tokens = int(config.get("total_input_tokens") or 0)
        output_tokens = int(config.get("total_output_tokens") or 0)
        if calls == 0 and input_tokens == 0 and output_tokens == 0:
            unmetered_runs += 1
            continue
        group = recorded_group(config)
        if not grouped[group].group:
            grouped[group].group = group
        add_usage(grouped[group], calls, input_tokens, output_tokens)
    return sorted(grouped.values(), key=lambda row: row.group), unmetered_runs


def estimate_partial_runs(runs_dir: Path, manual_config: dict[str, Any]) -> list[UsageRow]:
    sample_size = int(manual_config["sample_size"])
    calls_per_example = float(manual_config["llm_call_count"]) / sample_size
    input_per_example = float(manual_config["total_input_tokens"]) / sample_size
    output_per_example = float(manual_config["total_output_tokens"]) / sample_size

    rows: list[UsageRow] = []
    for log_path in sorted((runs_dir / "MATH" / "manual_v1").glob("*/log.json")):
        run_dir = log_path.parent
        if (run_dir / "run_config.json").exists():
            continue
        examples = len(read_json(log_path))
        rows.append(
            UsageRow(
                group=f"Unmetered stopped MATH manual_v1 attempt ({examples} examples)",
                runs=1,
                calls=round(calls_per_example * examples),
                input_tokens=round(input_per_example * examples),
                output_tokens=round(output_per_example * examples),
            )
        )
    return rows


def estimate_remaining_manual_run(
    manual_config: dict[str, Any],
    direct_test_config: dict[str, Any],
) -> UsageRow:
    validation_samples = int(manual_config["sample_size"])
    test_samples = int(direct_test_config["sample_size"])
    scale = test_samples / validation_samples
    return UsageRow(
        group="Remaining full MATH manual_v1 test estimate",
        runs=1,
        calls=round(float(manual_config["llm_call_count"]) * scale),
        input_tokens=round(float(manual_config["total_input_tokens"]) * scale),
        output_tokens=round(float(manual_config["total_output_tokens"]) * scale),
    )


def completed_manual_run(manual_test_run: Path) -> UsageRow | None:
    config_path = manual_test_run / "run_config.json"
    if not config_path.is_file():
        return None
    config = read_json(config_path)
    if not config.get("is_complete"):
        return None
    return UsageRow(
        group="MATH full manual_v1 workflow",
        runs=1,
        calls=int(config.get("llm_call_count") or 0),
        input_tokens=int(config.get("total_input_tokens") or 0),
        output_tokens=int(config.get("total_output_tokens") or 0),
    )


def cny_range(row: UsageRow) -> str:
    cache_hit = (
        row.input_tokens * INPUT_CACHE_HIT_CNY_PER_MILLION
        + row.output_tokens * OUTPUT_CNY_PER_MILLION
    ) / 1_000_000
    cache_miss = (
        row.input_tokens * INPUT_CACHE_MISS_CNY_PER_MILLION
        + row.output_tokens * OUTPUT_CNY_PER_MILLION
    ) / 1_000_000
    return f"CNY {cache_hit:.2f}-{cache_miss:.2f}"


def format_int(value: int) -> str:
    return f"{value:,}"


def render_usage_table(rows: list[UsageRow]) -> list[str]:
    lines = [
        "| group | runs | calls | input_tokens | output_tokens | total_tokens | estimated Kimi K2.5 cost |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.group,
                    format_int(row.runs),
                    format_int(row.calls),
                    format_int(row.input_tokens),
                    format_int(row.output_tokens),
                    format_int(row.total_tokens),
                    cny_range(row),
                ]
            )
            + " |"
        )
    return lines


def total_row(group: str, rows: list[UsageRow]) -> UsageRow:
    return UsageRow(
        group=group,
        runs=sum(row.runs for row in rows),
        calls=sum(row.calls for row in rows),
        input_tokens=sum(row.input_tokens for row in rows),
        output_tokens=sum(row.output_tokens for row in rows),
    )


def render_markdown(
    recorded_rows: list[UsageRow],
    partial_rows: list[UsageRow],
    remaining_row: UsageRow | None,
    unmetered_runs: int,
) -> str:
    recorded_total = total_row("Recorded subtotal", recorded_rows)
    known_total = total_row("Recorded plus estimated stopped attempts", recorded_rows + partial_rows)

    lines = [
        "# API Budget Summary",
        "",
        "This table summarizes local Kimi API usage from saved `run_config.json` files. It does not make API calls.",
        "",
        "Pricing basis checked on 2026-06-01 from Kimi documentation: Kimi K2.5 input is CNY 0.70/1M tokens for cache hits or CNY 4.00/1M tokens for cache misses; output is CNY 21.00/1M tokens. The cost column is therefore a cache-hit to cache-miss input range.",
        "",
        "Kimi rate-limit basis checked on 2026-06-01: Tier0 has 1.5M tokens per day; Tier1 starts at CNY 50 cumulative recharge and removes the daily token cap. The completed full MATH `manual_v1` run is larger than the Tier0 daily cap, so a Tier1 account or equivalent quota is required to reproduce it in one day.",
        "",
        "## Recorded Usage",
        "",
    ]
    lines.extend(render_usage_table(recorded_rows + [recorded_total]))

    lines.extend(
        [
            "",
            "## Estimated Unmetered Usage",
            "",
            f"{unmetered_runs} early smoke/debug run configs predate reliable token accounting and are not assigned a cost here. The stopped full MATH `manual_v1` attempt did not write a usage file, so it is estimated from the 50-example validation run.",
            "",
        ]
    )
    lines.extend(render_usage_table(partial_rows + [known_total]))

    lines.extend(["", "## Remaining Required API Budget", ""])
    if remaining_row is None:
        lines.append("No required API run remains for the assignment experiments. Additional Kimi budget is only needed for optional follow-up ablations or prompt tuning.")
    else:
        lines.extend(render_usage_table([remaining_row]))
        lines.extend(
            [
                "",
                "Recommendation: keep at least CNY 50 available before resuming full MATH `manual_v1`; CNY 80-100 leaves room for retries or a small follow-up validation run.",
            ]
        )
    lines.extend(
        [
            "",
            "Sources: `report/evidence/math_validate50/manual_v1/run_config.json`, `report/evidence/math_test_baselines/direct/run_config.json`, `experiments/chunked_runs/MATH/manual_v1/math-test-manual-v1/run_config.json`, and saved run configs under `experiments/runs/`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    manual_config = read_json(args.manual_validate_run / "run_config.json")
    direct_test_config = read_json(args.direct_test_run / "run_config.json")
    recorded_rows, unmetered_runs = load_recorded_usage(args.runs_dir)
    manual_test_row = completed_manual_run(args.manual_test_run)
    if manual_test_row is not None:
        recorded_rows.append(manual_test_row)
        recorded_rows = sorted(recorded_rows, key=lambda row: row.group)
    partial_rows = estimate_partial_runs(args.runs_dir, manual_config)
    remaining_row = None if manual_test_row is not None else estimate_remaining_manual_run(manual_config, direct_test_config)
    markdown = render_markdown(recorded_rows, partial_rows, remaining_row, unmetered_runs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
