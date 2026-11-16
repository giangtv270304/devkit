// Package widget is a Go client for the Widget API.
//
//	client, err := widget.NewClient(widget.SandboxBaseURL, apiKey, secretKey)
//	if err != nil {
//		return err
//	}
//
//	resp, err := client.CreateWidget(ctx, &widget.CreateWidgetRequest{Name: "Bolt", Price: "12.50"})
package widget

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"example.com/widget-go/signer"
)

const (
	Version = "0.1.0"

	SandboxBaseURL    = "https://sandbox.widget.example"
	ProductionBaseURL = "https://api.widget.example"

	DefaultTimeout = 30 * time.Second

	userAgent = "widget-go/" + Version
)

var (
	ErrEmptyBaseURL   = errors.New("widget: baseURL is required")
	ErrEmptyAPIKey    = errors.New("widget: apiKey is required")
	ErrEmptySecretKey = errors.New("widget: secretKey is required")
	ErrNilRequest     = errors.New("widget: request is nil")
	ErrMissingField   = errors.New("widget: required field is empty")
)

// HTTPClient is satisfied by *http.Client and by a test double.
type HTTPClient interface {
	Do(req *http.Request) (*http.Response, error)
}

// Logger is satisfied by *slog.Logger.
type Logger interface {
	Debug(msg string, args ...any)
}

type Option func(*Client)

// Client calls the Widget API. Create one with NewClient and reuse it.
type Client struct {
	baseURL    string
	apiKey     string
	secretKey  string
	httpClient HTTPClient
	logger     Logger
	now        func() time.Time
}

// WithHTTPClient replaces the default client (timeout DefaultTimeout).
func WithHTTPClient(httpClient HTTPClient) Option {
	return func(c *Client) { c.httpClient = httpClient }
}

// WithLogger turns on debug logs of method, URL and status. Bodies and headers are never logged.
func WithLogger(logger Logger) Option {
	return func(c *Client) { c.logger = logger }
}

func NewClient(baseURL, apiKey, secretKey string, opts ...Option) (*Client, error) {
	if baseURL == "" {
		return nil, ErrEmptyBaseURL
	}

	if apiKey == "" {
		return nil, ErrEmptyAPIKey
	}

	if secretKey == "" {
		return nil, ErrEmptySecretKey
	}

	client := &Client{
		baseURL:    strings.TrimRight(baseURL, "/"),
		apiKey:     apiKey,
		secretKey:  secretKey,
		httpClient: &http.Client{Timeout: DefaultTimeout},
		logger:     nil,
		now:        time.Now,
	}

	for _, opt := range opts {
		opt(client)
	}

	return client, nil
}

func call[T any](ctx context.Context, c *Client, req request) (*Response[T], error) {
	resp := new(Response[T])
	if err := c.execute(ctx, req, resp); err != nil {
		return nil, err
	}

	return resp, nil
}

func (c *Client) execute(ctx context.Context, req request, out any) error {
	var body []byte

	if req.Body != nil {
		encoded, err := json.Marshal(req.Body)
		if err != nil {
			return fmt.Errorf("widget: encode request body: %w", err)
		}

		body = encoded
	}

	query := req.Query.Encode()

	fullURL := c.baseURL + req.Path
	if query != "" {
		fullURL += "?" + query
	}

	httpReq, err := http.NewRequestWithContext(ctx, req.Method, fullURL, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("widget: build request: %w", err)
	}

	httpReq.Header.Set("Accept", "application/json")
	httpReq.Header.Set("User-Agent", userAgent)

	if body != nil {
		httpReq.Header.Set("Content-Type", "application/json")
	}

	// The signature covers the exact bytes sent: sign after encoding, never re-encode.
	signed := signer.Headers(c.apiKey, c.secretKey, signer.Params{
		Method:    req.Method,
		Path:      req.Path,
		Query:     query,
		Body:      body,
		Timestamp: c.now(),
	})
	for key, value := range signed {
		httpReq.Header.Set(key, value)
	}

	resp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return fmt.Errorf("widget: send %s %s: %w", req.Method, req.Path, err)
	}
	defer func() { _ = resp.Body.Close() }()

	raw, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("widget: read response of %s %s: %w", req.Method, req.Path, err)
	}

	if c.logger != nil {
		c.logger.Debug("widget request", "method", req.Method, "url", fullURL, "status", resp.StatusCode)
	}

	if resp.StatusCode >= http.StatusBadRequest {
		return newAPIError(resp.StatusCode, raw)
	}

	if err := json.Unmarshal(raw, out); err != nil {
		return fmt.Errorf("widget: decode response of %s %s (status %d): %w", req.Method, req.Path, resp.StatusCode, err)
	}

	return nil
}
