# -*- coding: utf-8 -*-
"""ProwlrBot Learning Engine — agents that learn from experience.

Provides both a class-based API (``LearningDB``) and module-level convenience
functions (``init_db``, ``add_learning``, ``query_learnings``,
``search_learnings``) for hook scripts and one-off usage.
"""

from .db import (
    LearningDB,
    add_learning,
    init_db,
    query_learnings,
    search_learnings,
)

__all__ = [
    "LearningDB",
    "add_learning",
    "init_db",
    "query_learnings",
    "search_learnings",
]
