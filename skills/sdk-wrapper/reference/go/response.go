package widget

// Response is the envelope of every successful call.
type Response[T any] struct {
	RequestID string `json:"requestId"`
	Data      T      `json:"data"`
}
