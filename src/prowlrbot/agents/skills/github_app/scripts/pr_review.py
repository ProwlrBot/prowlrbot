#!/usr/bin/env python3
"""PR diff review script for ProwlrBot GitHub App skill.

Parses a unified diff (from stdin or a file) and produces a structured
markdown review highlighting potential issues.

Usage:
    git diff main...feature | python pr_review.py
    python pr_review.py --file /path/to/diff.patch
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from typing import TextIO


# ---------------------------------------------------------------------------
# Patterns to flag
# ---------------------------------------------------------------------------

DEBUG_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("console.log", re.compile(r"\bconsole\.(log|debug|info|warn|error)\b")),
    ("print()", re.compile(r"\bprint\s*\(")),
    ("debugger", re.compile(r"\bdebugger\b")),
    ("binding.pry", re.compile(r"\bbinding\.pry\b")),
    ("var_dump", re.compile(r"\bvar_dump\s*\(")),
    ("pp / pprint", re.compile(r"\b(pp|pprint)\s*[\.(]")),
    ("System.out.println", re.compile(r"\bSystem\.out\.print(ln)?\s*\(")),
    ("fmt.Println", re.compile(r"\bfmt\.(Print|Println|Printf)\s*\(")),
]

TODO_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX|NOCOMMIT)\b", re.IGNORECASE)

SENSITIVE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("API key", re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][A-Za-z0-9]")),
    ("Secret/Token", re.compile(r"(?i)(secret|token|password|passwd)\s*[:=]\s*['\"][A-Za-z0-9]")),
    ("AWS key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private key", re.compile(r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----")),
]

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z",
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".pptx",
    ".pyc", ".pyo", ".class", ".o", ".obj",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".sqlite", ".db",
}

LARGE_CHANGE_THRESHOLD = 500  # lines added+deleted in a single file


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FileDiff:
    """Represents the diff for a single file."""
    filename: str
    old_filename: str | None = None
    is_new: bool = False
    is_deleted: bool = False
    is_rename: bool = False
    is_binary: bool = False
    additions: int = 0
    deletions: int = 0
    added_lines: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class Issue:
    """A flagged issue found during review."""
    severity: str  # "warning" | "info" | "error"
    category: str
    filename: str
    line: int | None
    message: str


# ---------------------------------------------------------------------------
# Diff parsing
# ---------------------------------------------------------------------------

def parse_diff(stream: TextIO) -> list[FileDiff]:
    """Parse a unified diff into a list of FileDiff objects."""
    files: list[FileDiff] = []
    current: FileDiff | None = None
    current_new_line = 0

    for raw_line in stream:
        line = raw_line.rstrip("\n\r")

        # New file header
        if line.startswith("diff --git"):
            parts = line.split(" b/", 1)
            filename = parts[1] if len(parts) > 1 else line.split()[-1]
            current = FileDiff(filename=filename)
            files.append(current)
            continue

        if current is None:
            continue

        # Detect binary files
        if line.startswith("Binary files") or line.startswith("GIT binary patch"):
            current.is_binary = True
            continue

        # New / deleted file markers
        if line.startswith("new file mode"):
            current.is_new = True
            continue
        if line.startswith("deleted file mode"):
            current.is_deleted = True
            continue

        # Rename detection
        if line.startswith("rename from "):
            current.is_rename = True
            current.old_filename = line[len("rename from "):]
            continue
        if line.startswith("rename to "):
            current.is_rename = True
            current.filename = line[len("rename to "):]
            continue

        # Hunk header — extract new-file line number
        if line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            if match:
                current_new_line = int(match.group(1))
            continue

        # Added lines
        if line.startswith("+") and not line.startswith("+++"):
            current.additions += 1
            current.added_lines.append((current_new_line, line[1:]))
            current_new_line += 1
            continue

        # Deleted lines
        if line.startswith("-") and not line.startswith("---"):
            current.deletions += 1
            continue

        # Context line — advances new-file line counter
        if not line.startswith("\\"):
            current_new_line += 1

    return files


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _get_extension(filename: str) -> str:
    """Get the lowercased file extension."""
    dot = filename.rfind(".")
    if dot == -1:
        return ""
    return filename[dot:].lower()


def analyze(files: list[FileDiff]) -> list[Issue]:
    """Run all checks against parsed file diffs and return issues."""
    issues: list[Issue] = []

    for f in files:
        ext = _get_extension(f.filename)

        # Binary file check
        if f.is_binary or ext in BINARY_EXTENSIONS:
            issues.append(Issue(
                severity="warning",
                category="Binary file",
                filename=f.filename,
                line=None,
                message=f"Binary file detected in diff. Consider using Git LFS or adding to .gitignore.",
            ))
            continue

        # Large change check
        total_changes = f.additions + f.deletions
        if total_changes > LARGE_CHANGE_THRESHOLD:
            issues.append(Issue(
                severity="warning",
                category="Large change",
                filename=f.filename,
                line=None,
                message=(
                    f"Large change: {f.additions} additions, {f.deletions} deletions "
                    f"({total_changes} total). Consider breaking into smaller PRs."
                ),
            ))

        # Scan added lines for patterns
        for line_num, content in f.added_lines:
            # Debug statements
            for name, pattern in DEBUG_PATTERNS:
                if pattern.search(content):
                    issues.append(Issue(
                        severity="warning",
                        category="Debug statement",
                        filename=f.filename,
                        line=line_num,
                        message=f"Debug statement `{name}` found — remove before merging.",
                    ))

            # TODO/FIXME markers
            match = TODO_PATTERN.search(content)
            if match:
                issues.append(Issue(
                    severity="info",
                    category="TODO marker",
                    filename=f.filename,
                    line=line_num,
                    message=f"`{match.group(0)}` comment found: `{content.strip()}`",
                ))

            # Sensitive data
            for name, pattern in SENSITIVE_PATTERNS:
                if pattern.search(content):
                    issues.append(Issue(
                        severity="error",
                        category="Sensitive data",
                        filename=f.filename,
                        line=line_num,
                        message=f"Possible {name} detected — do not commit secrets to the repository.",
                    ))

    return issues


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

_SEVERITY_ICON = {
    "error": "🔴",
    "warning": "🟡",
    "info": "🔵",
}


def generate_report(files: list[FileDiff], issues: list[Issue]) -> str:
    """Produce a markdown review report."""
    total_additions = sum(f.additions for f in files)
    total_deletions = sum(f.deletions for f in files)
    total_files = len(files)

    lines: list[str] = []
    lines.append("## PR Review Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Files changed | {total_files} |")
    lines.append(f"| Additions | +{total_additions} |")
    lines.append(f"| Deletions | -{total_deletions} |")
    lines.append(f"| Issues found | {len(issues)} |")
    lines.append("")

    # File breakdown
    lines.append("### Files Changed")
    lines.append("")
    for f in files:
        status = ""
        if f.is_new:
            status = " (new)"
        elif f.is_deleted:
            status = " (deleted)"
        elif f.is_rename:
            status = f" (renamed from `{f.old_filename}`)"
        elif f.is_binary:
            status = " (binary)"
        lines.append(f"- `{f.filename}`{status} — +{f.additions} / -{f.deletions}")
    lines.append("")

    # Issues
    if issues:
        lines.append("### Issues Found")
        lines.append("")

        # Group by severity for readability
        for severity in ("error", "warning", "info"):
            severity_issues = [i for i in issues if i.severity == severity]
            if not severity_issues:
                continue

            icon = _SEVERITY_ICON.get(severity, "")
            lines.append(f"#### {icon} {severity.upper()} ({len(severity_issues)})")
            lines.append("")

            for issue in severity_issues:
                loc = f"`{issue.filename}"
                if issue.line is not None:
                    loc += f":{issue.line}"
                loc += "`"
                lines.append(f"- **{issue.category}** in {loc}")
                lines.append(f"  {issue.message}")
                lines.append("")
    else:
        lines.append("### No Issues Found")
        lines.append("")
        lines.append("This diff looks clean. No debug statements, TODO markers, ")
        lines.append("sensitive data, or oversized changes detected.")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by ProwlrBot GitHub App skill*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Review a PR diff and output a structured markdown report.",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=None,
        help="Path to a diff/patch file. If omitted, reads from stdin.",
    )

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
                files = parse_diff(fh)
        except FileNotFoundError:
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print(
                "No input. Pipe a diff or use --file. Example:\n"
                "  git diff main...branch | python pr_review.py\n"
                "  python pr_review.py --file changes.patch",
                file=sys.stderr,
            )
            sys.exit(1)
        files = parse_diff(sys.stdin)

    issues = analyze(files)
    report = generate_report(files, issues)
    print(report)


if __name__ == "__main__":
    main()
