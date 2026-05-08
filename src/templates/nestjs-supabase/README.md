# becraft NestJS Starter — Supabase JS variant

> Production-grade backend starter using **Supabase JS Client** (no Prisma)

## 🚀 Quick Start

```bash
# 1. Install
npm install

# 2. Set environment
cp .env.example .env
echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
echo "JWT_REFRESH_SECRET=$(openssl rand -base64 32)" >> .env

# Edit .env: SUPABASE_URL + SUPABASE_ANON_KEY (from Supabase dashboard)

# 3. Start Redis (only — Supabase is cloud-hosted)
docker-compose up -d redis

# 4. Start dev server
npm run start:dev
```

Open:
- 📖 OpenAPI docs: http://localhost:3000/docs
- 🏥 Health: http://localhost:3000/health
- 📊 Liveness: http://localhost:3000/health/live
- ✅ Readiness: http://localhost:3000/health/ready (pings Supabase)

## 📦 Built-In

- ✅ **NestJS 10** with TypeScript strict mode
- ✅ **Supabase JS Client** (`@supabase/supabase-js`)
- ✅ **Pino** structured logging with PII redaction (incl. service-role keys)
- ✅ **OpenAPI** auto-generated at /docs
- ✅ **Validation** with class-validator + Zod env validation
- ✅ **Health checks** (live + ready, ready pings Supabase)
- ✅ **Rate limiting** via @nestjs/throttler
- ✅ **Helmet** security headers
- ✅ **CORS** configurable
- ✅ **API versioning** (URI-based: /api/v1/...)
- ✅ **RFC 7807** error responses
- ✅ **Request-id** propagation
- ✅ **Graceful shutdown**

## 🆚 vs nestjs-base (Prisma variant)

| Feature | nestjs-base | nestjs-supabase |
|---------|------------|-----------------|
| Data Access | Prisma 5 | @supabase/supabase-js |
| Local DB | docker-compose postgres | (none — Supabase cloud) |
| Migrations | `prisma migrate` | Supabase Studio (manual) |
| Type safety | Prisma generated types | Manual or `supabase gen types` |
| Best for | Self-hosted Postgres | Hosted Supabase + RLS |

## 🤖 Use becraft Agents

```
/be-api create CRUD for products    # api-builder uses Supabase JS
/be-auth setup JWT                  # auth-guard
/be-test for products module        # test-runner
```

## 📁 Project Structure

```
.
├── src/
│   ├── main.ts                     # App bootstrap
│   ├── app.module.ts               # Root module
│   ├── common/                     # Shared utilities
│   └── modules/
│       ├── supabase/               # SupabaseService (DI-injected)
│       │   ├── supabase.module.ts
│       │   └── supabase.service.ts
│       └── health/                 # /health endpoints (pings Supabase)
├── docker-compose.yml              # Redis only — Supabase is cloud
└── package.json
```

## 🔌 Using Supabase in Services

```typescript
@Injectable()
export class ProductsService {
  constructor(private supabase: SupabaseService) {}

  async findAll() {
    const { data, error } = await this.supabase.client
      .from('products')
      .select('*')
      .eq('is_active', true)
      .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
  }
}
```

## 📜 License

MIT
