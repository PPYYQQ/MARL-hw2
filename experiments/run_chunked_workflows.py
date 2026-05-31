#!/usr/bin/env python3
"""Run a tracked workflow in checkpointed chunks."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

from run_workflows import (
    AFLOW_ROOT,
    REPO_ROOT,
    build_benchmark,
    default_data_path,
    load_workflow_class,
    save_usage_summary,
    select_indices,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["MATH", "HumanEval"], required=True)
    parser.add_argument("--workflow", default="manual_v1")
    parser.add_argument("--model", default="kimi-k2.5")
    parser.add_argument("--split", choices=["validate", "test"], default="validate")
    parser.add_argument("--data-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/chunked_runs"))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--chunk-size", type=int, default=20)
    parser.add_argument("--start-chunk", type=int, default=0)
    parser.add_argument("--max-chunks", type=int, default=None)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--sample-seed", type=int, default=0)
    parser.add_argument("--indices", default=None, help="Comma-separated zero-based sample indices.")
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true", help="Print chunk plan without running model calls.")
    return parser.parse_args()


def chunk_indices(indices: list[int], chunk_size: int) -> list[list[int]]:
    if chunk_size <= 0:
        raise ValueError("chunk-size must be positive")
    return [indices[start : start + chunk_size] for start in range(0, len(indices), chunk_size)]


def latest_csv(run_dir: Path) -> Path:
    csv_paths = sorted(run_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV result found in {run_dir}")
    return csv_paths[-1]


def read_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_completed_chunks(run_dir: Path) -> list[dict[str, Any]]:
    chunks = []
    for config_path in sorted(run_dir.glob("chunk_*/chunk_config.json")):
        with config_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
        if config.get("status") == "completed":
            chunks.append(config)
    return chunks


def chunk_dir_for(run_dir: Path, chunk_number: int, indices: list[int]) -> Path:
    return run_dir / f"chunk_{chunk_number:04d}_{indices[0]}_{indices[-1]}"


def chunk_is_completed(run_dir: Path, chunk_number: int, indices: list[int]) -> bool:
    chunk_config_path = chunk_dir_for(run_dir, chunk_number, indices) / "chunk_config.json"
    if not chunk_config_path.exists():
        return False
    with chunk_config_path.open(encoding="utf-8") as config_file:
        chunk_config = json.load(config_file)
    return chunk_config.get("status") == "completed"


def aggregate_chunks(run_dir: Path, args: argparse.Namespace, all_indices: list[int], total_chunks: int) -> dict[str, Any]:
    chunk_configs = load_completed_chunks(run_dir)
    rows: list[dict[str, str]] = []
    completed_indices: list[int] = []
    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    call_count = 0
    total_cost = 0.0

    for chunk_config in chunk_configs:
        rows.extend(read_csv_rows(Path(chunk_config["csv_path"])))
        completed_indices.extend(chunk_config["indices"])
        total_input_tokens += int(chunk_config.get("total_input_tokens") or 0)
        total_output_tokens += int(chunk_config.get("total_output_tokens") or 0)
        total_tokens += int(chunk_config.get("total_tokens") or 0)
        call_count += int(chunk_config.get("llm_call_count") or 0)
        total_cost += float(chunk_config.get("llm_total_cost") or 0.0)

    score_values = [float(row.get("score", 0) or 0) for row in rows]
    costs = [float(row.get("cost", 0) or 0) for row in rows]
    aggregate_csv = run_dir / "aggregate.csv"
    write_csv(aggregate_csv, rows)

    usage_summary = {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "call_count": call_count,
        "total_cost": total_cost,
    }
    (run_dir / "llm_usage.json").write_text(json.dumps(usage_summary, indent=2), encoding="utf-8")

    config = {
        "dataset": args.dataset,
        "workflow": args.workflow,
        "model": args.model,
        "split": args.split,
        "chunked": True,
        "run_id": run_dir.name,
        "chunk_size": args.chunk_size,
        "sample_size": len(rows),
        "sample_seed": args.sample_seed,
        "indices": sorted(completed_indices),
        "planned_indices": all_indices,
        "completed_chunks": len(chunk_configs),
        "total_chunks": total_chunks,
        "is_complete": len(chunk_configs) == total_chunks and len(rows) == len(all_indices),
        "average_score": mean(score_values) if score_values else 0.0,
        "average_cost": (max(costs) / len(rows)) if rows and costs else 0.0,
        "total_cost": max(costs) if costs else 0.0,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "llm_call_count": call_count,
        "llm_total_cost": total_cost,
        "llm_usage_path": str(run_dir / "llm_usage.json"),
        "csv_path": str(aggregate_csv),
    }
    (run_dir / "run_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config


async def run_chunk(
    args: argparse.Namespace,
    data_path: Path,
    run_dir: Path,
    chunk_number: int,
    indices: list[int],
) -> dict[str, Any]:
    from scripts.async_llm import LLMsConfig

    chunk_dir = chunk_dir_for(run_dir, chunk_number, indices)
    chunk_config_path = chunk_dir / "chunk_config.json"
    if chunk_config_path.exists():
        with chunk_config_path.open(encoding="utf-8") as config_file:
            chunk_config = json.load(config_file)
        if chunk_config.get("status") == "completed":
            print(f"Skipping completed chunk {chunk_number}: {indices[0]}-{indices[-1]}")
            return chunk_config

    chunk_dir.mkdir(parents=True, exist_ok=True)
    benchmark = build_benchmark(args.dataset, data_path, chunk_dir)
    data = await benchmark.load_data(indices)

    llm_config = LLMsConfig.default().get(args.model)
    workflow_class = load_workflow_class(args.dataset, args.workflow)
    workflow = workflow_class(name=args.workflow, llm_config=llm_config, dataset=args.dataset)
    results = await benchmark.evaluate_all_problems(data, workflow, max_concurrent_tasks=args.max_concurrency)
    average_score, average_cost, total_cost = benchmark.save_results_to_csv(results, benchmark.get_result_columns())
    usage_summary = save_usage_summary(workflow, chunk_dir)
    csv_path = latest_csv(chunk_dir)

    chunk_config = {
        "status": "completed",
        "dataset": args.dataset,
        "workflow": args.workflow,
        "model": args.model,
        "split": args.split,
        "chunk_number": chunk_number,
        "indices": indices,
        "sample_size": len(data),
        "average_score": average_score,
        "average_cost": average_cost,
        "total_cost": total_cost,
        "total_input_tokens": usage_summary.get("total_input_tokens"),
        "total_output_tokens": usage_summary.get("total_output_tokens"),
        "total_tokens": usage_summary.get("total_tokens"),
        "llm_call_count": usage_summary.get("call_count"),
        "llm_total_cost": usage_summary.get("total_cost"),
        "llm_usage_path": str(chunk_dir / "llm_usage.json") if usage_summary else None,
        "csv_path": str(csv_path),
    }
    chunk_config_path.write_text(json.dumps(chunk_config, indent=2), encoding="utf-8")
    print(json.dumps(chunk_config, indent=2))
    return chunk_config


async def run(args: argparse.Namespace) -> None:
    data_path = args.data_path or default_data_path(args.dataset, args.split)
    if not data_path.is_absolute():
        data_path = (REPO_ROOT / data_path).resolve()
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {data_path}")

    output_dir = args.output_dir if args.output_dir.is_absolute() else REPO_ROOT / args.output_dir
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / args.dataset / args.workflow / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    os.chdir(AFLOW_ROOT)
    benchmark = build_benchmark(args.dataset, data_path, run_dir)
    all_data = await benchmark.load_data()
    selected_indices = select_indices(len(all_data), args.sample_size, args.sample_seed, args.indices)
    if selected_indices is None:
        selected_indices = list(range(len(all_data)))
    chunks = chunk_indices(selected_indices, args.chunk_size)
    selected_chunks = [(number, chunk) for number, chunk in enumerate(chunks) if number >= args.start_chunk]
    if args.max_chunks is not None:
        selected_chunks = [
            (number, chunk)
            for number, chunk in selected_chunks
            if not chunk_is_completed(run_dir, number, chunk)
        ][: args.max_chunks]

    plan = {
        "dataset": args.dataset,
        "workflow": args.workflow,
        "split": args.split,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "chunk_size": args.chunk_size,
        "start_chunk": args.start_chunk,
        "max_chunks": args.max_chunks,
        "total_indices": len(selected_indices),
        "total_chunks": len(chunks),
        "selected_chunks": len(selected_chunks),
        "chunks": [{"chunk_number": number, "indices": chunk} for number, chunk in enumerate(chunks)],
    }
    (run_dir / "manifest.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return

    for chunk_number, chunk in selected_chunks:
        await run_chunk(args, data_path, run_dir, chunk_number, chunk)
        aggregate_config = aggregate_chunks(run_dir, args, selected_indices, len(chunks))
        print(
            f"Checkpoint: {aggregate_config['completed_chunks']}/{aggregate_config['total_chunks']} chunks, "
            f"score={aggregate_config['average_score']:.5f}, tokens={aggregate_config['total_tokens']}"
        )


def main() -> None:
    args = parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
