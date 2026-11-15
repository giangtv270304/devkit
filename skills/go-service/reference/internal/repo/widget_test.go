package repo_test

import (
	"errors"
	"testing"

	"example.com/acme/example-service/internal/repo"
	"example.com/acme/example-service/internal/testutil"
)

func TestWidgetRepo(t *testing.T) {
	t.Parallel()

	widgetRepo := repo.New(testutil.NewPostgres(t))

	t.Run("get returns the widget that create inserted", func(t *testing.T) {
		t.Parallel()

		created, err := widgetRepo.CreateWidget(t.Context(), repo.CreateWidgetParams{TenantID: 1, Label: "main", CreatedBy: "andy"})
		if err != nil {
			t.Fatalf("create widget: %v", err)
		}

		got, err := widgetRepo.GetWidget(t.Context(), 1, created.ID)
		if err != nil {
			t.Fatalf("get widget: %v", err)
		}

		if got.Label != "main" || got.TenantID != 1 || got.CreatedBy != "andy" {
			t.Errorf("got %+v, want label=main tenant=1 createdBy=andy", got)
		}
	})

	t.Run("same label for the same tenant returns ErrDuplicateLabel", func(t *testing.T) {
		t.Parallel()

		params := repo.CreateWidgetParams{TenantID: 2, Label: "dup", CreatedBy: "andy"}

		if _, err := widgetRepo.CreateWidget(t.Context(), params); err != nil {
			t.Fatalf("first create: %v", err)
		}

		_, err := widgetRepo.CreateWidget(t.Context(), params)
		if !errors.Is(err, repo.ErrDuplicateLabel) {
			t.Errorf("second create error = %v, want ErrDuplicateLabel", err)
		}
	})

	t.Run("widget of another tenant returns ErrNotFound", func(t *testing.T) {
		t.Parallel()

		created, err := widgetRepo.CreateWidget(t.Context(), repo.CreateWidgetParams{TenantID: 3, Label: "mine", CreatedBy: "andy"})
		if err != nil {
			t.Fatalf("create widget: %v", err)
		}

		_, err = widgetRepo.GetWidget(t.Context(), 4, created.ID)
		if !errors.Is(err, repo.ErrNotFound) {
			t.Errorf("get error = %v, want ErrNotFound", err)
		}
	})
}
