import type { WidgetClient } from './client';
import type { ApiResponse } from './response';
import type { Widget, WidgetStatus } from './widget_get_by_id';

/** Fields left out are not sent and the API applies its defaults. */
export interface ListWidgetsRequest {
  page?: number;
  pageSize?: number;
  status?: WidgetStatus;
}

export interface ListWidgetsResponse {
  items: Widget[];
  page: number;
  pageSize: number;
  total: number;
}

export async function listWidgets(
  client: WidgetClient,
  req: ListWidgetsRequest = {},
): Promise<ApiResponse<ListWidgetsResponse>> {
  return client.execute({
    method: 'GET',
    path: '/v1/widgets',
    query: { page: req.page, pageSize: req.pageSize, status: req.status },
  });
}
