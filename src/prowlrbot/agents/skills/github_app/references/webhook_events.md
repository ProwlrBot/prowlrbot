# Supported GitHub Webhook Events

This document describes the GitHub webhook events that ProwlrBot's GitHub App skill processes, what triggers each event, how the agent responds, and key payload fields.

---

## 1. push

**Trigger:** A commit or series of commits is pushed to a repository branch.

**Agent behavior:**
- Checks pushed commits for quality signals (large files, sensitive data patterns, TODO markers).
- If the push is to the default branch, logs a summary of changes for the daily digest.
- Flags force-pushes for team awareness.

**Key payload fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ref` | string | Full ref that was pushed (e.g., `refs/heads/main`) |
| `before` | string | SHA of the previous HEAD commit |
| `after` | string | SHA of the new HEAD commit |
| `commits` | array | List of commit objects in the push |
| `commits[].id` | string | SHA of the commit |
| `commits[].message` | string | Commit message |
| `commits[].added` | array | Files added in this commit |
| `commits[].modified` | array | Files modified in this commit |
| `commits[].removed` | array | Files removed in this commit |
| `commits[].author.name` | string | Author name |
| `commits[].author.email` | string | Author email |
| `forced` | boolean | Whether the push was a force-push |
| `pusher.name` | string | Username of the pusher |
| `repository.full_name` | string | Full repo name (e.g., `owner/repo`) |

**Example scenario:** A developer pushes 3 commits to `main`. The agent scans each commit's changed files, flags a new 2MB JSON fixture that was accidentally committed, and posts a warning.

---

## 2. pull_request

**Trigger:** A pull request is opened, edited, closed, merged, synchronize (new commits pushed), or its review state changes.

**Agent behavior:**
- **opened / synchronize:** Runs `pr_review.py` against the PR diff. Posts a structured review comment highlighting potential issues, file change summary, and quality signals.
- **closed (merged):** Logs the merge for release note generation. Checks if the source branch should be cleaned up.
- **closed (not merged):** No action (optional: log abandonment metrics).
- **edited:** Re-evaluates labels if the title or body changed significantly.

**Key payload fields:**

| Field | Type | Description |
|-------|------|-------------|
| `action` | string | What happened: `opened`, `closed`, `synchronize`, `edited`, `reopened`, etc. |
| `number` | integer | PR number |
| `pull_request.title` | string | PR title |
| `pull_request.body` | string | PR description |
| `pull_request.state` | string | `open` or `closed` |
| `pull_request.merged` | boolean | Whether the PR was merged |
| `pull_request.diff_url` | string | URL to fetch the diff |
| `pull_request.user.login` | string | Author's GitHub username |
| `pull_request.head.ref` | string | Source branch name |
| `pull_request.base.ref` | string | Target branch name |
| `pull_request.changed_files` | integer | Number of files changed |
| `pull_request.additions` | integer | Lines added |
| `pull_request.deletions` | integer | Lines deleted |
| `pull_request.labels` | array | Labels applied to the PR |
| `pull_request.requested_reviewers` | array | Requested reviewers |

**Example scenario:** A contributor opens a PR adding a new channel adapter. The agent fetches the diff, runs `pr_review.py`, finds 2 leftover `print()` debug statements and a TODO comment, and posts a review comment suggesting they be addressed before merge.

---

## 3. issues

**Trigger:** An issue is opened, edited, deleted, transferred, pinned, unpinned, closed, reopened, assigned, unassigned, labeled, unlabeled, locked, unlocked, or milestoned.

**Agent behavior:**
- **opened:** Runs `issue_triage.py` with the title and body. Applies suggested labels, sets priority, and posts a triage comment with a response template.
- **edited:** Re-runs triage if the title or body changed substantially.
- **closed:** Logs resolution time for health metrics.
- **labeled / unlabeled:** Tracks label changes for triage accuracy reporting.

**Key payload fields:**

| Field | Type | Description |
|-------|------|-------------|
| `action` | string | What happened: `opened`, `closed`, `edited`, `labeled`, etc. |
| `issue.number` | integer | Issue number |
| `issue.title` | string | Issue title |
| `issue.body` | string | Issue body (markdown) |
| `issue.state` | string | `open` or `closed` |
| `issue.user.login` | string | Author's GitHub username |
| `issue.labels` | array | Current labels on the issue |
| `issue.assignees` | array | Assigned users |
| `issue.created_at` | string | ISO 8601 timestamp |
| `issue.comments` | integer | Number of comments |

**Example scenario:** A user opens an issue titled "Crash when connecting to Discord channel". The agent triages it as `bug` + `P1` (crash keyword), suggests assigning to whoever last touched `channels/discord_/`, and posts an acknowledgment comment asking for reproduction steps.

---

## 4. issue_comment

**Trigger:** A comment is created, edited, or deleted on an issue or pull request.

**Agent behavior:**
- **created:** Checks if the comment mentions the bot (e.g., `@prowlrbot`) or contains a command (e.g., `/review`, `/triage`, `/health`).
  - `/review` on a PR: Triggers a fresh PR review.
  - `/triage` on an issue: Re-runs triage analysis.
  - `/health` anywhere: Runs repo health check and posts results.
  - `/release-notes` on a PR: Drafts release note entry from the PR.
- If the comment is on an issue that has been unanswered for 7+ days, resets the "unanswered" timer.

**Key payload fields:**

| Field | Type | Description |
|-------|------|-------------|
| `action` | string | `created`, `edited`, or `deleted` |
| `comment.id` | integer | Comment ID |
| `comment.body` | string | Comment text (markdown) |
| `comment.user.login` | string | Commenter's GitHub username |
| `comment.created_at` | string | ISO 8601 timestamp |
| `issue.number` | integer | Associated issue/PR number |
| `issue.pull_request` | object or null | Present if the comment is on a PR |

**Example scenario:** A maintainer comments `/review` on PR #87. The agent fetches the latest diff, runs the review script, and posts an updated review comment.

---

## 5. release

**Trigger:** A release is published, unpublished, created, edited, deleted, or prereleased.

**Agent behavior:**
- **published:** Generates or enhances release notes by:
  1. Collecting all merged PRs since the previous release tag.
  2. Grouping changes by conventional commit type (features, fixes, docs, etc.).
  3. Highlighting breaking changes prominently.
  4. Posting the generated notes as a comment on the release (or updating the release body if configured).
- **prereleased:** Same as published but marks output as "pre-release notes (draft)."
- **edited:** Re-generates if the tag range changed.

**Key payload fields:**

| Field | Type | Description |
|-------|------|-------------|
| `action` | string | `published`, `created`, `edited`, `prereleased`, etc. |
| `release.tag_name` | string | Git tag for the release (e.g., `v2.1.0`) |
| `release.name` | string | Release title |
| `release.body` | string | Release description/notes (markdown) |
| `release.draft` | boolean | Whether this is a draft release |
| `release.prerelease` | boolean | Whether this is a pre-release |
| `release.target_commitish` | string | Branch or SHA the tag points to |
| `release.author.login` | string | Release author's username |
| `release.published_at` | string | ISO 8601 timestamp |
| `release.html_url` | string | URL to the release page |

**Example scenario:** A maintainer publishes release `v2.1.0`. The agent finds all 23 merged PRs since `v2.0.0`, groups them into 8 features, 12 fixes, and 3 docs updates, flags 1 breaking change, and updates the release body with formatted notes.
