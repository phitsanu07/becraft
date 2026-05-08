/**
 * Snippet: SupabaseService for NestJS
 *
 * Used by: bootstrap-agent (when stack = Supabase JS)
 * Provides 2 clients:
 *   - client: anon key (respects RLS) — use for normal operations
 *   - admin: service-role key (bypasses RLS) — use carefully
 *
 * Customize: usually no changes needed
 */

import { Global, Module, Injectable, Inject, Logger } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

export const SUPABASE_CLIENT = 'SUPABASE_CLIENT';
export const SUPABASE_ADMIN_CLIENT = 'SUPABASE_ADMIN_CLIENT';

@Injectable()
export class SupabaseService {
  private readonly logger = new Logger(SupabaseService.name);

  constructor(
    @Inject(SUPABASE_CLIENT) public readonly client: SupabaseClient,
    @Inject(SUPABASE_ADMIN_CLIENT) public readonly admin: SupabaseClient | null,
  ) {
    if (!this.admin) {
      this.logger.warn(
        'SUPABASE_SERVICE_ROLE_KEY not set — admin client unavailable',
      );
    }
  }

  /** Health check — pings Supabase. */
  async ping(): Promise<boolean> {
    try {
      const { error } = await this.client.auth.getSession();
      return !error;
    } catch (err) {
      this.logger.error({ err }, 'Supabase ping failed');
      return false;
    }
  }
}

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
