#!/usr/bin/env python3
"""Verify that submission-audit warnings are limited to known blockers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

ALLOWED_WARNINGS = {
    "Report still contains student metadata placeholders",
    "KIMI_API_KEY is not set in this shell",
    "Full MATH manual_v1 test table is not available yet",
}


def audit_lines() -> tuple[int, list[str]]:
    completed = subprocess.run(
        [sys.executable, "experiments/audit_submission.py"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return completed.returncode, completed.stdout.splitlines()


def main() -> None:
    returncode, lines = audit_lines()
    warnings = [line.removeprefix("WARN: ") for line in lines if line.startswith("WARN: ")]
    failures = [line.removeprefix("FAIL: ") for line in lines if line.startswith("FAIL: ")]
    unknown_warnings = [warning for warning in warnings if warning not in ALLOWED_WARNINGS]

    if returncode != 0 or failures:
        print("FAIL: submission audit reported failures")
        for failure in failures:
            print(f"FAIL: {failure}")
        sys.exit(1)

    if unknown_warnings:
        print("FAIL: submission audit reported unexpected warnings")
        for warning in unknown_warnings:
            print(f"WARN: {warning}")
        sys.exit(1)

    if warnings:
        print("PASS: audit warnings are limited to known external blockers")
        for warning in warnings:
            print(f"WARN: {warning}")
    else:
        print("PASS: submission audit has no warnings")


if __name__ == "__main__":
    main()
