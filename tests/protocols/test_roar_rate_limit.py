# -*- coding: utf-8 -*-
"""Tests for ROAR router rate limiting."""

from __future__ import annotations

import time
import unittest

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from prowlrbot.protocols.roar import AgentIdentity, MessageIntent
from prowlrbot.protocols.sdk.router import TokenBucket, create_roar_router
from prowlrbot.protocols.sdk.server import ROARServer


def _make_server() -> ROARServer:
    """Create a test ROARServer."""
    identity = AgentIdentity(display_name="test-agent")
    server = ROARServer(identity)

    @server.on(MessageIntent.EXECUTE)
    async def handle(msg):
        from prowlrbot.protocols.roar import ROARMessage

        return ROARMessage(
            **{"from": server.identity, "to": msg.from_identity},
            intent=MessageIntent.RESPOND,
            payload={"result": "ok"},
        )

    return server


def _make_message() -> dict:
    """Create a valid ROAR message payload."""
    sender = AgentIdentity(display_name="sender")
    receiver = AgentIdentity(display_name="receiver")
    return {
        "from": sender.model_dump(),
        "to": receiver.model_dump(),
        "intent": MessageIntent.EXECUTE,
        "payload": {"action": "test"},
    }


class TestTokenBucket(unittest.TestCase):
    """Tests for the token bucket rate limiter."""

    def test_initial_tokens_available(self):
        bucket = TokenBucket(max_tokens=10, refill_rate=1.0)
        for _ in range(10):
            assert bucket.consume() is True

    def test_bucket_exhaustion(self):
        bucket = TokenBucket(max_tokens=3, refill_rate=0.0)
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is False

    def test_refill(self):
        bucket = TokenBucket(max_tokens=2, refill_rate=100.0)  # Fast refill
        bucket.consume()
        bucket.consume()
        time.sleep(0.05)  # Should refill ~5 tokens
        assert bucket.consume() is True

    def test_no_exceed_max(self):
        bucket = TokenBucket(max_tokens=2, refill_rate=1000.0)
        time.sleep(0.1)  # Would refill way more than max
        # Should only have max_tokens available
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is False


class TestRateLimitedRouter(unittest.TestCase):
    """Tests for rate limiting on the ROAR router."""

    def test_no_rate_limit_by_default(self):
        """With rate_limit=0, no limiting occurs."""
        server = _make_server()
        router = create_roar_router(server, rate_limit=0)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        for _ in range(50):
            resp = client.post("/roar/message", json=_make_message())
            assert resp.status_code == 200

    def test_rate_limit_returns_429(self):
        """Exceeding rate limit returns 429."""
        server = _make_server()
        # Very low rate limit: 3 requests per minute
        router = create_roar_router(server, rate_limit=3)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        # First 3 should succeed (burst capacity)
        for i in range(3):
            resp = client.post("/roar/message", json=_make_message())
            assert resp.status_code == 200, f"Request {i} failed unexpectedly"

        # 4th should be rate limited
        resp = client.post("/roar/message", json=_make_message())
        assert resp.status_code == 429
        data = resp.json()
        assert data.get("error") == "rate_limited"

    def test_rate_limit_on_events_endpoint(self):
        """Rate limiting applies to SSE /events endpoint too."""
        server = _make_server()
        router = create_roar_router(server, rate_limit=2)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        # Consume tokens
        client.post("/roar/message", json=_make_message())
        client.post("/roar/message", json=_make_message())

        # Events endpoint should be rate limited
        resp = client.get("/roar/events")
        assert resp.status_code == 429
        data = resp.json()
        assert data.get("error") == "rate_limited"

    def test_health_not_rate_limited(self):
        """Health endpoint is not rate limited."""
        server = _make_server()
        router = create_roar_router(server, rate_limit=2)
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)

        # Exhaust rate limit
        for _ in range(3):
            client.post("/roar/message", json=_make_message())

        # Health should still work
        resp = client.get("/roar/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


if __name__ == "__main__":
    unittest.main()
