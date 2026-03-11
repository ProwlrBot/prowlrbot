# -*- coding: utf-8 -*-
"""FastAPI router for the ProwlrBot Marketplace."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from ...marketplace.models import (
    InstallRecord,
    MarketplaceCategory,
    MarketplaceListing,
    ReviewEntry,
)
from ...marketplace.store import MarketplaceStore

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

# Lazily initialized singleton store.
_store: MarketplaceStore | None = None


def _get_store() -> MarketplaceStore:
    """Get or create the global MarketplaceStore instance."""
    global _store
    if _store is None:
        _store = MarketplaceStore()
    return _store


# ------------------------------------------------------------------
# Listings
# ------------------------------------------------------------------


@router.post("/listings", response_model=MarketplaceListing)
async def publish_listing(listing: MarketplaceListing) -> MarketplaceListing:
    """Publish a new listing to the marketplace."""
    return _get_store().publish_listing(listing)


@router.get("/listings", response_model=list[MarketplaceListing])
async def search_listings(
    query: str = "",
    category: Optional[str] = None,
    limit: int = 50,
) -> list[MarketplaceListing]:
    """Search marketplace listings by query and/or category."""
    limit = max(1, min(limit, 200))
    return _get_store().search_listings(query=query, category=category, limit=limit)


@router.get("/listings/{listing_id}", response_model=MarketplaceListing)
async def get_listing(listing_id: str) -> MarketplaceListing:
    """Get a single listing by ID."""
    listing = _get_store().get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.put("/listings/{listing_id}", response_model=MarketplaceListing)
async def update_listing(listing_id: str, updates: dict) -> MarketplaceListing:
    """Partially update a listing."""
    listing = _get_store().update_listing(listing_id, updates)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.get("/listings/author/{author_id}", response_model=list[MarketplaceListing])
async def list_by_author(author_id: str) -> list[MarketplaceListing]:
    """Get all listings by a specific author."""
    return _get_store().list_by_author(author_id)


# ------------------------------------------------------------------
# Reviews
# ------------------------------------------------------------------


@router.post("/listings/{listing_id}/reviews", response_model=ReviewEntry)
async def add_review(listing_id: str, review: ReviewEntry) -> ReviewEntry:
    """Add a review to a listing."""
    listing = _get_store().get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    review.listing_id = listing_id
    return _get_store().add_review(review)


@router.get("/listings/{listing_id}/reviews", response_model=list[ReviewEntry])
async def get_reviews(listing_id: str, limit: int = 50) -> list[ReviewEntry]:
    """Get reviews for a listing."""
    return _get_store().get_reviews(listing_id, limit=min(limit, 200))


# ------------------------------------------------------------------
# Installs
# ------------------------------------------------------------------


@router.post("/listings/{listing_id}/install", response_model=InstallRecord)
async def record_install(listing_id: str, record: InstallRecord) -> InstallRecord:
    """Record an installation of a listing."""
    listing = _get_store().get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    record.listing_id = listing_id
    return _get_store().record_install(record)


# ------------------------------------------------------------------
# Discovery
# ------------------------------------------------------------------


@router.get("/popular", response_model=list[MarketplaceListing])
async def get_popular(limit: int = 20) -> list[MarketplaceListing]:
    """Get the most popular listings by download count."""
    return _get_store().get_popular(limit=min(limit, 100))


@router.get("/top-rated", response_model=list[MarketplaceListing])
async def get_top_rated(limit: int = 20) -> list[MarketplaceListing]:
    """Get the highest-rated listings."""
    return _get_store().get_top_rated(limit=min(limit, 100))


@router.get("/categories", response_model=list[str])
async def list_categories() -> list[str]:
    """Return all available marketplace categories."""
    return [c.value for c in MarketplaceCategory]
