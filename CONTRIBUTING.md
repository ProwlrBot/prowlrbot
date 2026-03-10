# Contributing to ProwlrBot

Thank you for your interest in contributing to ProwlrBot. We are building an autonomous AI agent platform for monitoring, automation, and multi-channel communication -- and we want you to be part of it.

Whether you fix a typo, add a new channel, build a skill, improve security, or tackle a gnarly bug, every contribution matters.

**Quick links:** [GitHub](https://github.com/prowlrbot/prowlrbot) | [Issues](https://github.com/prowlrbot/prowlrbot/issues) | [Discussions](https://github.com/prowlrbot/prowlrbot/discussions) | [Security Policy](SECURITY.md) | [License: Apache 2.0](LICENSE)

---

## Getting Started

### 1. Clone and Install

```bash
git clone https://github.com/prowlrbot/prowlrbot.git
cd prowlrbot
pip install -e ".[dev]"
pre-commit install
```

### 2. Initialize and Run

```bash
prowlr init --defaults
prowlr app
```

ProwlrBot is now running at `http://localhost:8088`. The Console UI is served automatically.

### 3. Run Tests

```bash
pytest                                          # full suite
pytest tests/test_react_agent_tool_choice.py    # single test
pytest -m "not slow"                            # skip slow tests
```

That is it. Three steps to a working development environment.

### Console Frontend (optional)

If you are working on the React console:

```bash
cd console
npm ci
npm run build      # production build
npm run dev        # dev server with hot reload
npm run format     # format before committing
```

---

## Finding Your First Contribution

New to ProwlrBot? Start here:

- **[`good first issue`](https://github.com/prowlrbot/prowlrbot/labels/good%20first%20issue)** -- Curated issues that are well-scoped and beginner-friendly. These include clear context and pointers to the relevant code.
- **[`help wanted`](https://github.com/prowlrbot/prowlrbot/labels/help%20wanted)** -- Issues where we would especially appreciate community help.
- **Documentation improvements** -- Found something confusing? Fix it. Clear docs help everyone.
- **Test coverage** -- Adding tests for untested paths is always welcome.

If you want to work on something but are not sure where to start, open a [discussion](https://github.com/prowlrbot/prowlrbot/discussions/categories/help) or comment on an issue. We are happy to help you find a good entry point.

---

## How to Contribute

### 1. Check Existing Issues

Before starting work:

- **Search [open issues](https://github.com/prowlrbot/prowlrbot/issues)** and [discussions](https://github.com/prowlrbot/prowlrbot/discussions) for related work.
- **If a related issue exists**: comment to say you want to work on it. This avoids duplicate effort.
- **If no related issue exists**: open one describing your proposal. For large changes, get alignment before writing code.

### 2. Create a Branch

```bash
git checkout -b feat/my-feature    # or fix/my-fix, docs/my-docs, etc.
```

### 3. Make Your Changes

Write clean, well-tested code. Follow the conventions below.

### 4. Submit a Pull Request

- Use a [Conventional Commits](https://www.conventionalcommits.org/) title: `type(scope): description`
- Fill out the PR template completely
- Link to any related issues
- Ensure CI passes

---

## Architecture Overview

ProwlrBot's architecture is documented in detail in [`CLAUDE.md`](CLAUDE.md). Here is the high-level flow:

```
User Message -> Channel -> ChannelManager -> AgentRunner
-> ProwlrBotAgent (ReActAgent) -> Model -> Response
-> Channel Output + ChatManager (persistence)
```

Key directories under `src/prowlrbot/`:

| Directory | Purpose |
|-----------|---------|
| `app/channels/` | Channel adapters (Discord, Telegram, DingTalk, Feishu, QQ, iMessage, Console) |
| `app/routers/` | FastAPI API routes |
| `agents/` | Agent logic, model factory, tools, skills, memory |
| `providers/` | Provider registry, detection, health checking, smart routing |
| `config/` | Pydantic config models, hot-reload |
| `monitor/` | Web/API change detection and notifications |
| `cli/` | Click CLI entry point |
| `local_models/` | Local model backends (llama.cpp, MLX, Ollama) |

---

## Extending ProwlrBot

ProwlrBot is designed to be extensible. Here are the main extension points.

### Adding a New Channel

Channels connect ProwlrBot to messaging platforms. To add one:

1. **Create a channel class** in `src/prowlrbot/app/channels/` that subclasses `BaseChannel` (defined in `base.py`).
2. **Set the `channel` class attribute** to a unique key (e.g., `"slack"`).
3. **Implement the lifecycle**: receive native payload, convert to `content_parts` (`TextContent`, `ImageContent`, `FileContent`), process through the agent, and send the response back.
4. **Register** in `src/prowlrbot/app/channels/registry.py`.
5. **Document** the channel's auth flow, webhooks, and configuration.
6. **Add tests** for message parsing and response formatting.

Users can also create custom channels without code changes by placing a module in `~/.prowlrbot/custom_channels/`.

### Adding a New Skill

Skills define what ProwlrBot can do. Each skill is a directory containing:

- **`SKILL.md`** -- Markdown instructions with YAML front matter (`name`, `description`).
- **`references/`** (optional) -- Reference documents for the agent.
- **`scripts/`** (optional) -- Scripts or tools the skill uses.

Place built-in skills in `src/prowlrbot/agents/skills/<skill_name>/`. Write clear trigger descriptions:

```yaml
---
name: my_skill
description: "Use this skill whenever the user wants to [main functionality]. Trigger especially when user mentions: [keywords]."
---
```

**Best practices for skill descriptions:**

1. **Clearly state when to trigger**: "Use this skill whenever user wants to..."
2. **List trigger keywords explicitly**: "Trigger especially when user mentions: \"call\", \"dial\", \"phone\""
3. **Be specific about scope**: What it does AND what it does not do
4. **Provide usage examples**: Show specific usage patterns in the body of SKILL.md

See existing skills for examples of good structure.

### Adding a New Provider

To add a new AI model provider:

1. **Add a `ProviderDefinition`** in `src/prowlrbot/providers/registry.py` with `id`, `name`, `default_base_url`, `env_var`, `cost_tier`, and `health_check_endpoint`.
2. **If the API is not OpenAI-compatible**, implement a `ChatModelBase` subclass supporting streaming, tools, and `tool_choice`.
3. **Register** the chat model class in `_CHAT_MODEL_MAP`.
4. **Document** required environment variables and configuration.

For OpenAI-compatible APIs, users can add custom providers via the Console UI or `providers.json` without any code changes.

### Adding a New Monitor

To add a new monitoring detector:

1. **Subclass `BaseDetector`** in `src/prowlrbot/monitor/detectors/`.
2. **Implement `async detect()`** with your detection logic.
3. **Register** and document the new detector type.

### Adding MCP Servers

ProwlrBot supports runtime MCP tool discovery and hot-plug. Contributing new MCP server integrations helps users extend the agent without changing core code. See the [MCP Integration](README.md#mcp-integration) section of the README for config format.

### Platform Support

ProwlrBot aims to run on Windows, Linux, and macOS. Contributions that improve platform support are welcome:

- **Compatibility fixes**: Path handling, shell commands, platform-specific dependencies.
- **Install and startup**: `pip install prowlrbot` and `prowlr init` / `prowlr app` should work on each platform.
- **Platform-specific features**: Optional integrations are fine as long as they do not break other platforms.

---

## Code Standards

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**Examples:**
```bash
feat(channels): add Slack channel adapter
fix(skills): correct SKILL.md front matter parsing
docs(readme): update quick start for Docker
refactor(providers): simplify custom provider validation
test(agents): add tests for skill loading
```

### PR Title Format

PR titles follow the same convention: `type(scope): description`

- Use one of: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`, `style`, `build`, `revert`.
- Scope must be lowercase (letters, numbers, hyphens, underscores only).
- Keep the description short and descriptive.

### Code Style

- **Python**: Black formatter, enforced via pre-commit. Python 3.10+ with async/await throughout.
- **Frontend**: Prettier via `npm run format` in `console/` and `website/`.
- **Config validation**: Pydantic `BaseModel` for all configuration.
- **Tests**: pytest with pytest-asyncio (`asyncio_mode = "auto"`).
- **Language**: All code, comments, docs, and UI in English.

### Pre-commit and CI

Always run pre-commit before submitting:

```bash
pre-commit run --all-files
```

CI will run the same checks. PRs with failing CI will not be merged.

---

## Code Review Process

Every PR goes through code review before merging. Here is what to expect:

1. **Automated checks** run first (pre-commit, tests, formatting). Fix any failures before requesting review.
2. **A maintainer will review** your PR, typically within a few business days. For larger changes, expect more thorough review.
3. **Feedback is collaborative**. We may suggest changes, ask questions, or propose alternatives. This is a normal part of the process.
4. **Iterate** on feedback. Push new commits to the same branch -- do not force-push during review.
5. **Approval and merge**. Once approved and CI passes, a maintainer will merge your PR.

### What reviewers look for

- **Correctness**: Does the code do what it claims?
- **Tests**: Are new code paths tested?
- **Security**: Does the change handle auth, secrets, or sandboxing correctly?
- **Documentation**: Are user-facing changes documented?
- **Style**: Does it follow project conventions?
- **Scope**: Is the PR focused on one thing?

### Security-Sensitive PRs

PRs that touch any of the following require explicit security review from a maintainer:

- Authentication or authorization logic
- Secret or credential handling (`~/.prowlrbot.secret/`, env vars, API keys)
- Sandboxing, skill loading, or code execution
- Channel authentication or webhook verification
- Configuration loading or validation
- File system access patterns

Mark these PRs with the `security` label and call out the security-relevant changes in your PR description.

---

## Do's and Don'ts

### DO

- Start with small, focused changes
- Discuss large or design-sensitive changes in an issue first
- Write or update tests for new functionality
- Update docs for user-facing changes
- Use conventional commit messages and PR titles
- Be respectful and constructive in all interactions

### DON'T

- Open very large PRs without prior discussion
- Ignore CI or pre-commit failures
- Mix unrelated changes in one PR
- Break existing APIs without a good reason and clear migration notes
- Add heavy dependencies to the core install without discussing in an issue
- Commit secrets, credentials, or API keys

---

## Getting Help

- **Discussions**: [GitHub Discussions](https://github.com/prowlrbot/prowlrbot/discussions) for questions, ideas, and general conversation
- **Issues**: [GitHub Issues](https://github.com/prowlrbot/prowlrbot/issues) for bugs and feature requests
- **Architecture**: [CLAUDE.md](CLAUDE.md) for the full source layout and conventions
- **Security**: [SECURITY.md](SECURITY.md) for the security policy and trust model

---

## License

By contributing to ProwlrBot, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).

---

Thank you for contributing to ProwlrBot. We are building something special and we want you to be part of it.
