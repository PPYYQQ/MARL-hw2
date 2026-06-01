#!/usr/bin/env python3
"""Verify final report metadata validation rules."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from fill_report_metadata import validate_metadata


REPO_ROOT = Path(__file__).resolve().parents[1]


def expect_valid(name: str, student_id: str, email: str, allow_test_metadata: bool = False) -> list[str]:
    try:
        validate_metadata(name, student_id, email, allow_test_metadata=allow_test_metadata)
    except ValueError as exc:
        return [f"Expected valid metadata but got {exc}: {name!r}, {student_id!r}, {email!r}"]
    return []


def expect_invalid(name: str, student_id: str, email: str, allow_test_metadata: bool = False) -> list[str]:
    try:
        validate_metadata(name, student_id, email, allow_test_metadata=allow_test_metadata)
    except ValueError:
        return []
    return [f"Expected invalid metadata to fail: {name!r}, {student_id!r}, {email!r}"]


def verify_cli_guard() -> list[str]:
    completed = subprocess.run(
        [
            sys.executable,
            "experiments/finalize_submission.py",
            "--name",
            "Test Student",
            "--student-id",
            "TEST123",
            "--email",
            "test@example.com",
            "--allow-test-metadata",
        ],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    expected = "FAIL: --allow-test-metadata is only valid with --dry-run"
    if completed.returncode == 0 or expected not in completed.stdout:
        return ["Expected finalize_submission.py to reject --allow-test-metadata without --dry-run"]
    return []


def main() -> None:
    failures: list[str] = []

    failures.extend(expect_valid("Alice Zhang", "2400012345", "student@pku.edu.cn"))
    failures.extend(expect_valid("Test Student", "TEST123", "test@example.com", allow_test_metadata=True))

    invalid_cases = [
        ("Your Name", "2400012345", "student@pku.edu.cn"),
        ("your name", "2400012345", "student@pku.edu.cn"),
        ("Alice Zhang", "Your ID", "student@pku.edu.cn"),
        ("Alice Zhang", "<student_id>", "student@pku.edu.cn"),
        ("Alice Zhang", "TODO", "student@pku.edu.cn"),
        ("Alice Zhang", "2400012345", "you@example.com"),
        ("Alice Zhang", "2400012345", "student@example.com"),
        ("Test Student", "TEST123", "test@example.com"),
    ]
    for case in invalid_cases:
        failures.extend(expect_invalid(*case))
    failures.extend(verify_cli_guard())

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)

    print("PASS: metadata validation rejects placeholders and allows maintained test metadata only with explicit opt-in")


if __name__ == "__main__":
    main()
