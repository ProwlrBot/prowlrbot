#!/usr/bin/env python3
"""Repository health check script for ProwlrBot GitHub App skill.

Uses git commands to assess repository health metrics and outputs a
markdown or JSON report.

Usage:
    python repo_health.py --repo /path/to/repo
    python repo_health.py --repo . --days 14 --format json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class BranchInfo:
    """Info about a git branch."""

    name: str
    last_commit_date: datetime | None = None
    is_merged: bool = False


@dataclass
class HealthReport:
    """Repository health metrics."""

    repo_path: str
    checked_at: str = ""

    # Commit activity
    total_commits: int = 0
    commits_last_30_days: int = 0
    commits_last_7_days: int = 0
    unique_authors_30_days: int = 0

    # Branch health
    total_branches: int = 0
    merged_not_deleted: list[str] = field(default_factory=list)
    stale_branches: list[str] = field(default_factory=list)

    # Tag info
    total_tags: int = 0
    latest_tag: str = ""
    latest_tag_date: str = ""

    # Approximate issue/PR metrics from branch naming conventions
    feature_branches: int = 0
    fix_branches: int = 0

    # File metrics
    total_files_tracked: int = 0
    repo_size_approx: str = ""

    # Warnings
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Git command helpers
# ---------------------------------------------------------------------------


def _run_git(repo: str, args: list[str], default: str = "") -> str:
    """Run a git command and return stdout. Returns default on failure."""
    cmd = ["git", "-C", repo] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return default
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return default


def _run_git_lines(repo: str, args: list[str]) -> list[str]:
    """Run a git command and return non-empty stdout lines."""
    output = _run_git(repo, args)
    if not output:
        return []
    return [line for line in output.split("\n") if line.strip()]


# ---------------------------------------------------------------------------
# Health check logic
# ---------------------------------------------------------------------------


def check_health(repo: str, stale_days: int = 30) -> HealthReport:
    """Run all health checks against a git repository."""
    report = HealthReport(
        repo_path=repo,
        checked_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )

    # Verify it is a git repo
    git_check = _run_git(repo, ["rev-parse", "--git-dir"], default="")
    if not git_check:
        report.warnings.append(f"'{repo}' does not appear to be a git repository.")
        return report

    # --- Commit activity ---
    total = _run_git(repo, ["rev-list", "--count", "HEAD"])
    report.total_commits = int(total) if total.isdigit() else 0

    since_30 = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    since_7 = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    commits_30 = _run_git(repo, ["rev-list", "--count", f"--since={since_30}", "HEAD"])
    report.commits_last_30_days = int(commits_30) if commits_30.isdigit() else 0

    commits_7 = _run_git(repo, ["rev-list", "--count", f"--since={since_7}", "HEAD"])
    report.commits_last_7_days = int(commits_7) if commits_7.isdigit() else 0

    # Unique authors in last 30 days
    authors_output = _run_git(
        repo,
        [
            "log",
            f"--since={since_30}",
            "--format=%aN",
            "HEAD",
        ],
    )
    if authors_output:
        unique_authors = set(authors_output.split("\n"))
        report.unique_authors_30_days = len(unique_authors)

    # --- Branch health ---
    branches = _run_git_lines(repo, ["branch", "--format=%(refname:short)"])
    report.total_branches = len(branches)

    # Default branch detection
    default_branch = _run_git(
        repo,
        [
            "symbolic-ref",
            "--short",
            "refs/remotes/origin/HEAD",
        ],
        default="",
    )
    if default_branch:
        default_branch = default_branch.replace("origin/", "")
    else:
        # Fallback: try main, then master
        if "main" in branches:
            default_branch = "main"
        elif "master" in branches:
            default_branch = "master"
        else:
            default_branch = branches[0] if branches else "main"

    stale_cutoff = datetime.now(timezone.utc) - timedelta(days=stale_days)

    for branch in branches:
        if branch == default_branch:
            continue

        # Check if merged into default branch
        merged_branches = _run_git_lines(
            repo,
            [
                "branch",
                "--merged",
                default_branch,
                "--format=%(refname:short)",
            ],
        )
        is_merged = branch in merged_branches

        if is_merged:
            report.merged_not_deleted.append(branch)

        # Check last commit date
        date_str = _run_git(
            repo,
            [
                "log",
                "-1",
                "--format=%aI",
                branch,
            ],
        )
        if date_str:
            try:
                last_date = datetime.fromisoformat(date_str)
                if last_date.tzinfo is None:
                    last_date = last_date.replace(tzinfo=timezone.utc)
                if last_date < stale_cutoff and not is_merged:
                    report.stale_branches.append(branch)
            except ValueError:
                pass

        # Classify branch type
        lower_branch = branch.lower()
        if any(p in lower_branch for p in ("feature/", "feat/", "feature-", "feat-")):
            report.feature_branches += 1
        elif any(p in lower_branch for p in ("fix/", "bugfix/", "hotfix/", "fix-")):
            report.fix_branches += 1

    # --- Tags ---
    tags = _run_git_lines(repo, ["tag", "--sort=-creatordate"])
    report.total_tags = len(tags)
    if tags:
        report.latest_tag = tags[0]
        tag_date = _run_git(
            repo,
            [
                "log",
                "-1",
                "--format=%aI",
                tags[0],
            ],
        )
        report.latest_tag_date = tag_date if tag_date else "unknown"

    # --- File metrics ---
    tracked_files = _run_git(repo, ["ls-files"])
    if tracked_files:
        report.total_files_tracked = len(tracked_files.split("\n"))

    # Repo size (approximate from .git)
    size_output = _run_git(repo, ["count-objects", "-vH"])
    if size_output:
        for line in size_output.split("\n"):
            if line.startswith("size-pack:"):
                report.repo_size_approx = line.split(":")[1].strip()
                break

    # --- Generate warnings ---
    if report.commits_last_30_days == 0:
        report.warnings.append(
            "No commits in the last 30 days — repository may be inactive."
        )

    if len(report.merged_not_deleted) > 5:
        report.warnings.append(
            f"{len(report.merged_not_deleted)} merged branches have not been deleted. "
            "Consider cleaning them up."
        )

    if len(report.stale_branches) > 3:
        report.warnings.append(
            f"{len(report.stale_branches)} branches have had no activity in {stale_days}+ days."
        )

    if report.total_tags == 0:
        report.warnings.append(
            "No tags found. Consider using semantic versioning tags for releases."
        )

    return report


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def format_markdown(report: HealthReport) -> str:
    """Format health report as markdown."""
    lines: list[str] = []

    lines.append("## Repository Health Report")
    lines.append("")
    lines.append(f"**Repository:** `{report.repo_path}`")
    lines.append(f"**Checked at:** {report.checked_at}")
    lines.append("")

    # Warnings first
    if report.warnings:
        lines.append("### Warnings")
        lines.append("")
        for warning in report.warnings:
            lines.append(f"- {warning}")
        lines.append("")

    # Commit activity
    lines.append("### Commit Activity")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total commits | {report.total_commits:,} |")
    lines.append(f"| Commits (last 30 days) | {report.commits_last_30_days} |")
    lines.append(f"| Commits (last 7 days) | {report.commits_last_7_days} |")
    lines.append(f"| Active authors (30 days) | {report.unique_authors_30_days} |")
    lines.append("")

    # Branch health
    lines.append("### Branch Health")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total branches | {report.total_branches} |")
    lines.append(f"| Merged (not deleted) | {len(report.merged_not_deleted)} |")
    lines.append(f"| Stale (no activity 30+ days) | {len(report.stale_branches)} |")
    lines.append(f"| Feature branches | {report.feature_branches} |")
    lines.append(f"| Fix branches | {report.fix_branches} |")
    lines.append("")

    if report.merged_not_deleted:
        lines.append("**Merged branches to clean up:**")
        for branch in report.merged_not_deleted[:10]:
            lines.append(f"- `{branch}`")
        if len(report.merged_not_deleted) > 10:
            lines.append(f"- ... and {len(report.merged_not_deleted) - 10} more")
        lines.append("")

    if report.stale_branches:
        lines.append("**Stale branches:**")
        for branch in report.stale_branches[:10]:
            lines.append(f"- `{branch}`")
        if len(report.stale_branches) > 10:
            lines.append(f"- ... and {len(report.stale_branches) - 10} more")
        lines.append("")

    # Tags / Releases
    lines.append("### Releases")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total tags | {report.total_tags} |")
    lines.append(
        f"| Latest tag | `{report.latest_tag}`{' (' + report.latest_tag_date + ')' if report.latest_tag_date else ''} |"
    )
    lines.append("")

    # Repository size
    lines.append("### Repository Stats")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Tracked files | {report.total_files_tracked:,} |")
    if report.repo_size_approx:
        lines.append(f"| Pack size | {report.repo_size_approx} |")
    lines.append("")

    lines.append("---")
    lines.append("*Generated by ProwlrBot GitHub App skill*")

    return "\n".join(lines)


def format_json(report: HealthReport) -> str:
    """Format health report as JSON."""
    data = {
        "repo_path": report.repo_path,
        "checked_at": report.checked_at,
        "commit_activity": {
            "total": report.total_commits,
            "last_30_days": report.commits_last_30_days,
            "last_7_days": report.commits_last_7_days,
            "unique_authors_30_days": report.unique_authors_30_days,
        },
        "branches": {
            "total": report.total_branches,
            "merged_not_deleted": report.merged_not_deleted,
            "stale": report.stale_branches,
            "feature_branches": report.feature_branches,
            "fix_branches": report.fix_branches,
        },
        "releases": {
            "total_tags": report.total_tags,
            "latest_tag": report.latest_tag,
            "latest_tag_date": report.latest_tag_date,
        },
        "stats": {
            "tracked_files": report.total_files_tracked,
            "pack_size": report.repo_size_approx,
        },
        "warnings": report.warnings,
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check repository health and output a structured report.",
    )
    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        default=".",
        help="Path to the git repository (default: current directory).",
    )
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=30,
        help="Number of days after which a branch is considered stale (default: 30).",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown).",
    )

    args = parser.parse_args()
    report = check_health(args.repo, stale_days=args.days)

    if args.format == "json":
        print(format_json(report))
    else:
        print(format_markdown(report))


if __name__ == "__main__":
    main()
