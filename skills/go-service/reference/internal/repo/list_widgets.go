package repo

import (
	"context"
	"fmt"
	"strings"

	"github.com/georgysavva/scany/v2/pgxscan"
)

type ListWidgetsFilter struct {
	TenantID int
	Search   string
	Offset   int
	Limit    int
}

func (r *PostgresRepo) ListWidgets(ctx context.Context, filter ListWidgetsFilter) ([]*Widget, int, error) {
	conditions := []string{"tenant_id = $1"}
	args := []any{filter.TenantID}

	if filter.Search != "" {
		args = append(args, "%"+filter.Search+"%")
		conditions = append(conditions, fmt.Sprintf("label ILIKE $%d", len(args)))
	}

	where := " WHERE " + strings.Join(conditions, " AND ")

	var totalCount int

	if err := pgxscan.Get(ctx, r.db, &totalCount, "SELECT COUNT(*) FROM widget"+where, args...); err != nil {
		return nil, 0, fmt.Errorf("failed to count widgets: %w", err)
	}

	args = append(args, filter.Limit, filter.Offset)
	dataQuery := fmt.Sprintf(
		"SELECT %s FROM widget%s ORDER BY created_at DESC LIMIT $%d OFFSET $%d",
		widgetColumns, where, len(args)-1, len(args),
	)

	var widgets []*Widget

	if err := pgxscan.Select(ctx, r.db, &widgets, dataQuery, args...); err != nil {
		return nil, 0, fmt.Errorf("failed to list widgets: %w", err)
	}

	return widgets, totalCount, nil
}
