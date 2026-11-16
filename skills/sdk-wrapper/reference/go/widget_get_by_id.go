package widget

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
)

type WidgetStatus string

const (
	WidgetStatusActive   WidgetStatus = "active"
	WidgetStatusArchived WidgetStatus = "archived"
)

// Widget is the resource returned by every widget endpoint.
// Price is a decimal string ("12.50"): never parse it into a float.
type Widget struct {
	ID        string       `json:"id"`
	Name      string       `json:"name"`
	Price     string       `json:"price"`
	Currency  string       `json:"currency"`
	Status    WidgetStatus `json:"status"`
	Note      *string      `json:"note"`
	CreatedAt string       `json:"createdAt"`
}

type GetWidgetByIDRequest struct {
	WidgetID string
}

type GetWidgetByIDResponse = Widget

// GetWidgetByID returns one widget. A missing widget is an *APIError; check it with IsNotFound.
func (c *Client) GetWidgetByID(ctx context.Context, req *GetWidgetByIDRequest) (*Response[GetWidgetByIDResponse], error) {
	if req == nil {
		return nil, ErrNilRequest
	}

	if req.WidgetID == "" {
		return nil, fmt.Errorf("%w: WidgetID", ErrMissingField)
	}

	return call[GetWidgetByIDResponse](ctx, c, request{
		Method: http.MethodGet,
		Path:   "/v1/widgets/" + url.PathEscape(req.WidgetID),
		Query:  nil,
		Body:   nil,
	})
}
