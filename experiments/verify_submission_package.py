#!/usr/bin/env python3
"""Verify the generated submission zip against tracked files and safety rules."""

from __future__ import annotations

import argparse
import subprocess
import zipfile
from pathlib import Path

from fill_report_metadata import latex_escape


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = Path("submission/MARL-hw2-submission.zip")
MANIFEST = "SUBMISSION_MANIFEST.txt"
OPTIONAL_FILES = {"report/main.pdf"}
FORBIDDEN_ENTRIES = {
    ".env",
    "AFlow/config/config2.yaml",
}
FORBIDDEN_PREFIXES = (
    "experiments/runs/",
    "experiments/chunked_runs/",
    "AFlow/data/datasets/",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE, help="Zip file to verify.")
    parser.add_argument("--expect-name", help="Expected filled report author name.")
    parser.add_argument("--expect-student-id", help="Expected filled student ID.")
    parser.add_argument("--expect-email", help="Expected filled report email.")
    return parser.parse_args()


def run_command(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def current_commit() -> str:
    return run_command(["git", "rev-parse", "--short", "HEAD"])


def tracked_files() -> set[str]:
    output = run_command(["git", "ls-files"])
    return {line for line in output.splitlines() if line}


def optional_existing_files(tracked: set[str]) -> set[str]:
    return {path for path in OPTIONAL_FILES if path not in tracked and (REPO_ROOT / path).is_file()}


def verify_manifest(entries: set[str], manifest_text: str, expected_commit: str) -> list[str]:
    failures: list[str] = []
    if MANIFEST not in entries:
        failures.append(f"Missing {MANIFEST}")
    if f"Git commit: {expected_commit}" not in manifest_text:
        failures.append(f"Manifest does not reference current commit {expected_commit}")
    if "Summary:" not in manifest_text:
        failures.append("Manifest does not include audit summary")
    return failures


def verify_entries(entries: set[str], expected_files: set[str]) -> list[str]:
    failures: list[str] = []
    expected_entries = expected_files | {MANIFEST}
    missing = sorted(expected_entries - entries)
    unexpected = sorted(entries - expected_entries)
    if missing:
        failures.append("Missing package entries: " + ", ".join(missing[:20]))
    if unexpected:
        failures.append("Unexpected package entries: " + ", ".join(unexpected[:20]))

    forbidden = sorted(
        entry
        for entry in entries
        if entry in FORBIDDEN_ENTRIES or any(entry.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
    )
    if forbidden:
        failures.append("Forbidden package entries: " + ", ".join(forbidden))
    return failures


def verify_report_metadata(archive: zipfile.ZipFile, entries: set[str], args: argparse.Namespace) -> list[str]:
    expected_values = [args.expect_name, args.expect_student_id, args.expect_email]
    if not any(expected_values):
        return []

    failures: list[str] = []
    report_entry = "report/main.tex"
    if report_entry not in entries:
        return [f"Missing {report_entry} for metadata verification"]

    report_text = archive.read(report_entry).decode("utf-8")
    placeholders = ["Student Name", "Student ID: TODO", "TODO@example.com"]
    present_placeholders = [placeholder for placeholder in placeholders if placeholder in report_text]
    if present_placeholders:
        failures.append("Report metadata placeholders remain: " + ", ".join(present_placeholders))

    expected_map = {
        "name": args.expect_name,
        "student ID": args.expect_student_id,
        "email": args.expect_email,
    }
    for label, value in expected_map.items():
        if value and latex_escape(value) not in report_text:
            failures.append(f"Expected report {label} not found in {report_entry}")
    return failures


def main() -> None:
    args = parse_args()
    package_path = args.package if args.package.is_absolute() else REPO_ROOT / args.package
    tracked = tracked_files()
    expected_files = tracked | optional_existing_files(tracked)

    with zipfile.ZipFile(package_path) as archive:
        entries = set(archive.namelist())
        manifest_text = archive.read(MANIFEST).decode("utf-8") if MANIFEST in entries else ""
        metadata_failures = verify_report_metadata(archive, entries, args)

    failures = verify_manifest(entries, manifest_text, current_commit())
    failures.extend(verify_entries(entries, expected_files))
    failures.extend(metadata_failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)

    print(f"PASS: Package {args.package} contains {len(entries)} entries")
    print(f"PASS: Manifest references commit {current_commit()}")
    print("PASS: No forbidden package entries found")
    if args.expect_name or args.expect_student_id or args.expect_email:
        print("PASS: Report metadata matches expected values")


if __name__ == "__main__":
    main()
