# -*- coding: utf-8 -*-
"""Tests for simplified gamification credit rules per spec."""

import tempfile

from prowlrbot.marketplace.models import (
    MarketplaceCategory,
    MarketplaceListing,
    ReviewEntry,
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
        id="s1",
        author_id="author1",
        title="Skill",
        description="test",
        category=MarketplaceCategory.skills,
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
        id="s1",
        author_id="author1",
        title="Skill",
        description="test",
        category=MarketplaceCategory.skills,
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
        id="s1",
        author_id="author1",
        title="Skill",
        description="test",
        category=MarketplaceCategory.skills,
    )
    store.publish_listing(listing)
    review = ReviewEntry(listing_id="s1", reviewer_id="reviewer1", rating=4)
    store.add_review(review)
    store.award_review_credits("reviewer1", review.id)
    balance = store.get_balance("reviewer1")
    assert balance.balance == 5
    store.close()
