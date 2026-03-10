#!/usr/bin/env bash
# Pre-edit hook: Check if a file is locked by another agent before editing.
#
# This hook runs BEFORE every Edit, Write, or MultiEdit tool call.
# If the file is locked by another agent, it warns Claude to back off.
#
# Input: $1 = JSON string with tool input (contains file_path)

set -euo pipefail

# Extract file_path from the tool input JSON
TOOL_INPUT="${1:-}"
if [ -z "$TOOL_INPUT" ]; then
    exit 0
fi

# Try to extract file_path using python (available everywhere prowlrbot runs)
FILE_PATH=$(python3 -c "
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get('file_path', ''))
except:
    print('')
" "$TOOL_INPUT" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Find the prowlrbot project root (look for src/prowlrbot/hub/)
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
    # Not in a prowlrbot project — skip check
    exit 0
fi

# Check conflicts via the MCP server
RESULT=$(echo "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"check_conflicts\",\"arguments\":{\"paths\":[\"$FILE_PATH\"]}}}" | \
    PYTHONPATH="$PROWLR_ROOT/src" python3 -m prowlrbot.hub 2>/dev/null || echo "")

# Check if there are conflicts (locked by another agent)
if echo "$RESULT" | python3 -c "
import json, sys
try:
    data = json.loads(sys.stdin.read())
    text = data.get('result', {}).get('content', [{}])[0].get('text', '')
    if 'LOCKED' in text.upper() and 'by you' not in text.lower():
        print('CONFLICT')
        sys.exit(0)
except:
    pass
" 2>/dev/null | grep -q "CONFLICT"; then
    echo "WARNING: File '$FILE_PATH' is locked by another agent in the war room. Check conflicts before editing."
fi

exit 0
