package main

import (
	"context"
	"fmt"
	"os"

	"example.com/acme/example-service/internal/config"
	"example.com/acme/example-service/internal/repo"
	"example.com/acme/example-service/internal/service"
	"github.com/andyle182810/gframework/httpserver"
	"github.com/andyle182810/gframework/jwks"
	"github.com/andyle182810/gframework/metricserver"
	"github.com/andyle182810/gframework/middleware"
	"github.com/andyle182810/gframework/postgres"
	"github.com/andyle182810/gframework/runner"
	_ "github.com/joho/godotenv/autoload"
	"github.com/labstack/echo/v5"
	"github.com/rs/zerolog"
)

const serviceName = "example-service"

// @title		Example Service API
// @version	1.0
// @BasePath	/
// .
func main() {
	logger := zerolog.New(os.Stdout).With().Timestamp().Str("service", serviceName).Logger()

	if err := run(logger); err != nil {
		logger.Fatal().Err(err).Msg("application exited with an error")
	}

	logger.Info().Msg("application shutdown complete")
}

func run(log zerolog.Logger) error {
	cfg, err := config.New()
	if err != nil {
		return err
	}

	postgresClient, err := newPostgresClient(cfg)
	if err != nil {
		return err
	}

	jwtAuth, err := newJWTAuth(cfg)
	if err != nil {
		return err
	}

	app := &application{
		cfg:     cfg,
		log:     log,
		service: service.New(cfg, repo.New(postgresClient)),
		jwtAuth: jwtAuth,
	}

	runner.New(
		runner.WithCoreService(app.newMetricServer()),
		runner.WithCoreService(app.newHTTPServer()),
	).Run()

	return nil
}

type application struct {
	cfg     *config.Config
	log     zerolog.Logger
	service *service.Service
	jwtAuth echo.MiddlewareFunc
}

func (app *application) registerRoutes(root *echo.Group) {
	root.GET("/health", func(c *echo.Context) error { return c.NoContent(200) }) //nolint:mnd

	v2 := root.Group("/v2",
		middleware.RequestID(httpserver.RequestIDSkipper(app.cfg.HTTPSkipRequestID)),
		app.jwtAuth,
	)
	v2.POST("/widgets", httpserver.Wrapper(app.service.CreateWidget))
	v2.GET("/tenants/:tenantId/widgets/:widgetId", httpserver.Wrapper(app.service.GetWidget))
}

func (app *application) newHTTPServer() *httpserver.Server {
	svr := httpserver.New(&httpserver.Config{
		Host:         app.cfg.HTTPServerHost,
		Port:         app.cfg.HTTPServerPort,
		EnableCors:   app.cfg.HTTPEnableCORS,
		AllowOrigins: app.cfg.HTTPAllowOrigins,
		BodyLimit:    app.cfg.HTTPBodyLimit,
		ReadTimeout:  app.cfg.HTTPServerReadTimeout,
		WriteTimeout: app.cfg.HTTPServerWriteTimeout,
		GracePeriod:  app.cfg.GracefulShutdownPeriod,
	})
	app.registerRoutes(svr.Root)

	return svr
}

func (app *application) newMetricServer() *metricserver.Server {
	return metricserver.New(&metricserver.Config{
		Host:         app.cfg.MetricServerHost,
		Port:         app.cfg.MetricServerPort,
		ReadTimeout:  app.cfg.MetricServerReadTimeout,
		WriteTimeout: app.cfg.MetricServerWriteTimeout,
		GracePeriod:  app.cfg.GracefulShutdownPeriod,
	})
}

func newJWTAuth(cfg *config.Config) (echo.MiddlewareFunc, error) {
	jwksURL := fmt.Sprintf("%s/realms/%s/protocol/openid-connect/certs", cfg.KeycloakURL.String(), cfg.KeycloakRealm)

	keyFunc, err := jwks.New(context.Background(), []string{jwksURL})
	if err != nil {
		return nil, fmt.Errorf("failed to load keycloak jwks: %w", err)
	}

	return middleware.JWT(keyFunc), nil
}

func newPostgresClient(cfg *config.Config) (*postgres.Postgres, error) {
	if cfg.MigrationEnabled {
		if err := postgres.MigrateUp(cfg.PostgresURL, cfg.MigrationSource); err != nil {
			return nil, fmt.Errorf("failed to run migrations: %w", err)
		}
	}

	postgresClient, err := postgres.New(&postgres.Config{
		URL:                      cfg.PostgresURL,
		MaxConnection:            cfg.PostgresMaxConnection,
		MinConnection:            cfg.PostgresMinConnection,
		MaxConnectionIdleTime:    cfg.PostgresMaxConnectionIdleTime,
		MaxConnectionLifetime:    cfg.PostgresMaxConnectionLifetime,
		HealthCheckPeriod:        cfg.PostgresHealthCheckPeriod,
		ConnectTimeout:           0,
		LogLevel:                 0,
		StatementTimeout:         0,
		LockTimeout:              0,
		IdleInTransactionTimeout: 0,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to initialize postgres client: %w", err)
	}

	return postgresClient, nil
}
