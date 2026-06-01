#!/usr/bin/env python3
"""Verify a Markdown result table contains an expected experiment row."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, required=True, help="Markdown table path.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--samples", type=int, required=True)
    parser.add_argument("--min-calls", type=int, default=1)
    parser.add_argument("--min-tokens", type=int, default=1)
    parser.add_argument("--require-model", default=None, help="Substring required in the model column.")
    return parser.parse_args()


def parse_markdown_table(table_path: Path) -> list[dict[str, str]]:
    if not table_path.is_file():
        raise SystemExit(f"FAIL: Table does not exist: {table_path}")

    table_lines = [
        line.strip()
        for line in table_path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    if len(table_lines) < 3:
        raise SystemExit(f"FAIL: Markdown table has no data rows: {table_path}")

    headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            raise SystemExit(f"FAIL: Row has {len(cells)} cells but expected {len(headers)}: {line}")
        rows.append(dict(zip(headers, cells)))
    return rows


def int_field(row: dict[str, str], field: str) -> int:
    value = row.get(field, "").replace(",", "")
    try:
        return int(value)
    except ValueError as exc:
        raise SystemExit(f"FAIL: Field {field} is not an integer: {row.get(field, '')}") from exc


def float_field(row: dict[str, str], field: str) -> float:
    try:
        return float(row.get(field, ""))
    except ValueError as exc:
        raise SystemExit(f"FAIL: Field {field} is not a float: {row.get(field, '')}") from exc


def main() -> None:
    args = parse_args()
    rows = parse_markdown_table(args.table)
    matches = [
        row
        for row in rows
        if row.get("dataset") == args.dataset
        and row.get("method") == args.method
        and row.get("split") == args.split
        and row.get("samples") == str(args.samples)
    ]
    if len(matches) != 1:
        print(
            f"FAIL: Expected exactly one {args.dataset}/{args.method}/{args.split}/{args.samples} row, "
            f"found {len(matches)}"
        )
        sys.exit(1)

    row = matches[0]
    if args.require_model and args.require_model not in row.get("model", ""):
        print(f"FAIL: Model field does not include {args.require_model!r}: {row.get('model', '')}")
        sys.exit(1)

    score = float_field(row, "score")
    calls = int_field(row, "calls")
    tokens = int_field(row, "tokens")
    if not 0.0 <= score <= 1.0:
        print(f"FAIL: Score is outside [0, 1]: {score}")
        sys.exit(1)
    if calls < args.min_calls:
        print(f"FAIL: calls={calls} is below required minimum {args.min_calls}")
        sys.exit(1)
    if tokens < args.min_tokens:
        print(f"FAIL: tokens={tokens} is below required minimum {args.min_tokens}")
        sys.exit(1)

    print(
        f"PASS: Verified {args.dataset}/{args.method}/{args.split} table row "
        f"samples={args.samples} score={score:.5f} calls={calls} tokens={tokens}"
    )


if __name__ == "__main__":
    main()
