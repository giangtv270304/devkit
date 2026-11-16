package widget

import (
	"context"
	"net/http"
)

type CreateWidgetRequest struct {
	Name     string  `json:"name"`
	Price    string  `json:"price"`
	Currency string  `json:"currency,omitempty"`
	Note     *string `json:"note,omitempty"`
}

type CreateWidgetResponse = Widget

// CreateWidget creates a widget. Price is a decimal string such as "12.50".
func (c *Client) CreateWidget(ctx context.Context, req *CreateWidgetRequest) (*Response[CreateWidgetResponse], error) {
	if req == nil {
		return nil, ErrNilRequest
	}

	return call[CreateWidgetResponse](ctx, c, request{
		Method: http.MethodPost,
		Path:   "/v1/widgets",
		Query:  nil,
		Body:   req,
	})
}
