#!/usr/bin/env bash
# capture-learning.sh — Hook script that captures learnings from agent sessions.
#
# Triggered on:
#   - PostToolUse (Edit|Write|MultiEdit|Bash): captures tool failures as learnings
#   - SubagentStop: logs session activity
#
# Reads the hook context from stdin (JSON) and stores any learnings
# in the learning engine database via the Python add_learning function.

set -euo pipefail

LEARNINGS_DB="${HOME}/.prowlrbot/learnings.db"

# Read hook input from stdin (may be empty for some hook types)
INPUT=$(cat 2>/dev/null || echo "{}")

# Detect hook type from input structure.
# PostToolUse provides tool_name and tool_result; SubagentStop provides agent info.
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
TOOL_EXIT=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('exit_code', d.get('tool_exit_code', '0')))" 2>/dev/null || echo "0")

# Determine current project from git or working directory
PROJECT=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")

# --- PostToolUse path: capture failures from Edit/Write/MultiEdit/Bash ---
if [ -n "$TOOL_NAME" ] && [ "$TOOL_EXIT" != "0" ]; then
    # Tool failed — record a "failure" learning.
    # Extract error output safely via environment variables.
    export PROWLR_LEARN_PROJECT="$PROJECT"
    export PROWLR_LEARN_TOOL="$TOOL_NAME"
    export PROWLR_LEARN_AGENT="${PROWLR_AGENT_NAME:-unknown}"

    # Extract truncated error from tool result (first 500 chars)
    TOOL_ERROR=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
err = d.get('tool_result', d.get('stderr', d.get('output', '')))
if isinstance(err, dict):
    err = json.dumps(err)
print(str(err)[:500])
" 2>/dev/null || echo "Unknown error")
    export PROWLR_LEARN_ERROR="$TOOL_ERROR"

    python3 -c "
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath('$0')), '..', '..', '..', '..', 'src'))
try:
    from prowlrbot.learning.db import init_db, add_learning
except ImportError:
    sys.exit(0)

project = os.environ.get('PROWLR_LEARN_PROJECT', '')
tool = os.environ.get('PROWLR_LEARN_TOOL', 'unknown')
agent = os.environ.get('PROWLR_LEARN_AGENT', 'unknown')
error = os.environ.get('PROWLR_LEARN_ERROR', '')

db_path = os.path.expanduser('~/.prowlrbot/learnings.db')
try:
    conn = init_db(db_path)
    add_learning(
        conn,
        project=project,
        category='failure',
        content=f'Tool {tool} failed: {error}',
        title=f'{tool} failure',
        source=agent,
        confidence=0.7,
    )
    conn.close()
except Exception:
    pass
" 2>/dev/null || true
    exit 0
fi

# --- SubagentStop path: log session activity ---
case "$TOOL_NAME" in
    Agent|Task|"")
        ;;
    *)
        exit 0
        ;;
esac

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
