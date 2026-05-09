/**
 * Snippet: SupabaseService for NestJS
 *
 * Used by: bootstrap-agent (when stack = Supabase JS)
 * Materializes to: src/modules/supabase/supabase.service.ts
 *
 * Provides 2 clients:
 *   - client: anon key (respects RLS) — use for normal operations
 *   - admin: service-role key (bypasses RLS) — use carefully, log every use
 *
 * Pairs with:
 *   - supabase-tokens.ts  → src/modules/supabase/supabase.tokens.ts
 *   - supabase-module.ts  → src/modules/supabase/supabase.module.ts
 *
 * Customize: usually no changes needed. Add helpers (ping, etc.) here.
 */

import { Inject, Injectable, Logger } from '@nestjs/common';
import { SupabaseClient } from '@supabase/supabase-js';
import { SUPABASE_CLIENT, SUPABASE_ADMIN_CLIENT } from './supabase.tokens';

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
