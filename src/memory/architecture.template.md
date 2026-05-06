# 🏗️ Service Architecture

> Service structure + dependency graph for AI context loading
> **Update:** After any structural changes (new modules, services, infrastructure)

---

## 📁 Entry Points

| Type | Path | Purpose |
|------|------|---------|
| Main | `src/main.ts` | NestJS bootstrap |
| App | `src/app.module.ts` | Root module + DI setup |
| Health | `src/health/health.controller.ts` | Health checks (`/health`) |
| Docs | `src/main.ts` (Swagger) | OpenAPI docs (`/docs`) |

---

## 🗂️ Modules

| Module | Path | Purpose | Dependencies |
|--------|------|---------|--------------|
| AppModule | `src/app.module.ts` | Root | All feature modules |
| ConfigModule | `src/config/` | Env config | - |
| HealthModule | `src/health/` | Health checks | - |

### Feature Modules
| Module | Path | Resource | Status |
|--------|------|----------|--------|
| - | - | - | - |

---

## 🔄 Request Lifecycle

```
Request
  ↓
Middleware (logging, request-id)
  ↓
Guards (auth, RBAC, rate-limit)
  ↓
Interceptors (caching, transform)
  ↓
Pipes (validation via class-validator/Zod)
  ↓
Controller
  ↓
Service (business logic)
  ↓
Repository (Prisma queries)
  ↓
Database (PostgreSQL)
```

---

## 🔌 External Services

| Service | Purpose | Config Location | Health Check |
|---------|---------|-----------------|--------------|
| PostgreSQL | Primary DB | `prisma/schema.prisma` | `/health/db` |
| Redis | Cache + Queue backend | `src/config/redis.config.ts` | `/health/redis` |

---

## 📨 Background Jobs (BullMQ)

| Queue | Worker | Purpose | Concurrency |
|-------|--------|---------|-------------|
| - | - | - | - |

---

## 🔐 Auth Architecture

- Strategy: JWT (Passport)
- Refresh tokens: TBD
- OAuth providers: TBD
- Session storage: Redis (if used)

---

## 📝 Notes

- Using becraft v{{VERSION}}
- Architecture tracking enabled
- All modules follow NestJS feature module pattern

---
*Last updated: {{TIMESTAMP}}*
