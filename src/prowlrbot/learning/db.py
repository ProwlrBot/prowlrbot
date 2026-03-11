# -*- coding: utf-8 -*-
"""Learning Engine database — stores corrections, preferences, and patterns.

Uses SQLite with FTS5 for fast full-text search across learnings.
Each learning is tagged by category and source for contextual retrieval.
"""

import json
import os
import re
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Max items returned by any list query
_MAX_LIMIT = 200

_SCHEMA = """
CREATE TABLE IF NOT EXISTS learnings (
    learning_id TEXT PRIMARY KEY,
    category    TEXT NOT NULL,  -- correction, preference, pattern, insight
    source      TEXT NOT NULL,  -- agent_id or 'user'
    title       TEXT NOT NULL,
    content     TEXT NOT NULL,
    metadata    TEXT DEFAULT '{}',
    confidence  REAL DEFAULT 1.0,
    times_used  INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_learnings_category ON learnings(category);
CREATE INDEX IF NOT EXISTS idx_learnings_source ON learnings(source);

CREATE VIRTUAL TABLE IF NOT EXISTS learnings_fts USING fts5(
    title, content, category,
    content=learnings,
    content_rowid=rowid
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS learnings_ai AFTER INSERT ON learnings BEGIN
    INSERT INTO learnings_fts(rowid, title, content, category)
    VALUES (new.rowid, new.title, new.content, new.category);
END;

CREATE TRIGGER IF NOT EXISTS learnings_ad AFTER DELETE ON learnings BEGIN
    INSERT INTO learnings_fts(learnings_fts, rowid, title, content, category)
    VALUES ('delete', old.rowid, old.title, old.content, old.category);
END;

CREATE TRIGGER IF NOT EXISTS learnings_au AFTER UPDATE ON learnings BEGIN
    INSERT INTO learnings_fts(learnings_fts, rowid, title, content, category)
    VALUES ('delete', old.rowid, old.title, old.content, old.category);
    INSERT INTO learnings_fts(rowid, title, content, category)
    VALUES (new.rowid, new.title, new.content, new.category);
END;

CREATE TABLE IF NOT EXISTS sessions (
    session_id  TEXT PRIMARY KEY,
    agent_id    TEXT NOT NULL,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    summary     TEXT DEFAULT '',
    learnings_captured INTEGER DEFAULT 0
);
"""


def _sanitize_fts_query(query: str) -> str:
    """Escape FTS5 special characters and wrap as phrase query."""
    sanitized = re.sub(r'[*"(){}[\]^~:!\\]', " ", query)
    sanitized = sanitized.strip()
    if not sanitized:
        return '""'
    return '"' + sanitized.replace('"', "") + '"'


def _clamp_limit(limit: int) -> int:
    return max(1, min(limit, _MAX_LIMIT))


class LearningDB:
    """SQLite-backed learning storage with FTS5 search.

    Thread-safe: all write operations are serialized via a lock.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base = os.path.expanduser("~/.prowlrbot")
            os.makedirs(base, exist_ok=True)
            db_path = os.path.join(base, "learnings.db")

        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        self._lock = threading.Lock()

    def add_learning(
        self,
        category: str,
        source: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> str:
        """Store a new learning. Returns the learning_id."""
        learning_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc).isoformat()
        with self._lock:
            self._conn.execute(
                """INSERT INTO learnings
                   (learning_id, category, source, title, content, metadata, confidence, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    learning_id,
                    category,
                    source,
                    title,
                    content,
                    json.dumps(metadata or {}),
                    confidence,
                    now,
                    now,
                ),
            )
            self._conn.commit()
        return learning_id

    def search(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Full-text search across learnings. Query is sanitized for FTS5 safety."""
        safe_query = _sanitize_fts_query(query)
        limit = _clamp_limit(limit)
        if category:
            rows = self._conn.execute(
                """SELECT l.* FROM learnings l
                   JOIN learnings_fts f ON l.rowid = f.rowid
                   WHERE learnings_fts MATCH ? AND l.category = ?
                   ORDER BY rank LIMIT ?""",
                (safe_query, category, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT l.* FROM learnings l
                   JOIN learnings_fts f ON l.rowid = f.rowid
                   WHERE learnings_fts MATCH ?
                   ORDER BY rank LIMIT ?""",
                (safe_query, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_recent(
        self, limit: int = 20, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get most recent learnings, optionally filtered by category."""
        limit = _clamp_limit(limit)
        if category:
            rows = self._conn.execute(
                "SELECT * FROM learnings WHERE category = ? ORDER BY updated_at DESC LIMIT ?",
                (category, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM learnings ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_by_source(self, source: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get learnings from a specific agent or user."""
        limit = _clamp_limit(limit)
        rows = self._conn.execute(
            "SELECT * FROM learnings WHERE source = ? ORDER BY updated_at DESC LIMIT ?",
            (source, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def increment_usage(self, learning_id: str) -> None:
        """Track that a learning was used in context injection."""
        with self._lock:
            self._conn.execute(
                "UPDATE learnings SET times_used = times_used + 1, updated_at = ? WHERE learning_id = ?",
                (datetime.now(tz=timezone.utc).isoformat(), learning_id),
            )
            self._conn.commit()

    def delete_learning(self, learning_id: str) -> bool:
        """Remove a learning."""
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM learnings WHERE learning_id = ?", (learning_id,)
            )
            self._conn.commit()
        return cur.rowcount > 0

    def start_session(self, agent_id: str) -> str:
        """Record the start of an agent session."""
        session_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                "INSERT INTO sessions (session_id, agent_id, started_at) VALUES (?, ?, ?)",
                (session_id, agent_id, datetime.now(tz=timezone.utc).isoformat()),
            )
            self._conn.commit()
        return session_id

    def end_session(
        self, session_id: str, summary: str = "", learnings_captured: int = 0
    ) -> None:
        """Record session end with summary."""
        with self._lock:
            self._conn.execute(
                "UPDATE sessions SET ended_at = ?, summary = ?, learnings_captured = ? WHERE session_id = ?",
                (
                    datetime.now(tz=timezone.utc).isoformat(),
                    summary,
                    learnings_captured,
                    session_id,
                ),
            )
            self._conn.commit()

    def stats(self) -> Dict[str, Any]:
        """Return learning engine statistics."""
        total = self._conn.execute("SELECT COUNT(*) FROM learnings").fetchone()[0]
        by_cat = self._conn.execute(
            "SELECT category, COUNT(*) as cnt FROM learnings GROUP BY category"
        ).fetchall()
        sessions = self._conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        return {
            "total_learnings": total,
            "by_category": {r["category"]: r["cnt"] for r in by_cat},
            "total_sessions": sessions,
        }
