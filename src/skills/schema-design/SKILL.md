---
name: schema-design
description: >
  PostgreSQL + Prisma schema design patterns. Type-to-SQL mapping, indexing,
  foreign keys, soft delete, migrations safety, RLS templates.
related_skills:
  - contract-first
  - api-design
---

# Schema Design Skill

Production-grade PostgreSQL schema patterns using Prisma 5.

---

## 🎯 Core Principles

1. **Types are source of truth** — TypeScript types define DB schema, not vice versa
2. **UUID over serial** — Don't expose row counts, easier to merge
3. **Always timestamps** — `createdAt`, `updatedAt`, optional `deletedAt`
4. **Index every FK** — PostgreSQL doesn't auto-index FK columns
5. **NOT NULL by default** — explicitly mark optional columns
6. **Migrations forward-only** — never edit applied migrations

---

## 📐 Standard Entity Template

### TypeScript Type → Prisma Schema

```typescript
// types/user.ts
export interface User {
  id: string;             // UUID v4
  email: string;          // unique
  passwordHash: string;   // bcrypt
  name: string;
  role: UserRole;         // enum
  emailVerifiedAt: Date | null;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null; // soft delete
}

export enum UserRole {
  USER = 'USER',
  ADMIN = 'ADMIN',
}
```

```prisma
// prisma/schema.prisma
model User {
  id              String    @id @default(uuid()) @db.Uuid
  email           String    @unique
  passwordHash    String    @map("password_hash")
  name            String
  role            UserRole  @default(USER)
  emailVerifiedAt DateTime? @map("email_verified_at")
  createdAt       DateTime  @default(now()) @map("created_at")
  updatedAt       DateTime  @updatedAt @map("updated_at")
  deletedAt       DateTime? @map("deleted_at")

  // Relations
  posts Post[]

  @@index([email])
  @@index([deletedAt])    // for "active users only" queries
  @@map("users")
}

enum UserRole {
  USER
  ADMIN
}
```

### Conventions

| Convention | Why |
|------------|-----|
| `@id @default(uuid()) @db.Uuid` | UUID v4, not serial |
| `@map("snake_case")` on every column | DB uses snake_case, code uses camelCase |
| `@@map("table_name_plural")` | Snake_case plural tables |
| `@updatedAt` | Prisma auto-updates |
| `deletedAt: DateTime?` | Soft delete (optional but recommended) |
| `@@index([fkColumn])` | All FK columns must be indexed |

---

## 🔗 Relationship Patterns

### One-to-Many

```prisma
model User {
  id    String @id @default(uuid()) @db.Uuid
  posts Post[]

  @@map("users")
}

model Post {
  id       String @id @default(uuid()) @db.Uuid
  authorId String @map("author_id") @db.Uuid
  author   User   @relation(fields: [authorId], references: [id], onDelete: Cascade)

  @@index([authorId])  // ⚠️ CRITICAL: index FK
  @@map("posts")
}
```

### Many-to-Many (with metadata)

```prisma
model Project {
  id      String         @id @default(uuid()) @db.Uuid
  members ProjectMember[]
  @@map("projects")
}

model User {
  id       String         @id @default(uuid()) @db.Uuid
  projects ProjectMember[]
  @@map("users")
}

// Junction table with extra fields
model ProjectMember {
  projectId String   @map("project_id") @db.Uuid
  userId    String   @map("user_id") @db.Uuid
  role      String   @default("member")
  joinedAt  DateTime @default(now()) @map("joined_at")

  project Project @relation(fields: [projectId], references: [id], onDelete: Cascade)
  user    User    @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@id([projectId, userId])
  @@index([userId])
  @@map("project_members")
}
```

### Self-Referential (parent/child)

```prisma
model Comment {
  id       String    @id @default(uuid()) @db.Uuid
  parentId String?   @map("parent_id") @db.Uuid
  parent   Comment?  @relation("CommentReplies", fields: [parentId], references: [id], onDelete: Cascade)
  replies  Comment[] @relation("CommentReplies")

  @@index([parentId])
  @@map("comments")
}
```

---

## 📊 Indexing Strategy

### Always Index

| Pattern | Example |
|---------|---------|
| Primary keys | `@id` (auto) |
| Foreign keys | `@@index([authorId])` |
| Unique constraints | `@unique` on email |
| Soft delete column | `@@index([deletedAt])` |
| Frequently filtered columns | `@@index([status])` |
| Sort columns | `@@index([createdAt])` |

### Composite Indexes (for query patterns)

```prisma
model Order {
  id        String @id @default(uuid()) @db.Uuid
  userId    String @map("user_id") @db.Uuid
  status    OrderStatus
  createdAt DateTime @default(now()) @map("created_at")

  // For: "Get user's recent orders by status"
  @@index([userId, status, createdAt])
  @@map("orders")
}
```

**Rule:** Composite index column order = WHERE clause order

### Partial Indexes (PostgreSQL-specific)

For `deletedAt IS NULL` filters (active records):

```sql
-- Run as raw migration after Prisma generates base
CREATE INDEX users_active_idx ON users (email) WHERE deleted_at IS NULL;
```

---

## 🗑️ Soft Delete Pattern

```typescript
// Repository pattern
async findActive(): Promise<User[]> {
  return prisma.user.findMany({
    where: { deletedAt: null },
  });
}

async softDelete(id: string): Promise<User> {
  return prisma.user.update({
    where: { id },
    data: { deletedAt: new Date() },
  });
}

async restore(id: string): Promise<User> {
  return prisma.user.update({
    where: { id },
    data: { deletedAt: null },
  });
}
```

**Always filter `deletedAt: null` in default queries** unless admin/audit context.

---

## 🚦 Migration Safety

### Additive Migrations (Safe)
- Add new column with default
- Add new table
- Add new index (use `CONCURRENTLY` in PostgreSQL)
- Add new enum value (at end only)

```prisma
// Add new column with default
model User {
  // ... existing fields
  twoFactorEnabled Boolean @default(false) @map("two_factor_enabled")
}
```

### Destructive Migrations (Require Confirmation)
- Drop column
- Drop table
- Rename column (= drop + add)
- Change column type narrowing
- Add NOT NULL without default

**Two-step process:**
1. **Phase 1:** Make column nullable / add new column
2. **Phase 2:** Migrate data + remove old (after deploy verified)

### Never Edit Applied Migrations
```
❌ Edit prisma/migrations/20260506_init/migration.sql
✅ Create new migration: npx prisma migrate dev --name fix_xxx
```

---

## 🔒 Row-Level Security (RLS)

PostgreSQL RLS adds defense-in-depth. Apply via raw migration:

### Public Read, Authenticated Write
```sql
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "products_public_read" ON products
  FOR SELECT USING (true);

CREATE POLICY "products_auth_write" ON products
  FOR ALL USING (auth.uid() IS NOT NULL);
```

### Owner Only
```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "orders_owner_select" ON orders
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "orders_owner_insert" ON orders
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "orders_owner_update" ON orders
  FOR UPDATE USING (user_id = auth.uid());
```

### Admin Override
```sql
CREATE POLICY "products_admin_all" ON products
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role = 'ADMIN'
    )
  );
```

**Note:** RLS requires Postgres `auth.uid()` function. With NestJS, set `app.current_user_id` session var on each connection via middleware.

---

## ❌ Anti-Patterns

### ❌ Serial IDs (`@default(autoincrement())`)
```
WHY BAD: Exposes row counts, makes merging impossible
USE: UUID v4 with @default(uuid())
```

### ❌ Missing FK Index
```
WHY BAD: PostgreSQL doesn't auto-index FK columns
        → JOINs become full table scans
USE: Always @@index([foreignKeyColumn])
```

### ❌ Nullable Without Reason
```
WHY BAD: Forces null checks everywhere
USE: Default to NOT NULL, mark optional explicitly
```

### ❌ TEXT for Everything
```
WHY BAD: No length validation, slower indexes
USE: VARCHAR(n) for known max (email: 255, slug: 100)
```

### ❌ Storing Computed Values
```
WHY BAD: Goes stale, requires manual update
USE: Compute in queries or generated columns
EXCEPTION: Aggregates updated by triggers (rare)
```

### ❌ JSON/JSONB for Structured Data
```
WHY BAD: No type safety, hard to query/index
USE: Normalize into proper tables
EXCEPTION: Truly variable schemas (settings, metadata)
```

### ❌ Hard Delete by Default
```
WHY BAD: Lose audit trail, foreign key chaos
USE: Soft delete (deletedAt) for user-facing entities
EXCEPTION: GDPR compliance requires hard delete
```

---

## ✅ Schema Design Checklist

Before applying migration:
- [ ] All entities have `id`, `createdAt`, `updatedAt`?
- [ ] User-facing entities have `deletedAt`?
- [ ] All FK columns have `@@index([...])`?
- [ ] Email/username has `@unique`?
- [ ] Composite indexes match query patterns?
- [ ] Enum values won't change (immutable)?
- [ ] Cascade behavior intentional? (`onDelete: Cascade`/`Restrict`/`SetNull`)
- [ ] Snake_case mapping with `@map`/`@@map`?
- [ ] Migration is additive (or 2-phase if destructive)?
- [ ] RLS policies defined for sensitive tables?
- [ ] Tested with `prisma migrate dev --create-only` first?

---

## 🎯 Migration Workflow

```bash
# 1. Edit schema
edit prisma/schema.prisma

# 2. Preview migration (DRY RUN)
npx prisma migrate dev --create-only --name describe_change

# 3. Review generated SQL
cat prisma/migrations/<latest>/migration.sql

# 4. Apply migration
npx prisma migrate dev

# 5. Generate client
npx prisma generate

# 6. Update memory
# Edit .be/memory/schema.md
# Add row to migrations table in changelog.md
```

---

*Schema Design Skill v1.0 — PostgreSQL + Prisma 5*
