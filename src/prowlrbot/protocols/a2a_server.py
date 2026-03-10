# -*- coding: utf-8 -*-
"""A2A (Agent-to-Agent) protocol server — discover and coordinate with agents.

Exposes ProwlrBot agents as A2A-compatible endpoints with Agent Cards,
task lifecycle, and context sharing.

Integration path:
    1. Mount A2A router on the FastAPI app
    2. Agents auto-register Agent Cards on startup
    3. External A2A agents discover ProwlrBot via /.well-known/agent.json
"""
from __future__ import annotations

import uuid
from enum import StrEnum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class A2AAgentCard(BaseModel):
    """A2A Agent Card — capability descriptor."""

    name: str = "ProwlrBot"
    description: str = "Autonomous AI agent platform — Always watching. Always ready."
    url: str = ""
    version: str = "1.0.0"
    capabilities: List[str] = Field(
        default_factory=lambda: [
            "chat",
            "monitoring",
            "cron",
            "skills",
            "mcp",
            "multi-channel",
        ]
    )
    supported_protocols: List[str] = Field(
        default_factory=lambda: ["a2a", "mcp", "roar"]
    )


class A2ATask(BaseModel):
    """A task in the A2A task lifecycle."""

    id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    from_agent: str = ""
    to_agent: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)


class A2ATaskStore:
    """In-memory task store for A2A coordination."""

    def __init__(self) -> None:
        self._tasks: Dict[str, A2ATask] = {}

    def create(self, task: A2ATask) -> A2ATask:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[A2ATask]:
        return self._tasks.get(task_id)

    def update_status(self, task_id: str, status: TaskStatus) -> Optional[A2ATask]:
        task = self._tasks.get(task_id)
        if task:
            task.status = status
        return task

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[A2ATask]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks


# ------------------------------------------------------------------
# FastAPI Router
# ------------------------------------------------------------------

router = APIRouter(tags=["a2a"])
_store = A2ATaskStore()
_agent_card = A2AAgentCard()


@router.get("/.well-known/agent.json")
async def get_agent_card() -> Dict[str, Any]:
    """A2A agent discovery endpoint."""
    return _agent_card.model_dump()


@router.post("/a2a/tasks", response_model=A2ATask)
async def create_task(task: A2ATask) -> A2ATask:
    """Create a new A2A task."""
    task.status = TaskStatus.PENDING
    return _store.create(task)


@router.get("/a2a/tasks/{task_id}", response_model=A2ATask)
async def get_task(task_id: str) -> A2ATask:
    """Get task status."""
    task = _store.get(task_id)
    if not task:
        from fastapi import HTTPException

        raise HTTPException(404, f"Task '{task_id}' not found")
    return task


@router.get("/a2a/tasks", response_model=List[A2ATask])
async def list_tasks(status: Optional[str] = None) -> List[A2ATask]:
    """List all A2A tasks."""
    task_status = TaskStatus(status) if status else None
    return _store.list_tasks(task_status)


@router.put("/a2a/tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> Dict[str, str]:
    """Cancel a task."""
    task = _store.update_status(task_id, TaskStatus.CANCELLED)
    if not task:
        from fastapi import HTTPException

        raise HTTPException(404, f"Task '{task_id}' not found")
    return {"status": "cancelled"}
