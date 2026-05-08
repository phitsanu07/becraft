import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';

/**
 * Supabase PostgrestError shape (returned via { data, error } — not thrown by default).
 * If service code chooses to rethrow it, this filter maps it to HTTP responses.
 */
interface PostgrestErrorLike {
  code?: string;
  message: string;
  details?: string;
  hint?: string;
}

interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  errors?: Array<{ field: string; message: string }>;
  requestId?: string;
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

  private buildProblem(
    exception: unknown,
    instance: string,
    requestId?: string,
  ): ProblemDetails {
    if (exception instanceof HttpException) {
      const response = exception.getResponse();
      const status = exception.getStatus();

      if (typeof response === 'object' && response !== null) {
        const r = response as any;

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

    // Supabase PostgrestError (if service rethrows from { data, error })
    if (this.isPostgrestError(exception)) {
      return this.handleSupabaseError(exception, instance, requestId);
    }

    return {
      type: `${PROBLEM_BASE}/internal-error`,
      title: 'Internal Server Error',
      status: 500,
      detail: 'An unexpected error occurred',
      instance,
      requestId,
    };
  }

  private isPostgrestError(err: unknown): err is PostgrestErrorLike {
    return (
      typeof err === 'object' &&
      err !== null &&
      'message' in err &&
      typeof (err as any).message === 'string' &&
      ('code' in err || 'details' in err || 'hint' in err)
    );
  }

  /**
   * Map common Supabase / Postgres error codes to HTTP responses.
   * Reference: https://www.postgresql.org/docs/current/errcodes-appendix.html
   */
  private handleSupabaseError(
    err: PostgrestErrorLike,
    instance: string,
    requestId?: string,
  ): ProblemDetails {
    switch (err.code) {
      case '23505': // unique_violation
        return {
          type: `${PROBLEM_BASE}/conflict`,
          title: 'Resource Conflict',
          status: 409,
          detail: err.details || 'A record with this value already exists',
          instance,
          requestId,
        };
      case 'PGRST116': // PostgREST: not found / no rows
      case '23503': // foreign_key_violation referencing missing row
        return {
          type: `${PROBLEM_BASE}/not-found`,
          title: 'Not Found',
          status: 404,
          detail: err.details || 'The requested resource was not found',
          instance,
          requestId,
        };
      case '42501': // insufficient_privilege (RLS denied)
        return {
          type: `${PROBLEM_BASE}/forbidden`,
          title: 'Forbidden',
          status: 403,
          detail: 'You do not have permission to perform this action',
          instance,
          requestId,
        };
      case '23514': // check_violation
      case '23502': // not_null_violation
        return {
          type: `${PROBLEM_BASE}/validation`,
          title: 'Validation Failed',
          status: 422,
          detail: err.details || err.message,
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

  private parseValidationErrors(
    messages: string[],
  ): Array<{ field: string; message: string }> {
    return messages.map((m) => {
      const match = m.match(/^([^.\s]+)\s+(.+)$/);
      return match
        ? { field: match[1], message: match[2] }
        : { field: 'unknown', message: m };
    });
  }

  private statusSlug(status: number): string {
    const map: Record<number, string> = {
      400: 'bad-request',
      401: 'unauthorized',
      403: 'forbidden',
      404: 'not-found',
      409: 'conflict',
      422: 'validation',
      429: 'rate-limit',
      500: 'internal-error',
    };
    return map[status] || `error-${status}`;
  }

  private defaultTitle(status: number): string {
    return HttpStatus[status]?.toString().replace(/_/g, ' ') || 'Error';
  }
}
