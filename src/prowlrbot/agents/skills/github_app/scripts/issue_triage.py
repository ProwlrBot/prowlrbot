#!/usr/bin/env python3
"""Issue triage script for ProwlrBot GitHub App skill.

Analyzes an issue title and body to suggest labels, priority, assignee
hints, and a response template.

Usage:
    python issue_triage.py --title "App crashes on startup" --body "After upgrading..."
    python issue_triage.py --title "Add dark mode" --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Label detection rules
# ---------------------------------------------------------------------------
# Each rule: (label, patterns_in_title_or_body)
# Patterns are case-insensitive partial matches.

LABEL_RULES: list[tuple[str, list[str]]] = [
    ("bug", [
        r"\bcrash(es|ed|ing)?\b", r"\bbug\b", r"\bbroken\b", r"\bfail(s|ed|ing|ure)?\b",
        r"\berror\b", r"\bexception\b", r"\bsegfault\b", r"\bregression\b",
        r"\bdoesn'?t work\b", r"\bnot working\b", r"\bunexpected\b",
        r"\b500\b", r"\b404\b", r"\btraceback\b", r"\bpanic\b",
    ]),
    ("feature", [
        r"\bfeature\b", r"\brequest\b", r"\badd(ing)?\b", r"\bnew\b",
        r"\bimplement\b", r"\bsupport\b", r"\bpropos(e|al)\b",
        r"\bwould be (nice|great|good)\b", r"\bwish\b",
    ]),
    ("enhancement", [
        r"\bimprove\b", r"\benhance\b", r"\boptimize\b", r"\bupgrade\b",
        r"\bbetter\b", r"\brefactor\b", r"\bclean\s?up\b",
    ]),
    ("question", [
        r"\bhow (do|can|to)\b", r"\bquestion\b", r"\bis (it|there)\b",
        r"\bwhat (is|are|does)\b", r"\bwhy (does|is|do)\b",
        r"\bhelp\b", r"\bconfused\b",
    ]),
    ("documentation", [
        r"\bdoc(s|umentation)?\b", r"\breadme\b", r"\btypo\b",
        r"\bexample\b", r"\btutorial\b", r"\bguide\b",
    ]),
    ("security", [
        r"\bsecurity\b", r"\bvulnerabilit(y|ies)\b", r"\bcve\b",
        r"\binjection\b", r"\bxss\b", r"\bcsrf\b", r"\bauth(entication)?\b",
        r"\bpermission\b", r"\bleak\b", r"\bexploit\b",
    ]),
    ("performance", [
        r"\bperformance\b", r"\bslow\b", r"\blatency\b", r"\bmemory\b",
        r"\bcpu\b", r"\btimeout\b", r"\bbottleneck\b", r"\blag\b",
    ]),
    ("dependencies", [
        r"\bdependenc(y|ies)\b", r"\bupdate .* version\b", r"\bnpm\b",
        r"\bpip\b", r"\bpackage\b", r"\bupgrade\b.*\bversion\b",
    ]),
    ("ci/cd", [
        r"\bci\b", r"\bcd\b", r"\bgithub actions?\b", r"\bpipeline\b",
        r"\bbuild\b", r"\bdeploy\b", r"\bworkflow\b",
    ]),
    ("good first issue", [
        r"\btypo\b", r"\bspelling\b", r"\bgrammar\b",
        r"\bminor\b", r"\bsmall\b",
    ]),
]

# ---------------------------------------------------------------------------
# Priority detection
# ---------------------------------------------------------------------------

PRIORITY_RULES: list[tuple[str, str, list[str]]] = [
    # (priority, description, patterns)
    ("P0", "Critical — system down, data loss, or security breach", [
        r"\bcrash(es|ed)?\b", r"\bsegfault\b", r"\bdata loss\b",
        r"\bsecurity\b", r"\bvulnerabilit(y|ies)\b", r"\bcve\b",
        r"\bproduction (down|broken|outage)\b", r"\bblocking\b",
        r"\bcritical\b", r"\burgent\b", r"\bemergency\b",
    ]),
    ("P1", "High — major functionality broken for many users", [
        r"\bbroken\b", r"\bfail(s|ed|ure)\b", r"\berror\b",
        r"\bregression\b", r"\bcannot\b", r"\bunable to\b",
        r"\bdoesn'?t work\b", r"\bnot working\b",
        r"\b500\b", r"\bpanic\b",
    ]),
    ("P2", "Medium — feature request or non-critical bug", [
        r"\bfeature\b", r"\brequest\b", r"\bimprove\b",
        r"\benhance\b", r"\bwould be\b", r"\bshould\b",
        r"\bexpected\b", r"\binconsistent\b",
    ]),
    ("P3", "Low — cosmetic, typos, minor suggestions", [
        r"\btypo\b", r"\bspelling\b", r"\bgrammar\b",
        r"\bcosmetic\b", r"\bminor\b", r"\bnit\b",
        r"\bnice to have\b",
    ]),
]

# ---------------------------------------------------------------------------
# Assignee hint rules — map file path patterns to component owners
# ---------------------------------------------------------------------------

COMPONENT_OWNERS: list[tuple[str, str, list[str]]] = [
    # (component, owner_hint, file path patterns)
    ("Channels", "channels-team", [
        r"\bchannel\b", r"\bdiscord\b", r"\btelegram\b",
        r"\bfeishu\b", r"\bdingtalk\b", r"\bslack\b", r"\bimessage\b",
    ]),
    ("CLI", "cli-team", [
        r"\bcli\b", r"\bcommand\b", r"\bterminal\b",
    ]),
    ("Agent Core", "agent-team", [
        r"\bagent\b", r"\breact\b", r"\bprompt\b",
        r"\bmemory\b", r"\btool\b", r"\bskill\b",
    ]),
    ("MCP", "mcp-team", [
        r"\bmcp\b", r"\bmodel context\b",
    ]),
    ("Providers", "providers-team", [
        r"\bprovider\b", r"\bmodel\b", r"\bollama\b",
        r"\bopenai\b", r"\banthropic\b", r"\bgroq\b",
    ]),
    ("Console UI", "frontend-team", [
        r"\bconsole\b", r"\bui\b", r"\bfrontend\b",
        r"\breact\b", r"\bvite\b", r"\bant design\b",
    ]),
    ("Config", "config-team", [
        r"\bconfig\b", r"\bsettings?\b", r"\benv\b",
    ]),
    ("Cron", "cron-team", [
        r"\bcron\b", r"\bschedul\b", r"\bheartbeat\b",
    ]),
    ("Docker/Swarm", "infra-team", [
        r"\bdocker\b", r"\bswarm\b", r"\bcontainer\b",
    ]),
    ("Documentation", "docs-team", [
        r"\bdoc(s|umentation)?\b", r"\breadme\b",
    ]),
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TriageResult:
    """Result of triaging an issue."""
    title: str
    labels: list[str] = field(default_factory=list)
    priority: str = "P2"
    priority_description: str = "Medium — feature request or non-critical bug"
    assignee_hints: list[tuple[str, str]] = field(default_factory=list)
    response_template: str = ""


# ---------------------------------------------------------------------------
# Triage logic
# ---------------------------------------------------------------------------

def _match_any(text: str, patterns: list[str]) -> bool:
    """Return True if any pattern matches the text (case-insensitive)."""
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _match_count(text: str, patterns: list[str]) -> int:
    """Count how many patterns match the text."""
    count = 0
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            count += 1
    return count


def triage(title: str, body: str = "") -> TriageResult:
    """Analyze an issue and produce triage suggestions."""
    combined = f"{title}\n{body}"
    result = TriageResult(title=title)

    # --- Labels ---
    label_scores: dict[str, int] = {}
    for label, patterns in LABEL_RULES:
        score = _match_count(combined, patterns)
        if score > 0:
            label_scores[label] = score

    # Sort by match count descending, take top labels
    sorted_labels = sorted(label_scores.items(), key=lambda x: x[1], reverse=True)
    result.labels = [label for label, _ in sorted_labels]

    # If no labels matched, default to "triage-needed"
    if not result.labels:
        result.labels = ["triage-needed"]

    # --- Priority ---
    # Check from highest to lowest; first match wins
    for priority, description, patterns in PRIORITY_RULES:
        if _match_any(combined, patterns):
            result.priority = priority
            result.priority_description = description
            break

    # --- Assignee hints ---
    seen_components: set[str] = set()
    for component, owner_hint, patterns in COMPONENT_OWNERS:
        if _match_any(combined, patterns) and component not in seen_components:
            result.assignee_hints.append((component, owner_hint))
            seen_components.add(component)

    # --- Response template ---
    result.response_template = _build_response_template(result)

    return result


def _build_response_template(result: TriageResult) -> str:
    """Generate a response template for the issue author."""
    lines: list[str] = []

    if "bug" in result.labels:
        lines.append("Thank you for reporting this issue.")
        lines.append("")
        lines.append("To help us investigate, could you please provide:")
        lines.append("1. Steps to reproduce the problem")
        lines.append("2. Expected vs. actual behavior")
        lines.append("3. Your environment (OS, Python version, ProwlrBot version)")
        lines.append("4. Any relevant logs or error messages")
    elif "feature" in result.labels or "enhancement" in result.labels:
        lines.append("Thank you for this suggestion!")
        lines.append("")
        lines.append("To help us evaluate, could you describe:")
        lines.append("1. The use case this would address")
        lines.append("2. Any alternatives you have considered")
        lines.append("3. Whether you would be interested in contributing a PR")
    elif "question" in result.labels:
        lines.append("Thanks for reaching out!")
        lines.append("")
        lines.append("We will look into this and get back to you. "
                      "In the meantime, you might find the answer in our documentation.")
    elif "security" in result.labels:
        lines.append("Thank you for reporting this security concern.")
        lines.append("")
        lines.append("**Important:** If this is a security vulnerability, please do not "
                      "discuss details publicly. Instead, email security@prowlrbot.dev "
                      "or use GitHub's private vulnerability reporting feature.")
    else:
        lines.append("Thank you for opening this issue. We will review it shortly.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_markdown(result: TriageResult) -> str:
    """Format triage result as markdown."""
    lines: list[str] = []

    lines.append("## Issue Triage Report")
    lines.append("")
    lines.append(f"**Title:** {result.title}")
    lines.append("")

    # Labels
    label_badges = " ".join(f"`{label}`" for label in result.labels)
    lines.append(f"### Suggested Labels")
    lines.append("")
    lines.append(label_badges)
    lines.append("")

    # Priority
    lines.append(f"### Priority")
    lines.append("")
    lines.append(f"**{result.priority}** — {result.priority_description}")
    lines.append("")

    # Assignee hints
    if result.assignee_hints:
        lines.append("### Suggested Assignees")
        lines.append("")
        lines.append("| Component | Owner Hint |")
        lines.append("|-----------|------------|")
        for component, owner in result.assignee_hints:
            lines.append(f"| {component} | `{owner}` |")
        lines.append("")

    # Response template
    lines.append("### Suggested Response")
    lines.append("")
    lines.append("```markdown")
    lines.append(result.response_template)
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("*Generated by ProwlrBot GitHub App skill*")

    return "\n".join(lines)


def format_json(result: TriageResult) -> str:
    """Format triage result as JSON."""
    data = {
        "title": result.title,
        "labels": result.labels,
        "priority": result.priority,
        "priority_description": result.priority_description,
        "assignee_hints": [
            {"component": c, "owner_hint": o} for c, o in result.assignee_hints
        ],
        "response_template": result.response_template,
    }
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Triage a GitHub issue and suggest labels, priority, and assignees.",
    )
    parser.add_argument(
        "--title", "-t",
        type=str,
        required=True,
        help="Issue title.",
    )
    parser.add_argument(
        "--body", "-b",
        type=str,
        default="",
        help="Issue body text.",
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown).",
    )

    args = parser.parse_args()

    result = triage(args.title, args.body)

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_markdown(result))


if __name__ == "__main__":
    main()
