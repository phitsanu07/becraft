/**
 * becraft Installer
 * Main installation orchestrator
 */

import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import fs from 'fs-extra';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { setupClaudeCode } from './ide-handlers/claude-code.js';
import { setupAntigravity } from './ide-handlers/antigravity.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const SRC_DIR = join(__dirname, '..', 'src');
const PKG_PATH = join(__dirname, '..', 'package.json');
const pkg = await fs.readJson(PKG_PATH);
const VERSION = pkg.version;

export async function install(options) {
  const { target, ide, quick, lang, stack } = options;

  console.log(chalk.cyan('\n📦 Starting becraft Installation...\n'));

  let config = {
    targetDir: target,
    ides: ide.split(',').map((i) => i.trim()),
    language: lang || 'en',
    stack: stack || 'nestjs',
    installSkills: true,
    installAgents: true,
    installCommands: true,
    installTemplates: true,
  };

  if (!quick) {
    config = await promptConfiguration(config);
  }

  // Validate target directory
  const spinner = ora('Validating target directory...').start();
  if (!fs.existsSync(config.targetDir)) {
    spinner.warn('Target directory does not exist');
    const { create } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'create',
        message: `Create directory ${config.targetDir}?`,
        default: true,
      },
    ]);
    if (!create) {
      spinner.fail('Installation cancelled');
      return;
    }
    await fs.ensureDir(config.targetDir);
    spinner.succeed('Directory created');
  } else {
    spinner.succeed('Target directory validated');
  }

  // Check existing installation
  const existing = await checkExistingInstall(config.targetDir);
  if (existing) {
    const { action } = await inquirer.prompt([
      {
        type: 'list',
        name: 'action',
        message: 'Existing becraft installation detected. What would you like to do?',
        choices: [
          { name: '🔄 Quick Update (preserve customizations)', value: 'update' },
          { name: '🗑️  Fresh Install (overwrite all)', value: 'fresh' },
          { name: '❌ Cancel', value: 'cancel' },
        ],
      },
    ]);
    if (action === 'cancel') {
      console.log(chalk.yellow('\nInstallation cancelled.'));
      return;
    }
    if (action === 'fresh') await cleanExistingInstall(config.targetDir);
  }

  // Install resources to .be/
  console.log(chalk.cyan('\n📁 Installing components...\n'));
  if (config.installSkills) await installComponent('skills', config.targetDir);
  if (config.installAgents) await installComponent('agents', config.targetDir);
  if (config.installCommands) await installComponent('commands', config.targetDir);
  if (config.installTemplates) await installComponent('templates', config.targetDir);

  // Setup memory (9 files)
  await setupMemoryFolder(config.targetDir);

  // Configure IDEs
  console.log(chalk.cyan('\n🛠️  Configuring IDEs...\n'));
  for (const ideName of config.ides) {
    switch (ideName.toLowerCase()) {
      case 'claude':
      case 'claude-code':
        await setupIDEWithSpinner('Claude Code', () =>
          setupClaudeCode(config.targetDir, config.language)
        );
        break;
      case 'antigravity':
      case 'google-antigravity':
        await setupIDEWithSpinner('Google Antigravity', () =>
          setupAntigravity(config.targetDir, SRC_DIR, config.language)
        );
        break;
      default:
        console.log(chalk.yellow(`  ⚠️  Unknown IDE: ${ideName}`));
    }
  }

  await generateManifest(config);

  console.log(chalk.green('\n✅ becraft installed successfully!\n'));
  printNextSteps(config);
}

async function promptConfiguration(defaults) {
  const answers = await inquirer.prompt([
    {
      type: 'list',
      name: 'language',
      message: '🌐 Select language / เลือกภาษา:',
      choices: [
        { name: '🇺🇸 English (Default)', value: 'en' },
        { name: '🇹🇭 ภาษาไทย', value: 'th' },
      ],
      default: 'en',
    },
    {
      type: 'input',
      name: 'targetDir',
      message: 'Target directory:',
      default: defaults.targetDir,
    },
    {
      type: 'checkbox',
      name: 'ides',
      message: 'Which IDEs to configure?',
      choices: [
        { name: '🤖 Claude Code (Anthropic)', value: 'claude', checked: true },
        { name: '🌌 Google Antigravity', value: 'antigravity', checked: true },
      ],
      validate: (input) => (input.length > 0 ? true : 'Please select at least one IDE'),
    },
    {
      type: 'list',
      name: 'stack',
      message: 'Stack profile:',
      choices: [{ name: 'NestJS + PostgreSQL + Prisma', value: 'nestjs' }],
      default: 'nestjs',
    },
    {
      type: 'checkbox',
      name: 'components',
      message: 'What would you like to install?',
      choices: [
        { name: 'Skills (10 backend skills)', value: 'skills', checked: true },
        { name: 'Agents (6 specialized agents)', value: 'agents', checked: true },
        { name: 'Commands (/be-* commands)', value: 'commands', checked: true },
        { name: 'Templates (NestJS starter)', value: 'templates', checked: true },
      ],
    },
  ]);

  return {
    ...defaults,
    ...answers,
    installSkills: answers.components.includes('skills'),
    installAgents: answers.components.includes('agents'),
    installCommands: answers.components.includes('commands'),
    installTemplates: answers.components.includes('templates'),
  };
}

async function checkExistingInstall(targetDir) {
  const markers = [
    join(targetDir, '.be', 'manifest.json'),
    join(targetDir, '.claude', 'agents', 'plan-orchestrator.md'),
    join(targetDir, '.agent', 'workflows', 'be-bootstrap.md'),
  ];
  return markers.some((m) => fs.existsSync(m));
}

async function cleanExistingInstall(targetDir) {
  const spinner = ora('Cleaning existing installation...').start();
  const paths = [
    join(targetDir, '.be'),
    join(targetDir, '.claude', 'skills'),
    join(targetDir, '.claude', 'agents'),
    join(targetDir, '.claude', 'commands'),
    join(targetDir, '.agent', 'workflows'),
  ];
  for (const p of paths) {
    if (fs.existsSync(p)) await fs.remove(p);
  }
  spinner.succeed('Cleaned existing installation');
}

async function setupIDEWithSpinner(name, fn) {
  const spinner = ora(`Configuring ${name}...`).start();
  try {
    await fn();
    spinner.succeed(`${name} configured`);
  } catch (err) {
    spinner.fail(`Failed to configure ${name}: ${err.message}`);
  }
}

async function installComponent(name, targetDir) {
  const spinner = ora(`Installing ${name}...`).start();
  const srcPath = join(SRC_DIR, name);
  const destPath = join(targetDir, '.be', name);
  try {
    if (!fs.existsSync(srcPath)) {
      spinner.warn(`${name} source not found, skipping`);
      return;
    }
    await fs.ensureDir(destPath);
    await fs.copy(srcPath, destPath, { overwrite: true });
    const count = await countFiles(destPath);
    spinner.succeed(`Installed ${name} (${count} files)`);
  } catch (err) {
    spinner.fail(`Failed to install ${name}: ${err.message}`);
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

async function generateManifest(config) {
  const spinner = ora('Generating manifest...').start();
  const manifest = {
    version: VERSION,
    installedAt: new Date().toISOString(),
    targetDir: config.targetDir,
    ides: config.ides,
    stack: config.stack,
    language: config.language,
    components: {
      skills: config.installSkills,
      agents: config.installAgents,
      commands: config.installCommands,
      templates: config.installTemplates,
      memory: true,
    },
  };
  const manifestPath = join(config.targetDir, '.be', 'manifest.json');
  await fs.ensureDir(join(config.targetDir, '.be'));
  await fs.writeJson(manifestPath, manifest, { spaces: 2 });
  spinner.succeed('Manifest generated');
}

async function setupMemoryFolder(targetDir) {
  const spinner = ora('Setting up Memory System (9 files)...').start();
  const memoryDir = join(targetDir, '.be', 'memory');
  const archiveDir = join(memoryDir, 'archive');
  const today = new Date().toISOString().split('T')[0];
  const timestamp = new Date().toISOString();

  try {
    await fs.ensureDir(memoryDir);
    await fs.ensureDir(archiveDir);

    const templates = [
      'active', 'summary', 'decisions', 'changelog', 'agents-log',
      'architecture', 'api-registry', 'schema', 'contracts',
    ];

    for (const name of templates) {
      const srcPath = join(SRC_DIR, 'memory', `${name}.template.md`);
      const destPath = join(memoryDir, `${name}.md`);

      if (fs.existsSync(destPath)) continue;

      let content;
      if (fs.existsSync(srcPath)) {
        content = await fs.readFile(srcPath, 'utf8');
      } else {
        content = `# ${name}\n\n_Template missing — created on ${today}_\n`;
      }
      content = content
        .replace(/{{TIMESTAMP}}/g, timestamp)
        .replace(/{{VERSION}}/g, VERSION)
        .replace(/{{DATE}}/g, today);
      await fs.writeFile(destPath, content);
    }

    spinner.succeed(`Memory System ready - 9 files (.be/memory/)`);
  } catch (err) {
    spinner.fail(`Failed to setup Memory System: ${err.message}`);
  }
}

function printNextSteps(config) {
  const W = 60;
  const pad = (s) => s.padEnd(W);
  const row = (c) => chalk.cyan('│') + c + chalk.cyan('│');
  const top = chalk.cyan('┌' + '─'.repeat(W) + '┐');
  const mid = chalk.cyan('├' + '─'.repeat(W) + '┤');
  const bot = chalk.cyan('└' + '─'.repeat(W) + '┘');
  const empty = row(' '.repeat(W));

  console.log(top);
  console.log(row(chalk.bold.white(pad(`  becraft v${VERSION} Installed!`))));
  console.log(mid);

  if (config.ides.includes('claude') || config.ides.includes('claude-code')) {
    console.log(row(chalk.white(pad('  Claude Code:'))));
    console.log(row(chalk.green('    /be-help') + chalk.gray('     - Show all commands'.padEnd(51))));
    console.log(row(chalk.green('    /be-bootstrap') + chalk.gray(' - Build full backend'.padEnd(46))));
    console.log(row(chalk.green('    /be-api') + chalk.gray('      - Create endpoints'.padEnd(52))));
    console.log(empty);
  }

  if (config.ides.includes('antigravity')) {
    console.log(row(chalk.white(pad('  Google Antigravity:'))));
    console.log(row(chalk.green('    /be-help') + chalk.gray('     - Show all commands'.padEnd(51))));
    console.log(row(chalk.green('    /be-bootstrap') + chalk.gray(' - Build full backend'.padEnd(46))));
    console.log(empty);
  }

  console.log(row(chalk.white(pad('  Memory: .be/memory/ (cross-IDE sync)'))));
  console.log(row(chalk.white(pad('  Stack: NestJS + PostgreSQL + Prisma'))));
  console.log(mid);
  console.log(row(chalk.bold.yellow(pad("  Quick start:"))));
  console.log(row(chalk.white(pad('  /be-bootstrap user management API'))));
  console.log(bot);
  console.log('');
}
