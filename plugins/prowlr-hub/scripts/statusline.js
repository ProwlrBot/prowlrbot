#!/usr/bin/env node
// ProwlrHub statusline — war room status for Claude Code terminal.
// Returns JSON: {"agents":5,"working":2,"tasks":7,"locks":3,"status":"connected"}
// Uses node:sqlite DatabaseSync for sub-10ms in-process reads.
"use strict";

const { existsSync } = require("fs");
const { join } = require("path");

const dbPath =
  process.env.PROWLR_HUB_DB ||
  join(process.env.HOME || "", ".prowlrbot", "warroom.db");

if (!existsSync(dbPath)) {
  process.stdout.write(JSON.stringify({ status: "disconnected" }));
  process.exit(0);
}

try {
  // node:sqlite is available in Node 22.5+ (stable in 23+)
  // Falls back to sqlite3 CLI for older Node versions
  let row;

  try {
    const { DatabaseSync } = require("node:sqlite");
    const db = new DatabaseSync(dbPath, { readOnly: true });
    const stmt = db.prepare(
      [
        "SELECT",
        "  (SELECT COUNT(*) FROM agents WHERE status != 'disconnected') as agents,",
        "  (SELECT COUNT(*) FROM agents WHERE status = 'working') as working,",
        "  (SELECT COUNT(*) FROM tasks) as tasks,",
        "  (SELECT COUNT(*) FROM file_locks) as locks",
      ].join("\n")
    );
    row = stmt.get();
    db.close();
  } catch (e) {
    // Fallback: shell out to sqlite3 CLI for Node < 22.5
    const { execFileSync } = require("child_process");
    const query = [
      "SELECT",
      "  (SELECT COUNT(*) FROM agents WHERE status != 'disconnected') as agents,",
      "  (SELECT COUNT(*) FROM agents WHERE status = 'working') as working,",
      "  (SELECT COUNT(*) FROM tasks) as tasks,",
      "  (SELECT COUNT(*) FROM file_locks) as locks;",
    ].join("\n");

    const result = execFileSync("sqlite3", ["-json", dbPath, query], {
      timeout: 3000,
      encoding: "utf-8",
    }).trim();

    const rows = JSON.parse(result);
    row = rows[0] || {};
  }

  process.stdout.write(
    JSON.stringify({
      agents: row.agents || 0,
      working: row.working || 0,
      tasks: row.tasks || 0,
      locks: row.locks || 0,
      status: "connected",
    })
  );
} catch {
  process.stdout.write(JSON.stringify({ status: "error" }));
}
