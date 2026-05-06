# becraft Framework Specification (v0.1.0)

> **Master design reference** — All sub-agents working on becraft must follow this spec.

---

## 🎯 Core Philosophy

**Contract-Driven Development (CDD):**
1. **Contract First** — OpenAPI spec + DTOs + error schema BEFORE code
2. **Schema Derived** — DB schema follows DTO entities
3. **Test Pyramid Mandatory** — Unit + Integration (Testcontainers) + Contract tests
4. **Production Baseline** — Logs/metrics/health/rate-limit/idempotency built-in
5. **Self-Healing** — Auto-fix loops for type errors, build errors, test failures (silent)

**Tagline:** *"Craft Production Backends, Not Prototypes"*

---

## 🏗️ Fixed Tech Stack (Phase 1)

| Layer | Technology |
|---|---|
| Runtime | Node.js 22 LTS |
| Framework | NestJS 10 |
| Database | PostgreSQL 16 |
| ORM | Prisma 5 |
| Cache | Redis 7 |
| Queue | BullMQ |
| Auth | Passport (JWT + OAuth) |
| Validation | class-validator + Zod |
| Tests | Jest + Supertest + Testcontainers |
| Container | Docker + docker-compose |
| Deploy | Railway (default), Fly.io (alt) |
| Language | TypeScript (strict) |

**Never ask user "which framework?" — Always use this stack in Phase 1.**

---

## 🤖 Agent Roster (6 agents)

| # | Agent | Emoji | Role | Triggers |
|---|---|---|---|---|
| 1 | plan-orchestrator | 📋 | THE BRAIN — analyze, plan, coordinate | `/be-plan`, `/be-bootstrap` |
| 2 | schema-architect | 📐 | DB schema, migrations, indexes, ER design | `/be-schema` |
| 3 | api-builder | 🔌 | Endpoints, DTOs, controllers, OpenAPI | `/be-api` |
| 4 | auth-guard | 🛡️ | JWT, RBAC, OAuth, rate-limit, CSRF | `/be-auth` |
| 5 | observability | 📊 | Logs, metrics, traces, health checks | `/be-observe` |
| 6 | test-runner | 🧪 | Unit + Integ + Contract + Load tests, auto-fix | `/be-test`, `/be-fix` |

### Agent Dependencies

```
plan-orchestrator (no deps)
    ↓
schema-architect ─┐
                  ├→ api-builder (needs schema)
auth-guard ───────┤
                  ↓
              api-builder
                  ↓
            test-runner ── parallel ── observability
```

### Mandatory Sections in Every Agent File

1. YAML frontmatter (format depends on target — see below)
2. **Memory Protocol** (read 9 / write relevant)
3. **Identity block** (name, role, expertise, motto)
4. **Agent Announcement** (start/parallel/complete templates)
5. **Ultrathink Principles** (4 items)
6. **Parallel Execution declaration** (CAN/MUST WAIT)
7. **`<default_to_action>`, `<use_parallel_tool_calls>`, `<investigate_before_answering>` blocks**
8. **Workflow Phases** (1-5: Investigate → Design → Build → Verify → Report)
9. **Error Recovery patterns**
10. **Code Patterns / Templates**
11. **Quality Standards** (Must Have / Must NOT Have)
12. **Self-Improvement Protocol**
13. **Skills Integration table**

### Agent File Formats

**Claude Code (`src/agents/subagents/*.md`):**
```yaml
---
name: schema-architect
description: |
  Expert database architect. Delegate when: schema design, migrations,
  index optimization, relational modeling.
tools: [Read, Write, Edit, Bash]
model: sonnet
---
```

**Antigravity-friendly (`src/agents/*.md`):**
```yaml
---
name: schema-architect
type: sub-agent
description: >
  Expert database architect for PostgreSQL + Prisma.
skills:
  - schema-design
  - contract-first
  - response-format
triggers:
  - /be-schema command
---
```

Both formats use the SAME body content. Only frontmatter differs.

---

## 🛠️ Skills (10 skills)

| # | Skill | Purpose |
|---|---|---|
| 1 | contract-first | Master workflow — Contract-Driven Development |
| 2 | schema-design | DB schema patterns, normalization, indexes, migrations |
| 3 | api-design | REST conventions, versioning, pagination, errors |
| 4 | auth-patterns | JWT, OAuth, RBAC, RLS, rate limiting |
| 5 | testing-pyramid | Unit + Integration (Testcontainers) + Contract tests |
| 6 | observability | Structured logs, metrics, tracing, health checks |
| 7 | error-handling | Standard error response, retry, idempotency |
| 8 | memory-system | Memory protocol (CORE — always loaded) |
| 9 | response-format | 3-section response (CORE — always loaded) |
| 10 | smart-routing | Intent classification for `/be` smart command (CORE) |

### Skill File Format

```yaml
---
name: schema-design
description: >
  Database schema patterns for PostgreSQL + Prisma...
related_skills:
  - contract-first
  - api-design
---

# Schema Design Skill

[Body with patterns, examples, anti-patterns, checklists]
```

Skill body sections:
- Purpose
- Core Principles (3-5 rules)
- Patterns (with code examples)
- Anti-Patterns (with explanations)
- Checklist
- Integration with other skills

---

## ⚡ Commands (10 commands)

| Command | Shortcut | Description | Loads Skills | Delegates To |
|---|---|---|---|---|
| `/be` | `/b` | Smart router | smart-routing, memory-system | (varies) |
| `/be-help` | `/be-h` | Show all commands | - | - |
| `/be-plan` | `/be-p` | Analyze + plan | contract-first, business-context | plan-orchestrator |
| `/be-bootstrap` | `/be-b` | Full project (Vibe equivalent) | contract-first, schema-design, api-design, auth-patterns | plan + schema + api + auth + test |
| `/be-schema` | `/be-s` | DB schema + migrations | schema-design, contract-first | schema-architect |
| `/be-api` | `/be-a` | Endpoints + DTOs | api-design, contract-first, error-handling | api-builder |
| `/be-auth` | `/be-au` | Authn/Authz | auth-patterns | auth-guard |
| `/be-observe` | `/be-o` | Logging + metrics + traces | observability | observability |
| `/be-test` | `/be-t` | Generate + run tests | testing-pyramid, error-handling | test-runner |
| `/be-fix` | `/be-f` | Debug + fix | error-handling, testing-pyramid | test-runner |

### Command File Format (`src/commands/*.md`)

```yaml
---
description: Create endpoints with DTOs and OpenAPI documentation
---

You are the **becraft API Builder Agent**.

## Your Mission
[clear description]

## Memory Protocol
[read 9 / write relevant]

## Skills to Load
@.claude/skills/api-design/SKILL.md
@.claude/skills/contract-first/SKILL.md
@.claude/skills/error-handling/SKILL.md

## Delegate To
@.claude/agents/api-builder.md

## Workflow
[phases]

## Response Format
[3-section]
```

---

## 💾 Memory System (9 files at `.be/memory/`)

```
.be/memory/
├── active.md              # Current task
├── summary.md             # Project overview + tech stack
├── decisions.md           # ADRs (Architecture Decision Records)
├── changelog.md           # Session changes
├── agents-log.md          # Agent activity log
├── architecture.md        # Service structure + dependency graph
├── api-registry.md        # Endpoints + DTOs + auth requirements
├── schema.md              # DB schema + migration history (BE-specific)
└── contracts.md           # OpenAPI snapshots + breaking change log (BE-specific)
```

**Memory rules:**
- Memory location is `.be/memory/` for BOTH IDEs (cross-IDE sync)
- Claude Code reads `.be/memory/` directly (NOT `.claude/memory/`)
- Antigravity references `.be/memory/` in workflow files
- All agents MUST read 9 files before work, write relevant after

---

## 🔌 IDE Support

### Claude Code

Files installed:
```
project/
├── CLAUDE.md                              # Generated system prompt
├── .claude/
│   ├── agents/*.md                         # Native sub-agent format
│   ├── skills/*/SKILL.md
│   └── commands/be-*.md
└── .be/
    └── memory/*.md                          # Shared memory
```

CLAUDE.md responsibilities:
- Identity ("becraft Orchestrator")
- Tech stack mandate (Fixed)
- Command recognition table
- Skills loading protocol with checkpoint
- Memory protocol (9 files)
- Sub-agent delegation map
- Anti-patterns / required patterns

### Antigravity

Files installed:
```
project/
├── .agent/
│   ├── AGENT.md                            # Generated context
│   └── workflows/be-*.md                   # Bundled workflows
└── .be/
    ├── agents/*.md                         # Reference (Antigravity-format)
    ├── skills/*/SKILL.md                   # Reference
    └── memory/*.md                          # Shared memory
```

Antigravity workflow file = command + orchestrator + agents + skills (all inlined)

Workflow file size estimate: 1,500-3,000 lines per file (self-contained)

---

## 📦 Folder Structure (Source Repo)

```
becraft/
├── bin/becraft-cli.js                      # CLI entry (commander.js)
├── installer/
│   ├── install.js                          # Main installer
│   ├── list.js                             # `becraft list`
│   ├── status.js                           # `becraft status`
│   └── ide-handlers/
│       ├── claude-code.js                  # Setup Claude Code
│       └── antigravity.js                  # Setup Antigravity
├── scripts/
│   └── bundle.js                           # Generate antigravity-workflows
├── src/
│   ├── agents/
│   │   ├── README.md
│   │   ├── plan-orchestrator.md            # Antigravity format
│   │   ├── schema-architect.md
│   │   ├── api-builder.md
│   │   ├── auth-guard.md
│   │   ├── observability.md
│   │   ├── test-runner.md
│   │   └── subagents/                      # Claude Code native format
│   │       └── (same 6 files)
│   ├── skills/
│   │   ├── contract-first/SKILL.md
│   │   ├── schema-design/SKILL.md
│   │   ├── api-design/SKILL.md
│   │   ├── auth-patterns/SKILL.md
│   │   ├── testing-pyramid/SKILL.md
│   │   ├── observability/SKILL.md
│   │   ├── error-handling/SKILL.md
│   │   ├── memory-system/SKILL.md
│   │   ├── response-format/SKILL.md
│   │   └── smart-routing/SKILL.md
│   ├── commands/                           # 10 Claude Code commands
│   ├── antigravity-workflows/              # 10 bundled workflows
│   ├── memory/                             # 9 templates
│   └── templates/
│       └── nestjs-base/                    # Working starter project
├── docs/
│   ├── README.md
│   └── README-TH.md
├── package.json
├── README.md
└── SPEC.md (this file)
```

---

## 🎬 Workflow Patterns

### Pattern 1: Quick Single Endpoint
```
[api-builder]
```

### Pattern 2: New Resource (CRUD)
```
[schema-architect] → [api-builder + auth-guard parallel] → [test-runner]
```

### Pattern 3: Bootstrap Mode (`/be-bootstrap`)
```
[plan] → [schema] → [api+auth+observability parallel] → [test]
```

### Pattern 4: Production Hardening
```
[observability] → [test (load)] → [auth-guard (rate-limit)]
```

---

## ✅ Mandatory Conventions Summary

Every agent / command / workflow MUST include:

1. ✅ **Memory checkpoint** — read 9 files, announce loaded
2. ✅ **Skills loaded checkpoint** — print skills loaded at start of response
3. ✅ **Agent announcement** — `[📐 Schema Architect] Starting: ...`
4. ✅ **Phase-based workflow** — Investigate → Design → Build → Verify → Report
5. ✅ **Quality gate before handoff** — TypeScript clean, build passes, tests pass
6. ✅ **3-section response** — What I Did / What You Get / What You Need To Do
7. ✅ **Memory write before complete** — confirm "✅ Memory saved"
8. ✅ **Self-fix loops** — auto-fix errors silently up to 5 attempts

---

## 🚫 Anti-Patterns (Universal)

- ❌ `console.log` in production code
- ❌ `any` types
- ❌ Stack traces exposed to API
- ❌ Hardcoded secrets
- ❌ Tables without RLS or RBAC check
- ❌ N+1 queries
- ❌ Missing rate limiting
- ❌ No idempotency keys on POST/PUT
- ❌ Sync work in request handlers (no queue)
- ❌ Missing OpenAPI annotations
- ❌ Unvalidated user input

---

## 🎯 Definition of Done (per agent task)

- [ ] All 9 memory files read
- [ ] Required skills loaded + announced
- [ ] OpenAPI spec updated (if API changed)
- [ ] DB schema valid + migration generated (if schema changed)
- [ ] `npm run build` passes (zero TypeScript errors)
- [ ] `npm test` passes (all green)
- [ ] No `any` types added
- [ ] No `console.log` added
- [ ] All env vars documented in `.env.example`
- [ ] Memory updated with changes
- [ ] Response uses 3-section format
- [ ] Next steps suggested

---

*Spec v0.1.0 - For Phase 1 implementation*
