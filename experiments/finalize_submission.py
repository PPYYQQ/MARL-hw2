#!/usr/bin/env python3
"""Fill metadata, rebuild the report PDF, and create the final submission zip."""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = Path("report/main.tex")
REPORT_PDF_PATH = Path("report/main.pdf")
DEFAULT_ASSIGNMENT = "MARL-hw2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Student name for report metadata and zip naming.")
    parser.add_argument("--student-id", required=True, help="Student ID for report metadata and zip naming.")
    parser.add_argument("--email", required=True, help="Corresponding author email for the report.")
    parser.add_argument("--assignment", default=DEFAULT_ASSIGNMENT, help="Assignment label for the final zip name.")
    parser.add_argument("--output", type=Path, help="Optional explicit output zip path.")
    parser.add_argument(
        "--keep-filled-report",
        action="store_true",
        help="Leave report/main.tex and report/main.pdf filled after packaging instead of restoring placeholders.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview metadata and package contents without writing.")
    return parser.parse_args()


def run_command(command: list[str]) -> None:
    print("$ " + shlex.join(command), flush=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def safe_name_component(value: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", value.strip())
    return cleaned.strip("._") or "unknown"


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output
    student_id = safe_name_component(args.student_id)
    name = safe_name_component(args.name)
    assignment = safe_name_component(args.assignment)
    return Path("submission") / f"{student_id}_{name}_{assignment}.zip"


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


def package_command(args: argparse.Namespace, output: Path, dry_run: bool) -> list[str]:
    command = [
        sys.executable,
        "experiments/package_submission.py",
        "--student-id",
        args.student_id,
        "--name",
        args.name,
        "--assignment",
        args.assignment,
        "--output",
        str(output),
        "--allow-dirty",
        REPORT_PATH.as_posix(),
    ]
    if dry_run:
        command.append("--dry-run")
    return command


def verify_command(args: argparse.Namespace, output: Path) -> list[str]:
    return [
        sys.executable,
        "experiments/verify_submission_package.py",
        "--package",
        str(output),
        "--expect-name",
        args.name,
        "--expect-student-id",
        args.student_id,
        "--expect-email",
        args.email,
    ]


def main() -> None:
    args = parse_args()
    output = output_path(args)
    if args.dry_run:
        run_command(metadata_command(args, dry_run=True))
        print("$ make build-report  # skipped in dry-run", flush=True)
        run_command(package_command(args, output, dry_run=True))
        print("$ " + shlex.join(verify_command(args, output)) + "  # skipped in dry-run", flush=True)
        return

    report_path = REPO_ROOT / REPORT_PATH
    pdf_path = REPO_ROOT / REPORT_PDF_PATH
    original_report = report_path.read_text(encoding="utf-8")
    original_pdf = pdf_path.read_bytes() if pdf_path.is_file() else None
    try:
        run_command(metadata_command(args, dry_run=False))
        run_command(["make", "build-report"])
        run_command(package_command(args, output, dry_run=False))
        run_command(verify_command(args, output))
    finally:
        if not args.keep_filled_report:
            report_path.write_text(original_report, encoding="utf-8")
            if original_pdf is None:
                pdf_path.unlink(missing_ok=True)
            else:
                pdf_path.write_bytes(original_pdf)
            print(f"Restored {REPORT_PATH} and {REPORT_PDF_PATH} placeholders after packaging.", flush=True)


if __name__ == "__main__":
    main()
