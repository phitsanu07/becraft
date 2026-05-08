#!/usr/bin/env bash
# append-event.sh — append a single event to events.jsonl (BCFT-009)
#
# Usage:
#   .be/scripts/append-event.sh <type> <agent> '<json-data>'
#
# Examples:
#   .be/scripts/append-event.sh decision bootstrap-agent \
#     '{"id":"ADR-001","decision":"use Supabase JS","reason":"only SUPABASE_URL set"}'
#
#   .be/scripts/append-event.sh file_created api-builder \
#     '{"path":"src/products/products.service.ts","lines":85}'
#
#   .be/scripts/append-event.sh endpoint_added api-builder \
#     '{"method":"GET","path":"/api/v1/products","auth":"public"}'

set -e

TYPE="${1:?Usage: append-event.sh <type> <agent> <json-data>}"
AGENT="${2:?Usage: append-event.sh <type> <agent> <json-data>}"
DATA="${3:-{\}}"

MEMORY_DIR="${MEMORY_DIR:-.be/memory}"
EVENTS_FILE="$MEMORY_DIR/events.jsonl"

mkdir -p "$MEMORY_DIR"

# Use Python via stdin to safely build + validate event
RESULT=$(python3 - "$TYPE" "$AGENT" "$DATA" "$EVENTS_FILE" << 'PYEOF'
import json
import sys
from datetime import datetime, timezone

ev_type, agent, data_str, events_file = sys.argv[1:5]

# Validate data JSON
try:
    data = json.loads(data_str) if data_str else {}
except json.JSONDecodeError as e:
    print(f"INVALID_JSON:{e}", file=sys.stderr)
    sys.exit(1)

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

event = {
    "ts": ts,
    "type": ev_type,
    "agent": agent,
    "data": data,
}

line = json.dumps(event, ensure_ascii=False)

with open(events_file, "a", encoding="utf-8") as f:
    f.write(line + "\n")

print(f"OK:{ev_type}")
PYEOF
)

EXIT=$?
if [ $EXIT -ne 0 ]; then
  echo "❌ Failed to append event: $RESULT" >&2
  exit $EXIT
fi

echo "✓ Event logged: $TYPE by $AGENT"
