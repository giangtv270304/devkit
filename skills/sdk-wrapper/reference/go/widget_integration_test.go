package widget_test

import (
	"context"
	"testing"
	"time"

	widget "example.com/widget-go"
)

const sandboxTimeout = 30 * time.Second

func TestSandbox_ListWidgets(t *testing.T) {
	t.Parallel()

	client := newSandboxClient(t)

	ctx, cancel := context.WithTimeout(context.Background(), sandboxTimeout)
	defer cancel()

	resp, err := client.ListWidgets(ctx, &widget.ListWidgetsRequest{Page: 1, PageSize: 1, Status: ""})
	if err != nil {
		t.Fatalf("ListWidgets: %v", err)
	}

	if resp.RequestID == "" {
		t.Error("requestId is empty")
	}
}

func TestSandbox_CreateThenGetWidget(t *testing.T) {
	t.Parallel()

	client := newSandboxClient(t)

	ctx, cancel := context.WithTimeout(context.Background(), sandboxTimeout)
	defer cancel()

	created, err := client.CreateWidget(ctx, &widget.CreateWidgetRequest{
		Name:     "sdk-sandbox-test",
		Price:    "1.00",
		Currency: "",
		Note:     nil,
	})
	if err != nil {
		t.Fatalf("CreateWidget: %v", err)
	}

	fetched, err := client.GetWidgetByID(ctx, &widget.GetWidgetByIDRequest{WidgetID: created.Data.ID})
	if err != nil {
		t.Fatalf("GetWidgetByID: %v", err)
	}

	if fetched.Data.ID != created.Data.ID || fetched.Data.Price != "1.00" {
		t.Errorf("fetched = %+v, want id %s and price 1.00", fetched.Data, created.Data.ID)
	}
}

func TestSandbox_GetWidgetByID_NotFound(t *testing.T) {
	t.Parallel()

	client := newSandboxClient(t)

	ctx, cancel := context.WithTimeout(context.Background(), sandboxTimeout)
	defer cancel()

	_, err := client.GetWidgetByID(ctx, &widget.GetWidgetByIDRequest{WidgetID: "wid_does_not_exist"})
	if !widget.IsNotFound(err) {
		t.Errorf("error = %v, want a 404 *widget.APIError", err)
	}
}
