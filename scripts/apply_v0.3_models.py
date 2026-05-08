#!/usr/bin/env python3
"""
BCFT-012: Apply per-agent model selection to optimize cost/performance.

Recommended assignments (per IMPROVEMENTS.md):
- plan-orchestrator → opus    (complex reasoning, decomposition)
- bootstrap-agent   → sonnet  (template-heavy + decisions)
- schema-architect  → sonnet  (domain expertise, constrained)
- api-builder       → sonnet  (templated work, good speed/quality)
- auth-guard        → sonnet  (security-sensitive, pattern-based)
- observability     → haiku   (mostly config wiring)
- test-runner       → haiku   (mechanical: write/run/parse tests)

Note: Antigravity-format agents do NOT have `model:` field (Antigravity uses
single AI). Only Claude Code native (subagents/) gets model assignment.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
NATIVE = ROOT / "src" / "agents" / "subagents"

MODEL_ASSIGNMENTS = {
    'plan-orchestrator': 'opus',
    'bootstrap-agent': 'sonnet',
    'schema-architect': 'sonnet',
    'api-builder': 'sonnet',
    'auth-guard': 'sonnet',
    'observability': 'haiku',
    'test-runner': 'haiku',
}


def update_model(filepath: Path, target_model: str) -> dict:
    content = filepath.read_text(encoding='utf-8')
    # Match `model: <something>` in YAML frontmatter (case sensitive)
    pattern = re.compile(r'^model:\s*(\w+)\s*$', re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return {'file': filepath.name, 'status': 'no model field', 'changed': False}

    old_model = match.group(1)
    if old_model == target_model:
        return {'file': filepath.name, 'status': f'already {target_model}', 'changed': False}

    new_content = pattern.sub(f'model: {target_model}', content, count=1)
    filepath.write_text(new_content, encoding='utf-8')
    return {
        'file': filepath.name,
        'status': f'{old_model} → {target_model}',
        'changed': True,
    }


def main():
    print("🎯 BCFT-012: Setting per-agent model selection\n")

    total_changed = 0
    for agent_name, target in MODEL_ASSIGNMENTS.items():
        filepath = NATIVE / f"{agent_name}.md"
        if not filepath.exists():
            print(f"   ⚠️  {agent_name}.md not found")
            continue
        result = update_model(filepath, target)
        prefix = '✓' if result['changed'] else '○'
        print(f"   {prefix} {result['file']:25s} {result['status']}")
        if result['changed']:
            total_changed += 1

    print(f"\n📊 Total: {total_changed} agents updated")
    print("\nCost impact estimate:")
    print("  - Opus (plan):      $$ (complex reasoning, used sparingly)")
    print("  - Sonnet (4 agents): $   (default for most work)")
    print("  - Haiku (2 agents):  ¢   (mechanical work, 3x cheaper)")


if __name__ == '__main__':
    main()
