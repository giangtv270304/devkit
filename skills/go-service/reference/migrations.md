# Migration (go-service)

- Tạo bằng `make migrate-create MIGRATION=<tên>`. File theo dạng `NNNNNN_<tên>.up.sql` và `.down.sql`.
- Không bao giờ sửa migration đã merge. Muốn đổi thì thêm migration mới.
- `down.sql` phải đảo ngược đúng `up.sql`.
- Bảng tên số ít, snake_case (`api_key`, `widget`). Luôn có `id`, `created_at`, `updated_at` (`TIMESTAMPTZ NOT NULL DEFAULT NOW()`). Thêm `created_by`/`updated_by` khi có người thao tác.
- Ràng buộc nằm trong database: `NOT NULL`, `CHECK`, unique index (kể cả unique có điều kiện `WHERE revoked_at IS NULL`). Code không phải nơi duy nhất giữ tính đúng đắn.
- Đặt tên index: `idx_<bảng>_<cột>`, unique: `uniq_<bảng>_<ý nghĩa>`.
- Thêm cột vào bảng lớn: cột mới phải cho phép NULL hoặc có DEFAULT, để code cũ vẫn chạy trong lúc deploy.
