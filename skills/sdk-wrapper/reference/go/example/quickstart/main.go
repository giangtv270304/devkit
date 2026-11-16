// Quickstart: create a widget in the sandbox, then read it back.
package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"
	"time"

	widget "example.com/widget-go"
)

func main() {
	client, err := widget.NewClient(
		widget.SandboxBaseURL,
		os.Getenv("WIDGET_SANDBOX_API_KEY"),
		os.Getenv("WIDGET_SANDBOX_SECRET_KEY"),
	)
	if err != nil {
		log.Fatalf("new client: %v", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	created, err := client.CreateWidget(ctx, &widget.CreateWidgetRequest{Name: "Bolt", Price: "12.50"})
	if err != nil {
		var apiErr *widget.APIError
		if errors.As(err, &apiErr) {
			log.Fatalf("create widget: %s (code %s, request %s)", apiErr.Message, apiErr.Code, apiErr.RequestID)
		}

		log.Fatalf("create widget: %v", err)
	}

	fetched, err := client.GetWidgetByID(ctx, &widget.GetWidgetByIDRequest{WidgetID: created.Data.ID})
	if err != nil {
		log.Fatalf("get widget: %v", err)
	}

	fmt.Printf("%s %s %s\n", fetched.Data.ID, fetched.Data.Name, fetched.Data.Price)
}
