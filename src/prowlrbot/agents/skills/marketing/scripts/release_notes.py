"""Generate release notes from git tags.

Uses git log between two tags to produce a formatted markdown changelog,
grouping commits by conventional commit type (feat, fix, docs, etc.).
"""

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from typing import Optional

COMMIT_TYPE_LABELS = {
    "feat": "New Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "refactor": "Refactoring",
    "test": "Tests",
    "chore": "Chores",
    "perf": "Performance",
    "style": "Style",
    "ci": "CI/CD",
    "build": "Build",
}

CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?!?:\s*(?P<subject>.+)$"
)

COMMIT_LOG_SEP = "---COMMIT-SEP---"
FIELD_SEP = "---FIELD-SEP---"


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


def get_tags(cwd: str) -> list[str]:
    """Get all tags sorted by version (most recent first)."""
    try:
        output = run_git(
            ["tag", "--sort=-version:refname"],
            cwd=cwd,
        )
    except RuntimeError:
        return []
    if not output:
        return []
    return output.splitlines()


def get_commits_between(from_ref: str, to_ref: str, cwd: str) -> list[dict[str, str]]:
    """Get commits between two refs as a list of dicts."""
    log_format = FIELD_SEP.join(["%H", "%an", "%ae", "%as", "%s"])
    output = run_git(
        [
            "log",
            f"{from_ref}..{to_ref}",
            f"--pretty=format:{log_format}{COMMIT_LOG_SEP}",
            "--no-merges",
        ],
        cwd=cwd,
    )
    if not output:
        return []

    commits = []
    for entry in output.split(COMMIT_LOG_SEP):
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


def parse_conventional_commit(subject: str) -> dict[str, Optional[str]]:
    """Parse a conventional commit message into type, scope, and subject."""
    match = CONVENTIONAL_COMMIT_RE.match(subject)
    if match:
        return {
            "type": match.group("type"),
            "scope": match.group("scope"),
            "subject": match.group("subject"),
        }
    return {"type": None, "scope": None, "subject": subject}


def group_by_type(commits: list[dict[str, str]]) -> dict[str, list[dict]]:
    """Group commits by conventional commit type."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for commit in commits:
        parsed = parse_conventional_commit(commit["subject"])
        commit_type = parsed["type"] or "other"
        groups[commit_type].append(
            {
                **commit,
                "parsed_scope": parsed["scope"],
                "parsed_subject": parsed["subject"],
            }
        )
    return dict(groups)


def group_by_author(commits: list[dict[str, str]]) -> dict[str, list[dict]]:
    """Group commits by author name."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for commit in commits:
        groups[commit["author"]].append(commit)
    return dict(groups)


def format_markdown(
    from_tag: str,
    to_tag: str,
    commits: list[dict[str, str]],
    group_by: str = "type",
) -> str:
    """Format commits as a markdown changelog."""
    lines = [
        f"# Release Notes: {to_tag}",
        "",
        f"**Changes since {from_tag}** ({len(commits)} commits)",
        "",
    ]

    if not commits:
        lines.append("No commits found in this range.")
        return "\n".join(lines)

    if group_by == "type":
        groups = group_by_type(commits)
        # Show known types first in a stable order, then unknown types
        ordered_types = [t for t in COMMIT_TYPE_LABELS if t in groups]
        other_types = sorted(t for t in groups if t not in COMMIT_TYPE_LABELS)
        for commit_type in ordered_types + other_types:
            label = COMMIT_TYPE_LABELS.get(commit_type, commit_type.capitalize())
            lines.append(f"## {label}")
            lines.append("")
            for c in groups[commit_type]:
                scope = f"**{c['parsed_scope']}:** " if c.get("parsed_scope") else ""
                short_hash = c["hash"][:7]
                lines.append(f"- {scope}{c['parsed_subject']} (`{short_hash}`)")
            lines.append("")

    elif group_by == "author":
        groups = group_by_author(commits)
        for author in sorted(groups.keys()):
            lines.append(f"## {author}")
            lines.append("")
            for c in groups[author]:
                short_hash = c["hash"][:7]
                lines.append(f"- {c['subject']} (`{short_hash}`)")
            lines.append("")

    else:  # flat
        for c in commits:
            short_hash = c["hash"][:7]
            lines.append(f"- {c['subject']} (`{short_hash}`)")
        lines.append("")

    return "\n".join(lines)


def format_plain(
    from_tag: str,
    to_tag: str,
    commits: list[dict[str, str]],
) -> str:
    """Format commits as plain text."""
    lines = [
        f"Release Notes: {to_tag}",
        f"Changes since {from_tag} ({len(commits)} commits)",
        "",
    ]
    for c in commits:
        short_hash = c["hash"][:7]
        lines.append(f"  * {c['subject']} ({short_hash})")
    return "\n".join(lines)


def format_slack(
    from_tag: str,
    to_tag: str,
    commits: list[dict[str, str]],
) -> str:
    """Format commits as Slack mrkdwn."""
    lines = [
        f"*Release Notes: {to_tag}*",
        f"Changes since `{from_tag}` ({len(commits)} commits)",
        "",
    ]
    groups = group_by_type(commits)
    ordered_types = [t for t in COMMIT_TYPE_LABELS if t in groups]
    other_types = sorted(t for t in groups if t not in COMMIT_TYPE_LABELS)
    for commit_type in ordered_types + other_types:
        label = COMMIT_TYPE_LABELS.get(commit_type, commit_type.capitalize())
        lines.append(f"*{label}*")
        for c in groups[commit_type]:
            scope = f"*{c['parsed_scope']}:* " if c.get("parsed_scope") else ""
            lines.append(f"  - {scope}{c['parsed_subject']}")
    return "\n".join(lines)


def generate_release_notes(
    repo_path: str = ".",
    from_tag: Optional[str] = None,
    to_tag: Optional[str] = None,
    output_format: str = "markdown",
    group_by: str = "type",
) -> str:
    """Generate release notes between two git tags.

    Args:
        repo_path: Path to the git repository.
        from_tag: Starting tag (older). Defaults to second-most-recent tag.
        to_tag: Ending tag (newer). Defaults to most recent tag.
        output_format: One of 'markdown', 'plain', or 'slack'.
        group_by: One of 'type', 'author', or 'flat'. Only used for markdown.

    Returns:
        Formatted release notes as a string.
    """
    repo_path = os.path.abspath(repo_path)
    tags = get_tags(repo_path)

    if not tags:
        return (
            "No git tags found. Create tags with `git tag v1.0.0` to use release notes."
        )

    if to_tag is None:
        to_tag = tags[0]

    if from_tag is None:
        if len(tags) < 2:
            # Only one tag — get all commits up to that tag
            from_tag = ""
        else:
            # Find the tag just before to_tag
            try:
                idx = tags.index(to_tag)
                if idx + 1 < len(tags):
                    from_tag = tags[idx + 1]
                else:
                    from_tag = ""
            except ValueError:
                from_tag = tags[1] if len(tags) > 1 else ""

    # Handle case where from_tag is empty (all commits up to to_tag)
    if not from_tag:
        commits = get_commits_between("", to_tag, repo_path)
        # If empty range didn't work, get all commits reachable from to_tag
        if not commits:
            output = run_git(
                [
                    "log",
                    to_tag,
                    f"--pretty=format:%H{FIELD_SEP}%an{FIELD_SEP}%ae{FIELD_SEP}%as{FIELD_SEP}%s{COMMIT_LOG_SEP}",
                    "--no-merges",
                ],
                repo_path,
            )
            commits = []
            for entry in output.split(COMMIT_LOG_SEP):
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
        from_tag = "(initial)"
    else:
        commits = get_commits_between(from_tag, to_tag, repo_path)

    if output_format == "plain":
        return format_plain(from_tag, to_tag, commits)
    elif output_format == "slack":
        return format_slack(from_tag, to_tag, commits)
    else:
        return format_markdown(from_tag, to_tag, commits, group_by=group_by)


def main():
    parser = argparse.ArgumentParser(
        description="Generate release notes from git tags."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--from-tag",
        default=None,
        help="Starting tag (default: second-most-recent tag)",
    )
    parser.add_argument(
        "--to-tag",
        default=None,
        help="Ending tag (default: most recent tag)",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "plain", "slack"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--group-by",
        choices=["type", "author", "flat"],
        default="type",
        help="How to group commits in markdown output (default: type)",
    )

    args = parser.parse_args()

    try:
        result = generate_release_notes(
            repo_path=args.repo,
            from_tag=args.from_tag,
            to_tag=args.to_tag,
            output_format=args.format,
            group_by=args.group_by,
        )
        print(result)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
