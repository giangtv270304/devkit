package widget

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
)

// APIError is returned for every response with status 400 or above.
// Read it with errors.As; give RequestID to support.
type APIError struct {
	StatusCode int
	Code       string
	Message    string
	RequestID  string
	Body       []byte
}

func (e *APIError) Error() string {
	return fmt.Sprintf("widget: api error: status=%d code=%s message=%s request_id=%s",
		e.StatusCode, e.Code, e.Message, e.RequestID)
}

type errorBody struct {
	RequestID string `json:"requestId"`
	Error     struct {
		Code    string `json:"code"`
		Message string `json:"message"`
	} `json:"error"`
}

func newAPIError(statusCode int, raw []byte) *APIError {
	apiErr := &APIError{StatusCode: statusCode, Code: "", Message: string(raw), RequestID: "", Body: raw}

	var parsed errorBody
	if err := json.Unmarshal(raw, &parsed); err == nil && parsed.Error.Message != "" {
		apiErr.Code = parsed.Error.Code
		apiErr.Message = parsed.Error.Message
		apiErr.RequestID = parsed.RequestID
	}

	return apiErr
}

func hasStatus(err error, statusCode int) bool {
	var apiErr *APIError

	return errors.As(err, &apiErr) && apiErr.StatusCode == statusCode
}

func IsNotFound(err error) bool     { return hasStatus(err, http.StatusNotFound) }
func IsUnauthorized(err error) bool { return hasStatus(err, http.StatusUnauthorized) }
func IsConflict(err error) bool     { return hasStatus(err, http.StatusConflict) }
func IsRateLimited(err error) bool  { return hasStatus(err, http.StatusTooManyRequests) }
