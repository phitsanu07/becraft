# Changelog

All notable changes to becraft will be documented in this file.

## [0.4.0] — 2026-05-08

### 🎉 Production-Ready Milestone

becraft v0.4 implements all 13 tickets from the v0.2 improvement spec
(`IMPROVEMENTS.md`). The framework is now production-ready with progress
visibility, checkpoint resilience, cost-aware models, and full template support.

### Added (Sprint 4 — Scaling)

- **BCFT-009 Memory Append-Only Event Log**
  - `.be/memory/events.jsonl` — append-only event stream
  - `.be/memory/event-schema.json` — JSON Schema validation
  - `.be/scripts/append-event.sh` — log events safely
  - `.be/scripts/snapshot-memory.sh` — regenerate `*.md` from events (idempotent)

- **BCFT-011 Checkpoint / Resume Mechanism**
  - `.be/checkpoints/` — per-task JSON checkpoints
  - `.be/scripts/resume-task.sh` — list/show/clean checkpoints
  - Checkpoint protocol documented in plan-orchestrator agent

- **BCFT-012 Cost-Aware Model Selection**
  - Per-agent `model:` field in YAML frontmatter:
    - plan-orchestrator → `opus`
    - bootstrap-agent / schema-architect / api-builder / auth-guard → `sonnet`
    - observability / test-runner → `haiku`
  - Estimated ~40% cost reduction

- **BCFT-013 Snippet System**
  - `.be/snippets/` — 7 reusable TypeScript code patterns:
    - `nestjs-bootstrap.ts`, `prisma-service.ts`, `supabase-service.ts`
    - `pagination-helper.ts`, `error-handler.ts`, `env-validation.ts`, `swagger-setup.ts`
  - bootstrap-agent references snippets instead of inlining
  - Estimated ~30% prompt token reduction

### Added (Sprint 3 — Architecture)

- **BCFT-006 Bootstrap Template Mode**
  - `.be/scripts/bootstrap.sh` — copy + customize template (~5 sec)
  - `.be/templates/nestjs-supabase/` — Supabase JS variant (12 files)
  - `nestjs-base/` (Prisma) and `nestjs-supabase/` (Supabase JS) both available

- **BCFT-008 Split Bootstrap Agent**
  - `bootstrap-agent` — new specialist for project skeleton (greenfield only)
  - `api-builder` updated to disclaim bootstrap responsibilities
  - Agent table in CLAUDE.md updated to include 7 agents (was 6)

- **BCFT-010 Confidence × Size Routing Matrix**
  - Smart router scores both confidence and task size
  - Bootstrap tasks always go through plan-orchestrator first
  - `<70%` confidence → ASK USER (no silent guessing)

### Added (Sprint 2 — Stack & Quality)

- **BCFT-004 Stack Detection in Agents**
  - api-builder, schema-architect, test-runner detect stack from `.env` + deps
  - Override propagated from CLAUDE.md → individual agents

- **BCFT-005 Pre-flight Checklist**
  - Smart router validates: stack explicit / prerequisites / project state /
    scope / no conflicting decisions BEFORE delegating

- **BCFT-007 Quality Gate**
  - All agents must run build + lint + file completeness check
    BEFORE claiming success

### Added (Sprint 1 — Quick Wins)

- **BCFT-001 Lazy Memory Protocol**
  - `.be/memory/_index.json` tracks which files have meaningful content
  - Agents read only populated files (~50% token saving on mid-projects,
    ~97% on fresh projects)
  - `.be/scripts/update-memory-index.sh` auto-detects template scaffolding

- **BCFT-002 Mandatory Progress Reporting**
  - All 12 agents required to emit progress messages every 5 files /
    every phase transition / every >10s operation
  - Format: `[N/total] ✓ files`, `[Phase: X] description`, `[Decision] reason`

- **BCFT-003 Parallelization Rules**
  - Explicit list of files agents MUST batch in single message
  - Explicit list of files that MUST be sequential
  - Anti-pattern: one Write per turn

### Changed

- Memory Protocol from "always read 9 files" → "lazy index-based"
- Tech Stack section in CLAUDE.md / AGENT.md / SPEC.md / README.md:
  ORM moved out of "Fixed Stack (NEVER CHANGE)" → "user-configurable"
- API Builder no longer handles bootstrap (delegated to bootstrap-agent)
- All Antigravity workflows re-bundled with new sections (~7,000 lines total)

### Notes

- 35 files modified, 4,041+ lines added, ~50 files now version-controlled
- All changes verified end-to-end via `becraft install --quick` test
- 13/13 tickets from `IMPROVEMENTS.md` completed

---

## [0.1.0] — 2026-05-06

### Initial Release

- 6 agents (plan-orchestrator, schema-architect, api-builder, auth-guard,
  observability, test-runner)
- 10 skills (contract-first, schema-design, api-design, auth-patterns,
  testing-pyramid, observability, error-handling, memory-system,
  response-format, smart-routing)
- 10 commands (`/be`, `/be-help`, `/be-plan`, `/be-bootstrap`, `/be-schema`,
  `/be-api`, `/be-auth`, `/be-observe`, `/be-test`, `/be-fix`)
- 9-file memory system at `.be/memory/`
- NestJS + PostgreSQL + Prisma starter template
- Multi-IDE support: Claude Code + Google Antigravity
- 10 pre-bundled Antigravity workflows
