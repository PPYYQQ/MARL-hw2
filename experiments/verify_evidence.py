#!/usr/bin/env python3
"""Verify tracked experiment evidence against cited report results."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = REPO_ROOT / "report/evidence"


@dataclass(frozen=True)
class ExpectedRun:
    group: str
    method: str
    dataset: str
    split: str
    samples: int
    score: float
    calls: int
    tokens: int


EXPECTED_RUNS = [
    ExpectedRun("math_validate50", "direct", "MATH", "validate", 50, 0.96000, 50, 38140),
    ExpectedRun("math_validate50", "cot", "MATH", "validate", 50, 0.94000, 50, 39806),
    ExpectedRun("math_validate50", "manual_v1", "MATH", "validate", 50, 0.98000, 250, 349515),
    ExpectedRun("math_validate50", "ablation_single", "MATH", "validate", 50, 0.94000, 100, 114590),
    ExpectedRun("humaneval_test", "direct", "HumanEval", "test", 131, 0.97710, 131, 48941),
    ExpectedRun("humaneval_test", "cot", "HumanEval", "test", 131, 0.98473, 131, 120573),
    ExpectedRun("humaneval_test", "manual_v1", "HumanEval", "test", 131, 0.98473, 287, 134751),
    ExpectedRun("humaneval_test", "ablation_no_public_test", "HumanEval", "test", 131, 0.99237, 409, 303127),
    ExpectedRun("math_test_baselines", "direct", "MATH", "test", 486, 0.88889, 486, 425052),
    ExpectedRun("math_test_baselines", "cot", "MATH", "test", 486, 0.89300, 486, 459130),
    ExpectedRun("math_test_manual", "manual_v1", "MATH", "test", 486, 0.91770, 2431, 3786936),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("report/tables/evidence_verification.md"))
    return parser.parse_args()


def load_math_benchmark() -> Any:
    aflow_path = REPO_ROOT / "AFlow"
    sys.path.insert(0, str(aflow_path))
    from benchmarks.math import MATHBenchmark

    return MATHBenchmark("MATH", "", "")


def find_single_csv(run_dir: Path) -> Path:
    csv_paths = sorted(run_dir.glob("*.csv"), key=lambda path: path.name)
    if len(csv_paths) != 1:
        raise ValueError(f"Expected one CSV in {run_dir}, found {len(csv_paths)}")
    return csv_paths[0]


def read_config(run_dir: Path) -> dict[str, Any]:
    with (run_dir / "run_config.json").open(encoding="utf-8") as config_file:
        return json.load(config_file)


def read_usage_summary(run_dir: Path) -> dict[str, Any]:
    with (run_dir / "llm_usage_summary.json").open(encoding="utf-8") as usage_file:
        return json.load(usage_file)


def calculate_score(expected: ExpectedRun, csv_path: Path, math_benchmark: Any) -> tuple[int, float]:
    scores: list[float] = []
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if expected.dataset == "MATH":
                score, _ = math_benchmark.calculate_score(row["expected_output"], row["prediction"])
                scores.append(float(score))
            else:
                scores.append(float(row.get("score", 0) or 0))
    return len(scores), mean(scores) if scores else 0.0


def verify_run(expected: ExpectedRun, math_benchmark: Any) -> dict[str, object]:
    run_dir = EVIDENCE_ROOT / expected.group / expected.method
    csv_path = find_single_csv(run_dir)
    config = read_config(run_dir)
    usage = read_usage_summary(run_dir)
    rows, score = calculate_score(expected, csv_path, math_benchmark)

    actual_method = config.get("baseline") or config.get("workflow")
    checks = {
        "dataset": config.get("dataset") == expected.dataset,
        "method": actual_method == expected.method,
        "split": config.get("split") == expected.split,
        "rows": rows == expected.samples,
        "score": abs(score - expected.score) < 0.00001,
        "calls": usage.get("call_count") == expected.calls == config.get("llm_call_count"),
        "tokens": usage.get("total_tokens") == expected.tokens == config.get("total_tokens"),
    }
    status = "ok" if all(checks.values()) else "fail:" + ",".join(name for name, passed in checks.items() if not passed)
    return {
        "group": expected.group,
        "method": expected.method,
        "rows": rows,
        "score": score,
        "expected_score": expected.score,
        "calls": usage.get("call_count"),
        "tokens": usage.get("total_tokens"),
        "status": status,
    }


def render_markdown(results: list[dict[str, object]]) -> str:
    lines = [
        "# Evidence Verification",
        "",
        "This table is computed from tracked `report/evidence/` CSV/config/token-summary files.",
        "MATH rows are rescored with the current evaluator; HumanEval rows use saved evaluator scores.",
        "",
        "| group | method | rows | score | expected_score | calls | tokens | status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            "| {group} | {method} | {rows} | {score:.5f} | {expected_score:.5f} | {calls} | {tokens} | {status} |".format(
                **result
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    math_benchmark = load_math_benchmark()
    results = [verify_run(expected, math_benchmark) for expected in EXPECTED_RUNS]
    markdown = render_markdown(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")

    failed = [result for result in results if result["status"] != "ok"]
    if failed:
        print(markdown, end="")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
