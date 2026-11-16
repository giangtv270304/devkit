import { createHmac } from 'node:crypto';

export const HEADER_KEY = 'X-Api-Key';
export const HEADER_SIGNATURE = 'X-Signature';
export const HEADER_TIMESTAMP = 'X-Timestamp';

/** Everything the signature covers. `body` is the exact string sent on the wire. */
export interface SignParams {
  method: string;
  path: string;
  query: string;
  body: string;
  timestamp: number;
}

export function message(apiKey: string, params: SignParams): string {
  return apiKey + params.method + params.path + params.query + params.body + String(params.timestamp);
}

export function sign(secretKey: string, msg: string): string {
  return createHmac('sha256', secretKey).update(msg).digest('base64url');
}

export function buildHeaders(apiKey: string, secretKey: string, params: SignParams): Record<string, string> {
  return {
    [HEADER_KEY]: apiKey,
    [HEADER_SIGNATURE]: sign(secretKey, message(apiKey, params)),
    [HEADER_TIMESTAMP]: String(params.timestamp),
  };
}
