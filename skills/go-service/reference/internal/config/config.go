package config

import (
	"fmt"
	"net/url"
	"time"

	"github.com/caarlos0/env/v11"
)

type Config struct {
	GracefulShutdownPeriod time.Duration `env:"GRACEFUL_SHUTDOWN_PERIOD" envDefault:"30s"`
	LogLevel               string        `env:"LOG_LEVEL"                envDefault:"info"`

	HTTPServerHost         string        `env:"HTTP_SERVER_HOST"          envDefault:"0.0.0.0"`
	HTTPServerPort         int           `env:"HTTP_SERVER_PORT"          envDefault:"8080"`
	HTTPServerReadTimeout  time.Duration `env:"HTTP_SERVER_READ_TIMEOUT"  envDefault:"30s"`
	HTTPServerWriteTimeout time.Duration `env:"HTTP_SERVER_WRITE_TIMEOUT" envDefault:"30s"`
	HTTPEnableCORS         bool          `env:"HTTP_ENABLE_CORS"          envDefault:"false"`
	HTTPBodyLimit          string        `env:"HTTP_BODY_LIMIT"           envDefault:"100K"`
	HTTPSkipRequestID      bool          `env:"HTTP_SKIP_REQUEST_ID"      envDefault:"false"`
	HTTPAllowOrigins       []string      `env:"HTTP_ALLOW_ORIGINS"        envDefault:"*"       envSeparator:""`

	MetricServerHost         string        `env:"METRIC_SERVER_HOST"          envDefault:"0.0.0.0"`
	MetricServerPort         int           `env:"METRIC_SERVER_PORT"          envDefault:"8082"`
	MetricServerReadTimeout  time.Duration `env:"METRIC_SERVER_READ_TIMEOUT"  envDefault:"30s"`
	MetricServerWriteTimeout time.Duration `env:"METRIC_SERVER_WRITE_TIMEOUT" envDefault:"30s"`

	PostgresURL                   string        `env:"POSTGRES_URL,required"`
	PostgresMaxConnection         int32         `env:"POSTGRES_MAX_CONNECTION"           envDefault:"10"`
	PostgresMinConnection         int32         `env:"POSTGRES_MIN_CONNECTION"           envDefault:"0"`
	PostgresMaxConnectionIdleTime time.Duration `env:"POSTGRES_MAX_CONNECTION_IDLE_TIME" envDefault:"15m"`
	PostgresMaxConnectionLifetime time.Duration `env:"POSTGRES_MAX_CONNECTION_LIFETIME"  envDefault:"1h"`
	PostgresHealthCheckPeriod     time.Duration `env:"POSTGRES_HEALTH_CHECK_PERIOD"      envDefault:"1m"`
	MigrationEnabled              bool          `env:"MIGRATION_ENABLED"                 envDefault:"false"`
	MigrationSource               string        `env:"MIGRATION_SOURCE"                  envDefault:"file://db/migrations"`

	KeycloakURL            url.URL  `env:"KEYCLOAK_URL,required"`
	KeycloakRealm          string   `env:"KEYCLOAK_REALM,required"`
	KeycloakAllowedClients []string `env:"KEYCLOAK_ALLOWED_CLIENTS,required" envSeparator:""`
}

func New() (*Config, error) {
	cfg := new(Config)

	if err := env.Parse(cfg); err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	return cfg, nil
}
