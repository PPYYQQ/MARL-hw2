#!/usr/bin/env python3
"""Collect AFlow experiment CSV outputs into a Markdown summary table."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("experiments/runs"))
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def read_scores(csv_path: Path) -> tuple[float, float, int]:
    scores: list[float] = []
    costs: list[float] = []
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            scores.append(float(row.get("score", 0) or 0))
            costs.append(float(row.get("cost", 0) or 0))
    total_cost = max(costs) if costs else 0.0
    return mean(scores) if scores else 0.0, total_cost, len(scores)


def find_run_rows(runs_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for config_path in sorted(runs_dir.glob("**/run_config.json")):
        run_dir = config_path.parent
        with config_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)

        csv_paths = sorted(run_dir.glob("*.csv"))
        for csv_path in csv_paths:
            score, total_cost, sample_count = read_scores(csv_path)
            rows.append(
                {
                    "dataset": config.get("dataset", ""),
                    "method": config.get("baseline") or config.get("workflow", ""),
                    "model": config.get("model", ""),
                    "split": config.get("split", ""),
                    "samples": str(sample_count),
                    "score": f"{score:.5f}",
                    "total_cost": f"{total_cost:.5f}",
                    "csv": str(csv_path),
                }
            )
    return rows


def render_markdown(rows: list[dict[str, str]]) -> str:
    headers = ["dataset", "method", "model", "split", "samples", "score", "total_cost", "csv"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[header] for header in headers) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    rows = find_run_rows(args.runs_dir)
    markdown = render_markdown(rows)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
