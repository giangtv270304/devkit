package widget_test

import (
	"context"
	"errors"
	"net/http"
	"testing"

	widget "example.com/widget-go"
	"example.com/widget-go/signer"
)

func TestGetWidgetByID_Success(t *testing.T) {
	t.Parallel()

	mock := &mockHTTPClient{
		status: http.StatusOK,
		body:   `{"requestId":"req_1","data":{"id":"wid_1","name":"Bolt","price":"12.50","status":"active","note":null}}`,
	}
	client := newMockClient(t, mock)

	resp, err := client.GetWidgetByID(context.Background(), &widget.GetWidgetByIDRequest{WidgetID: "wid/1"})
	if err != nil {
		t.Fatalf("GetWidgetByID: %v", err)
	}

	if resp.RequestID != "req_1" || resp.Data.ID != "wid_1" || resp.Data.Price != "12.50" {
		t.Errorf("response = %+v, want req_1 / wid_1 / 12.50", resp)
	}

	if resp.Data.Status != widget.WidgetStatusActive || resp.Data.Note != nil {
		t.Errorf("status = %q note = %v, want active / nil", resp.Data.Status, resp.Data.Note)
	}

	if mock.lastReq.Method != http.MethodGet {
		t.Errorf("method = %s, want GET", mock.lastReq.Method)
	}

	if got := mock.lastReq.URL.EscapedPath(); got != "/v1/widgets/wid%2F1" {
		t.Errorf("path = %q, want /v1/widgets/wid%%2F1", got)
	}

	for _, header := range []string{signer.HeaderKey, signer.HeaderSignature, signer.HeaderTimestamp, "User-Agent"} {
		if mock.lastReq.Header.Get(header) == "" {
			t.Errorf("header %s is missing", header)
		}
	}
}

func TestGetWidgetByID_APIError(t *testing.T) {
	t.Parallel()

	mock := &mockHTTPClient{
		status: http.StatusNotFound,
		body:   `{"requestId":"req_2","error":{"code":"widget_not_found","message":"widget not found"}}`,
	}
	client := newMockClient(t, mock)

	_, err := client.GetWidgetByID(context.Background(), &widget.GetWidgetByIDRequest{WidgetID: "wid_404"})

	var apiErr *widget.APIError
	if !errors.As(err, &apiErr) {
		t.Fatalf("error = %v, want *widget.APIError", err)
	}

	if apiErr.Code != "widget_not_found" || apiErr.RequestID != "req_2" || !widget.IsNotFound(err) {
		t.Errorf("api error = %+v, want widget_not_found / req_2 / 404", apiErr)
	}
}

func TestGetWidgetByID_NonJSONErrorBodyIsKept(t *testing.T) {
	t.Parallel()

	client := newMockClient(t, &mockHTTPClient{status: http.StatusBadGateway, body: "<html>bad gateway</html>"})

	_, err := client.GetWidgetByID(context.Background(), &widget.GetWidgetByIDRequest{WidgetID: "wid_1"})

	var apiErr *widget.APIError
	if !errors.As(err, &apiErr) || apiErr.Message != "<html>bad gateway</html>" {
		t.Errorf("error = %v, want *widget.APIError carrying the raw body", err)
	}
}

func TestGetWidgetByID_TransportErrorIsWrapped(t *testing.T) {
	t.Parallel()

	client := newMockClient(t, &mockHTTPClient{err: context.DeadlineExceeded})

	_, err := client.GetWidgetByID(context.Background(), &widget.GetWidgetByIDRequest{WidgetID: "wid_1"})
	if !errors.Is(err, context.DeadlineExceeded) {
		t.Errorf("error = %v, want wrapping context.DeadlineExceeded", err)
	}
}

func TestGetWidgetByID_InvalidInput(t *testing.T) {
	t.Parallel()

	client := newMockClient(t, &mockHTTPClient{status: http.StatusOK, body: `{}`})

	if _, err := client.GetWidgetByID(context.Background(), nil); !errors.Is(err, widget.ErrNilRequest) {
		t.Errorf("nil request: error = %v, want ErrNilRequest", err)
	}

	_, err := client.GetWidgetByID(context.Background(), &widget.GetWidgetByIDRequest{WidgetID: ""})
	if !errors.Is(err, widget.ErrMissingField) {
		t.Errorf("empty id: error = %v, want ErrMissingField", err)
	}
}

func TestGetWidgetByID_MalformedSuccessBody(t *testing.T) {
	t.Parallel()

	client := newMockClient(t, &mockHTTPClient{status: http.StatusOK, body: "not json"})

	if _, err := client.GetWidgetByID(context.Background(), &widget.GetWidgetByIDRequest{WidgetID: "wid_1"}); err == nil {
		t.Fatal("error = nil, want a decode error")
	}
}
