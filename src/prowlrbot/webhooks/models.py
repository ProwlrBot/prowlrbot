# -*- coding: utf-8 -*-
"""Pydantic models for the webhook builder system."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TriggerType(str, Enum):
    """Events that can fire a webhook rule."""

    github_push = "github_push"
    monitor_alert = "monitor_alert"
    cron_schedule = "cron_schedule"
    channel_message = "channel_message"
    api_webhook = "api_webhook"
    marketplace_sale = "marketplace_sale"


class ActionType(str, Enum):
    """Operations that a webhook rule can perform."""

    run_agent = "run_agent"
    post_channel = "post_channel"
    send_webhook = "send_webhook"
    send_email = "send_email"
    create_task = "create_task"


class WebhookTrigger(BaseModel):
    """Trigger specification for a webhook rule.

    The ``config`` dict holds trigger-specific settings, e.g.:

    - ``github_push``: ``{"repo": "owner/repo", "branch": "main"}``
    - ``monitor_alert``: ``{"detector_id": "...", "severity": "high"}``
    - ``cron_schedule``: ``{"cron": "*/5 * * * *"}``
    - ``channel_message``: ``{"channel": "telegram", "pattern": "deploy.*"}``
    - ``api_webhook``: ``{"secret": "hmac-sha256-secret"}``
    - ``marketplace_sale``: ``{"skill_id": "..."}``
    """

    type: TriggerType
    config: Dict[str, Any] = Field(default_factory=dict)


class WebhookAction(BaseModel):
    """Action specification for a webhook rule.

    The ``config`` dict holds action-specific settings, e.g.:

    - ``run_agent``: ``{"input": "...", "session_id": "...", "user_id": "..."}``
    - ``post_channel``: ``{"channel": "discord", "target": "...", "message": "..."}``
    - ``send_webhook``: ``{"url": "https://...", "method": "POST", "headers": {}}``
    - ``send_email``: ``{"to": "user@example.com", "subject": "...", "body": "..."}``
    - ``create_task``: ``{"title": "...", "description": "...", "priority": "high"}``
    """

    type: ActionType
    config: Dict[str, Any] = Field(default_factory=dict)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WebhookRule(BaseModel):
    """A single trigger-action automation rule."""

    id: str = Field(default="", description="Server-generated UUID.")
    name: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="")
    trigger: WebhookTrigger
    actions: List[WebhookAction] = Field(..., min_length=1)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = Field(default=0, ge=0)


class WebhookFile(BaseModel):
    """Top-level container persisted to webhooks.json."""

    version: int = 1
    rules: List[WebhookRule] = Field(default_factory=list)
