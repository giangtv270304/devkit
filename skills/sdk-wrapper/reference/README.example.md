# widget-go

Go client for the Widget API.

## Install

```bash
go get example.com/widget-go
```

Requires Go 1.23+. No dependencies outside the standard library.

## First call

Get a sandbox key pair from <portal URL>, then:

```go
client, err := widget.NewClient(widget.SandboxBaseURL, apiKey, secretKey)
if err != nil {
	log.Fatal(err)
}

resp, err := client.CreateWidget(ctx, &widget.CreateWidgetRequest{Name: "Bolt", Price: "12.50"})
if err != nil {
	log.Fatal(err)
}

fmt.Println(resp.Data.ID)
```

A full program is in `example/quickstart`.

## Authentication

Every request is signed with the key pair; the client does it for you. The secret key is for servers only: never ship it in a browser or a mobile app.

| Environment | Base URL |
|---|---|
| Sandbox | `widget.SandboxBaseURL` |
| Production | `widget.ProductionBaseURL` |

## Flows

One section per main flow: the steps in order, then the code for each step.

### Create a widget and read it back

1. `CreateWidget` returns the new id.
2. `GetWidgetByID` returns the widget.

## Methods

| Method | What it does |
|---|---|
| `CreateWidget` | Creates a widget |
| `GetWidgetByID` | Returns one widget |
| `ListWidgets` | Returns one page of widgets |

Amounts such as `Price` are decimal strings (`"12.50"`). Do not parse them into a float.

## Errors

Every response with status 400 or above is a `*widget.APIError`.

```go
var apiErr *widget.APIError
if errors.As(err, &apiErr) {
	log.Printf("%s (code %s, request %s)", apiErr.Message, apiErr.Code, apiErr.RequestID)
}

if widget.IsNotFound(err) {
	// 404
}
```

Give `RequestID` to support when you report a problem. A timeout is `errors.Is(err, context.DeadlineExceeded)`.

## Configuration

```go
client, err := widget.NewClient(baseURL, apiKey, secretKey,
	widget.WithHTTPClient(&http.Client{Timeout: 10 * time.Second}),
	widget.WithLogger(slog.Default()),
)
```

The default timeout is 30 seconds. Debug logs carry the method, URL and status, never headers or bodies.

## Tests

```bash
go test ./...
```

Sandbox tests are skipped unless the variables in `.env.example` are set:

```bash
go test -run TestSandbox_ ./...
```

They create widgets named `sdk-sandbox-test` in the sandbox and never run against production.

## Versioning

Semantic versioning. Breaking changes are listed in the release notes of each major version.
