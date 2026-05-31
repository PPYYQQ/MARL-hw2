#!/usr/bin/env python3
"""Fill report author metadata placeholders."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

DEFAULT_REPORT = Path("report/main.tex")
COURSE_TEXT = "Course: Multi-Agent Reinforcement Learning"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Author name to place in the report.")
    parser.add_argument("--student-id", required=True, help="Student ID to place in the report.")
    parser.add_argument("--email", required=True, help="Corresponding author email.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--dry-run", action="store_true", help="Print changed metadata lines without writing.")
    return parser.parse_args()


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def replace_once(pattern: str, replacement: str, text: str) -> str:
    new_text, count = re.subn(pattern, lambda _: replacement, text, count=1)
    if count != 1:
        raise ValueError(f"Expected exactly one match for pattern: {pattern}")
    return new_text


def fill_metadata(report_text: str, name: str, student_id: str, email: str) -> str:
    escaped_name = latex_escape(name)
    escaped_student_id = latex_escape(student_id)
    escaped_email = latex_escape(email)
    report_text = replace_once(
        r"\\icmlauthor\{[^{}]+\}\{pku\}",
        rf"\icmlauthor{{{escaped_name}}}{{pku}}",
        report_text,
    )
    report_text = replace_once(
        r"\\icmlaffiliation\{pku\}\{[^{}]+\}",
        rf"\icmlaffiliation{{pku}}{{Student ID: {escaped_student_id}; {COURSE_TEXT}}}",
        report_text,
    )
    return replace_once(
        r"\\icmlcorrespondingauthor\{[^{}]+\}\{[^{}]+\}",
        rf"\icmlcorrespondingauthor{{{escaped_name}}}{{{escaped_email}}}",
        report_text,
    )


def main() -> None:
    args = parse_args()
    report_text = args.report.read_text(encoding="utf-8")
    updated_text = fill_metadata(report_text, args.name, args.student_id, args.email)
    if args.dry_run:
        for line in updated_text.splitlines():
            if line.startswith(("\\icmlauthor", "\\icmlaffiliation", "\\icmlcorrespondingauthor")):
                print(line)
        return
    args.report.write_text(updated_text, encoding="utf-8")


if __name__ == "__main__":
    main()
