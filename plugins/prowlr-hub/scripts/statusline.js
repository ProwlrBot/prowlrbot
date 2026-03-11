#!/usr/bin/env node
// ProwlrHub statusline — war room status for Claude Code terminal.
// Returns JSON: {"agents":5,"working":2,"tasks":7,"locks":3,"status":"connected"}
// Designed for sub-10ms response via direct sqlite3 CLI query.
const { execFileSync } = require("child_process");
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
  const row = rows[0] || {};
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
