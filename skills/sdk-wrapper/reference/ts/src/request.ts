export interface InternalRequest {
  method: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  path: string;
  query?: Record<string, string | number | undefined>;
  body?: unknown;
}

/** Keys are sorted so every SDK signs the same query string. */
export function buildQuery(query?: Record<string, string | number | undefined>): string {
  if (!query) return '';

  const params = new URLSearchParams();
  for (const key of Object.keys(query).sort()) {
    const value = query[key];
    if (value !== undefined && value !== '') params.set(key, String(value));
  }
  return params.toString();
}
