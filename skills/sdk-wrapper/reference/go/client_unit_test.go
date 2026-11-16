package widget_test

import (
	"errors"
	"testing"

	widget "example.com/widget-go"
)

func TestNewClient_RequiredArguments(t *testing.T) {
	t.Parallel()

	testCases := []struct {
		name      string
		baseURL   string
		apiKey    string
		secretKey string
		want      error
	}{
		{"empty base url", "", "key", "secret", widget.ErrEmptyBaseURL},
		{"empty api key", "https://x.example", "", "secret", widget.ErrEmptyAPIKey},
		{"empty secret key", "https://x.example", "key", "", widget.ErrEmptySecretKey},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()

			_, err := widget.NewClient(testCase.baseURL, testCase.apiKey, testCase.secretKey)
			if !errors.Is(err, testCase.want) {
				t.Errorf("error = %v, want %v", err, testCase.want)
			}
		})
	}
}
