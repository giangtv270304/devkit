// Package signer builds the authentication headers for one request.
package signer

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"strconv"
	"time"
)

const (
	HeaderKey       = "X-Api-Key"
	HeaderSignature = "X-Signature"
	HeaderTimestamp = "X-Timestamp"
)

// Params is everything the signature covers. Body is the exact bytes sent on the wire.
type Params struct {
	Method    string
	Path      string
	Query     string
	Body      []byte
	Timestamp time.Time
}

// Message returns the string that gets signed.
func Message(apiKey string, params Params) string {
	timestamp := strconv.FormatInt(params.Timestamp.Unix(), 10)

	return apiKey + params.Method + params.Path + params.Query + string(params.Body) + timestamp
}

// Sign returns the URL-safe base64 HMAC-SHA256 of message.
func Sign(secretKey, message string) string {
	mac := hmac.New(sha256.New, []byte(secretKey))
	mac.Write([]byte(message))

	return base64.RawURLEncoding.EncodeToString(mac.Sum(nil))
}

// Headers returns the headers to add to the request.
func Headers(apiKey, secretKey string, params Params) map[string]string {
	return map[string]string{
		HeaderKey:       apiKey,
		HeaderSignature: Sign(secretKey, Message(apiKey, params)),
		HeaderTimestamp: strconv.FormatInt(params.Timestamp.Unix(), 10),
	}
}
