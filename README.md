# 🛠️ becraft

> **"Craft Production Backends, Not Prototypes"**
>
> AI-orchestrated backend development framework — Contract-Driven Development for **Claude Code** + **Google Antigravity**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stack](https://img.shields.io/badge/stack-NestJS%20%2B%20Postgres%20%2B%20Prisma-red.svg)](#tech-stack)

---

## 🎯 What is becraft?

becraft is the **backend equivalent of toh-framework** — instead of UIs, it generates **production-grade APIs** with everything built-in:

- ✅ NestJS endpoints with OpenAPI documentation
- ✅ PostgreSQL + Prisma schema with safe migrations
- ✅ JWT authentication + RBAC + rate limiting
- ✅ Pino structured logs + Prometheus metrics + health checks
- ✅ Jest + Supertest + Testcontainers integration tests
- ✅ Docker + docker-compose ready

**One command builds an entire production backend:**

```
/be-bootstrap user management API with JWT auth
```

---

## 🤖 Supported IDEs

| IDE | Status | Notes |
|-----|--------|-------|
| 🤖 **Claude Code** | ✅ Full Support | Native sub-agent delegation, parallel execution |
| 🌌 **Google Antigravity** | ✅ Full Support | Pre-bundled self-contained workflows |

---

## 📦 Installation

```bash
# Interactive
npx becraft install

# Quick (both IDEs, English)
npx becraft install --quick

# Specific IDE
npx becraft install --ide claude
npx becraft install --ide antigravity
```

After install:
```
your-project/
├── CLAUDE.md             ← Claude Code system prompt
├── .claude/
│   ├── agents/           ← 6 native sub-agents
│   ├── skills/           ← 10 skills
│   └── commands/         ← 10 commands
├── .agent/
│   ├── AGENT.md          ← Antigravity context
│   └── workflows/        ← 10 self-contained workflows
└── .be/
    ├── memory/           ← 9 memory files (cross-IDE shared)
    ├── skills/, agents/, commands/, templates/  ← reference
    └── manifest.json
```

---

## ⚡ Quick Start

### Build complete backend
```
/be-bootstrap user management API
```

### Add a resource
```
/be-schema add Product (name, price, stock)
/be-api create CRUD for products
/be-auth setup JWT
/be-test for products module
```

### Use smart router (anything goes)
```
/be add inventory tracking with audit log
```

The router classifies intent → picks right agent(s) → shows plan → executes.

---

## 🏗️ Tech Stack (Fixed)

| Layer | Technology |
|-------|------------|
| Runtime | Node.js 22 LTS |
| Framework | NestJS 10 |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Queue | BullMQ |
| Auth | Passport (JWT) |
| Validation | class-validator + Zod |
| Tests | Jest + Supertest + Testcontainers |
| Logger | Pino |
| Metrics | Prometheus (prom-client) |
| Container | Docker + docker-compose |
| Language | TypeScript (strict) |

> **ORM:** ผู้ใช้เลือกได้ — Prisma (default & recommended), TypeORM, Drizzle, MikroORM. Skills/agents มีตัวอย่างเป็น Prisma แต่ pattern โดยทั่วไปใช้ได้กับ ORM อื่น

**No decisions to make** — opinionated stack ready to go.

---

## 🧠 Philosophy: Contract-Driven Development (CDD)

```
1. Contract First    → OpenAPI spec + DTOs BEFORE code
2. Schema Derived    → DB schema follows entity types
3. Test Pyramid      → Unit + Integration + Contract tests mandatory
4. Production Baseline → Logs/metrics/health/rate-limit built-in
5. Self-Healing      → Auto-fix loops for type/build/test errors
```

**Result:** Every feature is production-ready from first commit.

---

## 📋 Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| `/be` | `/b` | 🧠 Smart Router — anything backend |
| `/be-help` | `/be-h` | Show all commands |
| `/be-plan` | `/be-p` | 📋 **THE BRAIN** — analyze + plan |
| `/be-bootstrap` | `/be-b` | 🚀 Build full backend |
| `/be-schema` | `/be-s` | 📐 DB schema + migrations |
| `/be-api` | `/be-a` | 🔌 Endpoints + DTOs |
| `/be-auth` | `/be-au` | 🛡️ Authn/Authz |
| `/be-observe` | `/be-o` | 📊 Logs + metrics |
| `/be-test` | `/be-t` | 🧪 Generate + run tests |
| `/be-fix` | `/be-f` | 🔧 Debug + fix |

---

## 🤖 Agents (6)

| Agent | Specialty |
|-------|-----------|
| 📋 **plan-orchestrator** | THE BRAIN — analyze + coordinate |
| 📐 **schema-architect** | PostgreSQL + Prisma schema design |
| 🔌 **api-builder** | NestJS endpoints + OpenAPI |
| 🛡️ **auth-guard** | JWT + RBAC + rate-limit |
| 📊 **observability** | Logs + metrics + health |
| 🧪 **test-runner** | Tests + auto-fix loop |

[See agent details →](src/agents/README.md)

---

## 📚 Skills (10)

- **contract-first** — Master CDD workflow
- **schema-design** — DB patterns, indexing, RLS
- **api-design** — REST conventions, versioning, pagination
- **auth-patterns** — JWT, OAuth, RBAC, rate limiting
- **testing-pyramid** — Unit + Integration + Contract
- **observability** — Logs, metrics, traces
- **error-handling** — RFC 7807, retry, idempotency
- **memory-system** — 9-file memory protocol
- **response-format** — 3-section response standard
- **smart-routing** — Intent classification

---

## 💾 Memory System (9 Files)

Memory at `.be/memory/` — **shared between Claude Code and Antigravity** (cross-IDE sync):

| File | Purpose |
|------|---------|
| `active.md` | Current task |
| `summary.md` | Project overview |
| `decisions.md` | Architecture Decision Records |
| `changelog.md` | Session changes |
| `agents-log.md` | Agent activity log |
| `architecture.md` | Service structure |
| `api-registry.md` | Endpoints + DTOs |
| `schema.md` | DB schema + migrations |
| `contracts.md` | OpenAPI snapshots |

Total budget: ~4,600 tokens for full memory load.

---

## 🚀 What You Get After `/be-bootstrap`

A working backend with:

```bash
http://localhost:3000/docs        # Swagger UI
http://localhost:3000/health      # Health check
http://localhost:3000/health/live # Liveness probe (k8s)
http://localhost:3000/health/ready # Readiness probe (k8s)
http://localhost:3000/metrics     # Prometheus metrics

# Endpoints:
POST   /api/v1/auth/register     (rate-limited 10/hr)
POST   /api/v1/auth/login        (rate-limited 5/min)
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/users/:id         (JWT required)
... and your domain endpoints
```

Plus:
- ✅ All endpoints documented in OpenAPI
- ✅ All inputs validated with class-validator
- ✅ All errors in RFC 7807 Problem Details format
- ✅ All requests have X-Request-Id header
- ✅ JWT with refresh token rotation
- ✅ bcrypt rounds 12+
- ✅ Idempotency keys on POST/PUT
- ✅ Cursor pagination
- ✅ Soft delete (deletedAt)
- ✅ Tests passing with Testcontainers

---

## 🎬 Example: New Resource Workflow

```
User: /be-schema add Product entity

📚 Skills Loaded: schema-design ✅
🤖 Agent: schema-architect
💾 Memory: Loaded ✅ (9 files)

[Schema Architect designs Product model with indexes]

✅ Migration applied: 20260506_add_products
✅ Memory updated: schema.md, changelog.md

User: /be-api create CRUD for products

📚 Skills Loaded: api-design ✅, contract-first ✅
🤖 Agent: api-builder

[API Builder generates module + controller + service + DTOs]

✅ 5 endpoints: POST/GET/GET/:id/PATCH/DELETE
✅ OpenAPI: http://localhost:3000/docs
✅ Memory updated: api-registry.md, contracts.md

User: /be-test for products

[Test Runner generates + runs tests with auto-fix loop]

✅ 12 unit tests + 8 e2e tests, 87% coverage
```

---



## 🛠️ Development

### Project Structure

```
becraft/
├── bin/becraft-cli.js          # CLI entry (commander.js)
├── installer/
│   ├── install.js              # Main installer
│   ├── list.js, status.js
│   └── ide-handlers/
│       ├── claude-code.js
│       └── antigravity.js
├── scripts/
│   └── bundle.js               # Antigravity workflow bundler
├── src/
│   ├── agents/
│   │   ├── *.md                # 6 Antigravity-format agents
│   │   ├── subagents/*.md      # 6 Claude Code native agents
│   │   └── README.md
│   ├── skills/
│   │   └── <skill>/SKILL.md    # 10 skills
│   ├── commands/
│   │   ├── be-*.md             # 10 commands
│   │   └── README.md
│   ├── antigravity-workflows/
│   │   └── be-*.md             # 10 pre-bundled workflows
│   ├── memory/
│   │   └── *.template.md       # 9 memory templates
│   └── templates/
│       └── nestjs-base/        # Working starter project
├── docs/
├── package.json
├── SPEC.md                     # Master design reference
└── README.md
```

### Regenerate Antigravity Workflows

```bash
npx becraft bundle
# or
node scripts/bundle.js
```

---

## 📊 Stats

- 🤖 **6 specialized agents** (3,352 lines)
- 📚 **10 backend skills** (~3,000 lines)
- ⚡ **10 commands** (~2,000 lines)
- 🌌 **10 Antigravity workflows** (auto-bundled)
- 💾 **9 memory file templates**
- 📦 **NestJS starter** (~22 files, production-ready)
- 🧠 **2 IDEs** supported natively
- 🏗️ **1 fixed stack** (no decisions needed)

---

## 📜 License

MIT — see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Inspired by [toh-framework](https://github.com/wasintoh/toh-framework) — credit to Wasin Treesinthuros for the AODD pattern.

becraft adapts the architecture for backend-only Contract-Driven Development.

---

<p align="center">
  <strong>"Craft Production Backends, Not Prototypes."</strong>
</p>

<p align="center">
  Made for Solo Developers who ship production APIs.
</p>
