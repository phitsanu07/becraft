#!/usr/bin/env node

/**
 * becraft CLI
 * Contract-Driven Backend Development
 *
 * Usage:
 *   npx becraft install
 *   npx becraft list
 *   npx becraft status
 *   npx becraft bundle
 */

import { Command } from 'commander';
import chalk from 'chalk';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Read package.json (Single Source of Truth for version)
const packagePath = join(__dirname, '..', 'package.json');
const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'));

const program = new Command();

// ASCII Banner
const versionStr = `v${packageJson.version}`;
const banner = `
${chalk.cyan('╔════════════════════════════════════════════════════════════╗')}
${chalk.cyan('║')}  ${chalk.bold.white('becraft')} ${chalk.gray(versionStr)}                                              ${chalk.cyan('║')}
${chalk.cyan('║')}  ${chalk.yellow('Contract-Driven Backend Development')}                       ${chalk.cyan('║')}
${chalk.cyan('║')}  ${chalk.green('"Craft Production Backends, Not Prototypes"')}              ${chalk.cyan('║')}
${chalk.cyan('╚════════════════════════════════════════════════════════════╝')}
`;

program
  .name('becraft')
  .description('Contract-Driven Backend Development Framework')
  .version(packageJson.version)
  .hook('preAction', () => {
    console.log(banner);
  });

// install
program
  .command('install')
  .description('Install becraft to your project')
  .option('-t, --target <path>', 'Target directory', process.cwd())
  .option('-i, --ide <ides>', 'IDEs to configure (claude,antigravity)', 'claude,antigravity')
  .option('-l, --lang <lang>', 'Language (en,th)', 'en')
  .option('-s, --stack <stack>', 'Stack profile (nestjs)', 'nestjs')
  .option('-q, --quick', 'Quick install without prompts')
  .action(async (options) => {
    const { install } = await import('../installer/install.js');
    await install(options);
  });

// list
program
  .command('list')
  .description('List all available commands, agents, and skills')
  .action(async () => {
    const { list } = await import('../installer/list.js');
    await list();
  });

// status
program
  .command('status')
  .description('Check installation status')
  .action(async () => {
    const { status } = await import('../installer/status.js');
    await status();
  });

// bundle
program
  .command('bundle')
  .description('Re-generate Antigravity workflows from agents + skills + commands')
  .option('-o, --output <path>', 'Output directory', './src/antigravity-workflows')
  .action(async (options) => {
    const { bundle } = await import('../scripts/bundle.js');
    await bundle(options);
  });

program.parse();
