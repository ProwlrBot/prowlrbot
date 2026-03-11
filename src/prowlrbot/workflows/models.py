# -*- coding: utf-8 -*-
"""Pydantic models for the ProwlrBot Workflow Engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from prowlrbot.compat import StrEnum


class StepType(StrEnum):
    """What a workflow step does."""

    agent_query = "agent_query"
    channel_send = "channel_send"
    conditional = "conditional"
    parallel_group = "parallel_group"
    transform = "transform"


class ErrorStrategy(StrEnum):
    """How to handle a step failure."""

    skip = "skip"
    retry = "retry"
    abort = "abort"
    fallback = "fallback"


class WorkflowStep(BaseModel):
    """A single step in a workflow DAG."""

    id: str
    type: StepType = StepType.agent_query
    prompt: str = ""
    tools: list[str] = Field(default_factory=list)
    inputs: dict[str, str] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    condition: str = ""
    on_error: ErrorStrategy = ErrorStrategy.skip
    timeout_seconds: int = 120
    retries: int = 0

    # For channel_send steps
    channel: str = ""
    message_template: str = ""

    # For parallel_group steps
    parallel_steps: list[str] = Field(default_factory=list)

    # For transform steps
    transform_expr: str = ""


class TriggerType(StrEnum):
    """What triggers a workflow."""

    cron = "cron"
    webhook = "webhook"
    event = "event"
    manual = "manual"


class WorkflowTrigger(BaseModel):
    """When/how a workflow is triggered."""

    type: TriggerType = TriggerType.manual
    schedule: str = ""
    timezone: str = "UTC"
    webhook_path: str = ""
    event_type: str = ""


class WorkflowSpec(BaseModel):
    """Complete definition of a multi-step workflow."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str
    version: str = "1.0.0"
    description: str = ""
    trigger: WorkflowTrigger = Field(default_factory=WorkflowTrigger)
    config: dict[str, Any] = Field(default_factory=dict)
    steps: list[WorkflowStep] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )


class StepStatus(StrEnum):
    """Runtime status of a single step."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class StepResult(BaseModel):
    """The result of executing one workflow step."""

    step_id: str
    status: StepStatus = StepStatus.pending
    output: str = ""
    error: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: int = 0


class WorkflowRunStatus(StrEnum):
    """Overall status of a workflow run."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class WorkflowRun(BaseModel):
    """A single execution of a workflow."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    workflow_id: str
    status: WorkflowRunStatus = WorkflowRunStatus.pending
    step_results: dict[str, StepResult] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: str = ""
