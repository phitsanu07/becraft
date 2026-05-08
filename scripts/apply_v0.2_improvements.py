#!/usr/bin/env python3
"""
Apply v0.2 improvements to all agent files.

Tickets:
- BCFT-002: Progress Reporting (all 12 agents)
- BCFT-003: Parallelization Rules (all 12 agents)
- BCFT-007: Quality Gate (all 12 agents)
- BCFT-004: Stack Detection (api-builder, schema-architect, test-runner — 6 files)
- BCFT-001: Memory Protocol → Lazy (note prepended to all agents)
"""

from pathlib import Path
import re

ROOT = Path(__file__).parent.parent
NATIVE = ROOT / "src" / "agents" / "subagents"
ANTIGRAV = ROOT / "src" / "agents"

# ============================================================
# New sections (content)
# ============================================================

PROGRESS_REPORTING = """## 📡 Progress Reporting (MANDATORY — BCFT-002)

You MUST emit a status message:
- **Before starting any phase** — announce phase name + estimated duration + file count
- **After every 5 file creations/edits** — show batch summary `[N/total] ✓ files`
- **When making non-obvious decisions** — announce reasoning briefly
- **Before any Bash command longer than 10 sec** — let user know what's running
- **When blocked or waiting on user input** — explicit prompt

### Format

```text
[Phase: Bootstrap] Setting up project skeleton (~10 files, ~30s)
[3/17] ✓ tsconfig.json, nest-cli.json, .eslintrc.js
[Phase: Modules] Creating SupabaseModule + ProductsModule in parallel
[8/17] ✓ supabase.module.ts, supabase.service.ts, products DTOs (5)
[Decision] Using offset pagination — cursor not specified in DTOs
[Running] npm install (~20s)…
[12/17] ✓ products.controller.ts, products.service.ts
[Phase: Wiring] Connecting modules to app.module.ts (sequential)
[17/17] ✓ Done — quality gate next
```

### ⚠️ Why This Matters
- Failure to report = work appears stuck = user cancels = wasted effort
- User must always be able to answer "what's the agent doing right now?"
- Verbosity is acceptable trade-off for transparency

---

"""

PARALLELIZATION_RULES = """## 🚀 Parallelization Rules (BCFT-003)

### Files that MUST be batched in a single message (independent)

- **All DTOs** in a feature folder (create-*.dto.ts, update-*.dto.ts, response-*.dto.ts)
- **All sibling config files** (tsconfig, nest-cli, eslintrc, prettierrc, jest.config)
- **All entity files within one feature** (controller + service + module + DTOs)
- **Multiple feature modules** at the same level (users + products + orders modules)
- **All test files** for sibling features

### Files that MUST be sequential (have dependencies)

- `main.ts` — depends on `app.module.ts` existing
- `app.module.ts` — must know which feature modules to import
- `package.json` — final deps inferred from generated code
- Migration files — depend on schema being finalized

### Tool Usage

Use **multiple `Write` tool calls in a single assistant message** — Claude Code
will execute them in parallel. Do NOT do one Write per message when files are
independent.

### ⚠️ Anti-pattern
```
❌ Write file 1 → Write file 2 → Write file 3 (3 separate turns)
✅ Write file 1 + file 2 + file 3 (1 turn, parallel)
```

---

"""

QUALITY_GATE = """## 🚦 Quality Gate (BEFORE claiming done — BCFT-007)

Before reporting success, run these checks:

### 1. Build Check
```bash
npm run build      # Or: npx tsc --noEmit (faster, type-only)
```
Must exit 0 with zero errors.

### 2. Lint Check
```bash
npm run lint       # Warnings OK; errors NOT OK
```

### 3. File Completeness
- List every file in your "What I Did" section
- Verify each exists with non-zero size
- Confirm imports resolve

### 4. Memory Index Updated
- `.be/memory/_index.json` reflects new file states
- Touched memory files have `populated: true`

### Report Shape (Success)

```text
✅ All quality gates passed
- Build: pass (0 errors)
- Lint: 0 errors, N warnings
- Files: M/M present
- Memory index: updated
```

### Report Shape (Failure)

```text
🚫 Quality gate failed
- Build: 2 TS errors in src/products/products.service.ts (lines 23, 45)
- Action: Fixing now and re-running…
```

### ⚠️ NEVER claim success if any check fails. Either fix-and-retry or escalate.

---

"""

STACK_DETECTION = """## 🔍 Stack Detection (MUST RUN FIRST — BCFT-004)

Before any tooling decision, determine the project's Data Access layer:

### Detection Order

1. **Explicit user choice** in current request (e.g., "use Supabase JS")
2. **`.be/memory/decisions.md`** — recent ADRs about Data Access
3. **`.env` / `.env.example`** signals:
   - `DATABASE_URL` only → **Prisma** (default)
   - `SUPABASE_URL` + `SUPABASE_ANON_KEY` only → **Supabase JS Client**
   - both → **Prisma** (default; Supabase URL is for REST/admin)
   - `TYPEORM_*` → **TypeORM**
   - `DRIZZLE_*` → **Drizzle**
4. **`package.json` deps**:
   - `@prisma/client` → Prisma
   - `@supabase/supabase-js` (no Prisma) → Supabase JS
   - `typeorm` + `@nestjs/typeorm` → TypeORM
   - `drizzle-orm` → Drizzle
5. **Fall back** to default in `CLAUDE.md` "Flexible Stack" section
6. **If still unclear** → **ASK USER, do NOT guess**

### ⚠️ Critical Rules

- Do NOT force Prisma if any signal points to a different layer
- Code patterns + skill examples MUST adapt to detected stack
- Announce detected stack in progress message:
  ```
  [Stack Detected] Supabase JS Client (from .env: SUPABASE_URL)
  ```

---

"""

LAZY_MEMORY_NOTE = """> 🆕 **BCFT-001 Lazy Memory:** Read `.be/memory/_index.json` FIRST.
> Only read files where `populated == true`. Skip empty templates to save tokens.
> Fresh project (all `populated == false`) → skip memory entirely.

"""

# ============================================================
# Files mapping
# ============================================================

# Apply Stack Detection only to these agents
STACK_AWARE_AGENTS = {'api-builder', 'schema-architect', 'test-runner'}

def get_agent_name(filepath: Path) -> str:
    """Extract agent name from file path (without .md)."""
    return filepath.stem


def has_section(content: str, section_marker: str) -> bool:
    """Check if a section is already present (idempotent)."""
    return section_marker in content


def insert_after_title(content: str, new_section: str) -> str:
    """Insert new section after the first H1 title (# Title vX.Y)."""
    lines = content.split('\n')
    out = []
    inserted = False

    for i, line in enumerate(lines):
        out.append(line)
        # After H1 + blank line, before next content
        if not inserted and line.startswith('# ') and 'Agent v' in line:
            # Find next non-blank line, insert before it
            out.append('')
            out.append(new_section.rstrip())
            out.append('')
            inserted = True

    return '\n'.join(out)


def insert_before_memory_protocol(content: str, new_section: str) -> str:
    """Insert before '## 🚨 Memory Protocol' section."""
    marker = '## 🚨 Memory Protocol'
    if marker not in content:
        return content
    return content.replace(marker, new_section.rstrip() + '\n\n' + marker, 1)


def prepend_lazy_memory_note(content: str) -> str:
    """Add lazy memory note inside Memory Protocol section."""
    marker = '## 🚨 Memory Protocol'
    if marker not in content or 'BCFT-001 Lazy Memory' in content:
        return content

    # Find the marker, then the next blank line after it
    idx = content.find(marker)
    # Find end of the heading line
    end_of_line = content.find('\n', idx)
    if end_of_line == -1:
        return content
    # Insert lazy note right after heading line
    return content[:end_of_line + 1] + '\n' + LAZY_MEMORY_NOTE + content[end_of_line + 1:]


def append_section_before_response_format(content: str, new_section: str) -> str:
    """Insert before '## 📝 Response Format' or at end if not found."""
    markers = [
        '## 📝 Response Format',
        '## Response Format',
        '## 📝 ',
    ]
    for marker in markers:
        if marker in content:
            return content.replace(marker, new_section.rstrip() + '\n\n' + marker, 1)
    # Fallback: append at end
    return content.rstrip() + '\n\n' + new_section


# ============================================================
# Process files
# ============================================================

def process_file(filepath: Path):
    """Apply all v0.2 improvements to a single agent file."""
    if filepath.name == 'README.md':
        return None

    name = get_agent_name(filepath)
    content = filepath.read_text(encoding='utf-8')
    original_size = len(content)
    changes = []

    # BCFT-002: Progress Reporting (after title)
    if not has_section(content, 'Progress Reporting (MANDATORY — BCFT-002)'):
        content = insert_after_title(content, PROGRESS_REPORTING)
        changes.append('BCFT-002')

    # BCFT-003: Parallelization Rules (before Memory Protocol)
    if not has_section(content, 'Parallelization Rules (BCFT-003)'):
        content = insert_before_memory_protocol(content, PARALLELIZATION_RULES)
        changes.append('BCFT-003')

    # BCFT-004: Stack Detection (only for affected agents, before Memory Protocol)
    if name in STACK_AWARE_AGENTS:
        if not has_section(content, 'Stack Detection (MUST RUN FIRST — BCFT-004)'):
            content = insert_before_memory_protocol(content, STACK_DETECTION)
            changes.append('BCFT-004')

    # BCFT-001: Lazy Memory note (inside Memory Protocol)
    if not has_section(content, 'BCFT-001 Lazy Memory'):
        content = prepend_lazy_memory_note(content)
        changes.append('BCFT-001')

    # BCFT-007: Quality Gate (before Response Format)
    if not has_section(content, 'Quality Gate (BEFORE claiming done — BCFT-007)'):
        content = append_section_before_response_format(content, QUALITY_GATE)
        changes.append('BCFT-007')

    if changes:
        filepath.write_text(content, encoding='utf-8')
        new_size = len(content)
        delta = new_size - original_size
        return {
            'file': str(filepath.relative_to(ROOT)),
            'agent': name,
            'changes': changes,
            'size_delta': delta,
        }
    return None


def main():
    print("🛠️  Applying v0.2 improvements (BCFT-001, 002, 003, 004, 007)\n")

    files = list(NATIVE.glob('*.md')) + list(ANTIGRAV.glob('*.md'))

    results = []
    for f in files:
        result = process_file(f)
        if result:
            results.append(result)
            print(f"✓ {result['agent']:25s} ({result['file']:50s}) "
                  f"[{', '.join(result['changes'])}] +{result['size_delta']} bytes")

    print(f"\n📊 Total: {len(results)} files modified")

    # Stats by ticket
    by_ticket = {}
    for r in results:
        for c in r['changes']:
            by_ticket[c] = by_ticket.get(c, 0) + 1

    print("\n📋 Coverage:")
    for ticket, count in sorted(by_ticket.items()):
        print(f"   {ticket}: {count} files")


if __name__ == '__main__':
    main()
