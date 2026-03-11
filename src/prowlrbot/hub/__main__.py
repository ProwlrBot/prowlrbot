#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entry point for running ProwlrHub as an MCP server.

Usage:
    python -m prowlrbot.hub
"""

from .mcp_server import run_mcp_server

if __name__ == "__main__":
    run_mcp_server()
