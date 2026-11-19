---
name: go-service
description: Quy ước bắt buộc khi viết hoặc sửa code Go trong một backend service. Gồm thư viện được dùng, cách tổ chức file, mẫu handler/repo/test, cách xử lý lỗi, log, SQL, migration và các bẫy của linter. Dùng trước khi viết bất kỳ file .go nào, khi thêm endpoint, query, migration, test, hoặc khi tạo service Go mới.
---

# go-service: cách viết một backend service bằng Go

Skill này là quy ước cứng. Code mẫu nằm trong `reference/` cạnh file này. Code mẫu đã build, chạy test trên Postgres thật và qua `golangci-lint` v1.64.8 với một cấu hình chặt. **Chép cấu trúc của code mẫu, đừng tự nghĩ ra cấu trúc mới.**

| Cần viết | Chép từ |
|---|---|
| Endpoint (request, response, swag, handler) | `reference/internal/service/create_widget.go`, `get_widget.go` |
| Response và hàm chuyển sang response dùng chung | trong `reference/internal/service/get_widget.go`; `create_widget.go` lấy ra dùng |
| Service gốc | `reference/internal/service/service.go` |
| Repo: struct, lỗi chung | `reference/internal/repo/repo.go` |
| Query lấy một dòng / thêm dòng / danh sách có lọc / transaction | `reference/internal/repo/get_widget.go`, `create_widget.go`, `list_widgets.go`, `rename_widget.go` |
| Struct của bảng và danh sách cột | trong `reference/internal/repo/get_widget.go`; các file query khác lấy ra dùng |
| Config | `reference/internal/config/config.go` |
| main.go: nối mọi thứ, route | `reference/main.go` |
| Migration | `reference/db/migrations/000001_create_widget_table.*.sql` |
| Test repo, test handler, helper Postgres | `reference/internal/repo/widget_test.go`, `reference/internal/service/get_widget_test.go`, `reference/internal/testutil/postgres.go` |

"widget" chỉ là tên giả. Đổi thành tên thật của tài nguyên.

**Repo đã có sẵn code:** có 3 quy ước mà mỗi repo đang làm một kiểu: khóa log, cách báo "không tìm thấy", và cách bọc lỗi. Ví dụ có repo dùng khóa log camelCase; có repo trả `(nil, false, nil)` và bọc lỗi ngắn (`"get card: %w"`). Mục "Go notes" trong `.claude/project.md` của dự án ghi repo nào theo kiểu nào, nếu có. Với 3 quy ước này, code mới theo kiểu mà **đa số code của repo đó** đang dùng, để một repo không bị trộn hai kiểu. Đếm nhanh bằng grep trước khi viết, ví dụ `grep -rc 'nil, false, nil' internal/repo`. Nói ra lựa chọn này khi bàn giao. Repo mới thì theo skill. Mọi quy ước khác theo skill. Không sửa code cũ cho giống skill, trừ khi người dùng yêu cầu.

## 1. Thư viện

Chỉ dùng các thư viện sau. Muốn thêm thư viện khác thì hỏi người dùng trước.

| Việc | Thư viện |
|---|---|
| HTTP server, route, middleware, phân trang, lỗi HTTP, runner, metric | `github.com/andyle182810/gframework` (`httpserver`, `middleware`, `runner`, `metricserver`, `jwks`, `keycloak`) |
| Web framework | `github.com/labstack/echo/v5` (repo cũ có thể còn echo v4: giữ nguyên bản đang dùng) |
| Postgres | `gframework/postgres` (pgx v5 bên dưới) + `github.com/georgysavva/scany/v2/pgxscan` |
| Mã lỗi Postgres | `github.com/jackc/pgerrcode` + `pgconn.PgError` |
| Migration | golang-migrate, file trong `db/migrations` |
| Cache, khóa phân tán | `gframework/valkey`, `gframework/distlock` |
| Hàng đợi việc chạy nền | `gframework/taskqueue` |
| Gọi HTTP ra ngoài | `gframework/httpclient` |
| Config | `github.com/caarlos0/env/v11` + `github.com/joho/godotenv/autoload` |
| Log | `github.com/rs/zerolog` |
| Tiền | `github.com/shopspring/decimal`. Không bao giờ dùng `float64` cho tiền |
| Validate request | tag `validate` (go-playground/validator, gframework đã gắn sẵn) |
| API doc | swag (`make api-doc`) |
| Test | `testing` của thư viện chuẩn + `gframework/testutil`. Không dùng testify, gomock hay pgxmock trong code của service |

Không thêm HTTP framework, ORM, query builder hay thư viện log khác.

## 2. Cách tổ chức file

```
main.go                      nối mọi thứ: config, client, repo, service, route, runner
internal/config/config.go    một struct Config, đọc env
internal/repo/repo.go        PostgresRepo, New, các lỗi chung (ErrNotFound...)
internal/repo/<hành_động>.go một hàm public cho mỗi file: get_widget.go, create_widget.go, list_widgets.go
                             struct của bảng và const danh sách cột nằm ngay trong file query chính (get_widget.go)
internal/service/service.go  Service, New
internal/service/<hành_động>.go  một endpoint cho mỗi file: create_widget.go
                             response dùng chung nằm trong file endpoint chính (get_widget.go)
internal/model/<tên>.go      chỉ khi một struct mang cả tag json và tag db (xem mục 7)
internal/cache/<tên>_cache.go    một struct cho mỗi loại cache Valkey
internal/provider/<tên>/     một client cho mỗi hệ thống bên ngoài, kèm interface để test
internal/middleware/         middleware riêng của service
internal/job/                việc chạy nền (taskqueue)
internal/testutil/           helper cho test (Postgres trong Docker, fake)
db/migrations/               NNNNNN_<tên>.up.sql và .down.sql
apispec/                     do swag sinh ra, không sửa tay
```

- Tên file: snake_case, bắt đầu bằng động từ: `create_widget.go`, `rotate_api_key.go`, `list_widgets.go`.
- Tên hàm và type theo tên file: `CreateWidget`, `CreateWidgetRequest`, `CreateWidgetHandler`, `NewCreateWidgetHandler`.
- Một package cho một lớp. Không tạo package `utils`, `helpers` hay `common`. Hàm nhỏ dùng chung đặt trong file đang dùng nó nhiều nhất (ví dụ `get_widget.go`), không tách file riêng.

## 3. Endpoint (handler)

Mỗi endpoint là một file trong `internal/service/`, gồm theo thứ tự:
1. `XRequest`: tag `json` (body), `param` (path), `query` (query string), `validate`, `example`. Tag xếp theo bảng chữ cái và thẳng cột (linter `tagalign` bắt lỗi này). Tên viết theo mục "Cách viết tên" bên dưới, và khối swag dùng đúng các tên đó.
2. Khối swag `// X godoc`. `@Router` phải khớp đúng route trong `main.go`, kể cả `/v2`.
3. `func (s *Service) X(ctx *echo.Context, req *XRequest) (any, *echo.HTTPError)`: chỉ tạo `delegator` rồi gọi `httpserver.ExecuteStandardized(ctx, req, "X", delegator)`. Không đặt logic ở đây.
4. `XHandler` struct, `NewXHandler`, và `Handle`. Logic nằm trong `Handle` và các method riêng của handler.
5. Thành công: `return httpserver.NewResponse(resp), nil`. Có phân trang: `httpserver.NewPaginatedResponse(resp, httpserver.NewPagination(page, pageSize, total))`, với `page, pageSize, offset := httpserver.NormalizePage(req.Page, req.PageSize)`.

Route đăng ký trong `main.go`: `v2.POST("/widgets", httpserver.Wrapper(app.service.CreateWidget))`.

### Cách viết tên

Tên trong API do service cung cấp viết camelCase; mọi thứ nội bộ (database, tag `db`, khóa log, khóa Redis, tên file) viết snake_case; dữ liệu bên ngoài theo đúng bên đó; API đang chạy giữ nguyên tên. Bảng đầy đủ và cách dùng `//nolint:tagliatelle`: `reference/naming.md`.

Tenant và user: với API mà tenant gọi qua gateway, lấy tenant từ middleware/JWT, không bao giờ lấy từ body. Với API nội bộ chỉ service khác gọi (Keycloak JWT + danh sách client được phép), tenant có thể nằm trong request.

## 4. Lỗi

- Lỗi chung của repo khai báo trong `repo/repo.go`: `ErrNotFound`, `ErrDuplicateLabel`... Mọi lỗi so sánh được phải là biến `Err...` khai báo sẵn (linter `err113`). Không `errors.New` ngay trong câu `return`.
- Repo không tìm thấy dòng: trả `ErrNotFound`. Không để `pgx.ErrNoRows` lọt ra ngoài repo.
- Vi phạm unique: bắt bằng `errors.As(err, &pgErr) && pgErr.Code == pgerrcode.UniqueViolation`, trả lỗi riêng (`ErrDuplicateLabel`).
- Bọc lỗi: `fmt.Errorf("failed to <động từ> <vật>: %w", err)`. Ví dụ `"failed to create widget: %w"`. Luôn dùng `%w`. So sánh bằng `errors.Is` / `errors.As`.
- Trong handler:
  - lỗi do người gọi: `echo.NewHTTPError(http.StatusBadRequest|NotFound|Conflict|Forbidden, "thông điệp chữ thường")`,
  - lỗi của mình (5xx): `httpserver.InternalError(err, "failed to create widget")`. **Luôn truyền thông điệp thứ hai.** Nếu thiếu, gframework trả `err.Error()` cho người gọi và làm lộ chi tiết bên trong. gframework đã tự log lỗi gốc, nên không log lại lỗi đó trong handler.
  - không bao giờ đưa `err.Error()` vào thông điệp trả về.
- Không `panic` trong code xử lý request. Không bỏ qua lỗi bằng `_ =`, trừ khi có comment giải thích vì sao.

## 5. Log

Dùng `h.log` trong handler, `zerolog.Logger` qua constructor ngoài handler. Khóa log snake_case, `Msg` chữ thường ngắn. Log lỗi một lần ở tầng xử lý nó, log mỗi lần gọi bên ngoài và mỗi quyết định làm đổi kết quả, dùng khóa chung (`request_id`, `tenant_id`, `user_uuid`, `duration_ms`...), mang `request_id` vào goroutine và job nền. Không bao giờ log secret, API key, token, header `Authorization`, số thẻ, dữ liệu cá nhân hay KYC. Log ở đâu, chọn level, bảng khóa, cách tra trên Loki: `reference/logging.md`.

## 6. Repo và SQL

SQL viết tay trong `const query`, tham số `$1..$n`; không `SELECT *`, không `RETURNING *`; lọc tenant ngay trong `WHERE`; nhiều lệnh ghi cùng thành bại thì dùng transaction. Chi tiết: `reference/sql.md`.

## 7. Model, config, main

Struct chỉ có tag `db` nằm trong `repo`; struct mang cả `json` và `db` nằm trong `internal/model`. Không trả struct bảng thẳng ra API. Config là một struct, secret dùng `,required`, mỗi biến mới có trong `.env.example`. `main.go` theo `reference/main.go`. **Bẫy:** luôn điền đủ mọi trường của `postgres.Config` (`HealthCheckPeriod: 0` làm panic). Chi tiết: `reference/models-config.md`.

## 8. Migration

Không bao giờ sửa migration đã merge; `down.sql` đảo ngược đúng `up.sql`; thêm cột vào bảng lớn thì cho phép NULL hoặc có DEFAULT. Chi tiết: `reference/migrations.md`.

## 9. Test

Repo và handler test trên Postgres thật (`testutil.NewPostgres(t)`), nhà cung cấp ngoài dùng fake viết tay, mọi test gọi `t.Parallel()`. Mỗi endpoint có ít nhất: thành công, lỗi do người gọi, sai tenant. Chi tiết: `reference/testing.md`.

## 10. Linter: những lỗi AI hay mắc

Lint theo cấu hình của chính repo đó, đúng phiên bản golangci-lint (`version: "2"` thì v2, ngược lại v1.64.8). Code mới phải qua lint của repo; không bật thêm linter cho repo cũ. Viết theo kiểu chặt luôn an toàn. Danh sách lỗi hay mắc và cách chạy đúng phiên bản: `reference/linters.md`.

## 11. Comment

Mặc định không viết comment. Theo ~/.claude/rules/comments.md: lý do của quyết định thiết kế ghi vào commit/PR/TASK.md; ý định thể hiện bằng tên hàm, tên biến; gợi ý cho người vận hành đặt trong log message. Comment chỉ được dùng cho: một dòng về điều kỳ lạ của hệ thống bên ngoài, một dòng cảnh báo điều trông như lỗi nhưng cố ý, lý do của `//nolint`, và khối swag. Không giải thích hành vi chuẩn của Go hay thư viện (`context.WithoutCancel`, `defer`, pgx). Một số code hiện có trong các repo có comment kiểu này: đừng chép chúng.

## 12. Trước khi nói "xong"

1. Lint của repo qua, với đúng phiên bản golangci-lint (mục 10).
2. `go test ./...` qua. Docker phải đang chạy cho test Postgres. Nếu không chạy được Docker, nói rõ là test database chưa chạy.
3. Handler hoặc khối swag thay đổi: chạy `make api-doc`, và kiểm tra `@Router` khớp route.
4. Có biến môi trường mới: đã thêm vào `.env.example` và `config.go`.
5. Có migration mới: có cả `up` và `down`, và đã chạy thử `make migrate-up-local` nếu có database trên máy.
6. Đọc lại diff: không có secret trong log, không có `SELECT *`, không có `err.Error()` trả cho người gọi, không có comment nào trượt bài kiểm tra trong .claude/rules/comments.md.
