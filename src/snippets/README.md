# becraft Snippets (BCFT-013)

Reusable code patterns referenced by agents/skills instead of being inlined.

## Why?

- **Token efficiency** — skills/agents reference snippets by name; only loaded
  when actually needed (~30% prompt token reduction).
- **Single source of truth** — fix a pattern once, everywhere updates.
- **CI-validatable** — snippets are real TypeScript files, can be type-checked.

## Available Snippets

| File | Purpose | Used By |
|------|---------|---------|
| `nestjs-bootstrap.ts` | `main.ts` skeleton with NestFactory + Swagger + global pipes | bootstrap-agent |
| `prisma-service.ts` | NestJS `PrismaService` with lifecycle hooks | bootstrap-agent (Prisma) |
| `supabase-tokens.ts` | DI token constants (leaf — no other imports) | bootstrap-agent (Supabase) |
| `supabase-service.ts` | NestJS `SupabaseService` (imports tokens) | bootstrap-agent (Supabase) |
| `supabase-module.ts` | `SupabaseModule` wiring providers + exports | bootstrap-agent (Supabase) |
| `supabase-search.helper.ts` | PostgREST escape, ilike-or builder, `mapSupabaseError` (BCFT-014) | api-builder (Supabase) |
| `pagination-helper.ts` | Cursor pagination DTO + helper | api-builder |
| `error-handler.ts` | RFC 7807 Problem Details exception filter | bootstrap-agent |
| `env-validation.ts` | Zod schema for env validation | bootstrap-agent |
| `swagger-setup.ts` | OpenAPI/Swagger boilerplate | bootstrap-agent |

## Usage in Agents/Skills

Instead of inlining code:

```markdown
❌ Old way (inlines ~50 lines of bootstrap code into prompt)

The main.ts should look like:
\```typescript
import { NestFactory } from '@nestjs/core';
// ... 50 more lines ...
\```
```

Reference the snippet:

```markdown
✅ New way (just a path reference)

Use the snippet at `.be/snippets/nestjs-bootstrap.ts` as the basis for `src/main.ts`.
Customize: replace `{{APP_NAME}}` placeholders with actual app name.
```

## Conventions

- All snippets use `{{PLACEHOLDERS}}` for runtime substitution
- Comments explain customization points
- Imports are complete (ready to copy)
- TypeScript strict-compatible
