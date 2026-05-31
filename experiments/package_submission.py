#!/usr/bin/env python3
"""Create a submission zip from tracked files and optional report PDF."""

from __future__ import annotations

import argparse
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
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output zip path.")
    parser.add_argument("--dry-run", action="store_true", help="List files without creating the zip.")
    parser.add_argument("--skip-audit", action="store_true", help="Do not run experiments/audit_submission.py first.")
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


def optional_existing_files(files: list[Path]) -> list[Path]:
    tracked = set(files)
    return [path for path in OPTIONAL_FILES if path not in tracked and (REPO_ROOT / path).is_file()]


def run_audit() -> str:
    completed = run_command([sys.executable, "experiments/audit_submission.py"])
    return completed.stdout.strip()


def render_manifest(files: list[Path], extras: list[Path], audit_output: str | None) -> str:
    lines = [
        "MARL HW2 submission package",
        f"Created: {datetime.now(timezone.utc).isoformat()}",
        f"Git commit: {current_commit()}",
        f"Tracked files: {len(files)}",
        f"Optional files: {len(extras)}",
        "",
        "Optional included files:",
    ]
    lines.extend(f"- {path.as_posix()}" for path in extras)
    if not extras:
        lines.append("- none")
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
    files = tracked_files()
    extras = optional_existing_files(files)
    audit_output = None if args.skip_audit else run_audit()
    manifest = render_manifest(files, extras, audit_output)

    if args.dry_run:
        print(f"Would package {len(files)} tracked files and {len(extras)} optional files")
        for path in files + extras:
            print(path.as_posix())
        return

    create_zip(args.output, files, extras, manifest)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
