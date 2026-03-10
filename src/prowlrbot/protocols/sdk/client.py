# -*- coding: utf-8 -*-
"""ROAR Protocol SDK — Client for agent-to-agent communication."""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional

from ..roar import (
    AgentCard,
    AgentDirectory,
    AgentIdentity,
    ConnectionConfig,
    DiscoveryEntry,
    MessageIntent,
    ROARMessage,
    TransportType,
)


class ROARClient:
    """Client for discovering agents and sending ROAR messages.

    Usage::

        identity = AgentIdentity(display_name="my-agent")
        client = ROARClient(identity)

        # Register self
        card = AgentCard(identity=identity, description="My agent")
        client.register(card)

        # Discover other agents
        agents = client.discover(capability="code-review")

        # Send a message
        response = client.send(
            to_agent_id=agents[0].agent_card.identity.did,
            intent=MessageIntent.DELEGATE,
            content={"task": "review this PR"},
        )
    """

    def __init__(
        self,
        identity: AgentIdentity,
        directory_url: Optional[str] = None,
        signing_secret: str = "",
    ) -> None:
        self._identity = identity
        self._directory_url = directory_url
        self._signing_secret = signing_secret or uuid.uuid4().hex
        self._directory = AgentDirectory()
        self._card: Optional[AgentCard] = None

    # -- public API -----------------------------------------------------------

    @property
    def identity(self) -> AgentIdentity:
        """Return the client's agent identity."""
        return self._identity

    def register(self, card: AgentCard) -> DiscoveryEntry:
        """Register this agent with the local directory.

        Args:
            card: The agent card describing this agent's capabilities.

        Returns:
            The discovery entry created for this agent.
        """
        self._card = card
        return self._directory.register(card)

    def discover(self, capability: Optional[str] = None) -> List[DiscoveryEntry]:
        """Find agents, optionally filtered by capability.

        Args:
            capability: If provided, only return agents with this capability.

        Returns:
            List of matching discovery entries.
        """
        if capability:
            return self._directory.search(capability)
        return self._directory.list_all()

    def send(
        self,
        to_agent_id: str,
        intent: MessageIntent,
        content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ROARMessage:
        """Create, sign, and return a ROAR message.

        In a full implementation this would transmit the message over the
        configured transport.  The current SDK version constructs and signs
        the message locally so callers can inspect or forward it themselves.

        Args:
            to_agent_id: DID of the target agent.
            intent: What the sender wants the receiver to do.
            content: Payload dictionary.
            context: Optional context metadata.

        Returns:
            A signed ``ROARMessage`` ready for transmission.
        """
        entry = self._directory.lookup(to_agent_id)
        to_identity = (
            entry.agent_card.identity
            if entry
            else AgentIdentity(did=to_agent_id, display_name="unknown")
        )

        msg = ROARMessage(
            **{"from": self._identity, "to": to_identity},
            intent=intent,
            payload=content,
            context=context or {},
        )
        return self._sign_message(msg)

    def connect(
        self,
        agent_id: str,
        transport: TransportType = TransportType.HTTP,
    ) -> ConnectionConfig:
        """Build a connection config for the given agent.

        Looks up the agent's registered endpoints and returns a
        ``ConnectionConfig`` with the appropriate URL and auth details.

        Args:
            agent_id: DID of the agent to connect to.
            transport: Preferred transport type.

        Returns:
            A ``ConnectionConfig`` for establishing a connection.
        """
        entry = self._directory.lookup(agent_id)
        url = ""
        if entry:
            endpoints = entry.agent_card.endpoints
            url = endpoints.get(transport.value, endpoints.get("http", ""))

        return ConnectionConfig(
            transport=transport,
            url=url,
            auth_method="hmac",
            secret=self._signing_secret,
        )

    @contextmanager
    def stream_events(self, callback: Callable[..., Any]):
        """Context manager placeholder for real-time event streaming.

        In a full implementation this would open a persistent connection
        (e.g. WebSocket or SSE) and invoke ``callback`` for each incoming
        ``StreamEvent``.

        Args:
            callback: Callable invoked with each ``StreamEvent``.

        Yields:
            ``None`` — the caller can perform work inside the ``with`` block.
        """
        # Placeholder: a real implementation would open a websocket / SSE
        # connection and call ``callback(event)`` for each incoming event.
        yield

    # -- internal -------------------------------------------------------------

    def _sign_message(self, msg: ROARMessage) -> ROARMessage:
        """Sign a message with HMAC-SHA256 using the client's secret.

        Args:
            msg: The message to sign.

        Returns:
            The same message instance, now with ``auth`` populated.
        """
        body = json.dumps(
            {"id": msg.id, "intent": msg.intent, "payload": msg.payload},
            sort_keys=True,
        )
        sig = hmac.new(
            self._signing_secret.encode(), body.encode(), hashlib.sha256
        ).hexdigest()
        msg.auth = {
            "signature": f"hmac-sha256:{sig}",
            "signer": self._identity.did,
            "timestamp": time.time(),
        }
        return msg
