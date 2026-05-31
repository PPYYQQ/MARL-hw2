#!/usr/bin/env python3
"""Export cited experiment artifacts from ignored run directories."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path("report/evidence")


@dataclass(frozen=True)
class EvidenceRun:
    group: str
    method: str
    source: Path


EVIDENCE_RUNS = [
    EvidenceRun("math_validate50", "direct", Path("experiments/runs/MATH/direct/20260531_001748")),
    EvidenceRun("math_validate50", "cot", Path("experiments/runs/MATH/cot/20260531_001748")),
    EvidenceRun("math_validate50", "manual_v1", Path("experiments/runs/MATH/manual_v1/20260531_002230")),
    EvidenceRun("math_validate50", "ablation_single", Path("experiments/runs/MATH/ablation_single/20260531_002230")),
    EvidenceRun("humaneval_test", "direct", Path("experiments/runs/HumanEval/direct/20260531_004920")),
    EvidenceRun("humaneval_test", "cot", Path("experiments/runs/HumanEval/cot/20260531_004920")),
    EvidenceRun("humaneval_test", "manual_v1", Path("experiments/runs/HumanEval/manual_v1/20260531_005625")),
    EvidenceRun(
        "humaneval_test",
        "ablation_no_public_test",
        Path("experiments/runs/HumanEval/ablation_no_public_test/20260531_005625"),
    ),
    EvidenceRun("math_test_baselines", "direct", Path("experiments/runs/MATH/direct/20260531_102239")),
    EvidenceRun("math_test_baselines", "cot", Path("experiments/runs/MATH/cot/20260531_102239")),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--clean", action="store_true", help="Remove the output directory before exporting.")
    return parser.parse_args()


def find_single_csv(run_dir: Path) -> Path:
    csv_paths = sorted(run_dir.glob("*.csv"), key=lambda path: path.stat().st_mtime)
    if not csv_paths:
        raise FileNotFoundError(f"No CSV found in {run_dir}")
    return csv_paths[-1]


def summarize_csv(csv_path: Path) -> dict[str, object]:
    scores: list[float] = []
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            scores.append(float(row.get("score", 0) or 0))
    return {
        "csv_file": csv_path.name,
        "rows": len(scores),
        "raw_average_score": sum(scores) / len(scores) if scores else 0.0,
    }


def summarize_usage(usage_path: Path) -> dict[str, object]:
    with usage_path.open(encoding="utf-8") as usage_file:
        usage = json.load(usage_file)
    return {
        "total_input_tokens": usage.get("total_input_tokens", 0),
        "total_output_tokens": usage.get("total_output_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "total_cost": usage.get("total_cost", 0.0),
        "call_count": usage.get("call_count", 0),
    }


def export_run(run: EvidenceRun, output_root: Path) -> dict[str, object]:
    source_dir = REPO_ROOT / run.source
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Missing run directory: {run.source}")

    target_dir = output_root / run.group / run.method
    target_dir.mkdir(parents=True, exist_ok=True)

    csv_path = find_single_csv(source_dir)
    run_config_path = source_dir / "run_config.json"
    llm_usage_path = source_dir / "llm_usage.json"
    log_path = source_dir / "log.json"

    shutil.copy2(csv_path, target_dir / csv_path.name)
    shutil.copy2(run_config_path, target_dir / "run_config.json")
    if log_path.is_file():
        shutil.copy2(log_path, target_dir / "log.json")

    usage_summary = summarize_usage(llm_usage_path) if llm_usage_path.is_file() else {}
    if usage_summary:
        (target_dir / "llm_usage_summary.json").write_text(
            json.dumps(usage_summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    csv_summary = summarize_csv(csv_path)
    return {
        "group": run.group,
        "method": run.method,
        "source": run.source.as_posix(),
        "target": target_dir.relative_to(REPO_ROOT).as_posix(),
        **csv_summary,
        **usage_summary,
    }


def write_manifest(output_root: Path, entries: list[dict[str, object]]) -> None:
    lines = [
        "# Experiment Evidence Manifest",
        "",
        "This directory contains copied artifacts for the experiment runs cited in the report tables.",
        "Generated files come from ignored `experiments/runs/` directories so the submission can include raw evidence without tracking every debug run.",
        "For MATH rows, `raw_average_score` is the original CSV score; report tables may use `experiments/collect_results.py --rescore-math` with the current evaluator.",
        "",
        "| group | method | rows | raw_average_score | calls | tokens | target |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            "| {group} | {method} | {rows} | {raw_average_score:.5f} | {call_count} | {total_tokens} | {target} |".format(
                **entry
            )
        )
    (output_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_root = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    if args.clean and output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    entries = [export_run(run, output_root) for run in EVIDENCE_RUNS]
    write_manifest(output_root, entries)
    print(f"Exported {len(entries)} evidence runs to {output_root.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
