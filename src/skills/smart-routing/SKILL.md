---
name: smart-routing
description: >
  Intent classification for /be smart command. Backend-specific keywords,
  confidence scoring, IDE detection, agent selection. CORE skill.
related_skills:
  - memory-system
  - response-format
  - contract-first
---

# Smart Routing Skill

## 📊 Confidence × Size Routing Matrix (BCFT-010)

After intent classification, score the request along **2 axes**:

### Score Confidence (0-100%)
| Score | Meaning |
|-------|---------|
| ≥90% | Crystal clear request, all signals align |
| 70-89% | Mostly clear, minor ambiguity |
| 50-69% | Significant ambiguity, multiple valid interpretations |
| <50% | Unclear — request more info |

### Estimate Task Size (file count)
| Size | Examples |
|------|----------|
| <5 files | "fix typo", "add field to DTO", single endpoint |
| 5-15 files | New feature module (CRUD), auth setup |
| >15 files | Bootstrap, multi-resource bootstrap, refactor |

### Routing Matrix

| Confidence | Size | Route |
|-----------|------|-------|
| **≥90%** | <5 files | Direct to specialist (no plan) |
| **≥90%** | 5-15 files | plan-orchestrator (light plan) → specialist |
| **≥90%** | >15 files | plan-orchestrator (full multi-phase plan) |
| **70-89%** | Any | plan-orchestrator → specialist |
| **<70%** | Any | Ask clarifying question |

### Special Rules

- **Bootstrap tasks** (greenfield, no `package.json`) → ALWAYS go through `plan-orchestrator` first, then `bootstrap-agent`
- **Schema changes** affecting existing data → ALWAYS plan first (destructive risk)
- **Auth changes** → ALWAYS plan first (security-sensitive)
- **Continue tasks** ("/be ทำต่อ") → resume from `.be/memory/active.md` directly

### Examples

```
"/be fix typo in users.controller.ts line 23"
  → Confidence 95%, Size 1 file
  → DIRECT to api-builder/fix mode

"/be add /products GET endpoint"
  → Confidence 92%, Size 4 files (controller + service + DTOs)
  → DIRECT to api-builder

"/be build user management"
  → Confidence 75%, Size 10-15 files
  → plan-orchestrator (light plan)

"/be bootstrap inventory system"
  → Confidence 80%, Size 20+ files
  → plan-orchestrator (full plan) → bootstrap-agent → ...

"/be improve performance"
  → Confidence 40%
  → ASK USER (which endpoint? which metric?)
```

---

## ✅ Pre-flight Checklist (MANDATORY — BCFT-005)

Run BEFORE any agent handoff. If ANY item fails, **ASK USER** instead of delegating.

### Checklist

- [ ] **Stack decision is explicit** (Prisma / Supabase JS / TypeORM / Drizzle / ...)
  - Check user request, `.env`, `decisions.md`, `package.json`
- [ ] **Prerequisites available** (env vars, credentials, schema info)
  - DATABASE_URL or SUPABASE_URL set if backend operations needed
  - JWT_SECRET set if auth operations needed
- [ ] **Project state determined** (greenfield / existing / partial)
  - Greenfield → bootstrap-mode workflow
  - Existing → incremental feature mode
- [ ] **Scope boundaries clear**
  - File count estimate (rough)
  - Time estimate (rough)
  - Specialist agent matches task type
- [ ] **No conflicting recent decisions** in `.be/memory/decisions.md`

### If Checklist Passes

1. Show workflow plan to user (already mandated by `/be`)
2. Delegate to specialist agent

### If Checklist Fails

1. Print which items failed:
   ```
   ⚠️ Pre-flight checklist failed:
   - Stack decision: not explicit (no .env, no recent decisions)
   - Project state: ambiguous (CLAUDE.md exists but no src/)
   ```
2. Ask user **minimum** clarifying questions
3. Re-run checklist after answers received

### Anti-pattern

```
❌ User: /be build users API
   AI: [silently delegates to api-builder, picks Prisma by default]
   AI: [api-builder fails because no DATABASE_URL]
   → wasted effort

✅ User: /be build users API
   AI: ⚠️ Pre-flight check failed:
       - Stack: not explicit
       - DB: no DATABASE_URL or SUPABASE_URL set
       Which data layer? (Prisma+Postgres / Supabase JS / something else?)
       Will you provide DB credentials?
```

---


Intelligent routing engine for the `/be` smart command. Routes any natural language backend request to the right agent(s).

---

## 🧠 Routing Pipeline

```
USER REQUEST
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 0: MEMORY CHECK (always first) │
│ ├── Read 9 .be/memory/ files        │
│ └── Build context understanding     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 1: INTENT CLASSIFICATION       │
│ ├── Keyword pattern matching        │
│ ├── Context inference (memory)      │
│ └── Scope detection                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 2: CONFIDENCE SCORING          │
│ ├── HIGH (80+) → Direct execution   │
│ ├── MEDIUM (50-79) → Plan first     │
│ └── LOW (<50) → Ask clarification   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 3: IDE DETECTION               │
│ ├── Claude Code → Parallel allowed  │
│ └── Antigravity → Sequential only   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 4: AGENT SELECTION + EXECUTE   │
└─────────────────────────────────────┘
```

---

## 📊 Intent Classification Matrix

### Backend-Specific Patterns

| Category | Keywords (EN) | Keywords (TH) | Primary Agent | Confidence |
|----------|---------------|---------------|---------------|------------|
| **Schema** | schema, table, migration, column, index, prisma | schema, ตาราง, migrate, คอลัมน์ | 📐 schema-architect | HIGH |
| **API/CRUD** | endpoint, route, controller, CRUD, REST, API | endpoint, สร้าง API, ทำ route | 🔌 api-builder | HIGH |
| **Auth** | login, register, JWT, OAuth, RBAC, role, permission | login, สมัคร, สิทธิ์ | 🛡️ auth-guard | HIGH |
| **Test** | test, jest, spec, integration, unit, coverage | test, ทดสอบ, เช็ค | 🧪 test-runner | HIGH |
| **Fix Bug** | bug, error, failing, broken, fix, debug | bug, error, พัง, แก้ | 🧪 test-runner (fix mode) | HIGH |
| **Observability** | log, metrics, tracing, monitoring, prometheus, sentry | log, monitor, ติดตาม | 📊 observability | HIGH |
| **Performance** | slow, optimize, N+1, cache, index | ช้า, optimize, cache | 🔌 api-builder + 📐 schema | MEDIUM |
| **Deploy** | deploy, ship, production, docker, CI/CD | deploy, ขึ้น production | 📋 plan + future deploy | MEDIUM |
| **New Project** | new project, create system, build backend, API for | project ใหม่, สร้างระบบ | 📋 plan-orchestrator | HIGH |
| **Plan** | plan, analyze, design, architecture | วางแผน, วิเคราะห์ | 📋 plan-orchestrator | HIGH |
| **Continue** | continue, resume, go on | ทำต่อ, ต่อ | Memory → Last Agent | MEDIUM |
| **Vague** | help, fix it, make better | ช่วยที, แก้ที | (ask clarification) | LOW |

---

## 🎯 Confidence Scoring

```typescript
interface ConfidenceFactors {
  keywordMatch: number;      // 0-40
  contextClarity: number;    // 0-30 (specific resource named)
  memorySupport: number;     // 0-20 (matches active task)
  scopeDefinition: number;   // 0-10 (single clear task)
}

function calculateConfidence(request: string, memory: Memory): number {
  let score = 0;

  // Keyword matching (0-40)
  // Strong match = 40, Partial = 20, None = 0
  score += keywordMatchScore(request);

  // Context clarity (0-30)
  // Specific resource (e.g., "users table") = 30
  // General area (e.g., "an API") = 15
  // No specifics = 0
  score += contextClarityScore(request);

  // Memory support (0-20)
  // Matches active task = 20
  // Relates to project = 10
  // No memory context = 0
  score += memorySupportScore(request, memory);

  // Scope definition (0-10)
  // Single clear task = 10
  // Multiple related tasks = 5
  // Unclear scope = 0
  score += scopeDefinitionScore(request);

  return score; // 0-100
}

const HIGH_CONFIDENCE = 80;     // Execute directly
const MEDIUM_CONFIDENCE = 50;   // Route to Plan first
// Below 50 = Ask clarification
```

---

## 🖥️ IDE Detection

### Detection Method

| Marker | IDE |
|--------|-----|
| `CLAUDE.md` exists + `.claude/agents/` populated | Claude Code |
| `.agent/workflows/` populated + `.agent/AGENT.md` | Antigravity |

### Execution Strategy

| IDE | Multi-Agent | Why |
|-----|-------------|-----|
| **Claude Code** | Parallel (native Task tool) | True sub-agent delegation |
| **Antigravity** | Sequential (single AI) | No native delegation |
| **Unknown** | Sequential (safe default) | - |

---

## 🔄 Routing Decision Tree

```
Request arrives
    │
    ▼
┌──────────────────────────┐
│ 1. Load Memory (9 files) │
└──────────────────────────┘
    │
    ▼
┌──────────────────────────┐
│ 2. Is "continue/ทำต่อ"?  │
├── YES → Resume from active.md
└── NO → Continue analysis
    │
    ▼
┌──────────────────────────┐
│ 3. Calculate Confidence  │
└──────────────────────────┘
    │
    ├── ≥80 (HIGH)
    │   └─→ Select agent based on intent
    │       └─→ Show workflow plan
    │           └─→ Execute directly
    │
    ├── 50-79 (MEDIUM)
    │   └─→ Route to plan-orchestrator
    │       └─→ Plan → confirm → execute
    │
    └── <50 (LOW)
        └─→ Ask clarifying question
            └─→ Wait for user response
```

---

## 📋 Clarification Patterns

### When to Ask

| Situation | Example | Action |
|-----------|---------|--------|
| No verb | "the users API" | "What about the users API? Create new endpoints?" |
| No target | "make it work" | "Which endpoint/feature is broken?" |
| Multiple meanings | "improve it" | "Performance, security, or design?" |
| Missing context + no memory | "fix it" | "What's broken? Describe the error or behavior." |

### When NOT to Ask

| Situation | Example | Action |
|-----------|---------|--------|
| Clear intent | "create users CRUD" | Execute directly |
| Memory provides context | "continue" + active task | Resume from memory |
| Reasonable default | "add an endpoint" | Add to current resource context |

---

## 🎨 Skills + Agent Loading by Intent

| Detected Intent | Skills to Load | Agent |
|-----------------|----------------|-------|
| Schema work | schema-design, contract-first | schema-architect |
| API work | api-design, contract-first, error-handling | api-builder |
| Auth work | auth-patterns | auth-guard |
| Testing | testing-pyramid, error-handling | test-runner |
| Fix bugs | error-handling, testing-pyramid | test-runner |
| Observability | observability | observability |
| New project | contract-first, schema-design, api-design, auth-patterns | plan-orchestrator |
| Planning | contract-first | plan-orchestrator |

**Always loaded** (regardless of intent):
- memory-system
- response-format
- smart-routing

---

## 📌 Examples

### Example 1: HIGH Confidence → Direct
```
Request: "/be สร้าง endpoint POST /products"

Analysis:
- Keyword "สร้าง" + "endpoint" = Create API (40)
- "POST /products" = specific (30)
- Memory: Project has products schema (15)
- Single task (10)
Total: 95 = HIGH

Route: 🔌 api-builder (direct execution)
```

### Example 2: MEDIUM Confidence → Plan First
```
Request: "/be build inventory management system"

Analysis:
- "build" = Create (40)
- "inventory management" = general concept (10)
- Memory: Empty project (0)
- Multiple features (0)
Total: 50 = MEDIUM

Route: 📋 plan-orchestrator → show plan → execute
```

### Example 3: LOW Confidence → Ask
```
Request: "/be fix it"

Analysis:
- "fix" (20)
- "it" = unclear (0)
- No recent error in memory (0)
- Unknown scope (0)
Total: 20 = LOW

Action: "What would you like me to fix? Describe the error or behavior."
```

### Example 4: Continue from Memory
```
Request: "/be ทำต่อ"

Memory: active.md has "In Progress: Add /users PATCH endpoint"

Action: Resume task from memory, route to api-builder.
```

---

## 🔄 Multi-Agent Orchestration Patterns

### Pattern 1: Single Task
```
[fix-mode test-runner]
```

### Pattern 2: Schema + API
```
[schema-architect] → [api-builder]
```

### Pattern 3: Full Resource (parallel-aware)
```
Claude Code:
[schema] → [api + auth + observe parallel] → [test]

Antigravity:
[schema] → [api] → [auth] → [observe] → [test]
```

### Pattern 4: New Project
```
[plan] → [schema] → [api+auth+observe] → [test]
```

---

## ⚠️ Critical Rules

1. **Memory ALWAYS first** — never route without context
2. **Confidence drives action** — trust the score
3. **Plan agent is your friend** — when in doubt, route to plan
4. **IDE awareness matters** — parallel only in Claude Code
5. **Show workflow plan** — always before execution
6. **`response-format` always loaded** — every response needs 3 sections

---

*Smart Routing Skill v1.0 — Backend intent classification*
