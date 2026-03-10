# -*- coding: utf-8 -*-
"""API endpoints for AgentVerse — the virtual world for AI agents."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...agentverse.models import (
    AgentPresence,
    ArenaBattle,
    Guild,
    TradeOffer,
    Zone,
    ZoneInfo,
)
from ...agentverse.world import AgentVerseWorld
from ...constant import WORKING_DIR

router = APIRouter(prefix="/agentverse", tags=["agentverse"])

_world = AgentVerseWorld(db_path=WORKING_DIR / "agentverse.db")


# --- Agents ---

@router.post("/agents", response_model=AgentPresence)
async def register_agent(presence: AgentPresence) -> AgentPresence:
    return _world.register_agent(presence)


@router.get("/agents/{agent_id}", response_model=AgentPresence)
async def get_agent(agent_id: str) -> AgentPresence:
    agent = _world.get_agent(agent_id)
    if not agent:
        raise HTTPException(404, f"Agent '{agent_id}' not found in AgentVerse")
    return agent


@router.get("/agents", response_model=List[AgentPresence])
async def list_online_agents() -> List[AgentPresence]:
    return _world.list_online_agents()


@router.put("/agents/{agent_id}/move")
async def move_agent(agent_id: str, zone: Zone) -> Dict[str, str]:
    if not _world.move_agent(agent_id, zone):
        raise HTTPException(404, f"Agent '{agent_id}' not found")
    return {"status": "moved", "zone": zone}


@router.put("/agents/{agent_id}/online")
async def set_online(agent_id: str, online: bool = True) -> Dict[str, Any]:
    _world.set_online(agent_id, online)
    return {"agent_id": agent_id, "online": online}


@router.post("/agents/{agent_id}/friend/{friend_id}")
async def add_friend(agent_id: str, friend_id: str) -> Dict[str, str]:
    _world.add_friend(agent_id, friend_id)
    return {"status": "added"}


# --- Zones ---

@router.get("/zones", response_model=List[ZoneInfo])
async def list_zones() -> List[ZoneInfo]:
    return _world.get_zone_info()


@router.get("/zones/{zone}/agents", response_model=List[AgentPresence])
async def agents_in_zone(zone: Zone) -> List[AgentPresence]:
    return _world.list_agents_in_zone(zone)


# --- Guilds ---

@router.post("/guilds", response_model=Guild)
async def create_guild(guild: Guild) -> Guild:
    return _world.create_guild(guild)


@router.get("/guilds", response_model=List[Guild])
async def list_guilds() -> List[Guild]:
    return _world.list_guilds()


# --- Trades ---

@router.post("/trades", response_model=TradeOffer)
async def create_trade(trade: TradeOffer) -> TradeOffer:
    return _world.create_trade(trade)


@router.get("/trades/{agent_id}", response_model=List[TradeOffer])
async def list_trades(agent_id: str) -> List[TradeOffer]:
    return _world.list_trades(agent_id)


class TradeResponse(BaseModel):
    trade_id: str
    accept: bool


@router.post("/trades/respond")
async def respond_trade(req: TradeResponse) -> Dict[str, str]:
    if not _world.respond_trade(req.trade_id, req.accept):
        raise HTTPException(404, "Trade not found or already resolved")
    return {"status": "accepted" if req.accept else "rejected"}


# --- Battles ---

@router.post("/battles", response_model=ArenaBattle)
async def create_battle(battle: ArenaBattle) -> ArenaBattle:
    return _world.create_battle(battle)


class BattleResult(BaseModel):
    battle_id: str
    challenger_score: float
    defender_score: float


@router.post("/battles/complete")
async def complete_battle(result: BattleResult) -> Dict[str, Any]:
    battle = _world.complete_battle(result.battle_id, result.challenger_score, result.defender_score)
    if not battle:
        raise HTTPException(404, "Battle not found")
    return {"winner": battle.winner_id, "status": "completed"}
