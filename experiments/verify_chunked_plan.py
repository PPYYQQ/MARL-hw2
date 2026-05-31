#!/usr/bin/env python3
"""Verify a chunked workflow run plan without calling the model API."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from run_chunked_workflows import chunk_indices
from run_workflows import REPO_ROOT, default_data_path, select_indices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["MATH", "HumanEval"], required=True)
    parser.add_argument("--split", choices=["validate", "test"], default="validate")
    parser.add_argument("--data-path", type=Path, default=None)
    parser.add_argument("--chunk-size", type=int, default=20)
    parser.add_argument("--sample-size", type=int, default=None)
    parser.add_argument("--sample-seed", type=int, default=0)
    parser.add_argument("--indices", default=None, help="Comma-separated zero-based sample indices.")
    parser.add_argument("--expect-total-indices", type=int, default=None)
    parser.add_argument("--expect-total-chunks", type=int, default=None)
    parser.add_argument("--expect-first-index", type=int, default=None)
    parser.add_argument("--expect-last-index", type=int, default=None)
    parser.add_argument("--expect-contiguous", action="store_true")
    return parser.parse_args()


def resolve_data_path(args: argparse.Namespace) -> Path:
    data_path = args.data_path or default_data_path(args.dataset, args.split)
    if not data_path.is_absolute():
        data_path = REPO_ROOT / data_path
    return data_path.resolve()


def count_jsonl_rows(data_path: Path) -> int:
    if not data_path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {data_path}")
    with data_path.open(encoding="utf-8") as jsonl_file:
        return sum(1 for line in jsonl_file if line.strip())


def planned_indices(total_rows: int, args: argparse.Namespace) -> list[int]:
    indices = select_indices(total_rows, args.sample_size, args.sample_seed, args.indices)
    if indices is None:
        return list(range(total_rows))
    return indices


def validate_plan(args: argparse.Namespace, total_rows: int, indices: list[int], chunks: list[list[int]]) -> list[str]:
    failures: list[str] = []
    if len(set(indices)) != len(indices):
        failures.append("Selected indices contain duplicates")

    invalid_indices = [index for index in indices if index < 0 or index >= total_rows]
    if invalid_indices:
        failures.append("Selected indices outside dataset bounds: " + ", ".join(map(str, invalid_indices[:10])))

    if args.expect_total_indices is not None and len(indices) != args.expect_total_indices:
        failures.append(f"Expected {args.expect_total_indices} indices, found {len(indices)}")

    if args.expect_total_chunks is not None and len(chunks) != args.expect_total_chunks:
        failures.append(f"Expected {args.expect_total_chunks} chunks, found {len(chunks)}")

    if indices:
        if args.expect_first_index is not None and indices[0] != args.expect_first_index:
            failures.append(f"Expected first index {args.expect_first_index}, found {indices[0]}")
        if args.expect_last_index is not None and indices[-1] != args.expect_last_index:
            failures.append(f"Expected last index {args.expect_last_index}, found {indices[-1]}")

    if args.expect_contiguous and indices:
        expected_indices = list(range(indices[0], indices[-1] + 1))
        if indices != expected_indices:
            failures.append("Selected indices are not contiguous in planned order")

    return failures


def print_summary(args: argparse.Namespace, data_path: Path, total_rows: int, indices: list[int], chunks: list[list[int]]) -> None:
    print(f"Dataset: {args.dataset} {args.split}")
    print(f"Data path: {data_path}")
    print(f"Dataset rows: {total_rows}")
    print(f"Planned indices: {len(indices)}")
    print(f"Chunk size: {args.chunk_size}")
    print(f"Total chunks: {len(chunks)}")
    if chunks:
        first_chunk = chunks[0]
        last_chunk = chunks[-1]
        print(f"First chunk: {first_chunk[0]}-{first_chunk[-1]} ({len(first_chunk)} items)")
        print(f"Last chunk: {last_chunk[0]}-{last_chunk[-1]} ({len(last_chunk)} items)")


def main() -> None:
    args = parse_args()
    data_path = resolve_data_path(args)
    total_rows = count_jsonl_rows(data_path)
    indices = planned_indices(total_rows, args)
    chunks = chunk_indices(indices, args.chunk_size)
    failures = validate_plan(args, total_rows, indices, chunks)

    print_summary(args, data_path, total_rows, indices, chunks)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        sys.exit(1)

    print(f"PASS: Chunked plan covers {len(indices)} indices in {len(chunks)} chunks")


if __name__ == "__main__":
    main()
