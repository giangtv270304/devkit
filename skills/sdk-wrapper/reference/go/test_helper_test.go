package widget_test

import (
	"io"
	"net/http"
	"os"
	"strings"
	"testing"

	widget "example.com/widget-go"
)

const (
	envSandboxBaseURL   = "WIDGET_SANDBOX_BASE_URL"
	envSandboxAPIKey    = "WIDGET_SANDBOX_API_KEY"
	envSandboxSecretKey = "WIDGET_SANDBOX_SECRET_KEY"
)

type mockHTTPClient struct {
	status   int
	body     string
	err      error
	lastReq  *http.Request
	lastBody string
}

func (m *mockHTTPClient) Do(req *http.Request) (*http.Response, error) {
	m.lastReq = req

	if req.Body != nil {
		raw, _ := io.ReadAll(req.Body)
		m.lastBody = string(raw)
	}

	if m.err != nil {
		return nil, m.err
	}

	return &http.Response{
		StatusCode: m.status,
		Header:     http.Header{},
		Body:       io.NopCloser(strings.NewReader(m.body)),
	}, nil
}

func newMockClient(t *testing.T, mock *mockHTTPClient) *widget.Client {
	t.Helper()

	client, err := widget.NewClient("https://mock.widget.example", "test-api-key", "test-secret-key",
		widget.WithHTTPClient(mock))
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	return client
}

func newSandboxClient(t *testing.T) *widget.Client {
	t.Helper()

	apiKey := os.Getenv(envSandboxAPIKey)
	secretKey := os.Getenv(envSandboxSecretKey)

	if apiKey == "" || secretKey == "" {
		t.Skipf("sandbox test skipped: set %s and %s", envSandboxAPIKey, envSandboxSecretKey)
	}

	baseURL := os.Getenv(envSandboxBaseURL)
	if baseURL == "" {
		baseURL = widget.SandboxBaseURL
	}

	if baseURL == widget.ProductionBaseURL {
		t.Fatalf("%s points at production; sandbox tests never run there", envSandboxBaseURL)
	}

	client, err := widget.NewClient(baseURL, apiKey, secretKey)
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	return client
}
