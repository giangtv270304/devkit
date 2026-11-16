# API spec for the SDK

Lives in the SDK repo, not in the skill. Fill every section from the API documentation or the service source before writing code.

## Identity
- SDK name and package: `widget-go` (`package widget`), `widget-sdk` (npm)
- Sandbox base URL: `https://sandbox.widget.example`
- Production base URL: `https://api.widget.example`
- Where a developer gets keys: <portal URL>

## Authentication
- Headers: `X-Api-Key`, `X-Signature`, `X-Timestamp`
- Signed string: `apiKey + METHOD + path + query + body + timestamp`
- `query`: keys sorted, URL-encoded, without `?`. Empty when there is none.
- `body`: the exact bytes sent. Empty for requests without a body.
- `timestamp`: Unix seconds. Server tolerance: <seconds>
- Algorithm: HMAC-SHA256 with the secret key, base64 URL-safe without padding

## Response shapes
- Success: `{"requestId": "...", "data": {...}}`
- Error: `{"requestId": "...", "error": {"code": "...", "message": "..."}}`
- Endpoints that differ from the above: <list, or "none">

## Endpoints

| Method | Path | SDK method | Request | Response data | Notes |
|---|---|---|---|---|---|
| POST | `/v1/widgets` | `CreateWidget` | body: `name`, `price`, `currency?`, `note?` | `Widget` | `price` is a decimal string |
| GET | `/v1/widgets/{widgetId}` | `GetWidgetByID` | path: `widgetId` | `Widget` | 404 `widget_not_found` |
| GET | `/v1/widgets` | `ListWidgets` | query: `page?`, `pageSize?`, `status?` | `items`, `page`, `pageSize`, `total` | |

## Types
- `Widget`: `id`, `name`, `price` (money, decimal string), `currency`, `status` (`active` \| `archived`), `note` (nullable), `createdAt` (RFC 3339 string)

## Sandbox
- What a test may create, and whether it is cleaned up: <text>
- Fixtures a test needs (existing ids), with the env var that carries each: <list>
