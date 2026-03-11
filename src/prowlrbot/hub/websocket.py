# -*- coding: utf-8 -*-
"""WebSocket support for the ProwlrHub bridge."""

import asyncio
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# Connected WebSocket clients
_ws_clients: set[WebSocket] = set()


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
    """Real-time war room event stream."""
    await ws.accept()
    _ws_clients.add(ws)
    logger.info("WebSocket client connected (%d total)", len(_ws_clients))
    try:
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_text(), timeout=35)
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
