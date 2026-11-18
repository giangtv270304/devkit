# Repo và SQL (go-service)

- `PostgresRepo` giữ `db *postgres.Postgres`. Mỗi file một method public.
- SQL viết tay trong `const query = `...``, tham số `$1..$n`. Không nối chuỗi giá trị của người dùng vào SQL. Chỉ nối chuỗi cho phần điều kiện cố định, như `list_widgets.go`.
- Không `SELECT *` và không `RETURNING *`. Dùng const `<bảng>Columns`, đặt ngay dưới struct của bảng, và const này phải liệt kê mọi tag `db` của struct đó.
- Đọc: `pgxscan.Get` (một dòng) / `pgxscan.Select` (nhiều dòng).
- Hàm ghi có hơn 3 tham số thì nhận một struct `XParams`, như `CreateWidgetParams`.
- Danh sách có lọc: `XFilter` struct, đếm tổng bằng `COUNT(*)` với cùng điều kiện, `ORDER BY` cố định, `LIMIT/OFFSET`.
- Nhiều lệnh ghi phải cùng thành công hoặc cùng thất bại: dùng `r.db.WithTransaction(ctx, func(ctx context.Context, dbTx pgx.Tx) error {...})`, hoặc gộp thành một câu SQL có CTE (ví dụ: xoay một API key, vô hiệu khóa cũ và tạo khóa mới trong một câu). Khóa dòng sắp sửa bằng `SELECT ... FOR UPDATE`.
- Lọc theo tenant ngay trong `WHERE` (`tenant_id = $1`). Không lọc sau khi đã đọc dữ liệu.
- Repo có thể đọc/ghi cache (ví dụ đọc một API key theo mã băm). Khi ghi database, xóa cache của khóa đó sau khi ghi thành công.
