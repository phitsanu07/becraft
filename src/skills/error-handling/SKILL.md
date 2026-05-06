---
name: error-handling
description: >
  Standard error handling for backend. RFC 7807 Problem Details, NestJS
  exception filters, retry, idempotency, graceful shutdown.
related_skills:
  - api-design
  - observability
  - testing-pyramid
---

# Error Handling Skill

Production-grade error handling for NestJS.

---

## 🎯 Core Principles

1. **One error format everywhere** — RFC 7807 Problem Details
2. **No stack traces in responses** — log server-side, return user-safe messages
3. **No catch-all `try/catch`** — let framework handle unknown errors
4. **Validate at boundaries** — API input, external responses
5. **Retry with backoff** — for transient errors only
6. **Idempotency for retry-safe operations** — POST/PUT with side effects

---

## 📋 RFC 7807 Problem Details Format

```json
{
  "type": "https://example.com/probs/validation",
  "title": "Validation Failed",
  "status": 422,
  "detail": "One or more fields are invalid",
  "instance": "/api/v1/users",
  "errors": [
    { "field": "email", "message": "must be a valid email" },
    { "field": "password", "message": "minimum 8 characters" }
  ],
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Required Fields
- `type` — URI identifying error type (canonical link)
- `title` — short human-readable summary
- `status` — HTTP status code (matches response status)
- `detail` — human-readable explanation
- `instance` — URI of specific occurrence

### Optional Extensions
- `errors[]` — field-level validation errors
- `requestId` — correlation ID for support
- `retryAfter` — seconds (rate limit, maintenance)

---

## 🛡️ Global Exception Filter

```typescript
// src/common/filters/all-exceptions.filter.ts
import {
  ExceptionFilter, Catch, ArgumentsHost,
  HttpException, HttpStatus, Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { Prisma } from '@prisma/client';

interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  errors?: Array<{ field: string; message: string }>;
  requestId?: string;
  retryAfter?: number;
}

const PROBLEM_BASE = process.env.PROBLEM_BASE_URL || 'https://example.com/probs';

@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  private readonly logger = new Logger(AllExceptionsFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const res = ctx.getResponse<Response>();
    const req = ctx.getRequest<Request>();
    const requestId = (req as any).id;

    const problem = this.buildProblem(exception, req.url, requestId);

    // Log server-side (with full stack)
    if (problem.status >= 500) {
      this.logger.error({ err: exception, requestId, problem }, 'Server error');
    } else if (problem.status >= 400) {
      this.logger.warn({ problem, requestId }, 'Client error');
    }

    res
      .status(problem.status)
      .header('Content-Type', 'application/problem+json')
      .json(problem);
  }

  private buildProblem(exception: unknown, instance: string, requestId?: string): ProblemDetails {
    // NestJS HttpException
    if (exception instanceof HttpException) {
      const response = exception.getResponse();
      const status = exception.getStatus();

      if (typeof response === 'object' && response !== null) {
        const r = response as any;

        // Validation errors from class-validator
        if (Array.isArray(r.message)) {
          return {
            type: `${PROBLEM_BASE}/validation`,
            title: 'Validation Failed',
            status,
            detail: 'One or more fields are invalid',
            instance,
            errors: this.parseValidationErrors(r.message),
            requestId,
          };
        }

        return {
          type: r.type || `${PROBLEM_BASE}/${this.statusSlug(status)}`,
          title: r.title || r.error || this.defaultTitle(status),
          status,
          detail: r.detail || r.message || 'An error occurred',
          instance,
          ...(r.errors && { errors: r.errors }),
          requestId,
        };
      }

      return {
        type: `${PROBLEM_BASE}/${this.statusSlug(status)}`,
        title: this.defaultTitle(status),
        status,
        detail: typeof response === 'string' ? response : 'An error occurred',
        instance,
        requestId,
      };
    }

    // Prisma errors
    if (exception instanceof Prisma.PrismaClientKnownRequestError) {
      return this.handlePrismaError(exception, instance, requestId);
    }

    // Unknown / unhandled
    return {
      type: `${PROBLEM_BASE}/internal-error`,
      title: 'Internal Server Error',
      status: 500,
      detail: 'An unexpected error occurred',
      instance,
      requestId,
    };
  }

  private handlePrismaError(
    err: Prisma.PrismaClientKnownRequestError,
    instance: string,
    requestId?: string,
  ): ProblemDetails {
    switch (err.code) {
      case 'P2002': // Unique constraint
        return {
          type: `${PROBLEM_BASE}/conflict`,
          title: 'Resource Conflict',
          status: 409,
          detail: `A record with this ${(err.meta?.target as string[])?.join(', ') || 'value'} already exists`,
          instance,
          requestId,
        };
      case 'P2025': // Not found
        return {
          type: `${PROBLEM_BASE}/not-found`,
          title: 'Not Found',
          status: 404,
          detail: 'The requested resource was not found',
          instance,
          requestId,
        };
      default:
        return {
          type: `${PROBLEM_BASE}/database-error`,
          title: 'Database Error',
          status: 500,
          detail: 'A database error occurred',
          instance,
          requestId,
        };
    }
  }

  private parseValidationErrors(messages: string[]): Array<{ field: string; message: string }> {
    return messages.map((m) => {
      const match = m.match(/^([^.\s]+)\s+(.+)$/);
      return match ? { field: match[1], message: match[2] } : { field: 'unknown', message: m };
    });
  }

  private statusSlug(status: number): string {
    return ({
      400: 'bad-request',
      401: 'unauthorized',
      403: 'forbidden',
      404: 'not-found',
      409: 'conflict',
      422: 'validation',
      429: 'rate-limit',
      500: 'internal-error',
    })[status] || `error-${status}`;
  }

  private defaultTitle(status: number): string {
    return HttpStatus[status]?.replace(/_/g, ' ') || 'Error';
  }
}
```

### Register Globally

```typescript
// src/main.ts
app.useGlobalFilters(new AllExceptionsFilter());
```

---

## 🎯 Throwing Exceptions Properly

### Use NestJS Built-ins

```typescript
import {
  BadRequestException,
  UnauthorizedException,
  ForbiddenException,
  NotFoundException,
  ConflictException,
  UnprocessableEntityException,
} from '@nestjs/common';

// Simple message
throw new NotFoundException('User not found');

// With problem details extension
throw new ConflictException({
  type: 'https://example.com/probs/duplicate-email',
  title: 'Email Already Exists',
  detail: `An account with email ${email} already exists`,
  errors: [{ field: 'email', message: 'already taken' }],
});
```

### Custom Domain Exceptions

```typescript
// src/common/exceptions/insufficient-balance.exception.ts
import { HttpException, HttpStatus } from '@nestjs/common';

export class InsufficientBalanceException extends HttpException {
  constructor(currentBalance: number, requiredAmount: number) {
    super(
      {
        type: 'https://example.com/probs/insufficient-balance',
        title: 'Insufficient Balance',
        detail: `Required ${requiredAmount}, available ${currentBalance}`,
        errors: [{ field: 'balance', message: 'insufficient funds' }],
      },
      HttpStatus.UNPROCESSABLE_ENTITY,
    );
  }
}

// Usage
if (account.balance < amount) {
  throw new InsufficientBalanceException(account.balance, amount);
}
```

---

## 🔄 Retry Patterns

### Exponential Backoff

```typescript
// src/common/utils/retry.ts
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts?: number;
    initialDelayMs?: number;
    maxDelayMs?: number;
    factor?: number;
    retryIf?: (err: Error) => boolean;
  } = {},
): Promise<T> {
  const {
    maxAttempts = 3,
    initialDelayMs = 100,
    maxDelayMs = 10000,
    factor = 2,
    retryIf = () => true,
  } = options;

  let attempt = 0;
  let delay = initialDelayMs;

  while (true) {
    try {
      return await fn();
    } catch (err) {
      attempt++;
      if (attempt >= maxAttempts || !retryIf(err as Error)) throw err;

      // Add jitter to prevent thundering herd
      const jitter = Math.random() * 100;
      await new Promise((r) => setTimeout(r, delay + jitter));
      delay = Math.min(delay * factor, maxDelayMs);
    }
  }
}

// Usage — retry only on network errors
const data = await retryWithBackoff(
  () => httpClient.get('/external-api'),
  {
    maxAttempts: 3,
    retryIf: (err: any) => err.code === 'ECONNRESET' || err.code === 'ETIMEDOUT',
  },
);
```

### Circuit Breaker (opossum)

```typescript
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(
  () => externalApi.fetch(),
  {
    timeout: 3000,
    errorThresholdPercentage: 50,
    resetTimeout: 30000,
  },
);

breaker.fallback(() => ({ source: 'cache', data: lastKnownGood }));

// Usage
const result = await breaker.fire();
```

---

## 🔁 Idempotency for Side Effects

```typescript
@Post()
async createOrder(
  @Headers('idempotency-key') idempotencyKey: string,
  @Body() dto: CreateOrderDto,
) {
  if (!idempotencyKey) {
    throw new BadRequestException({
      type: 'https://example.com/probs/missing-header',
      title: 'Missing Idempotency-Key',
      detail: 'POST /orders requires Idempotency-Key header',
    });
  }

  const cacheKey = `idempotency:orders:${idempotencyKey}`;
  const cached = await this.redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const order = await this.ordersService.create(dto);

  // Cache for 24 hours
  await this.redis.set(cacheKey, JSON.stringify(order), 'EX', 86400);

  return order;
}
```

**Recovery from partial failures:** Idempotency key allows safe retries without creating duplicate orders/charges.

---

## 🛑 Graceful Shutdown

```typescript
// src/main.ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable shutdown hooks
  app.enableShutdownHooks();

  // Wait up to 30s for in-flight requests to complete
  await app.listen(3000);
}

// In services
@Injectable()
export class OrdersService implements OnApplicationShutdown {
  async onApplicationShutdown(signal: string) {
    this.logger.log({ signal }, 'Shutting down OrdersService');
    // Drain queue
    // Close connections
    // Final flush
  }
}
```

### Shutdown Sequence
```
SIGTERM received
    ↓
Stop accepting new connections
    ↓
Wait for in-flight requests (max 30s)
    ↓
Close DB connections
    ↓
Close Redis connections
    ↓
Flush logs
    ↓
Exit 0
```

---

## 📨 Dead Letter Queue (BullMQ)

```typescript
// src/queues/orders.processor.ts
@Processor('orders')
export class OrdersProcessor {
  @Process('charge')
  async handleCharge(job: Job<ChargeData>) {
    try {
      await this.paymentService.charge(job.data);
    } catch (err) {
      // BullMQ retries automatically (configured in module)
      // After max retries → goes to failed queue
      this.logger.error({ err, jobId: job.id }, 'Charge failed');
      throw err;
    }
  }

  @OnQueueFailed()
  async onFailed(job: Job, error: Error) {
    if (job.attemptsMade >= job.opts.attempts!) {
      // Final failure → send to DLQ for manual review
      await this.deadLetterQueue.add('failed-charge', {
        originalJob: job.data,
        error: error.message,
        failedAt: new Date(),
      });

      // Alert team
      await this.alertService.notify('charge-failed', { jobId: job.id });
    }
  }
}
```

---

## ❌ Anti-Patterns

### ❌ Catch-All try/catch
```
WRONG:
try { ... } catch (err) {
  return { error: 'something went wrong' };
}
WHY: Hides bugs, returns 200 for errors

RIGHT:
Let exceptions propagate to AllExceptionsFilter.
Only catch specific errors you know how to handle.
```

### ❌ Stack Traces in Responses
```
WRONG:
{ error: err.stack }  ← exposes internals
RIGHT:
Log stack server-side; return RFC 7807 (no stack)
```

### ❌ Inconsistent Error Shapes
```
WRONG:
endpoint A: { error: "..." }
endpoint B: { message: "...", code: "..." }
endpoint C: { errors: [...] }

RIGHT:
Global filter ensures RFC 7807 everywhere
```

### ❌ Using HTTP 200 for Errors
```
WRONG:
HTTP 200
{ success: false, error: "user not found" }

RIGHT:
HTTP 404
{ type, title: "Not Found", status: 404, ... }
```

### ❌ Retry on All Errors
```
WRONG: retry on 4xx (validation errors)
RIGHT: retry only on 5xx, network errors, timeout
       Use retryIf() predicate to filter
```

### ❌ No Idempotency on POST
```
WRONG: POST /charge processes payment
       → user double-clicks → 2 charges
RIGHT: Require Idempotency-Key header
       Cache response for 24h
```

---

## ✅ Error Handling Checklist

- [ ] Global AllExceptionsFilter registered?
- [ ] All errors return RFC 7807 format?
- [ ] No stack traces in responses?
- [ ] Validation errors include field-level details?
- [ ] Prisma errors mapped to HTTP codes?
- [ ] Custom domain exceptions for business rules?
- [ ] Retry logic only on transient errors?
- [ ] Circuit breaker on external APIs?
- [ ] Idempotency on POST/PUT side effects?
- [ ] Dead letter queue for failed jobs?
- [ ] Graceful shutdown enabled?
- [ ] Request ID in error responses?
- [ ] Errors logged server-side (with stack)?

---

*Error Handling Skill v1.0 — RFC 7807 + retry + idempotency*
