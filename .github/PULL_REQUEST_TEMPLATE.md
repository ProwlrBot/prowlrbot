## Description

<!-- Describe what this PR does and why. Link to any related issues. -->

**Related Issue:** Fixes #(issue_number) <!-- or: Relates to #(issue_number) -->

## Type of Change

<!-- Check all that apply. -->

- [ ] `feat` -- New feature
- [ ] `fix` -- Bug fix
- [ ] `docs` -- Documentation only
- [ ] `refactor` -- Code restructuring (no behavior change)
- [ ] `perf` -- Performance improvement
- [ ] `test` -- Adding or updating tests
- [ ] `chore` -- Build, tooling, or maintenance
- [ ] `style` -- Code style (formatting, whitespace)

## Component(s) Affected

- [ ] Backend (app, agents, config, providers)
- [ ] Console (React frontend)
- [ ] Website (docs site)
- [ ] CLI (`prowlr` command)
- [ ] Channels (Discord, Telegram, DingTalk, Feishu, QQ, iMessage, Console)
- [ ] Monitoring (web/API detectors, notifications)
- [ ] Skills
- [ ] MCP Integration
- [ ] Local Models (llama.cpp, MLX, Ollama)
- [ ] CI/CD / DevOps
- [ ] Tests

## Breaking Changes

<!-- Does this PR introduce breaking changes? If yes, describe the migration path. -->

- [ ] This PR introduces breaking changes

<!-- If checked, describe what breaks and how users should migrate: -->

## Testing

<!-- Describe how you tested these changes. Include commands, screenshots, or test output. -->

```bash
# Example:
pytest tests/test_relevant_module.py
```

## Security Considerations

<!-- Required for PRs touching auth, secrets, sandboxing, channels, or config loading. -->
<!-- Delete this section if not applicable. -->

- [ ] This PR touches security-sensitive code (auth, secrets, sandboxing, channels)
- [ ] I have reviewed the changes for security implications
- [ ] No new secrets or credentials are exposed

## Checklist

- [ ] My PR title follows [Conventional Commits](https://www.conventionalcommits.org/) format: `type(scope): description`
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] Tests pass locally (`pytest`)
- [ ] I have added tests for new functionality (if applicable)
- [ ] Documentation is updated for user-facing changes (if applicable)
- [ ] I have read the [Contributing Guide](https://github.com/prowlrbot/prowlrbot/blob/main/CONTRIBUTING.md)

## Additional Notes

<!-- Optional: screenshots, performance benchmarks, design decisions, anything else reviewers should know. -->
