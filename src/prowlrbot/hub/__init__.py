# -*- coding: utf-8 -*-
"""ProwlrHub — War Room coordination engine.

Local-first agent coordination that lets AI agents across terminals
discover each other, claim tasks atomically, avoid duplicate work,
and operate as one visible team.

The hub is exposed as an MCP server (stdio) for Claude Code integration,
backed by SQLite for atomic operations and persistence.
"""
