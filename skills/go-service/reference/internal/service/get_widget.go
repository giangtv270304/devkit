package service

import (
	"errors"
	"net/http"
	"time"

	"example.com/acme/example-service/internal/repo"
	"github.com/andyle182810/gframework/httpserver"
	"github.com/labstack/echo/v5"
	"github.com/rs/zerolog"
)

type GetWidgetRequest struct {
	TenantID int    `example:"10"                                   param:"tenantId" validate:"required"`
	WidgetID string `example:"3e7a4923-0acb-4b1c-b97f-ddebb4dbfd9a" param:"widgetId" validate:"required,uuid"`
}

type WidgetResponse struct {
	ID        string    `example:"3e7a4923-0acb-4b1c-b97f-ddebb4dbfd9a" json:"id"`
	TenantID  int       `example:"10"                                   json:"tenantId"`
	Label     string    `example:"Main widget"                          json:"label"`
	CreatedBy string    `example:"andy"                                 json:"createdBy"`
	CreatedAt time.Time `example:"2026-01-01T00:00:00Z"                 json:"createdAt"`
	UpdatedAt time.Time `example:"2026-01-01T00:00:00Z"                 json:"updatedAt"`
}

func toWidgetResponse(widget *repo.Widget) WidgetResponse {
	return WidgetResponse{
		ID:        widget.ID,
		TenantID:  widget.TenantID,
		Label:     widget.Label,
		CreatedBy: widget.CreatedBy,
		CreatedAt: widget.CreatedAt,
		UpdatedAt: widget.UpdatedAt,
	}
}

// GetWidget godoc
//
//	@Summary		Get a widget
//	@Description	Get one widget of a tenant.
//	@Tags			widgets
//	@Produce		json
//	@Param			X-Request-Id	header		string									true	"Request ID (UUID)"
//	@Param			tenantId		path		int										true	"Tenant ID"
//	@Param			widgetId		path		string									true	"Widget ID (UUID)"
//	@Success		200				{object}	httpserver.APIResponse[WidgetResponse]	"Widget"
//	@Failure		400				{object}	echo.HTTPError							"Invalid input"
//	@Failure		404				{object}	echo.HTTPError							"Widget not found"
//	@Failure		500				{object}	echo.HTTPError							"Internal server error"
//	@Router			/v2/tenants/{tenantId}/widgets/{widgetId} [get]
func (s *Service) GetWidget(ctx *echo.Context, req *GetWidgetRequest) (any, *echo.HTTPError) {
	delegator := func(
		log zerolog.Logger,
		ctx *echo.Context,
		req *GetWidgetRequest,
	) (*httpserver.HandlerResponse[WidgetResponse], *echo.HTTPError) {
		handler := NewGetWidgetHandler(log, s.repo)

		return handler.Handle(ctx, req)
	}

	return httpserver.ExecuteStandardized(ctx, req, "GetWidget", delegator)
}

type GetWidgetHandler struct {
	log  zerolog.Logger
	repo *repo.PostgresRepo
}

func NewGetWidgetHandler(log zerolog.Logger, repository *repo.PostgresRepo) *GetWidgetHandler {
	return &GetWidgetHandler{
		log:  log,
		repo: repository,
	}
}

func (h *GetWidgetHandler) Handle(
	ctx *echo.Context,
	req *GetWidgetRequest,
) (*httpserver.HandlerResponse[WidgetResponse], *echo.HTTPError) {
	widget, err := h.repo.GetWidget(ctx.Request().Context(), req.TenantID, req.WidgetID)
	if err != nil {
		if errors.Is(err, repo.ErrNotFound) {
			return nil, echo.NewHTTPError(http.StatusNotFound, "widget not found")
		}

		return nil, httpserver.InternalError(err, "failed to get widget")
	}

	return httpserver.NewResponse(toWidgetResponse(widget)), nil
}
