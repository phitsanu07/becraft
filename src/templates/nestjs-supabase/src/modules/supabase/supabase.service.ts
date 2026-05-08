import { Inject, Injectable, Logger } from '@nestjs/common';
import { SupabaseClient } from '@supabase/supabase-js';
import { SUPABASE_CLIENT, SUPABASE_ADMIN_CLIENT } from './supabase.module';

/**
 * SupabaseService — wrapper around Supabase JS client.
 *
 * Use `client` for normal operations (anon key, respects RLS).
 * Use `admin` for service-role operations (bypasses RLS — careful!).
 *
 * Example:
 *   const { data, error } = await this.supabase.client
 *     .from('products')
 *     .select('*')
 *     .eq('is_active', true);
 */
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

  /**
   * Health check — pings Supabase REST endpoint.
   */
  async ping(): Promise<boolean> {
    try {
      const { error } = await this.client.auth.getSession();
      // Network reachable if no thrown error; null session is fine
      return !error;
    } catch (err) {
      this.logger.error({ err }, 'Supabase ping failed');
      return false;
    }
  }
}
