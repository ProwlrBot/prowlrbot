# -*- coding: utf-8 -*-
"""ProwlrHub HTTP Bridge — cross-machine war room coordination.

SQLite can't be shared across Mac and WSL. This bridge exposes the
war room engine over HTTP so remote Claude Code terminals can participate.

Run on the machine that hosts the database:
    python -m prowlrbot.hub.bridge

Remote terminals connect by setting PROWLR_HUB_URL in their MCP config.
"""
# NOTE: intentionally no `from __future__ import annotations` here.
# FastAPI needs runtime-evaluable type annotations to detect Pydantic
# BaseModel parameters as request bodies (not query params).

import asyncio
import logging
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .engine import WarRoomEngine
from .status_page import STATUS_HTML
from .websocket import broadcast_ws, warroom_ws

logger = logging.getLogger(__name__)


# --- Request models (module-level so FastAPI can introspect them) ---

class RegisterRequest(BaseModel):
    name: str
    capabilities: List[str] = ["general"]


class ClaimRequest(BaseModel):
    task_id: str = ""
    title: str = ""
    file_scopes: List[str] = []
    description: str = ""
    priority: str = "normal"


class UpdateRequest(BaseModel):
    task_id: str
    progress_note: str


class CompleteRequest(BaseModel):
    task_id: str
    summary: str = ""


class FailRequest(BaseModel):
    task_id: str
    reason: str = ""


class LockRequest(BaseModel):
    path: str


class ConflictRequest(BaseModel):
    paths: List[str]


class BroadcastRequest(BaseModel):
    message: str


class FindingRequest(BaseModel):
    key: str
    value: str


def create_bridge_app() -> FastAPI:
    """Create a FastAPI app that exposes the war room engine over HTTP."""
    app = FastAPI(title="ProwlrHub Bridge", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8088", "http://127.0.0.1:8088"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    db_path = os.environ.get("PROWLR_HUB_DB", None)
    engine = WarRoomEngine(db_path)

    # Ensure default room exists
    engine.get_or_create_default_room()

    # Wire engine events → WebSocket broadcast
    def _on_engine_event(event: dict):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(broadcast_ws(event))
        except RuntimeError:
            pass  # No event loop yet

    engine.set_event_callback(_on_engine_event)

    # WebSocket endpoint for real-time war room events
    @app.websocket("/ws/warroom")
    async def ws_warroom(ws):
        await warroom_ws(ws)

    @app.get("/", response_class=HTMLResponse)
    async def status_page():
        """Standalone war room status page."""
        return STATUS_HTML

    @app.get("/health")
    def health():
        room = engine.get_or_create_default_room()
        agents = engine.get_agents(room["room_id"])
        tasks = engine.get_mission_board(room["room_id"])
        return {
            "status": "ok",
            "room_id": room["room_id"],
            "agents": len(agents),
            "tasks": len(tasks),
        }

    @app.post("/register")
    def register(req: RegisterRequest):
        room = engine.get_or_create_default_room()
        result = engine.register_agent(req.name, room["room_id"], req.capabilities)
        return result

    @app.post("/heartbeat/{agent_id}")
    def heartbeat(agent_id: str):
        engine.heartbeat(agent_id)
        return {"ok": True}

    @app.get("/board")
    def mission_board(status: str = ""):
        room = engine.get_or_create_default_room()
        tasks = engine.get_mission_board(room["room_id"])
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return {"tasks": tasks}

    @app.post("/claim/{agent_id}")
    def claim_task(agent_id: str, req: ClaimRequest):
        room = engine.get_or_create_default_room()
        task_id = req.task_id
        if not task_id and req.title:
            task = engine.create_task(
                room["room_id"], req.title,
                description=req.description,
                file_scopes=req.file_scopes,
                priority=req.priority,
            )
            task_id = task["task_id"]
        result = engine.claim_task(task_id, agent_id, room["room_id"])
        if result.success:
            return {"success": True, "lock_token": result.lock_token}
        return {"success": False, "reason": result.reason, "conflicts": result.conflicts}

    @app.post("/update/{agent_id}")
    def update_task(agent_id: str, req: UpdateRequest):
        engine.update_task(req.task_id, agent_id, req.progress_note)
        return {"ok": True}

    @app.post("/complete/{agent_id}")
    def complete_task(agent_id: str, req: CompleteRequest):
        ok = engine.complete_task(req.task_id, agent_id, req.summary)
        return {"ok": ok}

    @app.post("/fail/{agent_id}")
    def fail_task(agent_id: str, req: FailRequest):
        ok = engine.fail_task(req.task_id, agent_id, req.reason)
        return {"ok": ok}

    @app.post("/lock/{agent_id}")
    def lock_file(agent_id: str, req: LockRequest):
        room = engine.get_or_create_default_room()
        result = engine.lock_file(req.path, agent_id, room["room_id"])
        if result.success:
            return {"success": True, "lock_token": result.lock_token}
        return {"success": False, "reason": result.reason, "owner": result.owner}

    @app.post("/unlock/{agent_id}")
    def unlock_file(agent_id: str, req: LockRequest):
        room = engine.get_or_create_default_room()
        ok = engine.unlock_file(req.path, agent_id, room["room_id"])
        return {"ok": ok}

    @app.post("/conflicts")
    def check_conflicts(req: ConflictRequest):
        room = engine.get_or_create_default_room()
        conflicts = engine.check_conflicts(req.paths, room["room_id"])
        return {"conflicts": conflicts}

    @app.get("/agents")
    def get_agents():
        room = engine.get_or_create_default_room()
        return {"agents": engine.get_agents(room["room_id"])}

    @app.post("/broadcast/{agent_id}")
    def broadcast(agent_id: str, req: BroadcastRequest):
        room = engine.get_or_create_default_room()
        engine.broadcast_status(room["room_id"], agent_id, req.message)
        return {"ok": True}

    @app.post("/findings/{agent_id}")
    def share_finding(agent_id: str, req: FindingRequest):
        room = engine.get_or_create_default_room()
        engine.set_context(room["room_id"], agent_id, req.key, req.value)
        return {"ok": True}

    @app.get("/context")
    def get_context(key: str = ""):
        room = engine.get_or_create_default_room()
        return {"context": engine.get_context(room["room_id"], key)}

    @app.get("/events")
    def get_events(limit: int = 20, event_type: str = ""):
        room = engine.get_or_create_default_room()
        return {"events": engine.get_events(room["room_id"], limit, event_type)}

    # --- JSON API endpoints for dashboard consumption ---

    @app.get("/api/agents")
    def api_agents():
        room = engine.get_or_create_default_room()
        return engine.get_agents(room["room_id"])

    @app.get("/api/board")
    def api_board(status: str = ""):
        room = engine.get_or_create_default_room()
        tasks = engine.get_mission_board(room["room_id"])
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return tasks

    @app.get("/api/events")
    def api_events(limit: int = 50, event_type: str = ""):
        room = engine.get_or_create_default_room()
        return engine.get_events(room["room_id"], limit, event_type)

    @app.get("/api/context")
    def api_context(key: str = ""):
        room = engine.get_or_create_default_room()
        return engine.get_context(room["room_id"], key)

    @app.get("/api/conflicts")
    def api_conflicts():
        room = engine.get_or_create_default_room()
        room_id = room["room_id"]
        rows = engine._conn.execute(
            """SELECT fl.*, a.name as agent_name
               FROM file_locks fl
               LEFT JOIN agents a ON fl.agent_id = a.agent_id
               WHERE fl.room_id=?
               ORDER BY fl.acquired_at DESC""",
            (room_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    return app


def run_bridge():
    """Run the HTTP bridge server."""
    import uvicorn

    host = os.environ.get("PROWLR_BRIDGE_HOST", "0.0.0.0")
    port = int(os.environ.get("PROWLR_BRIDGE_PORT", "8099"))

    logging.basicConfig(level=logging.INFO)
    logger.info("ProwlrHub Bridge starting on %s:%d", host, port)

    app = create_bridge_app()
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_bridge()
