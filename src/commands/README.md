# becraft Commands

10 slash commands for backend development. All work in **Claude Code** AND **Antigravity**.

## Commands

| Command | Shortcut | Agent | Purpose |
|---------|----------|-------|---------|
| `/be` | `/b` | router | 🧠 Smart router — type anything |
| `/be-help` | `/be-h` | - | ❓ Show all commands |
| `/be-plan` | `/be-p` | plan | 📋 Analyze + plan |
| `/be-bootstrap` | `/be-b` | all | 🚀 Build full backend |
| `/be-schema` | `/be-s` | schema | 📐 DB schema + migrations |
| `/be-api` | `/be-a` | api | 🔌 Endpoints + DTOs |
| `/be-auth` | `/be-au` | auth | 🛡️ JWT + RBAC + rate-limit |
| `/be-observe` | `/be-o` | observe | 📊 Logs + metrics + health |
| `/be-test` | `/be-t` | test | 🧪 Generate + run tests |
| `/be-fix` | `/be-f` | test | 🔧 Debug + fix |

## File Format

Each command is a Markdown file with:
- YAML frontmatter (`description`)
- Mission statement
- Memory protocol reference (9 files)
- Skills to load (`@.claude/skills/...`)
- Agent to delegate (`@.claude/agents/...`)
- Skills Loading Checkpoint template
- Workflow phases
- Critical rules
- 3-section response format
- NEVER / ALWAYS lists

## Cross-IDE Usage

### Claude Code
- Commands at `.claude/commands/be-*.md`
- Native sub-agent delegation via `Task` tool
- Parallel execution allowed

### Antigravity
- Same syntax `/be-*` (dash)
- Workflows at `.agent/workflows/be-*.md` (pre-bundled by `bundle.js`)
- Sequential execution (no native parallel)

## Examples

### Quick start
```
/be-bootstrap user management API
```

### Specific task
```
/be-schema add Product entity (name, price, stock)
/be-api create CRUD for products
/be-auth setup JWT
/be-test for products module
```

### Smart routing
```
/be สร้าง API สำหรับ inventory
```

The router classifies intent and picks right agent(s).
