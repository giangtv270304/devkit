package service

import (
	"example.com/acme/example-service/internal/config"
	"example.com/acme/example-service/internal/repo"
)

type Service struct {
	cfg  *config.Config
	repo *repo.PostgresRepo
}

func New(cfg *config.Config, repository *repo.PostgresRepo) *Service {
	return &Service{
		cfg:  cfg,
		repo: repository,
	}
}
