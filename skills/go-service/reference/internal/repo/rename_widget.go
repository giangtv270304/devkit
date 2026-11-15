package repo

import (
	"context"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
)

func (r *PostgresRepo) RenameWidget(ctx context.Context, tenantID int, widgetID, label, updatedBy string) error {
	err := r.db.WithTransaction(ctx, func(ctx context.Context, dbTx pgx.Tx) error {
		const lockQuery = `SELECT id FROM widget WHERE tenant_id = $1 AND id = $2 FOR UPDATE`

		var lockedID string
		if err := dbTx.QueryRow(ctx, lockQuery, tenantID, widgetID).Scan(&lockedID); err != nil {
			return err
		}

		const updateQuery = `UPDATE widget SET label = $3, updated_by = $4 WHERE tenant_id = $1 AND id = $2`

		_, err := dbTx.Exec(ctx, updateQuery, tenantID, widgetID, label, updatedBy)

		return err
	})
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return ErrNotFound
		}

		return fmt.Errorf("failed to rename widget: %w", err)
	}

	return nil
}
