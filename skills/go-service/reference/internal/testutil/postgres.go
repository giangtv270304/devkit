package testutil

import (
	"testing"
	"time"

	"github.com/andyle182810/gframework/postgres"
	gtestutil "github.com/andyle182810/gframework/testutil"
)

const (
	migrationsPath     = "../../db/migrations"
	maxTestConnections = 4
)

// NewPostgres needs Docker and is skipped with -short.
func NewPostgres(t *testing.T) *postgres.Postgres {
	t.Helper()

	if testing.Short() {
		t.Skip("needs Docker; skipped with -short")
	}

	container := gtestutil.SetupPostgresContainer(t)

	postgresClient, err := postgres.New(&postgres.Config{
		URL:                      container.ConnectionString(),
		MaxConnection:            maxTestConnections,
		MinConnection:            0,
		MaxConnectionIdleTime:    time.Minute,
		MaxConnectionLifetime:    time.Hour,
		HealthCheckPeriod:        time.Minute,
		ConnectTimeout:           10 * time.Second, //nolint:mnd
		LogLevel:                 0,
		StatementTimeout:         0,
		LockTimeout:              0,
		IdleInTransactionTimeout: 0,
	})
	if err != nil {
		t.Fatalf("connect postgres: %v", err)
	}

	t.Cleanup(postgresClient.Close)

	if err := gtestutil.RunMigrations(t.Context(), postgresClient, migrationsPath); err != nil {
		t.Fatalf("run migrations: %v", err)
	}

	return postgresClient
}
