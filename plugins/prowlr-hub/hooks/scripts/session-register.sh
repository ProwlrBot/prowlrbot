#!/usr/bin/env bash
# Session start hook: Register agent and show mission board summary.
#
# This hook runs when a new Claude Code session starts.
# It checks the war room for active tasks and agents.

set -euo pipefail

# Find the prowlrbot project root
PROWLR_ROOT=""
SEARCH_DIR="$(pwd)"
for _ in 1 2 3 4 5; do
    if [ -d "$SEARCH_DIR/src/prowlrbot/hub" ]; then
        PROWLR_ROOT="$SEARCH_DIR"
        break
    fi
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

if [ -z "$PROWLR_ROOT" ]; then
    exit 0
fi

# Quick health check — is the war room accessible?
RESULT=$(echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"check_mission_board","arguments":{}}}' | \
    PYTHONPATH="$PROWLR_ROOT/src" python3 -m prowlrbot.hub 2>/dev/null || echo "")

if echo "$RESULT" | grep -q "Mission Board"; then
    # Count tasks by parsing the output
    TASK_COUNT=$(echo "$RESULT" | python3 -c "
import json, sys
try:
    data = json.loads(sys.stdin.read())
    text = data.get('result', {}).get('content', [{}])[0].get('text', '')
    lines = [l for l in text.split('\n') if l.strip().startswith(('⬜', '🟢', '🔴', '🟡'))]
    print(len(lines))
except:
    print('0')
" 2>/dev/null || echo "0")

    if [ "$TASK_COUNT" -gt 0 ]; then
        echo "War Room connected: $TASK_COUNT tasks on the mission board. Use /board to see them."
    else
        echo "War Room connected: Mission board is empty. Use /claim to create a task."
    fi
fi

exit 0
