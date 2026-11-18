# Model, config, main (go-service)

- Struct chỉ dùng để đọc/ghi database (chỉ có tag `db`): viết thẳng trong package `repo`, ngay trong file query chính của bảng đó (`get_widget.go`). Các file khác lấy ra dùng (`repo.Widget`). Không tạo thư mục `internal/model` cho loại này.
- Struct mang cả tag `json` và tag `db` (ví dụ được lưu vào cache dưới dạng JSON, hoặc đọc từ cột JSON): đặt trong `internal/model/<tên>.go`.
- Không trả struct của bảng thẳng ra API: luôn chuyển sang `XResponse` (`toWidgetResponse`).
- Không tách file cho thứ nhỏ: const danh sách cột, struct của bảng, response dùng chung, hàm chuyển đổi, hàm phụ vài dòng. Viết chúng vào file đang dùng chúng nhiều nhất; file khác trong cùng package lấy ra dùng. Chỉ tách file mới khi nó là một hàm public mới của repo hoặc một endpoint mới.
- Cột có thể NULL dùng con trỏ: `*time.Time`, `*string`. Tiền dùng `decimal.Decimal`.
- Config: một struct, nhóm theo phần (HTTP, metric, Postgres, Valkey, Keycloak, nhà cung cấp). Mỗi trường có `env` và `envDefault`. Secret và URL bắt buộc dùng `,required`, không có default. Mỗi biến mới phải có trong `.env.example`.
- `main.go` theo đúng `reference/main.go`: `main` gọi `run`; `run` tạo config, client, repo, service; `runner.New(runner.WithCoreService(...)).Run()`. Mỗi client có một hàm `newXClient(cfg)` trả `(client, error)`. Route nằm trong `registerRoutes`.
- **Bẫy:** `postgres.New` của gframework ghi đè giá trị mặc định của pgx. `HealthCheckPeriod: 0` làm chương trình panic (`non-positive interval for NewTicker`). Luôn điền đủ mọi trường của `postgres.Config`.
