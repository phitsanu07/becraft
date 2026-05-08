/**
 * Snippet: RFC 7807 Problem Details exception filter for NestJS
 *
 * Used by: bootstrap-agent (registered globally in main.ts)
 * Customize: PROBLEM_BASE for your error documentation URL
 */

import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { Prisma } from '@prisma/client'; // remove if not using Prisma

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

  private buildProblem(exception: unknown, instance: string, requestId?: string): ProblemDetails {
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
            errors: r.message.map((m: string) => {
              const match = m.match(/^([^.\s]+)\s+(.+)$/);
              return match ? { field: match[1], message: match[2] } : { field: 'unknown', message: m };
            }),
            requestId,
          };
        }
        return {
          type: r.type || `${PROBLEM_BASE}/${this.statusSlug(status)}`,
          title: r.title || r.error || HttpStatus[status]?.toString().replace(/_/g, ' ') || 'Error',
          status,
          detail: r.detail || r.message || 'An error occurred',
          instance,
          ...(r.errors && { errors: r.errors }),
          requestId,
        };
      }
      return {
        type: `${PROBLEM_BASE}/${this.statusSlug(status)}`,
        title: HttpStatus[status]?.toString().replace(/_/g, ' ') || 'Error',
        status,
        detail: typeof response === 'string' ? response : 'An error occurred',
        instance,
        requestId,
      };
    }

    // Prisma — remove this block if not using Prisma
    if (exception instanceof Prisma.PrismaClientKnownRequestError) {
      const map: Record<string, [number, string, string]> = {
        P2002: [409, 'Resource Conflict', 'A record with this value already exists'],
        P2025: [404, 'Not Found', 'The requested resource was not found'],
      };
      const [status, title, detail] = map[exception.code] || [500, 'Database Error', 'A database error occurred'];
      return {
        type: `${PROBLEM_BASE}/${this.statusSlug(status)}`,
        title,
        status,
        detail,
        instance,
        requestId,
      };
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

  private statusSlug(status: number): string {
    const map: Record<number, string> = {
      400: 'bad-request', 401: 'unauthorized', 403: 'forbidden',
      404: 'not-found', 409: 'conflict', 422: 'validation',
      429: 'rate-limit', 500: 'internal-error',
    };
    return map[status] || `error-${status}`;
  }
}
