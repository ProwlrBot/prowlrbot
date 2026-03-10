# Platform-Specific Formatting Guidelines

## Twitter / X

- **Character limit:** 280 characters (links consume 23 characters regardless of length)
- **Format:** Plain text with optional hashtags at the end
- **Links:** One link per post preferred; use the project URL or release page
- **Hashtags:** 2-3 max, placed at the end
- **Threads:** For longer announcements, use a thread (numbered tweets). First tweet should be self-contained and compelling.
- **Media:** Mention if an image or GIF should be attached (e.g., terminal recording, architecture diagram)

### Template

```
[Announcement or hook — keep under 200 chars to leave room for link + hashtags]

[Link]

#ProwlrBot #OpenSource
```

### Example

```
ProwlrBot v2.0 is here — multi-provider smart routing, Docker Swarm support, and 12 new skills.

https://github.com/prowlrbot/prowlrbot/releases/tag/v2.0.0

#ProwlrBot #AIAgent #OpenSource
```

---

## Reddit

- **Format:** Markdown (Reddit flavor)
- **Title:** Descriptive, no clickbait. Include [Project Name] prefix for self-promotion posts.
- **Body:** Start with a 1-2 sentence summary. Use headers, bullet points, and code blocks.
- **Subreddits:** Target relevant communities (r/selfhosted, r/opensource, r/MachineLearning, r/Python, r/homelab)
- **Rules:** Read each subreddit's rules before posting. Many require specific flair or formats.
- **Tone:** Conversational and honest. Reddit audiences dislike overt marketing. Lead with value and utility.
- **Self-promotion ratio:** Follow the 10:1 rule (10 community contributions per 1 self-promotion post)

### Template

```markdown
# [Project Name] — [One-line description]

**What it does:** [2-3 sentences explaining the core value]

**Key features:**
- Feature 1
- Feature 2
- Feature 3

**Getting started:**
```bash
pip install prowlrbot
prowlr init --defaults
prowlr app
```

**Links:** [GitHub](url) | [Docs](url)

Happy to answer any questions!
```

---

## Hacker News

- **Format:** Plain text only (no markdown rendering in titles; comments support basic formatting)
- **Title:** Factual, concise. Follow HN conventions: "Show HN: [Name] – [Description]" for launches.
- **Comment/body:** Technical depth appreciated. Explain architecture decisions, trade-offs, and what makes this different. No hype words.
- **Tone:** Understated and technical. HN audiences value substance over polish.
- **Avoid:** Emojis, marketing language, superlatives ("revolutionary", "game-changing", "blazing fast")

### Title Template

```
Show HN: ProwlrBot – [Concise technical description]
```

### Title Examples

```
Show HN: ProwlrBot – Self-hosted autonomous AI agent with multi-channel support
Show HN: ProwlrBot – Open-source AI agent platform with MCP tool integration
```

### First Comment Template

```
Hey HN, I built ProwlrBot because [motivation].

Technical details:
- [Architecture point 1]
- [Architecture point 2]
- [Architecture point 3]

Stack: [languages, frameworks, key dependencies]

Repo: [URL]

Would love feedback on [specific area].
```

---

## Discord

- **Format:** Rich embeds with markdown support
- **Embeds:** Use structured fields for announcements. Include color coding (green for releases, blue for updates, yellow for community).
- **Mentions:** Use @here for important announcements, avoid @everyone
- **Channels:** Post in the appropriate channel (announcements, releases, general)
- **Length:** Keep embed descriptions under 2048 characters; field values under 1024 characters

### Embed Structure

```json
{
  "title": "ProwlrBot v2.0 Released",
  "description": "A brief summary of what this release includes and why it matters.",
  "color": 3066993,
  "fields": [
    {
      "name": "New Features",
      "value": "- Feature 1\n- Feature 2\n- Feature 3",
      "inline": false
    },
    {
      "name": "Bug Fixes",
      "value": "- Fix 1\n- Fix 2",
      "inline": false
    },
    {
      "name": "Links",
      "value": "[Release Notes](url) | [Upgrade Guide](url)",
      "inline": false
    }
  ],
  "footer": {
    "text": "Always watching. Always ready."
  }
}
```

### Plain Message Template

```
**ProwlrBot v2.0** is out!

Here's what's new:
- Feature 1
- Feature 2
- Feature 3

Full release notes: <link>
```

---

## Blog Posts

- **Format:** Markdown with YAML frontmatter
- **Length:** 800-2000 words for announcements; 1500-3000 for technical deep-dives
- **Structure:** Title, intro hook, sections with headers, code examples, conclusion with CTA
- **Images:** Reference where screenshots or diagrams should be placed
- **SEO:** Include a meta description (150-160 chars) in frontmatter
- **Tone:** More detailed and polished than social posts. Can be narrative.

### Frontmatter Template

```yaml
---
title: "ProwlrBot v2.0: What's New"
date: 2026-03-10
author: "ProwlrBot Team"
description: "ProwlrBot v2.0 introduces multi-provider smart routing, Docker Swarm orchestration, and 12 new skills for autonomous AI agents."
tags: ["release", "prowlrbot", "ai-agent", "open-source"]
---
```

### Structure Template

```markdown
# [Title]

[Opening hook — 1-2 sentences that capture attention and state the key news]

## What's New

[Overview paragraph]

### [Feature/Section 1]

[Explanation with code example if applicable]

### [Feature/Section 2]

[Explanation with code example if applicable]

## Getting Started

[Quick start instructions]

## What's Next

[Roadmap teaser — 1-2 upcoming features]

## Get Involved

[Links to GitHub, Discord, contributing guide]
```
