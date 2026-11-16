import { beforeEach, describe, expect, it } from 'vitest';
import { isNotFound, isUnauthorized, WidgetError } from '../errors';
import { HEADER_KEY, HEADER_SIGNATURE, HEADER_TIMESTAMP } from '../signer';
import { lastCall, makeClient, mockFetch, mockResponse } from './helpers';

const client = makeClient();

beforeEach(() => mockFetch.mockReset());

describe('getWidgetById', () => {
  it('sends a signed GET with an escaped id and returns the envelope', async () => {
    mockResponse(200, { requestId: 'req_1', data: { id: 'wid_1', price: '12.50', status: 'active', note: null } });

    const res = await client.getWidgetById({ widgetId: 'wid/1' });

    expect(res.requestId).toBe('req_1');
    expect(res.data.price).toBe('12.50');

    const { url, init, headers } = lastCall();
    expect(init.method).toBe('GET');
    expect(url).toBe('https://mock.widget.example/v1/widgets/wid%2F1');
    expect(headers[HEADER_KEY]).toBe('test-api-key');
    expect(headers[HEADER_TIMESTAMP]).toBe('1700000000');
    expect(headers[HEADER_SIGNATURE]).toBeTruthy();
    expect(headers['User-Agent']).toMatch(/^widget-node\//);
  });

  it('throws a WidgetError carrying code and requestId on 404', async () => {
    mockResponse(404, { requestId: 'req_2', error: { code: 'widget_not_found', message: 'widget not found' } });

    const err = await client.getWidgetById({ widgetId: 'wid_404' }).catch((e: unknown) => e);

    expect(err).toBeInstanceOf(WidgetError);
    expect(err).toMatchObject({ kind: 'api', statusCode: 404, code: 'widget_not_found', requestId: 'req_2' });
    expect(isNotFound(err)).toBe(true);
  });

  it('keeps a non-JSON error body', async () => {
    mockResponse(502, '<html>bad gateway</html>');

    await expect(client.getWidgetById({ widgetId: 'wid_1' })).rejects.toMatchObject({
      kind: 'api',
      statusCode: 502,
      body: '<html>bad gateway</html>',
    });
  });

  it('throws invalid_response when a 2xx body is not JSON', async () => {
    mockResponse(200, 'not json');

    await expect(client.getWidgetById({ widgetId: 'wid_1' })).rejects.toMatchObject({ kind: 'invalid_response' });
  });

  it('throws network when fetch rejects', async () => {
    mockFetch.mockRejectedValueOnce(new TypeError('fetch failed'));

    await expect(client.getWidgetById({ widgetId: 'wid_1' })).rejects.toMatchObject({ kind: 'network' });
  });

  it('throws timeout when the request is aborted by the timeout', async () => {
    mockFetch.mockImplementationOnce(
      (_url: string, init: RequestInit) =>
        new Promise((_resolve, reject) => {
          init.signal?.addEventListener('abort', () => reject(init.signal?.reason));
        }),
    );

    await expect(makeClient({ timeoutMs: 5 }).getWidgetById({ widgetId: 'wid_1' })).rejects.toMatchObject({
      kind: 'timeout',
    });
  });

  it('rejects an empty id before calling the API', async () => {
    await expect(client.getWidgetById({ widgetId: '' })).rejects.toThrow('widgetId is required');
    expect(mockFetch).not.toHaveBeenCalled();
  });
});

describe('createWidget', () => {
  it('posts the JSON body', async () => {
    mockResponse(201, { requestId: 'req_1', data: { id: 'wid_1' } });

    const res = await client.createWidget({ name: 'Bolt', price: '12.50' });

    expect(res.data.id).toBe('wid_1');
    const { url, init, headers } = lastCall();
    expect(init.method).toBe('POST');
    expect(url).toBe('https://mock.widget.example/v1/widgets');
    expect(init.body).toBe('{"name":"Bolt","price":"12.50"}');
    expect(headers['Content-Type']).toBe('application/json');
  });

  it('throws a WidgetError on 400', async () => {
    mockResponse(400, { requestId: 'req_2', error: { code: 'invalid_price', message: 'price must be a decimal string' } });

    await expect(client.createWidget({ name: 'Bolt', price: 'abc' })).rejects.toMatchObject({
      statusCode: 400,
      code: 'invalid_price',
    });
  });
});

describe('listWidgets', () => {
  it('sends a sorted query and skips undefined fields', async () => {
    mockResponse(200, { requestId: 'req_1', data: { items: [{ id: 'wid_1' }], page: 2, pageSize: 10, total: 11 } });

    const res = await client.listWidgets({ status: 'active', pageSize: 10, page: 2 });

    expect(res.data.items).toHaveLength(1);
    expect(lastCall().url).toBe('https://mock.widget.example/v1/widgets?page=2&pageSize=10&status=active');
  });

  it('sends no query without arguments', async () => {
    mockResponse(200, { requestId: 'req_1', data: { items: [], page: 1, pageSize: 20, total: 0 } });

    await client.listWidgets();

    expect(lastCall().url).toBe('https://mock.widget.example/v1/widgets');
  });

  it('throws a WidgetError on 401', async () => {
    mockResponse(401, { requestId: 'req_3', error: { code: 'invalid_signature', message: 'signature mismatch' } });

    const err = await client.listWidgets().catch((e: unknown) => e);

    expect(isUnauthorized(err)).toBe(true);
  });
});
