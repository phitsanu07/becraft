---
name: api-design
description: >
  REST API design conventions for NestJS. Resource naming, HTTP methods,
  status codes, pagination, versioning, error responses, OpenAPI annotations.
related_skills:
  - contract-first
  - error-handling
  - schema-design
---

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
