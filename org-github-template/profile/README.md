# ProwlrBot

**Always watching. Always ready.**

We're building the open-source autonomous AI agent platform. One platform. Every channel. Every provider. Zero vendor lock-in.

## What is ProwlrBot?

ProwlrBot is a self-hosted AI agent platform that connects to **8 communication channels** (Discord, Telegram, DingTalk, Feishu, QQ, iMessage, Console), routes across **7 AI providers** (OpenAI, Anthropic, Groq, Z.ai, Ollama, llama.cpp, MLX), and coordinates multiple agents in real-time through our **War Room** system.

**76% of enterprise AI agent deployments fail.** We're building the platform that doesn't.

## Why ProwlrBot?

| Feature | ProwlrBot | Others |
|---------|-----------|--------|
| Open Source (MIT) | Yes | Manus: No, Devin: No, Cursor: No |
| Self-Hosted | Yes | Most require cloud |
| Multi-Channel (8) | Yes | Most: 1-2 channels |
| Multi-Agent War Room | Yes | Most: single agent |
| Web Monitoring | Built-in | Separate tool needed |
| Provider Agnostic (7) | Yes | Most: 1-2 providers |
| Graduated Autonomy | Yes | Most: all-or-nothing |
| MCP + A2A Protocols | Yes | Partial at best |

## Get Started

```bash
pip install prowlrbot
prowlr init --defaults
prowlr app
```

Open `http://localhost:8088` and start chatting with your agent.

## Repositories

| Repo | Description |
|------|-------------|
| [prowlrbot](https://github.com/ProwlrBot/prowlrbot) | Core agent platform |
| [roar-protocol](https://github.com/ProwlrBot/roar-protocol) | ROAR protocol specification |
| [prowlr-marketplace](https://github.com/ProwlrBot/prowlr-marketplace) | Community marketplace — skills, agents, prompts, MCP servers, themes, workflows |
| [agentverse](https://github.com/ProwlrBot/agentverse) | Virtual agent world — zones, XP, guilds, tournaments |
| [prowlr-docs](https://github.com/ProwlrBot/prowlr-docs) | Official documentation (en + zh) |

## Contributing

We're building something new and we want you to be part of it.

- Look for [`good first issue`](https://github.com/prowlrbot/prowlrbot/labels/good%20first%20issue) labels
- Read our [Contributing Guide](https://github.com/prowlrbot/prowlrbot/blob/main/CONTRIBUTING.md)
- Join [GitHub Discussions](https://github.com/prowlrbot/prowlrbot/discussions)

## Links

- [Documentation](https://prowlrbot.github.io/docs)
- [Security Policy](https://github.com/prowlrbot/prowlrbot/blob/main/SECURITY.md)
