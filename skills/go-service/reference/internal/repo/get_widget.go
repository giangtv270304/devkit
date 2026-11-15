package repo

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/jackc/pgx/v5"
)

type Widget struct {
	ID        string    `db:"id"`
	TenantID  int       `db:"tenant_id"`
	Label     string    `db:"label"`
	CreatedBy string    `db:"created_by"`
	CreatedAt time.Time `db:"created_at"`
	UpdatedAt time.Time `db:"updated_at"`
}

// Must list every db tag of Widget.
const widgetColumns = `id, tenant_id, label, created_by, created_at, updated_at`

func (r *PostgresRepo) GetWidget(ctx context.Context, tenantID int, widgetID string) (*Widget, error) {
	const query = `
		SELECT ` + widgetColumns + `
		FROM widget
		WHERE tenant_id = $1 AND id = $2
	`

	var widget Widget

	if err := pgxscan.Get(ctx, r.db, &widget, query, tenantID, widgetID); err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return nil, ErrNotFound
		}

		return nil, fmt.Errorf("failed to get widget: %w", err)
	}

	return &widget, nil
}
