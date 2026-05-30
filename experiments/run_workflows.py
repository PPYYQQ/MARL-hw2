#!/usr/bin/env python3
"""Run a tracked AFlow workflow on an assignment benchmark."""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
AFLOW_ROOT = REPO_ROOT / "AFlow"
if str(AFLOW_ROOT) not in sys.path:
    sys.path.insert(0, str(AFLOW_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["MATH", "HumanEval"], required=True)
    parser.add_argument("--workflow", default="manual_v1")
    parser.add_argument("--model", default="kimi-k2.5")
    parser.add_argument("--split", choices=["validate", "test"], default="validate")
    parser.add_argument("--data-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/runs"))
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--sample-seed", type=int, default=0)
    parser.add_argument("--indices", default=None, help="Comma-separated zero-based sample indices.")
    parser.add_argument("--max-concurrency", type=int, default=4)
    return parser.parse_args()


def default_data_path(dataset: str, split: str) -> Path:
    filename = f"{dataset.lower()}_{split}.jsonl"
    return AFLOW_ROOT / "data" / "datasets" / filename


def select_indices(total_count: int, sample_size: int | None, sample_seed: int, indices: str | None) -> list[int] | None:
    if indices:
        return [int(index.strip()) for index in indices.split(",") if index.strip()]
    if sample_size is None:
        return None
    if sample_size > total_count:
        raise ValueError(f"sample-size {sample_size} exceeds dataset size {total_count}")
    sampler = random.Random(sample_seed)
    return sorted(sampler.sample(range(total_count), sample_size))


def build_benchmark(dataset: str, data_path: Path, log_path: Path):
    if dataset == "MATH":
        from benchmarks.math import MATHBenchmark

        return MATHBenchmark(name=dataset, file_path=str(data_path), log_path=str(log_path))
    if dataset == "HumanEval":
        from benchmarks.humaneval import HumanEvalBenchmark

        return HumanEvalBenchmark(name=dataset, file_path=str(data_path), log_path=str(log_path))
    raise ValueError(f"Unsupported dataset: {dataset}")


def load_workflow_class(dataset: str, workflow: str):
    module_name = f"workspace.{dataset}.workflows.{workflow}.graph"
    module = importlib.import_module(module_name)
    return module.Workflow


def save_usage_summary(workflow: Any, run_dir: Path) -> dict[str, Any]:
    llm = getattr(workflow, "llm", None)
    if llm is None:
        return {}
    usage_summary = llm.get_usage_summary()
    (run_dir / "llm_usage.json").write_text(json.dumps(usage_summary, indent=2), encoding="utf-8")
    return usage_summary


async def run(args: argparse.Namespace) -> None:
    from scripts.async_llm import LLMsConfig

    data_path = args.data_path or default_data_path(args.dataset, args.split)
    if not data_path.is_absolute():
        data_path = (REPO_ROOT / data_path).resolve()
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {data_path}")

    output_dir = args.output_dir if args.output_dir.is_absolute() else REPO_ROOT / args.output_dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / args.dataset / args.workflow / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    os.chdir(AFLOW_ROOT)
    benchmark = build_benchmark(args.dataset, data_path, run_dir)
    all_data = await benchmark.load_data()
    selected_indices = select_indices(len(all_data), args.sample_size, args.sample_seed, args.indices)
    data = await benchmark.load_data(selected_indices)

    llm_config = LLMsConfig.default().get(args.model)
    workflow_class = load_workflow_class(args.dataset, args.workflow)
    workflow = workflow_class(name=args.workflow, llm_config=llm_config, dataset=args.dataset)
    results = await benchmark.evaluate_all_problems(data, workflow, max_concurrent_tasks=args.max_concurrency)
    average_score, average_cost, total_cost = benchmark.save_results_to_csv(results, benchmark.get_result_columns())
    usage_summary = save_usage_summary(workflow, run_dir)

    config = {
        "dataset": args.dataset,
        "workflow": args.workflow,
        "model": args.model,
        "split": args.split,
        "data_path": str(data_path),
        "sample_size": len(data),
        "sample_seed": args.sample_seed,
        "indices": selected_indices,
        "max_concurrency": args.max_concurrency,
        "average_score": average_score,
        "average_cost": average_cost,
        "total_cost": total_cost,
        "total_input_tokens": usage_summary.get("total_input_tokens"),
        "total_output_tokens": usage_summary.get("total_output_tokens"),
        "total_tokens": usage_summary.get("total_tokens"),
        "llm_call_count": usage_summary.get("call_count"),
        "llm_total_cost": usage_summary.get("total_cost"),
        "llm_usage_path": str(run_dir / "llm_usage.json") if usage_summary else None,
    }
    (run_dir / "run_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(json.dumps(config, indent=2))


def main() -> None:
    args = parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
