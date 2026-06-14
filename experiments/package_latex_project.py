#!/usr/bin/env python3
"""Create an Overleaf-ready LaTeX project zip for the final report."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path("submission/MARL-hw2-overleaf-latex-project.zip")
REPORT_FILES = [
    Path("report/main.tex"),
    Path("report/references.bib"),
    Path("report/icml2022.sty"),
    Path("report/icml2022.bst"),
    Path("report/algorithm.sty"),
    Path("report/algorithmic.sty"),
    Path("report/fancyhdr.sty"),
    Path("report/README.md"),
]
README_ENTRY = "OVERLEAF_README.txt"
README_TEXT = """MARL HW2 LaTeX project

Upload this zip directly to Overleaf. The entry point is main.tex.

This archive intentionally contains only LaTeX source/support files. It does not
include report/main.pdf or generated build artifacts.

Before final course submission, replace the author placeholders in main.tex:
- Student Name
- Student ID: TODO
- TODO@example.com
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output zip path.")
    parser.add_argument("--dry-run", action="store_true", help="List files without creating the zip.")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def validate_files(files: list[Path]) -> None:
    missing = [path.as_posix() for path in files if not resolve(path).is_file()]
    if missing:
        raise SystemExit("Missing LaTeX project files: " + ", ".join(missing))


def archive_name(path: Path) -> str:
    return path.name


def create_zip(output: Path, files: list[Path]) -> None:
    absolute_output = resolve(output)
    absolute_output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(absolute_output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(README_ENTRY, README_TEXT)
        for path in files:
            archive.write(resolve(path), archive_name(path))


def main() -> None:
    args = parse_args()
    validate_files(REPORT_FILES)
    if args.dry_run:
        print(f"Would package {len(REPORT_FILES)} report files into {args.output}")
        print(README_ENTRY)
        for path in REPORT_FILES:
            print(f"{path.as_posix()} -> {archive_name(path)}")
        return

    create_zip(args.output, REPORT_FILES)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
