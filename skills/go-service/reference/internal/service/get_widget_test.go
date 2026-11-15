package service_test

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"testing"

	"example.com/acme/example-service/internal/config"
	"example.com/acme/example-service/internal/repo"
	"example.com/acme/example-service/internal/service"
	"example.com/acme/example-service/internal/testutil"
	"github.com/andyle182810/gframework/httpserver"
	gtestutil "github.com/andyle182810/gframework/testutil"
	"github.com/labstack/echo/v5"
)

func TestGetWidget(t *testing.T) {
	t.Parallel()

	widgetRepo := repo.New(testutil.NewPostgres(t))
	svc := service.New(&config.Config{}, widgetRepo) //nolint:exhaustruct // handler under test reads no config

	created, err := widgetRepo.CreateWidget(t.Context(), repo.CreateWidgetParams{TenantID: 7, Label: "main", CreatedBy: "andy"})
	if err != nil {
		t.Fatalf("create widget: %v", err)
	}

	tests := []struct {
		name       string
		tenantID   int
		widgetID   string
		wantStatus int
	}{
		{name: "own widget returns 200", tenantID: 7, widgetID: created.ID, wantStatus: http.StatusOK},
		{name: "widget of another tenant returns 404", tenantID: 8, widgetID: created.ID, wantStatus: http.StatusNotFound},
		{name: "id that is not a uuid returns 400", tenantID: 7, widgetID: "abc", wantStatus: http.StatusBadRequest},
	}

	for _, testCase := range tests {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()

			ctx, rec, _ := gtestutil.SetupEchoContext(t, &gtestutil.Options{ //nolint:exhaustruct // only the fields this request needs
				Method:     http.MethodGet,
				Path:       "/v2/tenants/" + strconv.Itoa(testCase.tenantID) + "/widgets/" + testCase.widgetID,
				PathParams: map[string]string{"tenantId": strconv.Itoa(testCase.tenantID), "widgetId": testCase.widgetID},
			})

			err := httpserver.Wrapper(svc.GetWidget)(ctx)

			if got := statusOf(rec.Code, err); got != testCase.wantStatus {
				t.Fatalf("status = %d, want %d (err: %v)", got, testCase.wantStatus, err)
			}

			if testCase.wantStatus != http.StatusOK {
				return
			}

			var body httpserver.APIResponse[service.WidgetResponse]
			if err := json.Unmarshal(rec.Body.Bytes(), &body); err != nil {
				t.Fatalf("decode body: %v", err)
			}

			if body.Data.ID != created.ID || body.Data.Label != "main" {
				t.Errorf("data = %+v, want id=%s label=main", body.Data, created.ID)
			}
		})
	}
}

func statusOf(recorded int, err error) int {
	var httpErr *echo.HTTPError
	if errors.As(err, &httpErr) {
		return httpErr.Code
	}

	return recorded
}
