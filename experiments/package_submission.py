#!/usr/bin/env python3
"""Create a submission zip from tracked files and optional report PDF."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path("submission/MARL-hw2-submission.zip")
OPTIONAL_FILES = [Path("report/main.pdf")]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Output zip path.")
    parser.add_argument("--student-id", help="Student ID for the final submission zip name.")
    parser.add_argument("--name", help="Student name for the final submission zip name.")
    parser.add_argument("--assignment", default="MARL-hw2", help="Assignment label for the final submission zip name.")
    parser.add_argument("--dry-run", action="store_true", help="List files without creating the zip.")
    parser.add_argument("--skip-audit", action="store_true", help="Do not run experiments/audit_submission.py first.")
    parser.add_argument(
        "--allow-dirty",
        action="append",
        default=[],
        metavar="PATH",
        help="Allow one tracked path to differ from HEAD while packaging.",
    )
    return parser.parse_args()


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def current_commit() -> str:
    return run_command(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()


def safe_name_component(value: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", value.strip())
    return cleaned.strip("._") or "unknown"


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return args.output
    if args.student_id and args.name:
        student_id = safe_name_component(args.student_id)
        name = safe_name_component(args.name)
        assignment = safe_name_component(args.assignment)
        return Path("submission") / f"{student_id}_{name}_{assignment}.zip"
    return DEFAULT_OUTPUT


def submission_label(args: argparse.Namespace) -> str | None:
    if args.student_id and args.name:
        return f"{args.student_id} {args.name} {args.assignment}"
    return None


def tracked_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    files = [Path(raw.decode("utf-8")) for raw in completed.stdout.split(b"\0") if raw]
    return sorted(files, key=lambda path: path.as_posix())


def dirty_tracked_files() -> set[Path]:
    completed = run_command(["git", "diff", "--name-only", "HEAD", "--"])
    return {Path(line) for line in completed.stdout.splitlines() if line}


def check_clean_tracked_files(allowed_paths: list[str]) -> None:
    allowed = {Path(path) for path in allowed_paths}
    disallowed = sorted(dirty_tracked_files() - allowed, key=lambda path: path.as_posix())
    if disallowed:
        paths = ", ".join(path.as_posix() for path in disallowed)
        raise SystemExit(f"Refusing to package uncommitted tracked changes: {paths}")


def optional_existing_files(files: list[Path]) -> list[Path]:
    tracked = set(files)
    return [path for path in OPTIONAL_FILES if path not in tracked and (REPO_ROOT / path).is_file()]


def run_audit() -> str:
    completed = run_command([sys.executable, "experiments/audit_submission.py"])
    return completed.stdout.strip()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_manifest(
    files: list[Path],
    extras: list[Path],
    output: Path,
    label: str | None,
    audit_output: str | None,
) -> str:
    lines = [
        "MARL HW2 submission package",
        f"Created: {datetime.now(timezone.utc).isoformat()}",
        f"Git commit: {current_commit()}",
        f"Output: {output.as_posix()}",
        f"Tracked files: {len(files)}",
        f"Optional files: {len(extras)}",
    ]
    if label:
        lines.append(f"Submission label: {label}")
    lines.extend(["", "Optional included files:"])
    lines.extend(f"- {path.as_posix()}" for path in extras)
    if not extras:
        lines.append("- none")
    lines.extend(["", "File checksums (sha256):"])
    for path in files + extras:
        lines.append(f"- {file_sha256(REPO_ROOT / path)}  {path.as_posix()}")
    if audit_output:
        lines.extend(["", "Audit output:", audit_output])
    return "\n".join(lines) + "\n"


def create_zip(output_path: Path, files: list[Path], extras: list[Path], manifest: str) -> None:
    absolute_output = output_path if output_path.is_absolute() else REPO_ROOT / output_path
    absolute_output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(absolute_output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("SUBMISSION_MANIFEST.txt", manifest)
        for path in files + extras:
            archive.write(REPO_ROOT / path, path.as_posix())


def main() -> None:
    args = parse_args()
    check_clean_tracked_files(args.allow_dirty)
    files = tracked_files()
    extras = optional_existing_files(files)
    audit_output = None if args.skip_audit else run_audit()
    output = output_path(args)
    manifest = render_manifest(files, extras, output, submission_label(args), audit_output)

    if args.dry_run:
        print(f"Would package {len(files)} tracked files and {len(extras)} optional files into {output}")
        for path in files + extras:
            print(path.as_posix())
        return

    create_zip(output, files, extras, manifest)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
