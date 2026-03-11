# -*- coding: utf-8 -*-
"""CLI command to start the ACP server over stdio."""

from __future__ import annotations

import asyncio

import click


@click.command(name="acp", help="Start ACP server (JSON-RPC 2.0 over stdio)")
def acp_cmd():
    """Start ProwlrBot as an ACP agent for IDE integration."""
    from ..protocols.acp_server import ACPServer

    click.echo("ProwlrBot ACP server starting on stdio...", err=True)
    server = ACPServer()
    asyncio.run(server.run_stdio())
