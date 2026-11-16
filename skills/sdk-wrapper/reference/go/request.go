package widget

import "net/url"

type request struct {
	Method string
	Path   string
	Query  url.Values
	Body   any
}
