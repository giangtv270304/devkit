import type { WidgetClient } from './client';
import type { ApiResponse } from './response';

export type WidgetStatus = 'active' | 'archived';

/** `price` is a decimal string (`'12.50'`): never parse it into a `number`. */
export interface Widget {
  id: string;
  name: string;
  price: string;
  currency: string;
  status: WidgetStatus;
  note: string | null;
  createdAt: string;
}

export interface GetWidgetByIdRequest {
  widgetId: string;
}

export type GetWidgetByIdResponse = Widget;

export async function getWidgetById(
  client: WidgetClient,
  req: GetWidgetByIdRequest,
): Promise<ApiResponse<GetWidgetByIdResponse>> {
  if (!req.widgetId) throw new Error('widget: widgetId is required');

  return client.execute({
    method: 'GET',
    path: `/v1/widgets/${encodeURIComponent(req.widgetId)}`,
  });
}
