# -*- coding: utf-8 -*-
"""FastAPI router for usage analytics endpoints."""

from typing import Dict, List

from fastapi import APIRouter, Request

from prowlrbot.dashboard.analytics import (
    AnalyticsTracker,
    ModelStats,
    UsageStat,
    UsageSummary,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Lazily initialized singleton tracker
_tracker: AnalyticsTracker | None = None


def _get_tracker() -> AnalyticsTracker:
    """Get or create the global AnalyticsTracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = AnalyticsTracker()
    return _tracker


@router.get("/summary", response_model=UsageSummary)
async def get_summary(period: str = "day") -> UsageSummary:
    """Get aggregated usage summary for a time period.

    Query params:
        period: "day", "week", "month", or "all" (default: "day")
    """
    if period not in ("day", "week", "month", "all"):
        period = "day"
    return _get_tracker().get_summary(period=period)


@router.get("/models", response_model=Dict[str, ModelStats])
async def get_model_breakdown() -> Dict[str, ModelStats]:
    """Get per-model usage breakdown (all time)."""
    return _get_tracker().get_model_breakdown()


@router.get("/cost-over-time", response_model=List[dict])
async def get_cost_over_time(days: int = 30) -> List[dict]:
    """Get daily cost data for charting.

    Query params:
        days: Number of days to look back (default: 30)
    """
    days = max(1, min(days, 365))
    return _get_tracker().get_cost_over_time(days=days)


@router.get("/recent", response_model=List[UsageStat])
async def get_recent(limit: int = 50) -> List[UsageStat]:
    """Get the most recent usage records.

    Query params:
        limit: Maximum number of records to return (default: 50, max: 500)
    """
    limit = max(1, min(limit, 500))
    return _get_tracker().get_recent(limit=limit)
