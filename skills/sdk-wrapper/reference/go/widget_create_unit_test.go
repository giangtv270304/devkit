package widget_test

import (
	"context"
	"net/http"
	"testing"

	widget "example.com/widget-go"
)

func TestCreateWidget_Success(t *testing.T) {
	t.Parallel()

	mock := &mockHTTPClient{
		status: http.StatusCreated,
		body:   `{"requestId":"req_1","data":{"id":"wid_1","name":"Bolt","price":"12.50","status":"active"}}`,
	}
	client := newMockClient(t, mock)

	resp, err := client.CreateWidget(context.Background(), &widget.CreateWidgetRequest{Name: "Bolt", Price: "12.50"})
	if err != nil {
		t.Fatalf("CreateWidget: %v", err)
	}

	if resp.Data.ID != "wid_1" {
		t.Errorf("id = %q, want wid_1", resp.Data.ID)
	}

	if mock.lastReq.Method != http.MethodPost || mock.lastReq.URL.Path != "/v1/widgets" {
		t.Errorf("request = %s %s, want POST /v1/widgets", mock.lastReq.Method, mock.lastReq.URL.Path)
	}

	if want := `{"name":"Bolt","price":"12.50"}`; mock.lastBody != want {
		t.Errorf("body = %s, want %s", mock.lastBody, want)
	}

	if got := mock.lastReq.Header.Get("Content-Type"); got != "application/json" {
		t.Errorf("Content-Type = %q, want application/json", got)
	}
}

func TestCreateWidget_ValidationError(t *testing.T) {
	t.Parallel()

	client := newMockClient(t, &mockHTTPClient{
		status: http.StatusBadRequest,
		body:   `{"requestId":"req_2","error":{"code":"invalid_price","message":"price must be a decimal string"}}`,
	})

	_, err := client.CreateWidget(context.Background(), &widget.CreateWidgetRequest{Name: "Bolt", Price: "abc"})
	if err == nil || widget.IsNotFound(err) {
		t.Fatalf("error = %v, want a 400 *widget.APIError", err)
	}
}
