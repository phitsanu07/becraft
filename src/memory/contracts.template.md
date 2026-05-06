# 📜 API Contracts

> OpenAPI snapshots, breaking change log, versioning history
> **Update:** Before/after every contract change

---

## 📊 Contract Statistics

| Metric | Value |
|--------|-------|
| Current API Version | v1 |
| OpenAPI Version | 3.0.3 |
| Breaking Changes (lifetime) | 0 |
| Last Snapshot | {{DATE}} |

---

## 🔖 Versioning Strategy

- **Major** (v1 → v2): Breaking changes (remove field, change type, change auth)
- **Minor** (v1.1 → v1.2): Additive changes (new field, new endpoint)
- **Patch** (bug fixes): Same version, fix in place

### Deprecation Policy
- Mark deprecated in OpenAPI: `deprecated: true`
- Add `Deprecation` HTTP header
- Minimum 6 months before removal
- Document in this file

---

## 📂 Contract Snapshots

### Current (v1.0.0) - {{DATE}}
- Status: 🟢 Active
- Endpoints: 0
- Snapshot: `openapi/v1.0.0.json` (after first /be-api run)

---

## 🚨 Breaking Changes Log

| Version | Date | Change | Migration Path |
|---------|------|--------|----------------|
| - | - | - | - |

---

## ⚠️ Deprecated Endpoints

| Endpoint | Deprecated Since | Removal Planned | Replacement |
|----------|------------------|-----------------|-------------|
| - | - | - | - |

---

## ✅ Contract Test Status

| Endpoint | Contract Test | Last Run | Status |
|----------|---------------|----------|--------|
| - | - | - | - |

---

## 🎯 Contract-First Workflow Rules

1. **OpenAPI spec written BEFORE code** (auto-generated from DTOs is OK)
2. **No field removal without major version bump**
3. **No type narrowing in responses** (e.g., `string | null` → `string` is breaking)
4. **No required field additions in requests** (unless major bump)
5. **Document all breaking changes here**

---
*Last updated: {{TIMESTAMP}}*
