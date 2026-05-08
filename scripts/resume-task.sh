#!/usr/bin/env bash
# resume-task.sh — list/resume/cleanup unfinished tasks (BCFT-011)
#
# Usage:
#   resume-task.sh list                          # show all checkpoints
#   resume-task.sh show <task-id>                # display checkpoint details
#   resume-task.sh clean <task-id>               # delete a checkpoint
#   resume-task.sh clean --completed             # delete all completed checkpoints

set -e

CHECKPOINTS_DIR="${CHECKPOINTS_DIR:-.be/checkpoints}"
SUBCMD="${1:-list}"

mkdir -p "$CHECKPOINTS_DIR"

case "$SUBCMD" in
  list)
    python3 - "$CHECKPOINTS_DIR" << 'PYEOF'
import json, os, sys
from datetime import datetime

cp_dir = sys.argv[1]
files = sorted([f for f in os.listdir(cp_dir) if f.endswith('.json')])

if not files:
    print("📭 No checkpoints found.")
    sys.exit(0)

print(f"📋 {len(files)} checkpoint(s):\n")
print(f"{'TASK ID':<14} {'STATUS':<12} {'AGENT':<22} {'PHASES':<10} TASK")
print('-' * 100)

for fn in files:
    try:
        with open(os.path.join(cp_dir, fn), 'r', encoding='utf-8') as f:
            cp = json.load(f)
        tid = cp.get('task_id', fn.replace('.json',''))[:12]
        status = cp.get('status', 'in_progress')
        agent = cp.get('agent', '?')[:20]
        done = len(cp.get('phases_done', []))
        pending = len(cp.get('phases_pending', []))
        progress = f"{done}/{done+pending}"
        summary = cp.get('task_summary', '?')[:50]
        print(f"{tid:<14} {status:<12} {agent:<22} {progress:<10} {summary}")
    except Exception as e:
        print(f"  ⚠️  Failed to read {fn}: {e}")
PYEOF
    ;;

  show)
    TASK_ID="${2:?Usage: resume-task.sh show <task-id>}"
    FILE="$CHECKPOINTS_DIR/$TASK_ID.json"
    if [ ! -f "$FILE" ]; then
      echo "❌ Checkpoint not found: $FILE" >&2
      exit 1
    fi
    python3 -m json.tool "$FILE"
    ;;

  clean)
    if [ "${2:-}" = "--completed" ]; then
      python3 - "$CHECKPOINTS_DIR" << 'PYEOF'
import json, os, sys
cp_dir = sys.argv[1]
removed = 0
for fn in os.listdir(cp_dir):
    if not fn.endswith('.json'): continue
    fp = os.path.join(cp_dir, fn)
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            cp = json.load(f)
        if cp.get('status') == 'completed':
            os.remove(fp)
            removed += 1
            print(f"  ✓ removed {fn}")
    except Exception:
        pass
print(f"\n✅ {removed} completed checkpoint(s) cleaned")
PYEOF
    else
      TASK_ID="${2:?Usage: resume-task.sh clean <task-id>|--completed}"
      FILE="$CHECKPOINTS_DIR/$TASK_ID.json"
      if [ -f "$FILE" ]; then
        rm "$FILE"
        echo "✅ Removed $FILE"
      else
        echo "❌ Not found: $FILE" >&2
        exit 1
      fi
    fi
    ;;

  *)
    cat << HELP
resume-task.sh — manage agent task checkpoints (BCFT-011)

Usage:
  resume-task.sh list                          List all checkpoints
  resume-task.sh show <task-id>                Show checkpoint details
  resume-task.sh clean <task-id>               Delete one checkpoint
  resume-task.sh clean --completed             Delete all completed
HELP
    ;;
esac
