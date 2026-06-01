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
    "README.md",
    "Makefile",
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
    "experiments/analyze_efficiency.py",
    "experiments/analyze_api_budget.py",
    "experiments/estimate_math_manual_test.py",
    "experiments/summarize_chunked_run.py",
    "experiments/verify_chunked_plan.py",
    "experiments/verify_report_pdf.py",
    "experiments/verify_audit_warnings.py",
    "experiments/verify_git_sync.py",
    "experiments/export_evidence.py",
    "experiments/verify_evidence.py",
    "experiments/fill_report_metadata.py",
    "experiments/finalize_submission.py",
    "experiments/analyze_math_failures.py",
    "experiments/analyze_humaneval_failures.py",
    "experiments/package_submission.py",
    "experiments/verify_submission_package.py",
    "experiments/README.md",
    "docs/SETUP.md",
    "docs/ABLATIONS.md",
    "docs/CHUNKED_WORKFLOWS.md",
    "docs/COMPLETION_AUDIT.md",
    "docs/EXPERIMENT_COMMANDS.md",
    "docs/FINAL_HANDOFF_CN.md",
    "docs/REQUIREMENT_RUN_MATRIX.md",
    "docs/PAPER_NOTES.md",
    "docs/SUBMISSION_STATUS.md",
    "report/main.tex",
    "report/references.bib",
    "report/tables/validation20_results.md",
    "report/tables/math_validation50_results.md",
    "report/tables/efficiency_summary.md",
    "report/tables/api_budget_summary.md",
    "report/tables/math_manual_test_estimate.md",
    "report/tables/evidence_verification.md",
    "report/tables/math_validation50_failure_analysis.md",
    "report/tables/humaneval_test_results.md",
    "report/tables/humaneval_test_failure_analysis.md",
    "report/tables/math_test_baselines.md",
    "report/evidence/README.md",
]


PYTHON_FILES = [
    "experiments/run_baselines.py",
    "experiments/run_workflows.py",
    "experiments/run_chunked_workflows.py",
    "experiments/collect_results.py",
    "experiments/analyze_efficiency.py",
    "experiments/analyze_api_budget.py",
    "experiments/estimate_math_manual_test.py",
    "experiments/summarize_chunked_run.py",
    "experiments/verify_chunked_plan.py",
    "experiments/verify_report_pdf.py",
    "experiments/verify_audit_warnings.py",
    "experiments/verify_git_sync.py",
    "experiments/export_evidence.py",
    "experiments/verify_evidence.py",
    "experiments/fill_report_metadata.py",
    "experiments/finalize_submission.py",
    "experiments/analyze_math_failures.py",
    "experiments/analyze_humaneval_failures.py",
    "experiments/package_submission.py",
    "experiments/verify_submission_package.py",
    "experiments/audit_submission.py",
    "AFlow/benchmarks/math.py",
]


REPORT_SECTIONS = [
    r"\section{Introduction}",
    r"\section{Research Context}",
    r"\section{AFlow Engineering Summary}",
    r"\section{Environment Setup}",
    r"\section{Baselines}",
    r"\section{Manual Workflow Design}",
    r"\section{Workflow Algorithm Details}",
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
    "report/tables/efficiency_summary.md": [
        "| MATH validate50 | manual_v1 | 0.98000 | +0.02000 | 250 | 5.00x | 349515 | 9.16x |",
        "| HumanEval test | ablation_no_public_test | 0.99237 | +0.01527 | 409 | 3.12x | 303127 | 6.19x |",
    ],
    "report/tables/api_budget_summary.md": [
        "| MATH full direct/CoT baselines | 2 | 972 | 107,606 | 776,576 | 884,182 | CNY 16.38-16.74 |",
        "| Remaining full MATH manual_v1 test estimate | 1 | 2,430 | 1,822,432 | 1,574,854 | 3,397,286 | CNY 34.35-40.36 |",
    ],
    "report/tables/evidence_verification.md": [
        "| math_validate50 | manual_v1 | 50 | 0.98000 | 0.98000 | 250 | 349515 | ok |",
        "| humaneval_test | ablation_no_public_test | 131 | 0.99237 | 0.99237 | 409 | 303127 | ok |",
        "| math_test_baselines | cot | 486 | 0.89300 | 0.89300 | 486 | 459130 | ok |",
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
    "report/evidence/README.md": [
        "| math_test_baselines | direct | 486 | 0.88889 | 486 | 425052 | report/evidence/math_test_baselines/direct |",
        "| humaneval_test | ablation_no_public_test | 131 | 0.99237 | 409 | 303127 | report/evidence/humaneval_test/ablation_no_public_test |",
    ],
}


EXPECTED_HANDOFF_SNIPPETS = {
    "docs/FINAL_HANDOFF_CN.md": [
        "## 当前可交付状态",
        "## 最终提交前必须补的信息",
        "make finalize-submission-dry-run FINAL_NAME=",
        "make finalize-submission FINAL_NAME=",
        "make handoff-check",
        "make verify-github-sync",
        "make post-push-check",
        "make verify-known-warnings",
        "make ready-to-submit-check",
        "MATH_MANUAL_MAX_CHUNKS=3 make resume-math-manual-chunk",
    ],
    "docs/REQUIREMENT_RUN_MATRIX.md": [
        "## 中文交接矩阵",
        "| MATH 多智能体 workflow | 设计 workflow，并证明优于 direct 和 CoT |",
        "## 额度使用矩阵",
        "| Remaining full MATH `manual_v1` estimate | 1 | 2,430 | 3,397,286 | CNY 34.35-40.36 |",
    ],
    "docs/COMPLETION_AUDIT.md": [
        "## Remaining External Inputs",
        "`make finalize-submission-dry-run FINAL_NAME=\"...\" FINAL_STUDENT_ID=\"...\" FINAL_EMAIL=\"...\"`",
        "`make finalize-submission FINAL_NAME=\"...\" FINAL_STUDENT_ID=\"...\" FINAL_EMAIL=\"...\"`",
        "`make handoff-check`",
        "`make post-push-check`",
        "`make verify-known-warnings`",
        "`make ready-to-submit-check`",
        "Full MATH `manual_v1` test result",
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
    untracked = [path for path in REQUIRED_FILES if (REPO_ROOT / path).is_file() and not git_ls_files(path)]
    if missing:
        result.fail("Missing required files: " + ", ".join(missing))
    elif untracked:
        result.fail("Required files are not tracked by Git: " + ", ".join(untracked))
    else:
        result.pass_check(f"Found {len(REQUIRED_FILES)} tracked required files")


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


def check_handoff_docs(result: AuditResult) -> None:
    missing_snippets: list[str] = []
    for path, snippets in EXPECTED_HANDOFF_SNIPPETS.items():
        doc_text = read_text(path)
        for snippet in snippets:
            if snippet not in doc_text:
                missing_snippets.append(f"{path}: {snippet}")
    if missing_snippets:
        result.fail("Handoff document snippets missing: " + "; ".join(missing_snippets))
    else:
        result.pass_check(f"Verified {len(EXPECTED_HANDOFF_SNIPPETS)} handoff documents")


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

    compiler = next((name for name in ("pdflatex", "xelatex", "tectonic") if shutil.which(name)), None)
    if compiler:
        result.pass_check(f"LaTeX compiler is available: {compiler}")
    else:
        result.warn("No local LaTeX compiler found")

    if (REPO_ROOT / "report/main.pdf").is_file():
        completed = subprocess.run(
            [sys.executable, "experiments/verify_report_pdf.py"],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if completed.returncode == 0:
            message = completed.stdout.strip()
            if message.startswith("PASS: "):
                message = message.removeprefix("PASS: ")
            result.pass_check(message)
        else:
            result.warn((completed.stdout + completed.stderr).strip())
    else:
        result.warn("Report PDF is not built yet")

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
    check_handoff_docs(result)
    check_secret_hygiene(result)
    check_external_blockers(result)
    print_result(result, args.strict)


if __name__ == "__main__":
    main()
