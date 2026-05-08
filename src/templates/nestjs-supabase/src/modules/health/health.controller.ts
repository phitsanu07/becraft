import { Controller, Get, HealthCheckError } from '@nestjs/common';
import {
  HealthCheck,
  HealthCheckService,
  HealthIndicatorResult,
} from '@nestjs/terminus';
import { ApiTags } from '@nestjs/swagger';
import { Public } from '../../common/decorators/public.decorator';
import { SupabaseService } from '../supabase/supabase.service';

@Controller('health')
@ApiTags('health')
@Public()
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private supabase: SupabaseService,
  ) {}

  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      async (): Promise<HealthIndicatorResult> => {
        const ok = await this.supabase.ping();
        if (!ok) {
          throw new HealthCheckError('Supabase ping failed', { supabase: { status: 'down' } });
        }
        return { supabase: { status: 'up' } };
      },
    ]);
  }

  @Get('live')
  liveness() {
    return { status: 'ok', timestamp: new Date().toISOString() };
  }

  @Get('ready')
  @HealthCheck()
  readiness() {
    return this.health.check([
      async (): Promise<HealthIndicatorResult> => {
        const ok = await this.supabase.ping();
        if (!ok) {
          throw new HealthCheckError('Supabase ping failed', { supabase: { status: 'down' } });
        }
        return { supabase: { status: 'up' } };
      },
    ]);
  }
}
