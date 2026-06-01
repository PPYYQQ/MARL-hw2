#!/usr/bin/env python3
"""Verify that the current Git HEAD is synchronized with its upstream branch."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Fetch upstream before checking sync state.")
    return parser.parse_args()


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def git_stdout(args: list[str]) -> str:
    return run_git(args).stdout.strip()


def main() -> None:
    args = parse_args()

    dirty = git_stdout(["status", "--porcelain=v1", "--untracked-files=all"])
    if dirty:
        changed = ", ".join(line[2:].strip() for line in dirty.splitlines()[:10])
        raise SystemExit(f"FAIL: Worktree has uncommitted changes: {changed}")

    upstream_result = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], check=False)
    if upstream_result.returncode != 0:
        raise SystemExit("FAIL: Current branch has no upstream configured")
    upstream = upstream_result.stdout.strip()

    if args.fetch:
        remote = upstream.split("/", 1)[0]
        run_git(["fetch", remote])

    local_commit = git_stdout(["rev-parse", "HEAD"])
    upstream_commit = git_stdout(["rev-parse", "@{u}"])
    branch = git_stdout(["branch", "--show-current"])

    if local_commit != upstream_commit:
        ahead_behind = git_stdout(["rev-list", "--left-right", "--count", f"HEAD...@{{u}}"])
        ahead, behind = ahead_behind.split()
        raise SystemExit(
            f"FAIL: {branch} is not synchronized with {upstream} "
            f"(ahead {ahead}, behind {behind})"
        )

    print(f"PASS: {branch} is synchronized with {upstream} at {local_commit[:7]}")


if __name__ == "__main__":
    main()
