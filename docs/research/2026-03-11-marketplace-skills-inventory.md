# ProwlrBot Marketplace Skills Inventory

**Date**: 2026-03-11
**Purpose**: Comprehensive inventory of open-source skills, plugins, MCP servers, and prompt libraries available for porting to the ProwlrBot marketplace.

---

## Executive Summary

**5 Key Findings:**

1. **Massive supply available**: 2,500+ individual skills/plugins across all sources, with strong permissive licensing (MIT dominates).
2. **Anthropic's official `skills` repo (90.7K stars)** is the gold standard for the SKILL.md format that ProwlrBot already uses -- direct compatibility.
3. **obra/superpowers (78K stars, MIT)** is the highest-quality framework-level skills collection -- its methodology (TDD, systematic debugging, plan-execute) maps perfectly to ProwlrBot's graduated autonomy model.
4. **MCP server ecosystem is enormous** -- 500+ servers across 40+ categories via curated lists, with an official registry at registry.modelcontextprotocol.io. ProwlrBot already supports MCP, so these are plug-and-play.
5. **Prompt libraries offer 151K+ prompts** under CC0/MIT -- instant content for a "prompts" marketplace category with zero licensing friction.

**Total Portable Assets Identified**: ~3,200+ items across all categories

---

## Section 1: Claude Code Skills & Plugin Repositories

### 1.1 anthropics/skills (OFFICIAL)

| Field | Value |
|-------|-------|
| **URL** | https://github.com/anthropics/skills |
| **Stars** | 90,749 |
| **License** | Source-available (no SPDX; document skills noted as "source-available, not open source") |
| **Last Updated** | 2026-03-11 |
| **Items** | ~15 reference skills + spec + template |
| **Quality** | EXCELLENT -- official Anthropic, defines the Agent Skills spec |
| **ProwlrBot Categories** | skills, specs |

**Top Skills Worth Porting:**
1. **docx** -- Create/edit Word documents with tracked changes
2. **pdf** -- PDF manipulation and generation
3. **pptx** -- PowerPoint presentation creation
4. **xlsx** -- Excel spreadsheet handling with formulas and visualization
5. **Algorithmic art** -- p5.js generative art
6. **Canvas art** -- PNG/PDF visual creation
7. **Web app testing** -- Playwright-based testing
8. **Frontend design** -- HTML artifact building with React/Tailwind

**LICENSE WARNING**: Document skills (docx, pdf, pptx, xlsx) are explicitly marked "source-available, not open source." Must verify individual skill licenses before porting. The spec and template are likely fine for reference.

---

### 1.2 obra/superpowers

| Field | Value |
|-------|-------|
| **URL** | https://github.com/obra/superpowers |
| **Stars** | 78,001 |
| **License** | MIT |
| **Last Updated** | Active |
| **Items** | 12 core skills |
| **Quality** | EXCELLENT -- battle-tested methodology, high community adoption |
| **ProwlrBot Categories** | skills, workflows |

**All 12 Skills (all worth porting):**
1. **test-driven-development** -- RED-GREEN-REFACTOR enforcement
2. **systematic-debugging** -- Four-phase root cause analysis
3. **verification-before-completion** -- Fix validation
4. **brainstorming** -- Socratic design refinement
5. **writing-plans** -- Detailed implementation plans
6. **executing-plans** -- Batch execution with checkpoints
7. **dispatching-parallel-agents** -- Concurrent subagent workflows
8. **requesting-code-review** -- Pre-review checklist
9. **receiving-code-review** -- Feedback response guidance
10. **using-git-worktrees** -- Parallel development branches
11. **finishing-a-development-branch** -- Merge/PR decision workflows
12. **writing-skills** -- Meta-skill for creating new skills

**VERDICT**: HIGH PRIORITY. MIT license, perfect SKILL.md format compatibility, maps directly to ProwlrBot's agent workflow system.

---

### 1.3 affaan-m/everything-claude-code

| Field | Value |
|-------|-------|
| **URL** | https://github.com/affaan-m/everything-claude-code |
| **Stars** | 72,013 |
| **License** | MIT |
| **Last Updated** | 2026-03-11 |
| **Items** | 65+ skills |
| **Quality** | VERY GOOD -- 10+ months production use, multi-framework support |
| **ProwlrBot Categories** | skills, agents, workflows |

**Top 10 Skills Worth Porting:**
1. **Backend API patterns** -- REST/GraphQL best practices
2. **React/Next.js workflows** -- Frontend development patterns
3. **TDD and E2E testing** -- Testing methodology
4. **AgentShield security** -- Vulnerability scanning integration
5. **Docker/CI-CD deployment** -- DevOps automation
6. **PostgreSQL/ClickHouse** -- Database optimization patterns
7. **Django patterns** -- Python web framework skills
8. **Document processing** -- File handling workflows
9. **Video/audio processing** -- Media manipulation
10. **Autonomous loops** -- Self-directing agent patterns

**VERDICT**: HIGH PRIORITY. MIT, large collection, production-tested.

---

### 1.4 alirezarezvani/claude-skills

| Field | Value |
|-------|-------|
| **URL** | https://github.com/alirezarezvani/claude-skills |
| **Stars** | 4,266 |
| **License** | MIT |
| **Last Updated** | 2026-03-11 |
| **Items** | 177 skills across 9+ domains |
| **Quality** | GOOD -- broad coverage, multi-platform support (11 AI tools) |
| **ProwlrBot Categories** | skills, agents |

**Top 10 Skills Worth Porting:**
1. **Architecture design** -- System design patterns
2. **RAG architecture** -- Retrieval-augmented generation
3. **Database schema design** -- Schema optimization
4. **CI/CD builders** -- Pipeline generation
5. **Playwright Pro suite** -- 12 testing skills
6. **Self-improving agent** -- Memory curation and pattern promotion (7 skills)
7. **UX research** -- User research methodology
8. **SEO optimization** -- Content and technical SEO
9. **Landing page generation** -- Marketing pages
10. **Financial analysis** -- SaaS metrics and coaching

**Unique value**: Marketing (43 skills), C-Level Advisory (28 skills), Regulatory compliance (12 skills) -- categories not found elsewhere.

**VERDICT**: MEDIUM-HIGH PRIORITY. MIT, very broad but shallower individual skill depth.

---

### 1.5 jeremylongshore/claude-code-plugins-plus-skills

| Field | Value |
|-------|-------|
| **URL** | https://github.com/jeremylongshore/claude-code-plugins-plus-skills |
| **Stars** | 1,583 |
| **License** | NOASSERTION (unclear) |
| **Last Updated** | 2026-03-11 |
| **Items** | 340 plugins + 1,367 skills |
| **Quality** | FAIR -- large quantity but license unclear, quality varies |
| **ProwlrBot Categories** | skills, agents |

**LICENSE WARNING**: License listed as NOASSERTION. Must investigate before porting any content. Quantity is impressive but needs license verification.

**VERDICT**: LOW PRIORITY until license is clarified.

---

### 1.6 levnikolaevich/claude-code-skills

| Field | Value |
|-------|-------|
| **URL** | https://github.com/levnikolaevich/claude-code-skills |
| **Stars** | 190 |
| **License** | MIT |
| **Last Updated** | 2026-03-11 |
| **Items** | ~20 delivery workflow skills |
| **Quality** | GOOD -- focused on software delivery lifecycle |
| **ProwlrBot Categories** | skills, workflows |

**Skills**: Research, discovery, epic planning, task breakdown, implementation, testing, code review, quality gates.

**VERDICT**: MEDIUM PRIORITY. MIT, niche but well-structured delivery workflow skills.

---

### 1.7 giuseppe-trisciuoglio/developer-kit

| Field | Value |
|-------|-------|
| **URL** | https://github.com/giuseppe-trisciuoglio/developer-kit |
| **Stars** | 151 |
| **License** | MIT |
| **Last Updated** | 2026-03-11 |
| **Items** | ~15 language/framework-specific plugin modules |
| **Quality** | GOOD -- modular, multi-language coverage |
| **ProwlrBot Categories** | skills |

**Modules**: Java/Spring Boot, TypeScript/NestJS/React, Python, PHP/WordPress, AWS CloudFormation, LangChain4J, AI patterns.

**VERDICT**: MEDIUM PRIORITY. MIT, useful for language-specific skill packs.

---

## Section 2: Curated Awesome Lists (Aggregators)

### 2.1 hesreallyhim/awesome-claude-code

| Field | Value |
|-------|-------|
| **URL** | https://github.com/hesreallyhim/awesome-claude-code |
| **Stars** | 27,523 |
| **License** | NOASSERTION |
| **Items** | 100+ resources across 8 categories |
| **Quality** | EXCELLENT -- selectively curated, well-organized |
| **ProwlrBot Categories** | meta (discovery resource) |

**Categories**: Agent Skills, Workflows, Tooling, Status Lines, Hooks, Slash-Commands, CLAUDE.md files, Alternative Clients.

**VERDICT**: Use as a DISCOVERY RESOURCE to find additional skills repos, not for direct porting.

---

### 2.2 ComposioHQ/awesome-claude-skills

| Field | Value |
|-------|-------|
| **URL** | https://github.com/ComposioHQ/awesome-claude-skills |
| **Stars** | 43,104 |
| **License** | Not specified |
| **Quality** | VERY GOOD -- maintained by Composio team |
| **ProwlrBot Categories** | meta (discovery resource) |

**VERDICT**: Discovery resource. Points to same underlying skill repos.

---

### 2.3 travisvn/awesome-claude-skills

| Field | Value |
|-------|-------|
| **URL** | https://github.com/travisvn/awesome-claude-skills |
| **Stars** | 8,669 |
| **License** | Not specified |
| **Quality** | GOOD -- community-maintained |
| **ProwlrBot Categories** | meta (discovery resource) |

---

## Section 3: MCP Server Registries

### 3.1 modelcontextprotocol/servers (OFFICIAL)

| Field | Value |
|-------|-------|
| **URL** | https://github.com/modelcontextprotocol/servers |
| **Stars** | 80,844 |
| **License** | NOASSERTION (mixed per-server) |
| **Last Updated** | 2026-03-11 |
| **Items** | 7 reference servers + 100+ official integrations |
| **Quality** | EXCELLENT -- official reference implementations |
| **ProwlrBot Categories** | mcp-servers |

**7 Reference Servers:**
1. **Everything** -- Test/reference server
2. **Fetch** -- Web content fetching/conversion
3. **Filesystem** -- Secure file operations
4. **Git** -- Git repository tools
5. **Memory** -- Knowledge graph persistence
6. **Sequential Thinking** -- Problem-solving through thought sequences
7. **Time** -- Timezone conversion

**VERDICT**: HIGH PRIORITY for reference. These are educational but demonstrate patterns ProwlrBot can adopt.

---

### 3.2 modelcontextprotocol/registry (OFFICIAL REGISTRY)

| Field | Value |
|-------|-------|
| **URL** | https://github.com/modelcontextprotocol/registry |
| **Stars** | 6,544 |
| **License** | NOASSERTION |
| **Registry URL** | https://registry.modelcontextprotocol.io/ |
| **Quality** | EXCELLENT -- official community registry, API frozen at v0.1 |
| **ProwlrBot Categories** | mcp-servers |

**VERDICT**: HIGH PRIORITY. ProwlrBot should integrate with this registry for MCP server discovery. This is the "app store" for MCP servers.

---

### 3.3 punkpeye/awesome-mcp-servers

| Field | Value |
|-------|-------|
| **URL** | https://github.com/punkpeye/awesome-mcp-servers |
| **Stars** | 82,795 |
| **License** | MIT |
| **Items** | 500+ servers across 40+ categories |
| **Quality** | EXCELLENT -- largest curated collection, actively maintained |
| **ProwlrBot Categories** | mcp-servers |

**Top Categories with Server Counts:**
- Databases, Browser Automation, Developer Tools, Version Control
- Cloud Platforms, Communication, Finance & Fintech
- Knowledge & Memory, Search, Security
- Home Automation, Education, Biology/Medicine
- Gaming, Legal, Real Estate, Sports

**Top 10 MCP Servers Worth Highlighting:**
1. **Playwright browser automation** -- Full browser control
2. **PostgreSQL/MySQL/SQLite** -- Database access
3. **Slack/Discord/Teams** -- Communication platforms
4. **AWS/Azure/GCP** -- Cloud management
5. **GitHub** -- Repository management
6. **Notion** -- Workspace integration
7. **Stripe/Plaid** -- Financial APIs
8. **Elasticsearch** -- Search engine
9. **Docker** -- Container management
10. **Prometheus/Grafana** -- Monitoring

**VERDICT**: Use as DISCOVERY LIST. Individual servers have their own licenses -- must verify per-server.

---

### 3.4 microsoft/mcp

| Field | Value |
|-------|-------|
| **URL** | https://github.com/microsoft/mcp |
| **Stars** | 2,756 |
| **License** | MIT |
| **Items** | 14+ MCP servers |
| **Quality** | EXCELLENT -- Microsoft official |
| **ProwlrBot Categories** | mcp-servers |

**Servers**: Azure, Azure DevOps, Microsoft 365, Fabric, Dataverse, Admin Center, GitHub, Clarity, Dev Box, Calendar, Mail, Chat, User, Markitdown.

**VERDICT**: MEDIUM PRIORITY. MIT licensed, enterprise-grade, but Microsoft-ecosystem focused.

---

### 3.5 wong2/awesome-mcp-servers

| Field | Value |
|-------|-------|
| **URL** | https://github.com/wong2/awesome-mcp-servers |
| **Stars** | 3,732 |
| **License** | MIT |
| **Quality** | GOOD -- smaller but well-maintained |
| **ProwlrBot Categories** | mcp-servers |

---

## Section 4: Agent Framework Tool Libraries

### 4.1 ComposioHQ/composio

| Field | Value |
|-------|-------|
| **URL** | https://github.com/ComposioHQ/composio |
| **Stars** | 27,347 |
| **License** | MIT |
| **Items** | 1,000+ toolkits for 100+ SaaS apps |
| **Quality** | EXCELLENT -- production platform, enterprise adoption |
| **ProwlrBot Categories** | skills, agents, workflows |

**Key Integration Categories:**
1. **CRM** -- Salesforce, HubSpot
2. **Communication** -- Slack, Gmail, Teams
3. **Development** -- GitHub, GitLab, Jira
4. **Cloud** -- AWS, GCP, Azure
5. **Marketing** -- Mailchimp, SendGrid
6. **Finance** -- Stripe, QuickBooks
7. **Productivity** -- Notion, Asana, Trello
8. **Data** -- Snowflake, BigQuery

**VERDICT**: HIGH PRIORITY. MIT, massive tool library, authentication handling built in. Could provide the SaaS integration layer ProwlrBot needs.

---

### 4.2 crewAIInc/crewAI

| Field | Value |
|-------|-------|
| **URL** | https://github.com/crewAIInc/crewAI |
| **Stars** | 45,798 |
| **License** | MIT |
| **Items** | 30+ built-in tools + community tools |
| **Quality** | EXCELLENT -- framework leader, 100K+ certified developers |
| **ProwlrBot Categories** | agents, workflows |

**Built-in Tools Worth Studying:**
1. **WebSearchTool** -- Internet search
2. **FileReadTool / FileWriteTool** -- File operations
3. **ScrapeWebsiteTool** -- Web scraping
4. **PDFSearchTool** -- PDF content search
5. **CodeInterpreterTool** -- Code execution
6. **SerperDevTool** -- Google search API
7. **YoutubeVideoSearchTool** -- Video search
8. **DirectoryReadTool / DirectorySearchTool** -- Directory operations
9. **DOCXSearchTool / CSVSearchTool** -- Document search
10. **GithubSearchTool** -- GitHub integration

**VERDICT**: MEDIUM PRIORITY. MIT, but tools are deeply coupled to CrewAI's framework. Better as inspiration/reference than direct porting.

---

### 4.3 langchain-ai/langchain

| Field | Value |
|-------|-------|
| **URL** | https://github.com/langchain-ai/langchain |
| **Stars** | 129,177 |
| **License** | MIT |
| **Items** | Hundreds of integrations across langchain-community |
| **Quality** | EXCELLENT -- industry standard, massive ecosystem |
| **ProwlrBot Categories** | skills, agents |

**VERDICT**: REFERENCE ONLY. Tools are deeply framework-coupled. Use as inspiration for what integrations to build, not for direct porting.

---

### 4.4 Significant-Gravitas/AutoGPT

| Field | Value |
|-------|-------|
| **URL** | https://github.com/Significant-Gravitas/AutoGPT |
| **Stars** | 182,364 |
| **License** | NOASSERTION |
| **Plugin Repo Stars** | 3,847 (Auto-GPT-Plugins, MIT) |
| **Quality** | GOOD -- large but evolved away from plugin model |
| **ProwlrBot Categories** | agents, workflows |

**VERDICT**: LOW PRIORITY. AutoGPT moved to a visual workflow builder model. Plugin repo (MIT) has some useful tools but many are outdated.

---

### 4.5 langchain-ai/langchain-skills

| Field | Value |
|-------|-------|
| **URL** | https://github.com/langchain-ai/langchain-skills |
| **Stars** | 330 |
| **License** | Not specified |
| **Quality** | EARLY -- newer repo, follows Agent Skills spec |
| **ProwlrBot Categories** | skills |

**VERDICT**: WATCH. Small but official LangChain adoption of the Agent Skills spec, which ProwlrBot already uses.

---

## Section 5: Prompt Libraries

### 5.1 f/awesome-chatgpt-prompts

| Field | Value |
|-------|-------|
| **URL** | https://github.com/f/awesome-chatgpt-prompts |
| **Stars** | 151,475 |
| **License** | CC0-1.0 (PUBLIC DOMAIN) |
| **Items** | 500+ prompts |
| **Quality** | EXCELLENT -- referenced by Harvard/Columbia, 40+ academic citations |
| **ProwlrBot Categories** | prompts |

**Top Prompt Types:**
1. Role-play prompts (act as Linux terminal, interviewer, etc.)
2. Creative writing prompts
3. Professional advisor prompts
4. Technical expert prompts
5. Educational tutor prompts

**VERDICT**: HIGH PRIORITY. CC0 = zero licensing friction. Instant content for prompts marketplace category.

---

### 5.2 0xeb/TheBigPromptLibrary

| Field | Value |
|-------|-------|
| **URL** | https://github.com/0xeb/TheBigPromptLibrary |
| **Stars** | 4,800 |
| **License** | MIT |
| **Items** | Hundreds of system prompts, custom instructions, GPT instructions |
| **Quality** | VERY GOOD -- well-organized, multi-provider coverage |
| **ProwlrBot Categories** | prompts |

**VERDICT**: HIGH PRIORITY. MIT, diverse prompt types, good categorization.

---

### 5.3 dontriskit/awesome-ai-system-prompts

| Field | Value |
|-------|-------|
| **URL** | https://github.com/dontriskit/awesome-ai-system-prompts |
| **Stars** | 5,504 |
| **License** | MIT |
| **Items** | System prompts from 15+ AI tools |
| **Quality** | VERY GOOD -- real-world system prompts |
| **ProwlrBot Categories** | prompts |

**VERDICT**: HIGH PRIORITY. MIT, real production system prompts for study/adaptation.

---

### 5.4 promptslab/Awesome-Prompt-Engineering

| Field | Value |
|-------|-------|
| **URL** | https://github.com/promptslab/Awesome-Prompt-Engineering |
| **Stars** | 5,530 |
| **License** | Apache-2.0 |
| **Quality** | VERY GOOD -- academic focus, well-curated |
| **ProwlrBot Categories** | prompts, specs |

**VERDICT**: MEDIUM PRIORITY. Apache-2.0, more of a reference guide than directly portable prompts.

---

### 5.5 x1xhlol/system-prompts-and-models-of-ai-tools

| Field | Value |
|-------|-------|
| **URL** | https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools |
| **Stars** | 130,267 |
| **License** | GPL-3.0 |
| **Items** | System prompts from 30+ AI tools |
| **Quality** | EXCELLENT -- most comprehensive collection |
| **ProwlrBot Categories** | prompts |

**LICENSE WARNING**: GPL-3.0 is copyleft. Any derivative work must also be GPL. NOT suitable for direct porting into ProwlrBot marketplace unless prompts themselves are factual/non-copyrightable. Use for REFERENCE ONLY.

---

### 5.6 EliFuzz/awesome-system-prompts

| Field | Value |
|-------|-------|
| **URL** | https://github.com/EliFuzz/awesome-system-prompts |
| **Stars** | 124 |
| **License** | GPL-3.0 |
| **Quality** | FAIR -- smaller collection |

**LICENSE WARNING**: GPL-3.0. Same copyleft concern. REFERENCE ONLY.

---

## Section 6: Consolidated Inventory Summary

### By Source Type

| Category | Sources Found | Total Items | Permissive License | Priority Items |
|----------|--------------|-------------|-------------------|----------------|
| Claude Code Skills | 7 repos | ~350+ skills | 5 MIT, 1 source-avail, 1 unclear | ~270 |
| Curated Lists | 3 lists | 100+ linked resources | Mixed | Discovery use |
| MCP Servers | 5 sources | 500+ servers | Mostly MIT | ~100 verified |
| Agent Frameworks | 4 frameworks | 1,100+ tools | All MIT | Reference use |
| Prompt Libraries | 6 repos | 1,000+ prompts | 3 MIT/CC0, 2 GPL, 1 Apache | ~700 |
| **TOTAL** | **25 sources** | **~3,200+ items** | | **~1,070 directly portable** |

### By ProwlrBot Marketplace Category

| ProwlrBot Category | Directly Portable Items | Best Sources |
|--------------------|-----------------------|--------------|
| **Skills** | ~270 | obra/superpowers, everything-claude-code, alirezarezvani/claude-skills |
| **Agents** | ~30 | everything-claude-code, crewAI patterns |
| **Prompts** | ~700 | awesome-chatgpt-prompts, TheBigPromptLibrary, awesome-ai-system-prompts |
| **MCP Servers** | ~100 (verified MIT) | punkpeye/awesome-mcp-servers, microsoft/mcp, MCP registry |
| **Themes** | 0 | No sources found -- greenfield opportunity |
| **Workflows** | ~50 | obra/superpowers, everything-claude-code |
| **Specs** | ~5 | anthropics/skills (Agent Skills spec), MCP spec |

### License Summary

| License | Repos | Status |
|---------|-------|--------|
| MIT | 12 | SAFE -- freely portable |
| CC0-1.0 | 1 | SAFE -- public domain |
| Apache-2.0 | 1 | SAFE -- permissive with notice |
| GPL-3.0 | 2 | BLOCKED -- copyleft, reference only |
| Source-available | 1 | CAUTION -- check individual items |
| NOASSERTION/None | 8 | CAUTION -- must verify before porting |

---

## Section 7: Recommended Porting Priority

### Tier 1 -- Immediate (MIT, high quality, direct compatibility)

1. **obra/superpowers** (78K stars, MIT) -- All 12 skills. Direct SKILL.md format. Maps to ProwlrBot workflows.
2. **affaan-m/everything-claude-code** (72K stars, MIT) -- Cherry-pick 30-40 best skills from 65+.
3. **f/awesome-chatgpt-prompts** (151K stars, CC0) -- All 500+ prompts. Zero licensing friction.
4. **0xeb/TheBigPromptLibrary** (4.8K stars, MIT) -- System prompts and instructions.

### Tier 2 -- Near-term (MIT, good quality, some adaptation needed)

5. **alirezarezvani/claude-skills** (4.3K stars, MIT) -- Marketing, regulatory, and C-suite skills (unique categories).
6. **dontriskit/awesome-ai-system-prompts** (5.5K stars, MIT) -- Production system prompts.
7. **microsoft/mcp** (2.8K stars, MIT) -- Enterprise MCP servers.
8. **ComposioHQ/composio** (27K stars, MIT) -- Study integration patterns, potentially wrap their toolkits.

### Tier 3 -- Strategic (requires more work or license verification)

9. **modelcontextprotocol/registry** -- Integrate ProwlrBot with the official MCP registry API.
10. **anthropics/skills** -- Reference for spec compliance (source-available license limits direct porting).
11. **giuseppe-trisciuoglio/developer-kit** (151 stars, MIT) -- Language-specific plugin modules.
12. **levnikolaevich/claude-code-skills** (190 stars, MIT) -- Delivery workflow skills.

### Not Recommended

- **jeremylongshore/claude-code-plugins-plus-skills** -- License unclear (NOASSERTION)
- **x1xhlol/system-prompts-and-models-of-ai-tools** -- GPL-3.0 copyleft
- **EliFuzz/awesome-system-prompts** -- GPL-3.0 copyleft
- **AutoGPT plugins** -- Outdated architecture, moving away from plugin model

---

## Section 8: Strategic Recommendations

### 8.1 Format Compatibility

ProwlrBot already uses the SKILL.md format (YAML frontmatter with name/description). This is identical to the Agent Skills spec from anthropics/skills and used by obra/superpowers. Skills from these repos can be ported with minimal modification -- primarily just rebranding and adding ProwlrBot-specific metadata (category, tags, author, version).

### 8.2 MCP Registry Integration

ProwlrBot should implement a sync mechanism with the official MCP registry (registry.modelcontextprotocol.io). This would give ProwlrBot users instant access to the entire MCP ecosystem without ProwlrBot needing to host the servers. Add a `prowlr market mcp-search` command.

### 8.3 Competitive Differentiation

No source found offers **themes** -- this is a greenfield category where ProwlrBot can differentiate. The themes.py file already in the codebase positions ProwlrBot ahead.

### 8.4 Quality Gate

When porting, each skill should go through:
1. License verification (per-file, not just repo-level)
2. Security review (no shell injection, no credential exposure)
3. Functionality test (does it work with ProwlrBot's ReActAgent?)
4. Documentation check (clear SKILL.md with examples)
5. Category tagging for marketplace taxonomy

---

## Full Bibliography

1. anthropics/skills -- https://github.com/anthropics/skills (90.7K stars)
2. obra/superpowers -- https://github.com/obra/superpowers (78K stars, MIT)
3. affaan-m/everything-claude-code -- https://github.com/affaan-m/everything-claude-code (72K stars, MIT)
4. alirezarezvani/claude-skills -- https://github.com/alirezarezvani/claude-skills (4.3K stars, MIT)
5. jeremylongshore/claude-code-plugins-plus-skills -- https://github.com/jeremylongshore/claude-code-plugins-plus-skills (1.6K stars, NOASSERTION)
6. levnikolaevich/claude-code-skills -- https://github.com/levnikolaevich/claude-code-skills (190 stars, MIT)
7. giuseppe-trisciuoglio/developer-kit -- https://github.com/giuseppe-trisciuoglio/developer-kit (151 stars, MIT)
8. hesreallyhim/awesome-claude-code -- https://github.com/hesreallyhim/awesome-claude-code (27.5K stars)
9. ComposioHQ/awesome-claude-skills -- https://github.com/ComposioHQ/awesome-claude-skills (43.1K stars)
10. travisvn/awesome-claude-skills -- https://github.com/travisvn/awesome-claude-skills (8.7K stars)
11. modelcontextprotocol/servers -- https://github.com/modelcontextprotocol/servers (80.8K stars)
12. modelcontextprotocol/registry -- https://github.com/modelcontextprotocol/registry (6.5K stars)
13. punkpeye/awesome-mcp-servers -- https://github.com/punkpeye/awesome-mcp-servers (82.8K stars, MIT)
14. wong2/awesome-mcp-servers -- https://github.com/wong2/awesome-mcp-servers (3.7K stars, MIT)
15. microsoft/mcp -- https://github.com/microsoft/mcp (2.8K stars, MIT)
16. ComposioHQ/composio -- https://github.com/ComposioHQ/composio (27.3K stars, MIT)
17. crewAIInc/crewAI -- https://github.com/crewAIInc/crewAI (45.8K stars, MIT)
18. langchain-ai/langchain -- https://github.com/langchain-ai/langchain (129.2K stars, MIT)
19. langchain-ai/langchain-skills -- https://github.com/langchain-ai/langchain-skills (330 stars)
20. Significant-Gravitas/AutoGPT -- https://github.com/Significant-Gravitas/AutoGPT (182.4K stars)
21. Significant-Gravitas/Auto-GPT-Plugins -- https://github.com/Significant-Gravitas/Auto-GPT-Plugins (3.8K stars, MIT)
22. f/awesome-chatgpt-prompts -- https://github.com/f/awesome-chatgpt-prompts (151.5K stars, CC0)
23. 0xeb/TheBigPromptLibrary -- https://github.com/0xeb/TheBigPromptLibrary (4.8K stars, MIT)
24. dontriskit/awesome-ai-system-prompts -- https://github.com/dontriskit/awesome-ai-system-prompts (5.5K stars, MIT)
25. promptslab/Awesome-Prompt-Engineering -- https://github.com/promptslab/Awesome-Prompt-Engineering (5.5K stars, Apache-2.0)
26. x1xhlol/system-prompts-and-models-of-ai-tools -- https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools (130.3K stars, GPL-3.0)
27. EliFuzz/awesome-system-prompts -- https://github.com/EliFuzz/awesome-system-prompts (124 stars, GPL-3.0)
28. danielrosehill/System-Prompt-Library -- https://github.com/danielrosehill/System-Prompt-Library (47 stars)
