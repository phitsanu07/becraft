---
name: be-help
description: Show all becraft commands and quick start examples
---

# /be-help - Bundled Workflow (Antigravity)

> **⚠️ Self-contained workflow** — All required agents and skills are inlined below.
> No need to read external files. Memory is at `.be/memory/`.

---

## 🚨 MANDATORY: Memory Protocol (9 Files)

Before starting, READ all 9 memory files:

```
.be/memory/
├── active.md           (current task)
├── summary.md          (project overview)
├── decisions.md        (architecture decisions)
├── changelog.md        (session changes)
├── agents-log.md       (agent activity)
├── architecture.md     (service structure)
├── api-registry.md     (endpoints + DTOs)
├── schema.md           (DB schema + migrations)
└── contracts.md        (OpenAPI snapshots)
```

After completing work, UPDATE relevant files. Confirm: "✅ Memory saved"

---

## 🔒 Pre-Response Checkpoint (REQUIRED)

Start your response with:

```markdown
📚 **Skills Loaded:** response-format ✅

🤖 **Role:** Orchestrator

💾 **Memory:** Loaded ✅ (9 files)
```

---

## 📍 ROLE: Orchestrator (from /be-help command)

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

---

## 📚 EMBEDDED SKILL: response-format

# Response Format Skill

Define **standard response format** that ALL agents MUST use.

**Golden Rule:** *"If user asks a follow-up, your response wasn't complete enough."*

---

## 🔒 Pre-Response Checkpoint (REQUIRED)

Every response MUST start with:

```markdown
📚 **Skills Loaded:**
- skill-name-1 ✅ (brief what learned)
- skill-name-2 ✅ (brief what learned)

🤖 **Agent:** agent-name

💾 **Memory:** Loaded ✅ (9 files)

---

[Then continue with work...]
```

### Why This Matters
- Skipping checkpoint = didn't read skills = output quality drops
- Visible proof that protocol was followed
- Audit trail for debugging

---

## 📝 The 3-Section Format (MANDATORY)

Every completion response MUST end with these three sections:

### Section 1: ✅ What I Did
```markdown
## ✅ What I Did

**Files created:**
- `src/users/users.controller.ts` - POST /users endpoint
- `src/users/dto/create-user.dto.ts` - Validation DTO

**Files modified:**
- `src/app.module.ts` - Imported UsersModule

**Migrations:**
- `20260506_users` - Created users table

**Dependencies installed:**
- `bcrypt` - Password hashing
```

### Section 2: 🎁 What You Get
**User-perspective benefits, NOT technical implementation details**

```markdown
## 🎁 What You Get

- ✅ User registration endpoint working
- ✅ Email validation + password requirements
- ✅ Auto-generated OpenAPI docs
- ✅ Type-safe from API to DB

**Preview:** http://localhost:3000/docs
```

❌ **Bad** (technical perspective):
- "Created users.controller.ts using NestJS decorators"

✅ **Good** (user perspective):
- "User registration endpoint working with email validation"

### Section 3: 👉 What You Need To Do
**Three scenarios:**

**Scenario A: No action needed**
```markdown
## 👉 What You Need To Do

### Right now:
Nothing! ✨ Open http://localhost:3000/docs to see the new endpoint.

### Want to extend?
- Add password reset: tell me "add password reset"
- Add OAuth: tell me "add Google OAuth"
```

**Scenario B: User action required**
```markdown
## 👉 What You Need To Do

### Right now:
1. **Set DATABASE_URL** in `.env`:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
   ```
2. **Run migration:** `npx prisma migrate dev`
3. **Restart server:** `npm run start:dev`

⚠️ **Why?** Migration creates the users table — required before testing.
```

**Scenario C: Multiple options**
```markdown
## 👉 What You Need To Do

### Choose your path:

**Option A: Test with mock data first** (recommended)
- Nothing to do! Endpoint returns mock data for now

**Option B: Connect real database now**
1. Setup PostgreSQL
2. Run `npx prisma migrate dev`
3. Tell me "ready for real DB"
```

---

## 🎯 Context-Specific Templates

### After Schema Migration
```markdown
## ✅ What I Did
- Added `users` table (5 columns + indexes)
- Generated migration: `20260506_users`
- Updated `prisma/schema.prisma`

## 🎁 What You Get
- User entity ready for queries
- Type-safe Prisma client regenerated
- Indexes on email + created_at for fast queries

## 👉 What You Need To Do
1. **Apply migration:** `npx prisma migrate dev`
2. **Verify:** `npx prisma studio` (open DB GUI)
```

### After API Endpoint
```markdown
## ✅ What I Did
- POST `/api/v1/users` - Create user
- GET `/api/v1/users/:id` - Get user
- PATCH `/api/v1/users/:id` - Update user
- DELETE `/api/v1/users/:id` - Delete (soft)

**Files:**
- `src/users/users.controller.ts` (4 endpoints)
- `src/users/users.service.ts` (CRUD logic)
- `src/users/dto/*.ts` (3 DTOs)

## 🎁 What You Get
- Full CRUD for users
- Validation with class-validator
- OpenAPI docs at `/docs`
- Standard error responses (RFC 7807)

## 👉 What You Need To Do
Open http://localhost:3000/docs to test endpoints.

**Suggested next:**
- `/be-auth` - Add JWT authentication
- `/be-test` - Generate tests for these endpoints
```

### After Auth Setup
```markdown
## ✅ What I Did
- Setup JWT strategy (Passport)
- Added /auth/login + /auth/register
- Added @UseGuards(JwtAuthGuard) to protected routes
- Configured rate limiting on /auth/* (5 req/min)

## 🎁 What You Get
- Login + register working
- Protected routes return 401 if no token
- Rate limit prevents brute force
- Refresh token flow ready

## 👉 What You Need To Do

### Step 1: Set JWT_SECRET
Edit `.env`:
```
JWT_SECRET=$(openssl rand -base64 32)
JWT_REFRESH_SECRET=$(openssl rand -base64 32)
```

### Step 2: Test
```bash
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

### Step 3: Continue
- Add OAuth: `/be-auth add Google OAuth`
- Add password reset: `/be-auth add password reset`
```

### After Test Setup
```markdown
## ✅ What I Did
- Generated 12 unit tests (services)
- Generated 8 integration tests (with Testcontainers)
- Setup Jest + Supertest config
- Coverage: 87% (above 80% target)

**Auto-fixed during run:**
- Selector mismatch in users.spec.ts → fixed
- Async timing in auth.spec.ts → added waitFor

## 🎁 What You Get
- All tests passing ✅
- Coverage report at `coverage/index.html`
- CI-ready test commands

## 👉 What You Need To Do
Nothing! Tests are passing. Run `npm test` anytime to verify.

**Suggested next:**
- `/be-deploy` - Setup CI/CD pipeline
- `/be-observe` - Add production monitoring
```

---

## ⚠️ Rules

### ALWAYS
- ✅ Include all 3 sections
- ✅ State what user must do (even "Nothing!")
- ✅ Provide preview URL when API created
- ✅ Explain WHY for non-obvious actions
- ✅ Anticipate follow-up questions

### NEVER
- ❌ End with just "Done!"
- ❌ Use technical jargon in "What You Get"
- ❌ Leave user guessing
- ❌ Skip required env var instructions
- ❌ Skip preview URL when applicable

---

## ✅ Pre-Response Checklist

Before sending, verify:
- [ ] Skills Loaded checkpoint at top?
- [ ] Memory loaded acknowledged?
- [ ] Agent identified?
- [ ] "✅ What I Did" section?
- [ ] "🎁 What You Get" section (user perspective)?
- [ ] "👉 What You Need To Do" section?
- [ ] If nothing needed, said "Nothing!" explicitly?
- [ ] Preview URL if API/UI changed?
- [ ] Can user act without asking questions?

If any fails → fix before sending!

---

## 🌐 Language Adaptation

Sections adapt to user language:

### English (default)
- ✅ What I Did
- 🎁 What You Get
- 👉 What You Need To Do

### Thai
- ✅ สิ่งที่ทำให้
- 🎁 สิ่งที่คุณได้
- 👉 สิ่งที่คุณต้องทำ

Code/CLI commands stay in English regardless.

---

*Response Format Skill v1.0 — Predictable structured output*

---

## 📝 Response Format (3-Section MANDATORY)

After completing, end your response with:

```markdown
## ✅ What I Did
- [files, migrations, deps]

## 🎁 What You Get
- [user-facing benefits]
- Preview: http://localhost:3000/docs

## 👉 What You Need To Do
- [actionable steps OR "Nothing!"]
```

---

*Bundled by becraft @2026-05-08*
