#!/usr/bin/env python3
"""Regression checks for submission-package verification safety logic."""

from __future__ import annotations

import os
import tempfile
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from verify_submission_package import MANIFEST, verify_manifest, verify_secret_hygiene


@contextmanager
def temporary_env(name: str, value: str) -> Iterator[None]:
    previous = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous


def assert_no_failures(failures: list[str], label: str) -> None:
    if failures:
        raise AssertionError(f"{label} unexpectedly failed: {failures}")


def assert_failure_contains(failures: list[str], expected: str, label: str) -> None:
    if not any(expected in failure for failure in failures):
        raise AssertionError(f"{label} did not report {expected!r}: {failures}")


def verify_manifest_file_counts() -> None:
    manifest_text = "\n".join(
        [
            "Git commit: abc1234",
            "Tracked files: 2",
            "Optional files: 1",
            "Summary: 10 passed, 0 warnings, 0 failures",
        ]
    )
    entries = {MANIFEST}

    assert_no_failures(
        verify_manifest(entries, manifest_text, "abc1234", tracked_count=2, optional_count=1),
        "matching manifest counts",
    )
    assert_failure_contains(
        verify_manifest(entries, manifest_text, "abc1234", tracked_count=3, optional_count=1),
        "tracked-file count",
        "mismatched tracked count",
    )
    assert_failure_contains(
        verify_manifest(entries, manifest_text, "abc1234", tracked_count=2, optional_count=0),
        "optional-file count",
        "mismatched optional count",
    )

    ambiguous_text = "\n".join(
        [
            "Git commit: abc12345",
            "Tracked files: 20",
            "Optional files: 10",
            "Summary: 10 passed, 0 warnings, 0 failures",
        ]
    )
    ambiguous_failures = verify_manifest(
        entries,
        ambiguous_text,
        "abc1234",
        tracked_count=2,
        optional_count=1,
    )
    assert_failure_contains(ambiguous_failures, "current commit", "ambiguous commit line")
    assert_failure_contains(ambiguous_failures, "tracked-file count", "ambiguous tracked count")
    assert_failure_contains(ambiguous_failures, "optional-file count", "ambiguous optional count")


def write_zip(path: Path, files: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for entry, text in files.items():
            archive.writestr(entry, text)


def verify_active_key_scan() -> None:
    fake_key = "sk-test-package-verifier-1234567890"
    with tempfile.TemporaryDirectory() as temp_dir:
        leaked_zip = Path(temp_dir) / "leaked.zip"
        safe_zip = Path(temp_dir) / "safe.zip"
        manifest_only_zip = Path(temp_dir) / "manifest-only.zip"

        write_zip(leaked_zip, {"notes.txt": f"key={fake_key}"})
        write_zip(safe_zip, {"notes.txt": "key is kept outside the archive"})
        write_zip(manifest_only_zip, {MANIFEST: f"Audit mentions {fake_key}"})

        with temporary_env("KIMI_API_KEY", fake_key):
            with zipfile.ZipFile(leaked_zip) as archive:
                assert_failure_contains(
                    verify_secret_hygiene(archive, set(archive.namelist())),
                    "KIMI_API_KEY value appears",
                    "leaked key scan",
                )

            with zipfile.ZipFile(safe_zip) as archive:
                assert_no_failures(
                    verify_secret_hygiene(archive, set(archive.namelist())),
                    "safe archive key scan",
                )

            with zipfile.ZipFile(manifest_only_zip) as archive:
                assert_failure_contains(
                    verify_secret_hygiene(archive, set(archive.namelist())),
                    "KIMI_API_KEY value appears",
                    "manifest key scan",
                )


def main() -> None:
    verify_manifest_file_counts()
    verify_active_key_scan()
    print("PASS: package verifier rejects manifest count drift and active API key leakage")


if __name__ == "__main__":
    main()
