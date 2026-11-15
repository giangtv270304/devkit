package service

import (
	"errors"
	"net/http"

	"example.com/acme/example-service/internal/repo"
	"github.com/andyle182810/gframework/httpserver"
	"github.com/labstack/echo/v5"
	"github.com/rs/zerolog"
)

type CreateWidgetRequest struct {
	TenantID  int    `example:"10"          json:"tenantId"  validate:"required"`
	Label     string `example:"Main widget" json:"label"     validate:"required,min=2,max=255"`
	CreatedBy string `example:"andy"        json:"createdBy" validate:"required"`
}

// CreateWidget godoc
//
//	@Summary		Create a widget
//	@Description	Create a widget for a tenant. A label is unique per tenant.
//	@Tags			widgets
//	@Accept			json
//	@Produce		json
//	@Param			X-Request-Id	header		string									true	"Request ID (UUID)"
//	@Param			request			body		CreateWidgetRequest						true	"Widget to create"
//	@Success		200				{object}	httpserver.APIResponse[WidgetResponse]	"Widget created"
//	@Failure		400				{object}	echo.HTTPError							"Invalid input"
//	@Failure		409				{object}	echo.HTTPError							"Label already used by this tenant"
//	@Failure		500				{object}	echo.HTTPError							"Internal server error"
//	@Router			/v2/widgets [post]
func (s *Service) CreateWidget(ctx *echo.Context, req *CreateWidgetRequest) (any, *echo.HTTPError) {
	delegator := func(
		log zerolog.Logger,
		ctx *echo.Context,
		req *CreateWidgetRequest,
	) (*httpserver.HandlerResponse[WidgetResponse], *echo.HTTPError) {
		handler := NewCreateWidgetHandler(log, s.repo)

		return handler.Handle(ctx, req)
	}

	return httpserver.ExecuteStandardized(ctx, req, "CreateWidget", delegator)
}

type CreateWidgetHandler struct {
	log  zerolog.Logger
	repo *repo.PostgresRepo
}

func NewCreateWidgetHandler(log zerolog.Logger, repository *repo.PostgresRepo) *CreateWidgetHandler {
	return &CreateWidgetHandler{
		log:  log,
		repo: repository,
	}
}

func (h *CreateWidgetHandler) Handle(
	ctx *echo.Context,
	req *CreateWidgetRequest,
) (*httpserver.HandlerResponse[WidgetResponse], *echo.HTTPError) {
	reqCtx := ctx.Request().Context()

	inserted, err := h.repo.CreateWidget(reqCtx, repo.CreateWidgetParams{
		TenantID:  req.TenantID,
		Label:     req.Label,
		CreatedBy: req.CreatedBy,
	})
	if err != nil {
		if errors.Is(err, repo.ErrDuplicateLabel) {
			return nil, echo.NewHTTPError(http.StatusConflict, "widget with this label already exists for tenant")
		}

		return nil, httpserver.InternalError(err, "failed to create widget")
	}

	h.log.Info().
		Str("widget_id", inserted.ID).
		Int("tenant_id", inserted.TenantID).
		Msg("widget created")

	return httpserver.NewResponse(toWidgetResponse(inserted)), nil
}
