# Quick start

Get ProwlrBot running in under 2 minutes. No coding required.

---

## Step 1: Install (30 seconds)

Pick your OS and run one command:

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/prowlrbot/prowlrbot/main/scripts/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/prowlrbot/prowlrbot/main/scripts/install.ps1 | iex
```

Then open a new terminal window.

> 💡 No Python required — the installer handles everything automatically.

---

## Step 2: Set up (30 seconds)

```bash
prowlr init --defaults
```

This creates your config with sensible defaults. You can customize everything later.

> Want to be guided through setup interactively? Run `prowlr init` (without `--defaults`).

---

## Step 3: Start (10 seconds)

```bash
prowlr app
```

That's it. Open **http://127.0.0.1:8088** in your browser to chat with your agent.

---

## What just happened?

You now have a personal AI agent running on your machine. Here's what you can do:

| What | How |
|:-----|:----|
| **Chat with your agent** | Open the [Console](./console) at `http://127.0.0.1:8088` |
| **Add a messaging app** | Connect [Discord, Telegram, or iMessage](./channels) |
| **Install agents** | Browse the [Marketplace](/marketplace) for ready-made agents |
| **Schedule tasks** | Set up [automated check-ins](./heartbeat) |
| **Build your own** | Create [custom skills](./skills) |

---

## Recommended next steps

### For everyone
1. **[Browse the Marketplace](/marketplace)** — Find agents that match your life
2. **[Console](./console)** — Chat with your agent and see it in action
3. **[Connect a channel](./channels)** — Get responses in Discord, Telegram, or iMessage

### For power users
4. **[Skills](./skills)** — Enable and customize agent capabilities
5. **[Heartbeat](./heartbeat)** — Set up daily briefings and scheduled check-ins
6. **[CLI reference](./cli)** — Full command-line power

### For developers
7. **[MCP](./mcp)** — Connect to external tools via Model Context Protocol
8. **[Workflows](./marketplace)** — Build multi-step automation pipelines
9. **[Config](./config)** — Advanced configuration and customization

---

## Other install methods

### pip install

If you prefer managing Python yourself (Python 3.10–3.13):

```bash
pip install prowlr
```

Then follow Steps 2 and 3 above.

### Docker

```bash
docker pull prowlrbot/prowlr:latest
docker run -p 8088:8088 -v prowlr-data:/app/working prowlrbot/prowlr:latest
```

Open **http://127.0.0.1:8088** for the Console. Pass API keys with `-e OPENAI_API_KEY=xxx` or `--env-file .env`.

### Upgrading

Re-run the install command. To uninstall: `prowlr uninstall`.

---

## Troubleshooting

| Problem | Fix |
|:--------|:----|
| `prowlr: command not found` | Open a new terminal, or run `source ~/.zshrc` |
| Port 8088 already in use | `prowlr app --port 8089` |
| No AI responses | Set an API key: `prowlr env set OPENAI_API_KEY sk-...` |
| Want to start over | `prowlr init --force` to reset config |

Still stuck? Check the [FAQ](./faq) or [file a bug](./community).
