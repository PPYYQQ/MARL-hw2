#!/usr/bin/env python3
"""Compare saved HumanEval runs and render failure/disagreement tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


@dataclass(frozen=True)
class ProblemResult:
    index: int
    entry_point: str
    score: int
    failure_reason: str


@dataclass(frozen=True)
class MethodRun:
    name: str
    path: Path
    split: str
    sample_size: int
    calls: int
    tokens: int
    results: dict[int, ProblemResult]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Named run directory in the form method=experiments/runs/HumanEval/method/timestamp.",
    )
    parser.add_argument("--baseline", required=True, help="Method name used for fixed/regression counts.")
    parser.add_argument("--output", type=Path, default=None, help="Optional Markdown output path.")
    parser.add_argument("--limit", type=int, default=40, help="Maximum detailed disagreement rows to render.")
    return parser.parse_args()


def parse_named_run(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError(f"Run must use name=path format: {value}")
    name, path_text = value.split("=", 1)
    if not name.strip():
        raise ValueError(f"Run name is empty: {value}")
    return name.strip(), Path(path_text)


def find_single_csv(run_dir: Path) -> Path:
    csv_paths = sorted(run_dir.glob("*.csv"), key=lambda path: path.stat().st_mtime)
    if not csv_paths:
        raise FileNotFoundError(f"No CSV found in {run_dir}")
    return csv_paths[-1]


def extract_entry_point(prompt: str) -> str:
    match = re.search(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", prompt)
    return match.group(1) if match else "unknown"


def extract_failure_reason(expected_output: str, score: int) -> str:
    if score:
        return "pass"
    reason = expected_output.split("Correct Solution:", 1)[0].strip()
    first_line = reason.splitlines()[0].strip() if reason else "failed"
    return first_line or "failed"


def load_run(name: str, run_dir: Path) -> MethodRun:
    config_path = run_dir / "run_config.json"
    with config_path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if config.get("dataset") != "HumanEval":
        raise ValueError(f"{run_dir} is not a HumanEval run")

    csv_path = find_single_csv(run_dir)
    results: dict[int, ProblemResult] = {}
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        for index, row in enumerate(csv.DictReader(csv_file)):
            score = int(float(row.get("score", 0) or 0))
            results[index] = ProblemResult(
                index=index,
                entry_point=extract_entry_point(row["inputs"]),
                score=score,
                failure_reason=extract_failure_reason(row["expected_output"], score),
            )

    return MethodRun(
        name=name,
        path=run_dir,
        split=str(config.get("split", "")),
        sample_size=int(config.get("sample_size") or len(results)),
        calls=int(config.get("llm_call_count") or 0),
        tokens=int(config.get("total_tokens") or 0),
        results=results,
    )


def escape_cell(value: object, max_length: int = 110) -> str:
    text = " ".join(str(value).split()).replace("|", "\\|")
    if len(text) > max_length:
        return text[: max_length - 3].rstrip() + "..."
    return text


def render_table(headers: list[str], rows: list[list[object]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_cell(value) for value in row) + " |")
    return lines


def score_mean(method_run: MethodRun) -> float:
    return mean(result.score for result in method_run.results.values()) if method_run.results else 0.0


def compare_to_baseline(method_run: MethodRun, baseline_run: MethodRun) -> tuple[int, int, int]:
    fixed = 0
    regressions = 0
    shared_failures = 0
    for index, baseline_result in baseline_run.results.items():
        method_result = method_run.results[index]
        if baseline_result.score == 0 and method_result.score == 1:
            fixed += 1
        elif baseline_result.score == 1 and method_result.score == 0:
            regressions += 1
        elif baseline_result.score == 0 and method_result.score == 0:
            shared_failures += 1
    return fixed, regressions, shared_failures


def render_markdown(runs: list[MethodRun], baseline_name: str, limit: int) -> str:
    runs_by_name = {method_run.name: method_run for method_run in runs}
    if baseline_name not in runs_by_name:
        raise ValueError(f"Baseline {baseline_name!r} was not provided")

    baseline_run = runs_by_name[baseline_name]
    all_indices = sorted(baseline_run.results)
    for method_run in runs:
        if sorted(method_run.results) != all_indices:
            raise ValueError(f"{method_run.name} does not use the same row indices as {baseline_name}")

    lines = [
        "# HumanEval Full-Test Failure Analysis",
        "",
        f"Split: `{baseline_run.split}`. Sample size: `{baseline_run.sample_size}`. Baseline for comparisons: `{baseline_name}`.",
        "Scores are read from the saved HumanEval evaluator outputs.",
        "",
        "## Summary",
        "",
    ]

    summary_rows: list[list[object]] = []
    for method_run in runs:
        fixed, regressions, shared_failures = compare_to_baseline(method_run, baseline_run)
        failures = sum(1 for result in method_run.results.values() if result.score == 0)
        summary_rows.append(
            [
                method_run.name,
                f"{score_mean(method_run):.5f}",
                failures,
                fixed,
                regressions,
                shared_failures,
                method_run.calls,
                method_run.tokens,
            ]
        )
    lines.extend(
        render_table(
            [
                "method",
                "score",
                "failures",
                f"fixes_vs_{baseline_name}",
                f"regressions_vs_{baseline_name}",
                f"shared_failures_vs_{baseline_name}",
                "calls",
                "tokens",
            ],
            summary_rows,
        )
    )

    disagreement_indices = [
        index
        for index in all_indices
        if any(method_run.results[index].score == 0 for method_run in runs)
    ]
    lines.extend(["", "## Failure And Disagreement Cases", ""])

    detail_rows: list[list[object]] = []
    for index in disagreement_indices[:limit]:
        baseline_result = baseline_run.results[index]
        score_bits = [f"{method_run.name}:{method_run.results[index].score}" for method_run in runs]
        failure_bits = [
            f"{method_run.name}:{method_run.results[index].failure_reason}"
            for method_run in runs
            if method_run.results[index].score == 0
        ]
        detail_rows.append(
            [
                index,
                baseline_result.entry_point,
                ", ".join(score_bits),
                "; ".join(failure_bits),
            ]
        )

    lines.extend(render_table(["index", "entry_point", "scores", "failure_reasons"], detail_rows))
    if len(disagreement_indices) > limit:
        lines.append(f"\nOnly the first {limit} of {len(disagreement_indices)} disagreement cases are shown.")

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    runs = [load_run(name, path) for name, path in (parse_named_run(value) for value in args.run)]
    markdown = render_markdown(runs, args.baseline, args.limit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
