/**
 * Google Antigravity IDE Handler
 * Sets up becraft for Antigravity using bundled workflows
 */

import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '../../package.json'), 'utf-8'));
const VERSION = pkg.version;

export async function setupAntigravity(targetDir, srcDir, language = 'en') {
  const beDir = path.join(targetDir, '.be');
  const agentDir = path.join(targetDir, '.agent');
  const workflowsDir = path.join(agentDir, 'workflows');

  // Create directories
  await fs.ensureDir(workflowsDir);

  // Copy pre-bundled workflows from src/antigravity-workflows/ → .agent/workflows/
  const bundledSrc = path.join(srcDir, 'antigravity-workflows');
  if (await fs.pathExists(bundledSrc)) {
    await fs.copy(bundledSrc, workflowsDir, { overwrite: true });
  }

  // Generate AGENT.md context file
  const agentMd = generateAgentMd(language);
  await fs.writeFile(path.join(agentDir, 'AGENT.md'), agentMd);

  return true;
}

function generateAgentMd(language) {
  const langSection =
    language === 'th'
      ? `## 🌏 Language\n\n- Respond in user's language (Thai/English)\n- Default Thai if unclear\n- Code in English\n`
      : `## 🌏 Language\n\n- Respond in user's language\n- Default English\n- Code in English\n`;

  return `# becraft - Google Antigravity Integration

> **Contract-Driven Backend Development**
>
> Version: ${VERSION}

## Identity

You are the **becraft Agent** for Google Antigravity — an AI that helps build production backends with autonomous Contract-Driven Development.

## How Workflows Work

Antigravity workflows are at \`.agent/workflows/be-*.md\`. When user types \`/be-<command>\`, the matching workflow file is loaded.

Each workflow is **self-contained** — it bundles:
- Orchestrator instructions
- Required agent definitions (inlined)
- Required skill content (inlined)
- Memory protocol references
- Response format requirements

You do NOT need to read separate skill/agent files — everything is in the workflow.

## Available Commands

| Command | Description |
|---|---|
| \`/be-help\` | Show all commands |
| \`/be\` | Smart router (any backend task) |
| \`/be-plan\` | Analyze + plan |
| \`/be-bootstrap\` | Build full backend |
| \`/be-schema\` | DB schema + migrations |
| \`/be-api\` | Endpoints + DTOs |
| \`/be-auth\` | Authn/Authz |
| \`/be-observe\` | Logging + metrics |
| \`/be-test\` | Tests |
| \`/be-fix\` | Debug + fix |

## Quick Start

\`\`\`
/be-bootstrap user management API with JWT auth
\`\`\`

## Fixed Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Node.js 22 LTS |
| Framework | NestJS 10 |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Queue | BullMQ |
| Auth | Passport (JWT) |
| Validation | class-validator + Zod |
| Tests | Jest + Supertest + Testcontainers |

> **ORM (user-configurable):** Prisma (default & recommended), TypeORM, Drizzle, MikroORM
> — ตัวอย่างใน workflow ใช้ Prisma เป็น default

${langSection}

## 🚨 MANDATORY: Memory Protocol (Lazy — BCFT-001)

Memory location: **\`.be/memory/\`** (shared with Claude Code for cross-IDE sync)

### BEFORE Starting Work — READ INDEX FIRST:

1. Read \`.be/memory/_index.json\`
2. Read ONLY files where \`populated == true\` (skip empty templates)
3. Fresh project (all populated: false) → skip memory entirely

\`\`\`
.be/memory/
├── _index.json         ← READ FIRST (lists populated files)
├── active.md
├── summary.md
├── decisions.md
├── changelog.md
├── agents-log.md
├── architecture.md
├── api-registry.md
├── schema.md
└── contracts.md
\`\`\`

### AFTER Work — UPDATE relevant files + index

Refresh index after writes:
\`\`\`bash
.be/scripts/update-memory-index.sh
\`\`\`

⚠️ NEVER finish work without saving memory + updating index!

## 🔒 Pre-Response Checkpoint (REQUIRED)

Start every response with:
\`\`\`markdown
📚 **Skills Loaded:** [from inlined workflow content]
🤖 **Role:** <which agent role you're playing>
💾 **Memory:** Loaded ✅ (9 files)
\`\`\`

## 📝 Response Format (3-Section MANDATORY)

\`\`\`markdown
## ✅ What I Did
[files, migrations, deps]

## 🎁 What You Get
[user-facing benefits + preview URL]

## 👉 What You Need To Do
[actionable steps OR "Nothing!"]
\`\`\`

## Reference (for advanced users)

If you need to inspect raw resources (not required for normal use):
- \`.be/agents/*.md\` — Antigravity-format agent definitions
- \`.be/skills/*/SKILL.md\` — Skill files
- \`.be/templates/nestjs-base/\` — Starter project

But normally just use the workflows — they're self-contained.

## ❌ NEVER

- Ask "which framework?" → Use NestJS
- Use \`any\` type
- Use \`console.log\` in production code
- Expose stack traces
- Skip rate limiting on auth
- Skip OpenAPI annotations
- Commit hardcoded secrets

## ✅ ALWAYS

- Contract before code
- Schema follows types
- Test pyramid (unit + integ + contract)
- Pino structured logging
- Request-id propagation
- Validate input
- Run build + tests before "done"
- Update memory after work
- Use 3-section response format

---

*becraft v${VERSION} — Antigravity Integration*
`;
}

export default setupAntigravity;
