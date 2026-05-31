#!/usr/bin/env python3
"""Run a local, no-API audit of assignment submission readiness."""

from __future__ import annotations

import argparse
import os
import py_compile
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "AGENTS.md",
    "PROGRESS.md",
    "AFlow_UPSTREAM.md",
    "AFlow/config/config2.kimi.example.yaml",
    "AFlow/scripts/async_llm.py",
    "AFlow/benchmarks/math.py",
    "AFlow/workspace/MATH/workflows/manual_v1/graph.py",
    "AFlow/workspace/MATH/workflows/ablation_single/graph.py",
    "AFlow/workspace/HumanEval/workflows/manual_v1/graph.py",
    "AFlow/workspace/HumanEval/workflows/ablation_no_public_test/graph.py",
    "experiments/run_baselines.py",
    "experiments/run_workflows.py",
    "experiments/run_chunked_workflows.py",
    "experiments/collect_results.py",
    "experiments/analyze_math_failures.py",
    "experiments/analyze_humaneval_failures.py",
    "experiments/package_submission.py",
    "experiments/README.md",
    "docs/SETUP.md",
    "docs/ABLATIONS.md",
    "docs/CHUNKED_WORKFLOWS.md",
    "docs/SUBMISSION_STATUS.md",
    "report/main.tex",
    "report/references.bib",
    "report/tables/validation20_results.md",
    "report/tables/math_validation50_results.md",
    "report/tables/math_validation50_failure_analysis.md",
    "report/tables/humaneval_test_results.md",
    "report/tables/humaneval_test_failure_analysis.md",
    "report/tables/math_test_baselines.md",
]


PYTHON_FILES = [
    "experiments/run_baselines.py",
    "experiments/run_workflows.py",
    "experiments/run_chunked_workflows.py",
    "experiments/collect_results.py",
    "experiments/analyze_math_failures.py",
    "experiments/analyze_humaneval_failures.py",
    "experiments/package_submission.py",
    "experiments/audit_submission.py",
    "AFlow/benchmarks/math.py",
]


REPORT_SECTIONS = [
    r"\section{Introduction}",
    r"\section{AFlow Engineering Summary}",
    r"\section{Environment Setup}",
    r"\section{Baselines}",
    r"\section{Manual Workflow Design}",
    r"\section{Validation Results}",
    r"\section{Remaining Experiments}",
    r"\section{Limitations}",
    r"\section{Conclusion}",
]


EXPECTED_TABLE_SNIPPETS = {
    "report/tables/validation20_results.md": [
        "| MATH | manual_v1 | kimi-k2.5 | validate | 20 | 1.00000",
        "| MATH | cot | kimi-k2.5 | validate | 20 | 0.95000",
    ],
    "report/tables/math_validation50_results.md": [
        "| MATH | manual_v1 | kimi-k2.5 | validate | 50 | 0.98000",
        "| MATH | direct | kimi-k2.5 | validate | 50 | 0.96000",
    ],
    "report/tables/math_validation50_failure_analysis.md": [
        "| manual_v1 | 0.98000 | 1 | 2 | 0 | 1 | 250 | 349515 |",
        "| 91 | \\frac{25 \\sqrt{10}}{4}",
    ],
    "report/tables/humaneval_test_results.md": [
        "| HumanEval | ablation_no_public_test | kimi-k2.5 | test | 131 | 0.99237",
        "| HumanEval | manual_v1 | kimi-k2.5 | test | 131 | 0.98473",
    ],
    "report/tables/humaneval_test_failure_analysis.md": [
        "| no_public | 0.99237 | 1 | 3 | 1 | 0 | 409 | 303127 |",
        "| 120 | sort_array | direct:1, cot:0, manual_v1:0, no_public:1 |",
    ],
    "report/tables/math_test_baselines.md": [
        "| MATH | direct | kimi-k2.5 | test | 486 | 0.88889",
        "| MATH | cot | kimi-k2.5 | test | 486 | 0.89300",
    ],
}


@dataclass
class AuditResult:
    passed: list[str]
    warnings: list[str]
    failures: list[str]

    def pass_check(self, message: str) -> None:
        self.passed.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    return parser.parse_args()


def read_text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def git_ls_files(path: str) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", path],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line]


def check_required_files(result: AuditResult) -> None:
    missing = [path for path in REQUIRED_FILES if not (REPO_ROOT / path).is_file()]
    if missing:
        result.fail("Missing required files: " + ", ".join(missing))
    else:
        result.pass_check(f"Found {len(REQUIRED_FILES)} required files")


def check_python_compile(result: AuditResult) -> None:
    failed: list[str] = []
    for path in PYTHON_FILES:
        try:
            py_compile.compile(str(REPO_ROOT / path), doraise=True)
        except py_compile.PyCompileError as exc:
            failed.append(f"{path}: {exc.msg}")
    if failed:
        result.fail("Python compile failures: " + "; ".join(failed))
    else:
        result.pass_check(f"Compiled {len(PYTHON_FILES)} Python files")


def check_report_sections(result: AuditResult) -> None:
    report_text = read_text("report/main.tex")
    missing = [section for section in REPORT_SECTIONS if section not in report_text]
    if missing:
        result.fail("Missing report sections: " + ", ".join(missing))
    else:
        result.pass_check(f"Report has {len(REPORT_SECTIONS)} required sections")


def check_result_tables(result: AuditResult) -> None:
    missing_snippets: list[str] = []
    for path, snippets in EXPECTED_TABLE_SNIPPETS.items():
        table_text = read_text(path)
        for snippet in snippets:
            if snippet not in table_text:
                missing_snippets.append(f"{path}: {snippet}")
    if missing_snippets:
        result.fail("Result table snippets missing: " + "; ".join(missing_snippets))
    else:
        result.pass_check(f"Verified {len(EXPECTED_TABLE_SNIPPETS)} result tables")


def check_secret_hygiene(result: AuditResult) -> None:
    tracked_local_config = git_ls_files("AFlow/config/config2.yaml")
    if tracked_local_config:
        result.fail("Local secret config is tracked: AFlow/config/config2.yaml")
    else:
        result.pass_check("Local Kimi config is not tracked")

    tracked_env_files = git_ls_files(".env") + git_ls_files("**/.env")
    if tracked_env_files:
        result.fail("Environment secret files are tracked: " + ", ".join(tracked_env_files))
    else:
        result.pass_check("No .env files are tracked")


def check_external_blockers(result: AuditResult) -> None:
    report_text = read_text("report/main.tex")
    if "Student Name" in report_text or "Student ID: TODO" in report_text or "TODO@example.com" in report_text:
        result.warn("Report still contains student metadata placeholders")
    else:
        result.pass_check("Report student metadata is filled")

    if not shutil.which("pdflatex") and not shutil.which("xelatex"):
        result.warn("No local pdflatex/xelatex executable found")
    else:
        result.pass_check("A LaTeX compiler is available")

    if not os.environ.get("KIMI_API_KEY"):
        result.warn("KIMI_API_KEY is not set in this shell")
    else:
        result.pass_check("KIMI_API_KEY is set")

    if not (REPO_ROOT / "report/tables/math_test_manual_chunked.md").is_file():
        result.warn("Full MATH manual_v1 test table is not available yet")
    else:
        result.pass_check("Full MATH manual_v1 test table exists")


def print_result(result: AuditResult, strict: bool) -> None:
    print("Submission audit")
    print("================")
    for message in result.passed:
        print(f"PASS: {message}")
    for message in result.warnings:
        print(f"WARN: {message}")
    for message in result.failures:
        print(f"FAIL: {message}")

    warning_count = len(result.warnings)
    failure_count = len(result.failures) + (warning_count if strict else 0)
    print(f"Summary: {len(result.passed)} passed, {warning_count} warnings, {len(result.failures)} failures")
    if strict and warning_count:
        print("Strict mode treats warnings as failures")
    sys.exit(1 if failure_count else 0)


def main() -> None:
    args = parse_args()
    result = AuditResult(passed=[], warnings=[], failures=[])
    check_required_files(result)
    check_python_compile(result)
    check_report_sections(result)
    check_result_tables(result)
    check_secret_hygiene(result)
    check_external_blockers(result)
    print_result(result, args.strict)


if __name__ == "__main__":
    main()
