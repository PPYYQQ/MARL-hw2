#!/usr/bin/env python3
"""Verify the generated submission zip against tracked files and safety rules."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
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
    parser.add_argument(
        "--allow-dirty",
        action="append",
        default=[],
        metavar="PATH",
        help="Allow one tracked path to differ from HEAD while verifying the package.",
    )
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


def dirty_tracked_files() -> set[str]:
    output = run_command(["git", "diff", "--name-only", "HEAD", "--"])
    return {line for line in output.splitlines() if line}


def check_clean_tracked_files(allowed_paths: list[str]) -> list[str]:
    allowed = set(allowed_paths)
    disallowed = sorted(dirty_tracked_files() - allowed)
    if disallowed:
        return ["Worktree has uncommitted tracked changes: " + ", ".join(disallowed)]
    return []


def optional_existing_files(tracked: set[str]) -> set[str]:
    return {path for path in OPTIONAL_FILES if path not in tracked and (REPO_ROOT / path).is_file()}


def verify_manifest(
    entries: set[str],
    manifest_text: str,
    expected_commit: str,
    tracked_count: int,
    optional_count: int,
) -> list[str]:
    failures: list[str] = []
    if MANIFEST not in entries:
        failures.append(f"Missing {MANIFEST}")
    if f"Git commit: {expected_commit}" not in manifest_text:
        failures.append(f"Manifest does not reference current commit {expected_commit}")
    if f"Tracked files: {tracked_count}" not in manifest_text:
        failures.append(f"Manifest tracked-file count does not match expected count {tracked_count}")
    if f"Optional files: {optional_count}" not in manifest_text:
        failures.append(f"Manifest optional-file count does not match expected count {optional_count}")
    summary_match = re.search(r"^Summary: \d+ passed, \d+ warnings, (?P<failures>\d+) failures$", manifest_text, re.MULTILINE)
    if not summary_match:
        failures.append("Manifest does not include a parseable audit summary")
    elif summary_match.group("failures") != "0":
        failures.append("Manifest audit summary reports failures")
    if re.search(r"^FAIL:", manifest_text, re.MULTILINE):
        failures.append("Manifest audit output contains failing checks")
    return failures


def parse_manifest_checksums(manifest_text: str) -> dict[str, str]:
    checksum_pattern = re.compile(r"^- (?P<sha256>[0-9a-f]{64})  (?P<path>.+)$", re.MULTILINE)
    return {match.group("path"): match.group("sha256") for match in checksum_pattern.finditer(manifest_text)}


def archive_sha256(archive: zipfile.ZipFile, entry: str) -> str:
    digest = hashlib.sha256()
    with archive.open(entry) as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest_checksums(
    archive: zipfile.ZipFile,
    entries: set[str],
    manifest_text: str,
    expected_files: set[str],
) -> list[str]:
    failures: list[str] = []
    checksums = parse_manifest_checksums(manifest_text)
    if not checksums:
        return ["Manifest does not include file checksums"]

    missing = sorted(expected_files - checksums.keys())
    unexpected = sorted(checksums.keys() - expected_files)
    if missing:
        failures.append("Missing manifest checksums: " + ", ".join(missing[:20]))
    if unexpected:
        failures.append("Unexpected manifest checksums: " + ", ".join(unexpected[:20]))

    for entry, expected_sha256 in sorted(checksums.items()):
        if entry not in entries:
            failures.append(f"Checksum entry missing from archive: {entry}")
            continue
        actual_sha256 = archive_sha256(archive, entry)
        if actual_sha256 != expected_sha256:
            failures.append(f"Checksum mismatch for {entry}")
        filesystem_path = REPO_ROOT / entry
        if not filesystem_path.is_file():
            failures.append(f"Checksum source missing from filesystem: {entry}")
            continue
        filesystem_sha256 = file_sha256(filesystem_path)
        if filesystem_sha256 != expected_sha256:
            failures.append(f"Filesystem checksum mismatch for {entry}")
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


def verify_secret_hygiene(archive: zipfile.ZipFile, entries: set[str]) -> list[str]:
    kimi_api_key = os.environ.get("KIMI_API_KEY", "")
    if len(kimi_api_key) < 8:
        return []

    secret_bytes = kimi_api_key.encode("utf-8")
    leaked_entries: list[str] = []
    for entry in sorted(entries):
        with archive.open(entry) as file_handle:
            if secret_bytes in file_handle.read():
                leaked_entries.append(entry)
    if leaked_entries:
        return ["KIMI_API_KEY value appears in package entries: " + ", ".join(leaked_entries)]
    return []


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
    clean_failures = check_clean_tracked_files(args.allow_dirty)
    tracked = tracked_files()
    optional = optional_existing_files(tracked)
    expected_files = tracked | optional

    with zipfile.ZipFile(package_path) as archive:
        entries = set(archive.namelist())
        manifest_text = archive.read(MANIFEST).decode("utf-8") if MANIFEST in entries else ""
        metadata_failures = verify_report_metadata(archive, entries, args)
        checksum_failures = verify_manifest_checksums(archive, entries, manifest_text, expected_files)
        secret_failures = verify_secret_hygiene(archive, entries)

    failures = verify_manifest(entries, manifest_text, current_commit(), len(tracked), len(optional))
    failures.extend(clean_failures)
    failures.extend(verify_entries(entries, expected_files))
    failures.extend(metadata_failures)
    failures.extend(checksum_failures)
    failures.extend(secret_failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)

    print(f"PASS: Package {args.package} contains {len(entries)} entries")
    print(f"PASS: Manifest references commit {current_commit()}")
    print("PASS: Manifest file counts match expected package contents")
    print("PASS: Manifest checksums match archive contents")
    print("PASS: No forbidden package entries or active API key values found")
    if args.expect_name or args.expect_student_id or args.expect_email:
        print("PASS: Report metadata matches expected values")


if __name__ == "__main__":
    main()
