# Prowlr-Studio Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform ShipSec Studio fork into Prowlr-Studio with rebranding, security fixes, CLI integration, ProwlrBot JWT auth, Agent Hub page, and Agent Workspace with live streaming.

**Architecture:** Two backends (Python FastAPI :8088 + TypeScript NestJS :3211), one React 19 frontend. Python is source of truth for agents/auth. Studio handles workflows/UI. They communicate via REST + SSE + shared JWT. Progressive infrastructure: SQLite+filesystem default, Docker required for agent workspaces.

**Tech Stack:** Python 3.10+/FastAPI (backend), TypeScript/NestJS/Bun (studio backend), React 19/Radix/shadcn/Tailwind/ReactFlow/xterm.js/Monaco (frontend), Docker (agent containers), Drizzle ORM, Temporal (optional).

**Spec:** `docs/superpowers/specs/2026-03-11-prowlr-studio-design.md`

**Repositories:**
- ProwlrBot: `/Users/nunu/prowlrbot/prowlrbot/` (this repo)
- Prowlr-Studio: `/tmp/prowrl-studio-full/` (cloned from `github.com/ProwlrBot/prowrl-studio`)

---

## Chunk 1: Rebranding (400+ references)

Automated find-and-replace across the prowrl-studio repository. Run scripts, verify build, commit.

### Task 1.1: Create Rebranding Script

**Files:**
- Create: `prowrl-studio/scripts/rebrand.sh`

- [ ] **Step 1: Write the rebranding shell script**

```bash
#!/usr/bin/env bash
set -euo pipefail

STUDIO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$STUDIO_ROOT"

echo "=== Prowlr-Studio Rebranding Script ==="

# Phase 1: Case-sensitive replacements (order matters - most specific first)
declare -a REPLACEMENTS=(
  # Package scopes and npm names
  "@shipsec/component-sdk|@prowlrbot/component-sdk"
  "@shipsec/contracts|@prowlrbot/contracts"
  "@shipsec/shared|@prowlrbot/shared"
  "@shipsec/backend-client|@prowlrbot/backend-client"
  "shipsec-studio|prowlrbot-studio"

  # Docker images
  "ghcr.io/shipsecai/|ghcr.io/prowlrbot/"

  # Environment variables
  "SHIPSEC_|PROWLRBOT_"

  # URLs
  "studio.shipsec.ai|studio.prowlrbot.com"
  "github.com/ShipSecAI/studio|github.com/ProwlrBot/prowrl-studio"

  # Code identifiers
  "shipsecWorkflowRun|prowlrbotWorkflowRun"
  "shipsec-dev|prowlrbot-dev"
  "shipsec_dev|prowlrbot_dev"

  # Component author type
  "'shipsecai'|'prowlrbot'"
  "\"shipsecai\"|\"prowlrbot\""

  # Brand names (do these last - broadest match)
  "ShipSec Studio|Prowlr-Studio"
  "ShipSecAI|ProwlrBot"
  "ShipSec|ProwlrBot"
  "Shipsec|Prowlrbot"
  "shipsecai|prowlrbot"
  "shipsec|prowlrbot"
)

# File extensions to process
EXTENSIONS="ts,tsx,js,jsx,json,yaml,yml,md,html,css,conf,sh,sql,env,toml,cfg,Dockerfile"

for pair in "${REPLACEMENTS[@]}"; do
  FROM="${pair%%|*}"
  TO="${pair##*|}"
  echo "  Replacing: $FROM -> $TO"

  # Use find + sed for cross-platform compatibility
  find . \
    -type f \
    \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
       -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" \
       -o -name "*.html" -o -name "*.css" -o -name "*.conf" -o -name "*.sh" \
       -o -name "*.sql" -o -name "*.env" -o -name "*.env.*" -o -name "*.toml" \
       -o -name "*.cfg" -o -name "Dockerfile*" -o -name "*.dockerignore" \
       -o -name ".env.*" \) \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" \
    -not -path "*/scripts/rebrand.sh" \
    -exec sed -i '' "s|${FROM}|${TO}|g" {} +
done

echo ""
echo "=== Rebranding complete ==="
echo "Next steps:"
echo "  1. Review changes with: git diff --stat"
echo "  2. Rename any files/directories still using 'shipsec'"
echo "  3. Run: bun install (to update lockfile)"
echo "  4. Run: bun run typecheck"
echo "  5. Run: bun run test"
```

- [ ] **Step 2: Make script executable and run it**

Run:
```bash
cd /tmp/prowrl-studio-full
chmod +x scripts/rebrand.sh
./scripts/rebrand.sh
```
Expected: Each replacement pair logs its line. No errors.

- [ ] **Step 3: Verify replacement count**

Run:
```bash
cd /tmp/prowrl-studio-full
git diff --stat | tail -5
grep -ri "shipsec" --include="*.ts" --include="*.tsx" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.md" --include="*.env*" --include="*.conf" --include="Dockerfile*" -l | grep -v node_modules | grep -v .git | grep -v dist || echo "No remaining references"
```
Expected: 100+ files changed. Zero remaining "shipsec" references (case-insensitive).

- [ ] **Step 4: Rename directories and files**

Run:
```bash
cd /tmp/prowrl-studio-full

# Rename package directories if any contain shipsec
find . -type d -name "*shipsec*" -not -path "*/node_modules/*" -not -path "*/.git/*" | while read dir; do
  newdir=$(echo "$dir" | sed 's/shipsec/prowlrbot/g')
  mv "$dir" "$newdir"
  echo "Renamed: $dir -> $newdir"
done

# Rename files
find . -type f -name "*shipsec*" -not -path "*/node_modules/*" -not -path "*/.git/*" | while read file; do
  newfile=$(echo "$file" | sed 's/shipsec/prowlrbot/g')
  mv "$file" "$newfile"
  echo "Renamed: $file -> $newfile"
done
```

- [ ] **Step 5: Update root package.json name**

Verify `/tmp/prowrl-studio-full/package.json` has `"name": "prowlrbot-studio"` (should be done by script, verify manually).

- [ ] **Step 6: Reinstall dependencies and verify build**

Run:
```bash
cd /tmp/prowrl-studio-full
bun install
bun run typecheck
```
Expected: Install succeeds. Typecheck passes (or shows pre-existing errors only).

- [ ] **Step 7: Run tests**

Run:
```bash
cd /tmp/prowrl-studio-full
bun run test 2>&1 | tail -20
```
Expected: Tests pass (or only pre-existing failures).

- [ ] **Step 8: Commit rebranding**

```bash
cd /tmp/prowrl-studio-full
git add -A
git commit -m "chore: rebrand ShipSec Studio to Prowlr-Studio

Replace 400+ references across 100+ files:
- Package names: @shipsec/* -> @prowlrbot/*
- Docker images: ghcr.io/shipsecai/* -> ghcr.io/prowlrbot/*
- Environment variables: SHIPSEC_* -> PROWLRBOT_*
- URLs: studio.shipsec.ai -> studio.prowlrbot.com
- Component author: shipsecai -> prowlrbot
- All UI text and meta tags

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 2: Security Fixes (Critical + High)

Fix all 4 Critical and 6 High findings from the security audit before deploying.

### Task 2.1: Fix C1 - Remove Default admin/admin Credentials

**Files:**
- Modify: `prowrl-studio/backend/src/config/auth.config.ts`
- Modify: `prowrl-studio/backend/src/auth/auth.guard.ts`
- Modify: `prowrl-studio/backend/src/app.controller.ts`

- [ ] **Step 1: Remove default credentials from auth config**

In `backend/src/config/auth.config.ts`, find the `ADMIN_USERNAME` and `ADMIN_PASSWORD` defaults (currently `admin`/`admin`). Change to:

```typescript
ADMIN_USERNAME: process.env.ADMIN_USERNAME ?? (() => {
  if (process.env.NODE_ENV === 'production') {
    throw new Error('ADMIN_USERNAME must be set in production');
  }
  return 'admin';
})(),
ADMIN_PASSWORD: process.env.ADMIN_PASSWORD ?? (() => {
  if (process.env.NODE_ENV === 'production') {
    throw new Error('ADMIN_PASSWORD must be set in production');
  }
  return 'admin';
})(),
```

- [ ] **Step 2: Add startup validation in main.ts**

In `backend/src/main.ts`, before `app.listen()`, add:

```typescript
if (process.env.NODE_ENV === 'production') {
  const requiredVars = ['ADMIN_USERNAME', 'ADMIN_PASSWORD', 'SECRET_STORE_MASTER_KEY', 'SESSION_SECRET'];
  const missing = requiredVars.filter(v => !process.env[v]);
  if (missing.length > 0) {
    throw new Error(`Missing required production env vars: ${missing.join(', ')}`);
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "fix(security): C1 — remove default admin credentials in production"
```

### Task 2.2: Fix C2 - Remove Hardcoded Encryption Keys

**Files:**
- Modify: `prowrl-studio/backend/src/secrets/secrets.service.ts` (or wherever SECRET_STORE_MASTER_KEY is used)

- [ ] **Step 1: Find and remove fallback keys**

```bash
cd /tmp/prowrl-studio-full
grep -rn "FALLBACK_DEV_KEY\|DEFAULT_DEV_KEY\|fallback.*key\|default.*master.*key" backend/src/ --include="*.ts" -l
```

Remove any hardcoded fallback keys. Replace with:

```typescript
const masterKey = process.env.SECRET_STORE_MASTER_KEY;
if (!masterKey) {
  if (process.env.NODE_ENV === 'production') {
    throw new Error('SECRET_STORE_MASTER_KEY must be set in production');
  }
  console.warn('WARNING: SECRET_STORE_MASTER_KEY not set. Secrets encryption disabled in development.');
}
```

- [ ] **Step 2: Add .env.docker to .gitignore**

```bash
echo ".env.docker" >> /tmp/prowrl-studio-full/.gitignore
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "fix(security): C2 — remove hardcoded encryption keys, require in production"
```

### Task 2.3: Fix C3 - Docker-in-Docker TLS

**Files:**
- Modify: `prowrl-studio/docker/docker-compose.infra.yml`
- Modify: Any DinD service definitions

- [ ] **Step 1: Find DinD configuration**

```bash
cd /tmp/prowrl-studio-full
grep -rn "dind\|docker:dind\|privileged" docker/ --include="*.yml" --include="*.yaml" -l
```

- [ ] **Step 2: Enable TLS for DinD services**

In any docker-compose file with DinD, change:

```yaml
# Before
services:
  dind:
    image: docker:dind
    privileged: true
    environment:
      - DOCKER_TLS_CERTDIR=

# After
services:
  dind:
    image: docker:dind
    privileged: true
    environment:
      - DOCKER_TLS_CERTDIR=/certs
    volumes:
      - dind-certs-ca:/certs/ca
      - dind-certs-client:/certs/client
    networks:
      - dind-network

volumes:
  dind-certs-ca:
  dind-certs-client:

networks:
  dind-network:
    driver: bridge
    internal: true
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "fix(security): C3 — enable TLS for Docker-in-Docker, isolate network"
```

### Task 2.4: Fix C4 - Timing-Safe Token Comparison

**Files:**
- Modify: `prowrl-studio/backend/src/auth/auth.guard.ts`

- [ ] **Step 1: Replace string comparison with timingSafeEqual**

Find all `!==` comparisons on tokens/secrets in `auth.guard.ts`. Replace with:

```typescript
import { timingSafeEqual } from 'crypto';

function safeCompare(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  return timingSafeEqual(Buffer.from(a), Buffer.from(b));
}
```

Use `safeCompare()` wherever internal tokens, API keys, or session tokens are compared.

- [ ] **Step 2: Apply same fix to session.utils.ts**

Check `backend/src/auth/session.utils.ts` for any string comparisons on session tokens and replace.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "fix(security): C4 — use timingSafeEqual for all token comparisons"
```

### Task 2.5: Fix H1-H6 (High Priority)

**Files:**
- Modify: `prowrl-studio/backend/src/auth/auth.guard.ts` (H1, H2, H3)
- Modify: `prowrl-studio/backend/src/main.ts` (H6)
- Modify: Upload handling files (H4)
- Modify: Session/cookie config (H5)

- [ ] **Step 1: H1 — Hash JWT token in logs**

Find any `console.log` or logger calls that output JWT tokens. Replace with:

```typescript
import { createHash } from 'crypto';

function tokenFingerprint(token: string): string {
  return createHash('sha256').update(token).digest('hex').substring(0, 8);
}

// Instead of: logger.debug(`Token: ${token.substring(0, 10)}...`)
// Use: logger.debug(`Token fingerprint: ${tokenFingerprint(token)}`)
```

- [ ] **Step 2: H2 — Default to MEMBER role**

In `auth.guard.ts`, find where `org_role` is read. Change fallback from ADMIN to MEMBER:

```typescript
// Before: const role = orgRole ?? 'ADMIN';
// After:
const role = orgRole ?? 'MEMBER';
```

- [ ] **Step 3: H3 — Secure ensure-tenant endpoint**

Find the `ensure-tenant` or tenant provisioning endpoint. Add:

```typescript
if (!process.env.INTERNAL_SERVICE_TOKEN) {
  throw new ForbiddenException('Internal service token not configured');
}
if (!safeCompare(providedToken, process.env.INTERNAL_SERVICE_TOKEN)) {
  throw new UnauthorizedException('Invalid internal service token');
}
```

- [ ] **Step 4: H4 — File upload validation**

Find upload handlers (likely in storage module). Add:

```typescript
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_MIME_TYPES = [
  'application/json', 'application/pdf', 'text/plain', 'text/csv',
  'image/png', 'image/jpeg', 'image/gif', 'image/webp',
  'application/zip', 'application/x-tar',
];

function validateUpload(file: Express.Multer.File): void {
  if (file.size > MAX_FILE_SIZE) {
    throw new BadRequestException(`File too large: ${file.size} > ${MAX_FILE_SIZE}`);
  }
  if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
    throw new BadRequestException(`Disallowed MIME type: ${file.mimetype}`);
  }
  // Sanitize filename - strip path traversal
  file.originalname = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
}
```

- [ ] **Step 5: H5 — Force secure cookies on HTTPS**

In session/cookie configuration:

```typescript
const isHttps = req.protocol === 'https' || req.headers['x-forwarded-proto'] === 'https';
res.cookie('x-session-token', token, {
  httpOnly: true,
  secure: isHttps,
  sameSite: 'lax',
  maxAge: 24 * 60 * 60 * 1000,
});
```

- [ ] **Step 6: H6 — Add security headers via helmet**

In `backend/src/main.ts`:

```typescript
import helmet from 'helmet';

// After app creation, before routes
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "blob:"],
      connectSrc: ["'self'", "ws:", "wss:"],
    },
  },
  crossOriginEmbedderPolicy: false,
}));
```

Run: `cd /tmp/prowrl-studio-full && bun add helmet --cwd backend`

- [ ] **Step 7: Commit all High fixes**

```bash
git add -A && git commit -m "fix(security): H1-H6 — token logging, role defaults, upload validation, security headers"
```

---

## Chunk 3: CLI Integration + Python Backend API

Add `prowlr studio` CLI command and new API endpoints for Studio integration.

### Task 3.1: Add Studio CLI Command

**Files:**
- Create: `src/prowlrbot/cli/studio_cmd.py`
- Modify: `src/prowlrbot/cli/main.py`

- [ ] **Step 1: Write failing test**

Create: `tests/cli/test_studio_cmd.py`

```python
import pytest
from click.testing import CliRunner
from prowlrbot.cli.main import cli


def test_studio_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["studio", "--help"])
    assert result.exit_code == 0
    assert "Prowlr-Studio" in result.output


def test_studio_status():
    runner = CliRunner()
    result = runner.invoke(cli, ["studio", "status"])
    assert result.exit_code == 0
    assert "Studio" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/cli/test_studio_cmd.py -v`
Expected: FAIL - no "studio" command registered

- [ ] **Step 3: Write studio_cmd.py**

Create: `src/prowlrbot/cli/studio_cmd.py`

```python
"""Prowlr-Studio management commands."""

import subprocess
import sys
from pathlib import Path

import click


@click.group("studio")
def studio_cmd() -> None:
    """Manage Prowlr-Studio workspace."""
    pass


@studio_cmd.command("start")
@click.option("--host", default="127.0.0.1", help="Studio backend host")
@click.option("--port", default=3211, type=int, help="Studio backend port")
@click.option("--dev", is_flag=True, help="Start in development mode")
def start_cmd(host: str, port: int, dev: bool) -> None:
    """Start Prowlr-Studio backend and frontend."""
    studio_dir = _find_studio_dir()
    if not studio_dir:
        click.echo("Error: Prowlr-Studio not found. Install with: prowlr studio install")
        sys.exit(1)

    click.echo(f"Starting Prowlr-Studio on {host}:{port}...")

    from prowlrbot.config.utils import load_config
    config = load_config()
    api_port = getattr(config, "port", 8088)

    env = {
        "HOST": host,
        "PORT": str(port),
        "AUTH_PROVIDER": "prowlrbot",
        "PROWLRBOT_API_URL": f"http://127.0.0.1:{api_port}",
    }

    if dev:
        cmd = ["bun", "run", "dev"]
    else:
        cmd = ["bun", "run", "start"]

    try:
        subprocess.run(cmd, cwd=str(studio_dir), env={**dict(__import__("os").environ), **env})
    except FileNotFoundError:
        click.echo("Error: 'bun' not found. Install Bun: https://bun.sh")
        sys.exit(1)


@studio_cmd.command("status")
def status_cmd() -> None:
    """Show Prowlr-Studio status."""
    studio_dir = _find_studio_dir()
    if studio_dir:
        click.echo(f"Studio directory: {studio_dir}")
        click.echo("Studio: installed")
    else:
        click.echo("Studio: not installed")

    # Check if studio backend is running
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:3211/api/v1/health", timeout=2)
        click.echo("Studio backend: running (port 3211)")
    except Exception:
        click.echo("Studio backend: not running")


@studio_cmd.command("install")
@click.option("--dir", "install_dir", default=None, help="Installation directory")
def install_cmd(install_dir: str | None) -> None:
    """Install Prowlr-Studio from GitHub."""
    target = Path(install_dir) if install_dir else Path.home() / ".prowlrbot" / "studio"
    if target.exists() and any(target.iterdir()):
        click.echo(f"Studio already exists at {target}")
        return

    click.echo(f"Installing Prowlr-Studio to {target}...")
    target.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            ["git", "clone", "https://github.com/ProwlrBot/prowrl-studio.git", str(target)],
            check=True,
        )
        subprocess.run(["bun", "install"], cwd=str(target), check=True)
        click.echo(f"Prowlr-Studio installed to {target}")
        click.echo("Start with: prowlr studio start")
    except subprocess.CalledProcessError as e:
        click.echo(f"Installation failed: {e}")
        sys.exit(1)


def _find_studio_dir() -> Path | None:
    """Find Prowlr-Studio installation directory."""
    candidates = [
        Path.home() / ".prowlrbot" / "studio",
        Path.cwd() / "prowrl-studio",
    ]
    # Dev convenience: check /tmp only if PROWLRBOT_DEV is set
    import os
    if os.environ.get("PROWLRBOT_DEV"):
        candidates.append(Path("/tmp/prowrl-studio-full"))
    for path in candidates:
        if (path / "package.json").exists():
            return path
    return None
```

- [ ] **Step 4: Register in main.py**

In `src/prowlrbot/cli/main.py`, add after other command imports:

```python
from .studio_cmd import studio_cmd
cli.add_command(studio_cmd)
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/cli/test_studio_cmd.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/prowlrbot/cli/studio_cmd.py src/prowlrbot/cli/main.py tests/cli/test_studio_cmd.py
git commit -m "feat(cli): add 'prowlr studio' command for Studio management"
```

### Task 3.2: Add Agent Streaming API Endpoints

**Files:**
- Create: `src/prowlrbot/app/routers/studio.py`
- Modify: `src/prowlrbot/app/routers/__init__.py`
- Create: `tests/app/test_studio_router.py`

- [ ] **Step 1: Write failing test**

Create: `tests/app/test_studio_router.py`

```python
import pytest
from httpx import AsyncClient, ASGITransport
from prowlrbot.app._app import create_app


@pytest.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_studio_agents_list(client):
    resp = await client.get("/api/studio/agents")
    assert resp.status_code in (200, 401)  # 401 if auth required


@pytest.mark.asyncio
async def test_studio_health(client):
    resp = await client.get("/api/studio/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/app/test_studio_router.py -v`
Expected: FAIL - 404 on /api/studio/* endpoints

- [ ] **Step 3: Write the studio router**

Create: `src/prowlrbot/app/routers/studio.py`

```python
"""Studio integration API endpoints.

Provides the REST + SSE contract defined in the Prowlr-Studio design spec
(Section 3.1: Backend Integration Contract).
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from prowlrbot.auth.middleware import get_current_user

router = APIRouter(prefix="/studio", tags=["studio"])


class StudioHealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float


class AgentSummary(BaseModel):
    id: str
    name: str
    description: str
    status: str  # running, idle, error
    capabilities: list[str]
    model: str | None = None
    provider: str | None = None


class AgentRunRequest(BaseModel):
    query: str
    autonomy: str = "delegate"  # watch, guide, delegate, autonomous
    timeout_s: int = 300


class AgentRunResponse(BaseModel):
    run_id: str
    agent_id: str
    status: str


class AgentMessageRequest(BaseModel):
    content: str


class AutonomyUpdateRequest(BaseModel):
    level: str  # watch, guide, delegate, autonomous


_start_time = time.time()


@router.get("/health")
async def studio_health() -> StudioHealthResponse:
    return StudioHealthResponse(
        status="ok",
        version="0.1.0",
        uptime_seconds=time.time() - _start_time,
    )


@router.get("/agents")
async def list_agents(
    request: Request,
    _user=Depends(get_current_user),
) -> list[AgentSummary]:
    """List all agents with status, config, and capabilities."""
    agents = []

    # Get agent configs from the runner
    runner = getattr(request.app.state, "runner", None)
    if not runner:
        return agents

    # Load agent configurations from ~/.prowlrbot/
    from prowlrbot.config.utils import load_config
    config = load_config()

    # config.agents may be a list of dicts or Pydantic models
    agents_config = getattr(config, "agents", [])
    if isinstance(agents_config, list):
        for agent_cfg in agents_config:
            # Handle both dict and Pydantic model
            get = agent_cfg.get if isinstance(agent_cfg, dict) else lambda k, d=None: getattr(agent_cfg, k, d)
            agents.append(AgentSummary(
                id=get("id", get("name", "unknown")),
                name=get("name", "Unknown"),
                description=get("description", ""),
                status="idle",
                capabilities=get("skills", []) or [],
                model=get("model"),
                provider=get("provider"),
            ))

    return agents


@router.post("/agents/{agent_id}/run")
async def run_agent(
    agent_id: str,
    body: AgentRunRequest,
    request: Request,
    _user=Depends(get_current_user),
) -> AgentRunResponse:
    """Start an agent run, returns run_id."""
    import uuid
    run_id = str(uuid.uuid4())

    runner = getattr(request.app.state, "runner", None)
    if not runner:
        raise HTTPException(status_code=503, detail="Agent runner not available")

    # TODO: Start agent run in background task
    return AgentRunResponse(
        run_id=run_id,
        agent_id=agent_id,
        status="starting",
    )


@router.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str, request: Request, _user=Depends(get_current_user)) -> dict:
    """Stop a running agent."""
    # TODO: Implement agent stop
    return {"agent_id": agent_id, "status": "stopped"}


@router.post("/agents/{agent_id}/message")
async def message_agent(
    agent_id: str,
    body: AgentMessageRequest,
    request: Request,
    _user=Depends(get_current_user),
) -> dict:
    """Send a human message to a running agent."""
    # TODO: Inject message into agent's input queue
    return {"agent_id": agent_id, "status": "message_sent"}


@router.put("/agents/{agent_id}/autonomy")
async def update_autonomy(
    agent_id: str,
    body: AutonomyUpdateRequest,
    request: Request,
    _user=Depends(get_current_user),
) -> dict:
    """Change an agent's autonomy level mid-run."""
    valid_levels = {"watch", "guide", "delegate", "autonomous"}
    if body.level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"Invalid level. Must be one of: {valid_levels}")
    return {"agent_id": agent_id, "autonomy": body.level}


@router.get("/agents/{agent_id}/stream")
async def stream_agent_events(
    agent_id: str,
    request: Request,
    token: str | None = None,
) -> StreamingResponse:
    """SSE stream of agent events for the Agent Workspace.

    Auth via query param `token` (EventSource doesn't support headers).
    Event types: thought, tool_call, tool_start, terminal_output,
    browser_screenshot, browser_action, file_change, chat_message,
    memory_update, cost_update, log, config_change, status.
    """
    # Validate token from query param (EventSource can't send headers)
    if token:
        try:
            from prowlrbot.auth.jwt_handler import JWTHandler
            JWTHandler().decode_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def event_generator() -> AsyncGenerator[str, None]:
        # Send initial status
        yield _sse_event("status", {"state": "connected", "agent_id": agent_id})

        # TODO: Subscribe to agent's event bus and relay events
        # For now, send heartbeat to keep connection alive
        try:
            while True:
                await asyncio.sleep(15)
                yield _sse_event("heartbeat", {"timestamp": time.time()})
        except asyncio.CancelledError:
            return

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/auth/validate")
async def validate_token(request: Request) -> dict:
    """Validate a JWT token. Called by Studio's NestJS backend."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = auth_header[7:]
    try:
        from prowlrbot.auth.jwt_handler import JWTHandler
        handler = JWTHandler()
        payload = handler.decode_token(token)
        return {
            "valid": True,
            "user": {
                "id": payload.get("user_id"),
                "role": payload.get("role", "viewer"),
                "username": payload.get("username"),
            },
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def _sse_event(event_type: str, data: dict) -> str:
    """Format a server-sent event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
```

- [ ] **Step 4: Register the router**

In `src/prowlrbot/app/routers/__init__.py`, add:

```python
from .studio import router as studio_router
router.include_router(studio_router)
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/app/test_studio_router.py -v`
Expected: PASS

- [ ] **Step 6: Run full test suite**

Run: `pytest --tb=short 2>&1 | tail -10`
Expected: 713+ tests pass, no regressions

- [ ] **Step 7: Commit**

```bash
git add src/prowlrbot/app/routers/studio.py src/prowlrbot/app/routers/__init__.py tests/app/test_studio_router.py
git commit -m "feat(api): add Studio integration endpoints — agents, streaming, auth validation"
```

---

## Chunk 4: ProwlrBot JWT Auth Provider in Studio

Add a new auth provider to Studio's NestJS backend that validates JWTs against ProwlrBot's FastAPI backend.

### Task 4.1: Create ProwlrBot Auth Provider

**Files:**
- Create: `prowrl-studio/backend/src/auth/providers/prowlrbot.provider.ts`
- Modify: `prowrl-studio/backend/src/auth/auth.guard.ts`
- Modify: `prowrl-studio/backend/src/config/auth.config.ts`

- [ ] **Step 1: Add ProwlrBot auth config**

In `backend/src/config/auth.config.ts`, add new env vars:

```typescript
PROWLRBOT_API_URL: process.env.PROWLRBOT_API_URL ?? 'http://localhost:8088',
PROWLRBOT_JWT_CACHE_TTL: parseInt(process.env.JWT_CACHE_TTL ?? '300000', 10), // 5 min
```

- [ ] **Step 2: Create ProwlrBot auth provider**

Create: `prowrl-studio/backend/src/auth/providers/prowlrbot.provider.ts`

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

interface ProwlrBotUser {
  id: string;
  role: string;
  username: string;
}

interface CacheEntry {
  user: ProwlrBotUser;
  expiresAt: number;
}

@Injectable()
export class ProwlrBotAuthProvider {
  private readonly logger = new Logger(ProwlrBotAuthProvider.name);
  private readonly cache = new Map<string, CacheEntry>();
  private readonly apiUrl: string;
  private readonly cacheTtl: number;

  constructor(private configService: ConfigService) {
    this.apiUrl = this.configService.get('PROWLRBOT_API_URL', 'http://localhost:8088');
    this.cacheTtl = this.configService.get('PROWLRBOT_JWT_CACHE_TTL', 300000);
  }

  async validateToken(token: string): Promise<ProwlrBotUser | null> {
    // Check cache first
    const cached = this.cache.get(token);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.user;
    }

    try {
      const response = await fetch(`${this.apiUrl}/api/studio/auth/validate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        this.cache.delete(token);
        return null;
      }

      const data = await response.json() as { valid: boolean; user: ProwlrBotUser };
      if (!data.valid) {
        return null;
      }

      // Cache the result
      this.cache.set(token, {
        user: data.user,
        expiresAt: Date.now() + this.cacheTtl,
      });

      // Evict old entries periodically
      if (this.cache.size > 1000) {
        const now = Date.now();
        for (const [key, entry] of this.cache) {
          if (entry.expiresAt < now) this.cache.delete(key);
        }
      }

      return data.user;
    } catch (error) {
      this.logger.error(`ProwlrBot auth validation failed: ${error}`);
      return null;
    }
  }
}
```

- [ ] **Step 3: Integrate into AuthGuard**

In `backend/src/auth/auth.guard.ts`, add the ProwlrBot provider path. In the `canActivate` method, before the Clerk/local checks:

```typescript
// ProwlrBot JWT validation
if (this.configService.get('AUTH_PROVIDER') === 'prowlrbot') {
  const token = this.extractBearerToken(request);
  if (token) {
    const user = await this.prowlrbotProvider.validateToken(token);
    if (user) {
      request.authContext = {
        userId: user.id,
        organizationId: 'default',
        roles: [user.role === 'admin' ? 'ADMIN' : 'MEMBER'],
        isAuthenticated: true,
        provider: 'prowlrbot',
      };
      return true;
    }
  }
  // Also check session cookie (for browser-based auth)
  const sessionToken = request.cookies?.['x-session-token'];
  if (sessionToken) {
    const user = await this.prowlrbotProvider.validateToken(sessionToken);
    if (user) {
      request.authContext = {
        userId: user.id,
        organizationId: 'default',
        roles: [user.role === 'admin' ? 'ADMIN' : 'MEMBER'],
        isAuthenticated: true,
        provider: 'prowlrbot',
      };
      return true;
    }
  }
}
```

- [ ] **Step 4: Register provider in AuthModule**

In `backend/src/auth/auth.module.ts`, add `ProwlrBotAuthProvider` to providers and exports.

- [ ] **Step 5: Add frontend auth provider**

Create: `prowrl-studio/frontend/src/auth/providers/prowlrbot.ts`

```typescript
import type { FrontendAuthProvider } from '../types';

export const prowlrbotAuthProvider: FrontendAuthProvider = {
  name: 'prowlrbot',

  async initialize() {
    // Check if we have a stored token
    const token = localStorage.getItem('prowlrbot_token');
    if (token) {
      // Validate token is still valid
      try {
        const resp = await fetch('/api/v1/auth/validate', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (resp.ok) {
          return { isAuthenticated: true, token };
        }
      } catch {
        // Token invalid, clear it
      }
      localStorage.removeItem('prowlrbot_token');
    }
    return { isAuthenticated: false };
  },

  async login(credentials: { username: string; password: string }) {
    const resp = await fetch('http://localhost:8088/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    if (!resp.ok) throw new Error('Login failed');
    const data = await resp.json();
    localStorage.setItem('prowlrbot_token', data.token);
    return { isAuthenticated: true, token: data.token };
  },

  async logout() {
    localStorage.removeItem('prowlrbot_token');
  },

  getToken() {
    return localStorage.getItem('prowlrbot_token');
  },
};
```

- [ ] **Step 6: Wire up provider selection in AuthProvider.tsx**

In `frontend/src/auth/AuthProvider.tsx`, add:

```typescript
import { prowlrbotAuthProvider } from './providers/prowlrbot';

// In the provider selection logic:
case 'prowlrbot':
  return prowlrbotAuthProvider;
```

- [ ] **Step 7: Commit**

```bash
cd /tmp/prowrl-studio-full
git add -A
git commit -m "feat(auth): add ProwlrBot JWT auth provider for Studio

- Backend: ProwlrBotAuthProvider validates tokens against ProwlrBot API
- Frontend: prowlrbotAuthProvider handles login/logout via ProwlrBot
- Token validation cached for 5 minutes (configurable via JWT_CACHE_TTL)
- AUTH_PROVIDER=prowlrbot activates this flow"
```

---

## Chunk 5: Agent Hub Page

New frontend page showing all agents as visual cards with status, capabilities, and quick actions.

### Task 5.1: Create Agent Hub Page

**Files:**
- Create: `prowrl-studio/frontend/src/pages/AgentHubPage.tsx`
- Create: `prowrl-studio/frontend/src/components/agent-hub/AgentCard.tsx`
- Create: `prowrl-studio/frontend/src/components/agent-hub/TeamCard.tsx`
- Create: `prowrl-studio/frontend/src/components/agent-hub/AgentHubHeader.tsx`
- Create: `prowrl-studio/frontend/src/store/agentHubStore.ts`
- Create: `prowrl-studio/frontend/src/api/agents.ts`
- Modify: `prowrl-studio/frontend/src/App.tsx` (add route)

- [ ] **Step 1: Create the agent API client**

Create: `prowrl-studio/frontend/src/api/agents.ts`

```typescript
export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'running' | 'idle' | 'error';
  capabilities: string[];
  model: string | null;
  provider: string | null;
  avatar?: string;
  currentTask?: string;
}

export interface Team {
  id: string;
  name: string;
  description: string;
  members: string[];
  status: 'active' | 'idle';
}

const PROWLRBOT_API = import.meta.env.VITE_PROWLRBOT_API_URL ?? 'http://localhost:8088';

export async function fetchAgents(): Promise<Agent[]> {
  const token = localStorage.getItem('prowlrbot_token');
  const resp = await fetch(`${PROWLRBOT_API}/api/studio/agents`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!resp.ok) throw new Error('Failed to fetch agents');
  return resp.json();
}

export async function runAgent(agentId: string, query: string): Promise<{ run_id: string }> {
  const token = localStorage.getItem('prowlrbot_token');
  const resp = await fetch(`${PROWLRBOT_API}/api/studio/agents/${agentId}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ query }),
  });
  if (!resp.ok) throw new Error('Failed to run agent');
  return resp.json();
}

export async function fetchTeams(): Promise<Team[]> {
  const token = localStorage.getItem('prowlrbot_token');
  const resp = await fetch(`${PROWLRBOT_API}/api/teams/list`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!resp.ok) return [];
  return resp.json();
}
```

- [ ] **Step 2: Create the Zustand store**

Create: `prowrl-studio/frontend/src/store/agentHubStore.ts`

```typescript
import { create } from 'zustand';
import type { Agent, Team } from '../api/agents';
import { fetchAgents, fetchTeams } from '../api/agents';

interface AgentHubState {
  agents: Agent[];
  teams: Team[];
  loading: boolean;
  error: string | null;
  filter: string;
  statusFilter: 'all' | 'running' | 'idle' | 'error';
  setFilter: (filter: string) => void;
  setStatusFilter: (status: 'all' | 'running' | 'idle' | 'error') => void;
  loadAgents: () => Promise<void>;
  loadTeams: () => Promise<void>;
}

export const useAgentHubStore = create<AgentHubState>((set) => ({
  agents: [],
  teams: [],
  loading: false,
  error: null,
  filter: '',
  statusFilter: 'all',

  setFilter: (filter) => set({ filter }),
  setStatusFilter: (statusFilter) => set({ statusFilter }),

  loadAgents: async () => {
    set({ loading: true, error: null });
    try {
      const agents = await fetchAgents();
      set({ agents, loading: false });
    } catch (e) {
      set({ error: (e as Error).message, loading: false });
    }
  },

  loadTeams: async () => {
    try {
      const teams = await fetchTeams();
      set({ teams });
    } catch {
      // Teams are optional
    }
  },
}));
```

- [ ] **Step 3: Create AgentCard component**

Create: `prowrl-studio/frontend/src/components/agent-hub/AgentCard.tsx`

```tsx
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Bot, Eye, Play, Settings } from 'lucide-react';
import type { Agent } from '@/api/agents';

interface AgentCardProps {
  agent: Agent;
  onRun: (agent: Agent) => void;
  onView: (agent: Agent) => void;
  onConfigure: (agent: Agent) => void;
}

const statusColors = {
  running: 'bg-green-500',
  idle: 'bg-gray-400',
  error: 'bg-red-500',
} as const;

export function AgentCard({ agent, onRun, onView, onConfigure }: AgentCardProps) {
  return (
    <Card className="group hover:shadow-lg transition-shadow">
      <CardHeader className="flex flex-row items-start gap-3 pb-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
          <Bot className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-sm truncate">{agent.name}</h3>
            <span className={`h-2 w-2 rounded-full ${statusColors[agent.status]}`} />
          </div>
          <p className="text-xs text-muted-foreground truncate">{agent.description}</p>
        </div>
      </CardHeader>

      <CardContent className="pb-2">
        <div className="flex flex-wrap gap-1">
          {agent.capabilities.slice(0, 4).map((cap) => (
            <Badge key={cap} variant="secondary" className="text-xs">
              {cap}
            </Badge>
          ))}
          {agent.capabilities.length > 4 && (
            <Badge variant="outline" className="text-xs">
              +{agent.capabilities.length - 4}
            </Badge>
          )}
        </div>
        {agent.currentTask && (
          <p className="mt-2 text-xs text-muted-foreground italic truncate">
            {agent.currentTask}
          </p>
        )}
        {agent.model && (
          <p className="mt-1 text-xs text-muted-foreground">
            {agent.model} via {agent.provider}
          </p>
        )}
      </CardContent>

      <CardFooter className="gap-1 pt-2">
        <Button size="sm" variant="default" onClick={() => onRun(agent)} disabled={agent.status === 'running'}>
          <Play className="h-3 w-3 mr-1" /> Run
        </Button>
        <Button size="sm" variant="outline" onClick={() => onView(agent)} disabled={agent.status !== 'running'}>
          <Eye className="h-3 w-3 mr-1" /> Live
        </Button>
        <Button size="sm" variant="ghost" onClick={() => onConfigure(agent)}>
          <Settings className="h-3 w-3" />
        </Button>
      </CardFooter>
    </Card>
  );
}
```

- [ ] **Step 4: Create TeamCard component**

Create: `prowrl-studio/frontend/src/components/agent-hub/TeamCard.tsx`

```tsx
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users } from 'lucide-react';
import type { Team } from '@/api/agents';

interface TeamCardProps {
  team: Team;
  agentCount: number;
  onManage: (team: Team) => void;
}

export function TeamCard({ team, agentCount, onManage }: TeamCardProps) {
  return (
    <Card className="border-dashed">
      <CardHeader className="flex flex-row items-center gap-3 pb-2">
        <Users className="h-5 w-5 text-muted-foreground" />
        <div>
          <h3 className="font-semibold text-sm">{team.name}</h3>
          <p className="text-xs text-muted-foreground">{agentCount} agents</p>
        </div>
      </CardHeader>
      <CardContent>
        <Button size="sm" variant="outline" onClick={() => onManage(team)}>
          Manage Team
        </Button>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 5: Create AgentHub page**

Create: `prowrl-studio/frontend/src/pages/AgentHubPage.tsx`

```tsx
import { useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, RefreshCw } from 'lucide-react';
import { AgentCard } from '@/components/agent-hub/AgentCard';
import { TeamCard } from '@/components/agent-hub/TeamCard';
import { useAgentHubStore } from '@/store/agentHubStore';
import type { Agent } from '@/api/agents';

export function AgentHubPage() {
  const navigate = useNavigate();
  const {
    agents, teams, loading, error, filter, statusFilter,
    setFilter, setStatusFilter, loadAgents, loadTeams,
  } = useAgentHubStore();

  useEffect(() => {
    loadAgents();
    loadTeams();
  }, [loadAgents, loadTeams]);

  const filteredAgents = useMemo(() => {
    return agents.filter((a) => {
      if (statusFilter !== 'all' && a.status !== statusFilter) return false;
      if (filter && !a.name.toLowerCase().includes(filter.toLowerCase())
          && !a.description.toLowerCase().includes(filter.toLowerCase())) return false;
      return true;
    });
  }, [agents, filter, statusFilter]);

  const handleRun = (agent: Agent) => {
    // TODO: Open run dialog
    console.log('Run agent:', agent.id);
  };

  const handleView = (agent: Agent) => {
    navigate(`/workspace/${agent.id}`);
  };

  const handleConfigure = (agent: Agent) => {
    // TODO: Open config panel
    console.log('Configure agent:', agent.id);
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Agent Hub</h1>
          <p className="text-muted-foreground">
            {agents.length} agents available
            {agents.filter(a => a.status === 'running').length > 0 &&
              ` \u00B7 ${agents.filter(a => a.status === 'running').length} running`}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => loadAgents()} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search agents..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as typeof statusFilter)}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="running">Running</SelectItem>
            <SelectItem value="idle">Idle</SelectItem>
            <SelectItem value="error">Error</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Teams */}
      {teams.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Teams</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {teams.map((team) => (
              <TeamCard
                key={team.id}
                team={team}
                agentCount={team.members.length}
                onManage={() => {}}
              />
            ))}
          </div>
        </div>
      )}

      {/* Agents */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Agents</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredAgents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onRun={handleRun}
              onView={handleView}
              onConfigure={handleConfigure}
            />
          ))}
          {filteredAgents.length === 0 && !loading && (
            <div className="col-span-full text-center py-12 text-muted-foreground">
              {filter || statusFilter !== 'all'
                ? 'No agents match your filters.'
                : 'No agents configured. Add agents in ProwlrBot settings.'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Add route to App.tsx**

In `prowrl-studio/frontend/src/App.tsx`, add:

```tsx
import { AgentHubPage } from './pages/AgentHubPage';

// Inside the Routes:
<Route path="/agents" element={<ProtectedRoute><AgentHubPage /></ProtectedRoute>} />
<Route path="/workspace/:agentId" element={<ProtectedRoute><div>Agent Workspace (Task 6)</div></ProtectedRoute>} />
```

Also add the nav link to the sidebar layout.

- [ ] **Step 7: Verify build**

Run:
```bash
cd /tmp/prowrl-studio-full
bun run typecheck
```
Expected: No new type errors.

- [ ] **Step 8: Commit**

```bash
cd /tmp/prowrl-studio-full
git add -A
git commit -m "feat(frontend): add Agent Hub page with cards, search, and filtering

- AgentCard: status indicator, capabilities, quick actions (Run/Live/Config)
- TeamCard: team view with member count
- AgentHubPage: grid layout, search, status filter
- agentHubStore: Zustand state management
- agents.ts: API client for ProwlrBot agent endpoints
- Route: /agents"
```

---

## Chunk 6: Agent Workspace (Core Tabs)

The flagship feature: per-agent workspace with live streaming tabs.

### Task 6.1: Create Agent Workspace Store and SSE Client

**Files:**
- Create: `prowrl-studio/frontend/src/store/agentWorkspaceStore.ts`
- Create: `prowrl-studio/frontend/src/api/agentStream.ts`

- [ ] **Step 1: Create SSE client**

Create: `prowrl-studio/frontend/src/api/agentStream.ts`

```typescript
export type AgentEventType =
  | 'thought' | 'tool_call' | 'tool_start'
  | 'terminal_output' | 'terminal_input'
  | 'browser_screenshot' | 'browser_action'
  | 'file_change' | 'chat_message'
  | 'memory_update' | 'cost_update'
  | 'log' | 'config_change' | 'status'
  | 'heartbeat';

export interface AgentEvent {
  type: AgentEventType;
  data: Record<string, unknown>;
  timestamp: number;
}

export type EventHandler = (event: AgentEvent) => void;

const PROWLRBOT_API = import.meta.env.VITE_PROWLRBOT_API_URL ?? 'http://localhost:8088';

export class AgentEventStream {
  private eventSource: EventSource | null = null;
  private handlers = new Map<string, Set<EventHandler>>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectDelay = 1000;

  constructor(
    private agentId: string,
    private onStatusChange?: (connected: boolean) => void,
  ) {}

  connect(): void {
    if (this.eventSource) this.disconnect();

    const token = localStorage.getItem('prowlrbot_token');
    const url = new URL(`${PROWLRBOT_API}/api/studio/agents/${this.agentId}/stream`);
    if (token) url.searchParams.set('token', token);

    this.eventSource = new EventSource(url.toString());

    this.eventSource.onopen = () => {
      this.reconnectDelay = 1000;
      this.onStatusChange?.(true);
    };

    this.eventSource.onerror = () => {
      this.onStatusChange?.(false);
      this.scheduleReconnect();
    };

    // Register handlers for all event types
    const eventTypes: AgentEventType[] = [
      'thought', 'tool_call', 'tool_start', 'terminal_output',
      'terminal_input', 'browser_screenshot', 'browser_action',
      'file_change', 'chat_message', 'memory_update', 'cost_update',
      'log', 'config_change', 'status', 'heartbeat',
    ];

    for (const type of eventTypes) {
      this.eventSource.addEventListener(type, (e) => {
        const event: AgentEvent = {
          type,
          data: JSON.parse((e as MessageEvent).data),
          timestamp: Date.now(),
        };
        this.emit(type, event);
        this.emit('*', event); // Wildcard for "all events"
      });
    }
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.onStatusChange?.(false);
  }

  on(type: string, handler: EventHandler): () => void {
    if (!this.handlers.has(type)) this.handlers.set(type, new Set());
    this.handlers.get(type)!.add(handler);
    return () => this.handlers.get(type)?.delete(handler);
  }

  private emit(type: string, event: AgentEvent): void {
    this.handlers.get(type)?.forEach((h) => h(event));
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, this.reconnectDelay);
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
  }
}
```

- [ ] **Step 2: Create workspace store**

Create: `prowrl-studio/frontend/src/store/agentWorkspaceStore.ts`

```typescript
import { create } from 'zustand';
import type { AgentEvent } from '@/api/agentStream';

export type WorkspaceTab =
  | 'screen' | 'code' | 'terminal' | 'browser'
  | 'files' | 'reasoning' | 'tools' | 'chat'
  | 'memory' | 'cost' | 'logs' | 'config';

export type LayoutMode = 'tile' | 'stack' | 'float' | 'split' | 'pip' | 'focus';

export interface ThoughtEntry {
  step: number;
  content: string;
  decision?: string;
  timestamp: number;
}

export interface ToolCallEntry {
  id: string;
  tool: string;
  inputs: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  duration_ms?: number;
  tokens?: number;
  timestamp: number;
  status: 'running' | 'completed' | 'error';
}

export interface CostSummary {
  tokens_in: number;
  tokens_out: number;
  total_cost: number;
  calls: number;
  model: string;
}

export interface LogEntry {
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

export interface FileEntry {
  path: string;
  op: 'create' | 'modify' | 'delete';
  content?: string;
  diff?: string;
  timestamp: number;
}

interface AgentWorkspaceState {
  // Active agents being viewed
  activeAgents: string[];
  activeTab: Record<string, WorkspaceTab>;
  layoutMode: LayoutMode;
  connected: Record<string, boolean>;

  // Per-agent data
  thoughts: Record<string, ThoughtEntry[]>;
  toolCalls: Record<string, ToolCallEntry[]>;
  cost: Record<string, CostSummary>;
  logs: Record<string, LogEntry[]>;
  files: Record<string, FileEntry[]>;
  chatMessages: Record<string, Array<{ from: string; content: string; timestamp: number }>>;
  screenshotUrl: Record<string, string>;
  terminalData: Record<string, string[]>;
  agentStatus: Record<string, string>;

  // Actions
  addAgent: (agentId: string) => void;
  removeAgent: (agentId: string) => void;
  setActiveTab: (agentId: string, tab: WorkspaceTab) => void;
  setLayoutMode: (mode: LayoutMode) => void;
  setConnected: (agentId: string, connected: boolean) => void;
  handleEvent: (agentId: string, event: AgentEvent) => void;
}

export const useAgentWorkspaceStore = create<AgentWorkspaceState>((set, get) => ({
  activeAgents: [],
  activeTab: {},
  layoutMode: 'stack',
  connected: {},
  thoughts: {},
  toolCalls: {},
  cost: {},
  logs: {},
  files: {},
  chatMessages: {},
  screenshotUrl: {},
  terminalData: {},
  agentStatus: {},

  addAgent: (agentId) => set((s) => ({
    activeAgents: s.activeAgents.includes(agentId) ? s.activeAgents : [...s.activeAgents, agentId],
    activeTab: { ...s.activeTab, [agentId]: 'screen' },
    thoughts: { ...s.thoughts, [agentId]: s.thoughts[agentId] ?? [] },
    toolCalls: { ...s.toolCalls, [agentId]: s.toolCalls[agentId] ?? [] },
    cost: { ...s.cost, [agentId]: s.cost[agentId] ?? { tokens_in: 0, tokens_out: 0, total_cost: 0, calls: 0, model: '' } },
    logs: { ...s.logs, [agentId]: s.logs[agentId] ?? [] },
    files: { ...s.files, [agentId]: s.files[agentId] ?? [] },
    chatMessages: { ...s.chatMessages, [agentId]: s.chatMessages[agentId] ?? [] },
    terminalData: { ...s.terminalData, [agentId]: s.terminalData[agentId] ?? [] },
  })),

  removeAgent: (agentId) => set((s) => ({
    activeAgents: s.activeAgents.filter((id) => id !== agentId),
  })),

  setActiveTab: (agentId, tab) => set((s) => ({
    activeTab: { ...s.activeTab, [agentId]: tab },
  })),

  setLayoutMode: (mode) => set({ layoutMode: mode }),

  setConnected: (agentId, connected) => set((s) => ({
    connected: { ...s.connected, [agentId]: connected },
  })),

  handleEvent: (agentId, event) => {
    switch (event.type) {
      case 'thought':
        set((s) => ({
          thoughts: {
            ...s.thoughts,
            [agentId]: [...(s.thoughts[agentId] ?? []), event.data as unknown as ThoughtEntry],
          },
        }));
        break;

      case 'tool_call':
        set((s) => ({
          toolCalls: {
            ...s.toolCalls,
            [agentId]: [...(s.toolCalls[agentId] ?? []), { ...event.data, status: 'completed', timestamp: event.timestamp } as unknown as ToolCallEntry],
          },
        }));
        break;

      case 'tool_start':
        set((s) => ({
          toolCalls: {
            ...s.toolCalls,
            [agentId]: [...(s.toolCalls[agentId] ?? []), { ...event.data, status: 'running', timestamp: event.timestamp } as unknown as ToolCallEntry],
          },
        }));
        break;

      case 'cost_update':
        set((s) => ({
          cost: {
            ...s.cost,
            [agentId]: {
              tokens_in: (s.cost[agentId]?.tokens_in ?? 0) + (event.data.tokens_in as number ?? 0),
              tokens_out: (s.cost[agentId]?.tokens_out ?? 0) + (event.data.tokens_out as number ?? 0),
              total_cost: event.data.total_cost as number ?? 0,
              calls: (s.cost[agentId]?.calls ?? 0) + 1,
              model: event.data.model as string ?? '',
            },
          },
        }));
        break;

      case 'log':
        set((s) => ({
          logs: {
            ...s.logs,
            [agentId]: [...(s.logs[agentId] ?? []).slice(-500), event.data as unknown as LogEntry],
          },
        }));
        break;

      case 'file_change':
        set((s) => ({
          files: {
            ...s.files,
            [agentId]: [...(s.files[agentId] ?? []), event.data as unknown as FileEntry],
          },
        }));
        break;

      case 'chat_message':
        set((s) => ({
          chatMessages: {
            ...s.chatMessages,
            [agentId]: [...(s.chatMessages[agentId] ?? []), { ...event.data, timestamp: event.timestamp } as { from: string; content: string; timestamp: number }],
          },
        }));
        break;

      case 'browser_screenshot':
        set((s) => ({
          screenshotUrl: { ...s.screenshotUrl, [agentId]: `data:image/png;base64,${event.data.png_base64}` },
        }));
        break;

      case 'terminal_output':
        set((s) => ({
          terminalData: {
            ...s.terminalData,
            [agentId]: [...(s.terminalData[agentId] ?? []).slice(-1000), atob(event.data.data as string)],
          },
        }));
        break;

      case 'status':
        set((s) => ({
          agentStatus: { ...s.agentStatus, [agentId]: event.data.state as string },
        }));
        break;
    }
  },
}));
```

- [ ] **Step 3: Commit**

```bash
cd /tmp/prowrl-studio-full
git add -A
git commit -m "feat(workspace): add agent workspace store and SSE event stream client"
```

### Task 6.2: Create Workspace UI Components

**Files:**
- Create: `prowrl-studio/frontend/src/pages/AgentWorkspacePage.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/WorkspaceTabBar.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/ScreenTab.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/ToolsTab.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/ReasoningTab.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/CostTab.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/LogsTab.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/TerminalTab.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/CodeTab.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/ChatTab.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/WorkspaceControls.tsx`
- Modify: `prowrl-studio/frontend/src/App.tsx`

- [ ] **Step 1: Create WorkspaceTabBar**

Create: `prowrl-studio/frontend/src/components/workspace/WorkspaceTabBar.tsx`

```tsx
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Monitor, Code, Terminal, Globe, FolderTree,
  Brain, Wrench, MessageCircle, Database, DollarSign,
  FileText, Settings,
} from 'lucide-react';
import type { WorkspaceTab } from '@/store/agentWorkspaceStore';

const tabs: { id: WorkspaceTab; label: string; icon: React.ElementType }[] = [
  { id: 'screen', label: 'Screen', icon: Monitor },
  { id: 'code', label: 'Code', icon: Code },
  { id: 'terminal', label: 'Terminal', icon: Terminal },
  { id: 'browser', label: 'Browser', icon: Globe },
  { id: 'files', label: 'Files', icon: FolderTree },
  { id: 'reasoning', label: 'Reasoning', icon: Brain },
  { id: 'tools', label: 'Tools', icon: Wrench },
  { id: 'chat', label: 'Chat', icon: MessageCircle },
  { id: 'memory', label: 'Memory', icon: Database },
  { id: 'cost', label: 'Cost', icon: DollarSign },
  { id: 'logs', label: 'Logs', icon: FileText },
  { id: 'config', label: 'Config', icon: Settings },
];

interface WorkspaceTabBarProps {
  activeTab: WorkspaceTab;
  onTabChange: (tab: WorkspaceTab) => void;
  notifications?: Partial<Record<WorkspaceTab, number>>;
}

export function WorkspaceTabBar({ activeTab, onTabChange, notifications }: WorkspaceTabBarProps) {
  return (
    <Tabs value={activeTab} onValueChange={(v) => onTabChange(v as WorkspaceTab)}>
      <TabsList className="h-9 bg-muted/50">
        {tabs.map(({ id, label, icon: Icon }) => (
          <TabsTrigger key={id} value={id} className="text-xs gap-1 px-2 relative">
            <Icon className="h-3.5 w-3.5" />
            <span className="hidden lg:inline">{label}</span>
            {notifications?.[id] && notifications[id]! > 0 && (
              <span className="absolute -top-0.5 -right-0.5 h-3.5 w-3.5 rounded-full bg-primary text-[9px] text-primary-foreground flex items-center justify-center">
                {notifications[id]! > 9 ? '9+' : notifications[id]}
              </span>
            )}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}
```

- [ ] **Step 2: Create individual tab components**

Create the following tab components. Each reads from the workspace store.

`prowrl-studio/frontend/src/components/workspace/tabs/ScreenTab.tsx`:
```tsx
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import { Button } from '@/components/ui/button';
import { Hand } from 'lucide-react';

export function ScreenTab({ agentId }: { agentId: string }) {
  const screenshotUrl = useAgentWorkspaceStore((s) => s.screenshotUrl[agentId]);
  const status = useAgentWorkspaceStore((s) => s.agentStatus[agentId]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 bg-black rounded-lg overflow-hidden relative">
        {screenshotUrl ? (
          <img src={screenshotUrl} alt="Agent screen" className="w-full h-full object-contain" />
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            {status === 'running' ? 'Waiting for screen capture...' : 'Agent not running'}
          </div>
        )}
        <div className="absolute bottom-3 right-3">
          <Button size="sm" variant="secondary" className="shadow-lg">
            <Hand className="h-3 w-3 mr-1" /> Take Control
          </Button>
        </div>
      </div>
    </div>
  );
}
```

`prowrl-studio/frontend/src/components/workspace/tabs/ReasoningTab.tsx`:
```tsx
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Brain } from 'lucide-react';

export function ReasoningTab({ agentId }: { agentId: string }) {
  const thoughts = useAgentWorkspaceStore((s) => s.thoughts[agentId] ?? []);

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-3">
        {thoughts.length === 0 ? (
          <div className="text-center text-muted-foreground py-12">
            <Brain className="h-8 w-8 mx-auto mb-2 opacity-50" />
            No reasoning steps yet.
          </div>
        ) : (
          thoughts.map((t, i) => (
            <div key={i} className="flex gap-3 text-sm">
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-mono">
                {t.step}
              </div>
              <div className="flex-1">
                <p className="text-foreground">{t.content}</p>
                {t.decision && (
                  <p className="text-xs text-muted-foreground mt-1">Decision: {t.decision}</p>
                )}
              </div>
              <span className="text-xs text-muted-foreground flex-shrink-0">
                {new Date(t.timestamp).toLocaleTimeString()}
              </span>
            </div>
          ))
        )}
      </div>
    </ScrollArea>
  );
}
```

`prowrl-studio/frontend/src/components/workspace/tabs/ToolsTab.tsx`:
```tsx
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronRight, Wrench, Loader2 } from 'lucide-react';
import { useState } from 'react';

export function ToolsTab({ agentId }: { agentId: string }) {
  const toolCalls = useAgentWorkspaceStore((s) => s.toolCalls[agentId] ?? []);

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-2">
        {toolCalls.length === 0 ? (
          <div className="text-center text-muted-foreground py-12">
            <Wrench className="h-8 w-8 mx-auto mb-2 opacity-50" />
            No tool calls yet.
          </div>
        ) : (
          toolCalls.map((tc, i) => (
            <ToolCallItem key={tc.id ?? i} call={tc} />
          ))
        )}
      </div>
    </ScrollArea>
  );
}

function ToolCallItem({ call }: { call: { tool: string; inputs: Record<string, unknown>; outputs?: Record<string, unknown>; duration_ms?: number; status: string; timestamp: number } }) {
  const [open, setOpen] = useState(false);

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger className="flex items-center gap-2 w-full p-2 rounded hover:bg-muted text-sm">
        <ChevronRight className={`h-3 w-3 transition-transform ${open ? 'rotate-90' : ''}`} />
        {call.status === 'running' ? (
          <Loader2 className="h-3 w-3 animate-spin text-yellow-500" />
        ) : (
          <Badge variant={call.status === 'completed' ? 'default' : 'destructive'} className="text-xs">
            {call.status}
          </Badge>
        )}
        <span className="font-mono">{call.tool}</span>
        {call.duration_ms != null && (
          <span className="text-xs text-muted-foreground ml-auto">{call.duration_ms}ms</span>
        )}
      </CollapsibleTrigger>
      <CollapsibleContent className="pl-8 pb-2">
        <div className="text-xs space-y-1">
          <p className="text-muted-foreground">Inputs:</p>
          <pre className="bg-muted p-2 rounded overflow-x-auto">{JSON.stringify(call.inputs, null, 2)}</pre>
          {call.outputs && (
            <>
              <p className="text-muted-foreground mt-2">Outputs:</p>
              <pre className="bg-muted p-2 rounded overflow-x-auto">{JSON.stringify(call.outputs, null, 2)}</pre>
            </>
          )}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
```

`prowrl-studio/frontend/src/components/workspace/tabs/CostTab.tsx`:
```tsx
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, ArrowDownToLine, ArrowUpFromLine, Zap } from 'lucide-react';

export function CostTab({ agentId }: { agentId: string }) {
  const cost = useAgentWorkspaceStore((s) => s.cost[agentId]);

  if (!cost) {
    return <div className="flex items-center justify-center h-full text-muted-foreground">No cost data yet.</div>;
  }

  return (
    <div className="p-4 grid grid-cols-2 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-1">
            <DollarSign className="h-4 w-4" /> Total Cost
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">${cost.total_cost.toFixed(4)}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-1">
            <Zap className="h-4 w-4" /> API Calls
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{cost.calls}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-1">
            <ArrowDownToLine className="h-4 w-4" /> Tokens In
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{cost.tokens_in.toLocaleString()}</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-1">
            <ArrowUpFromLine className="h-4 w-4" /> Tokens Out
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{cost.tokens_out.toLocaleString()}</p>
        </CardContent>
      </Card>
      {cost.model && (
        <Card className="col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Model</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg font-mono">{cost.model}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

`prowrl-studio/frontend/src/components/workspace/tabs/LogsTab.tsx`:
```tsx
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useState, useMemo } from 'react';

const levelColors = {
  debug: 'text-gray-400',
  info: 'text-blue-400',
  warn: 'text-yellow-400',
  error: 'text-red-400',
} as const;

export function LogsTab({ agentId }: { agentId: string }) {
  const logs = useAgentWorkspaceStore((s) => s.logs[agentId] ?? []);
  const [levelFilter, setLevelFilter] = useState<string>('all');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return logs.filter((l) => {
      if (levelFilter !== 'all' && l.level !== levelFilter) return false;
      if (search && !l.message.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [logs, levelFilter, search]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-2 p-2 border-b">
        <Input
          placeholder="Search logs..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 h-7 text-xs"
        />
        <Select value={levelFilter} onValueChange={setLevelFilter}>
          <SelectTrigger className="w-24 h-7 text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="debug">Debug</SelectItem>
            <SelectItem value="info">Info</SelectItem>
            <SelectItem value="warn">Warn</SelectItem>
            <SelectItem value="error">Error</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-2 font-mono text-xs space-y-0.5">
          {filtered.map((log, i) => (
            <div key={i} className="flex gap-2 hover:bg-muted/50 px-1 rounded">
              <span className="text-muted-foreground flex-shrink-0">
                {new Date(log.timestamp).toLocaleTimeString()}
              </span>
              <span className={`flex-shrink-0 uppercase w-12 ${levelColors[log.level]}`}>
                {log.level}
              </span>
              <span className="text-foreground">{log.message}</span>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
```

`prowrl-studio/frontend/src/components/workspace/tabs/ChatTab.tsx`:
```tsx
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Send } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const PROWLRBOT_API = import.meta.env.VITE_PROWLRBOT_API_URL ?? 'http://localhost:8088';

export function ChatTab({ agentId }: { agentId: string }) {
  const messages = useAgentWorkspaceStore((s) => s.chatMessages[agentId] ?? []);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const msg = input.trim();
    setInput('');

    const token = localStorage.getItem('prowlrbot_token');
    await fetch(`${PROWLRBOT_API}/api/studio/agents/${agentId}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ content: msg }),
    });
  };

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-3">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.from === 'human' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                msg.from === 'human' ? 'bg-primary text-primary-foreground' : 'bg-muted'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>
      <div className="flex gap-2 p-3 border-t">
        <Input
          placeholder="Message agent..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          className="flex-1"
        />
        <Button size="icon" onClick={sendMessage} disabled={!input.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create WorkspaceControls (bottom bar)**

Create: `prowrl-studio/frontend/src/components/workspace/WorkspaceControls.tsx`

```tsx
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Pause, Square, Hand, MessageCircle, DollarSign, Clock } from 'lucide-react';
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';

interface WorkspaceControlsProps {
  agentId: string;
  agentName: string;
}

export function WorkspaceControls({ agentId, agentName }: WorkspaceControlsProps) {
  const cost = useAgentWorkspaceStore((s) => s.cost[agentId]);
  const status = useAgentWorkspaceStore((s) => s.agentStatus[agentId] ?? 'idle');
  const connected = useAgentWorkspaceStore((s) => s.connected[agentId]);

  return (
    <div className="flex items-center gap-3 px-4 py-2 border-t bg-muted/30">
      <div className="flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-400'}`} />
        <span className="text-sm font-medium">{agentName}</span>
        <Badge variant="outline" className="text-xs">{status}</Badge>
      </div>

      <div className="flex items-center gap-1 ml-4">
        <Button size="sm" variant="outline" disabled={status !== 'running'}>
          <Pause className="h-3 w-3 mr-1" /> Pause
        </Button>
        <Button size="sm" variant="outline" disabled={status !== 'running'}>
          <Square className="h-3 w-3 mr-1" /> Stop
        </Button>
        <Button size="sm" variant="outline" disabled={status !== 'running'}>
          <Hand className="h-3 w-3 mr-1" /> Take Control
        </Button>
        <Button size="sm" variant="outline" disabled={status !== 'running'}>
          <MessageCircle className="h-3 w-3 mr-1" /> Message
        </Button>
      </div>

      <Select defaultValue="delegate">
        <SelectTrigger className="w-36 h-7 text-xs">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="watch">Watch</SelectItem>
          <SelectItem value="guide">Guide</SelectItem>
          <SelectItem value="delegate">Delegate</SelectItem>
          <SelectItem value="autonomous">Autonomous</SelectItem>
        </SelectContent>
      </Select>

      <div className="ml-auto flex items-center gap-4 text-xs text-muted-foreground">
        {cost && (
          <>
            <span className="flex items-center gap-1">
              <DollarSign className="h-3 w-3" /> ${cost.total_cost.toFixed(4)}
            </span>
            <span>{(cost.tokens_in + cost.tokens_out).toLocaleString()} tokens</span>
          </>
        )}
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" /> {cost?.model ?? 'N/A'}
        </span>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Create AgentWorkspacePage**

Create: `prowrl-studio/frontend/src/pages/AgentWorkspacePage.tsx`

```tsx
import { useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { WorkspaceTabBar } from '@/components/workspace/WorkspaceTabBar';
import { WorkspaceControls } from '@/components/workspace/WorkspaceControls';
import { ScreenTab } from '@/components/workspace/tabs/ScreenTab';
import { ReasoningTab } from '@/components/workspace/tabs/ReasoningTab';
import { ToolsTab } from '@/components/workspace/tabs/ToolsTab';
import { CostTab } from '@/components/workspace/tabs/CostTab';
import { LogsTab } from '@/components/workspace/tabs/LogsTab';
import { ChatTab } from '@/components/workspace/tabs/ChatTab';
import { TerminalTab } from '@/components/workspace/tabs/TerminalTab';
import { CodeTab } from '@/components/workspace/tabs/CodeTab';
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import { AgentEventStream } from '@/api/agentStream';

export function AgentWorkspacePage() {
  const { agentId } = useParams<{ agentId: string }>();
  const streamRef = useRef<AgentEventStream | null>(null);
  const { addAgent, setActiveTab, setConnected, handleEvent, activeTab } = useAgentWorkspaceStore();

  useEffect(() => {
    if (!agentId) return;

    addAgent(agentId);

    const stream = new AgentEventStream(agentId, (connected) => {
      setConnected(agentId, connected);
    });

    stream.on('*', (event) => {
      handleEvent(agentId, event);
    });

    stream.connect();
    streamRef.current = stream;

    return () => {
      stream.disconnect();
      streamRef.current = null;
    };
  }, [agentId, addAgent, setConnected, handleEvent]);

  if (!agentId) return null;

  const currentTab = activeTab[agentId] ?? 'screen';

  const renderTab = () => {
    switch (currentTab) {
      case 'screen': return <ScreenTab agentId={agentId} />;
      case 'reasoning': return <ReasoningTab agentId={agentId} />;
      case 'tools': return <ToolsTab agentId={agentId} />;
      case 'cost': return <CostTab agentId={agentId} />;
      case 'logs': return <LogsTab agentId={agentId} />;
      case 'chat': return <ChatTab agentId={agentId} />;
      case 'code': return <CodeTab agentId={agentId} />;
      case 'terminal': return <TerminalTab agentId={agentId} />;
      case 'browser': return <div className="p-4 text-muted-foreground">Browser view — Phase 2</div>;
      case 'files': return <div className="p-4 text-muted-foreground">File tree — Phase 2</div>;
      case 'memory': return <div className="p-4 text-muted-foreground">Memory view — Phase 2</div>;
      case 'config': return <div className="p-4 text-muted-foreground">Config editor — Phase 2</div>;
      default: return null;
    }
  };

  return (
    <div className="flex flex-col h-full">
      <WorkspaceTabBar
        activeTab={currentTab}
        onTabChange={(tab) => setActiveTab(agentId, tab)}
      />
      <div className="flex-1 overflow-hidden">
        {renderTab()}
      </div>
      <WorkspaceControls agentId={agentId} agentName={agentId} />
    </div>
  );
}
```

- [ ] **Step 5: Update App.tsx route**

In `prowrl-studio/frontend/src/App.tsx`, replace the placeholder workspace route:

```tsx
import { AgentWorkspacePage } from './pages/AgentWorkspacePage';

// Replace the placeholder:
<Route path="/workspace/:agentId" element={<ProtectedRoute><AgentWorkspacePage /></ProtectedRoute>} />
```

- [ ] **Step 6: Verify build**

Run:
```bash
cd /tmp/prowrl-studio-full
bun run typecheck
```
Expected: No new type errors.

- [ ] **Step 7: Commit**

```bash
cd /tmp/prowrl-studio-full
git add -A
git commit -m "feat(workspace): add Agent Workspace with 6 live tabs and controls

Tabs implemented:
- Screen: live browser/desktop view with Take Control
- Reasoning: step-by-step thought timeline
- Tools: expandable tool call history with inputs/outputs
- Cost: real-time token/cost tracking cards
- Logs: filterable structured log stream
- Chat: message agent mid-run

Tabs deferred to Phase 2: Code (Monaco), Terminal (xterm.js),
Browser, Files, Memory, Config.

Controls: pause/stop/take-control, autonomy dropdown,
cost display, model info."
```

### Task 6.3: Terminal Tab (xterm.js)

**Files:**
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/TerminalTab.tsx`

- [ ] **Step 1: Create TerminalTab with xterm.js**

Create: `prowrl-studio/frontend/src/components/workspace/tabs/TerminalTab.tsx`

```tsx
import { useEffect, useRef } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import '@xterm/xterm/css/xterm.css';

export function TerminalTab({ agentId }: { agentId: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const fitRef = useRef<FitAddon | null>(null);
  const terminalData = useAgentWorkspaceStore((s) => s.terminalData[agentId] ?? []);
  const lastWrittenRef = useRef(0);

  useEffect(() => {
    if (!containerRef.current) return;

    const term = new Terminal({
      theme: {
        background: '#1a1b26',
        foreground: '#a9b1d6',
        cursor: '#c0caf5',
      },
      fontSize: 13,
      fontFamily: 'JetBrains Mono, Menlo, monospace',
      cursorBlink: true,
      convertEol: true,
    });

    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(containerRef.current);
    fit.fit();

    termRef.current = term;
    fitRef.current = fit;

    const resizeObserver = new ResizeObserver(() => fit.fit());
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      term.dispose();
      termRef.current = null;
      fitRef.current = null;
      lastWrittenRef.current = 0;
    };
  }, []);

  // Write new terminal data as it arrives
  useEffect(() => {
    if (!termRef.current) return;
    const newData = terminalData.slice(lastWrittenRef.current);
    for (const chunk of newData) {
      termRef.current.write(chunk);
    }
    lastWrittenRef.current = terminalData.length;
  }, [terminalData]);

  return (
    <div ref={containerRef} className="h-full w-full bg-[#1a1b26]" />
  );
}
```

- [ ] **Step 2: Verify xterm deps exist**

Run:
```bash
cd /tmp/prowrl-studio-full
grep -q "xterm" frontend/package.json && echo "xterm found" || bun add @xterm/xterm @xterm/addon-fit --cwd frontend
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat(workspace): add Terminal tab with xterm.js"
```

### Task 6.4: Code Tab (Monaco - read-only)

**Files:**
- Create: `prowrl-studio/frontend/src/components/workspace/tabs/CodeTab.tsx`

- [ ] **Step 1: Create CodeTab with Monaco**

Create: `prowrl-studio/frontend/src/components/workspace/tabs/CodeTab.tsx`

```tsx
import { useMemo } from 'react';
import Editor from '@monaco-editor/react';
import { useAgentWorkspaceStore } from '@/store/agentWorkspaceStore';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Code, FilePlus, FileEdit, FileX } from 'lucide-react';
import { useState } from 'react';

const opIcons = {
  create: FilePlus,
  modify: FileEdit,
  delete: FileX,
} as const;

const opColors = {
  create: 'text-green-500',
  modify: 'text-yellow-500',
  delete: 'text-red-500',
} as const;

function detectLanguage(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase() ?? '';
  const map: Record<string, string> = {
    ts: 'typescript', tsx: 'typescript', js: 'javascript', jsx: 'javascript',
    py: 'python', rs: 'rust', go: 'go', java: 'java', rb: 'ruby',
    json: 'json', yaml: 'yaml', yml: 'yaml', md: 'markdown',
    html: 'html', css: 'css', sql: 'sql', sh: 'shell',
  };
  return map[ext] ?? 'plaintext';
}

export function CodeTab({ agentId }: { agentId: string }) {
  const files = useAgentWorkspaceStore((s) => s.files[agentId] ?? []);
  const [selectedFile, setSelectedFile] = useState<number | null>(null);

  const latestFiles = useMemo(() => {
    // Dedupe by path, keep latest
    const map = new Map<string, typeof files[number]>();
    for (const f of files) {
      map.set(f.path, f);
    }
    return Array.from(map.values());
  }, [files]);

  const selected = selectedFile !== null ? latestFiles[selectedFile] : latestFiles[latestFiles.length - 1];

  if (latestFiles.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <div className="text-center">
          <Code className="h-8 w-8 mx-auto mb-2 opacity-50" />
          No file changes yet.
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full">
      {/* File list sidebar */}
      <ScrollArea className="w-56 border-r">
        <div className="p-2 space-y-0.5">
          {latestFiles.map((f, i) => {
            const Icon = opIcons[f.op];
            const isSelected = selected?.path === f.path;
            return (
              <button
                key={f.path}
                onClick={() => setSelectedFile(i)}
                className={`flex items-center gap-2 w-full text-left px-2 py-1 rounded text-xs hover:bg-muted ${isSelected ? 'bg-muted' : ''}`}
              >
                <Icon className={`h-3 w-3 flex-shrink-0 ${opColors[f.op]}`} />
                <span className="truncate">{f.path.split('/').pop()}</span>
              </button>
            );
          })}
        </div>
      </ScrollArea>

      {/* Editor */}
      <div className="flex-1 flex flex-col">
        {selected && (
          <>
            <div className="flex items-center gap-2 px-3 py-1.5 border-b text-xs text-muted-foreground">
              <span className="font-mono">{selected.path}</span>
              <Badge variant="outline" className="text-xs">{selected.op}</Badge>
            </div>
            <div className="flex-1">
              <Editor
                height="100%"
                language={detectLanguage(selected.path)}
                value={selected.content ?? selected.diff ?? '// No content available'}
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 13,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                }}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify Monaco dep exists**

Run:
```bash
cd /tmp/prowrl-studio-full
grep -q "monaco" frontend/package.json && echo "monaco found" || bun add @monaco-editor/react --cwd frontend
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat(workspace): add Code tab with Monaco editor (read-only file viewer)"
```

### Task 6.5: Layout Modes (Tile + Stack)

**Files:**
- Create: `prowrl-studio/frontend/src/components/workspace/LayoutSwitcher.tsx`
- Create: `prowrl-studio/frontend/src/components/workspace/TileLayout.tsx`
- Modify: `prowrl-studio/frontend/src/pages/AgentWorkspacePage.tsx`

- [ ] **Step 1: Create LayoutSwitcher**

Create: `prowrl-studio/frontend/src/components/workspace/LayoutSwitcher.tsx`

```tsx
import { Button } from '@/components/ui/button';
import { LayoutGrid, Layers } from 'lucide-react';
import { useAgentWorkspaceStore, type LayoutMode } from '@/store/agentWorkspaceStore';

const layouts: { id: LayoutMode; label: string; icon: React.ElementType }[] = [
  { id: 'tile', label: 'Tile', icon: LayoutGrid },
  { id: 'stack', label: 'Stack', icon: Layers },
];

export function LayoutSwitcher() {
  const { layoutMode, setLayoutMode } = useAgentWorkspaceStore();

  return (
    <div className="flex items-center gap-1">
      {layouts.map(({ id, label, icon: Icon }) => (
        <Button
          key={id}
          size="sm"
          variant={layoutMode === id ? 'default' : 'ghost'}
          onClick={() => setLayoutMode(id)}
          className="h-7 px-2 text-xs"
        >
          <Icon className="h-3.5 w-3.5 mr-1" />
          {label}
        </Button>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create TileLayout**

Create: `prowrl-studio/frontend/src/components/workspace/TileLayout.tsx`

```tsx
import { WorkspaceTabBar } from './WorkspaceTabBar';
import { WorkspaceControls } from './WorkspaceControls';
import { ScreenTab } from './tabs/ScreenTab';
import { ReasoningTab } from './tabs/ReasoningTab';
import { ToolsTab } from './tabs/ToolsTab';
import { CostTab } from './tabs/CostTab';
import { LogsTab } from './tabs/LogsTab';
import { ChatTab } from './tabs/ChatTab';
import { TerminalTab } from './tabs/TerminalTab';
import { CodeTab } from './tabs/CodeTab';
import { useAgentWorkspaceStore, type WorkspaceTab } from '@/store/agentWorkspaceStore';

function renderTab(tab: WorkspaceTab, agentId: string) {
  switch (tab) {
    case 'screen': return <ScreenTab agentId={agentId} />;
    case 'reasoning': return <ReasoningTab agentId={agentId} />;
    case 'tools': return <ToolsTab agentId={agentId} />;
    case 'cost': return <CostTab agentId={agentId} />;
    case 'logs': return <LogsTab agentId={agentId} />;
    case 'chat': return <ChatTab agentId={agentId} />;
    case 'terminal': return <TerminalTab agentId={agentId} />;
    case 'code': return <CodeTab agentId={agentId} />;
    default: return <div className="p-4 text-muted-foreground">Coming in Phase 2</div>;
  }
}

interface TileLayoutProps {
  agentIds: string[];
}

export function TileLayout({ agentIds }: TileLayoutProps) {
  const { activeTab, setActiveTab } = useAgentWorkspaceStore();

  const cols = agentIds.length <= 1 ? 1 : agentIds.length <= 4 ? 2 : 3;

  return (
    <div
      className="grid h-full gap-1 p-1"
      style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
    >
      {agentIds.map((agentId) => {
        const tab = activeTab[agentId] ?? 'screen';
        return (
          <div key={agentId} className="flex flex-col border rounded overflow-hidden min-h-0">
            <div className="flex items-center justify-between px-2 py-1 bg-muted/50 border-b">
              <span className="text-xs font-medium truncate">{agentId}</span>
            </div>
            <WorkspaceTabBar activeTab={tab} onTabChange={(t) => setActiveTab(agentId, t)} />
            <div className="flex-1 overflow-hidden">
              {renderTab(tab, agentId)}
            </div>
            <WorkspaceControls agentId={agentId} agentName={agentId} />
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 3: Update AgentWorkspacePage to support layouts**

Replace the `AgentWorkspacePage` in the plan to use layout modes:

In `prowrl-studio/frontend/src/pages/AgentWorkspacePage.tsx`, add at the top of the component before the return:

```tsx
import { LayoutSwitcher } from '@/components/workspace/LayoutSwitcher';
import { TileLayout } from '@/components/workspace/TileLayout';

// Inside the component, before the return:
const layoutMode = useAgentWorkspaceStore((s) => s.layoutMode);
const activeAgents = useAgentWorkspaceStore((s) => s.activeAgents);

// The return now switches on layout mode:
if (layoutMode === 'tile' && activeAgents.length > 1) {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-2 border-b">
        <h2 className="text-sm font-semibold">Agent Workspace</h2>
        <LayoutSwitcher />
      </div>
      <div className="flex-1 overflow-hidden">
        <TileLayout agentIds={activeAgents} />
      </div>
    </div>
  );
}

// Otherwise render single-agent stack mode (existing code)
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat(workspace): add Tile and Stack layout modes with LayoutSwitcher"
```

### Task 6.6: Collaboration Canvas (Read-Only)

**Files:**
- Create: `prowrl-studio/frontend/src/pages/CollaborationCanvasPage.tsx`
- Create: `prowrl-studio/frontend/src/store/canvasStore.ts`
- Modify: `prowrl-studio/frontend/src/App.tsx` (add route)

- [ ] **Step 1: Create canvas store**

Create: `prowrl-studio/frontend/src/store/canvasStore.ts`

```typescript
import { create } from 'zustand';

export interface Finding {
  id: string;
  agent_id: string;
  agent_name: string;
  type: 'text' | 'code' | 'image' | 'link' | 'file';
  content: string;
  confidence: number;
  tags: string[];
  timestamp: number;
  status: 'pending' | 'approved' | 'rejected';
}

interface CanvasState {
  findings: Finding[];
  loading: boolean;
  tagFilter: string[];
  loadFindings: () => Promise<void>;
  updateFindingStatus: (id: string, status: 'approved' | 'rejected') => void;
  setTagFilter: (tags: string[]) => void;
}

const PROWLRBOT_API = import.meta.env.VITE_PROWLRBOT_API_URL ?? 'http://localhost:8088';

export const useCanvasStore = create<CanvasState>((set, get) => ({
  findings: [],
  loading: false,
  tagFilter: [],

  loadFindings: async () => {
    set({ loading: true });
    try {
      const token = localStorage.getItem('prowlrbot_token');
      // Fetch shared findings from ProwlrHub
      const resp = await fetch(`${PROWLRBOT_API}/api/hub/findings`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (resp.ok) {
        const data = await resp.json();
        set({ findings: data, loading: false });
      } else {
        set({ loading: false });
      }
    } catch {
      set({ loading: false });
    }
  },

  updateFindingStatus: (id, status) => {
    set((s) => ({
      findings: s.findings.map((f) => f.id === id ? { ...f, status } : f),
    }));
    // TODO: POST status update to backend
  },

  setTagFilter: (tags) => set({ tagFilter: tags }),
}));
```

- [ ] **Step 2: Create CollaborationCanvasPage**

Create: `prowrl-studio/frontend/src/pages/CollaborationCanvasPage.tsx`

```tsx
import { useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Check, X, Bot, RefreshCw } from 'lucide-react';
import { useCanvasStore, type Finding } from '@/store/canvasStore';

export function CollaborationCanvasPage() {
  const { findings, loading, tagFilter, loadFindings, updateFindingStatus } = useCanvasStore();

  useEffect(() => {
    loadFindings();
  }, [loadFindings]);

  const filtered = useMemo(() => {
    if (tagFilter.length === 0) return findings;
    return findings.filter((f) => f.tags.some((t) => tagFilter.includes(t)));
  }, [findings, tagFilter]);

  const allTags = useMemo(() => {
    const tags = new Set<string>();
    findings.forEach((f) => f.tags.forEach((t) => tags.add(t)));
    return Array.from(tags).sort();
  }, [findings]);

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Collaboration Canvas</h1>
          <p className="text-muted-foreground">
            {findings.length} findings from {new Set(findings.map((f) => f.agent_id)).size} agents
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadFindings} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-1 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </Button>
      </div>

      {/* Tag filter */}
      {allTags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {allTags.map((tag) => (
            <Badge
              key={tag}
              variant={tagFilter.includes(tag) ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => {
                const { setTagFilter, tagFilter: tf } = useCanvasStore.getState();
                setTagFilter(tf.includes(tag) ? tf.filter((t) => t !== tag) : [...tf, tag]);
              }}
            >
              {tag}
            </Badge>
          ))}
        </div>
      )}

      {/* Findings timeline */}
      <ScrollArea className="flex-1">
        <div className="space-y-3">
          {filtered.length === 0 && !loading && (
            <div className="text-center py-12 text-muted-foreground">
              No findings yet. Agents share findings via ROAR protocol during runs.
            </div>
          )}
          {filtered.map((finding) => (
            <FindingCard
              key={finding.id}
              finding={finding}
              onApprove={() => updateFindingStatus(finding.id, 'approved')}
              onReject={() => updateFindingStatus(finding.id, 'rejected')}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

function FindingCard({ finding, onApprove, onReject }: { finding: Finding; onApprove: () => void; onReject: () => void }) {
  const statusColors = {
    pending: 'border-l-yellow-500',
    approved: 'border-l-green-500',
    rejected: 'border-l-red-500',
  };

  return (
    <Card className={`border-l-4 ${statusColors[finding.status]}`}>
      <CardHeader className="flex flex-row items-center gap-2 py-2 pb-1">
        <Bot className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">{finding.agent_name}</span>
        <Badge variant="outline" className="text-xs">{finding.type}</Badge>
        <span className="text-xs text-muted-foreground ml-auto">
          {new Date(finding.timestamp).toLocaleTimeString()}
        </span>
        {finding.confidence < 1 && (
          <Badge variant="secondary" className="text-xs">
            {Math.round(finding.confidence * 100)}%
          </Badge>
        )}
      </CardHeader>
      <CardContent className="py-2">
        {finding.type === 'code' ? (
          <pre className="bg-muted p-3 rounded text-xs overflow-x-auto">{finding.content}</pre>
        ) : (
          <p className="text-sm">{finding.content}</p>
        )}
        <div className="flex items-center gap-2 mt-3">
          <div className="flex gap-1">
            {finding.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
            ))}
          </div>
          {finding.status === 'pending' && (
            <div className="flex gap-1 ml-auto">
              <Button size="sm" variant="outline" onClick={onApprove}>
                <Check className="h-3 w-3 mr-1" /> Approve
              </Button>
              <Button size="sm" variant="ghost" onClick={onReject}>
                <X className="h-3 w-3 mr-1" /> Reject
              </Button>
            </div>
          )}
          {finding.status !== 'pending' && (
            <Badge variant={finding.status === 'approved' ? 'default' : 'destructive'} className="ml-auto text-xs">
              {finding.status}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 3: Add route and nav**

In `prowrl-studio/frontend/src/App.tsx`:

```tsx
import { CollaborationCanvasPage } from './pages/CollaborationCanvasPage';

// Add route:
<Route path="/canvas" element={<ProtectedRoute><CollaborationCanvasPage /></ProtectedRoute>} />
```

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat(canvas): add read-only Collaboration Canvas with findings timeline"
```

---

## Chunk 7: Integration Testing and Verification

### Task 7.1: ProwlrBot Test Suite Verification

- [ ] **Step 1: Run full ProwlrBot test suite**

Run:
```bash
cd /Users/nunu/prowlrbot/prowlrbot
pytest --tb=short 2>&1 | tail -15
```
Expected: 713+ tests pass, no regressions from studio router additions.

- [ ] **Step 2: Run Studio typecheck**

Run:
```bash
cd /tmp/prowrl-studio-full
bun run typecheck
```
Expected: No errors.

- [ ] **Step 3: Run Studio tests**

Run:
```bash
cd /tmp/prowrl-studio-full
bun run test 2>&1 | tail -20
```
Expected: Existing tests pass.

- [ ] **Step 4: Verify Studio starts**

Run:
```bash
cd /tmp/prowrl-studio-full
timeout 10 bun run --cwd backend start 2>&1 | head -20 || true
```
Expected: NestJS starts on port 3211.

- [ ] **Step 5: Verify ProwlrBot starts and Studio endpoints work**

Run:
```bash
cd /Users/nunu/prowlrbot/prowlrbot
prowlr app &
sleep 3
curl -s http://127.0.0.1:8088/api/studio/health | python3 -m json.tool
curl -s http://127.0.0.1:8088/api/studio/agents | python3 -m json.tool
kill %1
```
Expected: Health returns `{"status": "ok", ...}`. Agents returns `[]` or list of agents.

- [ ] **Step 6: Push ProwlrBot changes**

```bash
cd /Users/nunu/prowlrbot/prowlrbot
git push origin main
```

- [ ] **Step 7: Push Studio changes**

```bash
cd /tmp/prowrl-studio-full
git push origin main
```

---

## Summary

| Chunk | Tasks | What It Delivers |
|-------|-------|-----------------|
| 1. Rebranding | 1.1 | All 400+ ShipSec references replaced |
| 2. Security | 2.1-2.5 | 4 Critical + 6 High findings fixed |
| 3. CLI + API | 3.1-3.2 | `prowlr studio` command + Studio REST/SSE endpoints |
| 4. Auth | 4.1 | ProwlrBot JWT auth provider in Studio |
| 5. Agent Hub | 5.1 | Agent cards page with search/filter |
| 6. Workspace | 6.1-6.6 | 8 live tabs (Screen, Code, Terminal, Tools, Cost, Logs, Chat, Reasoning) + Tile/Stack layouts + Collaboration Canvas + SSE streaming |
| 7. Integration | 7.1 | Full test suite verification |
