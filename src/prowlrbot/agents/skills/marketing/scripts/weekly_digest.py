"""Generate a weekly project digest from git activity.

Produces a structured markdown report with sections for highlights,
metrics, upcoming work, and community spotlight.
"""

import argparse
import os
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional

FIELD_SEP = "---FIELD-SEP---"
COMMIT_SEP = "---COMMIT-SEP---"


def run_git(args: list[str], cwd: str) -> str:
    """Run a git command and return its stdout."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def get_week_bounds(week_start: Optional[str] = None) -> tuple[str, str]:
    """Get the Monday and Sunday ISO dates for a given week.

    Args:
        week_start: Monday date in YYYY-MM-DD format, or None for current week.

    Returns:
        Tuple of (monday_iso, sunday_iso) date strings.
    """
    if week_start:
        monday = datetime.strptime(week_start, "%Y-%m-%d")
        # Adjust to Monday if the given date isn't one
        weekday = monday.weekday()
        if weekday != 0:
            monday = monday - timedelta(days=weekday)
    else:
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())

    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


def get_commits_for_week(cwd: str, since: str, until: str) -> list[dict[str, str]]:
    """Get all commits within a date range."""
    # Add one day to 'until' so git log includes commits on Sunday
    until_dt = datetime.strptime(until, "%Y-%m-%d") + timedelta(days=1)
    until_inclusive = until_dt.strftime("%Y-%m-%d")

    log_format = FIELD_SEP.join(["%H", "%an", "%ae", "%as", "%s"])
    try:
        output = run_git(
            [
                "log",
                "--all",
                f"--since={since}",
                f"--until={until_inclusive}",
                f"--pretty=format:{log_format}{COMMIT_SEP}",
                "--no-merges",
            ],
            cwd=cwd,
        )
    except RuntimeError:
        return []

    if not output:
        return []

    commits = []
    for entry in output.split(COMMIT_SEP):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(FIELD_SEP)
        if len(parts) != 5:
            continue
        commits.append(
            {
                "hash": parts[0],
                "author": parts[1],
                "email": parts[2],
                "date": parts[3],
                "subject": parts[4],
            }
        )
    return commits


def get_file_stats(cwd: str, since: str, until: str) -> dict[str, int]:
    """Get file change statistics for the week."""
    until_dt = datetime.strptime(until, "%Y-%m-%d") + timedelta(days=1)
    until_inclusive = until_dt.strftime("%Y-%m-%d")

    try:
        output = run_git(
            [
                "log",
                "--all",
                f"--since={since}",
                f"--until={until_inclusive}",
                "--no-merges",
                "--pretty=format:",
                "--numstat",
            ],
            cwd=cwd,
        )
    except RuntimeError:
        return {"additions": 0, "deletions": 0, "files_changed": 0}

    additions = 0
    deletions = 0
    files = set()
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, filepath = parts
        # Binary files show '-' for additions/deletions
        if added != "-":
            additions += int(added)
        if deleted != "-":
            deletions += int(deleted)
        files.add(filepath)

    return {
        "additions": additions,
        "deletions": deletions,
        "files_changed": len(files),
    }


def get_active_branches(cwd: str, since: str, until: str) -> list[str]:
    """Get branches that had activity during the week."""
    until_dt = datetime.strptime(until, "%Y-%m-%d") + timedelta(days=1)
    until_inclusive = until_dt.strftime("%Y-%m-%d")

    try:
        output = run_git(
            [
                "for-each-ref",
                "--sort=-committerdate",
                "--format=%(refname:short) %(committerdate:short)",
                "refs/heads/",
            ],
            cwd=cwd,
        )
    except RuntimeError:
        return []

    active = []
    since_dt = datetime.strptime(since, "%Y-%m-%d")
    until_dt = datetime.strptime(until_inclusive, "%Y-%m-%d")

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        branch, date_str = parts
        try:
            branch_dt = datetime.strptime(date_str, "%Y-%m-%d")
            if since_dt <= branch_dt <= until_dt:
                active.append(branch)
        except ValueError:
            continue

    return active


def extract_highlights(commits: list[dict[str, str]]) -> list[str]:
    """Extract notable commits as highlights.

    Prioritizes feat and fix commits, and picks the most significant ones.
    """
    highlights = []

    # Prioritize features, then fixes, then others
    feat_commits = [c for c in commits if c["subject"].startswith("feat")]
    fix_commits = [c for c in commits if c["subject"].startswith("fix")]
    other_notable = [
        c
        for c in commits
        if not c["subject"].startswith(("feat", "fix", "chore", "style", "ci"))
    ]

    for c in feat_commits[:5]:
        highlights.append(c["subject"])
    for c in fix_commits[:3]:
        highlights.append(c["subject"])
    for c in other_notable[:2]:
        highlights.append(c["subject"])

    return highlights[:8]  # Cap at 8 highlights


def get_contributor_stats(
    commits: list[dict[str, str]],
) -> list[tuple[str, int]]:
    """Get contributor commit counts, sorted by most active."""
    counter: Counter[str] = Counter()
    for c in commits:
        counter[c["author"]] += 1
    return counter.most_common()


def generate_weekly_digest(
    repo_path: str = ".",
    week_start: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """Generate a weekly project digest.

    Args:
        repo_path: Path to the git repository.
        week_start: Monday of the target week (YYYY-MM-DD). Defaults to current week.
        output_path: File path to write the digest. If None, returns the string.

    Returns:
        The formatted digest as a markdown string.
    """
    repo_path = os.path.abspath(repo_path)
    monday, sunday = get_week_bounds(week_start)

    # Gather data
    commits = get_commits_for_week(repo_path, monday, sunday)
    file_stats = get_file_stats(repo_path, monday, sunday)
    active_branches = get_active_branches(repo_path, monday, sunday)
    highlights = extract_highlights(commits)
    contributors = get_contributor_stats(commits)

    # Get repo name from directory
    repo_name = os.path.basename(repo_path)
    try:
        remote_url = run_git(["remote", "get-url", "origin"], repo_path)
        # Extract repo name from URL
        if remote_url.endswith(".git"):
            remote_url = remote_url[:-4]
        repo_name = remote_url.split("/")[-1]
    except RuntimeError:
        pass

    # Build the digest
    lines = [
        f"# Weekly Digest: {repo_name}",
        f"**Week of {monday} to {sunday}**",
        "",
        "---",
        "",
    ]

    # Highlights section
    lines.append("## Highlights")
    lines.append("")
    if highlights:
        for h in highlights:
            lines.append(f"- {h}")
    else:
        lines.append("- _No notable changes this week._")
    lines.append("")

    # Metrics section
    lines.append("## Metrics")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Commits | {len(commits)} |")
    lines.append(f"| Lines added | +{file_stats['additions']} |")
    lines.append(f"| Lines removed | -{file_stats['deletions']} |")
    lines.append(f"| Files changed | {file_stats['files_changed']} |")
    lines.append(f"| Active branches | {len(active_branches)} |")
    lines.append(f"| Contributors | {len(contributors)} |")
    lines.append("")

    # Active branches
    if active_branches:
        lines.append("### Active Branches")
        lines.append("")
        for branch in active_branches[:10]:
            lines.append(f"- `{branch}`")
        if len(active_branches) > 10:
            lines.append(f"- _...and {len(active_branches) - 10} more_")
        lines.append("")

    # Upcoming section (placeholder for manual input or future automation)
    lines.append("## Upcoming")
    lines.append("")
    lines.append(
        "_This section is a template — fill in planned work for the coming week._"
    )
    lines.append("")
    lines.append("- [ ] <!-- Priority 1: describe planned work -->")
    lines.append("- [ ] <!-- Priority 2: describe planned work -->")
    lines.append("- [ ] <!-- Priority 3: describe planned work -->")
    lines.append("")

    # Community Spotlight
    lines.append("## Community Spotlight")
    lines.append("")
    if contributors:
        # Highlight top contributors
        lines.append("### Top Contributors This Week")
        lines.append("")
        for author, count in contributors[:5]:
            commit_word = "commit" if count == 1 else "commits"
            lines.append(f"- **{author}** — {count} {commit_word}")
        lines.append("")

        if len(contributors) > 5:
            others = sum(count for _, count in contributors[5:])
            lines.append(
                f"_Plus {len(contributors) - 5} other contributors "
                f"with {others} commits._"
            )
            lines.append("")
    else:
        lines.append("- _No contributions this week._")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        f"_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} "
        f"by ProwlrBot Marketing Skill._"
    )

    digest = "\n".join(lines)

    if output_path:
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(digest)
        print(f"Digest written to {output_path}")

    return digest


def main():
    parser = argparse.ArgumentParser(
        description="Generate a weekly project digest from git activity."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--week",
        default=None,
        help="Monday of the target week in YYYY-MM-DD format (default: current week)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: print to stdout)",
    )

    args = parser.parse_args()

    try:
        result = generate_weekly_digest(
            repo_path=args.repo,
            week_start=args.week,
            output_path=args.output,
        )
        if not args.output:
            print(result)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
