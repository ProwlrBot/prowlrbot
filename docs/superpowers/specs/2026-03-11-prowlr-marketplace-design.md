# Prowlr Marketplace Redesign — Design Specification

**Date:** 2026-03-11
**Status:** Review Complete
**Approach:** B — Redesign & Curate

## Overview

Redesign the Prowlr Marketplace from a basic card grid into a curated, trust-tiered marketplace with editorial curation, role-based bundles, a Stripe tip jar, and ~118 verified listings across 7 categories. Inspired by Block's Goose Skills Marketplace (curated bundles, SKILL.md-as-contract), SkillsMP (trust signals, SDLC-phase discovery), and premium app store aesthetics.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trust model | Two tiers: Official + Verified | No unverified content at launch. Every listing is reviewed. Community tier deferred. |
| UI vibe | Hybrid dev store + premium polish | Data-rich (downloads, ratings, versions, license) with editorial curation (bundles, hero, picks) |
| Content source | Port from MIT/CC0 open-source repos | ~118 listings from builtins + buildwithclaude + claude-code-skills + compound-engineering + awesome-chatgpt-prompts |
| Payment model | Free everything + gamification credits + Stripe tip jar | Zero friction to install. Real money only flows through optional tips to authors. |
| Categories | 7 (added specs) | skills, agents, prompts, mcp-servers, themes, workflows, specs |
| Delivery model | GitHub-backed for Official/Verified | Listings fetched from `prowlr-marketplace` repo. No bundle uploads (no Community tier). |
| Install mechanism | Real file delivery | Connect marketplace install to `skills_hub.py` — actually deliver skill files to `~/.prowlrbot/customized_skills/` |

## 1. Trust Tier System

### Two Tiers

| Tier | Badge | Color | Source | Verification |
|------|-------|-------|--------|-------------|
| **Official** | Gold shield with star | `#facc15` | ProwlrBot team maintains in `prowlr-marketplace` repo | Team vouches for it |
| **Verified** | Blue checkmark | `#60a5fa` | Community author, code-reviewed and license-checked | Manual review, approved by maintainer |

### Data Model Changes

Add to `MarketplaceListing`:

```python
# Trust & identity
trust_tier: str          # "official" | "verified" (new enum)
author_name: str         # Display name (e.g., "ProwlrBot", "alireza")
author_url: str          # GitHub profile URL
author_avatar_url: str   # Avatar for cards and detail page
source_repo: str         # GitHub URL for transparency
license: str             # SPDX identifier (MIT, Apache-2.0, CC0-1.0)

# Content
changelog: str           # Markdown changelog
compatibility: str       # ProwlrBot version range (e.g., ">=1.0.0")

# Organization — computed, not stored
# bundle membership: queried via bundles table at read time (not denormalized)
# install_command: computed as f"prowlr market install {id}" in API response (not stored)
# tip_total: computed via existing get_tip_total() in detail endpoint (not cached on listing)
```

New enum value: Add `specs` to `MarketplaceCategory`.

New enum: `TrustTier` with values `official`, `verified`.

### Migration

Add new columns to existing `listings` table via `_migrate_v3()` in `store.py`. Same idempotent pattern as v1→v2 migration. Default `trust_tier` to `"verified"` for existing rows.

**Store methods requiring update for v3 fields:**
- `publish_listing()` — add new columns to INSERT statement
- `_row_to_listing()` — map new columns to model fields
- `update_listing()` — add new field names to `allowed` set

## 2. Curated Bundles

Inspired by Goose's role-based skill packs. A bundle is a pre-packaged set of related listings that can be installed with one click.

### Bundle Model

```python
class Bundle(BaseModel):
    id: str                    # e.g., "security-starter"
    name: str                  # "Security Starter"
    description: str           # "OWASP audit, JWT review, dependency scan"
    emoji: str                 # "🛡️"
    color: str                 # Gradient accent hex (e.g., "#00e5ff")
    listing_ids: list[str]     # Ordered list of listings in the bundle
    install_count: int = 0
    created_at: str
```

### Storage

New `bundles` table in `MarketplaceStore`:

```sql
CREATE TABLE IF NOT EXISTS bundles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    emoji TEXT DEFAULT '',
    color TEXT DEFAULT '#00e5ff',
    listing_ids TEXT DEFAULT '[]',  -- JSON array
    install_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### Initial Bundles (4 at launch)

| Bundle | Emoji | Skills | Description |
|--------|-------|--------|-------------|
| Security Starter | 🛡️ | security-auditor, api-security-audit, dependency-scan, jwt-review, owasp-check | OWASP audit, JWT review, dependency scan |
| Full-Stack Dev | 🚀 | frontend-design, backend-architect, database-designer, test-automator, ci-cd-builder, deployment-engineer, code-reviewer, api-documenter | API design, frontend, testing, CI/CD, deploy |
| Data & Analytics | 📊 | sql-expert, data-scientist, rag-architect, data-engineer, ml-engineer, visualization | SQL, BigQuery, visualization, RAG pipeline |
| Document Pro | 📝 | pdf, docx, pptx, xlsx | PDF, DOCX, PPTX, XLSX processing suite |

### API Endpoints

- `GET /marketplace/bundles` — list all bundles with listing counts
- `GET /marketplace/bundles/{id}` — bundle detail with full listing objects
- `POST /marketplace/bundles/{id}/install` — install all listings in bundle. Continues on individual failures. Response: `{installed: [slugs], failed: [{slug, error}], total: N}`

## 3. Content Strategy

### Sources (all MIT, Apache-2.0, or CC0 licensed)

| Source | License | Items to Port | Category |
|--------|---------|---------------|----------|
| ProwlrBot builtins (18 skills) | MIT | 18 → Official | skills |
| buildwithclaude (115 skills) | MIT | ~25 best → Verified | skills |
| claude-code-skills (25 POWERFUL-tier) | MIT | ~10 best → Verified | skills |
| compound-engineering (20 skills, 29 agents) | MIT | ~7 skills, ~15 agents → Verified | skills, agents |
| awesome-chatgpt-prompts (500+) | CC0 | ~20 curated → Verified | prompts |
| modelcontextprotocol/servers | MIT | ~8 reference servers → Verified | mcp-servers |
| ProwlrBot themes.py + Theme Factory | MIT | ~5 themes → Official | themes |
| ProwlrBot superpowers workflows | MIT | ~5 workflows → Verified | workflows |
| ProwlrBot design specs | MIT | ~5 specs → Official | specs |

### Total: ~118 listings

| Category | Official | Verified | Total |
|----------|----------|----------|-------|
| Skills | 18 | 42 | 60 |
| Agents | 0 | 15 | 15 |
| Prompts | 0 | 20 | 20 |
| MCP Servers | 3 | 5 | 8 |
| Themes | 5 | 0 | 5 |
| Workflows | 0 | 5 | 5 |
| Specs | 5 | 0 | 5 |
| **Total** | **31** | **87** | **118** |

### Attribution

Every ported listing includes:
- Original author name in `author_name`
- Link to source repo in `source_repo`
- Original license preserved in `license`
- Credit note in description: "Originally by [author] — adapted for ProwlrBot"

### Content Pipeline

1. Fork/adapt SKILL.md files from source repos
2. Add ProwlrBot-specific metadata (trust_tier, compatibility, tags)
3. Add to `ProwlrBot/prowlr-marketplace` GitHub repo under category directories
4. Registry sync (`prowlr market update`) pulls into local store
5. Manual review before merging to marketplace repo (this IS the verification step)

## 4. Marketplace UI

### Design Philosophy

Hybrid developer tool store + premium polish:
- **Data-rich** like VS Code Extensions: downloads, ratings, version, license, author on every card
- **Editorially curated** like Apple App Store: bundles, featured section, sorted views
- **Transparent** like SkillsMP: trust badges, source links, license visibility

### Page Structure

```
┌─────────────────────────────────────────────────┐
│  🐾 PROWLR MARKETPLACE                         │
│  Skills, agents, and tools — verified and ready │
│  118 listings · All reviewed · Official +       │
│  Verified only                                  │
│  [Search by name, tag, or what you need to do]  │
├─────────────────────────────────────────────────┤
│  [All 118] [Skills 60] [Agents 15] [Prompts 20] │
│  [MCP 8] [Themes 5] [Workflows 5] [Specs 5]    │
│                                    [Grid] [List] │
├─────────────────────────────────────────────────┤
│  Curated Bundles                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────┐ │
│  │🛡️Security│ │🚀FullStk │ │📊Data    │ │📝  │ │
│  │ Starter  │ │  Dev     │ │Analytics │ │Doc │ │
│  │ 5 skills │ │ 8 skills │ │ 6 skills │ │Pro │ │
│  └──────────┘ └──────────┘ └──────────┘ └────┘ │
├─────────────────────────────────────────────────┤
│  All Listings          [Popular|Rated|New|A-Z]  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │🏗️ RAG    │ │📄 PDF    │ │🌊 Ocean  │        │
│  │Architect │ │Processor │ │ Depths   │        │
│  │✓VERIFIED │ │⭐OFFICIAL│ │⭐OFFICIAL│        │
│  │by alireza│ │by Prowlr │ │by Prowlr │        │
│  │⬇1.2K ★4.8│ │⬇5.2K ★4.9│ │⬇890 ★4.6│        │
│  │MIT [Inst]│ │MIT [Inst]│ │  [Apply] │        │
│  └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────┘
```

### Skill Card (Grid View)

Each card shows:
- Emoji icon (from SKILL.md metadata or category default)
- Name + trust badge (OFFICIAL gold / VERIFIED blue)
- Author name + version
- 2-line description
- Tags (up to 3)
- Stats: downloads, rating, license
- Install button (or "Apply" for themes)

### Listing List Item (List View)

Compact row: emoji | name + badge + version | description | stats | install button

### Grid/List Toggle

Persisted in localStorage. Grid default for browsing, list for searching.

### Sorting

- **Popular** (default) — by downloads DESC
- **Top Rated** — by rating DESC (min 1 review)
- **Newest** — by created_at DESC
- **A-Z** — by title ASC

### Search

Debounced (400ms), searches title + description + tags. Category pills filter additively.

## 5. Skill Detail Page

Clicking a listing card navigates to a detail page.

### Header

- Large emoji + name + trust badge
- Author avatar + name (linked) + version + license + "Last updated: X"
- **Install button** (prominent, primary color)
- **CLI command** (copyable): `prowlr market install <slug>`
- **Tip button** ("Buy this creator a coffee" — Stripe)

### Body (Tabbed)

| Tab | Content |
|-----|---------|
| Overview | Full SKILL.md content rendered as markdown. Tags. Compatibility info. "Part of bundle: X" if applicable. |
| Changelog | Version history with dates, rendered from `changelog` field |
| Reviews | Star ratings + text comments from users. "Write a review" form. |
| Source | Link to GitHub repo/directory. License text. |

### Sidebar

- Download count, rating (with star bar), category badge
- Bundle membership (if any)
- Related listings (same category, ranked by shared tag count DESC then downloads DESC, max 4, excluding current)
- Author's other listings (max 4)

### Theme Detail Variation

Themes show a live color palette preview (color swatches) instead of emoji hero. "Apply" button instead of "Install".

## 6. Backend API Changes

### New Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/marketplace/bundles` | List all bundles |
| `GET` | `/marketplace/bundles/{id}` | Bundle detail with listings |
| `POST` | `/marketplace/bundles/{id}/install` | Install all bundle listings |
| `GET` | `/marketplace/listings/{id}/detail` | Full detail (content, changelog, reviews, related) |
| `POST` | `/marketplace/listings/{id}/tip` | Create Stripe checkout session for tip |
| `GET` | `/marketplace/listings/{id}/tip/success` | Stripe success callback, update tip_total |
| `POST` | `/marketplace/webhook/stripe` | Stripe webhook receiver (validates signature, records tip) |

### Fix Existing Bugs

1. **Add `sort` parameter** to `GET /marketplace/listings` — frontend already sends it but backend ignores it. Accepted values: `sort: "popular" | "top_rated" | "newest" | "alpha"`. SQL mapping: `popular` → `ORDER BY downloads DESC`, `top_rated` → `ORDER BY rating DESC` (where ratings_count > 0), `newest` → `ORDER BY created_at DESC`, `alpha` → `ORDER BY title ASC`.
2. **Fix `q` vs `query` parameter mismatch** — frontend sends `q` but backend expects `query`. Fix in backend: accept both `q` and `query` as aliases (check `q` first, fall back to `query`).
3. **Wire install to file delivery** — connect `POST /marketplace/listings/{id}/install` to `SkillService.create_skill()` in `src/prowlrbot/agents/skills_manager.py` and `skills_hub.py` in `src/prowlrbot/agents/skills_hub.py`. Actually download skill files to `~/.prowlrbot/customized_skills/` and auto-enable.
4. **Field name strategy** — backend API returns snake_case. Frontend transforms in a `transformListing()` utility: `title` → `name`, `ratings_count` → `ratingCount`, `trust_tier` → `trustTier`, `author_name` → `authorName`. The existing frontend `author` field maps to backend `author_name` (not `author_id`).
5. **Update `CATEGORY_COLORS`** in `ListingCard.tsx` — replace stale entries (`tools`, `integrations`, `templates`, `channels`, `monitors`) with actual enum values (`skills`, `agents`, `prompts`, `mcp-servers`, `themes`, `workflows`, `specs`).
6. **Add `specs` to `CATEGORY_DIR_MAP`** in `registry.py` — add `"specs": "specs"` to the directory mapping dict.

### Registry Sync Changes

In `registry.py` `sync_registry()`:
- Set `trust_tier` = `"official"` for listings where `author_id` matches ProwlrBot org
- Set `trust_tier` = `"verified"` for all others synced from the repo
- Populate `author_name`, `source_repo`, `license` from manifest metadata

## 7. Frontend Changes

### File Structure

```
console/src/pages/Marketplace/
├── index.tsx                    # Rewrite: hero, pills, bundles, grid/list
├── index.module.less            # Rewrite: dark theme, gradients, cards
├── ListingDetail.tsx            # New: full detail page (tabbed)
├── components/
│   ├── ListingCard.tsx          # Rewrite: trust badge, author, version, license
│   ├── ListingListItem.tsx      # New: compact list view row
│   ├── BundleCard.tsx           # New: gradient card with emoji, 1-click install
│   ├── TrustBadge.tsx           # New: reusable gold/blue badge
│   ├── CategoryPills.tsx        # New: filterable pill bar with counts
│   ├── InstallButton.tsx        # New: install state machine + CLI command copy
│   └── TipButton.tsx            # New: Stripe checkout redirect
```

### Color System

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#00e5ff` | Buttons, active pills, install button |
| Official | `#facc15` | Gold shield badge, official card border |
| Verified | `#60a5fa` | Blue checkmark badge |
| Surface | `rgba(255,255,255,0.025)` | Card background |
| Border | `rgba(255,255,255,0.07)` | Card borders |
| Text primary | `#ffffff` | Titles |
| Text secondary | `#888888` | Descriptions |
| Text muted | `#555555` | Stats, metadata |

### Responsive Breakpoints

- `>1200px`: 3-column grid
- `768-1200px`: 2-column grid
- `<768px`: 1-column grid, bundles stack vertically

### Field Mapping (API → Frontend)

| Backend (snake_case) | Frontend (camelCase) | Notes |
|---------------------|---------------------|-------|
| `title` | `name` | Display name on cards |
| `ratings_count` | `ratingCount` | Review count |
| `trust_tier` | `trustTier` | Badge selection |
| `author_name` | `authorName` | Card attribution (replaces old frontend `author` field) |

Computed fields (added in API response, not stored):
| Computed | Frontend | Notes |
|----------|----------|-------|
| `f"prowlr market install {id}"` | `installCommand` | Copyable CLI command |
| bundle query result | `bundles` | Array of bundle names this listing belongs to |
| `get_tip_total(author_id)` | `tipTotal` | Aggregate tip amount |

## 8. Stripe Tip Jar

### Flow

```
User clicks "Tip" → POST /marketplace/listings/{id}/tip
  → Backend creates Stripe Checkout Session (mode: payment)
  → Returns checkout URL
  → Frontend redirects to Stripe
  → User pays ($2, $5, $10, or custom)
  → Stripe webhook → POST /marketplace/webhook/stripe
  → Backend updates tip_total on listing
  → Backend records TipRecord
```

### Configuration

- Requires `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` in `~/.prowlrbot.secret/envs.json`
- If Stripe is not configured, tip button is hidden (graceful degradation)
- **No ProwlrBot cut** — 100% to author (minus Stripe fees ~2.9% + $0.30)
- Preset amounts: $2, $5, $10 (buttons) + custom amount input (min $1, max $100; 400 error outside range)

### Stripe Integration

- Use `stripe.checkout.Session.create()` with `mode="payment"`
- `success_url`: `/marketplace/listings/{id}?tipped=true`
- `cancel_url`: `/marketplace/listings/{id}`
- Webhook endpoint: `POST /marketplace/webhook/stripe` (validates signature)

### Graceful Degradation

If `STRIPE_SECRET_KEY` is not set:
- `TipButton` component renders nothing
- `POST /tip` returns 503 with message "Tipping not configured"
- No error, no broken UI

## 9. Gamification Credits

### Simplified Model

Keep existing credit system but use it purely for gamification (no real money, no tiers, no premium content gates).

### Earning

| Action | Credits | Description |
|--------|---------|-------------|
| Publish a listing | +100 | Reward content creation |
| Get a review on your listing | +10 | Reward quality (others review you) |
| Get an install | +5 | Reward popularity (one award per unique user_id per listing_id) |
| Get a 5-star rating | +25 | Reward excellence |
| Write a review | +5 | Reward community participation |

### Spending

| Action | Credits | Description |
|--------|---------|-------------|
| Feature your listing for 24h | 200 | Appears in "Featured" section |
| Custom author badge color | 500 | Personalize your profile |

### Display

- Credit balance shown on author profile
- Transaction history available via `prowlr market credits`
- No tiers, no monthly limits, no premium content locks

## 10. CLI Changes

### New/Modified Commands

```bash
# Existing — now actually delivers files
prowlr market install <slug>           # Downloads skill files to ~/.prowlrbot/customized_skills/

# New
prowlr market bundles                  # List available bundles
prowlr market install-bundle <id>      # Install all skills in a bundle
prowlr market detail <slug>            # Show full listing detail (content, changelog, reviews)
prowlr market tip <slug> <amount>      # Open Stripe checkout in browser

# Existing — unchanged
prowlr market search <query>
prowlr market popular
prowlr market categories
prowlr market review <slug> --rating --comment
prowlr market credits
prowlr market update
```

## 11. User Identity

There is no user authentication system. User identity uses a locally-generated anonymous ID stored in `~/.prowlrbot/config.json` (auto-created on first use). This means:
- Credits are local-only and non-transferable
- Reviews are tied to a local ID (not verified identity)
- Tip jar uses Stripe (Stripe handles payer identity)
- A user could game credits by resetting their ID, but since credits are cosmetic-only, this is acceptable for v1

Full auth is deferred to a future phase.

## 12. Out of Scope (Deferred)

- Community tier (unverified listings, bundle uploads, pending review queue)
- Payment for paid listings (pricing_model beyond "free")
- Author verification workflow (manual for now)
- Automated skill testing/validation pipeline
- MCP registry integration (registry.modelcontextprotocol.io)
- Author revenue dashboard
- SDK for skill developers
- Skill compatibility testing
- SDLC-phase discovery (category pills are sufficient for ~118 listings)
- Achievement badges beyond credit balance

## 13. Success Criteria

- [ ] All 118 listings visible and installable in the marketplace
- [ ] Trust badges (Official/Verified) displayed correctly on all cards
- [ ] 4 curated bundles with 1-click install working
- [ ] Grid/List view toggle works and persists
- [ ] Search filters by name, description, tags
- [ ] Category pills filter correctly with counts
- [ ] Skill detail page shows full content, changelog, reviews
- [ ] `prowlr market install <slug>` actually delivers skill files
- [ ] Stripe tip jar works end-to-end (when configured)
- [ ] Gamification credits awarded on publish, install, review
- [ ] Frontend-backend field mismatches resolved
- [ ] All existing tests still pass
- [ ] New tests cover bundles, trust tiers, tip flow, detail endpoint

## References

- [3 Principles for Designing Agent Skills — Block Engineering](https://engineering.block.xyz/blog/3-principles-for-designing-agent-skills)
- [Goose Skills Marketplace](https://block.github.io/goose/skills/)
- [block/agent-skills on GitHub](https://github.com/block/agent-skills)
- [SkillsMP Review 2026](https://smartscope.blog/en/blog/skillsmp-marketplace-guide/)
- [microsoft/multi-agent-marketplace](https://github.com/microsoft/multi-agent-marketplace)
- Visual mockups: `.superpowers/brainstorm/38396-1773270295/`
