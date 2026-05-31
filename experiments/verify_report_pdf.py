#!/usr/bin/env python3
"""Verify that the local report PDF is present and newer than its TeX sources."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = Path("report/main.pdf")
SOURCE_GLOBS = [
    "report/main.tex",
    "report/references.bib",
    "report/*.bst",
    "report/*.sty",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--source", action="append", default=[], help="Additional source file or glob.")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def source_paths(patterns: list[str]) -> list[Path]:
    paths: set[Path] = set()
    for pattern in patterns:
        matches = sorted(REPO_ROOT.glob(pattern))
        if matches:
            paths.update(path for path in matches if path.is_file())
            continue

        path = resolve(Path(pattern))
        if path.is_file():
            paths.add(path)
    return sorted(paths)


def main() -> None:
    args = parse_args()
    pdf_path = resolve(args.pdf)
    if not pdf_path.is_file():
        print(f"FAIL: Report PDF does not exist: {pdf_path.relative_to(REPO_ROOT)}")
        sys.exit(1)

    sources = source_paths(SOURCE_GLOBS + args.source)
    if not sources:
        print("FAIL: No report sources found")
        sys.exit(1)

    pdf_mtime = pdf_path.stat().st_mtime_ns
    stale_sources = [path for path in sources if path.stat().st_mtime_ns > pdf_mtime]
    if stale_sources:
        print(f"FAIL: {pdf_path.relative_to(REPO_ROOT)} is older than report source files:")
        for path in stale_sources:
            print(f"- {path.relative_to(REPO_ROOT)}")
        print("Run `make build-report` before packaging.")
        sys.exit(1)

    relative_pdf = pdf_path.relative_to(REPO_ROOT)
    print(f"PASS: {relative_pdf} is current for {len(sources)} report source files")


if __name__ == "__main__":
    main()
