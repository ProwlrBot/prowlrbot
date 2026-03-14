# -*- coding: utf-8 -*-
"""Console UI extension API: plugins that add tabs/pages (from marketplace or built-in)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...auth.middleware import get_current_user
from ...auth.models import User
from ...marketplace.store import MarketplaceStore

router = APIRouter(prefix="/console", tags=["console"])

_store: MarketplaceStore | None = None


def _get_store() -> MarketplaceStore:
    global _store
    if _store is None:
        _store = MarketplaceStore()
    return _store


@router.get("/plugins")
async def get_console_plugins(
    user: User = Depends(get_current_user),
) -> list[dict]:
    """Return console plugin manifests for the sidebar and routes.

    Includes built-in plugins (e.g. War Room) plus any from marketplace
    listings the current user has installed that declare a console_plugin.
    Each item has path, label, icon, entry (built-in key or URL for iframe).
    """
    return _get_store().get_console_plugins(user_id=user.id)
