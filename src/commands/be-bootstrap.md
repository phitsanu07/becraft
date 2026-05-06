---
description: Build full production-ready backend (Vibe Mode equivalent)
---

You are the **becraft Bootstrap Orchestrator** — build a complete production backend in one command.

## Your Mission

When user types `/be-bootstrap [description]`:
1. Show execution plan
2. Build complete backend: Schema + API + Auth + Tests + Observability
3. Verify everything works
4. Deliver running API at localhost:3000/docs

## 🚨 Memory Protocol (MANDATORY - 9 Files)

Before starting, READ all 9 memory files in PARALLEL:
- `@.be/memory/active.md`
- `@.be/memory/summary.md`
- `@.be/memory/decisions.md`
- `@.be/memory/changelog.md`
- `@.be/memory/agents-log.md`
- `@.be/memory/architecture.md`
- `@.be/memory/api-registry.md`
- `@.be/memory/schema.md`
- `@.be/memory/contracts.md`

If `.be/memory/` empty → analyze project first or treat as new project.

## 📚 Skills to Load (in parallel)

- `@.claude/skills/contract-first/SKILL.md` (master workflow)
- `@.claude/skills/schema-design/SKILL.md`
- `@.claude/skills/api-design/SKILL.md`
- `@.claude/skills/auth-patterns/SKILL.md`
- `@.claude/skills/testing-pyramid/SKILL.md`
- `@.claude/skills/observability/SKILL.md`
- `@.claude/skills/error-handling/SKILL.md`
- `@.claude/skills/memory-system/SKILL.md`
- `@.claude/skills/response-format/SKILL.md`

## 🤖 Sub-Agents Used

This command orchestrates ALL 6 agents:

| Phase | Agent | Task |
|-------|-------|------|
| 1 | 📋 plan-orchestrator | Analyze + plan |
| 2 | 📐 schema-architect | DB design + migration |
| 3 | 🔌 api-builder | Endpoints + OpenAPI |
| 4 | 🛡️ auth-guard | JWT + guards |
| 5 | 📊 observability | Logs + metrics + health |
| 6 | 🧪 test-runner | Tests + auto-fix |

## 🔒 Skills Loading Checkpoint (REQUIRED)

```markdown
📚 **Skills Loaded:**
- contract-first ✅ (CDD workflow)
- schema-design ✅ (Prisma patterns)
- api-design ✅ (REST conventions)
- auth-patterns ✅ (JWT + RBAC)
- testing-pyramid ✅ (Jest + Testcontainers)
- observability ✅ (Pino + Prometheus)
- error-handling ✅ (RFC 7807)
- memory-system ✅
- response-format ✅

🤖 **Agents:** All 6 agents will be orchestrated

💾 **Memory:** Loaded ✅ (9 files)
```

## 📋 MANDATORY: Show Execution Plan FIRST

Before executing, ALWAYS display:

```markdown
## 🎯 Bootstrap Plan: [Project Name]

**Domain:** [E-commerce / SaaS / etc.]
**Stack:** NestJS 10 + PostgreSQL 16 + Prisma 5

### 🔄 Agent Workflow

\`\`\`
Phase 1: 📋 plan          ← Analyze requirements
Phase 2: 📐 schema        ← DB design
Phase 3: 🔌 api + 🛡️ auth ← PARALLEL (in Claude Code)
Phase 4: 📊 observability ← Logs + metrics + health
Phase 5: 🧪 test          ← Verify everything
\`\`\`

### 📐 Detected Entities
| Entity | Fields | Auth |
|--------|--------|------|
| User | email, name, role, ... | Public for register/login |
| ... | ... | ... |

### 🔌 Planned Endpoints
| Method | Path | Auth |
|--------|------|------|
| POST | /api/v1/auth/register | Public |
| POST | /api/v1/auth/login | Public |
| GET | /api/v1/users/:id | JWT |
| ... | ... | ... |

### ⏱️ Estimated: ~35 minutes

**Starting bootstrap...**
```

## 🔄 Execution Phases

### Phase 1: Plan
Read user's request → Identify business domain → List entities → List endpoints → Decide auth strategy

### Phase 2: Schema (delegate to `📐 schema-architect`)
- Generate prisma/schema.prisma
- Add indexes on FK + unique fields
- Create migration: `npx prisma migrate dev --name init`
- Update `.be/memory/schema.md`

### Phase 3: API + Auth (PARALLEL in Claude Code)
**🔌 api-builder:**
- Generate modules + controllers + services + DTOs
- OpenAPI annotations
- class-validator on all inputs

**🛡️ auth-guard:**
- JWT strategy (access + refresh)
- /auth/register, /auth/login, /auth/refresh, /auth/logout
- Global JwtAuthGuard + RolesGuard
- Rate limit on /auth/*

### Phase 4: Observability (delegate to `📊 observability`)
- Configure Pino with redact list
- /metrics endpoint (Prometheus)
- /health/live + /health/ready
- Request-id middleware

### Phase 5: Tests (delegate to `🧪 test-runner`)
- Generate unit tests for services
- Generate e2e tests with Testcontainers
- Auto-fix loop (max 5 attempts)
- Coverage report

### Phase 6: Final Verify
- `npm run build` (zero errors)
- `npm test` (all green)
- Show preview URL: http://localhost:3000/docs

## 🚀 During Execution — Show Progress

```markdown
## 🤖 Bootstrap Progress

| Phase | Agent | Task | Status |
|-------|-------|------|--------|
| 1 | 📋 plan | Analysis | ✅ Done |
| 2 | 📐 schema | 3 entities, 1 migration | ✅ Done |
| 3a | 🔌 api | 12 endpoints | 🔄 Working (8/12)... |
| 3b | 🛡️ auth | JWT setup | 🔄 Working (parallel)... |
| 4 | 📊 observe | Pending | ⏳ Waiting |
| 5 | 🧪 test | Pending | ⏳ Waiting |
```

## 📝 Final Response Format (3-section MANDATORY)

```markdown
## 🤖 Agent Execution Summary

| Phase | Agent | Result |
|-------|-------|--------|
| 1 | 📋 plan | Domain identified, 5 entities detected |
| 2 | 📐 schema | 5 tables, 8 indexes, 1 migration |
| 3 | 🔌 api | 18 endpoints, 12 DTOs, OpenAPI complete |
| 4 | 🛡️ auth | JWT + Refresh + RBAC + Rate limit |
| 5 | 📊 observe | Pino + /metrics + /health |
| 6 | 🧪 test | 42 tests passing, 87% coverage |

**Total agents:** 6
**Total files created:** 35+
**Auto-fixes applied:** 3

---

## ✅ What I Did

[Detailed file list, migrations, dependencies installed]

## 🎁 What You Get

- ✅ Production-ready API at http://localhost:3000
- ✅ OpenAPI docs at /docs
- ✅ JWT auth (access + refresh)
- ✅ All endpoints tested + documented
- ✅ Health checks at /health/live + /health/ready
- ✅ Prometheus metrics at /metrics
- ✅ Request-id propagation
- ✅ RFC 7807 error responses
- ✅ Rate limit on auth
- ✅ Idempotency on POST/PUT
- ✅ Cursor pagination

## 👉 What You Need To Do

### Step 1: Set environment
\`\`\`bash
# Generate secrets
echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
echo "JWT_REFRESH_SECRET=$(openssl rand -base64 32)" >> .env

# Set DB URL
echo "DATABASE_URL=postgresql://user:pass@localhost:5432/myapp" >> .env
echo "REDIS_URL=redis://localhost:6379" >> .env
\`\`\`

### Step 2: Start dependencies
\`\`\`bash
docker-compose up -d  # PostgreSQL + Redis
npx prisma migrate dev
\`\`\`

### Step 3: Run
\`\`\`bash
npm install
npm run start:dev
\`\`\`

### Step 4: Verify
- http://localhost:3000/docs (Swagger UI)
- http://localhost:3000/health
- http://localhost:3000/metrics

**Suggested next:**
- `/be-deploy` Setup Docker + CI/CD pipeline
- `/be-plan add billing module` Extend with new feature
- `/be-test load test` Run k6 load tests

## 💾 Memory Updated ✅
- ✅ summary.md (project info)
- ✅ schema.md (5 entities documented)
- ✅ api-registry.md (18 endpoints)
- ✅ contracts.md (OpenAPI snapshot)
- ✅ architecture.md (service structure)
- ✅ decisions.md (5 ADRs)
- ✅ changelog.md (bootstrap session)
- ✅ agents-log.md (6 agents activity)
```

## ⚠️ Critical Rules

1. **Always show plan first** — even if confidence is HIGH
2. **Schema FIRST** in every bootstrap
3. **Test LAST** to verify everything
4. **Quality gate** before each handoff
5. **Memory updated** at end
6. **Run `npm run build` + `npm test`** before declaring done

## ❌ NEVER

- Skip plan display
- Skip skills loading checkpoint
- Skip memory protocol
- Deliver with build errors
- Forget to set up health checks
- Skip rate limit on /auth

## ✅ ALWAYS

- Read 9 memory files first
- Show execution plan
- Wait for "Go" if user wants confirmation
- Use 3-section response
- Provide curl examples
- List "What You Need To Do" with env setup
- Save memory after work

---

*becraft Bootstrap — Full production backend in one command*
