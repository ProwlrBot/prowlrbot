# -*- coding: utf-8 -*-
"""ACP (Agent Client Protocol) server — expose ProwlrBot as an ACP agent.

When running, any IDE with ACP support (VS Code, Zed, JetBrains) can use
ProwlrBot as its coding agent via JSON-RPC 2.0 over stdio.

Usage:
    prowlr acp   # start ACP server on stdio
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional


class ACPServer:
    """Minimal ACP JSON-RPC 2.0 server over stdio."""

    def __init__(self, runner=None) -> None:
        self._session_id: Optional[str] = None
        self._initialized = False
        self._runner = runner

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route a JSON-RPC request to the appropriate handler."""
        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        handlers = {
            "initialize": self._handle_initialize,
            "session/new": self._handle_session_new,
            "session/prompt": self._handle_session_prompt,
            "session/cancel": self._handle_session_cancel,
            "shutdown": self._handle_shutdown,
        }

        handler = handlers.get(method)
        if handler is None:
            return self._error_response(req_id, -32601, f"Method not found: {method}")

        try:
            result = await handler(params)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as exc:
            return self._error_response(req_id, -32603, str(exc))

    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ACP initialize handshake."""
        self._initialized = True
        return {
            "name": "ProwlrBot",
            "version": "1.0.0",
            "capabilities": {
                "prompting": True,
                "streaming": True,
                "tools": True,
            },
        }

    async def _handle_session_new(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ACP session."""
        import uuid

        self._session_id = f"acp_{uuid.uuid4().hex[:8]}"
        return {"session_id": self._session_id}

    async def _handle_session_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a prompt in the current session."""
        prompt = params.get("prompt", "")
        if not self._session_id:
            return {"error": "No active session. Call session/new first.", "status": "error"}

        if self._runner is None:
            return {
                "session_id": self._session_id,
                "response": f"[ProwlrBot ACP] No runner configured. Received: {prompt[:100]}",
                "status": "no_runner",
            }

        try:
            result = await self._runner.process_query(prompt)
            return {
                "session_id": self._session_id,
                "response": result.get("response", ""),
                "status": "ok",
            }
        except Exception as exc:
            return {
                "session_id": self._session_id,
                "response": str(exc),
                "status": "error",
            }

    async def _handle_session_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel the current session."""
        self._session_id = None
        return {"status": "cancelled"}

    async def _handle_shutdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Shut down the ACP server."""
        self._initialized = False
        return {"status": "shutdown"}

    @staticmethod
    def _error_response(req_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message},
        }

    async def run_stdio(self) -> None:
        """Run the ACP server reading JSON-RPC from stdin, writing to stdout."""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue
            response = await self.handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
