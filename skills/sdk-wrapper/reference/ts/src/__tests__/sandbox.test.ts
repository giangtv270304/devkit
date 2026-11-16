import { describe, expect, it } from 'vitest';
import { PRODUCTION_BASE_URL, SANDBOX_BASE_URL, WidgetClient } from '../client';
import { isNotFound } from '../errors';

const apiKey = process.env['WIDGET_SANDBOX_API_KEY'] ?? '';
const secretKey = process.env['WIDGET_SANDBOX_SECRET_KEY'] ?? '';
const baseUrl = process.env['WIDGET_SANDBOX_BASE_URL'] || SANDBOX_BASE_URL;

describe.skipIf(!apiKey || !secretKey)('sandbox', () => {
  if (baseUrl === PRODUCTION_BASE_URL) {
    throw new Error('WIDGET_SANDBOX_BASE_URL points at production; sandbox tests never run there');
  }

  const makeSandboxClient = () => new WidgetClient({ baseUrl, apiKey, secretKey });

  it('lists widgets', async () => {
    const res = await makeSandboxClient().listWidgets({ page: 1, pageSize: 1 });

    expect(res.requestId).toBeTruthy();
  });

  it('creates a widget and reads it back', async () => {
    const client = makeSandboxClient();

    const created = await client.createWidget({ name: 'sdk-sandbox-test', price: '1.00' });
    const fetched = await client.getWidgetById({ widgetId: created.data.id });

    expect(fetched.data.id).toBe(created.data.id);
    expect(fetched.data.price).toBe('1.00');
  });

  it('reports a missing widget as 404', async () => {
    const err = await makeSandboxClient()
      .getWidgetById({ widgetId: 'wid_does_not_exist' })
      .catch((e: unknown) => e);

    expect(isNotFound(err)).toBe(true);
  });
});
