# -*- coding: utf-8 -*-
"""API endpoints for per-agent configuration."""

from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...agents.agent_config import AgentConfig
from ...agents.agent_store import AgentStore
from ...constant import WORKING_DIR

router = APIRouter(prefix="/agents", tags=["agents"])

_store = AgentStore(base_dir=WORKING_DIR / "agents")


class AgentResponse(BaseModel):
    """Agent with its ID."""

    id: str
    config: Dict


@router.get("", response_model=List[AgentResponse])
async def list_agents() -> List[AgentResponse]:
    """List all configured agents."""
    agents = _store.list()
    return [
        AgentResponse(id=agent_id, config=config.model_dump())
        for agent_id, config in agents
    ]


@router.post("", response_model=AgentResponse)
async def create_agent(config: AgentConfig) -> AgentResponse:
    """Create a new agent."""
    agent_id = _store.create(config)
    return AgentResponse(id=agent_id, config=config.model_dump())


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get an agent by ID."""
    config = _store.get(agent_id)
    if config is None:
        raise HTTPException(404, detail=f"Agent '{agent_id}' not found")
    return AgentResponse(id=agent_id, config=config.model_dump())


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, config: AgentConfig) -> AgentResponse:
    """Update an agent's configuration."""
    if not _store.update(agent_id, config):
        raise HTTPException(404, detail=f"Agent '{agent_id}' not found")
    return AgentResponse(id=agent_id, config=config.model_dump())


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent."""
    if not _store.delete(agent_id):
        raise HTTPException(404, detail=f"Agent '{agent_id}' not found")
    return {"status": "deleted"}
