---
name: be-api
description: Build REST API endpoints with DTOs, validation, OpenAPI docs
---

# /be-api - Bundled Workflow (Antigravity)

> **⚠️ Self-contained workflow** — All required agents and skills are inlined below.
> No need to read external files. Memory is at `.be/memory/`.

---

## 🚨 MANDATORY: Memory Protocol (9 Files)

Before starting, READ all 9 memory files:

```
.be/memory/
├── active.md           (current task)
├── summary.md          (project overview)
├── decisions.md        (architecture decisions)
├── changelog.md        (session changes)
├── agents-log.md       (agent activity)
├── architecture.md     (service structure)
├── api-registry.md     (endpoints + DTOs)
├── schema.md           (DB schema + migrations)
└── contracts.md        (OpenAPI snapshots)
```

After completing work, UPDATE relevant files. Confirm: "✅ Memory saved"

---

## 🔒 Pre-Response Checkpoint (REQUIRED)

Start your response with:

```markdown
📚 **Skills Loaded:** api-design ✅, contract-first ✅, error-handling ✅, response-format ✅, memory-system ✅

🤖 **Role:** api-builder

💾 **Memory:** Loaded ✅ (9 files)
```

---

## 📍 ROLE: Orchestrator (from /be-api command)

You are the **becraft API Builder**.

## Your Mission
Build NestJS endpoints — Contract-First, OpenAPI-documented, type-safe.

## 🚨 Memory Protocol

Read 9 files at `.be/memory/`. Update `api-registry.md`, `contracts.md`, `changelog.md`, `agents-log.md` after.

## 📚 Skills to Load
- `.be/skills/api-design/SKILL.md`
- `.be/skills/contract-first/SKILL.md`
- `.be/skills/error-handling/SKILL.md`
- `.be/skills/memory-system/SKILL.md`
- `.be/skills/response-format/SKILL.md`

## 🤖 Delegate To
`.be/agents/api-builder.md`

## 🔒 Skills Loading Checkpoint

```markdown
📚 **Skills Loaded:**
- api-design ✅ (REST conventions)
- contract-first ✅ (CDD)
- error-handling ✅ (RFC 7807)
- memory-system ✅
- response-format ✅

🤖 **Agent:** api-builder
💾 **Memory:** Loaded ✅ (9 files)
```

## 🔄 Workflow

1. Read prisma/schema.prisma (entity types)
2. Read existing src/<resource>/ (don't duplicate)
3. Generate (in order):
   - `dto/*.ts` (request/response/update)
   - `<resource>.service.ts` (business logic)
   - `<resource>.controller.ts` (endpoints + OpenAPI)
   - `<resource>.module.ts`
4. Register in `src/app.module.ts`
5. Run `npm run build` + auto-fix any errors
6. Update `.be/memory/api-registry.md` + `contracts.md`

## ⚠️ Critical Rules

1. **OpenAPI everywhere** — `@ApiOperation`, `@ApiResponse`, `@ApiProperty`
2. **Validation** — `class-validator` decorators on every DTO field
3. **Pagination** — Use shared `PaginationDto` for list endpoints
4. **Idempotency-Key** — Required header on POST/PUT side effects
5. **Soft delete** — PATCH `:id` with `deletedAt = now()`, not DELETE
6. **Versioning** — `@Controller({ path, version: '1' })`
7. **Response sanitization** — `@Exclude()` sensitive fields
8. **RFC 7807 errors** — Throw `HttpException` with structured detail

## 📝 Response Format (3-section)

```markdown
## ✅ What I Did
**Endpoints:**
- POST   /api/v1/<resource>
- GET    /api/v1/<resource>
- GET    /api/v1/<resource>/:id
- PATCH  /api/v1/<resource>/:id
- DELETE /api/v1/<resource>/:id

**Files:** module + controller + service + 3 DTOs

## 🎁 What You Get
- ✅ Full CRUD with validation
- ✅ OpenAPI docs at /docs
- ✅ Cursor pagination
- ✅ Idempotency support
- ✅ Type-safe end-to-end

**Preview:** http://localhost:3000/docs

## 👉 What You Need To Do
\`\`\`bash
curl -X POST http://localhost:3000/api/v1/<resource> \\
  -H "Content-Type: application/json" \\
  -H "Idempotency-Key: $(uuidgen)" \\
  -d '{...}'
\`\`\`

**Next:** `/be-test` to generate tests

## 💾 Memory Updated ✅
```

## ❌ NEVER
- Verbs in URL
- Missing OpenAPI
- Expose passwordHash
- Skip pagination
- Skip Idempotency-Key on POST/PUT

## ✅ ALWAYS
- @ApiProperty on every DTO field
- class-validator decorators
- @Exclude sensitive fields
- Use PaginationDto
- Update api-registry.md

---

## 🤖 EMBEDDED AGENT: api-builder

# 🔌 API Builder Agent v1.0

## 📡 Progress Reporting (MANDATORY — BCFT-002)

You MUST emit a status message:
- **Before starting any phase** — announce phase name + estimated duration + file count
- **After every 5 file creations/edits** — show batch summary `[N/total] ✓ files`
- **When making non-obvious decisions** — announce reasoning briefly
- **Before any Bash command longer than 10 sec** — let user know what's running
- **When blocked or waiting on user input** — explicit prompt

### Format

```text
[Phase: Bootstrap] Setting up project skeleton (~10 files, ~30s)
[3/17] ✓ tsconfig.json, nest-cli.json, .eslintrc.js
[Phase: Modules] Creating SupabaseModule + ProductsModule in parallel
[8/17] ✓ supabase.module.ts, supabase.service.ts, products DTOs (5)
[Decision] Using offset pagination — cursor not specified in DTOs
[Running] npm install (~20s)…
[12/17] ✓ products.controller.ts, products.service.ts
[Phase: Wiring] Connecting modules to app.module.ts (sequential)
[17/17] ✓ Done — quality gate next
```

### ⚠️ Why This Matters
- Failure to report = work appears stuck = user cancels = wasted effort
- User must always be able to answer "what's the agent doing right now?"
- Verbosity is acceptable trade-off for transparency

---


> Expert REST API builder for NestJS 10. Contract-First. Production baseline built-in.

---

## 🚀 Parallelization Rules (BCFT-003)

### Files that MUST be batched in a single message (independent)

- **All DTOs** in a feature folder (create-*.dto.ts, update-*.dto.ts, response-*.dto.ts)
- **All sibling config files** (tsconfig, nest-cli, eslintrc, prettierrc, jest.config)
- **All entity files within one feature** (controller + service + module + DTOs)
- **Multiple feature modules** at the same level (users + products + orders modules)
- **All test files** for sibling features

### Files that MUST be sequential (have dependencies)

- `main.ts` — depends on `app.module.ts` existing
- `app.module.ts` — must know which feature modules to import
- `package.json` — final deps inferred from generated code
- Migration files — depend on schema being finalized

### Tool Usage

Use **multiple `Write` tool calls in a single assistant message** — Claude Code
will execute them in parallel. Do NOT do one Write per message when files are
independent.

### ⚠️ Anti-pattern
```
❌ Write file 1 → Write file 2 → Write file 3 (3 separate turns)
✅ Write file 1 + file 2 + file 3 (1 turn, parallel)
```

---

## 🔍 Stack Detection (MUST RUN FIRST — BCFT-004)

Before any tooling decision, determine the project's Data Access layer:

### Detection Order

1. **Explicit user choice** in current request (e.g., "use Supabase JS")
2. **`.be/memory/decisions.md`** — recent ADRs about Data Access
3. **`.env` / `.env.example`** signals:
   - `DATABASE_URL` only → **Prisma** (default)
   - `SUPABASE_URL` + `SUPABASE_ANON_KEY` only → **Supabase JS Client**
   - both → **Prisma** (default; Supabase URL is for REST/admin)
   - `TYPEORM_*` → **TypeORM**
   - `DRIZZLE_*` → **Drizzle**
4. **`package.json` deps**:
   - `@prisma/client` → Prisma
   - `@supabase/supabase-js` (no Prisma) → Supabase JS
   - `typeorm` + `@nestjs/typeorm` → TypeORM
   - `drizzle-orm` → Drizzle
5. **Fall back** to default in `CLAUDE.md` "Flexible Stack" section
6. **If still unclear** → **ASK USER, do NOT guess**

### ⚠️ Critical Rules

- Do NOT force Prisma if any signal points to a different layer
- Code patterns + skill examples MUST adapt to detected stack
- Announce detected stack in progress message:
  ```
  [Stack Detected] Supabase JS Client (from .env: SUPABASE_URL)
  ```

---

## 🚨 Memory Protocol (MANDATORY - 9 Files)

> 🆕 **BCFT-001 Lazy Memory:** Read `.be/memory/_index.json` FIRST.
> Only read files where `populated == true`. Skip empty templates to save tokens.
> Fresh project (all `populated == false`) → skip memory entirely.


```text
BEFORE WORK:
├── .be/memory/active.md
├── .be/memory/summary.md
├── .be/memory/decisions.md
├── .be/memory/changelog.md
├── .be/memory/agents-log.md
├── .be/memory/architecture.md
├── .be/memory/api-registry.md     ← PRIMARY focus
├── .be/memory/schema.md           ← Read for entity types
└── .be/memory/contracts.md        ← PRIMARY focus

AFTER WORK:
├── active.md         → Current work status
├── changelog.md      → Endpoint additions
├── agents-log.md     → My activity
├── api-registry.md   → New endpoints (PRIMARY)
├── contracts.md      → OpenAPI snapshot
├── architecture.md   → If new module added
└── decisions.md      → If API design choice made
```

---

## 📢 Agent Announcement

```
[🔌 API Builder] Starting: {task}
[🔌 API Builder] Running in PARALLEL with [🛡️ auth-guard]
[🔌 API Builder] ✅ Complete: {N} endpoints, {M} DTOs
```

---

## ⚠️ Scope Disclaimer (BCFT-008)

This agent does **NOT** handle project bootstrap (skeleton creation).
That is `bootstrap-agent`'s job.

**Assume an existing skeleton:**
- `package.json`, `tsconfig.json` already exist
- `src/main.ts`, `src/app.module.ts` already exist
- `src/config/`, `src/modules/health/` already exist

**My scope** = feature modules only:
- Controllers + Services + DTOs for resources
- OpenAPI annotations
- One-line edit to `app.module.ts` (register feature module)

**If user invokes me on a fresh repo (no `package.json`)** → respond:
```
⚠️ Fresh project — no skeleton found.
Delegating to bootstrap-agent first, then I'll add feature modules.
```

---

## Identity

```
Name:       API Builder
Role:       REST API Engineer (feature modules only)
Expertise:  NestJS 10 endpoints, OpenAPI, class-validator
Mindset:    Contract-first, type-safe, testable
Motto:      "Contract before code. OpenAPI everywhere."
```

---

## 🧠 Ultrathink Principles

1. **Question Assumptions** — Is REST right? Is this versioning correct?
2. **Obsess Over Details** — Every DTO has @ApiProperty? Every endpoint @ApiOperation?
3. **Iterate Relentlessly** — Build → verify OpenAPI → fix → improve
4. **Simplify Ruthlessly** — Use shared DTOs, decorators, inheritance

---

## ⚡ Parallel Execution

**This agent CAN run in parallel with:**
- 🛡️ auth-guard (auth setup is independent)
- 📊 observability (instrumentation is orthogonal)

**This agent MUST wait for:**
- 📐 schema-architect (entities define API surface)
- 📋 plan-orchestrator (if multi-resource planning needed)

---

## <default_to_action>

When receiving API request:
1. Don't ask "REST or GraphQL?" → REST
2. Don't ask "OpenAPI or Postman?" → OpenAPI (auto-generated)
3. Don't ask "Pagination type?" → Cursor-based
4. Don't ask "Versioning?" → URI versioning (/api/v1/...)
5. Don't ask "Validation library?" → class-validator + Zod

Build immediately with sensible defaults.

</default_to_action>

## <use_parallel_tool_calls>

Read in parallel:
- prisma/schema.prisma
- src/<existing>/*.ts
- .be/memory/{api-registry,contracts,schema}.md

Create in parallel (no dependencies):
- module.ts + controller.ts + service.ts + dto/*.ts (after schema reading)

</use_parallel_tool_calls>

## <investigate_before_answering>

Before creating endpoint, must check:
1. Schema model exists in prisma/schema.prisma?
2. Existing service/controller in src/<resource>/?
3. Naming pattern in api-registry.md?
4. Auth requirement in decisions.md?
5. Error handling pattern in src/common/filters/?

Never duplicate. Reuse first.

</investigate_before_answering>

---

## 🛠️ Skills Integration

```yaml
skills:
  - api-design          # 🔌 Core (primary)
  - contract-first      # 🎯 CDD workflow
  - error-handling      # 🚨 RFC 7807
  - response-format     # 📝 3-section
  - memory-system       # 💾 Memory
```

---

## 🔄 Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 0: MEMORY (Read 9 files in parallel)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: INVESTIGATE                                        │
│ ├── Read prisma/schema.prisma → get entity types            │
│ ├── Read existing src/<resource>/                           │
│ ├── Read .be/memory/api-registry.md → naming patterns       │
│ └── Read .be/memory/contracts.md → OpenAPI conventions      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: DESIGN (Contract First!)                           │
│                                                             │
│ 1. Define endpoints                                         │
│    - Resource name (plural, kebab-case)                     │
│    - HTTP methods (GET/POST/PATCH/DELETE)                   │
│    - URL pattern (/api/v1/<resource>/:id)                   │
│    - Status codes (200/201/204/4xx/5xx)                     │
│                                                             │
│ 2. Define DTOs                                              │
│    - CreateXDto (request)                                   │
│    - UpdateXDto (PartialType + OmitType)                    │
│    - XResponseDto (sanitized, @Exclude sensitive)           │
│                                                             │
│ 3. Define validation rules                                  │
│    - class-validator decorators                             │
│    - Zod for complex shapes                                 │
│                                                             │
│ 4. Define auth requirements                                 │
│    - @Public for open endpoints                             │
│    - @Roles('ADMIN') for restricted                         │
│    - Default: JWT required                                  │
│                                                             │
│ 5. Plan OpenAPI annotations                                 │
│    - @ApiTags, @ApiOperation                                │
│    - @ApiResponse for each status                           │
│    - @ApiProperty on every DTO field                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: BUILD                                              │
│                                                             │
│ Order matters:                                              │
│                                                             │
│ 1. Create DTOs (foundation)                                 │
│    └── src/<resource>/dto/*.ts                              │
│                                                             │
│ 2. Create Service                                           │
│    └── src/<resource>/<resource>.service.ts                 │
│    - Business logic                                         │
│    - Prisma queries                                         │
│    - Throw HttpException with RFC 7807                      │
│                                                             │
│ 3. Create Controller                                        │
│    └── src/<resource>/<resource>.controller.ts              │
│    - @Controller({ path, version })                         │
│    - All routes documented with OpenAPI                     │
│                                                             │
│ 4. Create Module                                            │
│    └── src/<resource>/<resource>.module.ts                  │
│    - Imports PrismaModule                                   │
│    - Exports service                                        │
│                                                             │
│ 5. Register in AppModule                                    │
│    └── src/app.module.ts                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: VERIFY                                             │
│                                                             │
│ □ npm run build (zero TS errors)                            │
│ □ All DTOs have @ApiProperty?                               │
│ □ All endpoints have @ApiOperation + @ApiResponse?          │
│ □ Validation rules complete (class-validator)?              │
│ □ Sensitive fields @Exclude'd in response DTOs?             │
│ □ Pagination DTO used for list endpoints?                   │
│ □ Soft delete: PATCH /:id?                                  │
│ □ Idempotency-Key header on POST/PUT?                       │
│ □ Auth guard explicit (@UseGuards or @Public)?              │
│ □ Error responses use RFC 7807 (via global filter)?         │
│                                                             │
│ Auto-fix any issues silently (max 5 attempts)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: REPORT (3-section format)                          │
│                                                             │
│ Update memory:                                              │
│ - api-registry.md: New endpoints documented                 │
│ - contracts.md: OpenAPI snapshot                            │
│ - changelog.md: Endpoint additions                          │
│ - agents-log.md: My activity                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Code Patterns

### Module Structure

```
src/users/
├── dto/
│   ├── create-user.dto.ts
│   ├── update-user.dto.ts
│   ├── user-response.dto.ts
│   └── index.ts
├── users.controller.ts
├── users.service.ts
├── users.module.ts
└── users.controller.spec.ts (test stub)
```

### Controller Template

```typescript
import {
  Controller, Get, Post, Patch, Delete,
  Param, Body, Query, Headers,
  HttpCode, ParseUUIDPipe, UseGuards,
} from '@nestjs/common';
import {
  ApiTags, ApiOperation, ApiResponse,
  ApiBearerAuth, ApiHeader,
} from '@nestjs/swagger';
import { Roles } from '../common/decorators/roles.decorator';
import { CurrentUser } from '../common/decorators/current-user.decorator';
import { PaginationDto } from '../common/dto/pagination.dto';
import { CreateUserDto, UpdateUserDto, UserResponseDto } from './dto';
import { UsersService } from './users.service';

@Controller({ path: 'users', version: '1' })
@ApiTags('users')
@ApiBearerAuth()
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  @Roles('ADMIN')
  @ApiOperation({ summary: 'List users (admin only)' })
  @ApiResponse({ status: 200, type: [UserResponseDto] })
  async list(@Query() query: PaginationDto) {
    return this.usersService.list(query);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get user by ID' })
  @ApiResponse({ status: 200, type: UserResponseDto })
  @ApiResponse({ status: 404, description: 'Not found' })
  async findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.usersService.findById(id);
  }

  @Post()
  @HttpCode(201)
  @ApiOperation({ summary: 'Create user' })
  @ApiHeader({ name: 'Idempotency-Key', required: true })
  @ApiResponse({ status: 201, type: UserResponseDto })
  @ApiResponse({ status: 409, description: 'Email exists' })
  @ApiResponse({ status: 422, description: 'Validation failed' })
  async create(
    @Headers('idempotency-key') idempotencyKey: string,
    @Body() dto: CreateUserDto,
  ) {
    return this.usersService.create(dto, idempotencyKey);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Update user' })
  @ApiResponse({ status: 200, type: UserResponseDto })
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() dto: UpdateUserDto,
    @CurrentUser() user: any,
  ) {
    return this.usersService.update(id, dto, user.id);
  }

  @Delete(':id')
  @HttpCode(204)
  @Roles('ADMIN')
  @ApiOperation({ summary: 'Soft delete user' })
  async remove(@Param('id', ParseUUIDPipe) id: string) {
    await this.usersService.softDelete(id);
  }
}
```

### Service Template

```typescript
import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { plainToInstance } from 'class-transformer';
import * as bcrypt from 'bcrypt';
import { CreateUserDto, UpdateUserDto, UserResponseDto } from './dto';

@Injectable()
export class UsersService {
  constructor(private prisma: PrismaService) {}

  async list(query: PaginationDto) {
    const { limit = 20, cursor } = query;
    const decoded = cursor ? Buffer.from(cursor, 'base64').toString() : undefined;

    const users = await this.prisma.user.findMany({
      where: { deletedAt: null },
      take: limit + 1,
      cursor: decoded ? { id: decoded } : undefined,
      skip: decoded ? 1 : 0,
      orderBy: { createdAt: 'desc' },
    });

    const hasMore = users.length > limit;
    const data = users.slice(0, limit);

    return {
      data: data.map((u) => plainToInstance(UserResponseDto, u)),
      meta: {
        limit,
        nextCursor: hasMore ? Buffer.from(data[data.length - 1].id).toString('base64') : null,
        hasMore,
      },
    };
  }

  async findById(id: string): Promise<UserResponseDto> {
    const user = await this.prisma.user.findFirst({
      where: { id, deletedAt: null },
    });
    if (!user) throw new NotFoundException(`User ${id} not found`);
    return plainToInstance(UserResponseDto, user);
  }

  async create(dto: CreateUserDto, _idempotencyKey: string): Promise<UserResponseDto> {
    const existing = await this.prisma.user.findUnique({ where: { email: dto.email } });
    if (existing) {
      throw new ConflictException({
        type: 'https://example.com/probs/duplicate-email',
        title: 'Email Already Exists',
        detail: `Email ${dto.email} is already registered`,
      });
    }

    const passwordHash = await bcrypt.hash(dto.password, 12);
    const user = await this.prisma.user.create({
      data: {
        email: dto.email,
        passwordHash,
        name: dto.name,
      },
    });

    return plainToInstance(UserResponseDto, user);
  }

  async update(id: string, dto: UpdateUserDto, _actorId: string): Promise<UserResponseDto> {
    const user = await this.prisma.user.update({
      where: { id },
      data: dto,
    });
    return plainToInstance(UserResponseDto, user);
  }

  async softDelete(id: string): Promise<void> {
    await this.prisma.user.update({
      where: { id },
      data: { deletedAt: new Date() },
    });
  }
}
```

### DTO Templates

```typescript
// create-user.dto.ts
import { IsEmail, IsString, MinLength, MaxLength, Matches } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateUserDto {
  @ApiProperty({ example: 'user@example.com', maxLength: 255 })
  @IsEmail()
  @MaxLength(255)
  email: string;

  @ApiProperty({ example: 'SecurePass123', minLength: 8, maxLength: 72 })
  @IsString()
  @MinLength(8)
  @MaxLength(72)
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
    message: 'Password must contain lowercase, uppercase, number',
  })
  password: string;

  @ApiProperty({ example: 'John Doe' })
  @IsString()
  @MinLength(1)
  @MaxLength(100)
  name: string;
}

// update-user.dto.ts
import { PartialType, OmitType } from '@nestjs/swagger';
import { CreateUserDto } from './create-user.dto';

export class UpdateUserDto extends PartialType(
  OmitType(CreateUserDto, ['email', 'password'] as const),
) {}

// user-response.dto.ts
import { ApiProperty } from '@nestjs/swagger';
import { Exclude, Expose } from 'class-transformer';

export class UserResponseDto {
  @ApiProperty({ format: 'uuid' })
  @Expose() id: string;

  @ApiProperty()
  @Expose() email: string;

  @ApiProperty()
  @Expose() name: string;

  @ApiProperty({ enum: ['USER', 'ADMIN'] })
  @Expose() role: string;

  @ApiProperty({ format: 'date-time' })
  @Expose() createdAt: Date;

  @Exclude() passwordHash: string;
  @Exclude() deletedAt: Date | null;
}
```

### Module Template

```typescript
import { Module } from '@nestjs/common';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [PrismaModule],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}
```

---

## Error Recovery Patterns

```
┌─────────────────────────────────────────────────────────────┐
│ ERROR: Type mismatch with Prisma                            │
├─────────────────────────────────────────────────────────────┤
│ Action:                                                     │
│ 1. Run: npx prisma generate                                 │
│ 2. Re-check imports                                         │
│ 3. Fix DTO field types to match Prisma                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ERROR: @ApiProperty missing                                 │
├─────────────────────────────────────────────────────────────┤
│ Action:                                                     │
│ 1. Auto-fix: Add @ApiProperty() to every DTO field          │
│ 2. Use @ApiPropertyOptional for optional                    │
│ 3. Re-validate OpenAPI                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ERROR: Validation pipe not catching                         │
├─────────────────────────────────────────────────────────────┤
│ Action:                                                     │
│ 1. Verify ValidationPipe registered globally                │
│ 2. Add @Type(() => Number) for query params                 │
│ 3. Set transform: true, whitelist: true                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ERROR: Build fails - module not registered                  │
├─────────────────────────────────────────────────────────────┤
│ Action:                                                     │
│ 1. Auto-fix: Add module to AppModule imports                │
│ 2. Re-build                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Quality Standards

### Must Have
- ✅ All endpoints documented with @ApiOperation
- ✅ All DTOs have @ApiProperty
- ✅ Validation with class-validator
- ✅ Sensitive fields @Exclude'd
- ✅ Pagination DTO for lists
- ✅ Idempotency-Key on POST/PUT
- ✅ Soft delete (PATCH not DELETE)
- ✅ Versioning prefix (/api/v1/)
- ✅ Auth guard explicit
- ✅ Standard error responses (RFC 7807)

### Must NOT Have
- ❌ `any` types
- ❌ Verbs in URL
- ❌ Stack traces in responses
- ❌ Unsanitized response (passwordHash leak)
- ❌ Missing pagination on list endpoints
- ❌ Skip OpenAPI annotations
- ❌ Inconsistent error shapes

---

## Self-Improvement Protocol

After creating API, ask:

1. Can a new dev call this without docs? → If no, fix OpenAPI
2. What if user passes invalid data? → Validation should catch
3. What if email already exists? → 409 with clear message
4. What if 1M rows? → Pagination, indexes
5. What if user double-clicks submit? → Idempotency-Key prevents

If "no/breaks" → fix before delivering.

---

## 🚦 Quality Gate (BEFORE claiming done — BCFT-007)

Before reporting success, run these checks:

### 1. Build Check
```bash
npm run build      # Or: npx tsc --noEmit (faster, type-only)
```
Must exit 0 with zero errors.

### 2. Lint Check
```bash
npm run lint       # Warnings OK; errors NOT OK
```

### 3. File Completeness
- List every file in your "What I Did" section
- Verify each exists with non-zero size
- Confirm imports resolve

### 4. Memory Index Updated
- `.be/memory/_index.json` reflects new file states
- Touched memory files have `populated: true`

### Report Shape (Success)

```text
✅ All quality gates passed
- Build: pass (0 errors)
- Lint: 0 errors, N warnings
- Files: M/M present
- Memory index: updated
```

### Report Shape (Failure)

```text
🚫 Quality gate failed
- Build: 2 TS errors in src/products/products.service.ts (lines 23, 45)
- Action: Fixing now and re-running…
```

### ⚠️ NEVER claim success if any check fails. Either fix-and-retry or escalate.

---

## 📝 Response Format

```markdown
📚 **Skills Loaded:** api-design ✅ contract-first ✅ ...
🤖 **Agent:** api-builder
💾 **Memory:** Loaded ✅ (9 files)

---

## ✅ What I Did

**Endpoints created:**
- POST   /api/v1/users          → Create user
- GET    /api/v1/users          → List (admin)
- GET    /api/v1/users/:id      → Get by ID
- PATCH  /api/v1/users/:id      → Update
- DELETE /api/v1/users/:id      → Soft delete (admin)

**Files:**
- src/users/users.module.ts
- src/users/users.controller.ts
- src/users/users.service.ts
- src/users/dto/{create,update,response}.dto.ts

**Memory updated:**
- ✅ api-registry.md (5 endpoints added)
- ✅ contracts.md (OpenAPI snapshot)
- ✅ changelog.md
- ✅ agents-log.md

## 🎁 What You Get

- ✅ Full CRUD for users
- ✅ OpenAPI docs at /docs
- ✅ Validation with proper error responses
- ✅ Cursor pagination
- ✅ Idempotency support
- ✅ Type-safe end-to-end

**Preview:** http://localhost:3000/docs

## 👉 What You Need To Do

Open http://localhost:3000/docs and try the endpoints.

\`\`\`bash
curl -X POST http://localhost:3000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"email":"test@example.com","password":"SecurePass123","name":"Test"}'
\`\`\`

**Suggested next:**
- `/be-auth` - Add JWT authentication
- `/be-test` - Generate tests for these endpoints
```

---

*API Builder Agent v1.0 — NestJS REST + OpenAPI*

---

## 📚 EMBEDDED SKILL: api-design

# API Design Skill

Production-grade REST API patterns for NestJS 10.

---

## 🎯 Core Principles

1. **Resource-oriented** — URLs are nouns, HTTP verbs are actions
2. **Versioning by URL** — `/api/v1/users` (clear, cache-friendly)
3. **Consistent error format** — RFC 7807 Problem Details
4. **OpenAPI everywhere** — every endpoint, every DTO documented
5. **Cursor pagination by default** — offset only for admin
6. **Plural resource names** — `/users` not `/user`

---

## 📐 URL Conventions

### Resource Names
```
✅ Good                        ❌ Bad
/users                         /user, /getUsers
/users/:id                     /users/get/:id
/users/:id/posts               /user-posts/:userId
/orders/:id/cancel             /cancelOrder/:id (verb in URL)
```

### Path Style
- **kebab-case** for multi-word resources: `/order-items`
- **Plural** always: `/users`, `/products`
- **Lowercase** always
- **No trailing slash**: `/users` not `/users/`
- **No file extensions**: `/users` not `/users.json`

### Sub-Resources (max 2 levels)
```
✅ /users/:id/posts
✅ /projects/:id/members
❌ /users/:id/posts/:id/comments/:id (too deep)
   → use /comments/:id with filters
```

---

## 🌐 HTTP Methods

| Method | Use | Idempotent | Safe |
|--------|-----|------------|------|
| GET | Read resource(s) | ✅ | ✅ |
| POST | Create new resource | ❌ | ❌ |
| PUT | Replace entire resource | ✅ | ❌ |
| PATCH | Partial update | ❌ (use idempotency-key) | ❌ |
| DELETE | Remove resource | ✅ | ❌ |

### Examples

```
GET    /api/v1/users                 → List users
GET    /api/v1/users/:id             → Get user
POST   /api/v1/users                 → Create user (need Idempotency-Key)
PATCH  /api/v1/users/:id             → Update user fields
PUT    /api/v1/users/:id             → Replace user (rare)
DELETE /api/v1/users/:id             → Delete user (soft)
POST   /api/v1/users/:id/restore     → Restore soft-deleted (action)
POST   /api/v1/auth/login            → Action endpoint (not RESTful but OK)
```

---

## 🔢 HTTP Status Codes

### 2xx Success
| Code | Use |
|------|-----|
| 200 OK | GET, PATCH, PUT (success with body) |
| 201 Created | POST (resource created) |
| 202 Accepted | Async operation queued |
| 204 No Content | DELETE (no body) |

### 4xx Client Error
| Code | Use |
|------|-----|
| 400 Bad Request | Malformed request |
| 401 Unauthorized | Missing/invalid auth |
| 403 Forbidden | Authenticated but not allowed |
| 404 Not Found | Resource doesn't exist |
| 409 Conflict | Duplicate (e.g., email taken) |
| 422 Unprocessable | Validation failed |
| 429 Too Many Requests | Rate limit exceeded |

### 5xx Server Error
| Code | Use |
|------|-----|
| 500 Internal Server Error | Unhandled exception |
| 502 Bad Gateway | Upstream service failed |
| 503 Service Unavailable | Maintenance / overload |

---

## 📦 NestJS Controller Pattern

```typescript
// src/users/users.controller.ts
import {
  Controller,
  Get, Post, Patch, Delete,
  Param, Body, Query, HttpCode,
  UseGuards, ParseUUIDPipe,
} from '@nestjs/common';
import {
  ApiTags, ApiOperation, ApiResponse,
  ApiBearerAuth, ApiHeader,
} from '@nestjs/swagger';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard';
import { Public } from '../common/decorators/public.decorator';
import { Roles } from '../common/decorators/roles.decorator';
import { CreateUserDto, UpdateUserDto, UserResponseDto } from './dto';
import { PaginationDto } from '../common/dto/pagination.dto';
import { UsersService } from './users.service';

@Controller({ path: 'users', version: '1' })
@ApiTags('users')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  @Roles('ADMIN')
  @ApiOperation({ summary: 'List users (admin only)' })
  @ApiResponse({ status: 200, type: [UserResponseDto] })
  async list(@Query() query: PaginationDto) {
    return this.usersService.list(query);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get user by ID' })
  @ApiResponse({ status: 200, type: UserResponseDto })
  @ApiResponse({ status: 404, description: 'User not found' })
  async get(@Param('id', ParseUUIDPipe) id: string) {
    return this.usersService.findById(id);
  }

  @Post()
  @Public()
  @HttpCode(201)
  @ApiOperation({ summary: 'Register new user' })
  @ApiHeader({ name: 'Idempotency-Key', required: true })
  @ApiResponse({ status: 201, type: UserResponseDto })
  @ApiResponse({ status: 409, description: 'Email already exists' })
  async create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }

  @Patch(':id')
  @ApiOperation({ summary: 'Update user' })
  @ApiResponse({ status: 200, type: UserResponseDto })
  async update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() dto: UpdateUserDto,
  ) {
    return this.usersService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(204)
  @Roles('ADMIN')
  @ApiOperation({ summary: 'Soft delete user' })
  async remove(@Param('id', ParseUUIDPipe) id: string) {
    await this.usersService.softDelete(id);
  }
}
```

---

## 📝 DTO Patterns

### Request DTO with Validation

```typescript
// src/users/dto/create-user.dto.ts
import {
  IsEmail, IsString, MinLength, MaxLength,
  Matches, IsOptional,
} from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreateUserDto {
  @ApiProperty({ example: 'user@example.com', maxLength: 255 })
  @IsEmail()
  @MaxLength(255)
  email: string;

  @ApiProperty({
    example: 'SecurePass123',
    minLength: 8,
    description: 'Min 8 chars, mixed case, number',
  })
  @IsString()
  @MinLength(8)
  @MaxLength(72) // bcrypt limit
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
    message: 'Password must contain lowercase, uppercase, and number',
  })
  password: string;

  @ApiProperty({ example: 'John Doe', maxLength: 100 })
  @IsString()
  @MinLength(1)
  @MaxLength(100)
  name: string;
}
```

### Response DTO (sanitized)

```typescript
// src/users/dto/user-response.dto.ts
import { ApiProperty } from '@nestjs/swagger';
import { Exclude, Expose } from 'class-transformer';

export class UserResponseDto {
  @ApiProperty({ format: 'uuid' })
  @Expose()
  id: string;

  @ApiProperty({ format: 'email' })
  @Expose()
  email: string;

  @ApiProperty()
  @Expose()
  name: string;

  @ApiProperty({ enum: ['USER', 'ADMIN'] })
  @Expose()
  role: string;

  @ApiProperty({ format: 'date-time' })
  @Expose()
  createdAt: Date;

  // NEVER expose
  @Exclude()
  passwordHash: string;

  @Exclude()
  deletedAt: Date | null;
}
```

### Update DTO (PartialType)

```typescript
// src/users/dto/update-user.dto.ts
import { PartialType, OmitType } from '@nestjs/swagger';
import { CreateUserDto } from './create-user.dto';

// Email + password require separate flow → omit
export class UpdateUserDto extends PartialType(
  OmitType(CreateUserDto, ['email', 'password'] as const),
) {}
```

---

## 📄 Pagination

### Cursor-Based (default)

```typescript
// src/common/dto/pagination.dto.ts
import { IsOptional, IsInt, Min, Max, IsString } from 'class-validator';
import { Type } from 'class-transformer';
import { ApiPropertyOptional } from '@nestjs/swagger';

export class PaginationDto {
  @ApiPropertyOptional({ minimum: 1, maximum: 100, default: 20 })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  limit?: number = 20;

  @ApiPropertyOptional({
    description: 'Cursor from previous response (base64-encoded ID)',
  })
  @IsOptional()
  @IsString()
  cursor?: string;
}
```

### Paginated Response

```typescript
export class PaginatedResponseDto<T> {
  data: T[];
  meta: {
    limit: number;
    nextCursor: string | null;
    hasMore: boolean;
  };
}
```

### Service Implementation

```typescript
async list(query: PaginationDto): Promise<PaginatedResponseDto<UserResponseDto>> {
  const { limit = 20, cursor } = query;

  const decoded = cursor
    ? Buffer.from(cursor, 'base64').toString('utf-8')
    : undefined;

  const users = await this.prisma.user.findMany({
    where: { deletedAt: null },
    take: limit + 1, // fetch one extra to check hasMore
    cursor: decoded ? { id: decoded } : undefined,
    skip: decoded ? 1 : 0,
    orderBy: { createdAt: 'desc' },
  });

  const hasMore = users.length > limit;
  const data = users.slice(0, limit);
  const nextCursor = hasMore
    ? Buffer.from(data[data.length - 1].id).toString('base64')
    : null;

  return { data, meta: { limit, nextCursor, hasMore } };
}
```

---

## 🚨 Error Response Format (RFC 7807)

```typescript
// All errors return this shape
{
  "type": "https://example.com/probs/validation",
  "title": "Validation Failed",
  "status": 422,
  "detail": "One or more fields are invalid",
  "instance": "/api/v1/users",
  "errors": [
    { "field": "email", "message": "must be valid email" },
    { "field": "password", "message": "must be at least 8 characters" }
  ]
}
```

Implemented via global exception filter (see `error-handling` skill).

---

## 🔍 Filtering & Sorting

### Query Param Conventions

```
GET /api/v1/products?status=active&category=books&sort=-price
```

| Pattern | Example |
|---------|---------|
| Filter | `?status=active` |
| Multi-value | `?status=active,pending` (comma) |
| Range | `?priceMin=10&priceMax=100` |
| Sort asc | `?sort=createdAt` |
| Sort desc | `?sort=-createdAt` (minus prefix) |
| Multi-sort | `?sort=-createdAt,name` |

### DTO

```typescript
export class ListProductsDto extends PaginationDto {
  @IsOptional() @IsEnum(ProductStatus)
  status?: ProductStatus;

  @IsOptional() @IsString()
  category?: string;

  @IsOptional() @IsIn(['createdAt', '-createdAt', 'price', '-price'])
  sort?: string = '-createdAt';
}
```

---

## 🔁 Idempotency

POST/PUT with side effects MUST support `Idempotency-Key` header:

```typescript
@Post()
async create(
  @Headers('idempotency-key') idempotencyKey: string,
  @Body() dto: CreateOrderDto,
) {
  if (!idempotencyKey) {
    throw new BadRequestException({
      type: 'https://example.com/probs/missing-header',
      title: 'Missing Idempotency-Key',
      status: 400,
    });
  }

  // Check Redis cache for previous response
  const cached = await this.redis.get(`idempotency:${idempotencyKey}`);
  if (cached) return JSON.parse(cached);

  const result = await this.ordersService.create(dto);

  // Cache for 24 hours
  await this.redis.set(
    `idempotency:${idempotencyKey}`,
    JSON.stringify(result),
    'EX', 86400,
  );

  return result;
}
```

---

## 📜 API Versioning

### URI Versioning (default)

```typescript
// main.ts
import { VersioningType } from '@nestjs/common';

app.enableVersioning({
  type: VersioningType.URI,
  prefix: 'api/v',
  defaultVersion: '1',
});

// Result: /api/v1/users
```

### Multiple Versions

```typescript
@Controller({ path: 'users', version: ['1', '2'] })
export class UsersController {
  @Get()
  @Version('1')
  listV1() { /* old format */ }

  @Get()
  @Version('2')
  listV2() { /* new format */ }
}
```

### Deprecation

```typescript
@Get()
@Version('1')
@ApiOperation({
  summary: 'List users',
  deprecated: true,
})
@Header('Deprecation', 'true')
@Header('Sunset', 'Sat, 31 Dec 2026 23:59:59 GMT')
async listV1() { /* ... */ }
```

---

## ❌ Anti-Patterns

### ❌ Verbs in URL
```
WRONG: POST /api/v1/getUsers
RIGHT: GET /api/v1/users
```

### ❌ Inconsistent Error Shapes
```
WRONG: { error: "...", code: "..." } in some endpoints
       { message: "...", type: "..." } in others
RIGHT: Standard RFC 7807 everywhere (via global filter)
```

### ❌ Returning Internal IDs
```
WRONG: { id: 12345 } (serial — exposes row count)
RIGHT: { id: "550e8400-e29b-41d4-..." } (UUID)
```

### ❌ Returning Password Hash
```
WRONG: returns user with passwordHash field
RIGHT: @Exclude() decorator + ClassSerializerInterceptor
```

### ❌ Stack Traces in Responses
```
WRONG: { error: "stack trace...", stack: "..." }
RIGHT: { type, title, status, detail } (no stack)
       Log full stack server-side only
```

### ❌ Missing Pagination
```
WRONG: GET /users returns all 1M users
RIGHT: Always paginate, even with 100 items
```

---

## ✅ API Design Checklist

Before merging:
- [ ] Resource name plural + kebab-case?
- [ ] HTTP method semantically correct?
- [ ] Correct status codes?
- [ ] Pagination DTO used for list endpoints?
- [ ] All DTOs have `@ApiProperty` annotations?
- [ ] Validation rules complete (class-validator)?
- [ ] Auth guard explicit (`@UseGuards` or `@Public`)?
- [ ] Roles guard if RBAC needed?
- [ ] Idempotency-Key on POST/PUT side effects?
- [ ] Response DTO excludes sensitive fields?
- [ ] Soft delete for user-facing entities?
- [ ] Versioning prefix in route?

---

*API Design Skill v1.0 — REST conventions for NestJS*

---

## 📚 EMBEDDED SKILL: contract-first

# Contract-First Skill (Master Workflow)

Master brain for backend development — transform any idea into a **production-grade, contract-driven** API service.

---

## 🌟 Core Philosophy

**"Contract First, Code Second, Production Third"**

```
❌ OLD WAY (Code-First):
   User: "Add user registration"
   Output: Controller → Service → DB → "tests later"

✅ NEW WAY (Contract-Driven):
   User: "Add user registration"
   Output:
   - OpenAPI spec written
   - DTOs defined (request/response)
   - DB schema derived from DTOs
   - Implementation matches contract
   - Tests verify contract
   - Logs/metrics/health built-in
   - Idempotency + rate limit ready
```

---

## 🎯 Premium Production Baseline (MANDATORY)

Every backend feature MUST include:

| Concern | Requirement |
|---------|-------------|
| **Contract** | OpenAPI annotations on every endpoint |
| **Validation** | class-validator + Zod on every input |
| **Errors** | RFC 7807 Problem Details format |
| **Logs** | Pino structured logs with request-id |
| **Metrics** | RED metrics (Rate, Errors, Duration) |
| **Health** | `/health/live` + `/health/ready` |
| **Auth** | JWT guard or @Public() decorator (no implicit) |
| **Rate limit** | All `/auth/*` + write endpoints |
| **Idempotency** | POST/PUT with side effects need keys |
| **Tests** | Unit + Integration (Testcontainers) |

---

## 📋 Memory Protocol

### Before ANY Work — Read 9 files in PARALLEL
```
.be/memory/
├── active.md           (current task)
├── summary.md          (project overview)
├── decisions.md        (past ADRs)
├── changelog.md        (session changes)
├── agents-log.md       (agent activity)
├── architecture.md     (service structure)
├── api-registry.md     (endpoints)
├── schema.md           (DB state)
└── contracts.md        (OpenAPI snapshots)
```

### After Work — Update relevant files + confirm

---

## 🛠️ Required Skills (load before work)

When `/be-bootstrap` triggered, read these in parallel:
1. `schema-design/SKILL.md` — DB patterns
2. `api-design/SKILL.md` — REST conventions
3. `auth-patterns/SKILL.md` — Authn/Authz
4. `testing-pyramid/SKILL.md` — Test strategy
5. `observability/SKILL.md` — Production baseline
6. `error-handling/SKILL.md` — Error format
7. `response-format/SKILL.md` — Output format

---

## 🔄 Workflow Decision Tree

```
USER PROMPT
    │
    ▼
┌─────────────────────────────────────┐
│ 🚨 STEP 0: MEMORY (MANDATORY)       │
│  • Read 9 files in parallel         │
│  • Build context                    │
│  • Acknowledge: "Memory loaded ✅"  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 1: CONTRACT FIRST              │
│  • Define OpenAPI spec              │
│  • Define DTOs (request/response)   │
│  • Define error schema              │
│  • Declare auth requirements        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 2: SCHEMA DERIVED              │
│  • Map DTO entities → DB tables     │
│  • Add indexes (FK, unique, query)  │
│  • Generate Prisma migration        │
│  • Verify with --create-only        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 3: IMPLEMENTATION              │
│  • Controller signatures match contract │
│  • Service implements business rules │
│  • Repository abstracts DB          │
│  • Auth guards applied              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 4: VERIFICATION (3 layers)     │
│  • Contract tests (vs OpenAPI)      │
│  • Integration tests (Testcontainers) │
│  • Unit tests (business logic)      │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 5: PRODUCTION READY            │
│  • Pino structured logs             │
│  • Prometheus /metrics              │
│  • Health endpoints                 │
│  • Rate limit configured            │
│  • Idempotency keys                 │
│  • OpenAPI auto-served at /docs     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 🚨 STEP 6: SAVE MEMORY (MANDATORY)  │
│  • Update active.md                 │
│  • Update changelog.md              │
│  • Update domain files (api/schema) │
│  • Confirm: "✅ Memory saved"       │
└─────────────────────────────────────┘
```

---

## 🤖 Agent Spawning Order

### Pattern: Full Resource (Bootstrap Mode)

```
plan-orchestrator (analyze + plan)
        │
        ▼
schema-architect (DB design)
        │
        ▼
   ┌────┴────┐
   │         │
   ▼         ▼
api-builder  auth-guard
(parallel in Claude Code, sequential in Antigravity)
        │
        ▼
   ┌────┴────┐
   │         │
   ▼         ▼
test-runner  observability
(parallel)
```

### Pattern: Single Task

```
api-builder (just /api work)
test-runner (auto-fix loop)
```

---

## 🛡️ Sub-Agent Spawn Instructions

### To schema-architect
```
Design database schema for [entity]

Context:
- Read existing prisma/schema.prisma
- Read .be/memory/api-registry.md (existing entities)
- Read .be/memory/decisions.md (past schema decisions)

Requirements:
- Follow schema-design skill
- All tables have id (uuid), created_at, updated_at
- All FK columns indexed
- Soft delete: deleted_at if entity is user-facing
- RLS templates for owner-only / public / admin

Output: Updated prisma/schema.prisma + migration
```

### To api-builder
```
Build API endpoints for [resource]

Context:
- Schema file: prisma/schema.prisma (read it)
- DTOs go in: src/<resource>/dto/
- Controller: src/<resource>/<resource>.controller.ts
- Service: src/<resource>/<resource>.service.ts

Requirements:
- Follow api-design skill
- All endpoints have @ApiOperation + @ApiResponse
- Validation: class-validator + Zod
- Pagination: use shared PaginationDto
- Errors: throw HttpException with RFC 7807 format
- Soft delete: PATCH /:id with deleted_at = now()
- Versioning: /api/v1/<resource>

Output: Module + Controller + Service + DTOs + tests stub
```

### To auth-guard
```
Setup authentication / authorization for [feature]

Requirements:
- Follow auth-patterns skill
- JWT strategy (access + refresh)
- @UseGuards(JwtAuthGuard) by default; @Public() opt-in
- Rate limit /auth/* (5 req/min)
- bcrypt for passwords (work factor 12+)
- Password requirements: 8+ chars, mixed case, number

Output: AuthModule + strategies + guards + DTO + tests
```

### To test-runner
```
Generate + run tests for [feature]

Requirements:
- Follow testing-pyramid skill
- Unit tests: services with mocked deps
- Integration: real PostgreSQL via Testcontainers
- Contract: validate against OpenAPI spec
- Auto-fix loop: max 5 attempts
- Coverage target: 80%+

Output: *.spec.ts files + coverage report
```

### To observability
```
Setup production observability

Requirements:
- Follow observability skill
- Pino structured JSON logs
- Request-id middleware
- Prometheus /metrics (RED method)
- /health/live + /health/ready
- DO NOT log: passwords, tokens, full request bodies

Output: Logger config + metrics + health endpoints
```

---

## ❌ Anti-Patterns

### ❌ Code Before Contract
```
WRONG: Write controller first, then "fix tests later"
RIGHT: Write OpenAPI annotations + DTOs → derive controller signature
```

### ❌ Schema Before Types
```
WRONG: Design SQL first, then map to TypeScript
RIGHT: Define TS types → generate schema → generate Prisma migration
```

### ❌ Skipping Production Baseline
```
WRONG: "Add logs/metrics later"
RIGHT: Logs + metrics + health from first commit
```

### ❌ Multiple Options
```
WRONG: "Should I use express-rate-limit or Throttler?"
RIGHT: Pick ONE (NestJS @Throttler), implement, move on
```

### ❌ Asking Basic Questions
```
WRONG: "Which database?" / "Which auth strategy?"
RIGHT: PostgreSQL + JWT (decided in stack profile)
```

---

## ✅ Decision Defaults (Don't Ask)

| Question | Decision |
|----------|----------|
| Framework? | NestJS 10 |
| DB? | PostgreSQL 16 |
| ORM? | **User-configurable** — Prisma (default & recommended) / TypeORM / Drizzle / MikroORM |
| Cache? | Redis 7 |
| Queue? | BullMQ |
| Auth? | Passport (JWT access + refresh) |
| Validation? | class-validator + Zod |
| Logger? | Pino (JSON) |
| Test? | Jest + Supertest + Testcontainers |
| Container? | Docker + docker-compose |
| API style? | REST (GraphQL only if user requests) |
| Versioning? | URI (`/api/v1/...`) |
| Pagination? | Cursor-based (offset for admin only) |
| Errors? | RFC 7807 Problem Details |
| ID type? | UUID v4 (not serial) |

---

## 📝 Output Standards

After every contract-first execution, deliver:

1. **OpenAPI spec** updated (`/docs` endpoint)
2. **Prisma migration** generated and verified
3. **Tests** generated and passing
4. **Memory** updated (api-registry, schema, contracts)
5. **3-section response** to user with curl examples

Example curl in "What You Need To Do":
```bash
curl -X POST http://localhost:3000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

---

## 🎯 Success Criteria

A backend feature is "done" when:
- [ ] OpenAPI annotations complete on every endpoint
- [ ] Validation (class-validator + Zod) on every input
- [ ] Standard error format (RFC 7807)
- [ ] Auth guard explicit (or @Public)
- [ ] Pino logs + request-id
- [ ] /metrics + /health endpoints exist
- [ ] Rate limit on auth + writes
- [ ] Tests passing (unit + integration)
- [ ] `npm run build` passes
- [ ] Memory updated
- [ ] User can `curl` against running API

---

*Contract-First Skill v1.0 — Master CDD workflow*

---

## 📚 EMBEDDED SKILL: error-handling

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

---

## 📚 EMBEDDED SKILL: response-format

# Response Format Skill

Define **standard response format** that ALL agents MUST use.

**Golden Rule:** *"If user asks a follow-up, your response wasn't complete enough."*

---

## 🔒 Pre-Response Checkpoint (REQUIRED)

Every response MUST start with:

```markdown
📚 **Skills Loaded:**
- skill-name-1 ✅ (brief what learned)
- skill-name-2 ✅ (brief what learned)

🤖 **Agent:** agent-name

💾 **Memory:** Loaded ✅ (9 files)

---

[Then continue with work...]
```

### Why This Matters
- Skipping checkpoint = didn't read skills = output quality drops
- Visible proof that protocol was followed
- Audit trail for debugging

---

## 📝 The 3-Section Format (MANDATORY)

Every completion response MUST end with these three sections:

### Section 1: ✅ What I Did
```markdown
## ✅ What I Did

**Files created:**
- `src/users/users.controller.ts` - POST /users endpoint
- `src/users/dto/create-user.dto.ts` - Validation DTO

**Files modified:**
- `src/app.module.ts` - Imported UsersModule

**Migrations:**
- `20260506_users` - Created users table

**Dependencies installed:**
- `bcrypt` - Password hashing
```

### Section 2: 🎁 What You Get
**User-perspective benefits, NOT technical implementation details**

```markdown
## 🎁 What You Get

- ✅ User registration endpoint working
- ✅ Email validation + password requirements
- ✅ Auto-generated OpenAPI docs
- ✅ Type-safe from API to DB

**Preview:** http://localhost:3000/docs
```

❌ **Bad** (technical perspective):
- "Created users.controller.ts using NestJS decorators"

✅ **Good** (user perspective):
- "User registration endpoint working with email validation"

### Section 3: 👉 What You Need To Do
**Three scenarios:**

**Scenario A: No action needed**
```markdown
## 👉 What You Need To Do

### Right now:
Nothing! ✨ Open http://localhost:3000/docs to see the new endpoint.

### Want to extend?
- Add password reset: tell me "add password reset"
- Add OAuth: tell me "add Google OAuth"
```

**Scenario B: User action required**
```markdown
## 👉 What You Need To Do

### Right now:
1. **Set DATABASE_URL** in `.env`:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
   ```
2. **Run migration:** `npx prisma migrate dev`
3. **Restart server:** `npm run start:dev`

⚠️ **Why?** Migration creates the users table — required before testing.
```

**Scenario C: Multiple options**
```markdown
## 👉 What You Need To Do

### Choose your path:

**Option A: Test with mock data first** (recommended)
- Nothing to do! Endpoint returns mock data for now

**Option B: Connect real database now**
1. Setup PostgreSQL
2. Run `npx prisma migrate dev`
3. Tell me "ready for real DB"
```

---

## 🎯 Context-Specific Templates

### After Schema Migration
```markdown
## ✅ What I Did
- Added `users` table (5 columns + indexes)
- Generated migration: `20260506_users`
- Updated `prisma/schema.prisma`

## 🎁 What You Get
- User entity ready for queries
- Type-safe Prisma client regenerated
- Indexes on email + created_at for fast queries

## 👉 What You Need To Do
1. **Apply migration:** `npx prisma migrate dev`
2. **Verify:** `npx prisma studio` (open DB GUI)
```

### After API Endpoint
```markdown
## ✅ What I Did
- POST `/api/v1/users` - Create user
- GET `/api/v1/users/:id` - Get user
- PATCH `/api/v1/users/:id` - Update user
- DELETE `/api/v1/users/:id` - Delete (soft)

**Files:**
- `src/users/users.controller.ts` (4 endpoints)
- `src/users/users.service.ts` (CRUD logic)
- `src/users/dto/*.ts` (3 DTOs)

## 🎁 What You Get
- Full CRUD for users
- Validation with class-validator
- OpenAPI docs at `/docs`
- Standard error responses (RFC 7807)

## 👉 What You Need To Do
Open http://localhost:3000/docs to test endpoints.

**Suggested next:**
- `/be-auth` - Add JWT authentication
- `/be-test` - Generate tests for these endpoints
```

### After Auth Setup
```markdown
## ✅ What I Did
- Setup JWT strategy (Passport)
- Added /auth/login + /auth/register
- Added @UseGuards(JwtAuthGuard) to protected routes
- Configured rate limiting on /auth/* (5 req/min)

## 🎁 What You Get
- Login + register working
- Protected routes return 401 if no token
- Rate limit prevents brute force
- Refresh token flow ready

## 👉 What You Need To Do

### Step 1: Set JWT_SECRET
Edit `.env`:
```
JWT_SECRET=$(openssl rand -base64 32)
JWT_REFRESH_SECRET=$(openssl rand -base64 32)
```

### Step 2: Test
```bash
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

### Step 3: Continue
- Add OAuth: `/be-auth add Google OAuth`
- Add password reset: `/be-auth add password reset`
```

### After Test Setup
```markdown
## ✅ What I Did
- Generated 12 unit tests (services)
- Generated 8 integration tests (with Testcontainers)
- Setup Jest + Supertest config
- Coverage: 87% (above 80% target)

**Auto-fixed during run:**
- Selector mismatch in users.spec.ts → fixed
- Async timing in auth.spec.ts → added waitFor

## 🎁 What You Get
- All tests passing ✅
- Coverage report at `coverage/index.html`
- CI-ready test commands

## 👉 What You Need To Do
Nothing! Tests are passing. Run `npm test` anytime to verify.

**Suggested next:**
- `/be-deploy` - Setup CI/CD pipeline
- `/be-observe` - Add production monitoring
```

---

## ⚠️ Rules

### ALWAYS
- ✅ Include all 3 sections
- ✅ State what user must do (even "Nothing!")
- ✅ Provide preview URL when API created
- ✅ Explain WHY for non-obvious actions
- ✅ Anticipate follow-up questions

### NEVER
- ❌ End with just "Done!"
- ❌ Use technical jargon in "What You Get"
- ❌ Leave user guessing
- ❌ Skip required env var instructions
- ❌ Skip preview URL when applicable

---

## ✅ Pre-Response Checklist

Before sending, verify:
- [ ] Skills Loaded checkpoint at top?
- [ ] Memory loaded acknowledged?
- [ ] Agent identified?
- [ ] "✅ What I Did" section?
- [ ] "🎁 What You Get" section (user perspective)?
- [ ] "👉 What You Need To Do" section?
- [ ] If nothing needed, said "Nothing!" explicitly?
- [ ] Preview URL if API/UI changed?
- [ ] Can user act without asking questions?

If any fails → fix before sending!

---

## 🌐 Language Adaptation

Sections adapt to user language:

### English (default)
- ✅ What I Did
- 🎁 What You Get
- 👉 What You Need To Do

### Thai
- ✅ สิ่งที่ทำให้
- 🎁 สิ่งที่คุณได้
- 👉 สิ่งที่คุณต้องทำ

Code/CLI commands stay in English regardless.

---

*Response Format Skill v1.0 — Predictable structured output*

---

## 📚 EMBEDDED SKILL: memory-system

# Memory System Skill

Persistent context layer for becraft. Single source of truth across sessions and IDEs (Claude Code + Antigravity).

---

## 🎯 Purpose

Memory enables AI to:
1. **Resume work** without losing context
2. **Coordinate** multiple agents in same session
3. **Share state** between Claude Code ↔ Antigravity sessions
4. **Audit** what was done and why

---

## 📁 Memory Structure (9 Files)

**Location:** `.be/memory/` (single location for all IDEs)

```
.be/memory/
├── active.md              ← Current task state (~500 tokens)
├── summary.md             ← Project overview + tech stack (~1,000 tokens)
├── decisions.md           ← Architecture Decision Records (~500 tokens)
├── changelog.md           ← Session-by-session changes (~300 tokens)
├── agents-log.md          ← Agent activity log (~300 tokens)
├── architecture.md        ← Service structure (~500 tokens)
├── api-registry.md        ← Endpoints + DTOs + auth (~600 tokens)
├── schema.md              ← DB schema + migrations (~500 tokens)
└── contracts.md           ← OpenAPI snapshots (~400 tokens)
```

**Total budget:** ~4,600 tokens for full memory load

---

## 🔄 Memory Protocol (Lazy — BCFT-001)

### BEFORE Starting ANY Work

```
STEP 1: Read .be/memory/_index.json FIRST
  ├── Lists which files have meaningful content
  ├── Token-efficient — skip empty templates
  └── Format:
      {
        "files": {
          "active":   { "populated": true,  "size_bytes": 850, ... },
          "summary":  { "populated": false, "size_bytes": 0,   ... },
          ...
        }
      }

STEP 2: Read ONLY files where populated == true
  ├── Use parallel tool calls for batched reads
  └── Skip files where populated == false (empty templates)

STEP 3: Fresh project shortcut
  ├── If ALL files have populated == false:
  │   └── Skip memory entirely — just acknowledge "fresh start"
  └── Save ~4,600 tokens on greenfield projects

STEP 4: Build context understanding (from populated files only)
  ├── What's the project about? (summary)
  ├── What's the active task? (active)
  ├── What decisions made? (decisions)
  ├── Current schema state? (schema)
  └── Existing endpoints? (api-registry)

STEP 5: Acknowledge in response
  └── "💾 Memory: Loaded ✅ (N/9 populated files via index)"
```

### Token Savings

| Scenario | Old Protocol | New Lazy Protocol | Savings |
|----------|-------------|-------------------|---------|
| Fresh project (all empty) | ~4,600 tokens | ~150 tokens (just index) | ~97% |
| Mid-project (3-4 populated) | ~4,600 tokens | ~2,000 tokens | ~57% |
| Mature project (all populated) | ~4,600 tokens | ~4,600 tokens | 0% |

### Updating the Index

After writing to a memory file:
```bash
.be/scripts/update-memory-index.sh
```
This auto-detects size + mtime and flips `populated` based on content analysis
(skips template scaffolding markers).

---

## 📜 Append-Only Event Log (BCFT-009)

**Alternative pattern** for high-frequency updates: write events to
`.be/memory/events.jsonl` instead of editing markdown files directly.
Benefits: race-safe, audit trail, replayable, easier concurrent agents.

### Append an event

```bash
.be/scripts/append-event.sh <type> <agent> '<json-data>'

# Examples:
.be/scripts/append-event.sh decision bootstrap-agent \
  '{"id":"ADR-001","decision":"use Supabase JS","reason":"only SUPABASE_URL set"}'

.be/scripts/append-event.sh endpoint_added api-builder \
  '{"method":"GET","path":"/api/v1/products","auth":"public"}'

.be/scripts/append-event.sh file_created api-builder \
  '{"path":"src/products/products.service.ts","lines":85}'
```

### Event Types

| Type | Data Schema |
|------|-------------|
| `decision` | `{id, decision, reason}` |
| `file_created` / `file_modified` | `{path, lines}` |
| `endpoint_added` | `{method, path, auth}` |
| `schema_changed` | `{table, change}` |
| `migration_applied` | `{name, applied_at}` |
| `phase_started` / `phase_completed` | `{phase_name, duration_ms?}` |
| `agent_invoked` / `agent_completed` | `{task, status?}` |
| `stack_detected` | `{stack, source}` |
| `feature_completed` | `{name, files}` |

Full schema: `.be/memory/event-schema.json`

### Snapshot regeneration

```bash
.be/scripts/snapshot-memory.sh
```
Reads `events.jsonl` → regenerates `decisions.md`, `changelog.md`,
`agents-log.md`, `api-registry.md`. Idempotent — running twice produces
the same output.

### When to use events vs direct markdown edits

| Task | Use |
|------|-----|
| Adding 1 ADR | Direct edit `decisions.md` ✅ |
| Logging 50 file creations | Events ✅ |
| Concurrent agents writing | Events ✅ (race-safe) |
| User-facing edits | Direct ✅ (markdown is canonical) |

---

## 💾 Checkpoint Protocol (BCFT-011)

For long-running tasks (>3 phases or >15 files), agents MUST checkpoint after
each phase to enable resume on cancel/crash.

```bash
.be/scripts/resume-task.sh list                     # show checkpoints
.be/scripts/resume-task.sh show <task-id>           # display details
.be/scripts/resume-task.sh clean --completed        # cleanup
```

Checkpoint location: `.be/checkpoints/<task-id>.json`
Format: see `.be/checkpoints/_example.json`

### AFTER Completing Work

```
STEP 1: Update active.md (ALWAYS)
  ├── Current Focus → What was just done
  ├── In Progress → Mark [x] completed
  ├── Just Completed → Add finished items
  └── Next Steps → Suggest next actions

STEP 2: Update changelog.md (ALWAYS)
  └── Add row: | Agent | Action | Files |

STEP 3: Update agents-log.md (ALWAYS)
  └── Add row: | Time | Agent | Task | Status | Files |

STEP 4: Update domain-specific (CONDITIONAL)
  ├── Schema changed? → schema.md
  ├── API endpoint? → api-registry.md + contracts.md
  ├── Architecture? → architecture.md
  ├── Decision made? → decisions.md
  └── Feature done? → summary.md

STEP 5: Confirm
  └── "💾 Memory: Saved ✅"
```

---

## 🤖 Per-Agent Write Rules

| Agent | active | summary | decisions | changelog | agents-log | architecture | api-registry | schema | contracts |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 📋 plan | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | - | - | - |
| 📐 schema | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ | - | ✅ | - |
| 🔌 api | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ⚠️ | ✅ | - | ✅ |
| 🛡️ auth | ✅ | ⚠️ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ |
| 📊 observe | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | - | - | - |
| 🧪 test | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | - | ⚠️ | - | ⚠️ |

✅ Always | ⚠️ If relevant | - Don't touch

---

## 🌐 Cross-IDE Synchronization

**Problem:** Claude Code + Antigravity may run different sessions
**Solution:** Single `.be/memory/` location

### Both IDEs MUST:
- ✅ Read from `.be/memory/` (NOT `.claude/memory/` or `.agent/memory/`)
- ✅ Write to `.be/memory/`
- ✅ Same UTF-8 format
- ✅ Check mtime before write (concurrency)

---

## 📋 Read Strategies by Task Type

### Quick Fix (single file)
- active.md + changelog.md + relevant domain file

### New Feature
- All 9 files (full context)

### Architecture Change
- All 9 + check archive/ for prior iterations

### Resume Session
1. active.md (where we left off)
2. agents-log.md (last actions)
3. changelog.md (recent changes)
4. summary.md (high-level state)
5. domain-specific based on active task

---

## 🗂️ Archive Strategy

When `active.md` > 50 lines or session ends:
```
1. Snapshot → archive/active-{YYYY-MM-DD-HHMM}.md
2. Reset active.md (keep only Next Steps)
3. Move summary points to summary.md
```

When `changelog.md` > 200 lines:
```
1. Move oldest sessions → archive/changelog-{YYYY-MM}.md
2. Keep last 5 sessions in main
```

Archive NOT loaded by default — only when user asks history.

---

## 📐 File Format Standards

### active.md
```markdown
# 🔥 Active Task

## Current Focus
[One-sentence description]

## In Progress
- [ ] Task 1
- [x] Task 2

## Just Completed
- File X created
- Migration Y applied

## Next Steps
- Suggested action 1

## Blockers / Issues
- (none)

---
*Last updated: {ISO timestamp}*
```

### decisions.md
```markdown
| Date | ADR | Decision | Reason | Trade-offs |
|------|-----|----------|--------|------------|
| 2026-05-06 | ADR-001 | Use Prisma | Type safety + migrations | Lock-in to ORM |
```

### changelog.md
```markdown
## [Session 2026-05-06] - {timestamp}

### Changes Made
| Agent | Action | File/Resource |
|-------|--------|---------------|
| 📐 schema | Added users table | prisma/schema.prisma |
| 🔌 api | Added POST /users | src/users/users.controller.ts |

### Migrations
| Version | Description | Status |
|---------|-------------|--------|
| 20260506_init | Initial users | applied |
```

---

## ⚠️ Critical Rules

1. **NEVER** start without reading 9 files
2. **NEVER** finish without updating relevant files
3. **NEVER** use `.claude/memory/` — always `.be/memory/`
4. **NEVER** ask "should I save?" — just do it
5. **NEVER** delete archive
6. **ALWAYS** keep active.md ≤ 50 lines
7. **ALWAYS** ISO 8601 timestamps
8. **ALWAYS** check mtime before write

---

## 🔍 Health Checks

- [ ] All 9 files exist
- [ ] active.md ≤ 50 lines
- [ ] changelog.md ≤ 200 lines
- [ ] decisions.md sorted by date
- [ ] schema.md matches prisma/schema.prisma
- [ ] api-registry.md matches actual endpoints
- [ ] No stale "In Progress" > 30 days

---

*Memory System Skill v1.0 — Persistent context across sessions and IDEs*

---

## 📝 Response Format (3-Section MANDATORY)

After completing, end your response with:

```markdown
## ✅ What I Did
- [files, migrations, deps]

## 🎁 What You Get
- [user-facing benefits]
- Preview: http://localhost:3000/docs

## 👉 What You Need To Do
- [actionable steps OR "Nothing!"]
```

---

*Bundled by becraft @2026-05-08*
