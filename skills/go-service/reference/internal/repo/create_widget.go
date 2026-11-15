package repo

import (
	"context"
	"errors"
	"fmt"

	"github.com/georgysavva/scany/v2/pgxscan"
	"github.com/jackc/pgerrcode"
	"github.com/jackc/pgx/v5/pgconn"
)

type CreateWidgetParams struct {
	TenantID  int
	Label     string
	CreatedBy string
}

func (r *PostgresRepo) CreateWidget(ctx context.Context, params CreateWidgetParams) (*Widget, error) {
	const query = `
		INSERT INTO widget (tenant_id, label, created_by)
		VALUES ($1, $2, $3)
		RETURNING ` + widgetColumns

	var inserted Widget

	err := pgxscan.Get(ctx, r.db, &inserted, query, params.TenantID, params.Label, params.CreatedBy)
	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) && pgErr.Code == pgerrcode.UniqueViolation {
			return nil, ErrDuplicateLabel
		}

		return nil, fmt.Errorf("failed to create widget: %w", err)
	}

	return &inserted, nil
}
