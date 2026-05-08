---
name: supabase-query-patterns
description: >
  PostgREST/Supabase JS query patterns. Wildcard rules, or()/and() syntax,
  value escaping, error code mapping, RLS-aware querying. Load BEFORE
  generating any Supabase JS query — prevents 500s from malformed filters.
related_skills:
  - api-design
  - error-handling
  - schema-design
---

# Supabase Query Patterns Skill

Production-grade PostgREST/Supabase JS query rules for becraft's
`nestjs-supabase` template. **Load this skill whenever generating code that
calls `supabase.from(...).select/insert/update/delete/or/and/filter`.**

---

## ⚠️ Why This Skill Exists

LLMs trained on SQL frequently emit `%` as a wildcard in PostgREST filters.
PostgREST uses `*` instead — the resulting query reaches Supabase, returns
500, and the user has no idea why. This skill encodes the rules so generated
code is correct on the first try.

---

## 🔥 Top Pitfalls (Memorize)

| Pitfall | Wrong | Correct |
|---------|-------|---------|
| Wildcard char | `name.ilike.%foo%` | `name.ilike.*foo*` |
| Unquoted special char | `name.eq.Hello, World` | `name.eq."Hello, World"` |
| User input not escaped | `or(\`name.ilike.*${q}*\`)` | escape `q` first |
| `or()` joiner | `name.eq.A AND price.gt.10` | `or(name.eq.A,price.gt.10)` |
| Single result missing | `.single()` returns 406 if 0 rows | use `.maybeSingle()` |
| Service-role on user request | `SUPABASE_ADMIN_CLIENT` for all reads | use anon client + RLS |

---

## 📐 PostgREST Filter Operators

```
eq    =        gt    >        like   LIKE  (case-sensitive, * wildcard)
neq   !=       gte   >=       ilike  ILIKE (case-insensitive, * wildcard)
                lt    <        is     IS    (.is.null only)
                lte   <=       in     IN    (.in.(1,2,3))
                                cs    @>    (array contains)
                                cd    <@    (contained by)
                                ov    &&    (overlaps)
```

### Wildcard rule

```
✅ * is wildcard         → name.ilike.*john*
❌ % is LITERAL %         → searches for literal "%john%"
```

### Quoting rule

Wrap the value in `"..."` whenever it contains any of `, . : ( ) space \`:

```
✅ name.eq."Hello, World"
✅ description.ilike."*Bangkok 10110*"
✅ slug.eq."v1.2.3"
❌ name.eq.Hello, World     → comma breaks the filter list
❌ slug.eq.v1.2.3           → dot is parsed as operator separator
```

### Escape rule for user input

User-provided values can contain `"`, `\`, `,`, `(`, `)`, `*` — escape them:

```typescript
function escapePostgrestValue(v: string): string {
  return v
    .replace(/\\/g, '\\\\')   // backslash first (always)
    .replace(/"/g, '\\"')     // double-quote
    .replace(/,/g, '\\,')     // comma (filter separator)
    .replace(/\(/g, '\\(')    // paren (group separator)
    .replace(/\)/g, '\\)')
    .replace(/\*/g, '\\*');   // wildcard (escape if user shouldn't control it)
}
```

> Note: keep `*` un-escaped only when YOU build the wildcard around the value
> (e.g., `*${escaped}*`). Never let user input control `*`.

---

## 🧩 or() / and() Composition

### Format

```
or(filter1,filter2,filter3)
and(filter1,filter2)
or(filter1,and(filter2,filter3))   ← nested
```

### Multi-column search (most common case)

```typescript
const safe = escapePostgrestValue(keyword.trim());
const filter = [
  `name.ilike."*${safe}*"`,
  `description.ilike."*${safe}*"`,
  `sku.ilike."*${safe}*"`,
].join(',');

const { data, error } = await supabase
  .from('products')
  .select('id, name, description, sku')
  .or(filter);
```

### Conditional filters

```typescript
let q = supabase.from('products').select('*');

if (category) q = q.eq('category', category);
if (minPrice) q = q.gte('price', minPrice);
if (keyword) {
  const safe = escapePostgrestValue(keyword);
  q = q.or(`name.ilike."*${safe}*",description.ilike."*${safe}*"`);
}

const { data, error } = await q;
```

### Nested logic

```typescript
// (status='active' OR status='pending') AND price>=100
const { data } = await supabase
  .from('products')
  .select('*')
  .or('status.eq.active,status.eq.pending')
  .gte('price', 100);
```

---

## 🪪 Auth Context — anon vs service-role

| Client | Key | RLS | Use for |
|--------|-----|-----|---------|
| `SUPABASE_CLIENT` | anon | ✅ enforced | Normal user requests |
| `SUPABASE_ADMIN_CLIENT` | service_role | ❌ bypassed | Cron jobs, admin-only paths, migrations |

**Default to `SUPABASE_CLIENT`.** Use admin client only for explicit
backend-only operations and document why in `.be/memory/decisions.md`.

```typescript
@Injectable()
export class ProductsService {
  constructor(
    @Inject(SUPABASE_CLIENT) private readonly db: SupabaseClient,        // ✅ default
    @Inject(SUPABASE_ADMIN_CLIENT) private readonly admin: SupabaseClient | null,
  ) {}

  // User-facing — RLS enforced
  search(keyword: string) {
    return this.db.from('products').select('*');
  }

  // Cron job — bypass RLS intentionally
  async refreshDenormalized() {
    if (!this.admin) throw new Error('admin client required');
    return this.admin.from('product_stats').upsert(...);
  }
}
```

---

## ❌ Error Code Mapping

PostgREST and Postgres errors. Map to HTTP status in your exception filter:

| Code | Source | Meaning | HTTP |
|------|--------|---------|------|
| `PGRST100` | PostgREST | Filter syntax error | 400 |
| `PGRST116` | PostgREST | `.single()` got 0 or >1 rows | 404 / 409 |
| `PGRST301` | PostgREST | JWT expired | 401 |
| `23505` | Postgres | Unique violation | 409 |
| `23503` | Postgres | Foreign key violation | 400 |
| `23502` | Postgres | NOT NULL violation | 400 |
| `23514` | Postgres | CHECK constraint violation | 400 |
| `42501` | Postgres | RLS / permission denied | 403 |
| `42P01` | Postgres | Table does not exist | 500 |

```typescript
function mapSupabaseError(e: { code?: string; message?: string }): HttpException {
  switch (e.code) {
    case 'PGRST100':
      return new BadRequestException({ title: 'Invalid query syntax', detail: e.message });
    case 'PGRST116':
      return new NotFoundException('Resource not found');
    case '23505':
      return new ConflictException('Duplicate entry');
    case '23503':
    case '23502':
    case '23514':
      return new BadRequestException(e.message);
    case '42501':
      return new ForbiddenException('Permission denied (RLS)');
    default:
      return new InternalServerErrorException({
        title: 'Database error',
        code: e.code,
      });
  }
}
```

---

## 📦 Pagination — `.range()` not LIMIT/OFFSET

```typescript
const PAGE_SIZE = 20;
const from = (page - 1) * PAGE_SIZE;
const to = from + PAGE_SIZE - 1;

const { data, count, error } = await supabase
  .from('products')
  .select('*', { count: 'exact' })   // ← need count for total
  .range(from, to)
  .order('created_at', { ascending: false });

return {
  data,
  meta: { page, limit: PAGE_SIZE, total: count ?? 0 },
};
```

---

## 🎯 Single-Row Reads — `.maybeSingle()` over `.single()`

```
.single()       throws PGRST116 if 0 rows OR >1 rows
.maybeSingle()  returns null if 0 rows; still throws if >1
```

```typescript
// ✅ Safe for "find by id"
const { data, error } = await supabase
  .from('products')
  .select('*')
  .eq('id', id)
  .maybeSingle();

if (error) throw mapSupabaseError(error);
if (!data) throw new NotFoundException('Product not found');
return data;
```

---

## 🔢 Type Safety

Generate types from the live Supabase schema:

```bash
npx supabase gen types typescript --project-id "$PROJECT_ID" > src/types/database.ts
```

Then:

```typescript
import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database';

const supabase = createClient<Database>(URL, KEY);

// Table names + column names + return types are now type-checked.
// Filter strings inside .or() are still plain strings — escape rules still apply.
```

---

## ✅ Safe-Pattern Checklist (apply to every generated query)

Before emitting a Supabase query, verify:

- [ ] User input passed to filters is escaped via `escapePostgrestValue`
- [ ] Wildcard char is `*` (never `%`)
- [ ] Values containing `,` `.` `:` `(` `)` space are wrapped in `"..."`
- [ ] `.single()` only when caller guarantees exactly one row, else `.maybeSingle()`
- [ ] Default client is anon (`SUPABASE_CLIENT`); admin used only when justified
- [ ] Errors are mapped via `mapSupabaseError` (or equivalent filter)
- [ ] Pagination uses `.range()` + `count: 'exact'`
- [ ] Tests cover: valid query, malformed input, RLS-blocked path, 0-row path

---

## 🔗 Companion Snippet

The helpers above ship in `.be/snippets/supabase-search.helper.ts`. Import
from there instead of re-implementing:

```typescript
import {
  escapePostgrestValue,
  searchAcrossColumns,
  mapSupabaseError,
} from '../../snippets/supabase-search.helper';
```

---

## 🚫 Anti-Patterns to Reject in Code Review

```typescript
// ❌ SQL-style wildcard
.or(`name.ilike.%${q}%`)

// ❌ Unescaped user input
.eq('email', userEmail)              // user-controlled comma → broken

// ❌ Service-role for user-facing reads
@Inject(SUPABASE_ADMIN_CLIENT) private db   // bypasses RLS by accident

// ❌ Throwing PostgrestError directly
if (error) throw error;               // leaks internals as 500

// ❌ .single() for "find by id"
.single()                             // 0 rows → noisy 406

// ❌ Hard-coded LIMIT
.limit(20).then(r => r.data.slice(0, 20))   // can't paginate
```

---

*Supabase Query Patterns Skill v1.0 — load whenever Supabase JS code is generated*
