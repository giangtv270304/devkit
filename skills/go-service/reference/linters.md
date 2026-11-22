# Linter: những lỗi AI hay mắc (go-service)

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
- Cấu hình không có dòng đó: dùng v1.64.8.
- Repo không có cấu hình: dùng v2, vì v2 chạy được bộ mặc định mà không cần file.

Makefile chỉ cài v1.64.8 khi máy chưa có golangci-lint, nên `make lint` có thể chạy sai phiên bản. Kiểm tra bằng `golangci-lint --version`. Nếu sai, chạy thẳng đúng phiên bản: `go run github.com/golangci/golangci-lint/cmd/golangci-lint@v1.64.8 run ./...` (v1) hoặc `go run github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.12.2 run ./...` (v2).
