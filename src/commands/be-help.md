---
description: Show all becraft commands and quick start examples
---

You are responding to `/be-help`. Display this help message immediately.

## 🔒 Skills Loaded
```markdown
📚 **Skills Loaded:** response-format ✅
🤖 **Agent:** help (no agent needed)
💾 **Memory:** Not required for help
```

## Display

```markdown
# 🛠️ becraft — Backend Development Framework

> "Craft Production Backends, Not Prototypes"
>
> Contract-Driven Development with NestJS + PostgreSQL + Prisma

## 📋 Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| `/be` | `/b` | 🧠 **Smart Router** — Type anything, AI picks agent |
| `/be-help` | `/be-h` | ❓ Show this help |
| `/be-plan` | `/be-p` | 📋 **THE BRAIN** — Analyze, plan, orchestrate |
| `/be-bootstrap` | `/be-b` | 🚀 **Build full backend** — Schema + API + Auth + Tests |
| `/be-schema` | `/be-s` | 📐 DB schema + migrations |
| `/be-api` | `/be-a` | 🔌 Endpoints + DTOs + OpenAPI |
| `/be-auth` | `/be-au` | 🛡️ Authn/Authz/RLS/rate-limit |
| `/be-observe` | `/be-o` | 📊 Logging + metrics + traces |
| `/be-test` | `/be-t` | 🧪 Generate + run tests |
| `/be-fix` | `/be-f` | 🔧 Debug + fix issues |

## 🚀 Quick Start

### Build complete backend in one command
\`\`\`
/be-bootstrap user management API with JWT auth
\`\`\`

### Add CRUD for a resource
\`\`\`
/be-schema add Product entity (name, price, stock, category)
/be-api create CRUD for products
\`\`\`

### Add authentication
\`\`\`
/be-auth setup JWT login/register/refresh
\`\`\`

### Generate tests
\`\`\`
/be-test for users module
\`\`\`

## 🏗️ Tech Stack (Fixed)

| Layer | Technology |
|-------|------------|
| Runtime | Node.js 22 LTS |
| Framework | NestJS 10 |
| Database | PostgreSQL 16 |
| ORM (configurable) | Prisma (default) / TypeORM / Drizzle / MikroORM |
| Cache | Redis 7 |
| Queue | BullMQ |
| Auth | Passport (JWT) |
| Validation | class-validator + Zod |
| Tests | Jest + Supertest + Testcontainers |
| Container | Docker |

## 💾 Memory System (9 Files)

Memory is at `.be/memory/` (shared across Claude Code + Antigravity):

- **active.md** — Current task
- **summary.md** — Project overview
- **decisions.md** — ADRs (Architecture Decision Records)
- **changelog.md** — Session changes
- **agents-log.md** — Agent activity
- **architecture.md** — Service structure
- **api-registry.md** — Endpoints + DTOs
- **schema.md** — DB schema + migrations
- **contracts.md** — OpenAPI snapshots

## 🤖 Agents (6)

| Agent | Specialty |
|-------|-----------|
| 📋 plan-orchestrator | THE BRAIN — analyze + coordinate |
| 📐 schema-architect | PostgreSQL + Prisma schema |
| 🔌 api-builder | NestJS endpoints + OpenAPI |
| 🛡️ auth-guard | JWT + RBAC + rate-limit |
| 📊 observability | Logs + metrics + health |
| 🧪 test-runner | Tests + auto-fix loop |

## 📚 Skills (10)

- `contract-first` — Master CDD workflow
- `schema-design` — DB patterns
- `api-design` — REST conventions
- `auth-patterns` — JWT, OAuth, RBAC, RLS
- `testing-pyramid` — Unit + Integration + Contract
- `observability` — Logs + metrics + traces
- `error-handling` — RFC 7807 + retry + idempotency
- `memory-system` — Memory protocol
- `response-format` — 3-section response
- `smart-routing` — Intent classification

## 📖 Docs

- GitHub: https://github.com/becraft/becraft
- Skills: `.claude/skills/<skill>/SKILL.md`
- Agents: `.claude/agents/<agent>.md`
- Templates: `.be/templates/nestjs-base/`

---

**Need more help?** Try:
- `/be analyze my project` — AI inspects your code + suggests next steps
- `/be-plan` — Show planning workflow
- `/be-bootstrap` (without args) — Tells you what bootstrap does
```
