#!/usr/bin/env python3
"""Compare saved MATH runs with the current evaluator and render failure tables."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class ProblemResult:
    index: int
    question: str
    reference_answer: str
    predicted_answer: str
    score: int


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
        help="Named run directory in the form method=experiments/runs/MATH/method/timestamp.",
    )
    parser.add_argument("--baseline", required=True, help="Method name used for fixed/regression counts.")
    parser.add_argument("--output", type=Path, default=None, help="Optional Markdown output path.")
    parser.add_argument("--limit", type=int, default=30, help="Maximum detailed disagreement rows to render.")
    return parser.parse_args()


def load_math_benchmark() -> Any:
    aflow_path = Path(__file__).resolve().parents[1] / "AFlow"
    sys.path.insert(0, str(aflow_path))
    from benchmarks.math import MATHBenchmark

    return MATHBenchmark("MATH", "", "")


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


def load_run(name: str, run_dir: Path, benchmark: Any) -> MethodRun:
    config_path = run_dir / "run_config.json"
    with config_path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if config.get("dataset") != "MATH":
        raise ValueError(f"{run_dir} is not a MATH run")

    indices = list(config.get("indices") or [])
    csv_path = find_single_csv(run_dir)
    results: dict[int, ProblemResult] = {}
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    if len(rows) != len(indices):
        raise ValueError(f"{run_dir} has {len(rows)} CSV rows but {len(indices)} indices")

    for index, row in zip(indices, rows):
        expected_output = row["expected_output"]
        prediction = row["prediction"]
        score, predicted_answer = benchmark.calculate_score(expected_output, prediction)
        reference_answer = benchmark.extract_reference_answer(expected_output)
        results[int(index)] = ProblemResult(
            index=int(index),
            question=row["question"],
            reference_answer=reference_answer,
            predicted_answer=predicted_answer,
            score=int(score),
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


def escape_cell(value: object, max_length: int = 90) -> str:
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


def render_interpretation_notes(runs: list[MethodRun], all_indices: list[int]) -> list[str]:
    lines = ["", "## Interpretation Notes", ""]

    all_failed_indices = [
        index for index in all_indices if all(method_run.results[index].score == 0 for method_run in runs)
    ]
    if all_failed_indices:
        details = []
        for index in all_failed_indices:
            reference = runs[0].results[index].reference_answer
            answers = sorted({method_run.results[index].predicted_answer for method_run in runs})
            details.append(
                f"index `{index}` has reference `{reference}` and extracted predictions "
                f"{', '.join(f'`{answer}`' for answer in answers)}"
            )
        lines.append(
            "- Shared failures across every compared method are unlikely to be fixed by rescoring alone: "
            + "; ".join(details)
            + "."
        )
    else:
        lines.append("- No compared index failed under every method.")

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
            raise ValueError(f"{method_run.name} does not use the same sample indices as {baseline_name}")

    lines = [
        "# MATH 50-Sample Failure Analysis",
        "",
        f"Split: `{baseline_run.split}`. Sample size: `{baseline_run.sample_size}`. Baseline for comparisons: `{baseline_name}`.",
        "Scores are recomputed from saved predictions with the current MATH evaluator.",
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
        reference = baseline_run.results[index].reference_answer
        score_bits = [f"{method_run.name}:{method_run.results[index].score}" for method_run in runs]
        answer_bits = [f"{method_run.name}:{method_run.results[index].predicted_answer}" for method_run in runs]
        detail_rows.append(
            [
                index,
                reference,
                ", ".join(score_bits),
                "; ".join(answer_bits),
                baseline_run.results[index].question,
            ]
        )

    lines.extend(render_table(["index", "reference", "scores", "extracted_answers", "question"], detail_rows))
    if len(disagreement_indices) > limit:
        lines.append(f"\nOnly the first {limit} of {len(disagreement_indices)} disagreement cases are shown.")

    lines.extend(render_interpretation_notes(runs, all_indices))

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    benchmark = load_math_benchmark()
    runs = [load_run(name, path, benchmark) for name, path in (parse_named_run(value) for value in args.run)]
    markdown = render_markdown(runs, args.baseline, args.limit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
