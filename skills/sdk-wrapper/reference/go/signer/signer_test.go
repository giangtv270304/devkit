package signer_test

import (
	"encoding/json"
	"os"
	"testing"
	"time"

	"example.com/widget-go/signer"
)

type vector struct {
	Name      string `json:"name"`
	APIKey    string `json:"apiKey"`
	SecretKey string `json:"secretKey"`
	Method    string `json:"method"`
	Path      string `json:"path"`
	Query     string `json:"query"`
	Body      string `json:"body"`
	Timestamp int64  `json:"timestamp"`
	Signature string `json:"signature"`
}

func TestHeaders_SharedVectors(t *testing.T) {
	t.Parallel()

	raw, err := os.ReadFile("../../signature-vectors.json")
	if err != nil {
		t.Fatalf("read vectors: %v", err)
	}

	var vectors []vector
	if err := json.Unmarshal(raw, &vectors); err != nil {
		t.Fatalf("decode vectors: %v", err)
	}

	for _, testCase := range vectors {
		t.Run(testCase.Name, func(t *testing.T) {
			t.Parallel()

			headers := signer.Headers(testCase.APIKey, testCase.SecretKey, signer.Params{
				Method:    testCase.Method,
				Path:      testCase.Path,
				Query:     testCase.Query,
				Body:      []byte(testCase.Body),
				Timestamp: time.Unix(testCase.Timestamp, 0),
			})

			if got := headers[signer.HeaderSignature]; got != testCase.Signature {
				t.Errorf("signature = %q, want %q", got, testCase.Signature)
			}
		})
	}
}
