# -*- coding: utf-8 -*-
"""FastAPI dependency functions for JWT authentication and RBAC."""

from __future__ import annotations

import logging
import os
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Callable, Sequence

from fastapi import Depends, HTTPException, Request

from .jwt_handler import JWTHandler
from .models import Permission, Role, ROLE_PERMISSIONS, User
from .store import UserStore

logger = logging.getLogger(__name__)

# Resolve JWT secret once at module load: prefer env var, then persisted file,
# then generate and persist a new one.
_JWT_SECRET_PATH = Path.home() / ".prowlrbot.secret" / "jwt_secret"


def _resolve_jwt_secret() -> str:
    """Return a stable JWT secret, persisting to disk if newly generated."""
    # 1. Environment variable takes priority
    env_secret = os.environ.get("PROWLRBOT_JWT_SECRET", "")
    if env_secret:
        return env_secret

    # 2. Persisted secret file
    if _JWT_SECRET_PATH.exists():
        stored = _JWT_SECRET_PATH.read_text().strip()
        if stored:
            return stored

    # 3. Generate, persist, and return
    new_secret = secrets.token_hex(32)
    _JWT_SECRET_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _JWT_SECRET_PATH.write_text(new_secret)
    _JWT_SECRET_PATH.chmod(0o600)
    logger.info(
        "Generated and persisted JWT secret to %s. "
        "Set PROWLRBOT_JWT_SECRET env var to override.",
        _JWT_SECRET_PATH,
    )
    return new_secret


_JWT_SECRET: str = _resolve_jwt_secret()


@lru_cache(maxsize=1)
def _get_user_store() -> UserStore:
    return UserStore()


def _get_jwt_handler() -> JWTHandler:
    expiry = int(os.environ.get("PROWLRBOT_JWT_EXPIRY_MINUTES", "60"))
    return JWTHandler(secret_key=_JWT_SECRET, expiry_minutes=expiry)


async def get_current_user(request: Request) -> User:
    """Extract and validate the Bearer token, returning the authenticated user.

    Raises :class:`HTTPException` 401 when the token is missing or invalid.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )

    token = auth_header[7:]
    handler = _get_jwt_handler()
    try:
        payload = handler.decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    store = _get_user_store()
    user = store.get_user_by_id(payload.sub)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


def require_role(*roles: Role) -> Callable:
    """Return a FastAPI dependency that checks the user has one of *roles*."""

    async def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.role}' is not permitted; required one of: {[r.value for r in roles]}",
            )
        return user

    return _checker


def require_permission(*perms: Permission) -> Callable:
    """Return a FastAPI dependency that checks the user has *all* required permissions."""

    async def _checker(user: User = Depends(get_current_user)) -> User:
        # Effective permissions = explicit user perms + role defaults
        effective = set(user.permissions) | set(ROLE_PERMISSIONS.get(user.role, []))
        missing = [p for p in perms if p not in effective]
        if missing:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permissions: {[m.value for m in missing]}",
            )
        return user

    return _checker
