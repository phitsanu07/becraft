# 📐 Database Schema

> Complete database schema + migration history
> **Update:** After every schema change

---

## 📊 Schema Statistics

| Metric | Count |
|--------|-------|
| Tables | 0 |
| Columns | 0 |
| Foreign Keys | 0 |
| Indexes | 0 |
| Migrations | 0 |

---

## 🗄️ Tables

### (none yet)

Template format for adding tables:

```
### users
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, default gen_random_uuid() | Primary key |
| email | text | UNIQUE, NOT NULL | User email |
| created_at | timestamptz | NOT NULL, default now() | Created at |
| updated_at | timestamptz | NOT NULL, default now() | Updated at |

**Indexes:**
- `users_email_idx` ON (email)

**Foreign Keys:**
- (none)

**RLS Policies:**
- Public read: ❌
- Owner only: ✅
```

---

## 🔗 Entity Relationships (ER)

```
(none yet)
```

---

## 📜 Migration History

| Version | Name | Date | Status | Type |
|---------|------|------|--------|------|
| - | - | - | - | - |

### Migration Types
- `additive` — Add columns/tables (safe)
- `destructive` — Drop columns/tables (requires confirmation)
- `data` — Data migration (verify before run)

---

## ⚠️ Pending Schema Changes

(none)

---

## 🔒 Row-Level Security (RLS)

| Table | RLS Enabled | Policies |
|-------|-------------|----------|
| - | - | - |

---

## 📈 Index Strategy

Columns frequently queried (need index):
- (none yet)

---
*Last updated: {{TIMESTAMP}}*
