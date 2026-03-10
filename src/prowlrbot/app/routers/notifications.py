# -*- coding: utf-8 -*-
"""API endpoints for the notification center."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

from ...constant import WORKING_DIR
from ...notifications.center import (
    Notification,
    NotificationCenter,
    NotificationStats,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])

_center = NotificationCenter(db_path=WORKING_DIR / "notifications.db")


@router.post("", response_model=Notification)
async def send_notification(notification: Notification) -> Notification:
    return _center.send(notification)


@router.get("", response_model=List[Notification])
async def list_notifications(
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Notification]:
    return _center.list_notifications(
        unread_only=unread_only, notification_type=notification_type,
        source=source, limit=limit, offset=offset,
    )


@router.get("/stats", response_model=NotificationStats)
async def get_stats() -> NotificationStats:
    return _center.get_stats()


@router.get("/{notification_id}", response_model=Notification)
async def get_notification(notification_id: str) -> Notification:
    notif = _center.get(notification_id)
    if not notif:
        raise HTTPException(404, f"Notification '{notification_id}' not found")
    return notif


@router.put("/{notification_id}/read")
async def mark_read(notification_id: str) -> Dict[str, str]:
    if not _center.mark_read(notification_id):
        raise HTTPException(404, f"Notification '{notification_id}' not found")
    return {"status": "read"}


@router.put("/read-all")
async def mark_all_read() -> Dict[str, int]:
    count = _center.mark_all_read()
    return {"marked_read": count}


@router.delete("/{notification_id}")
async def dismiss_notification(notification_id: str) -> Dict[str, str]:
    if not _center.dismiss(notification_id):
        raise HTTPException(404, f"Notification '{notification_id}' not found")
    return {"status": "dismissed"}


@router.post("/cleanup")
async def cleanup(older_than_days: int = 30) -> Dict[str, int]:
    count = _center.cleanup(older_than_days)
    return {"removed": count}
