---
name: memory-system
description: >
  Memory protocol for becraft (9 files at .be/memory/). Read/write rules per
  agent, cross-IDE sync strategy, archive management. CORE skill — always loaded.
related_skills:
  - response-format
  - smart-routing
---

# Memory System Skill

Persistent context layer for becraft. Single source of truth across sessions and IDEs (Claude Code + Antigravity).

---

## 🎯 Purpose

Memory enables AI to:
1. **Resume work** without losing context
2. **Coordinate** multiple agents in same session
3. **Share state** between Claude Code ↔ Antigravity sessions
4. **Audit** what was done and why

---

## 📁 Memory Structure (9 Files)

**Location:** `.be/memory/` (single location for all IDEs)

```
.be/memory/
├── active.md              ← Current task state (~500 tokens)
├── summary.md             ← Project overview + tech stack (~1,000 tokens)
├── decisions.md           ← Architecture Decision Records (~500 tokens)
├── changelog.md           ← Session-by-session changes (~300 tokens)
├── agents-log.md          ← Agent activity log (~300 tokens)
├── architecture.md        ← Service structure (~500 tokens)
├── api-registry.md        ← Endpoints + DTOs + auth (~600 tokens)
├── schema.md              ← DB schema + migrations (~500 tokens)
└── contracts.md           ← OpenAPI snapshots (~400 tokens)
```

**Total budget:** ~4,600 tokens for full memory load

---

## 🔄 Memory Protocol (Lazy — BCFT-001)

### BEFORE Starting ANY Work

```
STEP 1: Read .be/memory/_index.json FIRST
  ├── Lists which files have meaningful content
  ├── Token-efficient — skip empty templates
  └── Format:
      {
        "files": {
          "active":   { "populated": true,  "size_bytes": 850, ... },
          "summary":  { "populated": false, "size_bytes": 0,   ... },
          ...
        }
      }

STEP 2: Read ONLY files where populated == true
  ├── Use parallel tool calls for batched reads
  └── Skip files where populated == false (empty templates)

STEP 3: Fresh project shortcut
  ├── If ALL files have populated == false:
  │   └── Skip memory entirely — just acknowledge "fresh start"
  └── Save ~4,600 tokens on greenfield projects

STEP 4: Build context understanding (from populated files only)
  ├── What's the project about? (summary)
  ├── What's the active task? (active)
  ├── What decisions made? (decisions)
  ├── Current schema state? (schema)
  └── Existing endpoints? (api-registry)

STEP 5: Acknowledge in response
  └── "💾 Memory: Loaded ✅ (N/9 populated files via index)"
```

### Token Savings

| Scenario | Old Protocol | New Lazy Protocol | Savings |
|----------|-------------|-------------------|---------|
| Fresh project (all empty) | ~4,600 tokens | ~150 tokens (just index) | ~97% |
| Mid-project (3-4 populated) | ~4,600 tokens | ~2,000 tokens | ~57% |
| Mature project (all populated) | ~4,600 tokens | ~4,600 tokens | 0% |

### Updating the Index

After writing to a memory file:
```bash
.be/scripts/update-memory-index.sh
```
This auto-detects size + mtime and flips `populated` based on content analysis
(skips template scaffolding markers).

---

## 📜 Append-Only Event Log (BCFT-009)

**Alternative pattern** for high-frequency updates: write events to
`.be/memory/events.jsonl` instead of editing markdown files directly.
Benefits: race-safe, audit trail, replayable, easier concurrent agents.

### Append an event

```bash
.be/scripts/append-event.sh <type> <agent> '<json-data>'

# Examples:
.be/scripts/append-event.sh decision bootstrap-agent \
  '{"id":"ADR-001","decision":"use Supabase JS","reason":"only SUPABASE_URL set"}'

.be/scripts/append-event.sh endpoint_added api-builder \
  '{"method":"GET","path":"/api/v1/products","auth":"public"}'

.be/scripts/append-event.sh file_created api-builder \
  '{"path":"src/products/products.service.ts","lines":85}'
```

### Event Types

| Type | Data Schema |
|------|-------------|
| `decision` | `{id, decision, reason}` |
| `file_created` / `file_modified` | `{path, lines}` |
| `endpoint_added` | `{method, path, auth}` |
| `schema_changed` | `{table, change}` |
| `migration_applied` | `{name, applied_at}` |
| `phase_started` / `phase_completed` | `{phase_name, duration_ms?}` |
| `agent_invoked` / `agent_completed` | `{task, status?}` |
| `stack_detected` | `{stack, source}` |
| `feature_completed` | `{name, files}` |

Full schema: `.be/memory/event-schema.json`

### Snapshot regeneration

```bash
.be/scripts/snapshot-memory.sh
```
Reads `events.jsonl` → regenerates `decisions.md`, `changelog.md`,
`agents-log.md`, `api-registry.md`. Idempotent — running twice produces
the same output.

### When to use events vs direct markdown edits

| Task | Use |
|------|-----|
| Adding 1 ADR | Direct edit `decisions.md` ✅ |
| Logging 50 file creations | Events ✅ |
| Concurrent agents writing | Events ✅ (race-safe) |
| User-facing edits | Direct ✅ (markdown is canonical) |

---

## 💾 Checkpoint Protocol (BCFT-011)

For long-running tasks (>3 phases or >15 files), agents MUST checkpoint after
each phase to enable resume on cancel/crash.

```bash
.be/scripts/resume-task.sh list                     # show checkpoints
.be/scripts/resume-task.sh show <task-id>           # display details
.be/scripts/resume-task.sh clean --completed        # cleanup
```

Checkpoint location: `.be/checkpoints/<task-id>.json`
Format: see `.be/checkpoints/_example.json`

### AFTER Completing Work

```
STEP 1: Update active.md (ALWAYS)
  ├── Current Focus → What was just done
  ├── In Progress → Mark [x] completed
  ├── Just Completed → Add finished items
  └── Next Steps → Suggest next actions

STEP 2: Update changelog.md (ALWAYS)
  └── Add row: | Agent | Action | Files |

STEP 3: Update agents-log.md (ALWAYS)
  └── Add row: | Time | Agent | Task | Status | Files |

STEP 4: Update domain-specific (CONDITIONAL)
  ├── Schema changed? → schema.md
  ├── API endpoint? → api-registry.md + contracts.md
  ├── Architecture? → architecture.md
  ├── Decision made? → decisions.md
  └── Feature done? → summary.md

STEP 5: Confirm
  └── "💾 Memory: Saved ✅"
```

---

## 🤖 Per-Agent Write Rules

| Agent | active | summary | decisions | changelog | agents-log | architecture | api-registry | schema | contracts |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 📋 plan | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | - | - | - |
| 📐 schema | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ | - | ✅ | - |
| 🔌 api | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ | ✅ | - | ✅ |
| 🛡️ auth | ✅ | ⚠️ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ |
| 📊 observe | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | - | - | - |
| 🧪 test | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | - | ⚠️ | - | ⚠️ |

✅ Always | ⚠️ If relevant | - Don't touch

---

## 🌐 Cross-IDE Synchronization

**Problem:** Claude Code + Antigravity may run different sessions
**Solution:** Single `.be/memory/` location

### Both IDEs MUST:
- ✅ Read from `.be/memory/` (NOT `.claude/memory/` or `.agent/memory/`)
- ✅ Write to `.be/memory/`
- ✅ Same UTF-8 format
- ✅ Check mtime before write (concurrency)

---

## 📋 Read Strategies by Task Type

### Quick Fix (single file)
- active.md + changelog.md + relevant domain file

### New Feature
- All 9 files (full context)

### Architecture Change
- All 9 + check archive/ for prior iterations

### Resume Session
1. active.md (where we left off)
2. agents-log.md (last actions)
3. changelog.md (recent changes)
4. summary.md (high-level state)
5. domain-specific based on active task

---

## 🗂️ Archive Strategy

When `active.md` > 50 lines or session ends:
```
1. Snapshot → archive/active-{YYYY-MM-DD-HHMM}.md
2. Reset active.md (keep only Next Steps)
3. Move summary points to summary.md
```

When `changelog.md` > 200 lines:
```
1. Move oldest sessions → archive/changelog-{YYYY-MM}.md
2. Keep last 5 sessions in main
```

Archive NOT loaded by default — only when user asks history.

---

## 📐 File Format Standards

### active.md
```markdown
# 🔥 Active Task

## Current Focus
[One-sentence description]

## In Progress
- [ ] Task 1
- [x] Task 2

## Just Completed
- File X created
- Migration Y applied

## Next Steps
- Suggested action 1

## Blockers / Issues
- (none)

---
*Last updated: {ISO timestamp}*
```

### decisions.md
```markdown
| Date | ADR | Decision | Reason | Trade-offs |
|------|-----|----------|--------|------------|
| 2026-05-06 | ADR-001 | Use Prisma | Type safety + migrations | Lock-in to ORM |
```

### changelog.md
```markdown
## [Session 2026-05-06] - {timestamp}

### Changes Made
| Agent | Action | File/Resource |
|-------|--------|---------------|
| 📐 schema | Added users table | prisma/schema.prisma |
| 🔌 api | Added POST /users | src/users/users.controller.ts |

### Migrations
| Version | Description | Status |
|---------|-------------|--------|
| 20260506_init | Initial users | applied |
```

---

## ⚠️ Critical Rules

1. **NEVER** start without reading 9 files
2. **NEVER** finish without updating relevant files
3. **NEVER** use `.claude/memory/` — always `.be/memory/`
4. **NEVER** ask "should I save?" — just do it
5. **NEVER** delete archive
6. **ALWAYS** keep active.md ≤ 50 lines
7. **ALWAYS** ISO 8601 timestamps
8. **ALWAYS** check mtime before write

---

## 🔍 Health Checks

- [ ] All 9 files exist
- [ ] active.md ≤ 50 lines
- [ ] changelog.md ≤ 200 lines
- [ ] decisions.md sorted by date
- [ ] schema.md matches prisma/schema.prisma
- [ ] api-registry.md matches actual endpoints
- [ ] No stale "In Progress" > 30 days

---

*Memory System Skill v1.0 — Persistent context across sessions and IDEs*
