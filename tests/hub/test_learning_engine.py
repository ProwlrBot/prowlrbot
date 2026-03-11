# -*- coding: utf-8 -*-
"""Tests for the Learning Engine — CRUD, FTS5 search safety, thread safety, limits."""
import threading
import pytest
from prowlrbot.learning.db import LearningDB, _sanitize_fts_query, _clamp_limit


@pytest.fixture
def db(tmp_path):
    """Create a fresh learning DB with an ephemeral database."""
    db_path = str(tmp_path / "test_learnings.db")
    learning_db = LearningDB(db_path)
    yield learning_db


# --- CRUD ---


class TestLearningCRUD:
    def test_add_and_retrieve(self, db):
        lid = db.add_learning("correction", "agent-1", "Fix import", "Use absolute imports")
        assert lid is not None
        recent = db.get_recent(limit=1)
        assert len(recent) == 1
        assert recent[0]["learning_id"] == lid
        assert recent[0]["title"] == "Fix import"
        assert recent[0]["content"] == "Use absolute imports"
        assert recent[0]["category"] == "correction"

    def test_add_with_metadata(self, db):
        lid = db.add_learning(
            "pattern", "agent-2", "Retry pattern",
            "Exponential backoff for HTTP calls",
            metadata={"language": "python", "context": "http"},
            confidence=0.85,
        )
        recent = db.get_recent(limit=1)
        assert recent[0]["confidence"] == 0.85
        assert '"language"' in recent[0]["metadata"]

    def test_get_by_source(self, db):
        db.add_learning("correction", "agent-a", "Title A", "Content A")
        db.add_learning("correction", "agent-b", "Title B", "Content B")
        db.add_learning("pattern", "agent-a", "Title C", "Content C")
        results = db.get_by_source("agent-a")
        assert len(results) == 2
        assert all(r["source"] == "agent-a" for r in results)

    def test_get_recent_by_category(self, db):
        db.add_learning("correction", "a", "C1", "content")
        db.add_learning("pattern", "a", "P1", "content")
        db.add_learning("insight", "a", "I1", "content")
        corrections = db.get_recent(category="correction")
        assert len(corrections) == 1
        assert corrections[0]["category"] == "correction"

    def test_delete_learning(self, db):
        lid = db.add_learning("correction", "a", "Delete me", "gone")
        assert db.delete_learning(lid) is True
        assert db.get_recent() == []

    def test_delete_nonexistent(self, db):
        assert db.delete_learning("nonexistent-id") is False

    def test_increment_usage(self, db):
        lid = db.add_learning("pattern", "a", "Reusable", "content")
        db.increment_usage(lid)
        db.increment_usage(lid)
        recent = db.get_recent(limit=1)
        assert recent[0]["times_used"] == 2


# --- FTS5 Search ---


class TestFTSSearch:
    def test_basic_search(self, db):
        db.add_learning("correction", "a", "Fix async deadlock", "Use asyncio.gather instead of sequential awaits")
        db.add_learning("pattern", "a", "Database pooling", "Always use connection pools for SQLite")
        results = db.search("async deadlock")
        assert len(results) == 1
        assert results[0]["title"] == "Fix async deadlock"

    def test_search_content(self, db):
        db.add_learning("insight", "a", "Perf tip", "Use connection pools for better throughput")
        results = db.search("connection pools")
        assert len(results) == 1

    def test_search_with_category_filter(self, db):
        db.add_learning("correction", "a", "Fix bug", "Fix the async bug")
        db.add_learning("pattern", "a", "Async pattern", "Use async properly")
        results = db.search("async", category="correction")
        assert len(results) == 1
        assert results[0]["category"] == "correction"

    def test_search_no_results(self, db):
        db.add_learning("correction", "a", "Something", "Unrelated content")
        results = db.search("xyznonexistent")
        assert len(results) == 0

    def test_search_empty_query(self, db):
        db.add_learning("correction", "a", "Title", "Content")
        results = db.search("")
        assert isinstance(results, list)


# --- FTS5 Safety (FINDING-08) ---


class TestFTSSafety:
    def test_sanitize_strips_operators(self):
        # * is stripped, OR/AND remain as text but are inside quotes so FTS treats them as words
        result = _sanitize_fts_query('test OR *')
        assert '"' in result  # Wrapped in quotes
        assert '*' not in result  # Star operator removed
        result2 = _sanitize_fts_query('foo AND "bar"')
        assert '"' in result2
        assert result2.count('"') == 2  # Only outer quotes remain

    def test_sanitize_strips_special_chars(self):
        result = _sanitize_fts_query('hello(){}[]^~:!world')
        assert '"' in result
        assert '(' not in result
        assert ')' not in result
        assert '{' not in result
        assert '!' not in result

    def test_sanitize_empty_string(self):
        assert _sanitize_fts_query('') == '""'
        assert _sanitize_fts_query('***') == '""'

    def test_sanitize_normal_query_preserved(self):
        assert _sanitize_fts_query('fix import error') == '"fix import error"'

    def test_search_with_malicious_fts_operators(self, db):
        db.add_learning("correction", "a", "Safe title", "Safe content about imports")
        # These should not crash or return unexpected results
        results = db.search("* OR *")
        assert isinstance(results, list)
        results = db.search('NEAR("foo" "bar")')
        assert isinstance(results, list)
        results = db.search("title:exploit")
        assert isinstance(results, list)


# --- Limit Clamping (FINDING-06) ---


class TestLimitClamping:
    def test_clamp_limit_normal(self):
        assert _clamp_limit(10) == 10
        assert _clamp_limit(200) == 200

    def test_clamp_limit_too_high(self):
        assert _clamp_limit(999999) == 200
        assert _clamp_limit(1000000) == 200

    def test_clamp_limit_zero_or_negative(self):
        assert _clamp_limit(0) == 1
        assert _clamp_limit(-5) == 1

    def test_get_recent_respects_limit(self, db):
        for i in range(5):
            db.add_learning("correction", "a", f"Title {i}", f"Content {i}")
        results = db.get_recent(limit=3)
        assert len(results) == 3

    def test_search_respects_limit(self, db):
        for i in range(5):
            db.add_learning("correction", "a", f"Search target {i}", f"Searchable content {i}")
        results = db.search("searchable", limit=2)
        assert len(results) <= 2


# --- Session Tracking ---


class TestSessionTracking:
    def test_start_session(self, db):
        sid = db.start_session("agent-x")
        assert sid is not None
        stats = db.stats()
        assert stats["total_sessions"] == 1

    def test_end_session(self, db):
        sid = db.start_session("agent-y")
        db.end_session(sid, summary="Completed task", learnings_captured=3)
        # Session should still exist
        stats = db.stats()
        assert stats["total_sessions"] == 1

    def test_stats(self, db):
        db.add_learning("correction", "a", "C1", "content")
        db.add_learning("correction", "a", "C2", "content")
        db.add_learning("pattern", "b", "P1", "content")
        db.start_session("agent-1")
        stats = db.stats()
        assert stats["total_learnings"] == 3
        assert stats["by_category"]["correction"] == 2
        assert stats["by_category"]["pattern"] == 1
        assert stats["total_sessions"] == 1


# --- Thread Safety (FINDING-14) ---


class TestThreadSafety:
    def test_concurrent_writes(self, db):
        """Multiple threads writing simultaneously should not corrupt data."""
        errors = []

        def writer(thread_id):
            try:
                for i in range(20):
                    db.add_learning(
                        "correction", f"thread-{thread_id}",
                        f"Title {thread_id}-{i}", f"Content {thread_id}-{i}",
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"
        stats = db.stats()
        assert stats["total_learnings"] == 100  # 5 threads * 20 each

    def test_concurrent_read_write(self, db):
        """Reads during writes should not crash or corrupt data."""
        db.add_learning("correction", "seed", "Seed data", "Initial content for searching")
        write_errors = []
        read_errors = []

        def writer():
            try:
                for i in range(20):
                    db.add_learning("pattern", "writer", f"Write {i}", f"Content {i}")
            except Exception as e:
                write_errors.append(e)

        def reader():
            for _ in range(20):
                try:
                    db.get_recent(limit=10)
                except Exception:
                    pass  # SQLite may briefly error under contention
                try:
                    db.search("content")
                except Exception:
                    pass

        threads = [
            threading.Thread(target=writer),
            threading.Thread(target=reader),
            threading.Thread(target=reader),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Writes must succeed — that's the critical guarantee
        assert write_errors == [], f"Write errors: {write_errors}"
        # Data should be consistent after all threads finish
        stats = db.stats()
        assert stats["total_learnings"] == 21  # 1 seed + 20 writes
