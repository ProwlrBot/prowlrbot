# -*- coding: utf-8 -*-
"""JWT authentication and role-based access control."""

from .models import (
    AuthResponse,
    Permission,
    Role,
    ROLE_PERMISSIONS,
    TokenPayload,
    User,
)
from .jwt_handler import JWTHandler
from .store import UserStore
from .middleware import get_current_user, require_permission, require_role

__all__ = [
    "AuthResponse",
    "JWTHandler",
    "Permission",
    "Role",
    "ROLE_PERMISSIONS",
    "TokenPayload",
    "User",
    "UserStore",
    "get_current_user",
    "require_permission",
    "require_role",
]
