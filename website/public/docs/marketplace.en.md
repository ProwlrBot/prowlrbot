# Marketplace

Find agents, skills, and workflows that solve real problems — then install them in one command.

---

## Browse by who you are

The Marketplace organizes everything by the kind of person you are, not just by category:

| Who you are | What you'll find |
|:------------|:-----------------|
| **Parents** | Morning briefings, homework helpers, meal planners, family reminders |
| **Business owners** | Competitor monitoring, invoice tracking, client follow-ups, KPI dashboards |
| **Students** | Study planners, homework guides, deadline trackers, research assistants |
| **Creators** | Content schedulers, analytics agents, audience growth tools |
| **Freelancers** | Invoice chasers, client CRM, site monitoring, time tracking |
| **Developers** | Site monitors, MCP integrations, CI/CD agents, custom workflows |

→ **[Open the Marketplace](/marketplace)** to browse with filters, search, and skill scores.

---

## Install from the CLI

```bash
# Update your local registry
prowlr market update

# Search for something specific
prowlr market search "morning briefing"

# Install an agent
prowlr market install morning-briefing

# See what you've installed
prowlr market list
```

---

## What's in a listing?

Every listing includes:

- **Skill Scan** — 5-dimension rating: automation, ease, privacy, reliability, personalization
- **Before / After** — Concrete proof of what changes (e.g., "45 min sorting email → 30-second glance")
- **Time saved** — How much time you get back per week
- **Difficulty** — Beginner, intermediate, or advanced
- **Setup steps** — Guided walkthrough to get it running
- **Works with** — Integrations (Gmail, Slack, Google Calendar, etc.)
- **User stories** — Real quotes from people using it

---

## Categories

| Category | What's inside |
|:---------|:-------------|
| **Skills** | Single capabilities — monitoring, file handling, search, analysis |
| **Agents** | Pre-configured personalities with specialized knowledge |
| **Workflows** | Multi-step automation pipelines (trigger → action → action) |
| **Prompts** | Domain-specific prompt packs for business, coding, analysis |
| **MCP Servers** | Tool integrations via Model Context Protocol |
| **Themes** | Console UI customizations |

---

## Publishing your own

Share what you've built with the community:

1. Create a directory with `manifest.json` and `SKILL.md`
2. Follow the [manifest schema](https://github.com/ProwlrBot/prowlr-marketplace)
3. Open a pull request

Premium listings earn **70% revenue share** on credit purchases. Free listings are always welcome.

---

## Credits

ProwlrBot uses credits for premium content. Free listings are always free.

| Tier | Price | Credits | What you get |
|:-----|:------|:--------|:-------------|
| Free | $0 | 50/mo | All free listings, unlimited agents |
| Starter | $5 | 500/mo | Premium skills, custom branding |
| Pro | $15 | 2,000/mo | Premium agents, priority support |
| Team | $29 | 5,000/mo | Team features, bulk operations |

> **No limits on agents or teams** — every tier gets unlimited agents. Credits only apply to premium marketplace content.

### Earn credits

| Action | Credits |
|:-------|:--------|
| Complete a task | +10 |
| Share a finding | +5 |
| Publish a listing | +100 |
| Community contribution | +25 |
