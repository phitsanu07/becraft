---
name: observability
description: >
  Production observability for backend. Structured logs (Pino), Prometheus
  metrics, OpenTelemetry tracing, health checks, what NOT to log.
related_skills:
  - error-handling
  - api-design
---

# Observability Skill

Production-grade observability baseline for NestJS.

---

## 🎯 The Three Pillars

```
┌──────────────────────────────────────────────┐
│  LOGS         METRICS         TRACES         │
│  (events)     (numbers)       (request path) │
│                                              │
│  Pino         Prometheus      OpenTelemetry  │
│  (JSON)       (RED method)    (distributed)  │
└──────────────────────────────────────────────┘
```

**Required for every backend:**
- ✅ Structured JSON logs with request-id
- ✅ /metrics endpoint (Prometheus format)
- ✅ /health/live + /health/ready endpoints
- ❌ Tracing optional (add when distributed)
- ❌ Sentry optional (add when scaling)

---

## 📝 Structured Logging (Pino)

### Setup

```typescript
// src/main.ts
import { LoggerModule } from 'nestjs-pino';

LoggerModule.forRoot({
  pinoHttp: {
    transport: process.env.NODE_ENV !== 'production' ? {
      target: 'pino-pretty',
      options: { colorize: true, singleLine: true, translateTime: 'SYS:HH:MM:ss.l' },
    } : undefined,

    level: process.env.LOG_LEVEL || 'info',

    // CRITICAL: Redact sensitive data
    redact: {
      paths: [
        'req.headers.authorization',
        'req.headers.cookie',
        'req.body.password',
        'req.body.passwordHash',
        '*.password',
        '*.passwordHash',
        '*.token',
        '*.refreshToken',
        '*.accessToken',
        '*.creditCard',
        '*.ssn',
      ],
      censor: '[REDACTED]',
    },

    // Generate request ID
    genReqId: (req) => req.headers['x-request-id'] || randomUUID(),

    customProps: (req) => ({
      requestId: req.id,
      userId: (req as any).user?.id,
    }),

    serializers: {
      req: (req) => ({
        id: req.id,
        method: req.method,
        url: req.url,
        userAgent: req.headers['user-agent'],
      }),
      res: (res) => ({
        statusCode: res.statusCode,
      }),
    },
  },
});
```

### Log Levels

| Level | Use |
|-------|-----|
| `fatal` | App is going to crash |
| `error` | Operation failed (user-facing 5xx) |
| `warn` | Recoverable issue (retry, fallback) |
| `info` | Normal events (request, response, lifecycle) |
| `debug` | Detailed flow (off in prod) |
| `trace` | Very verbose (rarely on) |

### Usage in Service

```typescript
import { Logger } from 'nestjs-pino';

@Injectable()
export class OrdersService {
  constructor(private logger: Logger) {}

  async create(dto: CreateOrderDto, userId: string) {
    this.logger.log({ userId, items: dto.items.length }, 'Creating order');

    try {
      const order = await this.prisma.order.create({ data: ... });
      this.logger.log({ userId, orderId: order.id }, 'Order created');
      return order;
    } catch (error) {
      this.logger.error({ err: error, userId, dto }, 'Order creation failed');
      throw error;
    }
  }
}
```

### What to Log

**ALWAYS log:**
- Request received (method, url, userId)
- Response sent (status, duration)
- Errors (with stack)
- Auth events (login, logout, failed attempts)
- Business events (order placed, payment processed)
- External API calls (start, response, error)

**NEVER log:**
- ❌ Passwords / hashes
- ❌ Auth tokens / cookies
- ❌ Full request bodies (might contain PII)
- ❌ Credit cards / SSN / tax IDs
- ❌ Personal addresses, phone numbers (unless required for audit)
- ❌ Encrypted secrets

---

## 📊 Metrics (Prometheus)

### Setup with @willsoto/nestjs-prometheus

```typescript
// src/observability/metrics.module.ts
import { PrometheusModule } from '@willsoto/nestjs-prometheus';
import { makeCounterProvider, makeHistogramProvider } from '@willsoto/nestjs-prometheus';

@Module({
  imports: [
    PrometheusModule.register({
      defaultMetrics: { enabled: true },  // Node.js process metrics
      defaultLabels: {
        app: 'becraft-api',
        env: process.env.NODE_ENV,
      },
    }),
  ],
  providers: [
    makeCounterProvider({
      name: 'http_requests_total',
      help: 'Total HTTP requests',
      labelNames: ['method', 'route', 'status'],
    }),
    makeHistogramProvider({
      name: 'http_request_duration_seconds',
      help: 'HTTP request duration',
      labelNames: ['method', 'route', 'status'],
      buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
    }),
  ],
  exports: ['PROM_METRIC_HTTP_REQUESTS_TOTAL', 'PROM_METRIC_HTTP_REQUEST_DURATION_SECONDS'],
})
export class MetricsModule {}
```

### RED Method

For every HTTP service, track:
- **R**ate — requests per second
- **E**rrors — error rate (4xx, 5xx)
- **D**uration — p50, p95, p99

### Metrics Interceptor

```typescript
// src/common/interceptors/metrics.interceptor.ts
@Injectable()
export class MetricsInterceptor implements NestInterceptor {
  constructor(
    @Inject('PROM_METRIC_HTTP_REQUESTS_TOTAL') private requests: Counter,
    @Inject('PROM_METRIC_HTTP_REQUEST_DURATION_SECONDS') private duration: Histogram,
  ) {}

  intercept(ctx: ExecutionContext, next: CallHandler): Observable<any> {
    const req = ctx.switchToHttp().getRequest();
    const start = Date.now();
    const route = req.route?.path ?? req.url;

    return next.handle().pipe(
      tap({
        next: () => {
          const status = ctx.switchToHttp().getResponse().statusCode;
          this.requests.inc({ method: req.method, route, status });
          this.duration.observe(
            { method: req.method, route, status },
            (Date.now() - start) / 1000,
          );
        },
        error: (err) => {
          const status = err.status || 500;
          this.requests.inc({ method: req.method, route, status });
          this.duration.observe(
            { method: req.method, route, status },
            (Date.now() - start) / 1000,
          );
        },
      }),
    );
  }
}
```

### Custom Business Metrics

```typescript
@Injectable()
export class OrdersService {
  @InjectMetric('orders_total') private ordersCounter: Counter;
  @InjectMetric('orders_revenue_total') private revenueCounter: Counter;

  async create(dto: CreateOrderDto) {
    const order = await this.prisma.order.create({ data: ... });
    this.ordersCounter.inc({ status: order.status });
    this.revenueCounter.inc({ currency: order.currency }, order.totalAmount);
    return order;
  }
}
```

---

## 🏥 Health Checks

### @nestjs/terminus

```typescript
// src/health/health.module.ts
import { TerminusModule } from '@nestjs/terminus';

@Module({
  imports: [TerminusModule],
  controllers: [HealthController],
})
export class HealthModule {}
```

```typescript
// src/health/health.controller.ts
import { Controller, Get } from '@nestjs/common';
import {
  HealthCheck,
  HealthCheckService,
  PrismaHealthIndicator,
  HealthIndicatorResult,
  HealthIndicator,
} from '@nestjs/terminus';
import { Public } from '../common/decorators/public.decorator';
import { Inject, Injectable } from '@nestjs/common';
import { Redis } from 'ioredis';
import { REDIS } from '../redis/redis.module';

@Injectable()
class RedisHealthIndicator extends HealthIndicator {
  constructor(@Inject(REDIS) private redis: Redis) { super(); }
  async ping(key: string): Promise<HealthIndicatorResult> {
    const ok = (await this.redis.ping()) === 'PONG';
    return this.getStatus(key, ok);
  }
}

@Controller('health')
@Public()
export class HealthController {
  constructor(
    private health: HealthCheckService,
    private prismaHealth: PrismaHealthIndicator,
    private prisma: PrismaService,
    private redis: RedisHealthIndicator,
  ) {}

  @Get()
  @HealthCheck()
  check() {
    return this.health.check([
      () => this.prismaHealth.pingCheck('db', this.prisma),
      () => this.redis.ping('redis'),
    ]);
  }

  @Get('live')
  @HealthCheck()
  liveness() {
    // No external dependencies — process is alive
    return { status: 'ok', timestamp: new Date().toISOString() };
  }

  @Get('ready')
  @HealthCheck()
  readiness() {
    // Check all dependencies — ready to serve traffic
    return this.health.check([
      () => this.prismaHealth.pingCheck('db', this.prisma),
      () => this.redis.ping('redis'),
    ]);
  }
}
```

### Liveness vs Readiness

| Endpoint | Purpose | Returns 503 When |
|----------|---------|------------------|
| `/health/live` | Process alive | Process about to die (rare) |
| `/health/ready` | Ready to serve | DB/Redis down, deps unhealthy |

**Kubernetes:**
- `livenessProbe`: `/health/live` (restart if fail)
- `readinessProbe`: `/health/ready` (remove from LB if fail)

---

## 🔍 Distributed Tracing (OpenTelemetry)

### Setup (optional but recommended for microservices)

```typescript
// src/tracing.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'becraft-api',
    [SemanticResourceAttributes.SERVICE_VERSION]: process.env.APP_VERSION || '0.1.0',
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
process.on('SIGTERM', () => sdk.shutdown());
```

Import at the top of `main.ts`:
```typescript
// main.ts (FIRST line)
import './tracing';

// Rest of bootstrap...
```

---

## 🚨 Error Tracking (Sentry)

```typescript
// src/main.ts
import * as Sentry from '@sentry/node';

if (process.env.SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.NODE_ENV,
    release: process.env.APP_VERSION,
    tracesSampleRate: 0.1,
    integrations: [
      new Sentry.Integrations.Http({ tracing: true }),
      new Sentry.Integrations.Postgres(),
    ],
    beforeSend(event) {
      // Strip PII before sending
      if (event.request?.cookies) delete event.request.cookies;
      return event;
    },
  });
}
```

---

## 🆔 Request ID Propagation

```typescript
// src/common/middleware/request-id.middleware.ts
import { randomUUID } from 'crypto';

@Injectable()
export class RequestIdMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    const id = (req.headers['x-request-id'] as string) || randomUUID();
    (req as any).id = id;
    res.setHeader('x-request-id', id);
    next();
  }
}

// Apply globally
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(RequestIdMiddleware).forRoutes('*');
  }
}
```

**Forward to external services:**
```typescript
this.httpService.get('https://api.external.com/data', {
  headers: { 'x-request-id': req.id },
});
```

---

## ❌ Anti-Patterns

### ❌ console.log in Production
```
WRONG: console.log('user logged in')
RIGHT: this.logger.log({ userId }, 'User logged in')
```

### ❌ Logging Full Request Body
```
WRONG: logger.info({ body: req.body }, 'request')
       → password leaks!
RIGHT: Use redact list in Pino config
```

### ❌ String Concatenation in Logs
```
WRONG: logger.info(`User ${userId} did ${action}`)
       → not parseable, slower
RIGHT: logger.info({ userId, action }, 'user did action')
       → JSON, queryable
```

### ❌ Missing Request ID
```
WRONG: Logs without correlation ID
       → can't trace user's full request flow
RIGHT: x-request-id middleware + customProps
```

### ❌ /health Returns 200 Always
```
WRONG: { status: 'ok' } even if DB is down
RIGHT: Check actual deps; return 503 if any fail
```

### ❌ Same Endpoint for Live + Ready
```
WRONG: /health checks DB → liveness fails when DB blip
       → process restart → bad
RIGHT: /health/live (process only) + /health/ready (deps)
```

---

## ✅ Observability Checklist

- [ ] Pino configured with redact list?
- [ ] Request-id middleware applied globally?
- [ ] /health endpoint exists?
- [ ] /health/live (no deps)?
- [ ] /health/ready (checks DB + Redis)?
- [ ] /metrics endpoint (Prometheus)?
- [ ] Default metrics enabled?
- [ ] Custom counters for business events?
- [ ] Histogram for HTTP duration?
- [ ] Sentry initialized (production only)?
- [ ] OpenTelemetry started before NestJS bootstrap (if used)?
- [ ] Log level configurable via env?
- [ ] No `console.log` in src/?

---

## 🎯 Environment Variables

```env
LOG_LEVEL=info
NODE_ENV=production

# Optional
SENTRY_DSN=
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
APP_VERSION=0.1.0
```

---

*Observability Skill v1.0 — Logs + Metrics + Traces*
