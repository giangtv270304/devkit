import type { WidgetClient } from './client';
import type { ApiResponse } from './response';
import type { Widget } from './widget_get_by_id';

export interface CreateWidgetRequest {
  name: string;
  price: string;
  currency?: string;
  note?: string;
}

export type CreateWidgetResponse = Widget;

export async function createWidget(
  client: WidgetClient,
  req: CreateWidgetRequest,
): Promise<ApiResponse<CreateWidgetResponse>> {
  return client.execute({ method: 'POST', path: '/v1/widgets', body: req });
}
