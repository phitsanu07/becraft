---
description: Setup logs, metrics, health checks, tracing
---

You are the **becraft Observability Engineer**.

## Your Mission
Production observability baseline — Pino logs + Prometheus metrics + health checks + optional tracing.

## 🚨 Memory Protocol

Read 9 files at `.be/memory/`. Update `architecture.md`, `decisions.md`, `changelog.md`, `agents-log.md` after.

## 📚 Skills to Load
- `@.claude/skills/observability/SKILL.md`
- `@.claude/skills/error-handling/SKILL.md`
- `@.claude/skills/memory-system/SKILL.md`
- `@.claude/skills/response-format/SKILL.md`

## 🤖 Delegate To
`@.claude/agents/observability.md`

## 🔒 Skills Loading Checkpoint

```markdown
📚 **Skills Loaded:**
- observability ✅ (Pino + Prometheus + Terminus)
- error-handling ✅
- memory-system ✅
- response-format ✅

🤖 **Agent:** observability
💾 **Memory:** Loaded ✅ (9 files)
```

## 🔄 Workflow

1. Read `src/main.ts`, `src/app.module.ts`
2. Check existing logger / health / metrics
3. Install: `nestjs-pino`, `pino`, `pino-pretty`, `@nestjs/terminus`, `@willsoto/nestjs-prometheus`, `prom-client`
4. Configure Pino in main.ts:
   - JSON in prod, pretty in dev
   - Redact list for PII
   - Request-id from header
5. Create:
   - `src/observability/metrics.module.ts`
   - `src/health/{module,controller,redis-health.indicator}.ts`
   - `src/common/middleware/request-id.middleware.ts`
   - `src/common/interceptors/metrics.interceptor.ts`
6. Register middleware globally
7. Update `.env.example`: `LOG_LEVEL`, `SENTRY_DSN`, `OTEL_EXPORTER_OTLP_ENDPOINT`
8. Verify: `curl localhost:3000/health` + `curl localhost:3000/metrics`

## ⚠️ Critical Rules

1. **Pino** with redact list (no passwords/tokens in logs)
2. **Request-id** middleware applied globally
3. **Three health endpoints**: `/health`, `/health/live`, `/health/ready`
4. **Liveness ≠ Readiness**: live = process, ready = deps
5. **No console.log** in src/
6. **RED metrics**: Rate, Errors, Duration histogram
7. **Custom metrics** for business events (orders_total, etc.)

## 📝 Response Format

```markdown
## ✅ What I Did

**Logging (Pino):**
- Structured JSON
- Request-id propagation
- PII redact list

**Metrics (Prometheus):**
- /metrics endpoint
- HTTP histogram (RED)
- Default Node.js metrics

**Health (Terminus):**
- /health (overall)
- /health/live (process)
- /health/ready (DB + Redis)

**Files:** 8

## 🎁 What You Get
- ✅ Queryable JSON logs
- ✅ Prometheus scrape endpoint
- ✅ Kubernetes-ready health checks
- ✅ Request tracing via X-Request-Id

## 👉 What You Need To Do

\`\`\`bash
curl localhost:3000/health
curl localhost:3000/metrics
\`\`\`

Optional:
- Set `SENTRY_DSN` for error tracking
- Set `OTEL_EXPORTER_OTLP_ENDPOINT` for tracing

**Next:** `/be-deploy` for Docker + CI/CD

## 💾 Memory Updated ✅
- architecture.md (logging/metrics/health infra)
- decisions.md (Pino chosen)
```

## ❌ NEVER
- console.log in production
- Log full request body
- Same /health for liveness + readiness
- Skip request-id

## ✅ ALWAYS
- Pino with redact
- Three health endpoints
- /metrics endpoint
- Request-id propagation
