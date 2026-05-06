/**
 * Antigravity Workflow Bundler
 * Generates self-contained workflow files by inlining agents + skills into commands
 */

import chalk from 'chalk';
import ora from 'ora';
import fs from 'fs-extra';
import { fileURLToPath } from 'url';
import { dirname, join, basename } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = join(__dirname, '..');
const SRC = join(ROOT, 'src');

// Command → required agents + skills mapping
const BUNDLE_MAP = {
  'be': {
    agents: ['plan-orchestrator'],
    skills: ['smart-routing', 'memory-system', 'response-format', 'contract-first'],
  },
  'be-help': {
    agents: [],
    skills: ['response-format'],
  },
  'be-plan': {
    agents: ['plan-orchestrator'],
    skills: ['contract-first', 'memory-system', 'response-format'],
  },
  'be-bootstrap': {
    agents: ['plan-orchestrator', 'schema-architect', 'api-builder', 'auth-guard', 'observability', 'test-runner'],
    skills: ['contract-first', 'schema-design', 'api-design', 'auth-patterns', 'testing-pyramid', 'observability', 'response-format', 'memory-system'],
  },
  'be-schema': {
    agents: ['schema-architect'],
    skills: ['schema-design', 'contract-first', 'response-format', 'memory-system'],
  },
  'be-api': {
    agents: ['api-builder'],
    skills: ['api-design', 'contract-first', 'error-handling', 'response-format', 'memory-system'],
  },
  'be-auth': {
    agents: ['auth-guard'],
    skills: ['auth-patterns', 'response-format', 'memory-system'],
  },
  'be-observe': {
    agents: ['observability'],
    skills: ['observability', 'response-format', 'memory-system'],
  },
  'be-test': {
    agents: ['test-runner'],
    skills: ['testing-pyramid', 'error-handling', 'response-format', 'memory-system'],
  },
  'be-fix': {
    agents: ['test-runner'],
    skills: ['error-handling', 'testing-pyramid', 'response-format', 'memory-system'],
  },
};

export async function bundle(options = {}) {
  const output = options.output || join(SRC, 'antigravity-workflows');

  console.log(chalk.cyan('\n📦 Bundling Antigravity Workflows\n'));

  await fs.ensureDir(output);

  let total = 0;
  let success = 0;

  for (const [cmd, config] of Object.entries(BUNDLE_MAP)) {
    total++;
    const spinner = ora(`Bundling ${cmd}...`).start();

    try {
      const bundled = await bundleCommand(cmd, config);
      const destPath = join(output, `${cmd}.md`);
      await fs.writeFile(destPath, bundled);
      const lines = bundled.split('\n').length;
      spinner.succeed(`${cmd}.md (${lines} lines)`);
      success++;
    } catch (err) {
      spinner.fail(`${cmd}.md — ${err.message}`);
    }
  }

  console.log(
    chalk.green(`\n✅ Bundled ${success}/${total} workflows → ${output}\n`)
  );
}

async function bundleCommand(cmd, config) {
  const cmdPath = join(SRC, 'commands', `${cmd}.md`);

  if (!await fs.pathExists(cmdPath)) {
    // Generate stub if command doesn't exist yet
    return generateStubWorkflow(cmd, config);
  }

  let cmdContent = await fs.readFile(cmdPath, 'utf8');

  // Strip frontmatter and capture description
  const fmMatch = cmdContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  let description = `becraft ${cmd} workflow`;
  if (fmMatch) {
    const fm = fmMatch[1];
    const descMatch = fm.match(/description:\s*(.+)/);
    if (descMatch) description = descMatch[1].trim().replace(/^["']|["']$/g, '');
    cmdContent = fmMatch[2];
  }

  // Replace Claude-specific paths with .be/ paths
  cmdContent = cmdContent
    .replace(/@\.claude\/skills\//g, '.be/skills/')
    .replace(/@\.claude\/agents\//g, '.be/agents/')
    .replace(/@\.claude\/commands\//g, '.be/commands/');

  // Build the bundled workflow
  let bundle = `---
name: ${cmd}
description: ${description}
---

# /${cmd} - Bundled Workflow (Antigravity)

> **⚠️ Self-contained workflow** — All required agents and skills are inlined below.
> No need to read external files. Memory is at \`.be/memory/\`.

---

## 🚨 MANDATORY: Memory Protocol (9 Files)

Before starting, READ all 9 memory files:

\`\`\`
.be/memory/
├── active.md           (current task)
├── summary.md          (project overview)
├── decisions.md        (architecture decisions)
├── changelog.md        (session changes)
├── agents-log.md       (agent activity)
├── architecture.md     (service structure)
├── api-registry.md     (endpoints + DTOs)
├── schema.md           (DB schema + migrations)
└── contracts.md        (OpenAPI snapshots)
\`\`\`

After completing work, UPDATE relevant files. Confirm: "✅ Memory saved"

---

## 🔒 Pre-Response Checkpoint (REQUIRED)

Start your response with:

\`\`\`markdown
📚 **Skills Loaded:** ${config.skills.map((s) => `${s} ✅`).join(', ')}

🤖 **Role:** ${config.agents[0] || 'Orchestrator'}

💾 **Memory:** Loaded ✅ (9 files)
\`\`\`

---

## 📍 ROLE: Orchestrator (from /${cmd} command)

${cmdContent.trim()}

---
`;

  // Inline each agent
  for (const agent of config.agents) {
    const agentPath = join(SRC, 'agents', `${agent}.md`);
    if (await fs.pathExists(agentPath)) {
      let content = await fs.readFile(agentPath, 'utf8');
      content = stripFrontmatter(content);
      bundle += `\n## 🤖 EMBEDDED AGENT: ${agent}\n\n${content.trim()}\n\n---\n`;
    } else {
      bundle += `\n## 🤖 EMBEDDED AGENT: ${agent}\n\n_(agent file not found — will be added in next phase)_\n\n---\n`;
    }
  }

  // Inline each skill
  for (const skill of config.skills) {
    const skillPath = join(SRC, 'skills', skill, 'SKILL.md');
    if (await fs.pathExists(skillPath)) {
      let content = await fs.readFile(skillPath, 'utf8');
      content = stripFrontmatter(content);
      bundle += `\n## 📚 EMBEDDED SKILL: ${skill}\n\n${content.trim()}\n\n---\n`;
    } else {
      bundle += `\n## 📚 EMBEDDED SKILL: ${skill}\n\n_(skill file not found — will be added in next phase)_\n\n---\n`;
    }
  }

  // Footer with response format reminder
  bundle += `
## 📝 Response Format (3-Section MANDATORY)

After completing, end your response with:

\`\`\`markdown
## ✅ What I Did
- [files, migrations, deps]

## 🎁 What You Get
- [user-facing benefits]
- Preview: http://localhost:3000/docs

## 👉 What You Need To Do
- [actionable steps OR "Nothing!"]
\`\`\`

---

*Bundled by becraft @${new Date().toISOString().split('T')[0]}*
`;

  return bundle;
}

function stripFrontmatter(content) {
  const m = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
  return m ? m[1] : content;
}

function generateStubWorkflow(cmd, config) {
  return `---
name: ${cmd}
description: becraft ${cmd} workflow (stub)
---

# /${cmd} - Workflow (Stub)

> Command file not yet created. This is a placeholder.

## Required Agents
${config.agents.map((a) => `- ${a}`).join('\n')}

## Required Skills
${config.skills.map((s) => `- ${s}`).join('\n')}

## Memory Protocol

Read all 9 files at \`.be/memory/\` before work.

---

*Stub generated by becraft bundler*
`;
}
