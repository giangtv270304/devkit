import { WidgetError } from './errors';
import { buildQuery, type InternalRequest } from './request';
import { buildHeaders } from './signer';
import { createWidget, type CreateWidgetRequest } from './widget_create';
import { getWidgetById, type GetWidgetByIdRequest } from './widget_get_by_id';
import { listWidgets, type ListWidgetsRequest } from './widget_list';

export const VERSION = '0.1.0';
export const SANDBOX_BASE_URL = 'https://sandbox.widget.example';
export const PRODUCTION_BASE_URL = 'https://api.widget.example';
export const DEFAULT_TIMEOUT_MS = 30_000;

const USER_AGENT = `widget-node/${VERSION}`;

export interface Logger {
  debug(msg: string, ...args: unknown[]): void;
}

export interface WidgetClientOptions {
  /** `SANDBOX_BASE_URL`, `PRODUCTION_BASE_URL`, or a local server in tests. */
  baseUrl: string;
  apiKey: string;
  /** Server side only: never ship it to a browser or a mobile app. */
  secretKey: string;
  /** Defaults to `DEFAULT_TIMEOUT_MS`. */
  timeoutMs?: number;
  /** Replaces global `fetch`: proxies, tracing, tests. */
  fetch?: typeof fetch;
  /** Turns on debug logs of method, URL and status. Bodies and headers are never logged. */
  logger?: Logger;
  /** Clock in milliseconds, for tests. */
  now?: () => number;
}

export class WidgetClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly secretKey: string;
  private readonly timeoutMs: number;
  private readonly fetchImpl: typeof fetch;
  private readonly logger: Logger | undefined;
  private readonly now: () => number;

  constructor(options: WidgetClientOptions) {
    if (!options.baseUrl) throw new Error('widget: baseUrl is required');
    if (!options.apiKey) throw new Error('widget: apiKey is required');
    if (!options.secretKey) throw new Error('widget: secretKey is required');

    this.baseUrl = options.baseUrl.replace(/\/+$/, '');
    this.apiKey = options.apiKey;
    this.secretKey = options.secretKey;
    this.timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
    this.fetchImpl = options.fetch ?? fetch;
    this.logger = options.logger;
    this.now = options.now ?? Date.now;
  }

  /** @internal Endpoint files call this; application code uses the methods below. */
  async execute<T>(req: InternalRequest): Promise<T> {
    const query = buildQuery(req.query);
    const url = this.baseUrl + req.path + (query ? `?${query}` : '');
    const body = req.body === undefined ? '' : JSON.stringify(req.body);

    // The signature covers the exact string sent: sign after encoding, never re-encode.
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'User-Agent': USER_AGENT,
      ...(body && { 'Content-Type': 'application/json' }),
      ...buildHeaders(this.apiKey, this.secretKey, {
        method: req.method,
        path: req.path,
        query,
        body,
        timestamp: Math.floor(this.now() / 1000),
      }),
    };

    let response: Response;
    let text: string;
    try {
      response = await this.fetchImpl(url, {
        method: req.method,
        headers,
        body: body || null,
        signal: AbortSignal.timeout(this.timeoutMs),
      });
      text = await response.text();
    } catch (cause) {
      const timedOut = cause instanceof Error && (cause.name === 'TimeoutError' || cause.name === 'AbortError');
      throw new WidgetError(
        timedOut ? 'timeout' : 'network',
        timedOut
          ? `widget: ${req.method} ${req.path} timed out after ${this.timeoutMs} ms`
          : `widget: ${req.method} ${req.path} failed before a response arrived`,
        { cause },
      );
    }

    this.logger?.debug('widget request', req.method, url, response.status);

    if (!response.ok) throw WidgetError.fromResponse(response.status, text);

    try {
      return JSON.parse(text) as T;
    } catch (cause) {
      throw new WidgetError('invalid_response', `widget: ${req.method} ${req.path} returned a body that is not JSON`, {
        statusCode: response.status,
        body: text,
        cause,
      });
    }
  }

  /** Creates a widget. `price` is a decimal string such as `'12.50'`. */
  createWidget = (req: CreateWidgetRequest) => createWidget(this, req);
  /** Returns one widget. A missing widget throws a `WidgetError`; check it with `isNotFound`. */
  getWidgetById = (req: GetWidgetByIdRequest) => getWidgetById(this, req);
  /** Returns one page of widgets. */
  listWidgets = (req?: ListWidgetsRequest) => listWidgets(this, req);
}
