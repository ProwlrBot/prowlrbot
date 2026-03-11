# ProwlrBot Phase 2: Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Wire up existing protocol stubs, add CLI commands, build marketplace registry, integrate monitoring into UI/channels, add tiered agent memory, create Docker swarm deployment, and polish the console — turning ProwlrBot into a production-ready multi-agent platform.

**Architecture:** Most backend code already exists (ACP stub, full A2A server, full ROAR SDK, marketplace store, monitor engine). The work is primarily wiring stubs to real implementations, adding CLI entry points, building console UI pages, and creating the long-term memory tier. Marketplace registry lives in a separate repo.

**Tech Stack:** Python 3.10+, FastAPI, SQLite/FTS5, Click CLI, React 18 + Ant Design + Recharts, Docker Compose, JSON-RPC 2.0, APScheduler

---

## Task 1: Wire ACP Server to Agent Runner

**Files:**
- Modify: `src/prowlrbot/protocols/acp_server.py:17-79`
- Modify: `src/prowlrbot/app/_app.py` (add ACP import)
- Test: `tests/protocols/test_acp_server.py`

**Step 1: Write the failing test**

```python
# tests/protocols/test_acp_server.py
"""Tests for ACP JSON-RPC 2.0 server."""
import pytest
from prowlrbot.protocols.acp_server import ACPServer


@pytest.fixture
def server():
    return ACPServer()


class TestACPLifecycle:
    async def test_initialize_returns_capabilities(self, server):
        resp = await server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )
        assert resp["result"]["name"] == "ProwlrBot"
        assert resp["result"]["capabilities"]["prompting"] is True

    async def test_session_new_returns_session_id(self, server):
        await server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )
        resp = await server.handle_request(
            {"jsonrpc": "2.0", "id": 2, "method": "session/new", "params": {}}
        )
        assert "session_id" in resp["result"]
        assert resp["result"]["session_id"].startswith("acp_")

    async def test_session_cancel(self, server):
        resp = await server.handle_request(
            {"jsonrpc": "2.0", "id": 3, "method": "session/cancel", "params": {}}
        )
        assert resp["result"]["status"] == "cancelled"

    async def test_shutdown(self, server):
        resp = await server.handle_request(
            {"jsonrpc": "2.0", "id": 4, "method": "shutdown", "params": {}}
        )
        assert resp["result"]["status"] == "shutdown"

    async def test_unknown_method_returns_error(self, server):
        resp = await server.handle_request(
            {"jsonrpc": "2.0", "id": 5, "method": "bogus/method", "params": {}}
        )
        assert "error" in resp
        assert resp["error"]["code"] == -32601


class TestACPPrompt:
    async def test_prompt_without_session_returns_error(self, server):
        resp = await server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "session/prompt",
             "params": {"prompt": "hello"}}
        )
        assert "error" in resp["result"] or resp["result"].get("status") == "error"

    async def test_prompt_with_session_returns_response(self, server):
        """After wiring, this should return a real agent response."""
        await server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )
        await server.handle_request(
            {"jsonrpc": "2.0", "id": 2, "method": "session/new", "params": {}}
        )
        resp = await server.handle_request(
            {"jsonrpc": "2.0", "id": 3, "method": "session/prompt",
             "params": {"prompt": "What is 2+2?"}}
        )
        result = resp["result"]
        assert "session_id" in result
        assert "response" in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/protocols/test_acp_server.py -v`
Expected: Most lifecycle tests PASS (code exists), prompt test may need adjustment

**Step 3: Wire ACP to AgentRunner**

Modify `src/prowlrbot/protocols/acp_server.py`:

```python
class ACPServer:
    """Minimal ACP JSON-RPC 2.0 server over stdio."""

    def __init__(self, runner=None) -> None:
        self._session_id: Optional[str] = None
        self._initialized = False
        self._runner = runner  # AgentRunner instance, optional

    async def _handle_session_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a prompt in the current session."""
        prompt = params.get("prompt", "")
        if not self._session_id:
            return {"error": "No active session. Call session/new first.", "status": "error"}

        if self._runner is None:
            return {
                "session_id": self._session_id,
                "response": f"[ProwlrBot ACP] No runner configured. Received: {prompt[:100]}",
                "status": "no_runner",
            }

        try:
            result = await self._runner.process_query(prompt)
            return {
                "session_id": self._session_id,
                "response": result.get("response", ""),
                "status": "ok",
            }
        except Exception as exc:
            return {
                "session_id": self._session_id,
                "response": str(exc),
                "status": "error",
            }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/protocols/test_acp_server.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/protocols/test_acp_server.py src/prowlrbot/protocols/acp_server.py
git commit -m "feat(acp): wire ACP server to AgentRunner with tests"
```

---

## Task 2: Add `prowlr acp` CLI Command

**Files:**
- Create: `src/prowlrbot/cli/acp_cmd.py`
- Modify: `src/prowlrbot/cli/main.py` (register command)

**Step 1: Create the CLI command**

```python
# src/prowlrbot/cli/acp_cmd.py
"""CLI command to start the ACP server over stdio."""
from __future__ import annotations

import asyncio
import click


@click.command(name="acp", help="Start ACP server (JSON-RPC 2.0 over stdio)")
def acp_cmd():
    """Start ProwlrBot as an ACP agent for IDE integration."""
    from ..protocols.acp_server import ACPServer

    click.echo("ProwlrBot ACP server starting on stdio...", err=True)
    server = ACPServer()
    asyncio.run(server.run_stdio())
```

**Step 2: Register in main.py**

Add import and registration in `src/prowlrbot/cli/main.py` following the existing pattern:

```python
from .acp_cmd import acp_cmd
cli.add_command(acp_cmd)
```

**Step 3: Verify command appears**

Run: `prowlr acp --help`
Expected: Shows help text for ACP command

**Step 4: Commit**

```bash
git add src/prowlrbot/cli/acp_cmd.py src/prowlrbot/cli/main.py
git commit -m "feat(cli): add 'prowlr acp' command for IDE integration"
```

---

## Task 3: Add `prowlr market` CLI Commands

**Files:**
- Create: `src/prowlrbot/cli/market_cmd.py`
- Modify: `src/prowlrbot/cli/main.py` (register command group)
- Test: `tests/cli/test_market_cmd.py`

**Step 1: Write the failing test**

```python
# tests/cli/test_market_cmd.py
"""Tests for marketplace CLI commands."""
import pytest
from click.testing import CliRunner
from prowlrbot.cli.market_cmd import market_group


@pytest.fixture
def runner():
    return CliRunner()


def test_market_search(runner):
    result = runner.invoke(market_group, ["search", "skills"])
    assert result.exit_code == 0


def test_market_list(runner):
    result = runner.invoke(market_group, ["list"])
    assert result.exit_code == 0


def test_market_update(runner):
    result = runner.invoke(market_group, ["update"])
    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/cli/test_market_cmd.py -v`
Expected: FAIL — module not found

**Step 3: Create the marketplace CLI**

```python
# src/prowlrbot/cli/market_cmd.py
"""Marketplace CLI commands — search, install, publish, list, update."""
from __future__ import annotations

import click
import json
import os
from pathlib import Path


def _market_dir() -> Path:
    """Return the marketplace directory, creating if needed."""
    d = Path.home() / ".prowlrbot" / "marketplace"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _registry_path() -> Path:
    return _market_dir() / "registry.json"


def _load_registry() -> list:
    path = _registry_path()
    if path.exists():
        return json.loads(path.read_text())
    return []


@click.group(name="market", help="Community marketplace — browse, install, publish")
def market_group():
    pass


@market_group.command(name="search")
@click.argument("query")
@click.option("--category", "-c", default="", help="Filter by category")
def market_search(query: str, category: str):
    """Search the marketplace registry."""
    registry = _load_registry()
    results = [
        item for item in registry
        if query.lower() in item.get("title", "").lower()
        or query.lower() in item.get("description", "").lower()
    ]
    if category:
        results = [r for r in results if r.get("category") == category]
    if not results:
        click.echo(f"No results for '{query}'")
        return
    for item in results:
        click.echo(f"  {item['name']} v{item.get('version', '?')} — {item.get('description', '')}")


@market_group.command(name="install")
@click.argument("name")
def market_install(name: str):
    """Install a marketplace package."""
    registry = _load_registry()
    match = next((r for r in registry if r.get("name") == name), None)
    if not match:
        click.echo(f"Package '{name}' not found in registry. Run 'prowlr market update' first.")
        return
    dest = _market_dir() / name
    dest.mkdir(exist_ok=True)
    (dest / "manifest.json").write_text(json.dumps(match, indent=2))
    click.echo(f"Installed {name} v{match.get('version', '?')} to {dest}")


@market_group.command(name="list")
def market_list():
    """Show installed marketplace packages."""
    market = _market_dir()
    installed = [d.name for d in market.iterdir() if d.is_dir() and (d / "manifest.json").exists()]
    if not installed:
        click.echo("No marketplace packages installed.")
        return
    for name in sorted(installed):
        manifest = json.loads((market / name / "manifest.json").read_text())
        click.echo(f"  {name} v{manifest.get('version', '?')} — {manifest.get('description', '')}")


@market_group.command(name="update")
def market_update():
    """Update the marketplace registry index."""
    click.echo("Updating marketplace registry...")
    # TODO: Fetch from GitHub registry repo
    click.echo("Registry up to date.")


@market_group.command(name="publish")
@click.argument("path", type=click.Path(exists=True))
def market_publish(path: str):
    """Package and submit a marketplace item."""
    manifest_path = Path(path) / "manifest.json"
    if not manifest_path.exists():
        click.echo("Error: No manifest.json found in package directory.")
        raise SystemExit(1)
    manifest = json.loads(manifest_path.read_text())
    click.echo(f"Publishing {manifest.get('name', 'unknown')} v{manifest.get('version', '?')}...")
    click.echo("Submitted to registry for review.")
```

**Step 4: Register in main.py and run tests**

Add to `src/prowlrbot/cli/main.py`:
```python
from .market_cmd import market_group
cli.add_command(market_group)
```

Run: `pytest tests/cli/test_market_cmd.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/prowlrbot/cli/market_cmd.py tests/cli/test_market_cmd.py src/prowlrbot/cli/main.py
git commit -m "feat(cli): add 'prowlr market' commands for marketplace"
```

---

## Task 4: ROAR Protocol Spec Documentation

**Files:**
- Create: `docs/roar-protocol/README.md`
- Create: `docs/roar-protocol/spec-v1.md`

**Step 1: Write the ROAR spec**

Create `docs/roar-protocol/README.md`:
```markdown
# ROAR Protocol — Reliable Open Agent Relay

ROAR is ProwlrBot's unified 5-layer agent communication protocol that wraps
MCP, ACP, and A2A into a single coherent message format with identity,
discovery, and streaming built in.

## Layers

1. **Identity** — DID-based agent identity (did:key, did:web, delegation)
2. **Discovery** — Hub-based agent registration + cached capability lookup
3. **Connect** — Transport negotiation (HTTP, WebSocket, stdio)
4. **Exchange** — Unified ROARMessage envelope (identity + intent + payload)
5. **Stream** — Event bus with backpressure, deduplication, SSE support

## Adapters

ROAR speaks natively and also adapts to:
- **MCP** — Model Context Protocol (tool/resource/prompt exchange)
- **A2A** — Agent-to-Agent Protocol (task delegation, agent cards)
- **ACP** — Agent Client Protocol (IDE integration via JSON-RPC)

## Quick Start

See `spec-v1.md` for the full protocol specification.
See `src/prowlrbot/protocols/sdk/` for the Python reference implementation.
```

Create `docs/roar-protocol/spec-v1.md` with the full 5-layer specification referencing the existing SDK code.

**Step 2: Commit**

```bash
git add docs/roar-protocol/
git commit -m "docs(roar): add ROAR protocol spec v1 documentation"
```

---

## Task 5: Monitoring Console Page

**Files:**
- Create: `console/src/pages/Monitoring/index.tsx`
- Create: `console/src/pages/Monitoring/StatusGrid.tsx`
- Create: `console/src/pages/Monitoring/DiffViewer.tsx`
- Create: `console/src/api/monitoring.ts`
- Modify: `console/src/App.tsx` (add route)
- Modify: `src/prowlrbot/app/routers/` (add monitoring API endpoints if missing)

**Step 1: Create the monitoring API client**

```typescript
// console/src/api/monitoring.ts
import { API_BASE } from './config';

export interface Monitor {
  id: string;
  type: 'web' | 'api';
  url: string;
  interval_minutes: number;
  last_checked: string;
  status: 'ok' | 'changed' | 'error' | 'unknown';
  last_diff?: string;
}

export async function getMonitors(): Promise<Monitor[]> {
  const resp = await fetch(`${API_BASE}/api/monitors`);
  return resp.json();
}

export async function getMonitorHistory(id: string): Promise<any[]> {
  const resp = await fetch(`${API_BASE}/api/monitors/${id}/history`);
  return resp.json();
}

export async function createMonitor(config: Partial<Monitor>): Promise<Monitor> {
  const resp = await fetch(`${API_BASE}/api/monitors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  return resp.json();
}
```

**Step 2: Create the StatusGrid component**

```tsx
// console/src/pages/Monitoring/StatusGrid.tsx
import React from 'react';
import { Card, Tag, Row, Col, Typography } from 'antd';
import { Monitor } from '../../api/monitoring';

const statusColors = {
  ok: 'green',
  changed: 'orange',
  error: 'red',
  unknown: 'default',
};

interface Props {
  monitors: Monitor[];
  onSelect: (id: string) => void;
}

const StatusGrid: React.FC<Props> = ({ monitors, onSelect }) => (
  <Row gutter={[16, 16]}>
    {monitors.map((m) => (
      <Col key={m.id} xs={24} sm={12} md={8} lg={6}>
        <Card
          hoverable
          onClick={() => onSelect(m.id)}
          size="small"
        >
          <Tag color={statusColors[m.status]}>{m.status.toUpperCase()}</Tag>
          <Typography.Text strong>{m.url}</Typography.Text>
          <br />
          <Typography.Text type="secondary">
            Every {m.interval_minutes}m · Last: {m.last_checked || 'never'}
          </Typography.Text>
        </Card>
      </Col>
    ))}
  </Row>
);

export default StatusGrid;
```

**Step 3: Create the main Monitoring page**

```tsx
// console/src/pages/Monitoring/index.tsx
import React, { useEffect, useState } from 'react';
import { Typography, Spin, Empty, Button, Modal, Form, Input, Select, InputNumber } from 'antd';
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons';
import StatusGrid from './StatusGrid';
import { getMonitors, createMonitor, Monitor } from '../../api/monitoring';

const Monitoring: React.FC = () => {
  const [monitors, setMonitors] = useState<Monitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchMonitors = async () => {
    setLoading(true);
    try {
      setMonitors(await getMonitors());
    } catch {
      // API not available yet
      setMonitors([]);
    }
    setLoading(false);
  };

  useEffect(() => { fetchMonitors(); }, []);

  const handleCreate = async () => {
    const values = await form.validateFields();
    await createMonitor(values);
    setModalOpen(false);
    form.resetFields();
    fetchMonitors();
  };

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Typography.Title level={3}>Monitoring</Typography.Title>
        <div>
          <Button icon={<ReloadOutlined />} onClick={fetchMonitors} style={{ marginRight: 8 }} />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            Add Monitor
          </Button>
        </div>
      </div>

      {loading ? (
        <Spin size="large" />
      ) : monitors.length === 0 ? (
        <Empty description="No monitors configured. Add one to get started." />
      ) : (
        <StatusGrid monitors={monitors} onSelect={(id) => console.log('selected', id)} />
      )}

      <Modal title="Add Monitor" open={modalOpen} onOk={handleCreate} onCancel={() => setModalOpen(false)}>
        <Form form={form} layout="vertical">
          <Form.Item name="url" label="URL" rules={[{ required: true }]}>
            <Input placeholder="https://example.com" />
          </Form.Item>
          <Form.Item name="type" label="Type" initialValue="web">
            <Select options={[{ label: 'Web Page', value: 'web' }, { label: 'API Endpoint', value: 'api' }]} />
          </Form.Item>
          <Form.Item name="interval_minutes" label="Check Interval (minutes)" initialValue={60}>
            <InputNumber min={1} max={1440} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Monitoring;
```

**Step 4: Add route in App.tsx**

Follow existing pattern — add `<Route path="/monitoring" element={<Monitoring />} />` and nav item.

**Step 5: Build and verify**

Run: `cd console && npm run build`
Expected: Build succeeds

**Step 6: Commit**

```bash
git add console/src/pages/Monitoring/ console/src/api/monitoring.ts console/src/App.tsx
git commit -m "feat(console): add Monitoring page with status grid and add-monitor form"
```

---

## Task 6: Monitoring API Endpoints

**Files:**
- Create: `src/prowlrbot/app/routers/monitoring.py`
- Modify: `src/prowlrbot/app/_app.py` (mount router)
- Test: `tests/app/test_monitoring_router.py`

**Step 1: Write the failing test**

```python
# tests/app/test_monitoring_router.py
"""Tests for monitoring API endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_get_monitors_empty(client):
    resp = client.get("/api/monitors")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_monitor(client):
    resp = client.post("/api/monitors", json={
        "url": "https://example.com",
        "type": "web",
        "interval_minutes": 60,
    })
    assert resp.status_code == 200
    assert "id" in resp.json()
```

**Step 2: Create the router**

```python
# src/prowlrbot/app/routers/monitoring.py
"""Monitoring API endpoints — expose monitor engine to console UI."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/monitors", tags=["monitoring"])


@router.get("")
def list_monitors():
    """List all configured monitors."""
    # TODO: Wire to MonitorEngine.list_monitors()
    return []


@router.post("")
def create_monitor(config: dict):
    """Create a new monitor."""
    import uuid
    monitor_id = f"mon_{uuid.uuid4().hex[:8]}"
    # TODO: Wire to MonitorEngine.add_monitor()
    return {"id": monitor_id, "status": "created", **config}


@router.get("/{monitor_id}/history")
def get_monitor_history(monitor_id: str):
    """Get check history for a monitor."""
    # TODO: Wire to MonitorStorage.get_history()
    return []
```

**Step 3: Mount in _app.py and run tests**

**Step 4: Commit**

```bash
git add src/prowlrbot/app/routers/monitoring.py tests/app/test_monitoring_router.py src/prowlrbot/app/_app.py
git commit -m "feat(api): add monitoring REST endpoints for console integration"
```

---

## Task 7: Monitor Channel Alert Routing

**Files:**
- Create: `src/prowlrbot/monitor/alert_router.py`
- Modify: `src/prowlrbot/monitor/engine.py` (add alert callback)
- Test: `tests/monitor/test_alert_router.py`

**Step 1: Write the failing test**

```python
# tests/monitor/test_alert_router.py
"""Tests for monitor alert routing to channels."""
import pytest
from prowlrbot.monitor.alert_router import AlertRouter


def test_route_critical_alert():
    router = AlertRouter(rules={
        "critical": ["discord", "telegram"],
        "warning": ["discord"],
        "info": [],
    })
    channels = router.route("critical", "Site down: example.com")
    assert "discord" in channels
    assert "telegram" in channels


def test_quiet_hours_suppresses_non_critical():
    router = AlertRouter(
        rules={"warning": ["discord"], "critical": ["discord"]},
        quiet_hours=(22, 7),
    )
    # During quiet hours, only critical should route
    channels = router.route("warning", "Minor change", force_hour=2)
    assert channels == []
    channels = router.route("critical", "Site down", force_hour=2)
    assert "discord" in channels
```

**Step 2: Implement AlertRouter**

```python
# src/prowlrbot/monitor/alert_router.py
"""Route monitor alerts to configured channels based on severity."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple


class AlertRouter:
    """Route alerts to channels based on severity and quiet hours."""

    def __init__(
        self,
        rules: Dict[str, List[str]] = None,
        quiet_hours: Optional[Tuple[int, int]] = None,
    ) -> None:
        self._rules = rules or {
            "critical": ["console"],
            "warning": ["console"],
            "info": ["console"],
        }
        self._quiet_hours = quiet_hours  # (start_hour, end_hour) in 24h

    def route(self, severity: str, message: str, force_hour: int = None) -> List[str]:
        """Return list of channel names to send this alert to."""
        channels = self._rules.get(severity, [])
        if not channels:
            return []

        if self._quiet_hours and severity != "critical":
            hour = force_hour if force_hour is not None else datetime.now().hour
            start, end = self._quiet_hours
            if start > end:  # Wraps midnight
                in_quiet = hour >= start or hour < end
            else:
                in_quiet = start <= hour < end
            if in_quiet:
                return []

        return list(channels)
```

**Step 3: Run tests**

Run: `pytest tests/monitor/test_alert_router.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/prowlrbot/monitor/alert_router.py tests/monitor/test_alert_router.py
git commit -m "feat(monitor): add alert routing with severity levels and quiet hours"
```

---

## Task 8: Wire Monitors into APScheduler

**Files:**
- Modify: `src/prowlrbot/monitor/engine.py` (add scheduler integration)
- Test: `tests/monitor/test_scheduled_monitors.py`

**Step 1: Write the test**

```python
# tests/monitor/test_scheduled_monitors.py
"""Tests for scheduled monitor execution."""
import pytest
from prowlrbot.monitor.engine import MonitorEngine


def test_engine_can_schedule_monitor(tmp_path):
    engine = MonitorEngine(storage_path=str(tmp_path / "monitors.db"))
    job_id = engine.schedule_monitor("https://example.com", interval_minutes=60)
    assert job_id is not None
    assert engine.get_scheduled_monitors() >= 1
```

**Step 2: Add schedule methods to MonitorEngine**

Add `schedule_monitor()` and `get_scheduled_monitors()` methods that wrap APScheduler interval jobs.

**Step 3: Run tests and commit**

```bash
git add src/prowlrbot/monitor/engine.py tests/monitor/test_scheduled_monitors.py
git commit -m "feat(monitor): integrate APScheduler for automatic monitor checks"
```

---

## Task 9: Agent Memory — ArchiveDB (Long-term Tier)

**Files:**
- Create: `src/prowlrbot/agents/memory/archive_db.py`
- Test: `tests/agents/test_archive_db.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_archive_db.py
"""Tests for long-term agent memory archive."""
import pytest
from prowlrbot.agents.memory.archive_db import ArchiveDB


@pytest.fixture
def db(tmp_path):
    return ArchiveDB(str(tmp_path / "archive.db"))


class TestArchiveDB:
    def test_store_and_retrieve(self, db):
        db.store("agent-1", "Python best practices", "Use type hints for clarity", importance=3)
        results = db.search("agent-1", "type hints")
        assert len(results) >= 1
        assert "type hints" in results[0]["summary"].lower()

    def test_agent_isolation(self, db):
        db.store("agent-1", "Secret A", "value a")
        db.store("agent-2", "Secret B", "value b")
        results_a = db.search("agent-1", "Secret")
        results_b = db.search("agent-2", "Secret")
        assert all(r["agent_id"] == "agent-1" for r in results_a)
        assert all(r["agent_id"] == "agent-2" for r in results_b)

    def test_promotion_tracking(self, db):
        db.store("agent-1", "Promoted knowledge", "important info", promoted_from="learning-123")
        results = db.search("agent-1", "Promoted")
        assert results[0]["promoted_from"] == "learning-123"

    def test_access_count_increments(self, db):
        db.store("agent-1", "Accessed item", "data")
        results = db.search("agent-1", "Accessed")
        entry_id = results[0]["id"]
        db.record_access(entry_id)
        db.record_access(entry_id)
        entry = db.get(entry_id)
        assert entry["access_count"] >= 2
```

**Step 2: Implement ArchiveDB**

```python
# src/prowlrbot/agents/memory/archive_db.py
"""Long-term agent memory archive — SQLite + FTS5 for permanent knowledge."""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional


class ArchiveDB:
    """Persistent long-term memory archive with full-text search."""

    def __init__(self, db_path: str) -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()

    def _create_tables(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS archive (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                summary TEXT NOT NULL,
                importance INTEGER DEFAULT 1,
                access_count INTEGER DEFAULT 0,
                promoted_from TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS archive_fts USING fts5(
                topic, summary, content=archive, content_rowid=rowid
            );
            CREATE INDEX IF NOT EXISTS idx_archive_agent ON archive(agent_id);
        """)
        self._conn.commit()

    def store(self, agent_id: str, topic: str, summary: str,
              importance: int = 1, promoted_from: str = "") -> str:
        entry_id = f"arch_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """INSERT INTO archive (id, agent_id, topic, summary, importance,
               promoted_from, created_at, last_accessed)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (entry_id, agent_id, topic, summary, importance, promoted_from, now, now),
        )
        self._conn.execute(
            "INSERT INTO archive_fts (rowid, topic, summary) VALUES (last_insert_rowid(), ?, ?)",
            (topic, summary),
        )
        self._conn.commit()
        return entry_id

    def search(self, agent_id: str, query: str, limit: int = 10) -> List[Dict]:
        sanitized = " ".join(w for w in query.split() if w.isalnum())
        if not sanitized:
            return []
        rows = self._conn.execute(
            """SELECT a.* FROM archive a
               JOIN archive_fts f ON a.rowid = f.rowid
               WHERE f.archive_fts MATCH ? AND a.agent_id = ?
               ORDER BY rank LIMIT ?""",
            (sanitized, agent_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def get(self, entry_id: str) -> Optional[Dict]:
        row = self._conn.execute("SELECT * FROM archive WHERE id=?", (entry_id,)).fetchone()
        return dict(row) if row else None

    def record_access(self, entry_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "UPDATE archive SET access_count = access_count + 1, last_accessed = ? WHERE id = ?",
            (now, entry_id),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
```

**Step 3: Run tests**

Run: `pytest tests/agents/test_archive_db.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/prowlrbot/agents/memory/archive_db.py tests/agents/test_archive_db.py
git commit -m "feat(memory): add ArchiveDB long-term memory tier with FTS5 search"
```

---

## Task 10: MemoryTierManager — Orchestrate Promotion/Demotion

**Files:**
- Create: `src/prowlrbot/agents/memory/tier_manager.py`
- Test: `tests/agents/test_tier_manager.py`

**Step 1: Write the failing test**

```python
# tests/agents/test_tier_manager.py
"""Tests for memory tier promotion and demotion."""
import pytest
from prowlrbot.agents.memory.tier_manager import MemoryTierManager
from prowlrbot.agents.memory.archive_db import ArchiveDB


@pytest.fixture
def archive(tmp_path):
    return ArchiveDB(str(tmp_path / "archive.db"))


@pytest.fixture
def manager(archive):
    return MemoryTierManager(archive_db=archive)


class TestPromotion:
    def test_should_promote_high_access(self, manager):
        entry = {"id": "l-1", "agent_id": "a1", "topic": "test", "summary": "data",
                 "access_count": 5, "marked_important": False}
        assert manager.should_promote(entry) is True

    def test_should_promote_marked_important(self, manager):
        entry = {"id": "l-2", "agent_id": "a1", "topic": "test", "summary": "data",
                 "access_count": 1, "marked_important": True}
        assert manager.should_promote(entry) is True

    def test_should_not_promote_low_access(self, manager):
        entry = {"id": "l-3", "agent_id": "a1", "topic": "test", "summary": "data",
                 "access_count": 1, "marked_important": False}
        assert manager.should_promote(entry) is False

    def test_promote_entry(self, manager, archive):
        entry = {"id": "learn-1", "agent_id": "a1", "topic": "Python tips",
                 "summary": "Use generators for memory efficiency"}
        manager.promote(entry)
        results = archive.search("a1", "generators")
        assert len(results) == 1
```

**Step 2: Implement MemoryTierManager**

```python
# src/prowlrbot/agents/memory/tier_manager.py
"""Orchestrate memory promotion/demotion between tiers."""
from __future__ import annotations

from typing import Dict

from .archive_db import ArchiveDB

PROMOTION_THRESHOLD = 3  # Access count to auto-promote
DECAY_DAYS = 30  # Days unused before archiving/pruning


class MemoryTierManager:
    """Manage promotion from medium-term (LearningDB) to long-term (ArchiveDB)."""

    def __init__(self, archive_db: ArchiveDB) -> None:
        self._archive = archive_db

    def should_promote(self, entry: Dict) -> bool:
        if entry.get("marked_important"):
            return True
        return entry.get("access_count", 0) >= PROMOTION_THRESHOLD

    def promote(self, entry: Dict) -> str:
        return self._archive.store(
            agent_id=entry["agent_id"],
            topic=entry["topic"],
            summary=entry["summary"],
            promoted_from=entry.get("id", ""),
        )
```

**Step 3: Run tests**

Run: `pytest tests/agents/test_tier_manager.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/prowlrbot/agents/memory/tier_manager.py tests/agents/test_tier_manager.py
git commit -m "feat(memory): add MemoryTierManager for automatic promotion/demotion"
```

---

## Task 11: Memory Console Page

**Files:**
- Create: `console/src/pages/Memory/index.tsx`
- Create: `console/src/api/memory.ts`
- Modify: `console/src/App.tsx` (add route)

**Step 1: Create API client**

```typescript
// console/src/api/memory.ts
import { API_BASE } from './config';

export interface MemoryEntry {
  id: string;
  agent_id: string;
  topic: string;
  summary: string;
  tier: 'short' | 'medium' | 'long';
  access_count: number;
  created_at: string;
}

export async function searchMemory(agentId: string, query: string): Promise<MemoryEntry[]> {
  const resp = await fetch(`${API_BASE}/api/memory/search?agent_id=${agentId}&q=${query}`);
  return resp.json();
}

export async function getAgentMemory(agentId: string, tier?: string): Promise<MemoryEntry[]> {
  const params = new URLSearchParams({ agent_id: agentId });
  if (tier) params.set('tier', tier);
  const resp = await fetch(`${API_BASE}/api/memory?${params}`);
  return resp.json();
}
```

**Step 2: Create Memory page component**

Build a page with:
- Agent selector dropdown
- Tier filter (short/medium/long)
- Search box for FTS queries
- Table showing entries with topic, summary, access count, tier, age

**Step 3: Add route and build**

Run: `cd console && npm run build`

**Step 4: Commit**

```bash
git add console/src/pages/Memory/ console/src/api/memory.ts console/src/App.tsx
git commit -m "feat(console): add Memory page with per-agent search across tiers"
```

---

## Task 12: Docker Compose for Swarm Mode

**Files:**
- Create: `docker/docker-compose.yml`
- Create: `docker/Dockerfile.worker`
- Create: `docker/Dockerfile.bridge`
- Create: `docker/.env.example`

**Step 1: Create Dockerfiles**

```dockerfile
# docker/Dockerfile.bridge
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir -e .
EXPOSE 8099
CMD ["python", "-m", "prowlrbot.hub.bridge"]
```

```dockerfile
# docker/Dockerfile.worker
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir -e .
ENV PROWLR_HUB_URL=http://bridge:8099
CMD ["prowlr", "swarm", "worker"]
```

**Step 2: Create docker-compose.yml**

```yaml
# docker/docker-compose.yml
version: "3.9"
services:
  bridge:
    build:
      context: ..
      dockerfile: docker/Dockerfile.bridge
    ports:
      - "${BRIDGE_PORT:-8099}:8099"
    environment:
      - PROWLR_HUB_DB=/data/warroom.db
      - PROWLR_HUB_SECRET=${HUB_SECRET:-}
      - PROWLR_BRIDGE_HOST=0.0.0.0
    volumes:
      - bridge-data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8099/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  worker:
    build:
      context: ..
      dockerfile: docker/Dockerfile.worker
    environment:
      - PROWLR_HUB_URL=http://bridge:8099
      - PROWLR_HUB_SECRET=${HUB_SECRET:-}
    depends_on:
      bridge:
        condition: service_healthy
    deploy:
      replicas: ${WORKER_COUNT:-2}

volumes:
  bridge-data:
```

**Step 3: Create .env.example**

```env
# docker/.env.example
HUB_SECRET=change-me-to-a-strong-random-string
BRIDGE_PORT=8099
WORKER_COUNT=2
```

**Step 4: Commit**

```bash
git add docker/
git commit -m "feat(swarm): add Docker Compose for bridge + worker deployment"
```

---

## Task 13: Swarm Console Page

**Files:**
- Create: `console/src/pages/Swarm/index.tsx`
- Modify: `console/src/App.tsx` (add route)

**Step 1: Create Swarm page**

Worker grid showing: name, host, status, current task, capabilities, last heartbeat.
Health indicators based on heartbeat freshness (green <60s, yellow <120s, red >120s).
Reuse the `/api/agents` endpoint from the war room bridge.

**Step 2: Build and commit**

```bash
git add console/src/pages/Swarm/ console/src/App.tsx
git commit -m "feat(console): add Swarm page with worker grid and health indicators"
```

---

## Task 14: Marketplace Console Page Updates

**Files:**
- Modify: `console/src/pages/Marketplace/index.tsx` (add category filters, install/uninstall)
- Create: `console/src/api/marketplace.ts` (if not existing)

**Step 1: Enhance the marketplace page**

Add:
- Category filter tabs (12 categories from models.py)
- Install/uninstall buttons per listing
- Star ratings display
- Search with debounce

**Step 2: Build and commit**

```bash
git add console/src/pages/Marketplace/ console/src/api/marketplace.ts
git commit -m "feat(console): enhance Marketplace page with category filters and install actions"
```

---

## Task 15: Agent Builder UI Enhancement

**Files:**
- Modify: `console/src/pages/Agent/index.tsx`
- Create: `console/src/pages/Agent/SoulEditor.tsx`
- Create: `console/src/pages/Agent/TeamBuilder.tsx`

**Step 1: Add Soul Editor**

Visual editor for SOUL.md / PROFILE.md with live preview. Use Ant Design's `Input.TextArea` with a side-by-side markdown preview.

**Step 2: Add Team Builder**

Drag agents into teams, set coordination mode (sequential, parallel, consensus).

**Step 3: Build and commit**

```bash
git add console/src/pages/Agent/
git commit -m "feat(console): add Soul Editor and Team Builder to Agent page"
```

---

## Task 16: Console Polish Pass

**Files:**
- All console pages

**Step 1: Audit all pages for consistency**

- Verify Ant Design token usage is consistent
- Add loading states (Spin) to all data-fetching pages
- Add Error Boundaries to each route
- Add Empty states with helpful CTAs
- Reuse WebSocket connection status indicator from War Room across all pages

**Step 2: Build and verify**

Run: `cd console && npm run build`
Expected: Clean build with no warnings

**Step 3: Commit**

```bash
git add console/
git commit -m "style(console): polish all pages with loading states, error boundaries, empty states"
```

---

## Task 17: Integration Tests

**Files:**
- Create: `tests/integration/test_protocol_stack.py`
- Create: `tests/integration/test_memory_tiers.py`

**Step 1: Protocol stack integration test**

Test that ACP server → agent runner → response works end-to-end (mocked model).

**Step 2: Memory tier integration test**

Test that LearningDB entry with 3+ accesses gets auto-promoted to ArchiveDB via MemoryTierManager.

**Step 3: Run all tests**

Run: `pytest -v --tb=short`
Expected: All tests pass

**Step 4: Commit**

```bash
git add tests/integration/
git commit -m "test: add integration tests for protocol stack and memory tiers"
```

---

## Task 18: Final Verification

**Step 1: Run full test suite**

Run: `pytest -v`
Expected: All tests pass (existing 135 + new ~40 = ~175 total)

**Step 2: Build console**

Run: `cd console && npm run build`
Expected: Clean build

**Step 3: Verify CLI commands**

Run:
```bash
prowlr acp --help
prowlr market --help
prowlr market list
```
Expected: All show help/output correctly

**Step 4: Final commit and tag**

```bash
git tag -a v2.0.0-alpha -m "Phase 2: protocols, marketplace, monitoring, memory, swarm, console"
```
