import { describe, expect, it } from 'vitest';
import { buildHeaders, HEADER_SIGNATURE } from '../signer';
import vectors from '../../../signature-vectors.json';

describe('signer', () => {
  it.each(vectors)('matches the shared vector: $name', (vector) => {
    const headers = buildHeaders(vector.apiKey, vector.secretKey, {
      method: vector.method,
      path: vector.path,
      query: vector.query,
      body: vector.body,
      timestamp: vector.timestamp,
    });

    expect(headers[HEADER_SIGNATURE]).toBe(vector.signature);
  });
});
