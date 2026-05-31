#!/usr/bin/env python3
"""Fill metadata, rebuild the report PDF, and create the final submission zip."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Student name for report metadata and zip naming.")
    parser.add_argument("--student-id", required=True, help="Student ID for report metadata and zip naming.")
    parser.add_argument("--email", required=True, help="Corresponding author email for the report.")
    parser.add_argument("--assignment", default="MARL-hw2", help="Assignment label for the final zip name.")
    parser.add_argument("--output", type=Path, help="Optional explicit output zip path.")
    parser.add_argument("--dry-run", action="store_true", help="Preview metadata and package contents without writing.")
    return parser.parse_args()


def run_command(command: list[str]) -> None:
    print("$ " + shlex.join(command), flush=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def metadata_command(args: argparse.Namespace, dry_run: bool) -> list[str]:
    command = [
        sys.executable,
        "experiments/fill_report_metadata.py",
        "--name",
        args.name,
        "--student-id",
        args.student_id,
        "--email",
        args.email,
    ]
    if dry_run:
        command.append("--dry-run")
    return command


def package_command(args: argparse.Namespace, dry_run: bool) -> list[str]:
    command = [
        sys.executable,
        "experiments/package_submission.py",
        "--student-id",
        args.student_id,
        "--name",
        args.name,
        "--assignment",
        args.assignment,
    ]
    if args.output:
        command.extend(["--output", str(args.output)])
    if dry_run:
        command.append("--dry-run")
    return command


def main() -> None:
    args = parse_args()
    if args.dry_run:
        run_command(metadata_command(args, dry_run=True))
        print("$ make build-report  # skipped in dry-run", flush=True)
        run_command(package_command(args, dry_run=True))
        return

    run_command(metadata_command(args, dry_run=False))
    run_command(["make", "build-report"])
    run_command(package_command(args, dry_run=False))


if __name__ == "__main__":
    main()
