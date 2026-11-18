# Cách viết tên (go-service)

Kiểu chữ phụ thuộc vào việc tên đó đi đâu:

| Tên đi đâu | Kiểu | Ví dụ |
|---|---|---|
| Request và response của API do service mình cung cấp: tag `json`, `param`, `query` của `XRequest`/`XResponse` | camelCase | `tenantId`, `pageSize`, `/users/:userId` |
| Dữ liệu gửi cho hoặc nhận từ bên ngoài (nhà cung cấp, service khác, webhook của bên thứ ba) | đúng như bên đó yêu cầu | `partner_id`, `session_id` của nhà cung cấp |
| Mọi thứ nội bộ: cột và bảng database, tag `db`, SQL, khóa log, khóa Redis, tên file Go | snake_case | `tenant_id`, `api_key`, `.Str("widget_id", id)` |
| Biến môi trường | SNAKE_CASE viết hoa | `POSTGRES_URL` |

- API đang chạy giữ nguyên tên hiện có, kể cả khi đang là snake_case (ví dụ một route cũ dùng `:user_id`). Đổi tên sẽ làm hỏng bên đang gọi. Chỉ API mới theo bảng trên.
- Struct cho dữ liệu bên ngoài nằm trong `internal/provider/<tên>/` (hoặc `internal/psp/<tên>/`). Linter `tagliatelle` báo lỗi ở các struct này thì thêm `//nolint:tagliatelle // <tên bên ngoài> API uses snake_case`.
