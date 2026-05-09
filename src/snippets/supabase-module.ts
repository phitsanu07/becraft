/**
 * Snippet: SupabaseModule for NestJS
 *
 * Used by: bootstrap-agent (when stack = Supabase JS)
 * Materializes to: src/modules/supabase/supabase.module.ts
 *
 * Pairs with:
 *   - supabase-tokens.ts   → src/modules/supabase/supabase.tokens.ts
 *   - supabase-service.ts  → src/modules/supabase/supabase.service.ts
 *
 * Re-exports tokens for backwards compatibility with imports of the form
 * `from './supabase.module'`. New code should import from `./supabase.tokens`
 * directly.
 *
 * Customize: factory options (autoRefreshToken/persistSession) only when
 * the application has its own session store; defaults are correct for
 * stateless backend usage.
 */

import { Global, Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { SupabaseService } from './supabase.service';
import { SUPABASE_CLIENT, SUPABASE_ADMIN_CLIENT } from './supabase.tokens';

export { SUPABASE_CLIENT, SUPABASE_ADMIN_CLIENT };

@Global()
@Module({
  imports: [ConfigModule],
  providers: [
    {
      provide: SUPABASE_CLIENT,
      inject: [ConfigService],
      useFactory: (config: ConfigService): SupabaseClient => {
        const url = config.getOrThrow<string>('SUPABASE_URL');
        const anonKey = config.getOrThrow<string>('SUPABASE_ANON_KEY');
        return createClient(url, anonKey, {
          auth: { persistSession: false, autoRefreshToken: false },
        });
      },
    },
    {
      provide: SUPABASE_ADMIN_CLIENT,
      inject: [ConfigService],
      useFactory: (config: ConfigService): SupabaseClient | null => {
        const url = config.get<string>('SUPABASE_URL');
        const serviceKey = config.get<string>('SUPABASE_SERVICE_ROLE_KEY');
        if (!url || !serviceKey) return null;
        return createClient(url, serviceKey, {
          auth: { persistSession: false, autoRefreshToken: false },
        });
      },
    },
    SupabaseService,
  ],
  exports: [SUPABASE_CLIENT, SUPABASE_ADMIN_CLIENT, SupabaseService],
})
export class SupabaseModule {}
