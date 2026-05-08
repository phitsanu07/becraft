/**
 * Snippet: Cursor pagination DTO + helper
 *
 * Used by: api-builder
 * Customize: rarely
 */

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

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    limit: number;
    nextCursor: string | null;
    hasMore: boolean;
  };
}

/**
 * Helper: build paginated response from N+1 query result.
 *
 * Usage:
 *   const records = await this.prisma.user.findMany({
 *     take: limit + 1,
 *     cursor: cursor ? { id: decodeCursor(cursor) } : undefined,
 *     skip: cursor ? 1 : 0,
 *   });
 *   return paginate(records, limit, (r) => r.id);
 */
export function paginate<T>(
  records: T[],
  limit: number,
  getId: (record: T) => string,
): PaginatedResponse<T> {
  const hasMore = records.length > limit;
  const data = records.slice(0, limit);
  const nextCursor = hasMore && data.length > 0
    ? Buffer.from(getId(data[data.length - 1])).toString('base64')
    : null;
  return { data, meta: { limit, nextCursor, hasMore } };
}

export function decodeCursor(cursor: string): string {
  return Buffer.from(cursor, 'base64').toString('utf-8');
}
