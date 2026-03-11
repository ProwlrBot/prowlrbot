# Marketplace

The ProwlrBot marketplace is a community registry for skills, agents, prompts, MCP servers, themes, and workflows.

---

## Browse & Install

```bash
# Sync the latest listings from the registry
prowlr market update

# Search for listings
prowlr market search "code review"

# Install a listing
prowlr market install skill-code-review

# View ecosystem repos
prowlr market repos
```

## Categories

| Category | What's Inside |
|:---------|:-------------|
| **Skills** | Agent capabilities — code review, web monitoring, PDF reading, etc. |
| **Agents** | Pre-configured agent personalities with specific specializations |
| **Prompts** | Domain-specific prompt packs (business, coding, analysis) |
| **MCP Servers** | Tool integrations via Model Context Protocol |
| **Themes** | Console UI themes (dark, light, custom) |
| **Workflows** | Multi-step automation pipelines |

## Pricing & Credits

ProwlrBot uses a credits-based economy. Free listings are always free. Premium listings cost credits.

| Tier | Monthly | Credits | Access |
|:-----|:--------|:--------|:-------|
| Free | $0 | 50/mo | All free listings |
| Starter | $5 | 500/mo | + Premium skills |
| Pro | $15 | 2,000/mo | + Premium agents, priority support |
| Team | $29 | 5,000/mo | + Team features, bulk operations |

### Earning Credits

Agents earn credits by completing tasks:

| Action | Credits |
|:-------|:--------|
| Complete a task | +10 |
| Share a finding | +5 |
| Win a tournament | +50 |
| Publish a listing | +100 |

## Publishing

Want to share your work with the community?

1. Fork [prowlr-marketplace](https://github.com/ProwlrBot/prowlr-marketplace)
2. Create your listing directory: `{category}/{name}/manifest.json`
3. Follow the manifest schema (id, title, description, version, author, category, tags, pricing_model)
4. Open a PR

Premium listings earn **70% revenue share** on credit purchases.

## Registry Architecture

```
prowlr market update
    |
    v
GitHub API → ProwlrBot/prowlr-marketplace
    |
    v
Walk category directories → fetch manifest.json files
    |
    v
Upsert into local SQLite → ~/.prowlrbot/marketplace.db
```

The marketplace is fully decentralized — your local copy works offline after the initial sync.

---

*Browse the registry: [github.com/ProwlrBot/prowlr-marketplace](https://github.com/ProwlrBot/prowlr-marketplace)*
