#!/usr/bin/env python3
"""Verify the final report reflects the completed full MATH workflow result."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("report/main.tex"))
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--dataset", default="MATH")
    parser.add_argument("--method", default="manual_v1")
    parser.add_argument("--split", default="test")
    parser.add_argument("--samples", type=int, default=486)
    parser.add_argument("--forbidden-phrase", action="append", default=[])
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


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


def find_row(rows: list[dict[str, str]], args: argparse.Namespace) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row.get("dataset") == args.dataset
        and row.get("method") == args.method
        and row.get("split") == args.split
        and row.get("samples") == str(args.samples)
    ]
    if len(matches) != 1:
        raise SystemExit(
            f"FAIL: Expected exactly one {args.dataset}/{args.method}/{args.split}/{args.samples} row, "
            f"found {len(matches)}"
        )
    return matches[0]


def int_text(value: str) -> tuple[str, str]:
    integer = int(value.replace(",", ""))
    return str(integer), f"{integer:,}"


def require_any(report_text: str, label: str, options: tuple[str, ...]) -> None:
    if not any(option in report_text for option in options):
        joined = " or ".join(repr(option) for option in options)
        raise SystemExit(f"FAIL: Report does not mention {label}: expected {joined}")


def require_result_line(
    report_text: str,
    method_options: tuple[str, ...],
    score: str,
    call_options: tuple[str, ...],
    token_options: tuple[str, ...],
) -> None:
    for line in report_text.splitlines():
        if (
            any(method in line for method in method_options)
            and score in line
            and any(calls in line for calls in call_options)
            and any(tokens in line for tokens in token_options)
        ):
            return
    raise SystemExit("FAIL: Report does not contain one result line with method, score, calls, and tokens")


def main() -> None:
    args = parse_args()
    report_path = resolve(args.report)
    if not report_path.is_file():
        raise SystemExit(f"FAIL: Report source does not exist: {args.report}")

    row = find_row(parse_markdown_table(resolve(args.table)), args)
    report_text = report_path.read_text(encoding="utf-8")

    method_latex = args.method.replace("_", r"\_")
    method_options = (args.method, method_latex)
    call_options = int_text(row["calls"])
    token_options = int_text(row["tokens"])
    require_any(report_text, "method", method_options)
    require_any(report_text, "score", (row["score"],))
    require_any(report_text, "calls", call_options)
    require_any(report_text, "tokens", token_options)
    require_result_line(report_text, method_options, row["score"], call_options, token_options)

    forbidden_found = [phrase for phrase in args.forbidden_phrase if phrase in report_text]
    if forbidden_found:
        print("FAIL: Report still contains stale final-state text")
        for phrase in forbidden_found:
            print(f"- {phrase}")
        sys.exit(1)

    print(
        f"PASS: Report reflects {args.dataset}/{args.method}/{args.split} "
        f"score={row['score']} calls={row['calls']} tokens={row['tokens']}"
    )


if __name__ == "__main__":
    main()
