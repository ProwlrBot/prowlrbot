# -*- coding: utf-8 -*-
"""Webhook builder — a "visual Zapier for agents" system.

Provides trigger-action automation rules that connect external events
(GitHub pushes, monitor alerts, cron schedules, channel messages, API
webhooks, marketplace sales) to agent actions (run agent, post to channel,
send webhook, send email, create task).

Rules are persisted as JSON and executed asynchronously when matching
triggers fire.
"""
from .models import (
    ActionType,
    TriggerType,
    WebhookAction,
    WebhookFile,
    WebhookRule,
    WebhookTrigger,
)
from .store import WebhookStore
from .executor import WebhookExecutor

__all__ = [
    "ActionType",
    "TriggerType",
    "WebhookAction",
    "WebhookExecutor",
    "WebhookFile",
    "WebhookRule",
    "WebhookStore",
    "WebhookTrigger",
]
