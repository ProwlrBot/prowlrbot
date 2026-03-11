# -*- coding: utf-8 -*-
"""WebSocket support for the ProwlrHub bridge."""

import asyncio
import hmac
import json
import logging
import os

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# Connected WebSocket clients
_ws_clients: set[WebSocket] = set()

# Connection limit to prevent DoS
MAX_WS_CLIENTS = 50
# Max inbound message size (bytes)
MAX_MESSAGE_SIZE = 1024


async def broadcast_ws(event: dict):
    """Push event to all connected WebSocket clients."""
    if not _ws_clients:
        return
    dead = set()
    msg = json.dumps(event, default=str)
    for ws in _ws_clients:
        try:
            await ws.send_text(msg)
        except Exception:
            dead.add(ws)
    _ws_clients -= dead


async def warroom_ws(ws: WebSocket):
    """Real-time war room event stream with auth and connection limits."""
    # Verify auth token if PROWLR_HUB_SECRET is set
    secret = os.environ.get("PROWLR_HUB_SECRET", "")
    if secret:
        token = ws.query_params.get("token", "")
        if not hmac.compare_digest(token, secret):
            await ws.close(code=4001, reason="Unauthorized")
            return

    # Enforce connection limit
    if len(_ws_clients) >= MAX_WS_CLIENTS:
        await ws.close(code=4002, reason="Too many connections")
        return

    await ws.accept()
    _ws_clients.add(ws)
    logger.info("WebSocket client connected (%d total)", len(_ws_clients))
    try:
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_text(), timeout=35)
                # Enforce message size limit
                if len(data) > MAX_MESSAGE_SIZE:
                    await ws.close(code=1009, reason="Message too large")
                    break
                if data == "ping":
                    await ws.send_text("pong")
            except asyncio.TimeoutError:
                # Send keepalive
                await ws.send_text(json.dumps({"type": "keepalive"}))
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        _ws_clients.discard(ws)
        logger.info("WebSocket client disconnected (%d remaining)", len(_ws_clients))
