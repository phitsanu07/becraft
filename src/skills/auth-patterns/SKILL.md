---
name: auth-patterns
description: >
  Authentication & Authorization patterns. JWT (access + refresh), OAuth,
  RBAC, RLS, rate limiting, idempotency, password hashing.
related_skills:
  - api-design
  - error-handling
  - schema-design
---

# Auth Patterns Skill

Production-grade auth for NestJS using Passport + JWT + Redis.

---

## 🎯 Core Principles

1. **JWT for stateless API** — access token short-lived (15m), refresh long-lived (7d)
2. **Refresh token rotation** — issue new refresh on every use, invalidate old
3. **bcrypt with work factor 12+** — slow on purpose
4. **Rate limit /auth/* aggressively** — 5 req/min by default
5. **HttpOnly cookies for refresh** — prevent XSS theft
6. **RBAC via guards + decorators** — `@Roles('ADMIN')`
7. **No password in logs ever** — Pino redaction

---

## 🔐 JWT Strategy (Passport)

### Setup

```typescript
// src/auth/strategies/jwt.strategy.ts
import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy, ExtractJwt } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';

export interface JwtPayload {
  sub: string;       // user.id
  email: string;
  role: string;
  type: 'access' | 'refresh';
  iat?: number;
  exp?: number;
}

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(config: ConfigService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: config.getOrThrow<string>('JWT_SECRET'),
    });
  }

  async validate(payload: JwtPayload) {
    if (payload.type !== 'access') throw new UnauthorizedException();
    return { id: payload.sub, email: payload.email, role: payload.role };
  }
}
```

### Tokens Service

```typescript
// src/auth/tokens.service.ts
@Injectable()
export class TokensService {
  constructor(
    private jwt: JwtService,
    @Inject(REDIS) private redis: Redis,
    private config: ConfigService,
  ) {}

  async issuePair(user: User): Promise<{ accessToken: string; refreshToken: string }> {
    const basePayload = { sub: user.id, email: user.email, role: user.role };

    const accessToken = await this.jwt.signAsync(
      { ...basePayload, type: 'access' },
      { expiresIn: '15m', secret: this.config.get('JWT_SECRET') },
    );

    const refreshTokenId = randomUUID();
    const refreshToken = await this.jwt.signAsync(
      { ...basePayload, type: 'refresh', jti: refreshTokenId },
      { expiresIn: '7d', secret: this.config.get('JWT_REFRESH_SECRET') },
    );

    // Store refresh token ID in Redis (for revocation)
    await this.redis.set(
      `refresh:${user.id}:${refreshTokenId}`,
      '1',
      'EX', 7 * 24 * 60 * 60,
    );

    return { accessToken, refreshToken };
  }

  async rotateRefresh(oldToken: string): Promise<{ accessToken: string; refreshToken: string }> {
    const payload = await this.jwt.verifyAsync<JwtPayload & { jti: string }>(oldToken, {
      secret: this.config.get('JWT_REFRESH_SECRET'),
    });

    if (payload.type !== 'refresh') throw new UnauthorizedException();

    // Verify token exists in Redis (not revoked)
    const exists = await this.redis.get(`refresh:${payload.sub}:${payload.jti}`);
    if (!exists) throw new UnauthorizedException('Refresh token revoked');

    // Revoke old token
    await this.redis.del(`refresh:${payload.sub}:${payload.jti}`);

    // Issue new pair
    return this.issuePair({ id: payload.sub, email: payload.email, role: payload.role } as User);
  }

  async revokeAll(userId: string): Promise<void> {
    const keys = await this.redis.keys(`refresh:${userId}:*`);
    if (keys.length) await this.redis.del(...keys);
  }
}
```

---

## 🔑 Password Hashing

```typescript
// src/auth/auth.service.ts
import * as bcrypt from 'bcrypt';

const BCRYPT_ROUNDS = 12;

async hashPassword(plain: string): Promise<string> {
  return bcrypt.hash(plain, BCRYPT_ROUNDS);
}

async verifyPassword(plain: string, hash: string): Promise<boolean> {
  return bcrypt.compare(plain, hash);
}

// Constant-time comparison for tokens
import { timingSafeEqual } from 'crypto';

function safeCompare(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  return timingSafeEqual(Buffer.from(a), Buffer.from(b));
}
```

**bcrypt limit:** Truncate password to 72 chars before hashing (or use argon2 for unlimited):

```typescript
@MaxLength(72)  // bcrypt truncates at 72 bytes
password: string;
```

---

## 🛡️ Guards

### JwtAuthGuard (default protection)

```typescript
// src/common/guards/jwt-auth.guard.ts
import { Injectable, ExecutionContext } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { Reflector } from '@nestjs/core';
import { IS_PUBLIC_KEY } from '../decorators/public.decorator';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  constructor(private reflector: Reflector) { super(); }

  canActivate(context: ExecutionContext) {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;
    return super.canActivate(context);
  }
}
```

### Apply Globally

```typescript
// src/app.module.ts
import { APP_GUARD } from '@nestjs/core';

providers: [
  { provide: APP_GUARD, useClass: JwtAuthGuard },
]
// Now ALL routes require auth unless @Public()
```

### @Public() Decorator (opt-out)

```typescript
// src/common/decorators/public.decorator.ts
import { SetMetadata } from '@nestjs/common';
export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);

// Usage:
@Public()
@Post('login')
async login() {}
```

### RolesGuard (RBAC)

```typescript
// src/common/guards/roles.guard.ts
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { ROLES_KEY } from '../decorators/roles.decorator';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (!requiredRoles?.length) return true;

    const { user } = context.switchToHttp().getRequest();
    if (!user) throw new ForbiddenException();

    if (!requiredRoles.includes(user.role)) {
      throw new ForbiddenException(
        `Required role: ${requiredRoles.join(' or ')}`,
      );
    }
    return true;
  }
}
```

```typescript
// src/common/decorators/roles.decorator.ts
import { SetMetadata } from '@nestjs/common';
export const ROLES_KEY = 'roles';
export const Roles = (...roles: string[]) => SetMetadata(ROLES_KEY, roles);

// Usage:
@Roles('ADMIN')
@Get('users')
async listAll() {}
```

---

## 🚦 Rate Limiting

### Setup with @nestjs/throttler

```typescript
// src/app.module.ts
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { APP_GUARD } from '@nestjs/core';

ThrottlerModule.forRoot([
  { name: 'short',  ttl: 1000,  limit: 10  },  // 10 req/sec
  { name: 'medium', ttl: 60000, limit: 100 },  // 100 req/min
  { name: 'long',   ttl: 3600000, limit: 1000 },// 1000 req/hr
]),

providers: [
  { provide: APP_GUARD, useClass: ThrottlerGuard },
]
```

### Aggressive on /auth

```typescript
// src/auth/auth.controller.ts
import { Throttle, SkipThrottle } from '@nestjs/throttler';

@Controller('auth')
export class AuthController {
  @Post('login')
  @Throttle({ medium: { ttl: 60000, limit: 5 } })  // 5/min
  async login() {}

  @Post('register')
  @Throttle({ long: { ttl: 3600000, limit: 10 } })  // 10/hr per IP
  async register() {}
}
```

---

## 🔁 Refresh Token Flow

### Endpoint

```typescript
@Public()
@Post('refresh')
@HttpCode(200)
@ApiOperation({ summary: 'Refresh access token' })
async refresh(
  @Body() dto: RefreshTokenDto,
  @Res({ passthrough: true }) res: Response,
) {
  const tokens = await this.tokensService.rotateRefresh(dto.refreshToken);

  // Set refresh token as HttpOnly cookie (recommended)
  res.cookie('refreshToken', tokens.refreshToken, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000,
    path: '/api/v1/auth/refresh',
  });

  return { accessToken: tokens.accessToken };
}
```

### Logout (revoke all)

```typescript
@Post('logout')
@HttpCode(204)
async logout(@CurrentUser() user: User) {
  await this.tokensService.revokeAll(user.id);
}
```

---

## 🌐 OAuth (Google example)

```typescript
// src/auth/strategies/google.strategy.ts
import { PassportStrategy } from '@nestjs/passport';
import { Strategy, VerifyCallback } from 'passport-google-oauth20';

@Injectable()
export class GoogleStrategy extends PassportStrategy(Strategy, 'google') {
  constructor(config: ConfigService) {
    super({
      clientID: config.getOrThrow('GOOGLE_CLIENT_ID'),
      clientSecret: config.getOrThrow('GOOGLE_CLIENT_SECRET'),
      callbackURL: config.getOrThrow('GOOGLE_CALLBACK_URL'),
      scope: ['email', 'profile'],
    });
  }

  async validate(
    accessToken: string,
    refreshToken: string,
    profile: any,
    done: VerifyCallback,
  ) {
    const { id, emails, name } = profile;
    done(null, {
      googleId: id,
      email: emails[0].value,
      name: `${name.givenName} ${name.familyName}`,
    });
  }
}
```

---

## 🔒 Idempotency Pattern

```typescript
// src/common/middleware/idempotency.middleware.ts
@Injectable()
export class IdempotencyMiddleware implements NestMiddleware {
  constructor(@Inject(REDIS) private redis: Redis) {}

  async use(req: Request, res: Response, next: NextFunction) {
    if (!['POST', 'PUT'].includes(req.method)) return next();

    const key = req.headers['idempotency-key'] as string;
    if (!key) return next();

    const cached = await this.redis.get(`idempotency:${key}`);
    if (cached) {
      const { status, body } = JSON.parse(cached);
      return res.status(status).json(body);
    }

    // Capture response
    const originalJson = res.json.bind(res);
    res.json = (body: any) => {
      this.redis.set(
        `idempotency:${key}`,
        JSON.stringify({ status: res.statusCode, body }),
        'EX', 86400,
      );
      return originalJson(body);
    };

    next();
  }
}
```

---

## ❌ Anti-Patterns

### ❌ Storing JWT in localStorage
```
WRONG: localStorage.setItem('token', jwt) → XSS-vulnerable
RIGHT: Use HttpOnly cookies for refresh, memory only for access
```

### ❌ Long-Lived Access Tokens
```
WRONG: 30-day access tokens (no revocation possible)
RIGHT: 15-min access + 7-day refresh with rotation
```

### ❌ Same Secret for Access + Refresh
```
WRONG: process.env.JWT_SECRET for both
RIGHT: JWT_SECRET + JWT_REFRESH_SECRET (separate)
```

### ❌ Logging Passwords
```
WRONG: logger.info({ user: req.body })  // includes password!
RIGHT: pino redact: ['password', '*.password', 'authorization']
```

### ❌ No Rate Limit on /login
```
WRONG: Unlimited login attempts → brute force
RIGHT: 5 req/min per IP minimum
```

### ❌ MD5/SHA1 for Passwords
```
WRONG: hash = md5(password) → instant crack
RIGHT: bcrypt with rounds ≥ 12, or argon2
```

### ❌ Returning Different Errors for Email vs Password
```
WRONG:
  email not found → 404 "User not found"
  wrong password → 401 "Wrong password"
RIGHT: Both return 401 "Invalid credentials" (no enumeration)
```

---

## ✅ Auth Checklist

- [ ] JWT_SECRET set (32+ random bytes)?
- [ ] JWT_REFRESH_SECRET set (separate)?
- [ ] bcrypt rounds ≥ 12?
- [ ] @Throttle on /auth/login (5/min)?
- [ ] @Throttle on /auth/register (10/hr)?
- [ ] Global JwtAuthGuard registered?
- [ ] @Public() on login/register/health?
- [ ] @Roles() on admin endpoints?
- [ ] Refresh token rotation implemented?
- [ ] Refresh tokens in Redis (revocable)?
- [ ] Pino redact list includes password/authorization?
- [ ] HTTPS in production (cookie secure: true)?
- [ ] Idempotency middleware on POST/PUT?

---

## 🎯 Environment Variables

```env
# .env.example
JWT_SECRET=                    # 32+ random bytes
JWT_REFRESH_SECRET=            # different from above
JWT_ACCESS_TTL=15m
JWT_REFRESH_TTL=7d

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_CALLBACK_URL=

REDIS_URL=redis://localhost:6379
BCRYPT_ROUNDS=12
```

Generate secrets:
```bash
openssl rand -base64 32
```

---

*Auth Patterns Skill v1.0 — JWT + Passport + Redis*
