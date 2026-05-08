/**
 * Snippet: Zod env validation for NestJS ConfigModule
 *
 * Used by: bootstrap-agent (in app.module.ts)
 * Customize: add/remove env vars per stack
 *
 * Usage:
 *   ConfigModule.forRoot({
 *     isGlobal: true,
 *     validate: validateEnv,
 *   })
 */

import { z } from 'zod';

// === Common (all stacks) ===
const baseSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().default(3000),
  LOG_LEVEL: z.enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace']).default('info'),
  APP_NAME: z.string().default('becraft-app'),
  CORS_ORIGIN: z.string().optional(),

  // JWT
  JWT_SECRET: z.string().min(32),
  JWT_REFRESH_SECRET: z.string().min(32),
  JWT_ACCESS_TTL: z.string().default('15m'),
  JWT_REFRESH_TTL: z.string().default('7d'),
  BCRYPT_ROUNDS: z.coerce.number().default(12),

  // Cache
  REDIS_URL: z.string().url(),
});

// === Prisma variant ===
export const prismaEnvSchema = baseSchema.extend({
  DATABASE_URL: z.string().url(),
});

// === Supabase variant ===
export const supabaseEnvSchema = baseSchema.extend({
  SUPABASE_URL: z.string().url(),
  SUPABASE_ANON_KEY: z.string().min(20),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(20).optional(),
});

// === Validator function ===
export function makeValidateEnv(schema: z.ZodTypeAny) {
  return (config: Record<string, unknown>) => {
    const parsed = schema.safeParse(config);
    if (!parsed.success) {
      throw new Error(`Invalid env: ${parsed.error.message}`);
    }
    return parsed.data;
  };
}

// Use:
// validate: makeValidateEnv(prismaEnvSchema)
// validate: makeValidateEnv(supabaseEnvSchema)
