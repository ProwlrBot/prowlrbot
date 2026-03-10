# -*- coding: utf-8 -*-
"""Gamification data models."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class XPGain(BaseModel):
    """A single XP gain event."""

    entity_id: str
    entity_type: str = "user"  # "user" or "agent"
    amount: int
    category: str
    reason: str
    timestamp: float = 0.0


# Level thresholds: (level, title, xp_required)
USER_LEVELS: list[tuple[int, str, int]] = [
    (1, "Newcomer", 0),
    (5, "Explorer", 500),
    (10, "Builder", 2_000),
    (15, "Architect", 5_000),
    (20, "Commander", 10_000),
    (25, "Veteran", 20_000),
    (30, "Legend", 40_000),
    (50, "Grandmaster", 100_000),
]

AGENT_LEVELS: list[tuple[int, str, int]] = [
    (1, "Pup", 0),
    (5, "Scout", 500),
    (10, "Agent", 2_000),
    (15, "Specialist", 5_000),
    (20, "Elite", 10_000),
    (25, "Master", 20_000),
    (30, "Legend", 40_000),
]


def level_from_xp(xp: int, entity_type: str = "user") -> tuple[int, str]:
    """Return (level, title) for a given XP total."""
    levels = USER_LEVELS if entity_type == "user" else AGENT_LEVELS
    current_level, current_title = 1, levels[0][1]
    for level, title, threshold in levels:
        if xp >= threshold:
            current_level, current_title = level, title
        else:
            break
    return current_level, current_title


class LevelInfo(BaseModel):
    """Current level info for an entity."""

    entity_id: str
    entity_type: str
    total_xp: int
    level: int
    title: str
    xp_to_next: int


class Achievement(BaseModel):
    """An achievement definition."""

    id: str
    name: str
    description: str
    xp_reward: int = 0
    badge: str = ""
    hidden: bool = False


class UnlockedAchievement(BaseModel):
    """A user/agent's unlocked achievement."""

    achievement_id: str
    entity_id: str
    unlocked_at: float


class LeaderboardEntry(BaseModel):
    """A single leaderboard row."""

    rank: int
    entity_id: str
    entity_type: str
    total_xp: int
    level: int
    title: str


# Built-in achievement definitions
ACHIEVEMENTS: list[Achievement] = [
    Achievement(id="first_steps", name="First Steps", description="Send your first message to an agent", xp_reward=10, badge="🐾"),
    Achievement(id="skill_crafter", name="Skill Crafter", description="Create your first custom skill", xp_reward=50, badge="🔧"),
    Achievement(id="channel_surfer", name="Channel Surfer", description="Connect 3 different channels", xp_reward=100, badge="📡"),
    Achievement(id="night_owl", name="Night Owl", description="Agent completes a task between 2am-5am", xp_reward=25, badge="🦉"),
    Achievement(id="century_club", name="Century Club", description="Complete 100 tasks", xp_reward=200, badge="💯"),
    Achievement(id="marathon", name="Marathon", description="10 consecutive days with agent activity", xp_reward=150, badge="🏃"),
    Achievement(id="polyglot", name="Polyglot", description="Use 3 different AI models", xp_reward=75, badge="🌍"),
    Achievement(id="monitor_master", name="Monitor Master", description="Set up 5 monitoring targets", xp_reward=100, badge="👁️"),
]

# XP award amounts by category
XP_AWARDS = {
    "task_complete": 10,
    "new_tool_used": 25,
    "skill_created": 50,
    "marketplace_publish": 100,
    "skill_downloaded": 5,
    "skill_reviewed": 25,
    "arena_win": 75,
    "daily_challenge": 30,
    "github_pr_merged": 200,
    "invite_user": 150,
    "uptime_streak_day": 5,
    "channel_connected": 40,
    "monitor_created": 20,
    "monitor_alert_resolved": 15,
}
