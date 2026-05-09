/**
 * Supabase DI tokens — leaf file (no imports from module/service).
 *
 * Why a separate file: prevents a circular import between
 * `supabase.module.ts` (which registers `SupabaseService` as a provider)
 * and `supabase.service.ts` (which needs the tokens to declare its
 * constructor injections). Without this split, CommonJS module
 * initialization order leaves the token constants `undefined` at the
 * moment NestJS captures `SupabaseService`'s constructor metadata,
 * producing a runtime "Nest can't resolve dependencies of SupabaseService"
 * error that does NOT show up in unit tests (which usually mock the
 * service via `overrideProvider(...).useValue(...)`).
 */

export const SUPABASE_CLIENT = 'SUPABASE_CLIENT';
export const SUPABASE_ADMIN_CLIENT = 'SUPABASE_ADMIN_CLIENT';
