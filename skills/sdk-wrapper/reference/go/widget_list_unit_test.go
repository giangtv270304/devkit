package widget_test

import (
	"context"
	"net/http"
	"testing"

	widget "example.com/widget-go"
)

func TestListWidgets_Success(t *testing.T) {
	t.Parallel()

	mock := &mockHTTPClient{
		status: http.StatusOK,
		body:   `{"requestId":"req_1","data":{"items":[{"id":"wid_1"},{"id":"wid_2"}],"page":2,"pageSize":10,"total":12}}`,
	}
	client := newMockClient(t, mock)

	resp, err := client.ListWidgets(context.Background(), &widget.ListWidgetsRequest{
		Page:     2,
		PageSize: 10,
		Status:   widget.WidgetStatusActive,
	})
	if err != nil {
		t.Fatalf("ListWidgets: %v", err)
	}

	if len(resp.Data.Items) != 2 || resp.Data.Total != 12 {
		t.Errorf("items = %d total = %d, want 2 / 12", len(resp.Data.Items), resp.Data.Total)
	}

	if got := mock.lastReq.URL.RawQuery; got != "page=2&pageSize=10&status=active" {
		t.Errorf("query = %q, want page=2&pageSize=10&status=active", got)
	}
}

func TestListWidgets_NilRequestSendsNoQuery(t *testing.T) {
	t.Parallel()

	mock := &mockHTTPClient{status: http.StatusOK, body: `{"requestId":"req_1","data":{"items":[]}}`}
	client := newMockClient(t, mock)

	if _, err := client.ListWidgets(context.Background(), nil); err != nil {
		t.Fatalf("ListWidgets: %v", err)
	}

	if got := mock.lastReq.URL.RawQuery; got != "" {
		t.Errorf("query = %q, want empty", got)
	}
}

func TestListWidgets_Unauthorized(t *testing.T) {
	t.Parallel()

	client := newMockClient(t, &mockHTTPClient{
		status: http.StatusUnauthorized,
		body:   `{"requestId":"req_3","error":{"code":"invalid_signature","message":"signature mismatch"}}`,
	})

	if _, err := client.ListWidgets(context.Background(), nil); !widget.IsUnauthorized(err) {
		t.Errorf("error = %v, want a 401 *widget.APIError", err)
	}
}
