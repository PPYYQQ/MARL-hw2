#!/usr/bin/env python3
"""Render score and token-efficiency comparisons from tracked result tables."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


DEFAULT_COMPARISONS = [
    ("MATH validate50", [Path("report/tables/math_validation50_results.md")], "direct"),
    ("HumanEval test", [Path("report/tables/humaneval_test_results.md")], "direct"),
    (
        "MATH test",
        [Path("report/tables/math_test_baselines.md"), Path("report/tables/math_test_manual_chunked.md")],
        "direct",
    ),
]


@dataclass(frozen=True)
class ResultRow:
    group: str
    method: str
    score: float
    calls: int
    tokens: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("report/tables/efficiency_summary.md"))
    return parser.parse_args()


def parse_int(value: str) -> int:
    return int(value.replace(",", "").strip())


def parse_markdown_table(path: Path, group: str) -> list[ResultRow]:
    rows: list[ResultRow] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    headers: list[str] | None = None
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(set(cell) <= {"-"} for cell in cells):
            continue
        if headers is None:
            headers = cells
            continue
        row = dict(zip(headers, cells))
        rows.append(
            ResultRow(
                group=group,
                method=row["method"],
                score=float(row["score"]),
                calls=parse_int(row["calls"]),
                tokens=parse_int(row["tokens"]),
            )
        )
    return rows


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|")


def render_markdown() -> str:
    headers = [
        "group",
        "method",
        "score",
        "delta_vs_direct",
        "calls",
        "call_multiplier",
        "tokens",
        "token_multiplier",
    ]
    lines = [
        "# Efficiency Summary",
        "",
        "Score deltas and multipliers are computed against the direct baseline within each result group.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for group, paths, baseline_method in DEFAULT_COMPARISONS:
        rows: list[ResultRow] = []
        for path in paths:
            if path.is_file():
                rows.extend(parse_markdown_table(path, group))
        baseline = next((row for row in rows if row.method == baseline_method), None)
        if baseline is None:
            path_text = ", ".join(path.as_posix() for path in paths)
            raise ValueError(f"Missing baseline {baseline_method!r} in {path_text}")
        for row in sorted(rows, key=lambda item: (item.group, item.method)):
            score_delta = row.score - baseline.score
            call_multiplier = row.calls / baseline.calls if baseline.calls else 0.0
            token_multiplier = row.tokens / baseline.tokens if baseline.tokens else 0.0
            lines.append(
                "| "
                + " | ".join(
                    escape_cell(value)
                    for value in [
                        row.group,
                        row.method,
                        f"{row.score:.5f}",
                        f"{score_delta:+.5f}",
                        row.calls,
                        f"{call_multiplier:.2f}x",
                        row.tokens,
                        f"{token_multiplier:.2f}x",
                    ]
                )
                + " |"
            )

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    markdown = render_markdown()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
