/**
 * List Command
 * Shows all available commands, agents, and skills
 */

import chalk from 'chalk';

export async function list() {
  console.log(chalk.cyan('\n📋 becraft - Available Resources\n'));

  // Commands
  console.log(chalk.white('Commands:'));
  console.log(chalk.gray('  ─────────────────────────────────────────────────────────'));
  const commands = [
    { cmd: '/be',           short: '/b',     desc: 'Smart router (any backend task)',     icon: '🧠' },
    { cmd: '/be-help',      short: '/be-h',  desc: 'Show all commands',                   icon: '❓' },
    { cmd: '/be-plan',      short: '/be-p',  desc: 'Analyze + plan',                      icon: '📋' },
    { cmd: '/be-bootstrap', short: '/be-b',  desc: 'Build full backend (Vibe equiv)',     icon: '🚀' },
    { cmd: '/be-schema',    short: '/be-s',  desc: 'DB schema + migrations',              icon: '📐' },
    { cmd: '/be-api',       short: '/be-a',  desc: 'Endpoints + DTOs + OpenAPI',          icon: '🔌' },
    { cmd: '/be-auth',      short: '/be-au', desc: 'Authn/Authz/RLS/rate-limit',          icon: '🛡️' },
    { cmd: '/be-observe',   short: '/be-o',  desc: 'Logs + metrics + traces',             icon: '📊' },
    { cmd: '/be-test',      short: '/be-t',  desc: 'Generate + run tests',                icon: '🧪' },
    { cmd: '/be-fix',       short: '/be-f',  desc: 'Debug + fix issues',                  icon: '🔧' },
  ];

  for (const c of commands) {
    console.log(
      `  ${c.icon} ${chalk.green(c.cmd.padEnd(16))} ${chalk.gray(c.short.padEnd(8))} ${chalk.white(c.desc)}`
    );
  }

  console.log(chalk.gray('\n  ─────────────────────────────────────────────────────────'));

  // Agents
  console.log(chalk.cyan('\n🤖 Agents:\n'));
  const agents = [
    { name: 'plan-orchestrator', icon: '📋', desc: 'THE BRAIN — analyze + coordinate' },
    { name: 'schema-architect',  icon: '📐', desc: 'PostgreSQL + Prisma schema design' },
    { name: 'api-builder',       icon: '🔌', desc: 'NestJS endpoints + DTOs + OpenAPI' },
    { name: 'auth-guard',        icon: '🛡️', desc: 'Authn + Authz + Rate limit + RLS' },
    { name: 'observability',     icon: '📊', desc: 'Logs + Metrics + Traces + Health' },
    { name: 'test-runner',       icon: '🧪', desc: 'Unit + Integ + Contract + Auto-fix' },
  ];

  for (const a of agents) {
    console.log(`  ${a.icon} ${chalk.yellow(a.name.padEnd(22))} ${chalk.white(a.desc)}`);
  }

  // Skills
  console.log(chalk.cyan('\n📚 Skills:\n'));
  const skills = [
    { name: 'contract-first',   desc: 'Master CDD workflow' },
    { name: 'schema-design',    desc: 'PostgreSQL + Prisma patterns' },
    { name: 'api-design',       desc: 'REST conventions + versioning' },
    { name: 'auth-patterns',    desc: 'JWT, OAuth, RBAC, RLS, rate-limit' },
    { name: 'testing-pyramid',  desc: 'Unit + Integration + Contract' },
    { name: 'observability',    desc: 'Logs + Metrics + Traces' },
    { name: 'error-handling',   desc: 'RFC 7807 + retry + idempotency' },
    { name: 'memory-system',    desc: 'Memory protocol (9 files)' },
    { name: 'response-format',  desc: '3-section response standard' },
    { name: 'smart-routing',    desc: 'Intent classification for /be' },
  ];

  for (const s of skills) {
    console.log(`  • ${chalk.magenta(s.name.padEnd(20))} ${chalk.white(s.desc)}`);
  }

  console.log('');
}
