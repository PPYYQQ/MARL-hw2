#!/usr/bin/env python3
"""Summarize checkpointed chunked workflow progress without making API calls."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("experiments/chunked_runs"))
    parser.add_argument("--dataset", default="MATH")
    parser.add_argument("--workflow", default="manual_v1")
    parser.add_argument("--run-id", default="math-test-manual-v1")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file_handle:
        return json.load(file_handle)


def chunk_dir_for(run_dir: Path, chunk_number: int, indices: list[int]) -> Path:
    return run_dir / f"chunk_{chunk_number:04d}_{indices[0]}_{indices[-1]}"


def chunk_status(run_dir: Path, chunk: dict[str, Any]) -> tuple[str, Path]:
    chunk_number = int(chunk["chunk_number"])
    indices = list(chunk["indices"])
    chunk_dir = chunk_dir_for(run_dir, chunk_number, indices)
    config_path = chunk_dir / "chunk_config.json"
    if not config_path.exists():
        return "missing", config_path
    config = read_json(config_path)
    return str(config.get("status") or "unknown"), config_path


def main() -> None:
    args = parse_args()
    runs_dir = args.runs_dir if args.runs_dir.is_absolute() else REPO_ROOT / args.runs_dir
    run_dir = runs_dir / args.dataset / args.workflow / args.run_id
    manifest_path = run_dir / "manifest.json"

    if not manifest_path.exists():
        print(f"Chunked run not started: {run_dir}")
        print("Run `make dry-run-math-manual-chunks` to write the planned manifest.")
        return

    manifest = read_json(manifest_path)
    chunks = list(manifest.get("chunks") or [])
    status_counts: Counter[str] = Counter()
    next_chunk: dict[str, Any] | None = None
    next_status = ""

    for chunk in chunks:
        status, _ = chunk_status(run_dir, chunk)
        status_counts[status] += 1
        if next_chunk is None and status != "completed":
            next_chunk = chunk
            next_status = status

    total_chunks = int(manifest.get("total_chunks") or len(chunks))
    completed = status_counts.get("completed", 0)
    failed_quota = status_counts.get("failed_quota", 0)
    missing = status_counts.get("missing", 0)
    unknown = sum(count for status, count in status_counts.items() if status not in {"completed", "failed_quota", "missing"})

    aggregate_path = run_dir / "run_config.json"
    aggregate = read_json(aggregate_path) if aggregate_path.exists() else {}

    print(f"Run: {args.dataset}/{args.workflow}/{args.run_id}")
    print(f"Directory: {run_dir}")
    print(f"Chunks: {completed}/{total_chunks} completed, {failed_quota} quota-failed, {missing} missing, {unknown} other")
    if aggregate:
        print(
            "Aggregate: "
            f"score={float(aggregate.get('average_score') or 0):.5f}, "
            f"tokens={int(aggregate.get('total_tokens') or 0)}, "
            f"calls={int(aggregate.get('llm_call_count') or 0)}, "
            f"complete={bool(aggregate.get('is_complete'))}"
        )
    else:
        print("Aggregate: not available yet")

    if next_chunk is None:
        print("Next chunk: none; all planned chunks are completed")
    else:
        indices = list(next_chunk["indices"])
        print(
            "Next chunk: "
            f"{int(next_chunk['chunk_number'])} "
            f"indices {indices[0]}-{indices[-1]} "
            f"status={next_status}"
        )


if __name__ == "__main__":
    main()
