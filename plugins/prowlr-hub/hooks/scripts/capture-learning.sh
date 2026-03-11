#!/usr/bin/env bash
# capture-learning.sh — Hook script that captures learnings from agent sessions.
# Triggered on SubagentStop to extract corrections, preferences, and patterns.
#
# Reads the tool result from stdin (JSON) and stores any learnings
# found in the agent's output to the learning engine database.

set -euo pipefail

LEARNINGS_DB="${HOME}/.prowlrbot/learnings.db"

# Ensure database exists
if [ ! -f "$LEARNINGS_DB" ]; then
  exit 0
fi

# Read hook input from stdin
INPUT=$(cat)

# Extract agent output if available
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")

# Only process agent-related tool calls
case "$TOOL_NAME" in
  Agent|Task)
    ;;
  *)
    exit 0
    ;;
esac

# Log session activity for the learning engine to analyze.
# IMPORTANT: Pass values via environment variables, never interpolate into Python code.
export PROWLR_CAPTURE_AGENT="${PROWLR_AGENT_NAME:-unknown}"
export PROWLR_CAPTURE_TIMESTAMP
PROWLR_CAPTURE_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

python3 -c "
import sqlite3, uuid, sys, os

db_path = os.path.expanduser('~/.prowlrbot/learnings.db')
if not os.path.exists(db_path):
    sys.exit(0)

agent_id = os.environ.get('PROWLR_CAPTURE_AGENT', 'unknown')
timestamp = os.environ.get('PROWLR_CAPTURE_TIMESTAMP', '')

conn = sqlite3.connect(db_path)
try:
    conn.execute('''INSERT OR IGNORE INTO sessions (session_id, agent_id, started_at)
                    VALUES (?, ?, ?)''',
                 (str(uuid.uuid4()), agent_id, timestamp))
    conn.commit()
except Exception:
    pass
finally:
    conn.close()
" 2>/dev/null || true

exit 0
