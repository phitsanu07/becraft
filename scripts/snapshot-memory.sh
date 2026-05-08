#!/usr/bin/env bash
# snapshot-memory.sh — rebuild memory snapshots (*.md) from events.jsonl (BCFT-009)
#
# Usage:
#   .be/scripts/snapshot-memory.sh           # uses .be/memory/
#   .be/scripts/snapshot-memory.sh /path     # explicit memory dir
#
# Idempotent: running twice produces same output.

set -e

MEMORY_DIR="${1:-.be/memory}"
EVENTS_FILE="$MEMORY_DIR/events.jsonl"

if [ ! -d "$MEMORY_DIR" ]; then
  echo "❌ Memory dir not found: $MEMORY_DIR" >&2
  exit 1
fi

if [ ! -f "$EVENTS_FILE" ]; then
  echo "📭 No events log found at $EVENTS_FILE — nothing to snapshot"
  exit 0
fi

python3 - "$MEMORY_DIR" "$EVENTS_FILE" << 'PYEOF'
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

memory_dir = sys.argv[1]
events_file = sys.argv[2]

# Read events
events = []
with open(events_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"  ⚠️  Skipping invalid JSON line: {e}", file=sys.stderr)

print(f"📥 Read {len(events)} event(s) from {events_file}")

# Group by type
by_type = defaultdict(list)
for ev in events:
    by_type[ev.get('type', 'unknown')].append(ev)

# === Reconstruct decisions.md (ADRs) ===
decisions_path = os.path.join(memory_dir, 'decisions.md')
if by_type.get('decision'):
    decisions_md = "# 🧠 Architecture Decision Records (ADRs)\n\n"
    decisions_md += "> Auto-generated from events.jsonl (BCFT-009)\n\n"
    decisions_md += "| Date | ADR | Decision | Reason | Agent |\n"
    decisions_md += "|------|-----|----------|--------|-------|\n"
    for ev in by_type['decision']:
        d = ev.get('data', {})
        date = ev.get('ts', '?')[:10]
        adr_id = d.get('id', '?')
        dec = d.get('decision', '?')
        reason = d.get('reason', '?')
        agent = ev.get('agent', '?')
        decisions_md += f"| {date} | {adr_id} | {dec} | {reason} | {agent} |\n"
    decisions_md += f"\n---\n*Snapshot generated at {datetime.utcnow().isoformat()}Z*\n"
    with open(decisions_path, 'w', encoding='utf-8') as f:
        f.write(decisions_md)
    print(f"  ✓ Snapshot decisions.md ({len(by_type['decision'])} ADRs)")

# === Reconstruct changelog.md ===
changelog_path = os.path.join(memory_dir, 'changelog.md')
file_events = (by_type.get('file_created', []) +
               by_type.get('file_modified', []) +
               by_type.get('migration_applied', []))
if file_events:
    changelog_md = "# 📝 Session Changelog\n\n"
    changelog_md += "> Auto-generated from events.jsonl (BCFT-009)\n\n"
    changelog_md += "| Time | Agent | Action | File/Resource |\n"
    changelog_md += "|------|-------|--------|---------------|\n"
    for ev in sorted(file_events, key=lambda e: e.get('ts', '')):
        time = ev.get('ts', '?')[:19].replace('T', ' ')
        agent = ev.get('agent', '?')
        ev_type = ev.get('type', '?').replace('_', ' ')
        d = ev.get('data', {})
        resource = d.get('path') or d.get('name') or json.dumps(d, ensure_ascii=False)[:40]
        changelog_md += f"| {time} | {agent} | {ev_type} | {resource} |\n"
    changelog_md += f"\n---\n*Snapshot generated at {datetime.utcnow().isoformat()}Z*\n"
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(changelog_md)
    print(f"  ✓ Snapshot changelog.md ({len(file_events)} entries)")

# === Reconstruct agents-log.md ===
agent_events = (by_type.get('agent_invoked', []) +
                by_type.get('agent_completed', []))
agents_log_path = os.path.join(memory_dir, 'agents-log.md')
if agent_events:
    log_md = "# 🤖 Agents Activity Log\n\n"
    log_md += "> Auto-generated from events.jsonl (BCFT-009)\n\n"
    log_md += "| Time | Agent | Status | Details |\n"
    log_md += "|------|-------|--------|---------|\n"
    for ev in sorted(agent_events, key=lambda e: e.get('ts', '')):
        time = ev.get('ts', '?')[:19].replace('T', ' ')
        agent = ev.get('agent', '?')
        status = '🟢 invoked' if ev.get('type') == 'agent_invoked' else '✅ completed'
        details = json.dumps(ev.get('data', {}), ensure_ascii=False)[:50]
        log_md += f"| {time} | {agent} | {status} | {details} |\n"
    log_md += f"\n---\n*Snapshot generated at {datetime.utcnow().isoformat()}Z*\n"
    with open(agents_log_path, 'w', encoding='utf-8') as f:
        f.write(log_md)
    print(f"  ✓ Snapshot agents-log.md ({len(agent_events)} entries)")

# === Reconstruct api-registry.md ===
ep_events = by_type.get('endpoint_added', [])
api_path = os.path.join(memory_dir, 'api-registry.md')
if ep_events:
    api_md = "# 📋 API Registry\n\n"
    api_md += "> Auto-generated from events.jsonl (BCFT-009)\n\n"
    api_md += "| Method | Path | Auth | Added By | Date |\n"
    api_md += "|--------|------|------|----------|------|\n"
    for ev in sorted(ep_events, key=lambda e: (e.get('data', {}).get('path', ''), e.get('data', {}).get('method', ''))):
        d = ev.get('data', {})
        method = d.get('method', '?')
        path = d.get('path', '?')
        auth = d.get('auth', '?')
        agent = ev.get('agent', '?')
        date = ev.get('ts', '?')[:10]
        api_md += f"| {method} | `{path}` | {auth} | {agent} | {date} |\n"
    api_md += f"\n---\n*Snapshot generated at {datetime.utcnow().isoformat()}Z*\n"
    with open(api_path, 'w', encoding='utf-8') as f:
        f.write(api_md)
    print(f"  ✓ Snapshot api-registry.md ({len(ep_events)} endpoints)")

print(f"\n✅ Memory snapshot complete (idempotent)")
PYEOF
