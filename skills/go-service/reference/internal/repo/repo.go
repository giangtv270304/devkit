package repo

import (
	"errors"

	"github.com/andyle182810/gframework/postgres"
)

var (
	ErrNotFound       = errors.New("record not found")
	ErrDuplicateLabel = errors.New("label already exists for tenant")
)

type PostgresRepo struct {
	db *postgres.Postgres
}

func New(db *postgres.Postgres) *PostgresRepo {
	return &PostgresRepo{db: db}
}
