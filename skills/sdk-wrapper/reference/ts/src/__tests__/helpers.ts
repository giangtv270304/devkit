import { vi } from 'vitest';
import { WidgetClient } from '../client';

export const mockFetch = vi.fn();

export function makeClient(overrides: { timeoutMs?: number } = {}) {
  return new WidgetClient({
    baseUrl: 'https://mock.widget.example',
    apiKey: 'test-api-key',
    secretKey: 'test-secret-key',
    fetch: mockFetch as unknown as typeof fetch,
    now: () => 1_700_000_000_000,
    ...overrides,
  });
}

export function mockResponse(status: number, body: unknown) {
  const text = typeof body === 'string' ? body : JSON.stringify(body);
  mockFetch.mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    text: async () => text,
  } as Response);
}

export function lastCall(): { url: string; init: RequestInit; headers: Record<string, string> } {
  const call = mockFetch.mock.calls.at(-1);
  if (!call) throw new Error('fetch was not called');
  const [url, init] = call as [string, RequestInit];
  return { url, init, headers: init.headers as Record<string, string> };
}
