# Changelog

All notable changes to ProwlrBot are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Fixed
- Removed all hardcoded colors from War Room, Dashboard, and Analytics — everything now flows through the theme system.
- Unified dashboard and analytics styling so dark mode and custom color themes actually work end-to-end.

### Changed
- Ran Black formatter across 62 previously unformatted Python files.

---

## [0.5.0] — Security hardening, War Room, Analytics, Studio, Memory tiers

### Added
- Dedicated Analytics page with cost and token usage charts (Recharts).
- Grafana-style dashboard with live data wired to all API endpoints.
- Auth UI with login, register, and OAuth flows (GitHub + Google).
- Autonomy slider, credits display, session replay, embedded terminal, and status line in the console.
- `prowlr doctor` CLI command — thin wrapper that shells out to the `prowlr-doctor` tool.
- `MemoryTierManager` wired into `MemoryManager` for automatic hot/warm/cold promotion.
- War Room WebSocket dashboard, learning engine, and 76 security tests covering bridge API and war room engine.

### Fixed
- JWT endpoints exempted from the API token gate; first-user admin setup now works on a fresh install.
- ROAR SDK TypeScript `canonicalize()` aligned with the Python golden fixture.
- War Room console shows a proper error state when the server isn't running.
- Prevented unbounded writes — output caps and auto-cleanup added to the file tool.
- Closed 7 auth/SSRF/shell gaps and fixed 8 test failures left over from the audit sweep.

### Changed
- Memory API router added; CORS bridge config overhauled.
- `prowlr init --defaults` now bypasses the interactive security prompt.

---

## [0.4.0] — ACP, ROAR protocol, marketplace v3, deployment

### Added
- ROAR SDK Phases 1–7: Python/TypeScript unified types, transport, streaming, identity, discovery, and channel adapters.
- ROAR router wired into FastAPI with A2A streaming; EXECUTE/DELEGATE intents flow through `AgentRunner`.
- Fly.io and Cloudflare Pages deployment infrastructure (configs, volume permissions, secrets).
- Marketplace v3: trust tiers, bundle model, Stripe tip jar, gamification credit rules, seed bundles, and CLI commands (`bundles`, `detail`, `install-bundle`).
- Persona-driven marketplace frontend with `TrustBadge`, `CategoryPills`, and `BundleCard` components.
- Provider auto-detection from environment variables on startup.
- `prowlr acp` CLI command with `--debug` flag and clean `KeyboardInterrupt` handling.
- CSS custom-properties theme system with real-time dark mode and color theme switching.
- ProwlrHub War Room: multi-agent coordination via MCP, HTTP bridge for cross-machine setups, interactive setup wizard.

### Fixed
- Stripe webhook records tip after payment confirmation, not before.
- Marketplace sort parameter and `q` alias for query added.
- `TrustTier` field typed as enum instead of bare string.
- 25 files hardened: HMAC signing, replay protection, input validation, shell allowlist.
- 14 Dependabot alerts patched (npm overrides + pip dismissals).

### Changed
- Replaced `@agentscope-ai/chat`, `@agentscope-ai/icons`, and `@agentscope-ai/design` with `@prowlrbot/chat` fork and Ant Design equivalents.
- Removed 9 dead console pages, fixed residual Chinese text, cleaned nav.

---

## [0.3.0] — Initial channels, monitoring, cron, MCP, and rebrand

### Added
- Complete CoPaw → ProwlrBot rebrand: new name, dark theme, teal accents, cybernetic eye logo.
- Monitoring engine with web change detection, content diffing, and multi-channel notifications.
- Docker Swarm support for multi-device agent coordination.
- `wsl_doctor` and `mac_doctor` diagnostic skills.
- Provider detection pipeline with async health checks and smart routing (scored by cost, performance, availability).
- Telegram channel support.
- Heartbeat control panel in the console.
- Memory compaction with token-based message filtering to eliminate context overflow.
- OpenAI and Azure OpenAI as built-in providers; Ollama SDK as optional battery-included dependency.
- CORS support via `PROWLR_CORS_ORIGINS` environment variable.

### Fixed
- Bootstrap persisted envs safely at package init to avoid startup crashes.
- `providers.json` now persisted under the sibling `SECRET_DIR`, not the config dir.
- Fixed Playwright in Docker and idle browser cleanup to reclaim Chrome renderer processes.
- Ollama 404 avoided by honoring `base_url` and normalizing `/v1`.
- MCP sessions recovered from closure without overwriting active sessions.

### Changed
- All content translated from Chinese to English; Chinese locale files removed.
- CI/CD overhauled: fixed bad action SHAs, missing deps, switched from pnpm to npm.
- Codebase formatted with Black; pre-commit hooks installed.

---

[Unreleased]: https://github.com/ProwlrBot/prowlrbot/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/ProwlrBot/prowlrbot/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/ProwlrBot/prowlrbot/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ProwlrBot/prowlrbot/releases/tag/v0.3.0
