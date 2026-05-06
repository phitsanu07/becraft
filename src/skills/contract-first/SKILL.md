---
name: contract-first
description: >
  Master workflow skill for becraft — enforces Contract-Driven Development.
  Routes any backend request through Contract → Schema → Code → Test → Production.
related_skills:
  - schema-design
  - api-design
  - auth-patterns
  - testing-pyramid
  - response-format
---

# Contract-First Skill (Master Workflow)

Master brain for backend development — transform any idea into a **production-grade, contract-driven** API service.

---

## 🌟 Core Philosophy

**"Contract First, Code Second, Production Third"**

```
❌ OLD WAY (Code-First):
   User: "Add user registration"
   Output: Controller → Service → DB → "tests later"

✅ NEW WAY (Contract-Driven):
   User: "Add user registration"
   Output:
   - OpenAPI spec written
   - DTOs defined (request/response)
   - DB schema derived from DTOs
   - Implementation matches contract
   - Tests verify contract
   - Logs/metrics/health built-in
   - Idempotency + rate limit ready
```

---

## 🎯 Premium Production Baseline (MANDATORY)

Every backend feature MUST include:

| Concern | Requirement |
|---------|-------------|
| **Contract** | OpenAPI annotations on every endpoint |
| **Validation** | class-validator + Zod on every input |
| **Errors** | RFC 7807 Problem Details format |
| **Logs** | Pino structured logs with request-id |
| **Metrics** | RED metrics (Rate, Errors, Duration) |
| **Health** | `/health/live` + `/health/ready` |
| **Auth** | JWT guard or @Public() decorator (no implicit) |
| **Rate limit** | All `/auth/*` + write endpoints |
| **Idempotency** | POST/PUT with side effects need keys |
| **Tests** | Unit + Integration (Testcontainers) |

---

## 📋 Memory Protocol

### Before ANY Work — Read 9 files in PARALLEL
```
.be/memory/
├── active.md           (current task)
├── summary.md          (project overview)
├── decisions.md        (past ADRs)
├── changelog.md        (session changes)
├── agents-log.md       (agent activity)
├── architecture.md     (service structure)
├── api-registry.md     (endpoints)
├── schema.md           (DB state)
└── contracts.md        (OpenAPI snapshots)
```

### After Work — Update relevant files + confirm

---

## 🛠️ Required Skills (load before work)

When `/be-bootstrap` triggered, read these in parallel:
1. `schema-design/SKILL.md` — DB patterns
2. `api-design/SKILL.md` — REST conventions
3. `auth-patterns/SKILL.md` — Authn/Authz
4. `testing-pyramid/SKILL.md` — Test strategy
5. `observability/SKILL.md` — Production baseline
6. `error-handling/SKILL.md` — Error format
7. `response-format/SKILL.md` — Output format

---

## 🔄 Workflow Decision Tree

```
USER PROMPT
    │
    ▼
┌─────────────────────────────────────┐
│ 🚨 STEP 0: MEMORY (MANDATORY)       │
│  • Read 9 files in parallel         │
│  • Build context                    │
│  • Acknowledge: "Memory loaded ✅"  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 1: CONTRACT FIRST              │
│  • Define OpenAPI spec              │
│  • Define DTOs (request/response)   │
│  • Define error schema              │
│  • Declare auth requirements        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 2: SCHEMA DERIVED              │
│  • Map DTO entities → DB tables     │
│  • Add indexes (FK, unique, query)  │
│  • Generate Prisma migration        │
│  • Verify with --create-only        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 3: IMPLEMENTATION              │
│  • Controller signatures match contract │
│  • Service implements business rules │
│  • Repository abstracts DB          │
│  • Auth guards applied              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 4: VERIFICATION (3 layers)     │
│  • Contract tests (vs OpenAPI)      │
│  • Integration tests (Testcontainers) │
│  • Unit tests (business logic)      │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 5: PRODUCTION READY            │
│  • Pino structured logs             │
│  • Prometheus /metrics              │
│  • Health endpoints                 │
│  • Rate limit configured            │
│  • Idempotency keys                 │
│  • OpenAPI auto-served at /docs     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 🚨 STEP 6: SAVE MEMORY (MANDATORY)  │
│  • Update active.md                 │
│  • Update changelog.md              │
│  • Update domain files (api/schema) │
│  • Confirm: "✅ Memory saved"       │
└─────────────────────────────────────┘
```

---

## 🤖 Agent Spawning Order

### Pattern: Full Resource (Bootstrap Mode)

```
plan-orchestrator (analyze + plan)
        │
        ▼
schema-architect (DB design)
        │
        ▼
   ┌────┴────┐
   │         │
   ▼         ▼
api-builder  auth-guard
(parallel in Claude Code, sequential in Antigravity)
        │
        ▼
   ┌────┴────┐
   │         │
   ▼         ▼
test-runner  observability
(parallel)
```

### Pattern: Single Task

```
api-builder (just /api work)
test-runner (auto-fix loop)
```

---

## 🛡️ Sub-Agent Spawn Instructions

### To schema-architect
```
Design database schema for [entity]

Context:
- Read existing prisma/schema.prisma
- Read .be/memory/api-registry.md (existing entities)
- Read .be/memory/decisions.md (past schema decisions)

Requirements:
- Follow schema-design skill
- All tables have id (uuid), created_at, updated_at
- All FK columns indexed
- Soft delete: deleted_at if entity is user-facing
- RLS templates for owner-only / public / admin

Output: Updated prisma/schema.prisma + migration
```

### To api-builder
```
Build API endpoints for [resource]

Context:
- Schema file: prisma/schema.prisma (read it)
- DTOs go in: src/<resource>/dto/
- Controller: src/<resource>/<resource>.controller.ts
- Service: src/<resource>/<resource>.service.ts

Requirements:
- Follow api-design skill
- All endpoints have @ApiOperation + @ApiResponse
- Validation: class-validator + Zod
- Pagination: use shared PaginationDto
- Errors: throw HttpException with RFC 7807 format
- Soft delete: PATCH /:id with deleted_at = now()
- Versioning: /api/v1/<resource>

Output: Module + Controller + Service + DTOs + tests stub
```

### To auth-guard
```
Setup authentication / authorization for [feature]

Requirements:
- Follow auth-patterns skill
- JWT strategy (access + refresh)
- @UseGuards(JwtAuthGuard) by default; @Public() opt-in
- Rate limit /auth/* (5 req/min)
- bcrypt for passwords (work factor 12+)
- Password requirements: 8+ chars, mixed case, number

Output: AuthModule + strategies + guards + DTO + tests
```

### To test-runner
```
Generate + run tests for [feature]

Requirements:
- Follow testing-pyramid skill
- Unit tests: services with mocked deps
- Integration: real PostgreSQL via Testcontainers
- Contract: validate against OpenAPI spec
- Auto-fix loop: max 5 attempts
- Coverage target: 80%+

Output: *.spec.ts files + coverage report
```

### To observability
```
Setup production observability

Requirements:
- Follow observability skill
- Pino structured JSON logs
- Request-id middleware
- Prometheus /metrics (RED method)
- /health/live + /health/ready
- DO NOT log: passwords, tokens, full request bodies

Output: Logger config + metrics + health endpoints
```

---

## ❌ Anti-Patterns

### ❌ Code Before Contract
```
WRONG: Write controller first, then "fix tests later"
RIGHT: Write OpenAPI annotations + DTOs → derive controller signature
```

### ❌ Schema Before Types
```
WRONG: Design SQL first, then map to TypeScript
RIGHT: Define TS types → generate schema → generate Prisma migration
```

### ❌ Skipping Production Baseline
```
WRONG: "Add logs/metrics later"
RIGHT: Logs + metrics + health from first commit
```

### ❌ Multiple Options
```
WRONG: "Should I use express-rate-limit or Throttler?"
RIGHT: Pick ONE (NestJS @Throttler), implement, move on
```

### ❌ Asking Basic Questions
```
WRONG: "Which database?" / "Which auth strategy?"
RIGHT: PostgreSQL + JWT (decided in stack profile)
```

---

## ✅ Decision Defaults (Don't Ask)

| Question | Decision |
|----------|----------|
| Framework? | NestJS 10 |
| DB? | PostgreSQL 16 + Prisma 5 |
| Cache? | Redis 7 |
| Queue? | BullMQ |
| Auth? | Passport (JWT access + refresh) |
| Validation? | class-validator + Zod |
| Logger? | Pino (JSON) |
| Test? | Jest + Supertest + Testcontainers |
| Container? | Docker + docker-compose |
| API style? | REST (GraphQL only if user requests) |
| Versioning? | URI (`/api/v1/...`) |
| Pagination? | Cursor-based (offset for admin only) |
| Errors? | RFC 7807 Problem Details |
| ID type? | UUID v4 (not serial) |

---

## 📝 Output Standards

After every contract-first execution, deliver:

1. **OpenAPI spec** updated (`/docs` endpoint)
2. **Prisma migration** generated and verified
3. **Tests** generated and passing
4. **Memory** updated (api-registry, schema, contracts)
5. **3-section response** to user with curl examples

Example curl in "What You Need To Do":
```bash
curl -X POST http://localhost:3000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

---

## 🎯 Success Criteria

A backend feature is "done" when:
- [ ] OpenAPI annotations complete on every endpoint
- [ ] Validation (class-validator + Zod) on every input
- [ ] Standard error format (RFC 7807)
- [ ] Auth guard explicit (or @Public)
- [ ] Pino logs + request-id
- [ ] /metrics + /health endpoints exist
- [ ] Rate limit on auth + writes
- [ ] Tests passing (unit + integration)
- [ ] `npm run build` passes
- [ ] Memory updated
- [ ] User can `curl` against running API

---

*Contract-First Skill v1.0 — Master CDD workflow*
