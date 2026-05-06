---
name: testing-pyramid
description: >
  Test pyramid for backend. Unit + Integration (Testcontainers) + Contract tests.
  Jest, Supertest, factories, isolation strategies, coverage targets.
related_skills:
  - error-handling
  - api-design
---

# Testing Pyramid Skill

Production-grade test strategy for NestJS using Jest + Supertest + Testcontainers.

---

## 🎯 The Pyramid

```
              ┌──────────┐
              │ Contract │  ← few (vs OpenAPI)
              │   ~5%    │
              └──────────┘
            ┌──────────────┐
            │ Integration  │  ← some (real DB)
            │     ~25%     │
            └──────────────┘
        ┌──────────────────────┐
        │       Unit           │  ← many (services, mocked deps)
        │       ~70%           │
        └──────────────────────┘
```

**Coverage targets:**
- Overall: 80%+
- Critical paths (auth, payments, billing): 100%
- Repos & services with logic: 90%+
- Trivial getters/setters: skip

---

## 🧪 Unit Tests

**Test pure functions and services with mocked dependencies.**

### Service Test Template

```typescript
// src/users/users.service.spec.ts
import { Test } from '@nestjs/testing';
import { UsersService } from './users.service';
import { PrismaService } from '../prisma/prisma.service';
import { ConflictException, NotFoundException } from '@nestjs/common';

describe('UsersService', () => {
  let service: UsersService;
  let prisma: jest.Mocked<PrismaService>;

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: PrismaService,
          useValue: {
            user: {
              create: jest.fn(),
              findUnique: jest.fn(),
              findMany: jest.fn(),
              update: jest.fn(),
            },
          },
        },
      ],
    }).compile();

    service = module.get(UsersService);
    prisma = module.get(PrismaService);
  });

  describe('create', () => {
    it('creates user with hashed password', async () => {
      const dto = { email: 'a@b.com', password: 'SecurePass123', name: 'A' };
      prisma.user.findUnique.mockResolvedValue(null);
      prisma.user.create.mockResolvedValue({ id: 'uuid', ...dto, passwordHash: 'hashed' } as any);

      const result = await service.create(dto);

      expect(result.email).toBe('a@b.com');
      expect((result as any).passwordHash).toBeUndefined(); // sanitized
      expect(prisma.user.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          email: 'a@b.com',
          passwordHash: expect.any(String),
        }),
      });
    });

    it('throws ConflictException if email exists', async () => {
      prisma.user.findUnique.mockResolvedValue({ id: 'existing' } as any);
      await expect(
        service.create({ email: 'a@b.com', password: 'x', name: 'A' }),
      ).rejects.toThrow(ConflictException);
    });
  });

  describe('findById', () => {
    it('returns user when found', async () => {
      prisma.user.findUnique.mockResolvedValue({ id: 'uuid', email: 'a@b.com' } as any);
      const result = await service.findById('uuid');
      expect(result.id).toBe('uuid');
    });

    it('throws NotFoundException when missing', async () => {
      prisma.user.findUnique.mockResolvedValue(null);
      await expect(service.findById('missing')).rejects.toThrow(NotFoundException);
    });
  });
});
```

### Test Patterns

| Pattern | Use |
|---------|-----|
| AAA (Arrange-Act-Assert) | Standard structure |
| `describe.each([...])` | Test multiple cases |
| `it.each([...])` | Same |
| `beforeEach` | Reset mocks |
| `afterEach(() => jest.restoreAllMocks())` | Cleanup |

---

## 🔬 Integration Tests with Testcontainers

**Test against REAL PostgreSQL container — not mocks.**

### Setup

```typescript
// test/setup-integration.ts
import { PostgreSqlContainer, StartedPostgreSqlContainer } from '@testcontainers/postgresql';
import { execSync } from 'child_process';

let container: StartedPostgreSqlContainer;

export async function setupTestDatabase(): Promise<string> {
  container = await new PostgreSqlContainer('postgres:16-alpine')
    .withDatabase('test')
    .withUsername('test')
    .withPassword('test')
    .start();

  const url = container.getConnectionUri();

  // Run migrations
  execSync('npx prisma migrate deploy', { env: { ...process.env, DATABASE_URL: url } });

  return url;
}

export async function teardownTestDatabase() {
  await container?.stop();
}
```

### E2E Test Template

```typescript
// test/users.e2e-spec.ts
import { Test } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { setupTestDatabase, teardownTestDatabase } from './setup-integration';
import { PrismaService } from '../src/prisma/prisma.service';

describe('Users (e2e)', () => {
  let app: INestApplication;
  let prisma: PrismaService;
  let accessToken: string;

  beforeAll(async () => {
    process.env.DATABASE_URL = await setupTestDatabase();

    const module = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = module.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ transform: true, whitelist: true }));
    await app.init();

    prisma = app.get(PrismaService);
  });

  afterAll(async () => {
    await app.close();
    await teardownTestDatabase();
  });

  beforeEach(async () => {
    // Clean DB between tests
    await prisma.$transaction([
      prisma.user.deleteMany(),
    ]);
  });

  describe('POST /api/v1/users', () => {
    it('creates user (201)', async () => {
      const res = await request(app.getHttpServer())
        .post('/api/v1/users')
        .set('Idempotency-Key', 'test-key-1')
        .send({
          email: 'test@example.com',
          password: 'SecurePass123',
          name: 'Test User',
        })
        .expect(201);

      expect(res.body.id).toMatch(/^[0-9a-f-]{36}$/);
      expect(res.body.email).toBe('test@example.com');
      expect(res.body.passwordHash).toBeUndefined();
    });

    it('rejects duplicate email (409)', async () => {
      await prisma.user.create({
        data: { email: 'dup@example.com', passwordHash: 'x', name: 'X' },
      });

      const res = await request(app.getHttpServer())
        .post('/api/v1/users')
        .set('Idempotency-Key', 'test-key-2')
        .send({ email: 'dup@example.com', password: 'SecurePass123', name: 'Y' })
        .expect(409);

      expect(res.body.type).toContain('conflict');
    });

    it('rejects weak password (422)', async () => {
      const res = await request(app.getHttpServer())
        .post('/api/v1/users')
        .set('Idempotency-Key', 'test-key-3')
        .send({ email: 't@e.com', password: 'weak', name: 'X' })
        .expect(422);

      expect(res.body.errors).toContainEqual(
        expect.objectContaining({ field: 'password' }),
      );
    });
  });

  describe('GET /api/v1/users/:id (auth)', () => {
    it('returns 401 without token', async () => {
      await request(app.getHttpServer())
        .get('/api/v1/users/00000000-0000-0000-0000-000000000000')
        .expect(401);
    });

    it('returns user with valid token', async () => {
      const user = await prisma.user.create({
        data: { email: 'auth@e.com', passwordHash: 'x', name: 'A' },
      });
      // Get token via login endpoint (test the full flow)
      // ... or use TokensService directly

      const res = await request(app.getHttpServer())
        .get(`/api/v1/users/${user.id}`)
        .set('Authorization', `Bearer ${accessToken}`)
        .expect(200);

      expect(res.body.id).toBe(user.id);
    });
  });
});
```

---

## 📜 Contract Tests

**Verify API matches OpenAPI spec.**

### Approach 1: Generated Test from OpenAPI

```typescript
// test/contract/users.contract-spec.ts
import * as fs from 'fs';
import * as Ajv from 'ajv';
import * as request from 'supertest';

const openApi = JSON.parse(fs.readFileSync('openapi.json', 'utf8'));
const ajv = new Ajv();

describe('Contract: POST /api/v1/users', () => {
  it('response matches OpenAPI schema', async () => {
    const res = await request(app)
      .post('/api/v1/users')
      .send(validPayload);

    const schema = openApi.paths['/api/v1/users'].post.responses['201'].content['application/json'].schema;
    const validate = ajv.compile(schema);

    expect(validate(res.body)).toBe(true);
    if (!validate(res.body)) console.error(validate.errors);
  });
});
```

### Approach 2: Schemathesis (Property-based)

```bash
# Auto-generate fuzz tests from OpenAPI
npx schemathesis run http://localhost:3000/openapi.json \
  --auth admin:admin \
  --checks all
```

---

## 🏭 Test Data Factories

**Avoid fixtures — use factories for flexibility.**

```typescript
// test/factories/user.factory.ts
import { faker } from '@faker-js/faker';
import { User } from '@prisma/client';

export function userFactory(overrides: Partial<User> = {}): Omit<User, 'id'> {
  return {
    email: faker.internet.email(),
    passwordHash: '$2b$12$dummy',  // pre-hashed for speed
    name: faker.person.fullName(),
    role: 'USER',
    emailVerifiedAt: null,
    createdAt: new Date(),
    updatedAt: new Date(),
    deletedAt: null,
    ...overrides,
  };
}

// Usage in test
beforeEach(async () => {
  await prisma.user.create({ data: userFactory({ email: 'specific@test.com' }) });
});
```

---

## 🧹 Database Isolation Strategies

### Strategy 1: Truncate Before Each Test (default)
```typescript
beforeEach(async () => {
  // Order matters — child tables first
  await prisma.$transaction([
    prisma.post.deleteMany(),
    prisma.user.deleteMany(),
  ]);
});
```

**Pros:** Simple, isolated
**Cons:** Slow if many tables

### Strategy 2: Transaction Rollback (faster)
```typescript
beforeEach(async () => {
  await prisma.$executeRaw`BEGIN`;
});

afterEach(async () => {
  await prisma.$executeRaw`ROLLBACK`;
});
```

**Pros:** Fast, automatic cleanup
**Cons:** Doesn't work with Prisma's connection pooling

### Strategy 3: Schema-per-test (parallel)
```typescript
beforeEach(async () => {
  const schemaName = `test_${Date.now()}_${Math.random().toString(36).slice(2)}`;
  await prisma.$executeRaw`CREATE SCHEMA ${schemaName}`;
  // Run migrations on new schema
});
```

**Pros:** Parallel test execution
**Cons:** Complex setup

**Recommendation:** Start with Strategy 1, switch to 3 if test suite > 5 minutes.

---

## 🚀 Performance / Load Testing

### k6 Example

```javascript
// load-tests/users-create.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },   // ramp up
    { duration: '2m',  target: 50 },   // sustain
    { duration: '30s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% under 500ms
    http_req_failed:   ['rate<0.01'], // <1% errors
  },
};

export default function () {
  const payload = JSON.stringify({
    email: `user${__VU}-${__ITER}@test.com`,
    password: 'SecurePass123',
    name: `User ${__VU}`,
  });

  const res = http.post('http://localhost:3000/api/v1/users', payload, {
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': `${__VU}-${__ITER}`,
    },
  });

  check(res, {
    'status 201': (r) => r.status === 201,
    'has id': (r) => r.json('id') !== undefined,
  });

  sleep(1);
}
```

---

## ❌ Anti-Patterns

### ❌ Mocking the Database
```
WRONG: jest.mock(PrismaService)
       → tests pass but production breaks
RIGHT: Use Testcontainers for integration tests
       Mock only at service boundaries (external APIs)
```

### ❌ Sleep / setTimeout in Tests
```
WRONG: await new Promise(r => setTimeout(r, 1000))
RIGHT: await waitFor(() => expect(...).toBeTruthy())
       or use jest.useFakeTimers()
```

### ❌ Shared State Between Tests
```
WRONG: const sharedUser = createUser(); // outside beforeEach
       describe('A', () => { test uses sharedUser })
       describe('B', () => { test mutates sharedUser })
RIGHT: Each test creates its own data via factory
```

### ❌ Testing Implementation Details
```
WRONG: expect(prisma.user.create).toHaveBeenCalledWith(...)
       → breaks on refactor
RIGHT: Test behavior: expect(result.email).toBe('...')
```

### ❌ One Massive Test
```
WRONG: it('does CRUD', async () => {
         create(); read(); update(); delete();
       })
RIGHT: Separate it() per behavior
```

---

## ✅ Test Checklist

Before merging:
- [ ] Unit tests for services (mocked deps)?
- [ ] Integration tests for controllers (real DB)?
- [ ] At least one happy path per endpoint?
- [ ] Error cases tested (4xx, 5xx)?
- [ ] Edge cases (empty, null, boundary)?
- [ ] Auth tested (with + without token)?
- [ ] Validation tested (422 responses)?
- [ ] Coverage ≥ 80%?
- [ ] No `setTimeout` / sleep?
- [ ] No shared state between tests?
- [ ] Tests use factories, not fixtures?

---

## 🎯 Auto-Fix Loop

Test runner agent should:

```
1. Run tests
2. Test fails? → Analyze error
3. Auto-fixable? → Fix immediately:
   - Selector mismatch → use data-testid
   - Async timing → add waitFor
   - Type error → fix import
4. Run again
5. Repeat (max 5 attempts)
6. Report SUCCESS only

User NEVER sees test failures during loop.
```

---

*Testing Pyramid Skill v1.0 — Jest + Supertest + Testcontainers*
