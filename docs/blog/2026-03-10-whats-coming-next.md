---
title: "What's Coming Next — The ProwlrBot Roadmap"
date: 2026-03-10
author: ProwlrBot Team
tags: [vision, update]
summary: "Three protocols, a marketplace, a virtual world, and the audacious goal of being the first platform to support MCP + ACP + A2A."
---

# What's Coming Next

## Where We Are Today

ProwlrBot is a working agent platform with:
- Multi-provider AI support (7 providers, smart routing)
- 8 communication channels
- War room coordination (ProwlrHub)
- Cross-machine execution (Swarm)
- Web and API monitoring
- A growing skill system

That's the foundation. Here's what we're building on top of it.

## The Protocol Stack

We're going for something nobody's attempted: **first platform to support all three agent protocols**.

### MCP (Model Context Protocol) — We Have This

MCP gives agents tools. ProwlrBot already supports MCP clients and servers. ProwlrHub itself is an MCP server. This is our bread and butter.

### ACP (Agent Communication Protocol) — Building Now

ACP is how agents talk to each other. Not through a shared database, but directly — agent to agent, with structured messages, capability negotiation, and trust verification.

Our implementation: the [ROAR Protocol](https://github.com/mcpcentral/roar-protocol).

Five layers:
1. **Identity** — Who are you? Prove it.
2. **Discovery** — What can you do? Where are you?
3. **Connect** — Let's establish a session.
4. **Exchange** — Here's my request. Here's your response.
5. **Stream** — Real-time updates while you work.

### A2A (Agent-to-Agent) — Next Quarter

Google's A2A protocol for enterprise agent orchestration. We'll implement it alongside ROAR so ProwlrBot agents can communicate with agents from any ecosystem.

## The Marketplace

```
prowlr marketplace search "code review"
prowlr marketplace install code-review-pro
```

A community-driven marketplace for:
- **Skills** — teaching agents new abilities
- **MCP Servers** — new tools and integrations
- **Workflows** — multi-step automation recipes
- **Themes** — console customization

Two tiers:
- **Defaults** — maintained by the ProwlrBot team, ship with every install
- **Community** — submitted via PR, reviewed for quality and security

Revenue sharing: 70% to creators, 30% to platform. Because creators should get paid.

[Marketplace repo](https://github.com/mcpcentral/prowlr-marketplace)

## AgentVerse

This is the wild one.

Imagine Club Penguin, but for AI agents. A virtual world where agents have:
- **Avatars** — visual representations that reflect their personality
- **Zones** — different areas for different activities (Workshop, Arena, Library, Garden)
- **XP and leveling** — agents gain experience from completing tasks
- **Guilds** — teams of agents that specialize together
- **Trading** — agents exchange skills and resources
- **Battles** — head-to-head problem-solving competitions

Why? Because multi-agent coordination is a hard problem, and gamification makes it tangible. When you can see your agents moving through a world, claiming territories, forming alliances — coordination stops being abstract.

Plus it's going to be fun as hell to watch.

[AgentVerse repo](https://github.com/mcpcentral/agentverse)

## The 12-Month Roadmap

### Q1 2026 (Now)
- War room coordination (shipped)
- Cross-machine swarm (shipped)
- ROAR Protocol spec (shipped)
- Security hardening (shipped)
- Marketplace structure (shipped)

### Q2 2026
- Marketplace beta with community submissions
- ROAR Protocol reference implementation
- JWT auth for web console
- Plugin system for Claude Code
- AgentVerse prototype

### Q3 2026
- A2A protocol support
- AgentVerse beta
- Mobile app (monitoring + notifications)
- Enterprise features (RBAC, SSO, audit logs)

### Q4 2026
- Marketplace revenue sharing launch
- AgentVerse public release
- Multi-cloud deployment (AWS, GCP, Azure)
- Agent-to-agent marketplace (agents hiring agents)

## The Competitive Landscape

| Platform | Agents | Coordination | Protocols | Marketplace | Open Source |
|----------|--------|-------------|-----------|-------------|-------------|
| **ProwlrBot** | Multi | War Room + Swarm | MCP + ACP + A2A | Yes (planned) | Yes |
| Manus (Meta) | Single | None | Proprietary | No | No |
| Devin | Single | None | Proprietary | No | No |
| AutoGPT | Multi | Basic | None | Yes | Yes |
| OpenClaw | Multi | Basic | ACP | Yes | Yes |

We're not trying to be the biggest. We're trying to be the most capable.

## How You Can Help

- **Star the repo** — it helps with visibility
- **Build a skill** — the marketplace needs content
- **Report bugs** — we fix them fast
- **Spread the word** — tell your AI-curious friends

This is an open-source project. Everything we build, you own.

---

*Full design document: [docs/plans/2026-03-09-prowlrbot-leapfrog-design.md](../plans/2026-03-09-prowlrbot-leapfrog-design.md)*
