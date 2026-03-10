# -*- coding: utf-8 -*-
"""Tests for prowlrbot.monitor.notifications.webhook."""
import json

import pytest
import httpx

from prowlrbot.monitor.notifications.webhook import WebhookNotifier


@pytest.mark.asyncio
class TestWebhookNotifier:
    async def test_notify_success(self):
        received = {}

        def handler(req):
            received["body"] = json.loads(req.content)
            return httpx.Response(200)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)
        notifier = WebhookNotifier(url="https://hooks.example.com/notify", client=client)

        ok = await notifier.notify("my-monitor", "2 lines changed", "new content")
        assert ok is True
        assert received["body"]["monitor"] == "my-monitor"
        assert received["body"]["summary"] == "2 lines changed"
        assert received["body"]["content"] == "new content"
        assert "timestamp" in received["body"]
        await client.aclose()

    async def test_notify_with_headers(self):
        def handler(req):
            assert req.headers.get("X-Token") == "secret"
            return httpx.Response(200)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)
        notifier = WebhookNotifier(
            url="https://hooks.example.com/notify",
            headers={"X-Token": "secret"},
            client=client,
        )
        ok = await notifier.notify("test", "change")
        assert ok is True
        await client.aclose()

    async def test_notify_server_error(self):
        transport = httpx.MockTransport(lambda req: httpx.Response(500))
        client = httpx.AsyncClient(transport=transport)
        notifier = WebhookNotifier(url="https://hooks.example.com/notify", client=client)

        ok = await notifier.notify("test", "change")
        assert ok is False
        await client.aclose()

    async def test_notify_connection_error(self):
        def handler(req):
            raise httpx.ConnectError("connection refused")

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(transport=transport)
        notifier = WebhookNotifier(url="https://hooks.example.com/notify", client=client)

        ok = await notifier.notify("test", "change")
        assert ok is False
        await client.aclose()
