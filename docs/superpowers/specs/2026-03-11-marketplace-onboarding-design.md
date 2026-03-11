# ProwlrBot Marketplace & Onboarding Design Spec

**Date**: 2026-03-11
**Status**: Approved
**Scope**: Marketplace v2, persona onboarding, 52 listings, workflow engine, repo strategy

---

## 1. Philosophy

ProwlrBot is not an AI chatbot. It is a crew of autonomous agents that handle the things people don't want to do — on autopilot. The marketplace, onboarding, and every touchpoint must reflect this.

**Core principle: No limits on capabilities.** Every skill, agent, and workflow is accessible to every user regardless of tier. Premium tiers unlock premium *content* (business templates, enterprise workflows) and *convenience* (more credits, priority support, paid publishing).

---

## 2. Tier Model (Revised)

| | Free | Starter ($5/mo) | Pro ($15/mo) | Team ($29/mo) |
|---|---|---|---|---|
| Agents | Unlimited | Unlimited | Unlimited | Unlimited |
| Skills | All community | All community | All + premium | All + enterprise |
| Active Workflows | 5 | 25 | Unlimited | Unlimited |
| Marketplace Publish | Free items only | Free items only | Paid items | Paid + analytics |
| Credits/month | 100 | 500 | 2,000 | 10,000 |
| Support | Community | Email | Priority | Dedicated |
| Custom Branding | No | No | Yes | Yes + white-label |

---

## 3. Marketplace Listing Schema v2

### New Fields (added to MarketplaceListing)

```python
difficulty: str              # "beginner" | "intermediate" | "advanced"
setup_time_minutes: int      # estimated setup time
persona_tags: list[str]      # ["parent", "business", "student", "creator", "freelancer", "developer", "everyone"]
before_after: dict           # {"before": str, "after": str, "time_saved": str}
skill_scan: dict             # {"automation": int, "ease": int, "privacy": int, "reliability": int, "personalization": int}
works_with: list[str]        # ["gmail", "google-cal", "outlook", "slack", ...]
demo_url: str                # link to interactive demo or preview
setup_steps: list[dict]      # [{"question": str, "options": list, "default": str}, ...]
user_stories: list[dict]     # [{"quote": str, "name": str, "role": str}, ...]
hero_animation: str          # animation type: "sort", "write", "scan", "monitor", "pulse"
```

### Skill Scan Dimensions

Every listing is rated 1-10 across 5 dimensions:

1. **Automation Power** — How much does it automate? (10 = fully autonomous)
2. **Ease of Setup** — How easy to get running? (10 = one click)
3. **Privacy Score** — How private is your data? (10 = everything local)
4. **Reliability** — How consistently does it work? (10 = never fails)
5. **Personalization** — How customizable is it? (10 = fully adaptive)

---

## 4. Listing Card Design

Every marketplace listing card displays:

- Title + version badge
- Difficulty badge (green/yellow/red) + setup time + pricing
- One-line description
- Skill Scan bar chart (5 dimensions)
- Overall star rating + install count
- Before/After with time-saved metric
- Top user story quote (name + role)
- "Works With" integration badges
- Tags + author + verified badge
- Three CTAs: Watch Demo | Install Now | See Steps

---

## 5. Persona-Based Onboarding

### First Visit Flow (Website)

1. Prowlr mascot greeting animation (particles materializing into cat, eyes glow cyan)
2. Three-question quiz:
   - "What's your day like?" → 7 persona options
   - "What eats your time?" → 6 pain-point options
   - "How technical are you?" → 3 comfort levels
3. Personalized dashboard: 5-8 curated listings based on answers
4. Background: "Agents at Work" animation (mini agents sorting, writing, scanning, monitoring)

### Persona Paths

| Persona | Entry Question | Top 3 Recommended |
|---|---|---|
| Parent | "What eats your time at home?" | Morning Briefing, Homework Helper, Meal Planner |
| Business | "What slows your business down?" | Invoice Chaser, Meeting Summarizer, Review Responder |
| Student | "What stresses you about school?" | Study Planner, Flashcard Generator, Deadline Tracker |
| Creator | "What keeps you from creating?" | Content Repurposer, Trend Scout, Comment Manager |
| Freelancer | "What admin do you dread?" | Time Tracker, Client Follow-Up, Contract Reviewer |
| Developer | "What breaks your flow?" | Code Reviewer, Deploy Guardian, API Monitor |
| Explorer | "Just browsing?" | Daily Digest, Email Declutterer, Smart Reminder |

### Interactive Setup (Chat-Style)

Every listing's setup is a guided conversation, not a config file:

```
Agent: "Let's set up [Skill Name]! [First question]"
       [Option A]  [Option B]  [Option C]
User clicks option.
Agent: "[Next question]"
...
Agent: "Done! Here's a preview of what you'll get..."
       [Preview card]
       [Looks great!]  [Customize more]
```

Setup steps are defined in `setup.json` per listing.

---

## 6. The 52 Listings Catalog

### For Parents & Families (7)

| # | Name | Type | Difficulty | Setup | Description |
|---|---|---|---|---|---|
| 1 | Morning Briefing | Skill | beginner | 2 min | Summarizes email + calendar + weather + school alerts |
| 2 | Homework Helper | Agent | beginner | 3 min | Walks kids through problems step-by-step without giving answers |
| 3 | Meal Planner | Workflow | beginner | 5 min | Weekly meal plans from budget + dietary needs |
| 4 | Birthday Never-Forgetter | Skill | beginner | 2 min | Tracks family birthdays, auto-suggests gifts, sends reminders |
| 5 | Family Budget Tracker | Agent | intermediate | 10 min | Monitors spending, flags unusual charges, weekly summary |
| 6 | School Pickup Coordinator | Workflow | intermediate | 10 min | Coordinates carpool schedules, handles changes |
| 7 | Bedtime Story Generator | Skill | beginner | 1 min | Personalized stories featuring your kid's name and interests |

### For Small Business (7)

| # | Name | Type | Difficulty | Setup | Description |
|---|---|---|---|---|---|
| 8 | Invoice Chaser | Agent | beginner | 5 min | Tracks unpaid invoices, sends polite follow-ups |
| 9 | Customer Email Responder | Agent | intermediate | 10 min | Drafts replies to routine customer emails |
| 10 | Social Media Poster | Workflow | intermediate | 8 min | Repurposes content across Twitter, LinkedIn, Instagram |
| 11 | Competitor Price Watcher | Skill | intermediate | 10 min | Monitors competitor websites for price changes |
| 12 | Meeting Summarizer | Skill | beginner | 3 min | Turns meeting notes into action items |
| 13 | Inventory Alert | Agent | intermediate | 15 min | Watches stock levels, alerts when reordering needed |
| 14 | Review Responder | Skill | beginner | 3 min | Drafts professional responses to Google/Yelp reviews |

### For Freelancers & Gig Workers (6)

| # | Name | Type | Difficulty | Setup | Description |
|---|---|---|---|---|---|
| 15 | Time Tracker | Skill | beginner | 5 min | Auto-logs hours from calendar + app usage |
| 16 | Proposal Writer | Agent | intermediate | 8 min | Generates client proposals from a brief conversation |
| 17 | Contract Reviewer | Skill | beginner | 2 min | Scans contracts for red flags, explains clauses |
| 18 | Client Follow-Up | Workflow | beginner | 5 min | Schedules and sends follow-up emails on cadence |
| 19 | Tax Prep Assistant | Agent | intermediate | 15 min | Categorizes expenses, flags deductions |
| 20 | Portfolio Updater | Skill | intermediate | 10 min | Generates case studies from completed projects |

### For Students (6)

| # | Name | Type | Difficulty | Setup | Description |
|---|---|---|---|---|---|
| 21 | Study Planner | Agent | beginner | 3 min | Builds study schedules from syllabus + exam dates |
| 22 | Research Assistant | Agent | beginner | 5 min | Finds papers, summarizes them, builds bibliographies |
| 23 | Essay Feedback | Skill | beginner | 2 min | Reviews essays for structure, clarity, citations |
| 24 | Flashcard Generator | Skill | beginner | 2 min | Turns lecture notes into spaced-repetition flashcards |
| 25 | Deadline Tracker | Workflow | beginner | 3 min | Aggregates deadlines, sends daily priority list |
| 26 | Math Tutor | Agent | beginner | 1 min | Step-by-step math walkthrough with hints, not answers |

### For Content Creators (6)

| # | Name | Type | Difficulty | Setup | Description |
|---|---|---|---|---|---|
| 27 | Content Repurposer | Workflow | intermediate | 10 min | One piece → Twitter thread + LinkedIn + Instagram + newsletter |
| 28 | Thumbnail Analyzer | Skill | beginner | 2 min | Scores YouTube thumbnails for click-through potential |
| 29 | Comment Manager | Agent | intermediate | 8 min | Monitors comments, drafts replies, flags trolls |
| 30 | Sponsorship Pitch | Skill | intermediate | 10 min | Generates media kits and sponsorship proposals |
| 31 | Trend Scout | Agent | intermediate | 5 min | Monitors trending topics in your niche daily |
| 32 | Video Script Writer | Agent | intermediate | 8 min | Outlines video scripts from topic + target length |

### For Entrepreneurs (6)

| # | Name | Type | Difficulty | Setup | Description |
|---|---|---|---|---|---|
| 33 | Market Research Agent | Agent | intermediate | 15 min | Competitors, market size, trends — investor-ready report |
| 34 | Pitch Deck Builder | Workflow | intermediate | 10 min | Generates pitch deck from business description |
| 35 | Grant Finder | Agent | advanced | 20 min | Searches grant databases, matches eligibility |
| 36 | Financial Model Builder | Agent | advanced | 20 min | Revenue projections, burn rate, runway calculator |
| 37 | Hiring Screener | Workflow | intermediate | 10 min | Screens resumes, ranks candidates, suggests questions |
| 38 | Legal Doc Generator | Skill | intermediate | 5 min | NDAs, contractor agreements, terms of service |

### For Developers (6)

| # | Name | Type | Difficulty | Setup | Description |
|---|---|---|---|---|---|
| 39 | Code Reviewer | Agent | intermediate | 10 min | Reviews PRs for bugs, security, style |
| 40 | Dependency Auditor | Skill | beginner | 2 min | Scans for vulnerabilities + license issues |
| 41 | API Monitor | Agent | intermediate | 10 min | Watches endpoints for downtime, latency, schema changes |
| 42 | Deploy Guardian | Workflow | intermediate | 15 min | Pre-deploy checklist: tests, secrets, changelog |
| 43 | Incident Responder | Agent | advanced | 20 min | Auto-triages alerts, checks logs, drafts postmortem |
| 44 | Doc Generator | Skill | intermediate | 10 min | API docs from code comments + type annotations |

### For Everyone (8)

| # | Name | Type | Difficulty | Setup | Description |
|---|---|---|---|---|---|
| 45 | Daily Digest | Workflow | beginner | 2 min | Morning summary: email, calendar, news, weather |
| 46 | Smart Reminder | Skill | beginner | 1 min | Context-aware reminders |
| 47 | Email Declutterer | Skill | beginner | 3 min | Unsubscribes junk, sorts important, drafts replies |
| 48 | Travel Planner | Agent | intermediate | 10 min | Flights, hotels, itinerary, packing list, budget |
| 49 | Health Check-In | Skill | beginner | 1 min | Daily wellness: water, meds, exercise, mood |
| 50 | News Filter | Skill | beginner | 2 min | Only news you care about, no doom-scrolling |
| 51 | Language Practice | Agent | beginner | 1 min | Daily conversation practice, adapts to your level |
| 52 | Grocery List Builder | Skill | beginner | 2 min | Lists from meal plans + pantry inventory |

---

## 7. Workflow Definition Format

```yaml
# workflow.prowlr.yaml
name: Morning Briefing
version: "1.0.0"
description: "Your day in 30 seconds"
trigger:
  type: cron
  schedule: "0 7 * * *"
  timezone: "user.timezone"
config:
  email_provider: "{{user.email_provider}}"
  news_topics: "{{user.interests}}"
steps:
  - id: fetch_email
    type: agent_query
    prompt: "Summarize unread emails from the last 12 hours. Highlight urgent ones."
    tools: [himalaya]
  - id: fetch_calendar
    type: agent_query
    prompt: "List today's calendar events with times."
    tools: [browser_use]
  - id: fetch_news
    type: agent_query
    prompt: "Get top 3 news stories in: {{config.news_topics}}"
    tools: [browser_use]
  - id: compile
    type: agent_query
    prompt: "Combine these into a morning briefing. Be concise, use emoji headers."
    inputs:
      email_summary: "{{fetch_email.output}}"
      calendar: "{{fetch_calendar.output}}"
      news: "{{fetch_news.output}}"
  - id: deliver
    type: channel_send
    channel: "{{user.preferred_channel}}"
    message: "{{compile.output}}"
```

### WorkflowSpec Model

```python
class WorkflowStep(BaseModel):
    id: str
    type: str          # "agent_query" | "channel_send" | "conditional" | "parallel_group"
    prompt: str = ""
    tools: list[str] = []
    inputs: dict = {}
    depends_on: list[str] = []
    condition: str = ""
    on_error: str = "skip"  # "skip" | "retry" | "abort" | "fallback"
    timeout_seconds: int = 120

class WorkflowTrigger(BaseModel):
    type: str           # "cron" | "webhook" | "event" | "manual"
    schedule: str = ""
    timezone: str = "UTC"
    webhook_path: str = ""
    event_type: str = ""

class WorkflowSpec(BaseModel):
    name: str
    version: str = "1.0.0"
    description: str = ""
    trigger: WorkflowTrigger
    config: dict = {}
    steps: list[WorkflowStep]
```

---

## 8. Manifest Format (prowlr-marketplace)

Each listing in the marketplace repo follows this structure:

```
listing-name/
├── manifest.json          # metadata, pricing, skill scan, before/after, user stories
├── SKILL.md               # full documentation + usage guide
├── setup.json             # interactive setup flow (questions + options)
├── workflow.prowlr.yaml   # (workflows only) step definitions
├── scripts/               # implementation scripts
│   ├── main.py
│   └── helpers/
├── references/            # guides, docs
├── demo/                  # preview data, screenshots
│   ├── preview.json       # sample output data
│   └── screenshot.png
└── tests/                 # validation tests
    └── test_manifest.py
```

### manifest.json Schema

```json
{
  "id": "morning-briefing",
  "title": "Morning Briefing",
  "description": "Summarizes your email, calendar, weather, and news into a 30-second morning snapshot",
  "version": "1.0.0",
  "author": {
    "id": "prowlrbot-team",
    "name": "ProwlrBot Team",
    "verified": true
  },
  "category": "skills",
  "difficulty": "beginner",
  "setup_time_minutes": 2,
  "pricing_model": "free",
  "price": 0.0,
  "persona_tags": ["parent", "business", "freelancer", "everyone"],
  "tags": ["email", "daily", "productivity", "beginner"],
  "skill_scan": {
    "automation": 8,
    "ease": 10,
    "privacy": 8,
    "reliability": 9,
    "personalization": 7
  },
  "before_after": {
    "before": "45 minutes sorting email every morning",
    "after": "30-second glance, done",
    "time_saved": "~6 hours/week"
  },
  "works_with": ["gmail", "outlook", "yahoo", "google-calendar", "ical", "rss"],
  "user_stories": [
    {
      "quote": "I haven't opened my email app in a month. This changed my mornings.",
      "name": "Sarah K.",
      "role": "Working mom"
    },
    {
      "quote": "Set it up for my whole team. Game changer.",
      "name": "Mike D.",
      "role": "Startup founder"
    }
  ],
  "hero_animation": "sort",
  "demo_url": "/marketplace/morning-briefing/demo"
}
```

---

## 9. Repo Strategy

| Repo | Identity | Audience | Content |
|---|---|---|---|
| **prowlrbot** | The product | Developers + users | Core platform — don't touch |
| **prowlr-docs** | The funnel | Everyone | Persona paths, 3-step onboarding, video demos |
| **prowlr-marketplace** | The store | Everyone | 52+ listings with manifests, setup flows, scripts |
| **roar-protocol** | The spec | Builders | Protocol spec, SDK, compliance tests, RFCs |
| **agentverse** | The hype | Community | Dormant until 1K installs + 50 contributors + revenue |

---

## 10. Website Enhancements

### New Pages

1. **Marketplace** (`/marketplace`) — Browse all listings with persona filters, Skill Scan cards, search
2. **Listing Detail** (`/marketplace/:id`) — Full listing with setup flow, demo, reviews

### Enhanced Components

1. **AgentGreeting** — First-visit mascot greeting + persona quiz
2. **AgentsAtWork** — Background animation of agents working (sort, write, scan, monitor)
3. **SkillScanChart** — 5-dimension bar chart for each listing
4. **SetupWizard** — Chat-style interactive setup flow
5. **BeforeAfterCard** — Before/after comparison with time-saved metric

### Brand Moments

- Prowlr cat materializes from particles on first visit
- Cyan pulse when agents are active ("Always watching. Always ready.")
- Difficulty badges: green (#00E5FF), yellow (#F5A623), red (#FF5252)
- Skill Scan bars use brand cyan with glow effect
- "Agents at Work" animation: mini agents with cyan trails performing tasks

---

## 11. Implementation Priority

1. Marketplace models v2 (backend)
2. Store + API update (backend)
3. 10 highest-impact listing manifests (content)
4. Workflow definition format + engine (backend)
5. Website marketplace page (frontend)
6. Agent greeting + persona quiz (frontend)
7. prowlr-docs funnel restructure (content)
8. Remaining 42 listing manifests (content)

---

## 12. Success Criteria

- Any person, regardless of technical skill, can go from landing page to first working agent in under 3 minutes
- Every listing has a Skill Scan, before/after, user stories, and guided setup
- Zero tier restrictions on agent/skill access
- Marketplace page loads under 2 seconds
- Background animations run at 60fps without jank
- All existing functionality preserved (no breaking changes)
