/**
 * Status Command
 * Check installation status in current directory
 */

import chalk from 'chalk';
import fs from 'fs-extra';
import { join } from 'path';

export async function status() {
  console.log(chalk.cyan('\n🔍 becraft Installation Status\n'));

  const cwd = process.cwd();

  // Check .be/manifest.json
  const manifestPath = join(cwd, '.be', 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    console.log(chalk.red('  ✗ becraft not installed in this directory'));
    console.log(chalk.gray('    Run: npx becraft install\n'));
    return;
  }

  const manifest = await fs.readJson(manifestPath);
  console.log(chalk.green(`  ✓ Installed: v${manifest.version}`));
  console.log(chalk.gray(`    Date: ${manifest.installedAt}`));
  console.log(chalk.gray(`    Stack: ${manifest.stack || 'nestjs'}`));
  console.log(chalk.gray(`    Language: ${manifest.language || 'en'}`));
  console.log(chalk.gray(`    IDEs: ${manifest.ides.join(', ')}\n`));

  // Check components
  console.log(chalk.white('  Components:'));
  await checkPath(join(cwd, '.be', 'skills'),    'skills');
  await checkPath(join(cwd, '.be', 'agents'),    'agents');
  await checkPath(join(cwd, '.be', 'commands'),  'commands');
  await checkPath(join(cwd, '.be', 'templates'), 'templates');

  // Check memory (9 files)
  console.log(chalk.white('\n  Memory:'));
  const memoryFiles = [
    'active', 'summary', 'decisions', 'changelog', 'agents-log',
    'architecture', 'api-registry', 'schema', 'contracts',
  ];
  for (const f of memoryFiles) {
    const p = join(cwd, '.be', 'memory', `${f}.md`);
    if (fs.existsSync(p)) {
      console.log(chalk.green(`    ✓ ${f}.md`));
    } else {
      console.log(chalk.red(`    ✗ ${f}.md (missing)`));
    }
  }

  // Check IDE configs
  console.log(chalk.white('\n  IDE Config:'));

  if (manifest.ides.includes('claude') || manifest.ides.includes('claude-code')) {
    const claudeMd = join(cwd, 'CLAUDE.md');
    const claudeAgents = join(cwd, '.claude', 'agents');
    if (fs.existsSync(claudeMd)) console.log(chalk.green('    ✓ CLAUDE.md'));
    else console.log(chalk.red('    ✗ CLAUDE.md (missing)'));
    if (fs.existsSync(claudeAgents)) {
      const files = await fs.readdir(claudeAgents);
      console.log(chalk.green(`    ✓ .claude/agents/ (${files.length} files)`));
    } else {
      console.log(chalk.red('    ✗ .claude/agents/ (missing)'));
    }
  }

  if (manifest.ides.includes('antigravity')) {
    const agentMd = join(cwd, '.agent', 'AGENT.md');
    const workflows = join(cwd, '.agent', 'workflows');
    if (fs.existsSync(agentMd)) console.log(chalk.green('    ✓ .agent/AGENT.md'));
    else console.log(chalk.red('    ✗ .agent/AGENT.md (missing)'));
    if (fs.existsSync(workflows)) {
      const files = await fs.readdir(workflows);
      console.log(chalk.green(`    ✓ .agent/workflows/ (${files.length} files)`));
    } else {
      console.log(chalk.red('    ✗ .agent/workflows/ (missing)'));
    }
  }

  console.log('');
}

async function checkPath(p, name) {
  if (fs.existsSync(p)) {
    const files = await countFiles(p);
    console.log(chalk.green(`    ✓ ${name.padEnd(12)} (${files} files)`));
  } else {
    console.log(chalk.red(`    ✗ ${name} (missing)`));
  }
}

async function countFiles(dir) {
  let count = 0;
  const items = await fs.readdir(dir, { withFileTypes: true });
  for (const item of items) {
    if (item.isDirectory()) count += await countFiles(join(dir, item.name));
    else count++;
  }
  return count;
}
