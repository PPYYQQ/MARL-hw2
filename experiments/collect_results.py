#!/usr/bin/env python3
"""Collect AFlow experiment CSV outputs into a Markdown summary table."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from statistics import mean
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("experiments/runs"))
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--dataset", choices=["MATH", "HumanEval"], default=None)
    parser.add_argument("--split", choices=["validate", "test"], default=None)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--latest-only", action="store_true", help="Keep only the newest CSV per dataset/method/model/split.")
    parser.add_argument(
        "--rescore-math",
        action="store_true",
        help="Recompute MATH scores from saved predictions with the current MATH evaluator.",
    )
    return parser.parse_args()


def load_math_benchmark() -> Any:
    aflow_path = Path(__file__).resolve().parents[1] / "AFlow"
    sys.path.insert(0, str(aflow_path))
    from benchmarks.math import MATHBenchmark

    return MATHBenchmark("MATH", "", "")


def read_scores(csv_path: Path, dataset: str, math_benchmark: Any = None) -> tuple[float, float, int]:
    scores: list[float] = []
    costs: list[float] = []
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if math_benchmark and dataset == "MATH" and row.get("expected_output") and row.get("prediction"):
                score, _ = math_benchmark.calculate_score(row["expected_output"], row["prediction"])
                scores.append(float(score))
            else:
                scores.append(float(row.get("score", 0) or 0))
            costs.append(float(row.get("cost", 0) or 0))
    total_cost = max(costs) if costs else 0.0
    return mean(scores) if scores else 0.0, total_cost, len(scores)


def find_run_rows(runs_dir: Path, rescore_math: bool = False) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    math_benchmark = load_math_benchmark() if rescore_math else None
    for config_path in sorted(runs_dir.glob("**/run_config.json")):
        run_dir = config_path.parent
        with config_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
        dataset = config.get("dataset", "")

        csv_paths = sorted(run_dir.glob("*.csv"))
        for csv_path in csv_paths:
            score, total_cost, sample_count = read_scores(csv_path, dataset, math_benchmark)
            rows.append(
                {
                    "dataset": dataset,
                    "method": config.get("baseline") or config.get("workflow", ""),
                    "model": config.get("model", ""),
                    "split": config.get("split", ""),
                    "samples": str(sample_count),
                    "score": f"{score:.5f}",
                    "total_cost": f"{total_cost:.5f}",
                    "calls": str(config.get("llm_call_count") or ""),
                    "input_tokens": str(config.get("total_input_tokens") or ""),
                    "output_tokens": str(config.get("total_output_tokens") or ""),
                    "tokens": str(config.get("total_tokens") or ""),
                    "csv": str(csv_path),
                    "_mtime": str(csv_path.stat().st_mtime),
                }
            )
    return rows


def keep_latest(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    latest_by_key: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["dataset"], row["method"], row["model"], row["split"])
        previous = latest_by_key.get(key)
        if previous is None or float(row["_mtime"]) > float(previous["_mtime"]):
            latest_by_key[key] = row
    return sorted(latest_by_key.values(), key=lambda row: (row["dataset"], row["method"], row["model"], row["split"]))


def filter_rows(
    rows: list[dict[str, str]],
    dataset: str | None,
    split: str | None,
    sample_size: int | None,
) -> list[dict[str, str]]:
    filtered_rows = rows
    if dataset:
        filtered_rows = [row for row in filtered_rows if row["dataset"] == dataset]
    if split:
        filtered_rows = [row for row in filtered_rows if row["split"] == split]
    if sample_size is not None:
        filtered_rows = [row for row in filtered_rows if row["samples"] == str(sample_size)]
    return filtered_rows


def render_markdown(rows: list[dict[str, str]]) -> str:
    headers = [
        "dataset",
        "method",
        "model",
        "split",
        "samples",
        "score",
        "calls",
        "input_tokens",
        "output_tokens",
        "tokens",
        "total_cost",
        "csv",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[header] for header in headers) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    rows = find_run_rows(args.runs_dir, args.rescore_math)
    rows = filter_rows(rows, args.dataset, args.split, args.sample_size)
    if args.latest_only:
        rows = keep_latest(rows)
    markdown = render_markdown(rows)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
