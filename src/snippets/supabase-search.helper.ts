/**
 * Snippet: Supabase Search Helpers
 *
 * Used by: api-builder (when stack = Supabase JS, query needs or()/ilike search)
 *
 * Provides:
 *   - escapePostgrestValue()   — sanitize user input for PostgREST filters
 *   - buildIlikeOrFilter()     — compose multi-column ILIKE search
 *   - searchAcrossColumns()    — full helper: escape + build + execute
 *   - mapSupabaseError()       — convert Postgres/PostgREST codes → NestJS exceptions
 *   - SupabaseError            — typed error from Supabase responses
 *
 * Why: PostgREST uses '*' as wildcard (NOT '%'), and treats ',' '.' '(' ')' as
 * filter syntax. User input must be escaped or queries silently break (500).
 *
 * Reference: .be/skills/supabase-query-patterns/SKILL.md
 *
 * Customize: rarely — these helpers handle the mechanical edge cases. If you
 * need column-specific weighting or fuzzy ranking, switch to Postgres
 * full-text search (tsvector) or pg_trgm instead of expanding this file.
 */

import {
  BadRequestException,
  ConflictException,
  ForbiddenException,
  HttpException,
  InternalServerErrorException,
  NotFoundException,
} from '@nestjs/common';
import type { PostgrestError, SupabaseClient } from '@supabase/supabase-js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SupabaseErrorLike {
  code?: string;
  message?: string;
  details?: string;
  hint?: string;
}

export interface SearchOptions {
  /** Number of rows to return (default: 20). Capped at 100. */
  limit?: number;
  /** Page number, 1-indexed (default: 1). */
  page?: number;
  /** Column to order by. */
  orderBy?: string;
  /** Order direction (default: descending). */
  ascending?: boolean;
  /** Additional select columns (default: '*'). */
  select?: string;
}

export interface SearchResult<T> {
  data: ReadonlyArray<T>;
  meta: {
    page: number;
    limit: number;
    total: number;
  };
}

// ---------------------------------------------------------------------------
// Input escaping
// ---------------------------------------------------------------------------

/**
 * Escape a user-provided value for safe inclusion in a PostgREST filter.
 *
 * PostgREST treats these chars as syntax inside filter expressions:
 *   ,  filter list separator
 *   .  operator separator (e.g., name.eq.value)
 *   :  type cast prefix
 *   (  ) group / function delimiters
 *   *  ilike/like wildcard
 *   "  string quote
 *   \  escape char
 *
 * Caller decides whether to wrap the result in `"..."` (for or()/and()) or
 * pass it directly (for `.eq()`/`.ilike()` builders, which auto-quote).
 */
export function escapePostgrestValue(value: string): string {
  if (typeof value !== 'string') return '';
  return value
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/,/g, '\\,')
    .replace(/\(/g, '\\(')
    .replace(/\)/g, '\\)')
    .replace(/\*/g, '\\*');
}

// ---------------------------------------------------------------------------
// Filter composition
// ---------------------------------------------------------------------------

/**
 * Build an `or()` filter that matches `keyword` (case-insensitive, wildcard
 * both sides) against any of the given columns.
 *
 * @example
 *   buildIlikeOrFilter(['name', 'description'], 'shoes')
 *   // → 'name.ilike."*shoes*",description.ilike."*shoes*"'
 */
export function buildIlikeOrFilter(
  columns: ReadonlyArray<string>,
  keyword: string,
): string {
  if (!Array.isArray(columns) || columns.length === 0) {
    throw new Error('buildIlikeOrFilter: columns must be a non-empty array');
  }
  const safe = escapePostgrestValue(keyword.trim());
  return columns.map((col) => `${col}.ilike."*${safe}*"`).join(',');
}

// ---------------------------------------------------------------------------
// High-level search
// ---------------------------------------------------------------------------

/**
 * Search a table by case-insensitive substring match across multiple columns.
 * Handles input validation, escaping, pagination, ordering, and error mapping.
 *
 * @example
 *   const result = await searchAcrossColumns<Product>(supabase, 'products', {
 *     columns: ['name', 'description'],
 *     keyword: req.query.q,
 *     page: req.query.page,
 *     orderBy: 'created_at',
 *   });
 */
export async function searchAcrossColumns<T>(
  client: SupabaseClient,
  table: string,
  params: {
    columns: ReadonlyArray<string>;
    keyword: string;
  } & SearchOptions,
): Promise<SearchResult<T>> {
  const {
    columns,
    keyword,
    limit = 20,
    page = 1,
    orderBy,
    ascending = false,
    select = '*',
  } = params;

  if (!keyword || keyword.trim().length === 0) {
    throw new BadRequestException('keyword must not be empty');
  }
  const safeLimit = Math.min(Math.max(1, Math.floor(limit)), 100);
  const safePage = Math.max(1, Math.floor(page));
  const from = (safePage - 1) * safeLimit;
  const to = from + safeLimit - 1;

  const filter = buildIlikeOrFilter(columns, keyword);

  let query = client
    .from(table)
    .select(select, { count: 'exact' })
    .or(filter)
    .range(from, to);

  if (orderBy) {
    query = query.order(orderBy, { ascending });
  }

  const { data, error, count } = await query;
  if (error) throw mapSupabaseError(error);

  return {
    data: (data ?? []) as ReadonlyArray<T>,
    meta: {
      page: safePage,
      limit: safeLimit,
      total: count ?? 0,
    },
  };
}

// ---------------------------------------------------------------------------
// Error mapping
// ---------------------------------------------------------------------------

/**
 * Convert a PostgREST/Postgres error into the appropriate NestJS HttpException.
 *
 * Maps known codes to 4xx where the cause is the caller's input or auth.
 * Unknown codes fall back to 500 with the raw `code` exposed for debugging
 * (no `details`/`hint` — those may leak schema info).
 */
export function mapSupabaseError(
  err: SupabaseErrorLike | PostgrestError,
): HttpException {
  const code = err.code ?? '';
  const message = err.message ?? 'Database error';

  switch (code) {
    case 'PGRST100':
      return new BadRequestException({
        title: 'Invalid query syntax',
        detail: message,
      });

    case 'PGRST116':
      return new NotFoundException('Resource not found');

    case 'PGRST301':
      return new ForbiddenException('Token expired');

    case '23505':
      return new ConflictException('Duplicate entry');

    case '23503':
      return new BadRequestException('Foreign key violation');

    case '23502':
      return new BadRequestException('Required field missing');

    case '23514':
      return new BadRequestException('Value violates check constraint');

    case '42501':
      return new ForbiddenException('Permission denied (row-level security)');

    default:
      return new InternalServerErrorException({
        title: 'Database error',
        code,
      });
  }
}
