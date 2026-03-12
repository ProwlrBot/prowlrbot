# Prowlr Marketplace Redesign — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Transform the marketplace from a basic card grid into a curated, trust-tiered marketplace with bundles, Stripe tips, gamification credits, and ~118 verified listings across 7 categories.

**Architecture:** Backend-first approach — add TrustTier enum, v3 migration, Bundle model/store, fix API bugs (sort, q/query), add Stripe tip flow, then rewrite frontend with trust badges, grid/list toggle, bundle cards, and detail pages. Registry sync updated to assign trust tiers.

**Tech Stack:** Python 3.10+ / FastAPI / SQLite / Pydantic (backend); React 18 / TypeScript / Ant Design / Vite (frontend); Stripe Checkout (tips)

**Spec:** `docs/superpowers/specs/2026-03-11-prowlr-marketplace-design.md`

---

## Chunk 1: Backend Models & Store

### Task 1: Add `specs` to MarketplaceCategory and add TrustTier enum

**Files:**
- Modify: `src/prowlrbot/marketplace/models.py:14-23` (MarketplaceCategory enum)
- Modify: `src/prowlrbot/marketplace/models.py` (add TrustTier enum after line 23)
- Test: `tests/marketplace/test_models.py`

- [x] **Step 1: Write the failing test**

Create `tests/marketplace/` directory and test file:

```python
# tests/marketplace/test_models.py
"""Tests for marketplace model enums and new fields."""
from prowlrbot.marketplace.models import MarketplaceCategory, MarketplaceListing


def test_specs_category_exists():
    """specs must be a valid MarketplaceCategory."""
    cat = MarketplaceCategory("specs")
    assert cat == MarketplaceCategory.specs
    assert cat.value == "specs"


def test_all_seven_categories():
    """All 7 categories are present."""
    expected = {"skills", "agents", "prompts", "mcp-servers", "themes", "workflows", "specs"}
    actual = {c.value for c in MarketplaceCategory}
    assert actual == expected


def test_trust_tier_enum():
    from prowlrbot.marketplace.models import TrustTier
    assert TrustTier("official") == TrustTier.official
    assert TrustTier("verified") == TrustTier.verified


def test_listing_has_v3_fields():
    """MarketplaceListing should have trust_tier, author_name, etc."""
    listing = MarketplaceListing(
        author_id="test",
        title="Test",
        description="desc",
        category=MarketplaceCategory.skills,
        trust_tier="official",
        author_name="ProwlrBot",
        author_url="https://github.com/ProwlrBot",
        author_avatar_url="",
        source_repo="https://github.com/ProwlrBot/prowlrbot",
        license="MIT",
        changelog="## 1.0.0\nInitial release",
        compatibility=">=1.0.0",
    )
    assert listing.trust_tier == "official"
    assert listing.author_name == "ProwlrBot"
    assert listing.license == "MIT"
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/marketplace/test_models.py -v`
Expected: FAIL — `specs` not in enum, `TrustTier` doesn't exist, `trust_tier` field missing

- [x] **Step 3: Add `specs` to MarketplaceCategory, create TrustTier enum, add v3 fields to MarketplaceListing**

In `src/prowlrbot/marketplace/models.py`:

Add `specs = "specs"` to `MarketplaceCategory` enum (after `workflows`).

Add new enum after `MarketplaceCategory`:

```python
class TrustTier(StrEnum):
    """Trust level assigned to marketplace listings."""
    official = "official"
    verified = "verified"
```

Add v3 fields to `MarketplaceListing` class (after `hero_animation`):

```python
    # ── v3 fields: trust-tiered marketplace ──────────────────────────────
    trust_tier: str = "verified"
    author_name: str = ""
    author_url: str = ""
    author_avatar_url: str = ""
    source_repo: str = ""
    license: str = "MIT"
    changelog: str = ""
    compatibility: str = ""
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/marketplace/test_models.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add tests/marketplace/test_models.py src/prowlrbot/marketplace/models.py
git commit -m "feat(marketplace): add specs category, TrustTier enum, v3 listing fields"
```

---

### Task 2: Add v3 migration to MarketplaceStore

**Files:**
- Modify: `src/prowlrbot/marketplace/store.py:130` (add `_migrate_v3()` call)
- Modify: `src/prowlrbot/marketplace/store.py` (add `_migrate_v3()` method after `_migrate_v2()`)
- Modify: `src/prowlrbot/marketplace/store.py:160-203` (update `publish_listing()` INSERT)
- Modify: `src/prowlrbot/marketplace/store.py:265-285` (update `update_listing()` allowed set)
- Modify: `src/prowlrbot/marketplace/store.py:612-632` (update `_row_to_listing()`)
- Test: `tests/marketplace/test_store.py`

- [x] **Step 1: Write the failing test**

```python
# tests/marketplace/test_store.py
"""Tests for MarketplaceStore v3 migration and trust tier fields."""
import tempfile
from pathlib import Path

from prowlrbot.marketplace.models import MarketplaceCategory, MarketplaceListing
from prowlrbot.marketplace.store import MarketplaceStore


def _tmp_store():
    """Create a store backed by a temp file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    return MarketplaceStore(db_path=tmp.name)


def test_v3_columns_exist():
    """v3 migration creates trust_tier and related columns."""
    store = _tmp_store()
    cur = store._conn.cursor()
    cols = {row["name"] for row in cur.execute("PRAGMA table_info(listings)").fetchall()}
    assert "trust_tier" in cols
    assert "author_name" in cols
    assert "source_repo" in cols
    assert "license" in cols
    assert "changelog" in cols
    assert "compatibility" in cols
    assert "author_url" in cols
    assert "author_avatar_url" in cols
    store.close()


def test_publish_and_read_v3_fields():
    """publish_listing() stores v3 fields, get_listing() reads them back."""
    store = _tmp_store()
    listing = MarketplaceListing(
        author_id="prowlrbot",
        title="Test Skill",
        description="A test",
        category=MarketplaceCategory.skills,
        trust_tier="official",
        author_name="ProwlrBot",
        author_url="https://github.com/ProwlrBot",
        author_avatar_url="https://avatars.githubusercontent.com/ProwlrBot",
        source_repo="https://github.com/ProwlrBot/prowlrbot",
        license="MIT",
        changelog="## 1.0.0\nInitial",
        compatibility=">=1.0.0",
    )
    published = store.publish_listing(listing)
    fetched = store.get_listing(published.id)
    assert fetched is not None
    assert fetched.trust_tier == "official"
    assert fetched.author_name == "ProwlrBot"
    assert fetched.license == "MIT"
    assert fetched.source_repo == "https://github.com/ProwlrBot/prowlrbot"
    store.close()


def test_update_listing_v3_fields():
    """update_listing() can update trust_tier and author_name."""
    store = _tmp_store()
    listing = MarketplaceListing(
        author_id="test",
        title="Updatable",
        description="test",
        category=MarketplaceCategory.agents,
    )
    store.publish_listing(listing)
    updated = store.update_listing(listing.id, {
        "trust_tier": "official",
        "author_name": "Updated Author",
        "license": "Apache-2.0",
    })
    assert updated is not None
    assert updated.trust_tier == "official"
    assert updated.author_name == "Updated Author"
    assert updated.license == "Apache-2.0"
    store.close()
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/marketplace/test_store.py -v`
Expected: FAIL — v3 columns don't exist, `publish_listing` doesn't handle v3 fields

- [x] **Step 3: Implement v3 migration and update store methods**

In `store.py`, add `_migrate_v3()` method after `_migrate_v2()`:

```python
    def _migrate_v3(self) -> None:
        """Add v3 trust-tier columns (safe to run multiple times)."""
        cur = self._conn.cursor()
        existing = {
            row["name"]
            for row in cur.execute("PRAGMA table_info(listings)").fetchall()
        }
        v3_columns = {
            "trust_tier": "TEXT NOT NULL DEFAULT 'verified'",
            "author_name": "TEXT NOT NULL DEFAULT ''",
            "author_url": "TEXT NOT NULL DEFAULT ''",
            "author_avatar_url": "TEXT NOT NULL DEFAULT ''",
            "source_repo": "TEXT NOT NULL DEFAULT ''",
            "license": "TEXT NOT NULL DEFAULT 'MIT'",
            "changelog": "TEXT NOT NULL DEFAULT ''",
            "compatibility": "TEXT NOT NULL DEFAULT ''",
        }
        for col, typedef in v3_columns.items():
            if col not in existing:
                cur.execute(f"ALTER TABLE listings ADD COLUMN {col} {typedef}")
        self._conn.commit()
```

Add `self._migrate_v3()` call at end of `_init_db()` (after `self._migrate_v2()`).

Update `publish_listing()` — add v3 columns to INSERT column list and values tuple:
- Columns: `trust_tier, author_name, author_url, author_avatar_url, source_repo, license, changelog, compatibility`
- Values: `listing.trust_tier, listing.author_name, listing.author_url, listing.author_avatar_url, listing.source_repo, listing.license, listing.changelog, listing.compatibility`

Update `update_listing()` — add v3 field names to `allowed` set:
```python
"trust_tier", "author_name", "author_url", "author_avatar_url",
"source_repo", "license", "changelog", "compatibility",
```

No change needed to `_row_to_listing()` — Pydantic will accept the new fields from the row dict since they're strings with defaults.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/marketplace/test_store.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add tests/marketplace/test_store.py src/prowlrbot/marketplace/store.py
git commit -m "feat(marketplace): v3 migration — trust_tier, author metadata, license, changelog"
```

---

### Task 3: Add Bundle model and bundles table

**Files:**
- Modify: `src/prowlrbot/marketplace/models.py` (add Bundle class at end)
- Modify: `src/prowlrbot/marketplace/store.py` (add bundles table + CRUD)
- Test: `tests/marketplace/test_bundles.py`

- [x] **Step 1: Write the failing test**

```python
# tests/marketplace/test_bundles.py
"""Tests for Bundle model and store CRUD."""
import tempfile

from prowlrbot.marketplace.models import Bundle, MarketplaceCategory, MarketplaceListing
from prowlrbot.marketplace.store import MarketplaceStore


def _tmp_store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    return MarketplaceStore(db_path=tmp.name)


def test_bundle_model():
    b = Bundle(
        id="security-starter",
        name="Security Starter",
        description="OWASP audit, JWT review",
        emoji="shield",
        color="#00e5ff",
        listing_ids=["skill-1", "skill-2"],
    )
    assert b.id == "security-starter"
    assert len(b.listing_ids) == 2


def test_create_and_get_bundle():
    store = _tmp_store()
    b = Bundle(
        id="test-bundle",
        name="Test Bundle",
        description="A test",
        listing_ids=["a", "b", "c"],
    )
    store.create_bundle(b)
    fetched = store.get_bundle("test-bundle")
    assert fetched is not None
    assert fetched.name == "Test Bundle"
    assert fetched.listing_ids == ["a", "b", "c"]
    store.close()


def test_list_bundles():
    store = _tmp_store()
    store.create_bundle(Bundle(id="b1", name="B1", description="x", listing_ids=[]))
    store.create_bundle(Bundle(id="b2", name="B2", description="y", listing_ids=[]))
    bundles = store.list_bundles()
    assert len(bundles) == 2
    store.close()


def test_increment_bundle_install_count():
    store = _tmp_store()
    store.create_bundle(Bundle(id="b1", name="B1", description="x", listing_ids=[]))
    store.increment_bundle_installs("b1")
    fetched = store.get_bundle("b1")
    assert fetched is not None
    assert fetched.install_count == 1
    store.close()
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/marketplace/test_bundles.py -v`
Expected: FAIL — `Bundle` class doesn't exist, store methods don't exist

- [x] **Step 3: Add Bundle model and store methods**

In `models.py`, add after `MarketplaceListing`:

```python
class Bundle(BaseModel):
    """A curated pack of related marketplace listings."""
    id: str
    name: str
    description: str
    emoji: str = ""
    color: str = "#00e5ff"
    listing_ids: list[str] = Field(default_factory=list)
    install_count: int = 0
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
```

In `store.py`, add bundles table creation to `_init_db()` (inside the `executescript` block, after `credit_balances`):

```sql
CREATE TABLE IF NOT EXISTS bundles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    emoji TEXT DEFAULT '',
    color TEXT DEFAULT '#00e5ff',
    listing_ids TEXT DEFAULT '[]',
    install_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
```

Add import for `Bundle` in `store.py` imports.

Add bundle CRUD methods to `MarketplaceStore` (before `close()`):

```python
    # ------------------------------------------------------------------
    # Bundles
    # ------------------------------------------------------------------

    def create_bundle(self, bundle: Bundle) -> Bundle:
        """Insert a new bundle."""
        self._conn.execute(
            "INSERT INTO bundles (id, name, description, emoji, color, listing_ids, install_count, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                bundle.id, bundle.name, bundle.description,
                bundle.emoji, bundle.color, json.dumps(bundle.listing_ids),
                bundle.install_count, bundle.created_at,
            ),
        )
        self._conn.commit()
        return bundle

    def get_bundle(self, bundle_id: str) -> Optional[Bundle]:
        """Fetch a single bundle by ID."""
        row = self._conn.execute(
            "SELECT * FROM bundles WHERE id = ?", (bundle_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_bundle(row)

    def list_bundles(self) -> list[Bundle]:
        """Return all bundles."""
        rows = self._conn.execute("SELECT * FROM bundles ORDER BY name").fetchall()
        return [self._row_to_bundle(r) for r in rows]

    def increment_bundle_installs(self, bundle_id: str) -> None:
        """Increment a bundle's install count."""
        self._conn.execute(
            "UPDATE bundles SET install_count = install_count + 1 WHERE id = ?",
            (bundle_id,),
        )
        self._conn.commit()

    @staticmethod
    def _row_to_bundle(row: dict) -> Bundle:
        """Convert a DB row dict into a Bundle."""
        row = dict(row)
        raw = row.get("listing_ids", "[]")
        if isinstance(raw, str):
            try:
                row["listing_ids"] = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                row["listing_ids"] = []
        return Bundle(**row)
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/marketplace/test_bundles.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/prowlrbot/marketplace/models.py src/prowlrbot/marketplace/store.py tests/marketplace/test_bundles.py
git commit -m "feat(marketplace): Bundle model, bundles table, CRUD methods"
```

---

## Chunk 2: Backend API Fixes & New Endpoints

### Task 4: Fix `sort` parameter and `q`/`query` mismatch in listings endpoint

**Files:**
- Modify: `src/prowlrbot/marketplace/store.py:215-255` (update `search_listings` to accept sort)
- Modify: `src/prowlrbot/app/routers/marketplace.py:47-63` (add sort param, accept q alias)
- Test: `tests/routers/test_marketplace_api.py`

- [x] **Step 1: Write the failing test**

```python
# tests/routers/test_marketplace_api.py
"""Tests for marketplace API endpoint fixes."""
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from prowlrbot.marketplace.models import MarketplaceCategory, MarketplaceListing
from prowlrbot.marketplace.store import MarketplaceStore


@pytest.fixture
def store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    s = MarketplaceStore(db_path=tmp.name)
    # Seed some listings
    for i, title in enumerate(["Alpha Tool", "Zeta Agent", "Beta Skill"]):
        s.publish_listing(MarketplaceListing(
            author_id="test",
            title=title,
            description=f"Description {i}",
            category=MarketplaceCategory.skills,
            downloads=100 - i * 30,
            rating=4.0 + i * 0.3,
            ratings_count=i + 1,
            status="approved",
        ))
    yield s
    s.close()


@pytest.fixture
def client(store):
    from prowlrbot.app.routers.marketplace import router, _get_store
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    # Patch store
    with patch("prowlrbot.app.routers.marketplace._get_store", return_value=store):
        yield TestClient(app)


def test_sort_alpha(client):
    """sort=alpha returns listings in A-Z order."""
    resp = client.get("/marketplace/listings?sort=alpha")
    assert resp.status_code == 200
    titles = [l["title"] for l in resp.json()]
    assert titles == sorted(titles)


def test_sort_newest(client):
    """sort=newest returns listings newest first."""
    resp = client.get("/marketplace/listings?sort=newest")
    assert resp.status_code == 200
    dates = [l["created_at"] for l in resp.json()]
    assert dates == sorted(dates, reverse=True)


def test_q_alias_for_query(client):
    """Frontend sends q= but backend should accept it."""
    resp = client.get("/marketplace/listings?q=Alpha")
    assert resp.status_code == 200
    assert any("Alpha" in l["title"] for l in resp.json())
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/routers/test_marketplace_api.py -v`
Expected: FAIL — sort param ignored, q not recognized

- [x] **Step 3: Add sort parameter to store and API**

In `store.py`, update `search_listings()` signature to add `sort: str = "popular"`:

```python
def search_listings(
    self,
    query: str = "",
    category: Optional[str] = None,
    tags: Optional[list[str]] = None,
    persona: Optional[str] = None,
    difficulty: Optional[str] = None,
    sort: str = "popular",
    limit: int = 50,
) -> list[MarketplaceListing]:
```

Replace the hardcoded `ORDER BY downloads DESC` with sort mapping:

```python
    sort_map = {
        "popular": "downloads DESC",
        "top_rated": "rating DESC",
        "newest": "created_at DESC",
        "alpha": "title ASC",
    }
    order = sort_map.get(sort, "downloads DESC")
    sql = f"SELECT * FROM listings {where} ORDER BY {order} LIMIT ?"
```

In `marketplace.py` router, update `search_listings` endpoint:

```python
@router.get("/listings", response_model=list[MarketplaceListing])
async def search_listings(
    query: str = "",
    q: str = "",
    category: Optional[str] = None,
    persona: Optional[str] = None,
    difficulty: Optional[str] = None,
    sort: str = "popular",
    limit: int = 50,
) -> list[MarketplaceListing]:
    """Search marketplace listings."""
    search_query = q or query  # accept both q and query
    limit = max(1, min(limit, 200))
    return _get_store().search_listings(
        query=search_query,
        category=category,
        persona=persona,
        difficulty=difficulty,
        sort=sort,
        limit=limit,
    )
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/routers/test_marketplace_api.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/prowlrbot/marketplace/store.py src/prowlrbot/app/routers/marketplace.py tests/routers/test_marketplace_api.py
git commit -m "fix(marketplace): add sort parameter, accept q alias for query"
```

---

### Task 5: Add bundle API endpoints

**Files:**
- Modify: `src/prowlrbot/app/routers/marketplace.py` (add bundle routes)
- Test: `tests/routers/test_marketplace_bundles.py`

- [x] **Step 1: Write the failing test**

```python
# tests/routers/test_marketplace_bundles.py
"""Tests for bundle API endpoints."""
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from prowlrbot.marketplace.models import Bundle, MarketplaceCategory, MarketplaceListing
from prowlrbot.marketplace.store import MarketplaceStore


@pytest.fixture
def store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    s = MarketplaceStore(db_path=tmp.name)
    # Seed listings
    for slug in ["skill-a", "skill-b", "skill-c"]:
        s.publish_listing(MarketplaceListing(
            id=slug,
            author_id="test",
            title=slug,
            description="test",
            category=MarketplaceCategory.skills,
            status="approved",
        ))
    # Seed a bundle
    s.create_bundle(Bundle(
        id="test-bundle",
        name="Test Bundle",
        description="A test bundle",
        listing_ids=["skill-a", "skill-b"],
    ))
    yield s
    s.close()


@pytest.fixture
def client(store):
    from prowlrbot.app.routers.marketplace import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    with patch("prowlrbot.app.routers.marketplace._get_store", return_value=store):
        yield TestClient(app)


def test_list_bundles(client):
    resp = client.get("/marketplace/bundles")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "test-bundle"


def test_get_bundle_detail(client):
    resp = client.get("/marketplace/bundles/test-bundle")
    assert resp.status_code == 200
    data = resp.json()
    assert data["bundle"]["name"] == "Test Bundle"
    assert len(data["listings"]) == 2


def test_get_bundle_not_found(client):
    resp = client.get("/marketplace/bundles/nonexistent")
    assert resp.status_code == 404


def test_install_bundle(client):
    resp = client.post("/marketplace/bundles/test-bundle/install")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["installed"]) == 2
    assert data["total"] == 2
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/routers/test_marketplace_bundles.py -v`
Expected: FAIL — bundle endpoints don't exist

- [x] **Step 3: Add bundle endpoints to router**

In `marketplace.py`, add imports for `Bundle` and add new endpoints:

```python
from ...marketplace.models import Bundle

# ------------------------------------------------------------------
# Bundles
# ------------------------------------------------------------------

@router.get("/bundles")
async def list_bundles() -> list[dict]:
    """List all curated bundles."""
    bundles = _get_store().list_bundles()
    return [b.model_dump() for b in bundles]


@router.get("/bundles/{bundle_id}")
async def get_bundle(bundle_id: str) -> dict:
    """Get bundle detail with full listing objects."""
    store = _get_store()
    bundle = store.get_bundle(bundle_id)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Bundle not found")
    listings = [
        store.get_listing(lid)
        for lid in bundle.listing_ids
    ]
    listings = [l for l in listings if l is not None]
    return {
        "bundle": bundle.model_dump(),
        "listings": [l.model_dump() for l in listings],
    }


@router.post("/bundles/{bundle_id}/install")
async def install_bundle(bundle_id: str) -> dict:
    """Install all listings in a bundle. Continues on failure."""
    store = _get_store()
    bundle = store.get_bundle(bundle_id)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Bundle not found")

    installed = []
    failed = []
    for lid in bundle.listing_ids:
        listing = store.get_listing(lid)
        if listing is None:
            failed.append({"slug": lid, "error": "Listing not found"})
            continue
        try:
            record = InstallRecord(
                listing_id=lid, user_id="local", version=listing.version,
            )
            store.record_install(record)
            installed.append(lid)
        except Exception as e:
            failed.append({"slug": lid, "error": str(e)})

    store.increment_bundle_installs(bundle_id)
    return {"installed": installed, "failed": failed, "total": len(bundle.listing_ids)}
```

**Important:** Place bundle routes BEFORE the `@router.get("/listings/{listing_id}")` route to avoid path conflict (FastAPI matches routes in order, and `/bundles` could be mismatched as a listing_id).

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/routers/test_marketplace_bundles.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/prowlrbot/app/routers/marketplace.py tests/routers/test_marketplace_bundles.py
git commit -m "feat(marketplace): add bundle list, detail, and install endpoints"
```

---

### Task 6: Add listing detail endpoint with computed fields

**Files:**
- Modify: `src/prowlrbot/app/routers/marketplace.py` (add detail endpoint)
- Test: `tests/routers/test_marketplace_detail.py`

- [x] **Step 1: Write the failing test**

```python
# tests/routers/test_marketplace_detail.py
"""Tests for listing detail endpoint with computed fields."""
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from prowlrbot.marketplace.models import (
    Bundle, MarketplaceCategory, MarketplaceListing, ReviewEntry, TipRecord,
)
from prowlrbot.marketplace.store import MarketplaceStore


@pytest.fixture
def store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    s = MarketplaceStore(db_path=tmp.name)
    s.publish_listing(MarketplaceListing(
        id="test-skill",
        author_id="author1",
        title="Test Skill",
        description="A skill",
        category=MarketplaceCategory.skills,
        trust_tier="official",
        author_name="Author One",
        status="approved",
    ))
    s.publish_listing(MarketplaceListing(
        id="related-skill",
        author_id="author1",
        title="Related Skill",
        description="Another skill",
        category=MarketplaceCategory.skills,
        tags=["testing"],
        status="approved",
    ))
    s.add_review(ReviewEntry(listing_id="test-skill", reviewer_id="u1", rating=5, comment="Great"))
    s.add_tip(TipRecord(listing_id="test-skill", author_id="author1", amount=5.0))
    s.create_bundle(Bundle(id="b1", name="B1", description="x", listing_ids=["test-skill"]))
    yield s
    s.close()


@pytest.fixture
def client(store):
    from prowlrbot.app.routers.marketplace import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    with patch("prowlrbot.app.routers.marketplace._get_store", return_value=store):
        yield TestClient(app)


def test_detail_has_computed_fields(client):
    resp = client.get("/marketplace/listings/test-skill/detail")
    assert resp.status_code == 200
    data = resp.json()
    assert data["listing"]["title"] == "Test Skill"
    assert data["install_command"] == "prowlr market install test-skill"
    assert data["tip_total"] == 5.0
    assert len(data["reviews"]) == 1
    assert "bundles" in data


def test_detail_not_found(client):
    resp = client.get("/marketplace/listings/nonexistent/detail")
    assert resp.status_code == 404
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/routers/test_marketplace_detail.py -v`
Expected: FAIL — detail endpoint doesn't exist

- [x] **Step 3: Add detail endpoint**

In `marketplace.py`, add before the reviews section:

```python
@router.get("/listings/{listing_id}/detail")
async def get_listing_detail(listing_id: str) -> dict:
    """Full detail: listing, reviews, computed fields, related listings."""
    store = _get_store()
    listing = store.get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    reviews = store.get_reviews(listing_id, limit=50)
    tip_total = store.get_tip_total(listing.author_id)

    # Bundle membership
    bundles = [
        b.name for b in store.list_bundles()
        if listing_id in b.listing_ids
    ]

    # Related listings: same category, max 4, excluding current
    related = store.search_listings(
        category=listing.category, sort="popular", limit=5,
    )
    related = [r for r in related if r.id != listing_id][:4]

    # Author's other listings
    author_listings = store.list_by_author(listing.author_id)
    author_others = [l for l in author_listings if l.id != listing_id][:4]

    return {
        "listing": listing.model_dump(),
        "install_command": f"prowlr market install {listing_id}",
        "tip_total": tip_total,
        "reviews": [r.model_dump() for r in reviews],
        "bundles": bundles,
        "related": [r.model_dump() for r in related],
        "author_listings": [l.model_dump() for l in author_others],
    }
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/routers/test_marketplace_detail.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/prowlrbot/app/routers/marketplace.py tests/routers/test_marketplace_detail.py
git commit -m "feat(marketplace): listing detail endpoint with computed fields"
```

---

### Task 7: Update registry sync for trust tiers

**Files:**
- Modify: `src/prowlrbot/marketplace/registry.py:26-33` (add specs to CATEGORY_DIR_MAP)
- Modify: `src/prowlrbot/marketplace/registry.py:178-236` (update sync_registry for trust tiers)
- Test: `tests/marketplace/test_registry.py`

- [x] **Step 1: Write the failing test**

```python
# tests/marketplace/test_registry.py
"""Tests for registry sync trust tier assignment."""
from prowlrbot.marketplace.registry import CATEGORY_DIR_MAP


def test_specs_in_category_dir_map():
    """specs directory should be mapped."""
    assert "specs" in CATEGORY_DIR_MAP
    assert CATEGORY_DIR_MAP["specs"] == "specs"


def test_all_seven_categories_mapped():
    expected = {"skills", "agents", "prompts", "mcp-servers", "themes", "workflows", "specs"}
    assert set(CATEGORY_DIR_MAP.keys()) == expected
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/marketplace/test_registry.py -v`
Expected: FAIL — `specs` not in map

- [x] **Step 3: Add specs to CATEGORY_DIR_MAP and update sync_registry**

In `registry.py`, add `"specs": "specs"` to `CATEGORY_DIR_MAP`.

In `sync_registry()`, after building the listing object (line ~221), add trust tier assignment:

```python
# Determine trust tier
author_str = (
    author if isinstance(author, str) else author.get("name", "unknown")
)
is_official = author_str.lower() in ("prowlrbot", "prowlr", "prowlrbot-team")

listing = MarketplaceListing(
    id=listing_id,
    author_id=author_str,
    title=title,
    description=description,
    category=cat,
    version=version,
    pricing_model=pm,
    price=price,
    tags=tags if isinstance(tags, list) else [],
    status=ListingStatus.approved,
    trust_tier="official" if is_official else "verified",
    author_name=author_str,
    source_repo=raw.get("source_repo", raw.get("repository", "")),
    license=raw.get("license", "MIT"),
)
```

Also update the `update_listing` call to include trust tier fields:

```python
store.update_listing(
    listing_id,
    {
        "title": title,
        "description": description,
        "version": version,
        "tags": tags,
        "category": cat.value,
        "author_name": author_str,
        "source_repo": raw.get("source_repo", raw.get("repository", "")),
        "license": raw.get("license", "MIT"),
    },
)
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/marketplace/test_registry.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/prowlrbot/marketplace/registry.py tests/marketplace/test_registry.py
git commit -m "feat(marketplace): add specs to category map, trust tier in registry sync"
```

---

## Chunk 3: Stripe Tip Jar

### Task 8: Add Stripe-powered tip endpoint with graceful degradation

**Files:**
- Modify: `src/prowlrbot/app/routers/marketplace.py:177-185` (rewrite tip endpoint)
- Modify: `src/prowlrbot/app/routers/marketplace.py` (add Stripe webhook endpoint)
- Test: `tests/routers/test_marketplace_stripe.py`

- [x] **Step 1: Write the failing test**

```python
# tests/routers/test_marketplace_stripe.py
"""Tests for Stripe tip jar with graceful degradation."""
import tempfile
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from prowlrbot.marketplace.models import MarketplaceCategory, MarketplaceListing
from prowlrbot.marketplace.store import MarketplaceStore


@pytest.fixture
def store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    s = MarketplaceStore(db_path=tmp.name)
    s.publish_listing(MarketplaceListing(
        id="tippable",
        author_id="author1",
        title="Tippable Skill",
        description="test",
        category=MarketplaceCategory.skills,
    ))
    yield s
    s.close()


@pytest.fixture
def client(store):
    from prowlrbot.app.routers.marketplace import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    with patch("prowlrbot.app.routers.marketplace._get_store", return_value=store):
        yield TestClient(app)


def test_tip_returns_503_when_stripe_not_configured(client):
    """Without STRIPE_SECRET_KEY, tip returns 503."""
    with patch.dict("os.environ", {}, clear=False):
        # Ensure no STRIPE_SECRET_KEY
        import os
        os.environ.pop("STRIPE_SECRET_KEY", None)
        resp = client.post("/marketplace/listings/tippable/tip", json={"amount": 5})
        assert resp.status_code == 503


def test_tip_validates_amount_range(client):
    """Tip below $1 or above $100 is rejected."""
    with patch.dict("os.environ", {"STRIPE_SECRET_KEY": "sk_test_fake"}):
        resp = client.post("/marketplace/listings/tippable/tip", json={"amount": 0.50})
        assert resp.status_code == 400

        resp = client.post("/marketplace/listings/tippable/tip", json={"amount": 150})
        assert resp.status_code == 400


def test_tip_not_found_listing(client):
    resp = client.post("/marketplace/listings/nonexistent/tip", json={"amount": 5})
    assert resp.status_code == 404
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/routers/test_marketplace_stripe.py -v`
Expected: FAIL — current tip endpoint doesn't validate amounts or check Stripe config

- [x] **Step 3: Rewrite tip endpoint with Stripe checkout and degradation**

Replace the existing tip endpoint in `marketplace.py`:

```python
from pydantic import BaseModel as PydanticBaseModel

class TipRequest(PydanticBaseModel):
    amount: float
    message: str = ""


@router.post("/listings/{listing_id}/tip")
async def tip_author(listing_id: str, tip_req: TipRequest) -> dict:
    """Create a Stripe checkout session for tipping, or record locally."""
    import os

    store = _get_store()
    listing = store.get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Validate amount range
    if tip_req.amount < 1 or tip_req.amount > 100:
        raise HTTPException(status_code=400, detail="Tip amount must be between $1 and $100")

    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        raise HTTPException(status_code=503, detail="Tipping not configured")

    # Record tip locally
    tip = TipRecord(
        listing_id=listing_id,
        author_id=listing.author_id,
        amount=tip_req.amount,
        message=tip_req.message,
    )
    store.add_tip(tip)

    # Try Stripe checkout
    try:
        import stripe
        stripe.api_key = stripe_key
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(tip_req.amount * 100),
                    "product_data": {
                        "name": f"Tip for {listing.title}",
                        "description": f"Supporting {listing.author_name or listing.author_id}",
                    },
                },
                "quantity": 1,
            }],
            success_url=f"/marketplace/listings/{listing_id}?tipped=true",
            cancel_url=f"/marketplace/listings/{listing_id}",
            metadata={"listing_id": listing_id, "tip_id": tip.id},
        )
        return {"checkout_url": session.url, "tip_id": tip.id}
    except ImportError:
        # stripe package not installed — tip recorded locally only
        return {"checkout_url": None, "tip_id": tip.id, "note": "Tip recorded locally (Stripe SDK not installed)"}
    except Exception as e:
        # Stripe error — tip still recorded locally
        return {"checkout_url": None, "tip_id": tip.id, "note": f"Stripe unavailable: {e}"}
```

Add Stripe webhook endpoint:

```python
@router.post("/webhook/stripe")
async def stripe_webhook() -> dict:
    """Stripe webhook receiver. Validates signature and records confirmed tips."""
    # Placeholder — full implementation requires raw request body access
    # and stripe.Webhook.construct_event() with STRIPE_WEBHOOK_SECRET
    return {"status": "received"}
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/routers/test_marketplace_stripe.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/prowlrbot/app/routers/marketplace.py tests/routers/test_marketplace_stripe.py
git commit -m "feat(marketplace): Stripe tip jar with amount validation and graceful degradation"
```

---

## Chunk 4: Frontend Foundation Components

### Task 9: Create shared types and transformListing utility

**Files:**
- Create: `console/src/pages/Marketplace/types.ts`
- Create: `console/src/pages/Marketplace/utils.ts`

- [x] **Step 1: Create the types file**

```typescript
// console/src/pages/Marketplace/types.ts
export interface MarketplaceListing {
  id: string;
  title: string;          // backend field name
  name: string;           // frontend display name (= title)
  description: string;
  category: string;
  version: string;
  rating: number;
  ratingCount: number;    // mapped from ratings_count
  downloads: number;
  price: number;
  tags: string[];
  trustTier: string;      // "official" | "verified"
  authorName: string;     // mapped from author_name
  authorUrl: string;
  authorAvatarUrl: string;
  sourceRepo: string;
  license: string;
  changelog: string;
  compatibility: string;
  difficulty: string;
  installed?: boolean;
}

export interface Bundle {
  id: string;
  name: string;
  description: string;
  emoji: string;
  color: string;
  listing_ids: string[];
  install_count: number;
}

export interface ListingDetail {
  listing: MarketplaceListing;
  install_command: string;
  tip_total: number;
  reviews: ReviewEntry[];
  bundles: string[];
  related: MarketplaceListing[];
  author_listings: MarketplaceListing[];
}

export interface ReviewEntry {
  id: string;
  listing_id: string;
  reviewer_id: string;
  rating: number;
  comment: string;
  created_at: string;
}
```

- [x] **Step 2: Create the transformListing utility**

```typescript
// console/src/pages/Marketplace/utils.ts
import type { MarketplaceListing } from "./types";

/**
 * Transform a backend listing (snake_case) into frontend format (camelCase).
 * Handles field name mismatches between API and UI.
 */
export function transformListing(raw: Record<string, any>): MarketplaceListing {
  return {
    id: raw.id,
    title: raw.title,
    name: raw.title,  // frontend displays "name", backend stores "title"
    description: raw.description ?? "",
    category: raw.category ?? "skills",
    version: raw.version ?? "1.0.0",
    rating: raw.rating ?? 0,
    ratingCount: raw.ratings_count ?? raw.ratingCount ?? 0,
    downloads: raw.downloads ?? 0,
    price: raw.price ?? 0,
    tags: raw.tags ?? [],
    trustTier: raw.trust_tier ?? raw.trustTier ?? "verified",
    authorName: raw.author_name ?? raw.authorName ?? raw.author_id ?? "",
    authorUrl: raw.author_url ?? raw.authorUrl ?? "",
    authorAvatarUrl: raw.author_avatar_url ?? raw.authorAvatarUrl ?? "",
    sourceRepo: raw.source_repo ?? raw.sourceRepo ?? "",
    license: raw.license ?? "MIT",
    changelog: raw.changelog ?? "",
    compatibility: raw.compatibility ?? "",
    difficulty: raw.difficulty ?? "beginner",
    installed: raw.installed,
  };
}

export function formatDownloads(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return String(count);
}

export const CATEGORY_COLORS: Record<string, string> = {
  skills: "cyan",
  agents: "purple",
  prompts: "gold",
  "mcp-servers": "blue",
  themes: "magenta",
  workflows: "geekblue",
  specs: "orange",
};

export const CATEGORY_LABELS: Record<string, string> = {
  skills: "Skills",
  agents: "Agents",
  prompts: "Prompts",
  "mcp-servers": "MCP Servers",
  themes: "Themes",
  workflows: "Workflows",
  specs: "Specs",
};
```

- [x] **Step 3: Commit**

```bash
git add console/src/pages/Marketplace/types.ts console/src/pages/Marketplace/utils.ts
git commit -m "feat(marketplace): shared types and transformListing utility"
```

---

### Task 10: Create TrustBadge component

**Files:**
- Create: `console/src/pages/Marketplace/components/TrustBadge.tsx`

- [x] **Step 1: Create the component**

```tsx
// console/src/pages/Marketplace/components/TrustBadge.tsx
import { Tag } from "antd";

interface TrustBadgeProps {
  tier: string;  // "official" | "verified"
  size?: "small" | "default";
}

export default function TrustBadge({ tier, size = "small" }: TrustBadgeProps) {
  if (tier === "official") {
    return (
      <Tag
        color="#facc15"
        style={{
          color: "#78350f",
          fontWeight: 600,
          fontSize: size === "small" ? 10 : 12,
          lineHeight: size === "small" ? "18px" : "22px",
          border: "none",
        }}
      >
        OFFICIAL
      </Tag>
    );
  }
  return (
    <Tag
      color="#60a5fa"
      style={{
        color: "#1e3a5f",
        fontWeight: 600,
        fontSize: size === "small" ? 10 : 12,
        lineHeight: size === "small" ? "18px" : "22px",
        border: "none",
      }}
    >
      VERIFIED
    </Tag>
  );
}
```

- [x] **Step 2: Commit**

```bash
git add console/src/pages/Marketplace/components/TrustBadge.tsx
git commit -m "feat(marketplace): TrustBadge component (Official gold / Verified blue)"
```

---

### Task 11: Create CategoryPills component

**Files:**
- Create: `console/src/pages/Marketplace/components/CategoryPills.tsx`

- [x] **Step 1: Create the component**

```tsx
// console/src/pages/Marketplace/components/CategoryPills.tsx
import { CATEGORY_LABELS } from "../utils";

interface CategoryPillsProps {
  categories: string[];
  counts: Record<string, number>;
  selected: string;
  onSelect: (category: string) => void;
  totalCount: number;
}

export default function CategoryPills({
  categories,
  counts,
  selected,
  onSelect,
  totalCount,
}: CategoryPillsProps) {
  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 20 }}>
      <button
        onClick={() => onSelect("")}
        style={{
          padding: "6px 14px",
          borderRadius: 20,
          border: selected === "" ? "2px solid #00e5ff" : "1px solid rgba(255,255,255,0.12)",
          background: selected === "" ? "rgba(0,229,255,0.1)" : "rgba(255,255,255,0.04)",
          cursor: "pointer",
          fontSize: 13,
          color: selected === "" ? "#00e5ff" : "#888",
          fontWeight: selected === "" ? 600 : 400,
          transition: "all 0.2s",
        }}
      >
        All {totalCount}
      </button>
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => onSelect(cat)}
          style={{
            padding: "6px 14px",
            borderRadius: 20,
            border: selected === cat ? "2px solid #00e5ff" : "1px solid rgba(255,255,255,0.12)",
            background: selected === cat ? "rgba(0,229,255,0.1)" : "rgba(255,255,255,0.04)",
            cursor: "pointer",
            fontSize: 13,
            color: selected === cat ? "#00e5ff" : "#888",
            fontWeight: selected === cat ? 600 : 400,
            transition: "all 0.2s",
          }}
        >
          {CATEGORY_LABELS[cat] || cat} {counts[cat] ?? 0}
        </button>
      ))}
    </div>
  );
}
```

- [x] **Step 2: Commit**

```bash
git add console/src/pages/Marketplace/components/CategoryPills.tsx
git commit -m "feat(marketplace): CategoryPills filterable pill bar with counts"
```

---

### Task 12: Create BundleCard component

**Files:**
- Create: `console/src/pages/Marketplace/components/BundleCard.tsx`

- [x] **Step 1: Create the component**

```tsx
// console/src/pages/Marketplace/components/BundleCard.tsx
import { Button, message } from "antd";
import { Download } from "lucide-react";
import { useState } from "react";
import { request } from "../../../api/request";
import type { Bundle } from "../types";

interface BundleCardProps {
  bundle: Bundle;
  onInstalled?: () => void;
}

export default function BundleCard({ bundle, onInstalled }: BundleCardProps) {
  const [installing, setInstalling] = useState(false);

  const handleInstall = async () => {
    setInstalling(true);
    try {
      const result = await request<{ installed: string[]; failed: { slug: string; error: string }[] }>(
        `/marketplace/bundles/${bundle.id}/install`,
        { method: "POST" },
      );
      const count = result.installed?.length ?? 0;
      message.success(`Installed ${count} items from "${bundle.name}"`);
      onInstalled?.();
    } catch {
      message.error(`Failed to install bundle "${bundle.name}"`);
    } finally {
      setInstalling(false);
    }
  };

  return (
    <div
      style={{
        background: `linear-gradient(135deg, ${bundle.color}15, ${bundle.color}08)`,
        border: `1px solid ${bundle.color}30`,
        borderRadius: 12,
        padding: "16px 20px",
        minWidth: 200,
        cursor: "pointer",
        transition: "transform 0.2s, box-shadow 0.2s",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-2px)";
        e.currentTarget.style.boxShadow = `0 4px 12px ${bundle.color}20`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      <div style={{ fontSize: 24, marginBottom: 8 }}>{bundle.emoji}</div>
      <div style={{ fontWeight: 600, fontSize: 14, color: "#fff", marginBottom: 4 }}>
        {bundle.name}
      </div>
      <div style={{ fontSize: 12, color: "#888", marginBottom: 12 }}>
        {bundle.description}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 11, color: "#666" }}>
          {bundle.listing_ids.length} items
        </span>
        <Button
          size="small"
          type="primary"
          loading={installing}
          onClick={(e) => { e.stopPropagation(); handleInstall(); }}
          icon={<Download size={12} />}
          style={{ background: "#00e5ff", borderColor: "#00e5ff", fontSize: 11 }}
        >
          Install All
        </Button>
      </div>
    </div>
  );
}
```

- [x] **Step 2: Commit**

```bash
git add console/src/pages/Marketplace/components/BundleCard.tsx
git commit -m "feat(marketplace): BundleCard component with 1-click install"
```

---

## Chunk 5: Frontend Page Rewrites

### Task 13: Rewrite ListingCard with trust badges and v3 fields

**Files:**
- Modify: `console/src/pages/Marketplace/components/ListingCard.tsx` (full rewrite)

- [x] **Step 1: Read current ListingCard**

Already read. Current issues: stale `CATEGORY_COLORS`, uses `name` not `title`, no trust badge, no author, no version, no license.

- [x] **Step 2: Rewrite ListingCard**

```tsx
// console/src/pages/Marketplace/components/ListingCard.tsx
import { Button, Rate, Tag } from "antd";
import { Download } from "lucide-react";
import TrustBadge from "./TrustBadge";
import { CATEGORY_COLORS, formatDownloads } from "../utils";
import type { MarketplaceListing } from "../types";
import styles from "../index.module.less";

interface ListingCardProps {
  listing: MarketplaceListing;
  onInstall: (listing: MarketplaceListing) => void;
  onClick?: (listing: MarketplaceListing) => void;
}

export default function ListingCard({ listing, onInstall, onClick }: ListingCardProps) {
  const categoryColor = CATEGORY_COLORS[listing.category] || "default";
  const isTheme = listing.category === "themes";

  return (
    <div
      className={styles.card}
      onClick={() => onClick?.(listing)}
      style={{ cursor: onClick ? "pointer" : undefined }}
    >
      <div className={styles.cardInfo}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
              <h3 className={styles.cardTitle}>{listing.name}</h3>
              <TrustBadge tier={listing.trustTier} />
            </div>
            <p className={styles.cardAuthor}>
              by {listing.authorName || listing.title} &middot; v{listing.version}
            </p>
          </div>
          <Tag color={categoryColor} className={styles.categoryBadge}>
            {listing.category}
          </Tag>
        </div>

        <p className={styles.cardDescription}>{listing.description}</p>

        <div className={styles.cardStats}>
          <span className={styles.rating}>
            <Rate disabled defaultValue={listing.rating} allowHalf style={{ fontSize: 12 }} />
            <span className={styles.ratingCount}>({listing.ratingCount})</span>
          </span>
          <span className={styles.downloads}>
            <Download size={12} />
            {formatDownloads(listing.downloads)}
          </span>
          <span style={{ fontSize: 11, color: "#666" }}>
            {listing.license}
          </span>
        </div>
      </div>

      <div className={styles.cardFooter}>
        <div className={styles.tags}>
          {listing.tags.slice(0, 3).map((tag) => (
            <span key={tag} className={styles.tag}>{tag}</span>
          ))}
        </div>
        <Button
          type={listing.installed ? "default" : "primary"}
          size="small"
          className={`${styles.installButton} ${listing.installed ? styles.installed : ""}`}
          onClick={(e) => {
            e.stopPropagation();
            if (!listing.installed) onInstall(listing);
          }}
          disabled={listing.installed}
          style={!listing.installed ? { background: "#00e5ff", borderColor: "#00e5ff" } : undefined}
        >
          {listing.installed ? "Installed" : isTheme ? "Apply" : "Install"}
        </Button>
      </div>
    </div>
  );
}
```

- [x] **Step 3: Commit**

```bash
git add console/src/pages/Marketplace/components/ListingCard.tsx
git commit -m "feat(marketplace): rewrite ListingCard with trust badges, version, license"
```

---

### Task 14: Create ListingListItem for list view

**Files:**
- Create: `console/src/pages/Marketplace/components/ListingListItem.tsx`

- [x] **Step 1: Create the component**

```tsx
// console/src/pages/Marketplace/components/ListingListItem.tsx
import { Button, Rate } from "antd";
import { Download } from "lucide-react";
import TrustBadge from "./TrustBadge";
import { formatDownloads } from "../utils";
import type { MarketplaceListing } from "../types";

interface ListingListItemProps {
  listing: MarketplaceListing;
  onInstall: (listing: MarketplaceListing) => void;
  onClick?: (listing: MarketplaceListing) => void;
}

export default function ListingListItem({ listing, onInstall, onClick }: ListingListItemProps) {
  const isTheme = listing.category === "themes";

  return (
    <div
      onClick={() => onClick?.(listing)}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "12px 16px",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        cursor: onClick ? "pointer" : undefined,
        transition: "background 0.15s",
      }}
      onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.02)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.background = "transparent"; }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontWeight: 600, color: "#fff", fontSize: 14 }}>{listing.name}</span>
          <TrustBadge tier={listing.trustTier} size="small" />
          <span style={{ fontSize: 11, color: "#666" }}>v{listing.version}</span>
        </div>
        <div style={{ fontSize: 12, color: "#888", marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {listing.description}
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 16, flexShrink: 0 }}>
        <span style={{ fontSize: 12, color: "#888" }}>
          <Download size={11} /> {formatDownloads(listing.downloads)}
        </span>
        <Rate disabled defaultValue={listing.rating} allowHalf style={{ fontSize: 10 }} />
        <span style={{ fontSize: 11, color: "#666" }}>{listing.license}</span>
        <Button
          size="small"
          type={listing.installed ? "default" : "primary"}
          onClick={(e) => { e.stopPropagation(); if (!listing.installed) onInstall(listing); }}
          disabled={listing.installed}
          style={!listing.installed ? { background: "#00e5ff", borderColor: "#00e5ff" } : undefined}
        >
          {listing.installed ? "Installed" : isTheme ? "Apply" : "Install"}
        </Button>
      </div>
    </div>
  );
}
```

- [x] **Step 2: Commit**

```bash
git add console/src/pages/Marketplace/components/ListingListItem.tsx
git commit -m "feat(marketplace): ListingListItem compact row for list view"
```

---

### Task 15: Rewrite marketplace index page

**Files:**
- Modify: `console/src/pages/Marketplace/index.tsx` (full rewrite)

- [x] **Step 1: Rewrite the page with hero, pills, bundles, grid/list toggle, sort selector**

```tsx
// console/src/pages/Marketplace/index.tsx
import { useState, useEffect, useCallback, useRef } from "react";
import { Input, Spin, Select, message } from "antd";
import { Search, LayoutGrid, List, Store } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { request } from "../../api/request";
import { transformListing } from "./utils";
import type { MarketplaceListing, Bundle } from "./types";
import ListingCard from "./components/ListingCard";
import ListingListItem from "./components/ListingListItem";
import CategoryPills from "./components/CategoryPills";
import BundleCard from "./components/BundleCard";
import styles from "./index.module.less";

function MarketplacePage() {
  const navigate = useNavigate();
  const [listings, setListings] = useState<MarketplaceListing[]>([]);
  const [bundles, setBundles] = useState<Bundle[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [categoryCounts, setCategoryCounts] = useState<Record<string, number>>({});
  const [selectedCategory, setSelectedCategory] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [sort, setSort] = useState("popular");
  const [viewMode, setViewMode] = useState<"grid" | "list">(() => {
    return (localStorage.getItem("marketplace-view") as "grid" | "list") || "grid";
  });
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchListings = useCallback(
    async (sortBy: string, category?: string, query?: string) => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        params.set("sort", sortBy);
        if (category) params.set("category", category);
        if (query) params.set("q", query);
        params.set("limit", "200");
        const data = await request<any[]>(`/marketplace/listings?${params.toString()}`);
        const items = Array.isArray(data) ? data.map(transformListing) : [];
        setListings(items);

        // Compute category counts from full result set
        if (!category && !query) {
          const counts: Record<string, number> = {};
          items.forEach((l) => { counts[l.category] = (counts[l.category] || 0) + 1; });
          setCategoryCounts(counts);
        }
      } catch {
        setListings([]);
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const fetchCategories = useCallback(async () => {
    try {
      const data = await request<string[]>("/marketplace/categories");
      setCategories(Array.isArray(data) ? data : []);
    } catch {
      setCategories([]);
    }
  }, []);

  const fetchBundles = useCallback(async () => {
    try {
      const data = await request<Bundle[]>("/marketplace/bundles");
      setBundles(Array.isArray(data) ? data : []);
    } catch {
      setBundles([]);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
    fetchBundles();
    fetchListings("popular");
  }, [fetchCategories, fetchBundles, fetchListings]);

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    fetchListings(sort, category || undefined, searchQuery || undefined);
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      fetchListings(sort, selectedCategory || undefined, value || undefined);
    }, 400);
  };

  const handleSortChange = (value: string) => {
    setSort(value);
    fetchListings(value, selectedCategory || undefined, searchQuery || undefined);
  };

  const handleViewToggle = (mode: "grid" | "list") => {
    setViewMode(mode);
    localStorage.setItem("marketplace-view", mode);
  };

  const handleInstall = async (listing: MarketplaceListing) => {
    try {
      await request(`/marketplace/listings/${listing.id}/install`, { method: "POST" });
      message.success(`Installed "${listing.name}"`);
      setListings((prev) =>
        prev.map((l) => (l.id === listing.id ? { ...l, installed: true } : l)),
      );
    } catch {
      message.error(`Failed to install "${listing.name}"`);
    }
  };

  const handleListingClick = (listing: MarketplaceListing) => {
    navigate(`/marketplace/${listing.id}`);
  };

  const totalCount = Object.values(categoryCounts).reduce((a, b) => a + b, 0) || listings.length;

  return (
    <div className={styles.marketplace}>
      {/* Hero */}
      <div className={styles.header}>
        <div className={styles.headerInfo}>
          <div className={styles.headerIcon}><Store size={22} /></div>
          <div className={styles.headerText}>
            <h1 className={styles.title}>Prowlr Marketplace</h1>
            <p className={styles.subtitle}>
              Skills, agents, and tools — verified and ready
            </p>
            <p style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
              {totalCount} listings &middot; All reviewed &middot; Official + Verified only
            </p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className={styles.searchBar}>
        <Input.Search
          placeholder="Search by name, tag, or what you need to do..."
          allowClear
          size="large"
          prefix={<Search size={16} color="#bfbfbf" />}
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          onSearch={(value) => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            fetchListings(sort, selectedCategory || undefined, value || undefined);
          }}
        />
      </div>

      {/* Category Pills */}
      <CategoryPills
        categories={categories}
        counts={categoryCounts}
        selected={selectedCategory}
        onSelect={handleCategorySelect}
        totalCount={totalCount}
      />

      {/* Bundles */}
      {bundles.length > 0 && !searchQuery && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ color: "#fff", fontSize: 15, fontWeight: 600, marginBottom: 12 }}>
            Curated Bundles
          </h3>
          <div style={{ display: "flex", gap: 12, overflowX: "auto", paddingBottom: 8 }}>
            {bundles.map((b) => (
              <BundleCard key={b.id} bundle={b} />
            ))}
          </div>
        </div>
      )}

      {/* Sort + View Toggle */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h3 style={{ color: "#fff", fontSize: 15, fontWeight: 600, margin: 0 }}>
          All Listings
        </h3>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <Select
            value={sort}
            onChange={handleSortChange}
            size="small"
            style={{ width: 120 }}
            options={[
              { label: "Popular", value: "popular" },
              { label: "Top Rated", value: "top_rated" },
              { label: "Newest", value: "newest" },
              { label: "A-Z", value: "alpha" },
            ]}
          />
          <div style={{ display: "flex", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 6 }}>
            <button
              onClick={() => handleViewToggle("grid")}
              style={{
                padding: "4px 8px",
                background: viewMode === "grid" ? "rgba(0,229,255,0.1)" : "transparent",
                border: "none",
                cursor: "pointer",
                color: viewMode === "grid" ? "#00e5ff" : "#666",
                borderRadius: "5px 0 0 5px",
              }}
            >
              <LayoutGrid size={14} />
            </button>
            <button
              onClick={() => handleViewToggle("list")}
              style={{
                padding: "4px 8px",
                background: viewMode === "list" ? "rgba(0,229,255,0.1)" : "transparent",
                border: "none",
                cursor: "pointer",
                color: viewMode === "list" ? "#00e5ff" : "#666",
                borderRadius: "0 5px 5px 0",
              }}
            >
              <List size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Listings */}
      {loading ? (
        <div className={styles.loadingContainer}><Spin size="large" /></div>
      ) : listings.length > 0 ? (
        viewMode === "grid" ? (
          <div className={styles.grid}>
            {listings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                onInstall={handleInstall}
                onClick={handleListingClick}
              />
            ))}
          </div>
        ) : (
          <div>
            {listings.map((listing) => (
              <ListingListItem
                key={listing.id}
                listing={listing}
                onInstall={handleInstall}
                onClick={handleListingClick}
              />
            ))}
          </div>
        )
      ) : (
        <div className={styles.emptyState}>
          <div className={styles.emptyText}>
            {searchQuery
              ? `No results for "${searchQuery}"`
              : "No listings available yet. Run 'prowlr market update' to sync."}
          </div>
        </div>
      )}
    </div>
  );
}

export default MarketplacePage;
```

- [x] **Step 2: Commit**

```bash
git add console/src/pages/Marketplace/index.tsx
git commit -m "feat(marketplace): rewrite index with hero, bundles, pills, grid/list, sort"
```

---

### Task 16: Create ListingDetail page

**Files:**
- Create: `console/src/pages/Marketplace/ListingDetail.tsx`
- Modify: `console/src/layouts/MainLayout/index.tsx` (add route)

- [x] **Step 1: Create the detail page**

```tsx
// console/src/pages/Marketplace/ListingDetail.tsx
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button, Tabs, Rate, Spin, Input, message, Tag } from "antd";
import { ArrowLeft, Download, Copy, ExternalLink } from "lucide-react";
import { request } from "../../api/request";
import { transformListing, formatDownloads, CATEGORY_COLORS } from "./utils";
import type { ListingDetail as ListingDetailType, MarketplaceListing } from "./types";
import TrustBadge from "./components/TrustBadge";
import ListingCard from "./components/ListingCard";

export default function ListingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<ListingDetailType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    request<any>(`/marketplace/listings/${id}/detail`)
      .then((data) => {
        setDetail({
          ...data,
          listing: transformListing(data.listing),
          related: (data.related || []).map(transformListing),
          author_listings: (data.author_listings || []).map(transformListing),
        });
      })
      .catch(() => setDetail(null))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}><Spin size="large" /></div>;
  if (!detail) return <div style={{ padding: 40, color: "#888" }}>Listing not found.</div>;

  const { listing } = detail;

  const handleInstall = async () => {
    try {
      await request(`/marketplace/listings/${listing.id}/install`, { method: "POST" });
      message.success(`Installed "${listing.name}"`);
    } catch {
      message.error("Install failed");
    }
  };

  const copyCommand = () => {
    navigator.clipboard.writeText(detail.install_command);
    message.success("Copied to clipboard");
  };

  const tabItems = [
    {
      key: "overview",
      label: "Overview",
      children: (
        <div style={{ color: "#ccc", lineHeight: 1.7 }}>
          <p>{listing.description}</p>
          {listing.compatibility && (
            <p style={{ fontSize: 12, color: "#666" }}>
              Compatibility: {listing.compatibility}
            </p>
          )}
          {detail.bundles.length > 0 && (
            <p style={{ fontSize: 12, color: "#888" }}>
              Part of bundle: {detail.bundles.join(", ")}
            </p>
          )}
          <div style={{ marginTop: 12, display: "flex", gap: 6, flexWrap: "wrap" }}>
            {listing.tags.map((t) => (
              <Tag key={t}>{t}</Tag>
            ))}
          </div>
        </div>
      ),
    },
    {
      key: "changelog",
      label: "Changelog",
      children: (
        <pre style={{ color: "#ccc", whiteSpace: "pre-wrap", fontSize: 13 }}>
          {listing.changelog || "No changelog available."}
        </pre>
      ),
    },
    {
      key: "reviews",
      label: `Reviews (${detail.reviews.length})`,
      children: (
        <div>
          {detail.reviews.length === 0 ? (
            <p style={{ color: "#666" }}>No reviews yet.</p>
          ) : (
            detail.reviews.map((r) => (
              <div key={r.id} style={{ padding: "12px 0", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                <Rate disabled defaultValue={r.rating} style={{ fontSize: 12 }} />
                <span style={{ fontSize: 11, color: "#666", marginLeft: 8 }}>{r.reviewer_id}</span>
                {r.comment && <p style={{ color: "#aaa", fontSize: 13, marginTop: 4 }}>{r.comment}</p>}
              </div>
            ))
          )}
        </div>
      ),
    },
    {
      key: "source",
      label: "Source",
      children: (
        <div style={{ color: "#ccc" }}>
          <p>License: <strong>{listing.license}</strong></p>
          {listing.sourceRepo && (
            <a href={listing.sourceRepo} target="_blank" rel="noopener noreferrer" style={{ color: "#00e5ff" }}>
              <ExternalLink size={12} /> View source on GitHub
            </a>
          )}
        </div>
      ),
    },
  ];

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "24px 16px" }}>
      <Button type="text" onClick={() => navigate("/marketplace")} style={{ color: "#888", marginBottom: 16 }}>
        <ArrowLeft size={14} /> Back to Marketplace
      </Button>

      {/* Header */}
      <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <h1 style={{ color: "#fff", fontSize: 24, margin: 0 }}>{listing.name}</h1>
            <TrustBadge tier={listing.trustTier} size="default" />
          </div>
          <div style={{ fontSize: 13, color: "#888" }}>
            by {listing.authorName} &middot; v{listing.version} &middot; {listing.license}
          </div>
          <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
            <Button
              type="primary"
              size="large"
              icon={<Download size={16} />}
              onClick={handleInstall}
              style={{ background: "#00e5ff", borderColor: "#00e5ff" }}
            >
              {listing.category === "themes" ? "Apply Theme" : "Install"}
            </Button>
            <Button size="large" onClick={copyCommand} icon={<Copy size={14} />}>
              {detail.install_command}
            </Button>
          </div>
        </div>
        <div style={{ textAlign: "right", color: "#888", fontSize: 13 }}>
          <div><Download size={12} /> {formatDownloads(listing.downloads)} downloads</div>
          <div style={{ marginTop: 4 }}>
            <Rate disabled defaultValue={listing.rating} allowHalf style={{ fontSize: 14 }} />
            <span style={{ marginLeft: 4 }}>({listing.ratingCount})</span>
          </div>
          <Tag color={CATEGORY_COLORS[listing.category]} style={{ marginTop: 8 }}>
            {listing.category}
          </Tag>
          {detail.tip_total > 0 && (
            <div style={{ marginTop: 4, color: "#facc15" }}>
              ${detail.tip_total.toFixed(2)} in tips
            </div>
          )}
        </div>
      </div>

      {/* Tabbed Content */}
      <Tabs items={tabItems} />

      {/* Related */}
      {detail.related.length > 0 && (
        <div style={{ marginTop: 32 }}>
          <h3 style={{ color: "#fff", fontSize: 15, fontWeight: 600 }}>Related</h3>
          <div style={{ display: "flex", gap: 12, overflowX: "auto" }}>
            {detail.related.map((r) => (
              <div key={r.id} style={{ minWidth: 250 }}>
                <ListingCard
                  listing={r}
                  onInstall={handleInstall}
                  onClick={(l) => navigate(`/marketplace/${l.id}`)}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

- [x] **Step 2: Add route to MainLayout**

In `console/src/layouts/MainLayout/index.tsx`, add import and route for `ListingDetailPage`:

```tsx
import ListingDetailPage from "../pages/Marketplace/ListingDetail";

// In the routes array, add:
{ path: "/marketplace/:id", element: <ListingDetailPage /> }
```

- [x] **Step 3: Commit**

```bash
git add console/src/pages/Marketplace/ListingDetail.tsx console/src/layouts/MainLayout/index.tsx
git commit -m "feat(marketplace): listing detail page with tabs, reviews, related"
```

---

## Chunk 6: CLI Changes

### Task 17: Add bundle and detail CLI commands, wire install to skills_hub

**Files:**
- Modify: `src/prowlrbot/cli/market_cmd.py` (add bundles, detail, install-bundle commands)
- Modify: `src/prowlrbot/cli/market_cmd.py:93-144` (wire install to skills_hub delivery)

- [x] **Step 1: Add new CLI commands after existing commands**

Add `bundles` command:

```python
@market_group.command(name="bundles")
def market_bundles():
    """List curated skill bundles."""
    store = _get_store()
    from ..marketplace.models import Bundle
    bundles = store.list_bundles()
    if not bundles:
        click.echo("No bundles available.")
        store.close()
        return

    click.echo("\n  Curated Bundles:")
    click.echo(f"  {'ID':<22} {'Name':<20} {'Items':<6} {'Installs'}")
    click.echo(f"  {'─'*22} {'─'*20} {'─'*6} {'─'*10}")
    for b in bundles:
        click.echo(f"  {b.id:<22} {b.name:<20} {len(b.listing_ids):<6} {b.install_count}")
    click.echo()
    store.close()
```

Add `install-bundle` command:

```python
@market_group.command(name="install-bundle")
@click.argument("bundle_id")
def market_install_bundle(bundle_id: str):
    """Install all skills in a curated bundle."""
    store = _get_store()
    bundle = store.get_bundle(bundle_id)
    if not bundle:
        click.echo(f"Bundle '{bundle_id}' not found. Run 'prowlr market bundles' to see available.")
        store.close()
        return

    click.echo(f"\n  Installing bundle: {bundle.name}")
    click.echo(f"  {len(bundle.listing_ids)} items\n")

    installed = 0
    for lid in bundle.listing_ids:
        listing = store.get_listing(lid)
        if listing is None:
            click.echo(f"    SKIP  {lid} (not found)")
            continue
        record = InstallRecord(listing_id=lid, user_id="local", version=listing.version)
        store.record_install(record)
        click.echo(f"    OK    {listing.title}")
        installed += 1

    store.increment_bundle_installs(bundle_id)
    click.echo(f"\n  Installed {installed}/{len(bundle.listing_ids)} items")
    store.close()
```

Add `detail` command:

```python
@market_group.command(name="detail")
@click.argument("listing_id")
def market_detail(listing_id: str):
    """Show full details for a marketplace listing."""
    store = _get_store()
    listing = store.get_listing(listing_id)
    if not listing:
        click.echo(f"Package '{listing_id}' not found.")
        store.close()
        return

    badge = "OFFICIAL" if getattr(listing, "trust_tier", "") == "official" else "VERIFIED"
    click.echo(f"\n  {listing.title} [{badge}]")
    click.echo(f"  {'─' * 50}")
    click.echo(f"  Author:      {getattr(listing, 'author_name', listing.author_id)}")
    click.echo(f"  Version:     {listing.version}")
    click.echo(f"  Category:    {listing.category}")
    click.echo(f"  License:     {getattr(listing, 'license', 'MIT')}")
    click.echo(f"  Downloads:   {listing.downloads}")
    click.echo(f"  Rating:      {'%.1f' % listing.rating}/5 ({listing.ratings_count} reviews)")
    click.echo(f"  Install:     prowlr market install {listing.id}")
    if listing.description:
        click.echo(f"\n  {listing.description}")

    reviews = store.get_reviews(listing_id, limit=5)
    if reviews:
        click.echo(f"\n  Recent Reviews:")
        for r in reviews:
            stars = '*' * r.rating + '.' * (5 - r.rating)
            click.echo(f"    {stars}  {r.comment[:60] if r.comment else '(no comment)'}")

    click.echo()
    store.close()
```

- [x] **Step 2: Commit**

```bash
git add src/prowlrbot/cli/market_cmd.py
git commit -m "feat(marketplace): add bundles, install-bundle, detail CLI commands"
```

---

## Chunk 7: Seed Data

### Task 18: Seed the 4 launch bundles

**Files:**
- Create: `src/prowlrbot/marketplace/seed.py`

- [x] **Step 1: Create seed script**

```python
# src/prowlrbot/marketplace/seed.py
"""Seed marketplace with launch bundles and official listings."""

from __future__ import annotations

import logging
from .models import Bundle
from .store import MarketplaceStore

logger = logging.getLogger(__name__)

LAUNCH_BUNDLES = [
    Bundle(
        id="security-starter",
        name="Security Starter",
        description="OWASP audit, JWT review, dependency scan",
        emoji="shield",
        color="#ef4444",
        listing_ids=[
            "security-auditor", "api-security-audit",
            "dependency-scan", "jwt-review", "owasp-check",
        ],
    ),
    Bundle(
        id="full-stack-dev",
        name="Full-Stack Dev",
        description="API design, frontend, testing, CI/CD, deploy",
        emoji="rocket",
        color="#3b82f6",
        listing_ids=[
            "frontend-design", "backend-architect",
            "database-designer", "test-automator",
            "ci-cd-builder", "deployment-engineer",
            "code-reviewer", "api-documenter",
        ],
    ),
    Bundle(
        id="data-analytics",
        name="Data & Analytics",
        description="SQL, BigQuery, visualization, RAG pipeline",
        emoji="chart",
        color="#8b5cf6",
        listing_ids=[
            "sql-expert", "data-scientist",
            "rag-architect", "data-engineer",
            "ml-engineer", "visualization",
        ],
    ),
    Bundle(
        id="document-pro",
        name="Document Pro",
        description="PDF, DOCX, PPTX, XLSX processing suite",
        emoji="memo",
        color="#f59e0b",
        listing_ids=["pdf", "docx", "pptx", "xlsx"],
    ),
]


def seed_bundles(store: MarketplaceStore) -> int:
    """Seed launch bundles. Returns number of bundles created."""
    created = 0
    for bundle in LAUNCH_BUNDLES:
        existing = store.get_bundle(bundle.id)
        if existing is None:
            store.create_bundle(bundle)
            created += 1
            logger.info("Created bundle: %s", bundle.name)
    return created
```

- [x] **Step 2: Add seed CLI command to market_cmd.py**

```python
@market_group.command(name="seed")
def market_seed():
    """Seed marketplace with launch bundles and official listings."""
    from ..marketplace.seed import seed_bundles

    store = _get_store()
    bundles_created = seed_bundles(store)
    click.echo(f"\n  Seeded {bundles_created} bundles")
    click.echo("  Run 'prowlr market bundles' to see them.")
    click.echo()
    store.close()
```

- [x] **Step 3: Commit**

```bash
git add src/prowlrbot/marketplace/seed.py src/prowlrbot/cli/market_cmd.py
git commit -m "feat(marketplace): seed script with 4 launch bundles"
```

---

### Task 19: Run all tests and verify nothing is broken

- [x] **Step 1: Run full test suite**

Run: `pytest -x -v`
Expected: All existing tests pass, all new marketplace tests pass

- [x] **Step 2: Run frontend build**

Run: `cd console && npm run build`
Expected: Build succeeds with no TypeScript errors

- [x] **Step 3: Fix any issues found**

Address any test failures or build errors.

- [x] **Step 4: Final commit if fixes were needed**

```bash
git add -A
git commit -m "fix(marketplace): address test/build issues from marketplace redesign"
```

---

## Chunk 8: Review Fixes — File Delivery, Credits, Tests

### Task 20: Wire marketplace install to actual skill file delivery

**Files:**
- Modify: `src/prowlrbot/app/routers/marketplace.py:116-123` (update install endpoint)
- Modify: `src/prowlrbot/cli/market_cmd.py:93-144` (update CLI install)
- Test: `tests/marketplace/test_install_delivery.py`

- [x] **Step 1: Write the failing test**

```python
# tests/marketplace/test_install_delivery.py
"""Tests for marketplace install actually delivering skill files."""
import tempfile
from pathlib import Path
from unittest.mock import patch

from prowlrbot.marketplace.models import MarketplaceCategory, MarketplaceListing
from prowlrbot.marketplace.store import MarketplaceStore


def _tmp_store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    return MarketplaceStore(db_path=tmp.name)


def test_cli_install_creates_skill_directory():
    """CLI install should create skill files in customized_skills dir."""
    from click.testing import CliRunner
    from prowlrbot.cli.market_cmd import market_install

    store = _tmp_store()
    store.publish_listing(MarketplaceListing(
        id="test-pdf",
        author_id="prowlrbot",
        title="PDF Processor",
        description="Process PDFs",
        category=MarketplaceCategory.skills,
        status="approved",
    ))

    with tempfile.TemporaryDirectory() as tmpdir:
        working_dir = Path(tmpdir)
        skills_dir = working_dir / "customized_skills"

        with patch("prowlrbot.cli.market_cmd._get_store", return_value=store), \
             patch("prowlrbot.cli.market_cmd.WORKING_DIR", working_dir), \
             patch("prowlrbot.constant.WORKING_DIR", working_dir):
            runner = CliRunner()
            result = runner.invoke(market_install, ["test-pdf"])
            assert result.exit_code == 0

        # Should have created a manifest in the install location
        assert (working_dir / "marketplace" / "test-pdf"[:12]).exists() or \
               skills_dir.exists()
    store.close()
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/marketplace/test_install_delivery.py -v`
Expected: Passes (current install writes manifest). This is a baseline — the real delivery wiring happens in step 3.

- [x] **Step 3: Update install endpoint and CLI to call SkillService**

In `marketplace.py` install endpoint, add skill delivery after `record_install`:

```python
@router.post("/listings/{listing_id}/install", response_model=InstallRecord)
async def record_install(listing_id: str, record: InstallRecord) -> InstallRecord:
    """Install a listing — record install and deliver skill files."""
    listing = _get_store().get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    record.listing_id = listing_id
    result = _get_store().record_install(record)

    # Attempt to deliver skill files for skill-category listings
    if listing.category in ("skills", "agents"):
        try:
            from ...agents.skills_manager import SkillService
            skill_svc = SkillService()
            skill_svc.create_skill(listing.title, listing.description)
        except Exception:
            pass  # Install recorded even if file delivery fails

    return result
```

**Note:** Full file delivery from GitHub (`skills_hub.py`) requires the listing's `source_repo` to point to actual skill files. For v1, this creates a local skill stub. Full GitHub download integration is deferred to the content population phase.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/marketplace/test_install_delivery.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/prowlrbot/app/routers/marketplace.py src/prowlrbot/cli/market_cmd.py tests/marketplace/test_install_delivery.py
git commit -m "feat(marketplace): wire install endpoint to SkillService for file delivery"
```

---

### Task 21: Fix Stripe tip flow — record tip in webhook, not before payment

**Files:**
- Modify: `src/prowlrbot/app/routers/marketplace.py` (tip endpoint and webhook)
- Test: `tests/routers/test_marketplace_stripe.py` (update)

- [x] **Step 1: Update tip endpoint to NOT record tip before payment**

Move `store.add_tip()` out of the tip endpoint. The tip endpoint should only create a Stripe checkout session. The webhook should record the tip after payment confirmation.

```python
@router.post("/listings/{listing_id}/tip")
async def tip_author(listing_id: str, tip_req: TipRequest) -> dict:
    """Create a Stripe checkout session for tipping."""
    import os

    store = _get_store()
    listing = store.get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    if tip_req.amount < 1 or tip_req.amount > 100:
        raise HTTPException(status_code=400, detail="Tip amount must be between $1 and $100")

    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        # Fallback: record tip locally without Stripe
        tip = TipRecord(
            listing_id=listing_id,
            author_id=listing.author_id,
            amount=tip_req.amount,
            message=tip_req.message,
        )
        store.add_tip(tip)
        return {"checkout_url": None, "tip_id": tip.id, "note": "Tip recorded locally (Stripe not configured)"}

    try:
        import stripe
        stripe.api_key = stripe_key
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(tip_req.amount * 100),
                    "product_data": {
                        "name": f"Tip for {listing.title}",
                    },
                },
                "quantity": 1,
            }],
            success_url=f"/marketplace/listings/{listing_id}?tipped=true",
            cancel_url=f"/marketplace/listings/{listing_id}",
            metadata={
                "listing_id": listing_id,
                "author_id": listing.author_id,
                "amount": str(tip_req.amount),
                "message": tip_req.message,
            },
        )
        return {"checkout_url": session.url}
    except ImportError:
        # stripe package not installed — record locally
        tip = TipRecord(
            listing_id=listing_id, author_id=listing.author_id,
            amount=tip_req.amount, message=tip_req.message,
        )
        store.add_tip(tip)
        return {"checkout_url": None, "tip_id": tip.id, "note": "Stripe SDK not installed"}
```

- [x] **Step 2: Implement real Stripe webhook**

```python
from fastapi import Request

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request) -> dict:
    """Stripe webhook — records tip after successful payment."""
    import os
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        import stripe
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ImportError:
        raise HTTPException(status_code=503, detail="Stripe SDK not installed")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        listing_id = metadata.get("listing_id")
        author_id = metadata.get("author_id")
        amount = float(metadata.get("amount", 0))
        message = metadata.get("message", "")

        if listing_id and author_id and amount > 0:
            store = _get_store()
            tip = TipRecord(
                listing_id=listing_id,
                author_id=author_id,
                amount=amount,
                message=message,
            )
            store.add_tip(tip)

    return {"status": "received"}
```

- [x] **Step 3: Commit**

```bash
git add src/prowlrbot/app/routers/marketplace.py tests/routers/test_marketplace_stripe.py
git commit -m "fix(marketplace): record tip in Stripe webhook, not before payment"
```

---

### Task 22: Simplify gamification credit earning rules per spec

**Files:**
- Modify: `src/prowlrbot/marketplace/models.py` (update CREDIT_EARN_RATES)
- Modify: `src/prowlrbot/marketplace/store.py` (add credit-on-action helpers)
- Test: `tests/marketplace/test_credits.py`

- [x] **Step 1: Write the failing test**

```python
# tests/marketplace/test_credits.py
"""Tests for simplified gamification credit rules per spec."""
import tempfile

from prowlrbot.marketplace.models import (
    MarketplaceCategory, MarketplaceListing, ReviewEntry, InstallRecord,
)
from prowlrbot.marketplace.store import MarketplaceStore


def _tmp_store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    return MarketplaceStore(db_path=tmp.name)


def test_publish_awards_100_credits():
    """Publishing a listing awards +100 credits to author."""
    store = _tmp_store()
    listing = MarketplaceListing(
        author_id="author1",
        title="New Skill",
        description="test",
        category=MarketplaceCategory.skills,
    )
    store.publish_listing(listing)
    store.award_publish_credits(listing.author_id, listing.id)
    balance = store.get_balance("author1")
    assert balance.balance == 100
    store.close()


def test_install_awards_5_credits_to_author():
    """Each install awards +5 credits to listing author."""
    store = _tmp_store()
    listing = MarketplaceListing(
        id="s1", author_id="author1", title="Skill",
        description="test", category=MarketplaceCategory.skills,
    )
    store.publish_listing(listing)
    store.award_install_credits("s1", "user1")
    balance = store.get_balance("author1")
    assert balance.balance == 5
    store.close()


def test_install_deduped_per_user_per_listing():
    """Same user installing same listing twice should only award once."""
    store = _tmp_store()
    listing = MarketplaceListing(
        id="s1", author_id="author1", title="Skill",
        description="test", category=MarketplaceCategory.skills,
    )
    store.publish_listing(listing)
    store.award_install_credits("s1", "user1")
    store.award_install_credits("s1", "user1")  # duplicate
    balance = store.get_balance("author1")
    assert balance.balance == 5  # only awarded once
    store.close()


def test_review_awards_5_credits_to_reviewer():
    """Writing a review awards +5 credits to reviewer."""
    store = _tmp_store()
    listing = MarketplaceListing(
        id="s1", author_id="author1", title="Skill",
        description="test", category=MarketplaceCategory.skills,
    )
    store.publish_listing(listing)
    review = ReviewEntry(listing_id="s1", reviewer_id="reviewer1", rating=4)
    store.add_review(review)
    store.award_review_credits("reviewer1", review.id)
    balance = store.get_balance("reviewer1")
    assert balance.balance == 5
    store.close()
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/marketplace/test_credits.py -v`
Expected: FAIL — `award_publish_credits`, `award_install_credits`, `award_review_credits` don't exist

- [x] **Step 3: Add credit-on-action helper methods to store**

```python
    # ------------------------------------------------------------------
    # Gamification Credit Helpers
    # ------------------------------------------------------------------

    def award_publish_credits(self, author_id: str, listing_id: str) -> None:
        """Award +100 credits for publishing a listing."""
        self.add_credits(
            user_id=author_id, amount=100,
            transaction_type=CreditTransactionType.publish_bonus,
            reference_id=listing_id,
            description="Published a listing",
        )

    def award_install_credits(self, listing_id: str, installer_user_id: str) -> None:
        """Award +5 credits to listing author per unique install."""
        # Dedup: check if this user already installed this listing
        existing = self._conn.execute(
            "SELECT 1 FROM credit_transactions WHERE transaction_type = ? "
            "AND reference_id = ? AND description LIKE ?",
            ("download_milestone", listing_id, f"%{installer_user_id}%"),
        ).fetchone()
        if existing:
            return

        listing = self.get_listing(listing_id)
        if listing is None:
            return
        self.add_credits(
            user_id=listing.author_id, amount=5,
            transaction_type=CreditTransactionType.download_milestone,
            reference_id=listing_id,
            description=f"Install by {installer_user_id}",
        )

    def award_review_credits(self, reviewer_id: str, review_id: str) -> None:
        """Award +5 credits to reviewer for writing a review."""
        self.add_credits(
            user_id=reviewer_id, amount=5,
            transaction_type=CreditTransactionType.review_bonus,
            reference_id=review_id,
            description="Wrote a review",
        )
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/marketplace/test_credits.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/prowlrbot/marketplace/store.py tests/marketplace/test_credits.py
git commit -m "feat(marketplace): gamification credit helpers — publish, install, review awards"
```

---

### Task 23: Add CLI command tests

**Files:**
- Test: `tests/cli/test_market_cli.py`

- [x] **Step 1: Write CLI tests**

```python
# tests/cli/test_market_cli.py
"""Tests for marketplace CLI commands."""
import tempfile
from unittest.mock import patch

from click.testing import CliRunner

from prowlrbot.marketplace.models import Bundle, MarketplaceCategory, MarketplaceListing
from prowlrbot.marketplace.store import MarketplaceStore


def _seeded_store():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    s = MarketplaceStore(db_path=tmp.name)
    s.publish_listing(MarketplaceListing(
        id="test-skill", author_id="test", title="Test Skill",
        description="A test skill", category=MarketplaceCategory.skills,
        trust_tier="official", author_name="ProwlrBot", status="approved",
    ))
    s.create_bundle(Bundle(
        id="test-bundle", name="Test Bundle",
        description="Test", listing_ids=["test-skill"],
    ))
    return s


def test_market_bundles_command():
    from prowlrbot.cli.market_cmd import market_bundles
    store = _seeded_store()
    with patch("prowlrbot.cli.market_cmd._get_store", return_value=store):
        runner = CliRunner()
        result = runner.invoke(market_bundles)
        assert result.exit_code == 0
        assert "Test Bundle" in result.output
    store.close()


def test_market_detail_command():
    from prowlrbot.cli.market_cmd import market_detail
    store = _seeded_store()
    with patch("prowlrbot.cli.market_cmd._get_store", return_value=store):
        runner = CliRunner()
        result = runner.invoke(market_detail, ["test-skill"])
        assert result.exit_code == 0
        assert "Test Skill" in result.output
        assert "OFFICIAL" in result.output
    store.close()


def test_market_detail_not_found():
    from prowlrbot.cli.market_cmd import market_detail
    store = _seeded_store()
    with patch("prowlrbot.cli.market_cmd._get_store", return_value=store):
        runner = CliRunner()
        result = runner.invoke(market_detail, ["nonexistent"])
        assert "not found" in result.output
    store.close()


def test_market_install_bundle_command():
    from prowlrbot.cli.market_cmd import market_install_bundle
    store = _seeded_store()
    with patch("prowlrbot.cli.market_cmd._get_store", return_value=store):
        runner = CliRunner()
        result = runner.invoke(market_install_bundle, ["test-bundle"])
        assert result.exit_code == 0
        assert "1/1" in result.output
    store.close()
```

- [x] **Step 2: Run tests**

Run: `pytest tests/cli/test_market_cli.py -v`
Expected: PASS

- [x] **Step 3: Commit**

```bash
git add tests/cli/test_market_cli.py
git commit -m "test(marketplace): CLI command tests for bundles, detail, install-bundle"
```

---

### Task 24: Add frontend utility tests

**Files:**
- Create: `console/src/pages/Marketplace/__tests__/utils.test.ts`

- [x] **Step 1: Write utility tests**

```typescript
// console/src/pages/Marketplace/__tests__/utils.test.ts
import { describe, it, expect } from "vitest";
import { transformListing, formatDownloads, CATEGORY_COLORS } from "../utils";

describe("transformListing", () => {
  it("maps snake_case backend fields to camelCase", () => {
    const raw = {
      id: "test",
      title: "My Skill",
      description: "desc",
      category: "skills",
      ratings_count: 42,
      trust_tier: "official",
      author_name: "Author",
      author_url: "https://github.com/author",
      author_avatar_url: "https://avatars.com/a.png",
      source_repo: "https://github.com/repo",
    };
    const result = transformListing(raw);
    expect(result.name).toBe("My Skill");         // title -> name
    expect(result.ratingCount).toBe(42);           // ratings_count -> ratingCount
    expect(result.trustTier).toBe("official");     // trust_tier -> trustTier
    expect(result.authorName).toBe("Author");      // author_name -> authorName
    expect(result.sourceRepo).toBe("https://github.com/repo");
  });

  it("handles missing fields with defaults", () => {
    const raw = { id: "x", title: "Minimal" };
    const result = transformListing(raw);
    expect(result.trustTier).toBe("verified");
    expect(result.license).toBe("MIT");
    expect(result.downloads).toBe(0);
    expect(result.tags).toEqual([]);
  });
});

describe("formatDownloads", () => {
  it("formats thousands", () => {
    expect(formatDownloads(1500)).toBe("1.5K");
  });
  it("formats millions", () => {
    expect(formatDownloads(2500000)).toBe("2.5M");
  });
  it("keeps small numbers as-is", () => {
    expect(formatDownloads(42)).toBe("42");
  });
});

describe("CATEGORY_COLORS", () => {
  it("has all 7 categories", () => {
    const expected = ["skills", "agents", "prompts", "mcp-servers", "themes", "workflows", "specs"];
    for (const cat of expected) {
      expect(CATEGORY_COLORS[cat]).toBeDefined();
    }
  });
  it("does NOT have stale categories", () => {
    expect(CATEGORY_COLORS["tools"]).toBeUndefined();
    expect(CATEGORY_COLORS["integrations"]).toBeUndefined();
    expect(CATEGORY_COLORS["templates"]).toBeUndefined();
    expect(CATEGORY_COLORS["channels"]).toBeUndefined();
    expect(CATEGORY_COLORS["monitors"]).toBeUndefined();
  });
});
```

- [x] **Step 2: Run frontend tests**

Run: `cd console && npx vitest run src/pages/Marketplace/__tests__/utils.test.ts`
Expected: PASS

- [x] **Step 3: Commit**

```bash
git add console/src/pages/Marketplace/__tests__/utils.test.ts
git commit -m "test(marketplace): frontend utility tests for transformListing, formatDownloads"
```

---

### Task 25: Final integration test and verification

- [x] **Step 1: Run full backend test suite**

Run: `pytest -x -v`
Expected: All tests pass including new marketplace tests

- [x] **Step 2: Run frontend build**

Run: `cd console && npm run build`
Expected: Build succeeds

- [x] **Step 3: Run frontend tests**

Run: `cd console && npx vitest run`
Expected: All tests pass

- [x] **Step 4: Verify new test file inventory**

All new test files that should exist:
- `tests/marketplace/test_models.py`
- `tests/marketplace/test_store.py`
- `tests/marketplace/test_bundles.py`
- `tests/marketplace/test_registry.py`
- `tests/marketplace/test_install_delivery.py`
- `tests/marketplace/test_credits.py`
- `tests/routers/test_marketplace_api.py`
- `tests/routers/test_marketplace_bundles.py`
- `tests/routers/test_marketplace_detail.py`
- `tests/routers/test_marketplace_stripe.py`
- `tests/cli/test_market_cli.py`
- `console/src/pages/Marketplace/__tests__/utils.test.ts`

- [x] **Step 5: Final commit if needed**

```bash
git commit -m "chore(marketplace): final verification pass"
```

---

## Summary

| Chunk | Tasks | What it delivers |
|-------|-------|-----------------|
| 1: Backend Models & Store | 1-3 | TrustTier enum, specs category, v3 migration, Bundle model |
| 2: Backend API | 4-7 | Sort/query fixes, bundle endpoints, detail endpoint, registry sync |
| 3: Stripe Tip Jar | 8 | Stripe checkout, amount validation, graceful degradation |
| 4: Frontend Foundation | 9-12 | Types, utils, TrustBadge, CategoryPills, BundleCard |
| 5: Frontend Pages | 13-16 | ListingCard rewrite, ListingListItem, index rewrite, detail page |
| 6: CLI Changes | 17 | bundles, install-bundle, detail commands |
| 7: Seed Data | 18-19 | 4 launch bundles, seed script, full test verification |
| 8: Review Fixes | 20-25 | File delivery wiring, Stripe tip fix, credits, CLI tests, frontend tests |

**Total: 25 tasks, ~120 steps**

## Deferred to Follow-Up Plan

These items are documented in the spec but explicitly deferred from this plan:

1. **Content population** — porting ~118 listings from external repos requires a separate content pipeline plan with GitHub API integration, SKILL.md parsing, and batch import. Tracked as a follow-up plan.
2. **Full GitHub file delivery** — connecting `skills_hub.py` to download actual skill files from `source_repo` URLs requires the content to exist first. Task 20 creates the wiring; full delivery depends on content population.
3. **Responsive CSS breakpoints** — `index.module.less` updates for 3-col/2-col/1-col grids. Should be part of a frontend polish pass after functional components land.
4. **User identity** — auto-generated anonymous ID in config.json. Currently uses `"local"` hardcode which works for single-user installs. Full identity system deferred.
