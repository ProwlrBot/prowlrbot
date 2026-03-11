# -*- coding: utf-8 -*-
"""Built-in migration definitions for ProwlrBot."""

from __future__ import annotations

from .manager import MigrationManager

# ------------------------------------------------------------------
# Migration definitions
# ------------------------------------------------------------------

MIGRATIONS: list[dict[str, object]] = [
    # ---- v1: Core tables ----
    {
        "version": 1,
        "name": "core_tables",
        "up_sql": """
            CREATE TABLE IF NOT EXISTS agents_config (
                agent_id   TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                soul       TEXT NOT NULL DEFAULT '',
                profile    TEXT NOT NULL DEFAULT '',
                model      TEXT NOT NULL DEFAULT '',
                tools      TEXT NOT NULL DEFAULT '[]',
                skills     TEXT NOT NULL DEFAULT '[]',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                agent_id   TEXT NOT NULL,
                channel    TEXT NOT NULL DEFAULT '',
                status     TEXT NOT NULL DEFAULT 'active',
                metadata   TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role       TEXT NOT NULL,
                content    TEXT NOT NULL,
                metadata   TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );

            CREATE INDEX IF NOT EXISTS idx_chat_history_session
                ON chat_history(session_id);
            CREATE INDEX IF NOT EXISTS idx_sessions_agent
                ON sessions(agent_id);
        """,
        "down_sql": """
            DROP TABLE IF EXISTS chat_history;
            DROP TABLE IF EXISTS sessions;
            DROP TABLE IF EXISTS agents_config;
        """,
    },
    # ---- v2: Provider detection ----
    {
        "version": 2,
        "name": "provider_detection",
        "up_sql": """
            CREATE TABLE IF NOT EXISTS providers (
                provider_id TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                kind        TEXT NOT NULL DEFAULT 'openai',
                base_url    TEXT NOT NULL DEFAULT '',
                api_key_ref TEXT NOT NULL DEFAULT '',
                cost_tier   INTEGER NOT NULL DEFAULT 2,
                is_healthy  INTEGER NOT NULL DEFAULT 0,
                last_check  REAL,
                created_at  REAL NOT NULL,
                updated_at  REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS provider_health_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id TEXT NOT NULL,
                is_healthy  INTEGER NOT NULL,
                latency_ms  REAL,
                error       TEXT,
                checked_at  REAL NOT NULL,
                FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
            );

            CREATE INDEX IF NOT EXISTS idx_health_log_provider
                ON provider_health_log(provider_id);
        """,
        "down_sql": """
            DROP TABLE IF EXISTS provider_health_log;
            DROP TABLE IF EXISTS providers;
        """,
    },
    # ---- v3: Gamification ----
    {
        "version": 3,
        "name": "gamification",
        "up_sql": """
            CREATE TABLE IF NOT EXISTS xp_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id   TEXT NOT NULL,
                xp_amount  INTEGER NOT NULL,
                reason     TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS achievements (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id   TEXT NOT NULL,
                badge      TEXT NOT NULL,
                name       TEXT NOT NULL,
                earned_at  REAL NOT NULL,
                UNIQUE(agent_id, badge)
            );

            CREATE INDEX IF NOT EXISTS idx_xp_log_agent
                ON xp_log(agent_id);
            CREATE INDEX IF NOT EXISTS idx_achievements_agent
                ON achievements(agent_id);
        """,
        "down_sql": """
            DROP TABLE IF EXISTS achievements;
            DROP TABLE IF EXISTS xp_log;
        """,
    },
    # ---- v4: AgentVerse ----
    {
        "version": 4,
        "name": "agentverse",
        "up_sql": """
            CREATE TABLE IF NOT EXISTS verse_agents (
                agent_id   TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                avatar_url TEXT NOT NULL DEFAULT '',
                level      INTEGER NOT NULL DEFAULT 1,
                xp_total   INTEGER NOT NULL DEFAULT 0,
                location   TEXT NOT NULL DEFAULT 'spawn',
                status     TEXT NOT NULL DEFAULT 'idle',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS guilds (
                guild_id   TEXT PRIMARY KEY,
                name       TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                owner_id   TEXT NOT NULL,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS guild_members (
                guild_id   TEXT NOT NULL,
                agent_id   TEXT NOT NULL,
                role       TEXT NOT NULL DEFAULT 'member',
                joined_at  REAL NOT NULL,
                PRIMARY KEY (guild_id, agent_id),
                FOREIGN KEY (guild_id) REFERENCES guilds(guild_id),
                FOREIGN KEY (agent_id) REFERENCES verse_agents(agent_id)
            );

            CREATE TABLE IF NOT EXISTS trades (
                trade_id   TEXT PRIMARY KEY,
                seller_id  TEXT NOT NULL,
                buyer_id   TEXT NOT NULL,
                item_type  TEXT NOT NULL,
                item_id    TEXT NOT NULL,
                price      INTEGER NOT NULL DEFAULT 0,
                status     TEXT NOT NULL DEFAULT 'pending',
                created_at REAL NOT NULL,
                completed_at REAL
            );

            CREATE TABLE IF NOT EXISTS battles (
                battle_id   TEXT PRIMARY KEY,
                challenger  TEXT NOT NULL,
                defender    TEXT NOT NULL,
                winner      TEXT,
                battle_type TEXT NOT NULL DEFAULT 'duel',
                log         TEXT NOT NULL DEFAULT '[]',
                created_at  REAL NOT NULL,
                ended_at    REAL
            );

            CREATE INDEX IF NOT EXISTS idx_trades_seller
                ON trades(seller_id);
            CREATE INDEX IF NOT EXISTS idx_trades_buyer
                ON trades(buyer_id);
            CREATE INDEX IF NOT EXISTS idx_battles_challenger
                ON battles(challenger);
        """,
        "down_sql": """
            DROP TABLE IF EXISTS battles;
            DROP TABLE IF EXISTS trades;
            DROP TABLE IF EXISTS guild_members;
            DROP TABLE IF EXISTS guilds;
            DROP TABLE IF EXISTS verse_agents;
        """,
    },
    # ---- v5: Marketplace ----
    {
        "version": 5,
        "name": "marketplace",
        "up_sql": """
            CREATE TABLE IF NOT EXISTS marketplace_listings (
                listing_id  TEXT PRIMARY KEY,
                author_id   TEXT NOT NULL,
                category    TEXT NOT NULL,
                name        TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                version     TEXT NOT NULL DEFAULT '1.0.0',
                price       INTEGER NOT NULL DEFAULT 0,
                status      TEXT NOT NULL DEFAULT 'draft',
                downloads   INTEGER NOT NULL DEFAULT 0,
                rating_avg  REAL NOT NULL DEFAULT 0.0,
                rating_count INTEGER NOT NULL DEFAULT 0,
                created_at  REAL NOT NULL,
                updated_at  REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS marketplace_reviews (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id  TEXT NOT NULL,
                reviewer_id TEXT NOT NULL,
                rating      INTEGER NOT NULL,
                comment     TEXT NOT NULL DEFAULT '',
                created_at  REAL NOT NULL,
                FOREIGN KEY (listing_id) REFERENCES marketplace_listings(listing_id),
                UNIQUE(listing_id, reviewer_id)
            );

            CREATE TABLE IF NOT EXISTS marketplace_installs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id  TEXT NOT NULL,
                agent_id    TEXT NOT NULL,
                version     TEXT NOT NULL,
                installed_at REAL NOT NULL,
                FOREIGN KEY (listing_id) REFERENCES marketplace_listings(listing_id)
            );

            CREATE INDEX IF NOT EXISTS idx_listings_category
                ON marketplace_listings(category);
            CREATE INDEX IF NOT EXISTS idx_listings_author
                ON marketplace_listings(author_id);
            CREATE INDEX IF NOT EXISTS idx_reviews_listing
                ON marketplace_reviews(listing_id);
            CREATE INDEX IF NOT EXISTS idx_installs_agent
                ON marketplace_installs(agent_id);
        """,
        "down_sql": """
            DROP TABLE IF EXISTS marketplace_installs;
            DROP TABLE IF EXISTS marketplace_reviews;
            DROP TABLE IF EXISTS marketplace_listings;
        """,
    },
    # ---- v6: RAG ----
    {
        "version": 6,
        "name": "rag_tables",
        "up_sql": """
            CREATE TABLE IF NOT EXISTS rag_documents (
                doc_id      TEXT PRIMARY KEY,
                agent_id    TEXT NOT NULL,
                source      TEXT NOT NULL,
                title       TEXT NOT NULL DEFAULT '',
                content     TEXT NOT NULL DEFAULT '',
                mime_type   TEXT NOT NULL DEFAULT 'text/plain',
                token_count INTEGER NOT NULL DEFAULT 0,
                metadata    TEXT NOT NULL DEFAULT '{}',
                created_at  REAL NOT NULL,
                updated_at  REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rag_chunks (
                chunk_id    TEXT PRIMARY KEY,
                doc_id      TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content     TEXT NOT NULL,
                embedding   BLOB,
                token_count INTEGER NOT NULL DEFAULT 0,
                metadata    TEXT NOT NULL DEFAULT '{}',
                created_at  REAL NOT NULL,
                FOREIGN KEY (doc_id) REFERENCES rag_documents(doc_id)
            );

            CREATE INDEX IF NOT EXISTS idx_rag_docs_agent
                ON rag_documents(agent_id);
            CREATE INDEX IF NOT EXISTS idx_rag_chunks_doc
                ON rag_chunks(doc_id);
        """,
        "down_sql": """
            DROP TABLE IF EXISTS rag_chunks;
            DROP TABLE IF EXISTS rag_documents;
        """,
    },
    # ---- v7: Audit log ----
    {
        "version": 7,
        "name": "audit_log",
        "up_sql": """
            CREATE TABLE IF NOT EXISTS audit_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp   REAL NOT NULL,
                actor       TEXT NOT NULL DEFAULT 'system',
                action      TEXT NOT NULL,
                resource    TEXT NOT NULL DEFAULT '',
                resource_id TEXT NOT NULL DEFAULT '',
                detail      TEXT NOT NULL DEFAULT '{}',
                ip_address  TEXT NOT NULL DEFAULT '',
                success     INTEGER NOT NULL DEFAULT 1
            );

            CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
                ON audit_log(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_log_actor
                ON audit_log(actor);
            CREATE INDEX IF NOT EXISTS idx_audit_log_action
                ON audit_log(action);
        """,
        "down_sql": """
            DROP TABLE IF EXISTS audit_log;
        """,
    },
    # ---- v8: Analytics ----
    {
        "version": 8,
        "name": "analytics",
        "up_sql": """
            CREATE TABLE IF NOT EXISTS analytics_events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type  TEXT NOT NULL,
                agent_id    TEXT NOT NULL DEFAULT '',
                session_id  TEXT NOT NULL DEFAULT '',
                channel     TEXT NOT NULL DEFAULT '',
                payload     TEXT NOT NULL DEFAULT '{}',
                created_at  REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS analytics_daily (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                date_key     TEXT NOT NULL,
                agent_id     TEXT NOT NULL DEFAULT '',
                channel      TEXT NOT NULL DEFAULT '',
                messages_in  INTEGER NOT NULL DEFAULT 0,
                messages_out INTEGER NOT NULL DEFAULT 0,
                tokens_in    INTEGER NOT NULL DEFAULT 0,
                tokens_out   INTEGER NOT NULL DEFAULT 0,
                avg_latency  REAL NOT NULL DEFAULT 0.0,
                errors       INTEGER NOT NULL DEFAULT 0,
                UNIQUE(date_key, agent_id, channel)
            );

            CREATE INDEX IF NOT EXISTS idx_analytics_events_type
                ON analytics_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_analytics_events_created
                ON analytics_events(created_at);
            CREATE INDEX IF NOT EXISTS idx_analytics_daily_date
                ON analytics_daily(date_key);
        """,
        "down_sql": """
            DROP TABLE IF EXISTS analytics_daily;
            DROP TABLE IF EXISTS analytics_events;
        """,
    },
]


def register_all(manager: MigrationManager) -> None:
    """Register all built-in migrations with the given manager."""
    for m in MIGRATIONS:
        manager.register(
            version=m["version"],  # type: ignore[arg-type]
            name=m["name"],  # type: ignore[arg-type]
            up_sql=m["up_sql"],  # type: ignore[arg-type]
            down_sql=m["down_sql"],  # type: ignore[arg-type]
        )
