---
name: ProwlrDoctor
description: Audit your Claude Code environment for token waste, duplicate plugins, broken hooks, and security issues. Shows token cost per component and fixes everything in one command.
version: 0.1.0
author: ProwlrBot Team
category: skills
install_command: pip install prowlr-doctor
---

# ProwlrDoctor

ProwlrDoctor is a security-aware environment auditor with token cost intelligence. It reads your Claude Code environment — plugins, hooks, MCP servers, CLAUDE.md, memory files — and tells you exactly what each component costs and what's safe to remove.

## Commands

```
prowlr-doctor                          # full audit, interactive TUI
prowlr-doctor --no-tui                 # Rich terminal report only
prowlr-doctor --profile security       # security-focused recommendations
prowlr-doctor --profile minimal        # strip to minimum
prowlr-doctor --json                   # machine-readable output
prowlr-doctor --write-plan             # write fix plan to ~/.claude/doctor-plan.json
prowlr-doctor --diff                   # preview exact settings.json changes
prowlr-doctor --apply                  # apply plan (creates timestamped backup first)

# Via prowlrbot CLI:
prowlr doctor                          # same as prowlr-doctor
prowlr doctor --profile agent-builder
```

## What It Checks

| Auditor | Checks |
|---|---|
| Plugins | Duplicate registries, large agent bundles (50+ agents) |
| Hooks | Broken import paths, multiple PreToolUse, oversized SessionStart injections |
| Agents | Byte-identical agent definitions across plugins |
| MCP servers | Missing binaries, duplicate entries |
| CLAUDE.md | Verbosity thresholds (>2k tokens = medium, >8k = high) |
| Memory | Stale files (>30 days old or >5k tokens) |
| Security | Conflicting security plugins, shell-execution patterns in hooks |

## Example Output

```
  ProwlrDoctor v0.1 ──────────────────────────────────────────
  Profile: developer  ·  Findings: 3  ·  Auto-fixable: 2

  ● CRITICAL   example-skills registry — ~134k tokens wasted/session
               Byte-identical copy of claude-api. Safe to disable.
               Fix: disable example-skills@anthropic-agent-skills

  ◆ HIGH       hookify (old) — broken sys.path
               /home/user/.claude/plugins/cache/hookify.../hook.py
               inserts '/nonexistent/path' — imports fail silently.

  ◆ MEDIUM     CLAUDE.md — ~9k tokens (verbose)
               Review for redundant instructions.

  ──────────────────────────────────────────────────────────────
  Session fixed:     ~7k tokens
  Per-turn (×20):   ~30k tokens
  20-turn estimate: ~37k tokens
  Wasted:          ~134k tokens
  Savings:         ~134k tokens  →  ~$0.40/session saved
```

## Profiles

- **developer** — disables duplicates, keeps most tooling
- **security** — disables more aggressively, condenses verbose files
- **minimal** — strips to bare minimum
- **agent-builder** — preserves agent bundles, removes clutter
- **research** — preserves all knowledge/doc tooling

## TUI Keyboard Shortcuts

| Key | Action |
|---|---|
| `↑↓` | Navigate findings |
| `D` | Approve disable for selected finding |
| `S` | Skip (mark keep) |
| `V` | View exact settings.json diff |
| `A` | Apply all approved actions |
| `P` | Cycle profiles |
| `W` | Write plan to disk |
| `Q` | Quit |

## Integration

ProwlrDoctor writes `~/.claude/doctor-cache.json` after every run. Add to your statusline script to show savings at a glance:

```bash
# In your statusline config:
prowlr-doctor --json > /dev/null 2>&1  # refresh cache
python3 -c "
import json, pathlib
cache = pathlib.Path('~/.claude/doctor-cache.json').expanduser()
if cache.exists():
    d = json.loads(cache.read_text())
    w = d['token_budget']['wasted']
    print(f'◆ {w//1000}k wasted · prowlr-doctor to fix' if w > 0 else '✓ env clean')
"
```
