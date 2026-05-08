#!/usr/bin/env bash
# update-memory-index.sh — refresh .be/memory/_index.json from current file state
#
# Usage:
#   ./scripts/update-memory-index.sh [memory_dir]
#
# Examples:
#   ./scripts/update-memory-index.sh                  # uses .be/memory/
#   ./scripts/update-memory-index.sh /path/to/memory  # explicit path
#
# Detection: content-based (looks for real user content beyond template scaffolding).

set -e

MEMORY_DIR="${1:-.be/memory}"

if [ ! -d "$MEMORY_DIR" ]; then
  echo "❌ Memory dir not found: $MEMORY_DIR" >&2
  exit 1
fi

INDEX_FILE="$MEMORY_DIR/_index.json"

if [ ! -f "$INDEX_FILE" ]; then
  echo "❌ _index.json not found at $INDEX_FILE" >&2
  echo "   Run: becraft install (or copy template manually)" >&2
  exit 2
fi

# Use Python for content-based "populated" detection
python3 - "$MEMORY_DIR" "$INDEX_FILE" << 'PYEOF'
import json
import os
import re
import sys
from datetime import datetime, timezone

memory_dir = sys.argv[1]
index_file = sys.argv[2]

# Template markers — lines containing only these = still template
EMPTY_MARKERS = [
    r'\(none\)',
    r'\(none yet\)',
    r'\(no signals yet\)',
    r'\(will update.*\)',
    r'\(will be auto-generated.*\)',
    r'\(will be documented.*\)',
    r'\(will record here\)',
    r'\(previous sessions will be recorded here\)',
    r'\(rebuild from current state\)',
    r'\[waiting for user command\]',
    r'\[no active task.*\]',
    r'\[project name\]',
    r'\[type\]',
    r'\[brief description\]',
    r'\[one-sentence description\]',
    r'\[not specified\]',
    r'\[fill in.*\]',
    r'\[prisma \| typeorm \| drizzle \| mikroorm\]',
    r'_template missing.*_',
]
EMPTY_PATTERN = re.compile('|'.join(EMPTY_MARKERS), re.IGNORECASE)


def is_populated(content: str) -> bool:
    """Detect if memory file has real user content beyond template scaffolding."""
    lines = []
    for raw in content.split('\n'):
        s = raw.strip()
        if not s:
            continue
        # Skip headings, dividers, blockquotes
        if s.startswith('#') or s.startswith('---') or s.startswith('>'):
            continue
        # Skip template-marker lines
        if EMPTY_PATTERN.search(s):
            continue
        # Skip italic timestamp meta lines
        if re.fullmatch(r'\*[a-z _]*:[^*]+\*', s, re.IGNORECASE):
            continue
        # Skip table separator / empty rows
        if re.fullmatch(r'\|?[\s\-|]+\|?', s):
            continue
        # Skip "| - | - | - |"-style empty rows
        if re.fullmatch(r'\|(\s*-\s*\|)+', s):
            continue
        # Skip pure table headers (text with all caps OR pipe-separated short cells)
        if s.startswith('|') and len(s.split('|')) >= 3:
            cells = [c.strip() for c in s.strip('|').split('|') if c.strip()]
            if all(len(c) < 30 and c[0].isupper() for c in cells if c):
                continue
        lines.append(s)

    meaningful = '\n'.join(lines)
    return len(meaningful) > 80


with open(index_file, 'r', encoding='utf-8') as f:
    index = json.load(f)

changed = 0
for name in list(index.get('files', {}).keys()):
    md_path = os.path.join(memory_dir, f"{name}.md")
    if not os.path.exists(md_path):
        continue

    size = os.path.getsize(md_path)
    mtime = datetime.fromtimestamp(
        os.path.getmtime(md_path), tz=timezone.utc
    ).isoformat()

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    populated = is_populated(content)

    entry = index['files'][name]
    old_pop = entry.get('populated', False)

    entry['size_bytes'] = size
    entry['last_modified'] = mtime
    entry['populated'] = populated

    if old_pop != populated:
        changed += 1

with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

populated_count = sum(1 for f in index['files'].values() if f.get('populated'))
total = len(index['files'])
print(f"✅ Memory index updated: {populated_count}/{total} files populated, {changed} state changes")
PYEOF
