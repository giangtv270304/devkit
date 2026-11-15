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
Kiểu chữ phụ thuộc vào việc tên đó đi đâu:

| Tên đi đâu | Kiểu | Ví dụ |
|---|---|---|
| Request và response của API do service mình cung cấp: tag `json`, `param`, `query` của `XRequest`/`XResponse` | camelCase | `tenantId`, `pageSize`, `/users/:userId` |
| Dữ liệu gửi cho hoặc nhận từ bên ngoài (nhà cung cấp, service khác, webhook của bên thứ ba) | đúng như bên đó yêu cầu | `partner_id`, `session_id` của nhà cung cấp |
| Mọi thứ nội bộ: cột và bảng database, tag `db`, SQL, khóa log, khóa Redis, tên file Go | snake_case | `tenant_id`, `api_key`, `.Str("widget_id", id)` |
| Biến môi trường | SNAKE_CASE viết hoa | `POSTGRES_URL` |

- API đang chạy giữ nguyên tên hiện có, kể cả khi đang là snake_case (ví dụ một route cũ dùng `:user_id`). Đổi tên sẽ làm hỏng bên đang gọi. Chỉ API mới theo bảng trên.
- Struct cho dữ liệu bên ngoài nằm trong `internal/provider/<tên>/` (hoặc `internal/psp/<tên>/`). Linter `tagliatelle` báo lỗi ở các struct này thì thêm `//nolint:tagliatelle // <tên bên ngoài> API uses snake_case`.

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

- Dùng `h.log` (logger mà `ExecuteStandardized` truyền vào, đã có `handler` và `request_id`). Ngoài handler, nhận `zerolog.Logger` qua constructor. Không dùng logger global `log.Info()` trong code nghiệp vụ.
- Khóa log viết snake_case: `.Str("widget_id", id).Int("tenant_id", tenantID)`.
- `Msg` viết chữ thường, ngắn, thì quá khứ cho sự kiện: `"widget created"`, `"cache get failed"`.
- Một dòng hay nhiều dòng: viết trên một dòng khi chuỗi log có tối đa 2 field (`Err` cũng tính là một field) và dòng không quá 100 ký tự. Dài hơn thì xuống dòng, mỗi lời gọi một dòng, dấu chấm ở cuối dòng trước. Không viết kiểu nửa nọ nửa kia (vài field một dòng).
  ```go
  h.log.Info().Str("widget_id", id).Msg("widget renamed")

  h.log.Error().
  	Err(err).
  	Str("widget_id", id).
  	Int("tenant_id", tenantID).
  	Str("label", label).
  	Msg("widget rename failed")
  ```
- Thứ tự trong chuỗi: `Err(err)` trước, rồi mã định danh (`tenant_id`, `widget_id`...), rồi các field khác, `Msg` luôn ở cuối.
- Log `Info` khi có thay đổi dữ liệu quan trọng (tạo, thu hồi, chuyển tiền). Không log mỗi lần đọc.
- Không bao giờ log: secret, API key đầy đủ, token, header `Authorization`, số thẻ, dữ liệu KYC, mật khẩu, body request có các thứ này.

## 6. Repo và SQL

- `PostgresRepo` giữ `db *postgres.Postgres`. Mỗi file một method public.
- SQL viết tay trong `const query = `...``, tham số `$1..$n`. Không nối chuỗi giá trị của người dùng vào SQL. Chỉ nối chuỗi cho phần điều kiện cố định, như `list_widgets.go`.
- Không `SELECT *` và không `RETURNING *`. Dùng const `<bảng>Columns`, đặt ngay dưới struct của bảng, và const này phải liệt kê mọi tag `db` của struct đó.
- Đọc: `pgxscan.Get` (một dòng) / `pgxscan.Select` (nhiều dòng).
- Hàm ghi có hơn 3 tham số thì nhận một struct `XParams`, như `CreateWidgetParams`.
- Danh sách có lọc: `XFilter` struct, đếm tổng bằng `COUNT(*)` với cùng điều kiện, `ORDER BY` cố định, `LIMIT/OFFSET`.
- Nhiều lệnh ghi phải cùng thành công hoặc cùng thất bại: dùng `r.db.WithTransaction(ctx, func(ctx context.Context, dbTx pgx.Tx) error {...})`, hoặc gộp thành một câu SQL có CTE (ví dụ: xoay một API key, vô hiệu khóa cũ và tạo khóa mới trong một câu). Khóa dòng sắp sửa bằng `SELECT ... FOR UPDATE`.
- Lọc theo tenant ngay trong `WHERE` (`tenant_id = $1`). Không lọc sau khi đã đọc dữ liệu.
- Repo có thể đọc/ghi cache (ví dụ đọc một API key theo mã băm). Khi ghi database, xóa cache của khóa đó sau khi ghi thành công.

## 7. Model, config, main

- Struct chỉ dùng để đọc/ghi database (chỉ có tag `db`): viết thẳng trong package `repo`, ngay trong file query chính của bảng đó (`get_widget.go`). Các file khác lấy ra dùng (`repo.Widget`). Không tạo thư mục `internal/model` cho loại này.
- Struct mang cả tag `json` và tag `db` (ví dụ được lưu vào cache dưới dạng JSON, hoặc đọc từ cột JSON): đặt trong `internal/model/<tên>.go`.
- Không trả struct của bảng thẳng ra API: luôn chuyển sang `XResponse` (`toWidgetResponse`).
- Không tách file cho thứ nhỏ: const danh sách cột, struct của bảng, response dùng chung, hàm chuyển đổi, hàm phụ vài dòng. Viết chúng vào file đang dùng chúng nhiều nhất; file khác trong cùng package lấy ra dùng. Chỉ tách file mới khi nó là một hàm public mới của repo hoặc một endpoint mới.
- Cột có thể NULL dùng con trỏ: `*time.Time`, `*string`. Tiền dùng `decimal.Decimal`.
- Config: một struct, nhóm theo phần (HTTP, metric, Postgres, Valkey, Keycloak, nhà cung cấp). Mỗi trường có `env` và `envDefault`. Secret và URL bắt buộc dùng `,required`, không có default. Mỗi biến mới phải có trong `.env.example`.
- `main.go` theo đúng `reference/main.go`: `main` gọi `run`; `run` tạo config, client, repo, service; `runner.New(runner.WithCoreService(...)).Run()`. Mỗi client có một hàm `newXClient(cfg)` trả `(client, error)`. Route nằm trong `registerRoutes`.
- **Bẫy:** `postgres.New` của gframework ghi đè giá trị mặc định của pgx. `HealthCheckPeriod: 0` làm chương trình panic (`non-positive interval for NewTicker`). Luôn điền đủ mọi trường của `postgres.Config`.

## 8. Migration

- Tạo bằng `make migrate-create MIGRATION=<tên>`. File theo dạng `NNNNNN_<tên>.up.sql` và `.down.sql`.
- Không bao giờ sửa migration đã merge. Muốn đổi thì thêm migration mới.
- `down.sql` phải đảo ngược đúng `up.sql`.
- Bảng tên số ít, snake_case (`api_key`, `widget`). Luôn có `id`, `created_at`, `updated_at` (`TIMESTAMPTZ NOT NULL DEFAULT NOW()`). Thêm `created_by`/`updated_by` khi có người thao tác.
- Ràng buộc nằm trong database: `NOT NULL`, `CHECK`, unique index (kể cả unique có điều kiện `WHERE revoked_at IS NULL`). Code không phải nơi duy nhất giữ tính đúng đắn.
- Đặt tên index: `idx_<bảng>_<cột>`, unique: `uniq_<bảng>_<ý nghĩa>`.
- Thêm cột vào bảng lớn: cột mới phải cho phép NULL hoặc có DEFAULT, để code cũ vẫn chạy trong lúc deploy.

## 9. Test

- Repo và handler test trên Postgres thật chạy trong Docker: `testutil.NewPostgres(t)` (chép `reference/internal/testutil/postgres.go`). Helper tự chạy mọi migration. Test này bị bỏ qua khi chạy `go test -short`.
- Nhà cung cấp bên ngoài (KMS, nhà phát hành thẻ, nhà cung cấp KYC...) gọi qua interface đặt trong `internal/provider/<tên>`. Test dùng một fake viết tay, không dùng thư viện mock.
- Package test tên `<pkg>_test` (linter `testpackage`). Mọi test và subtest gọi `t.Parallel()`.
- Một Postgres cho mỗi hàm test cấp cao nhất. Các subtest dùng chung database đó, nên mỗi subtest dùng dữ liệu riêng (tenant id riêng) để không đụng nhau.
- Test handler: `gtestutil.SetupEchoContext` rồi gọi `httpserver.Wrapper(svc.X)(ctx)`. Lấy status từ `*echo.HTTPError` hoặc `rec.Code` (xem `statusOf` trong code mẫu). Nhiều trường hợp chỉ khác dữ liệu: dùng bảng test.
- Assert bằng `if ... { t.Errorf/Fatalf("got %v, want %v") }`. Assert vào thứ người gọi thấy: status, body, dòng trong database, lỗi trả về.
- Mỗi endpoint mới có ít nhất: một trường hợp thành công, một trường hợp lỗi do người gọi, và trường hợp sai tenant nếu dữ liệu thuộc về tenant.

## 10. Linter: những lỗi AI hay mắc

**Lint theo cấu hình của chính repo đó.** Mỗi repo có thể có cấu hình riêng: `.golangci.yaml` chặt, một bản ít linter hơn, hoặc không có cấu hình (golangci-lint dùng bộ mặc định). Xem file cấu hình trong repo trước khi viết. Mục "Go notes" trong `.claude/project.md` của dự án ghi repo nào dùng cấu hình nào, nếu có.

Code mới phải qua lint của repo đó. Không bật thêm linter cho repo cũ trong một task khác: việc đó là một task riêng, vì nó làm hiện ra hàng trăm lỗi ở code cũ. Repo mới dùng cấu hình chặt (repo chuẩn ghi trong project.md, nếu có).

Viết theo kiểu chặt bên dưới luôn an toàn: code viết đúng kiểu chặt cũng qua lint lỏng. Đây là những lỗi AI hay mắc khi gặp cấu hình chặt:
- `exhaustruct`: struct literal phải ghi đủ mọi trường, kể cả giá trị rỗng (`Pagination: nil`). Ngoại lệ duy nhất: struct cấu hình test, kèm `//nolint:exhaustruct // <lý do>`.
- `wsl`, `nlreturn`: một dòng trống trước `return`, trước và sau khối `if`/`for` khi khối đứng cạnh lệnh khác, và sau khai báo `var`.
- `varnamelen`: tên biến tối thiểu 3 ký tự, trừ `id`, `db`, `ctx`, `err`, `v1`. Viết `dbTx`, `testCase`, không viết `tx`, `tc`.
- `mnd`: không có số "ma thuật". Đặt số vào `const` có tên.
- `err113`: lỗi so sánh được phải là biến `Err...` khai báo sẵn.
- `nilnil`: không `return nil, nil`. Nếu thật sự cần (cache miss), thêm `//nolint:nilnil` kèm lý do.
- `funlen`: tối đa 80 dòng hoặc 60 câu lệnh một hàm. `lll`: tối đa 130 ký tự một dòng. Hàm dài thì tách thành method riêng của handler.
- `tagalign`: tag xếp theo bảng chữ cái và thẳng cột. `tagliatelle`: tag `json` viết camelCase, trừ struct cho dữ liệu bên ngoài (xem "Cách viết tên" ở mục 3).
- `gci`: import chia hai nhóm: thư viện chuẩn, rồi mọi thứ còn lại (gồm cả module của chính tổ chức).
- `godot`: comment kết thúc bằng dấu chấm.
- `ireturn`, `nonamedreturns`: trả type cụ thể, không đặt tên cho giá trị trả về.
- `gochecknoglobals`: không có biến global, trừ biến `Err...`.

Lệnh kiểm tra: `make lint`. Phiên bản golangci-lint phải khớp định dạng cấu hình của repo:
- Cấu hình có dòng `version: "2"`: dùng golangci-lint v2.
- Cấu hình không có dòng đó, hoặc repo không có cấu hình: dùng v1.64.8.

Makefile chỉ cài v1.64.8 khi máy chưa có golangci-lint, nên `make lint` có thể chạy sai phiên bản. Kiểm tra bằng `golangci-lint --version`. Nếu sai, chạy thẳng đúng phiên bản: `go run github.com/golangci/golangci-lint/cmd/golangci-lint@v1.64.8 run ./...` (v1) hoặc `go run github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest run ./...` (v2).

## 11. Comment

Mặc định không viết comment. Theo .claude/rules/comments.md: lý do của quyết định thiết kế ghi vào commit/PR/TASK.md; ý định thể hiện bằng tên hàm, tên biến; gợi ý cho người vận hành đặt trong log message. Comment chỉ được dùng cho: một dòng về điều kỳ lạ của hệ thống bên ngoài, một dòng cảnh báo điều trông như lỗi nhưng cố ý, lý do của `//nolint`, và khối swag. Không giải thích hành vi chuẩn của Go hay thư viện (`context.WithoutCancel`, `defer`, pgx). Một số code hiện có trong các repo có comment kiểu này: đừng chép chúng.

## 12. Trước khi nói "xong"

1. Lint của repo qua, với đúng phiên bản golangci-lint (mục 10).
2. `go test ./...` qua. Docker phải đang chạy cho test Postgres. Nếu không chạy được Docker, nói rõ là test database chưa chạy.
3. Handler hoặc khối swag thay đổi: chạy `make api-doc`, và kiểm tra `@Router` khớp route.
4. Có biến môi trường mới: đã thêm vào `.env.example` và `config.go`.
5. Có migration mới: có cả `up` và `down`, và đã chạy thử `make migrate-up-local` nếu có database trên máy.
6. Đọc lại diff: không có secret trong log, không có `SELECT *`, không có `err.Error()` trả cho người gọi, không có comment nào trượt bài kiểm tra trong .claude/rules/comments.md.
