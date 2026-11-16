package widget

import (
	"context"
	"net/http"
	"net/url"
	"strconv"
)

// ListWidgetsRequest: zero values are left out and the API applies its defaults.
type ListWidgetsRequest struct {
	Page     int
	PageSize int
	Status   WidgetStatus
}

type ListWidgetsResponse struct {
	Items    []Widget `json:"items"`
	Page     int      `json:"page"`
	PageSize int      `json:"pageSize"`
	Total    int      `json:"total"`
}

// ListWidgets returns one page of widgets. Pass nil for the first page with defaults.
func (c *Client) ListWidgets(ctx context.Context, req *ListWidgetsRequest) (*Response[ListWidgetsResponse], error) {
	query := url.Values{}

	if req != nil {
		if req.Page > 0 {
			query.Set("page", strconv.Itoa(req.Page))
		}

		if req.PageSize > 0 {
			query.Set("pageSize", strconv.Itoa(req.PageSize))
		}

		if req.Status != "" {
			query.Set("status", string(req.Status))
		}
	}

	return call[ListWidgetsResponse](ctx, c, request{
		Method: http.MethodGet,
		Path:   "/v1/widgets",
		Query:  query,
		Body:   nil,
	})
}
