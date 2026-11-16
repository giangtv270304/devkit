export type WidgetErrorKind = 'api' | 'timeout' | 'network' | 'invalid_response';

/**
 * Every error the SDK throws.
 * `kind: 'api'` means the server answered with status >= 400; `code` and `requestId` come from its body.
 */
export class WidgetError extends Error {
  readonly kind: WidgetErrorKind;
  readonly statusCode?: number;
  readonly code?: string;
  readonly requestId?: string;
  readonly body?: string;

  constructor(
    kind: WidgetErrorKind,
    message: string,
    details: { statusCode?: number; code?: string; requestId?: string; body?: string; cause?: unknown } = {},
  ) {
    super(message, details.cause === undefined ? undefined : { cause: details.cause });
    this.name = 'WidgetError';
    this.kind = kind;
    if (details.statusCode !== undefined) this.statusCode = details.statusCode;
    if (details.code !== undefined) this.code = details.code;
    if (details.requestId !== undefined) this.requestId = details.requestId;
    if (details.body !== undefined) this.body = details.body;
  }

  static fromResponse(statusCode: number, body: string): WidgetError {
    let message = body || `HTTP ${statusCode}`;
    let code: string | undefined;
    let requestId: string | undefined;

    try {
      const parsed = JSON.parse(body) as { requestId?: unknown; error?: { code?: unknown; message?: unknown } };
      if (typeof parsed.error?.message === 'string') message = parsed.error.message;
      if (typeof parsed.error?.code === 'string') code = parsed.error.code;
      if (typeof parsed.requestId === 'string') requestId = parsed.requestId;
    } catch {
      // A proxy or gateway can answer with HTML: the raw body stays in `message` and `body`.
    }

    return new WidgetError('api', message, {
      statusCode,
      body,
      ...(code !== undefined && { code }),
      ...(requestId !== undefined && { requestId }),
    });
  }
}

export function isNotFound(err: unknown): boolean {
  return err instanceof WidgetError && err.statusCode === 404;
}

export function isUnauthorized(err: unknown): boolean {
  return err instanceof WidgetError && err.statusCode === 401;
}

export function isConflict(err: unknown): boolean {
  return err instanceof WidgetError && err.statusCode === 409;
}

export function isRateLimited(err: unknown): boolean {
  return err instanceof WidgetError && err.statusCode === 429;
}
