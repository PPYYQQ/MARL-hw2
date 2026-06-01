#!/usr/bin/env python3
"""Verify the assignment run matrix agrees with tracked result tables."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = "docs/REQUIREMENT_RUN_MATRIX.md"

RESULT_ROWS = [
    {
        "table": "report/tables/math_test_baselines.md",
        "dataset": "MATH",
        "method": "direct",
        "display_method": "direct",
        "split": "test",
        "samples": "486",
    },
    {
        "table": "report/tables/math_test_baselines.md",
        "dataset": "MATH",
        "method": "cot",
        "display_method": "CoT",
        "split": "test",
        "samples": "486",
    },
    {
        "table": "report/tables/math_validation50_results.md",
        "dataset": "MATH",
        "method": "direct",
        "display_method": "direct",
        "split": "validate",
        "samples": "50",
    },
    {
        "table": "report/tables/math_validation50_results.md",
        "dataset": "MATH",
        "method": "cot",
        "display_method": "CoT",
        "split": "validate",
        "samples": "50",
    },
    {
        "table": "report/tables/math_validation50_results.md",
        "dataset": "MATH",
        "method": "manual_v1",
        "display_method": "`manual_v1`",
        "split": "validate",
        "samples": "50",
    },
    {
        "table": "report/tables/math_validation50_results.md",
        "dataset": "MATH",
        "method": "ablation_single",
        "display_method": "`ablation_single`",
        "split": "validate",
        "samples": "50",
    },
    {
        "table": "report/tables/humaneval_test_results.md",
        "dataset": "HumanEval",
        "method": "direct",
        "display_method": "direct",
        "split": "test",
        "samples": "131",
    },
    {
        "table": "report/tables/humaneval_test_results.md",
        "dataset": "HumanEval",
        "method": "cot",
        "display_method": "CoT",
        "split": "test",
        "samples": "131",
    },
    {
        "table": "report/tables/humaneval_test_results.md",
        "dataset": "HumanEval",
        "method": "manual_v1",
        "display_method": "`manual_v1`",
        "split": "test",
        "samples": "131",
    },
    {
        "table": "report/tables/humaneval_test_results.md",
        "dataset": "HumanEval",
        "method": "ablation_no_public_test",
        "display_method": "`ablation_no_public_test`",
        "split": "test",
        "samples": "131",
    },
]

BUDGET_ROWS = [
    ("20-example validation experiments", "20-example validation experiments"),
    ("3-example smoke and ablation checks", "3-example smoke and ablation checks"),
    ("HumanEval full test experiments", "HumanEval full test experiments"),
    ("MATH 50-example validation experiments", "MATH 50-example validation experiments"),
    ("MATH full direct/CoT baselines", "MATH full direct/CoT baselines"),
    ("Recorded subtotal", "Recorded subtotal"),
    ("Unmetered stopped MATH manual_v1 attempt (15 examples)", "Stopped MATH `manual_v1` attempt estimate"),
    ("Remaining full MATH manual_v1 test estimate", "Remaining full MATH `manual_v1` estimate"),
]

REQUIRED_STATUS_SNIPPETS = [
    "| Direct baseline | MATH-500 和 HumanEval 的 direct prompting 基线 |",
    "| CoT baseline | MATH-500 和 HumanEval 的 chain-of-thought 基线 |",
    "| MATH 多智能体 workflow | 设计 workflow，并证明优于 direct 和 CoT |",
    "| HumanEval 多智能体 workflow | 设计 workflow，并证明优于 base model |",
    "| Ablation 消融 | 对最终 workflow 做简化版对比 |",
    "| Full benchmark comparison | 尽可能全量比较 direct、CoT、workflow、ablation |",
    "| Token/efficiency analysis | 统计调用量、token 和精度/成本权衡 |",
    "| Report/package | PDF 报告、代码、证据、提交 zip |",
    "| Missing MATH workflow full test | `make resume-math-manual-chunk`，完成后 `make collect-math-manual-chunked` |",
    "| Local handoff verification | `make post-push-check` |",
    "| Final course package | `make finalize-submission FINAL_NAME=... FINAL_STUDENT_ID=... FINAL_EMAIL=...` |",
    "make verify-requirement-matrix",
]

PENDING_MATH_SNIPPETS = [
    "full test 未完成",
    "full test pending quota",
    "需要 Kimi 余额或新 API key",
    "0/25 chunks 完成",
]


def read_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def is_separator_row(cells: list[str]) -> bool:
    return all(cell and set(cell) <= {"-", ":", " "} and "-" in cell for cell in cells)


def parse_markdown_rows(path: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    table_lines: list[str] = []
    for line in read_text(path).splitlines() + [""]:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines.append(stripped)
            continue
        if len(table_lines) >= 3:
            headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
            for row_line in table_lines[1:]:
                cells = [cell.strip() for cell in row_line.strip("|").split("|")]
                if is_separator_row(cells):
                    continue
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
        table_lines = []
    return rows


def find_row(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    matches = [row for row in rows if all(row.get(field) == value for field, value in criteria.items())]
    if len(matches) != 1:
        criteria_text = ", ".join(f"{field}={value}" for field, value in criteria.items())
        raise SystemExit(f"FAIL: Expected one row matching {criteria_text}, found {len(matches)}")
    return matches[0]


def format_int(value: str) -> str:
    return f"{int(value.replace(',', '')):,}"


def verify_result_matrix(matrix_text: str) -> int:
    checked = 0
    parsed_tables: dict[str, list[dict[str, str]]] = {}
    for spec in RESULT_ROWS:
        table = spec["table"]
        parsed_tables.setdefault(table, parse_markdown_rows(table))
        row = find_row(
            parsed_tables[table],
            dataset=spec["dataset"],
            method=spec["method"],
            split=spec["split"],
            samples=spec["samples"],
        )
        expected = (
            f"| {spec['dataset']} | {spec['display_method']} | {spec['split']}, {spec['samples']} | "
            f"`{row['score']}` | {format_int(row['calls'])} | {format_int(row['tokens'])} | `{table}` |"
        )
        if expected not in matrix_text:
            raise SystemExit(f"FAIL: Missing or stale key-result matrix row: {expected}")
        checked += 1
    return checked


def verify_budget_matrix(matrix_text: str) -> int:
    rows = parse_markdown_rows("report/tables/api_budget_summary.md")
    checked = 0
    for source_group, matrix_group in BUDGET_ROWS:
        row = find_row(rows, group=source_group)
        expected = (
            f"| {matrix_group} | {format_int(row['runs'])} | {format_int(row['calls'])} | "
            f"{format_int(row['total_tokens'])} | {row['estimated Kimi K2.5 cost']} |"
        )
        if expected not in matrix_text:
            raise SystemExit(f"FAIL: Missing or stale budget matrix row prefix: {expected}")
        checked += 1
    return checked


def verify_status_text(matrix_text: str) -> int:
    missing = [snippet for snippet in REQUIRED_STATUS_SNIPPETS if snippet not in matrix_text]
    if missing:
        raise SystemExit("FAIL: Missing requirement-matrix snippets: " + "; ".join(missing))

    full_math_table = REPO_ROOT / "report/tables/math_test_manual_chunked.md"
    if full_math_table.exists():
        if any(snippet in matrix_text for snippet in PENDING_MATH_SNIPPETS):
            raise SystemExit("FAIL: Full MATH manual table exists, but requirement matrix still says it is pending")
    else:
        missing_pending = [snippet for snippet in PENDING_MATH_SNIPPETS if snippet not in matrix_text]
        if missing_pending:
            raise SystemExit("FAIL: Missing pending full-MATH status snippets: " + "; ".join(missing_pending))
    return len(REQUIRED_STATUS_SNIPPETS)


def main() -> None:
    matrix_text = read_text(MATRIX_PATH)
    status_count = verify_status_text(matrix_text)
    result_count = verify_result_matrix(matrix_text)
    budget_count = verify_budget_matrix(matrix_text)
    print(
        "PASS: Requirement run matrix matches tracked status, "
        f"{result_count} result rows, and {budget_count} budget rows"
    )
    print(f"PASS: Verified {status_count} required matrix status snippets")


if __name__ == "__main__":
    main()
