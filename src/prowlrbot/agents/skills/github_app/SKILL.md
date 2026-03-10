---
name: github_app
description: "GitHub App integration for autonomous PR reviews, issue triage, release note generation, and repository health monitoring. Processes webhook events and provides actionable insights on pull requests, issues, and overall project health."
metadata:
  {
    "prowlr":
      {
        "emoji": "🐙",
        "requires": {}
      }
  }
---

# GitHub App Integration

An autonomous GitHub integration skill that helps maintain repository quality through automated PR reviews, intelligent issue triage, release note generation, and continuous repo health monitoring.

## Capabilities

### 1. Automated PR Review

Analyze pull request diffs to catch common issues before human review. Use the `scripts/pr_review.py` script via the **shell** tool:

```bash
python scripts/pr_review.py --file /path/to/diff.patch
```

Or pipe a diff directly:

```bash
git diff main...feature-branch | python scripts/pr_review.py
```

The script parses unified diff format and flags:
- Large file changes (>500 lines)
- Binary files included in the diff
- TODO/FIXME/HACK comments left in new code
- Debug statements (`console.log`, `print()`, `debugger`, `binding.pry`)
- Sensitive patterns (API keys, tokens, passwords)
- Files with no test coverage changes when source files are modified

Output is a structured markdown review comment ready to post.

### 2. Issue Triage

Automatically classify and prioritize incoming issues. Use `scripts/issue_triage.py`:

```bash
python scripts/issue_triage.py --title "App crashes on startup" --body "After upgrading to v2.0, the app segfaults when..."
```

Options:
- `--title TEXT` — The issue title (required)
- `--body TEXT` — The issue body (optional, improves accuracy)
- `--format FORMAT` — Output format: `markdown` (default), `json`

Produces:
- **Suggested labels** — bug, feature, question, documentation, enhancement, security, performance, etc.
- **Priority estimate** — P0 (critical) through P3 (low) based on severity keywords
- **Assignee hints** — Suggested owners based on file paths and components mentioned
- **Response template** — A draft first-response for the issue author

### 3. Release Note Generation

Generate changelogs from git history between tags. For this capability, use the marketing skill's `release_notes.py` script or ask the agent to compile notes from PR titles and labels.

### 4. Repository Health Monitoring

Check overall repo health metrics. Use `scripts/repo_health.py`:

```bash
python scripts/repo_health.py --repo /path/to/repo
```

Options:
- `--repo PATH` — Path to the git repository (defaults to current directory)
- `--days DAYS` — Lookback window for stale thresholds (default: 30)
- `--format FORMAT` — Output format: `markdown` (default), `json`

Reports on:
- Open vs. closed issues and PRs
- Stale PRs (no activity in 30+ days)
- Unanswered issues (no comments in 7+ days)
- Commit frequency and contributor activity
- Branch hygiene (merged but undeleted branches)

### 5. Webhook Event Processing

When configured as a GitHub App, ProwlrBot receives webhook events and takes action automatically. See `references/webhook_events.md` for supported events and behaviors.

Supported events:
- **push** — Analyze commits for quality
- **pull_request** — Auto-review new and updated PRs
- **issues** — Triage new issues
- **issue_comment** — Respond to mentions and commands
- **release** — Generate and enhance release notes

## Usage Examples

- "Review the diff for PR #42"
- "Triage this issue: title='Login broken on Safari', body='...'"
- "Run a health check on this repo"
- "What webhook events does the GitHub App handle?"
- "Analyze the last 10 PRs for review patterns"

## Reference Files

- `references/webhook_events.md` — Supported GitHub webhook events and agent behaviors

## Notes

- PR review output is advisory — always have a human approve before merging.
- Issue triage uses keyword heuristics, not ML classification. Accuracy improves when issue templates are used.
- Repo health checks require a local git clone with full history (not a shallow clone).
- Sensitive pattern detection is best-effort; do not rely on it as a sole security gate.
