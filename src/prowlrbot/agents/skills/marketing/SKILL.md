---
name: marketing
author: "kdairatchi"
license: "Apache-2.0"
description: "Autonomous marketing agent for open-source projects. Drafts social media posts, generates release notes from git history, produces engagement reports, monitors competitors, and manages content pipelines across platforms."
metadata:
  {
    "prowlr":
      {
        "emoji": "📣",
        "requires": {}
      }
  }
---

# Marketing Automation

An autonomous marketing skill for promoting open-source projects. It helps maintain a consistent brand voice, generate content across platforms, and track community engagement — all without leaving ProwlrBot.

## Capabilities

### 1. Social Media Drafting

Generate platform-appropriate posts for announcements, releases, feature highlights, and community milestones. Each draft respects platform-specific character limits and formatting conventions.

**Supported platforms:**
- **Twitter/X** — 280-character posts with hashtags and links
- **Reddit** — Markdown-formatted posts for subreddit submissions
- **Hacker News** — Plain-text titles and descriptions optimized for technical audiences
- **Discord** — Rich embed messages with fields, colors, and thumbnails
- **Blog** — Long-form markdown articles with frontmatter

When the user asks to draft a post, refer to `references/platforms.md` for formatting rules and `references/brand_voice.md` for tone guidelines.

### 2. Release Note Generation

Automatically generate changelogs and release notes from git history. Use the `scripts/release_notes.py` script via the **shell** tool:

```bash
python scripts/release_notes.py --repo /path/to/repo
```

Options:
- `--repo PATH` — Path to the git repository (defaults to current directory)
- `--from-tag TAG` — Start tag (defaults to second-most-recent tag)
- `--to-tag TAG` — End tag (defaults to most recent tag)
- `--format FORMAT` — Output format: `markdown` (default), `plain`, or `slack`
- `--group-by TYPE` — Group commits by: `type` (conventional commits), `author`, or `flat`

The script parses conventional commit messages (feat, fix, docs, refactor, etc.) and groups them into sections.

### 3. Weekly Digest

Generate a weekly project digest using `scripts/weekly_digest.py`:

```bash
python scripts/weekly_digest.py --repo /path/to/repo --week 2026-03-02
```

Options:
- `--repo PATH` — Path to the git repository (defaults to current directory)
- `--week DATE` — Monday of the target week in YYYY-MM-DD format (defaults to current week)
- `--output PATH` — Output file path (defaults to stdout)

Produces a structured markdown report with sections for highlights, metrics, upcoming work, and community spotlight.

### 4. Engagement Reports

When asked for an engagement report, gather metrics by:
1. Using **browser_use** to visit the project's GitHub insights page
2. Collecting stars, forks, issues opened/closed, and PR activity
3. Comparing against previous periods if historical data is available
4. Formatting a summary with trends and recommendations

### 5. Competitor Monitoring

Monitor competitor projects by:
1. Taking a list of competitor GitHub repos or websites from the user
2. Using **browser_use** to check for new releases, blog posts, or feature announcements
3. Summarizing findings with relevance to the user's project
4. Suggesting differentiation opportunities

### 6. Content Pipeline Management

Help plan and schedule content by:
1. Maintaining a content calendar (user provides topics and dates)
2. Drafting content in advance for each scheduled item
3. Suggesting optimal posting times based on platform best practices
4. Tracking which content has been published vs. pending

## Usage Examples

- "Draft a Twitter thread announcing our v2.0 release"
- "Generate release notes for the latest tag"
- "Write a Reddit post for r/selfhosted about ProwlrBot"
- "Create this week's project digest"
- "Monitor these 3 competitor repos for new releases"
- "Plan a content calendar for the next 2 weeks"

## Reference Files

- `references/brand_voice.md` — Tone, messaging principles, and tagline usage
- `references/platforms.md` — Platform-specific formatting guidelines and constraints

## Notes

- Always follow the brand voice guidelines when generating any public-facing content.
- Adapt the level of technical detail to the target platform audience.
- When generating release notes, ensure the repository has git tags; if not, suggest creating them first.
- All generated content is a draft — remind the user to review before publishing.
