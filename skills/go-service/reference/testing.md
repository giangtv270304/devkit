# Test (go-service)

- Repo và handler test trên Postgres thật chạy trong Docker: `testutil.NewPostgres(t)` (chép `reference/internal/testutil/postgres.go`). Helper tự chạy mọi migration. Test này bị bỏ qua khi chạy `go test -short`.
- Nhà cung cấp bên ngoài (KMS, nhà phát hành thẻ, nhà cung cấp KYC...) gọi qua interface đặt trong `internal/provider/<tên>`. Test dùng một fake viết tay, không dùng thư viện mock.
- Package test tên `<pkg>_test` (linter `testpackage`). Mọi test và subtest gọi `t.Parallel()`.
- Một Postgres cho mỗi hàm test cấp cao nhất. Các subtest dùng chung database đó, nên mỗi subtest dùng dữ liệu riêng (tenant id riêng) để không đụng nhau.
- Test handler: `gtestutil.SetupEchoContext` rồi gọi `httpserver.Wrapper(svc.X)(ctx)`. Lấy status từ `*echo.HTTPError` hoặc `rec.Code` (xem `statusOf` trong code mẫu). Nhiều trường hợp chỉ khác dữ liệu: dùng bảng test.
- Assert bằng `if ... { t.Errorf/Fatalf("got %v, want %v") }`. Assert vào thứ người gọi thấy: status, body, dòng trong database, lỗi trả về.
- Mỗi endpoint mới có ít nhất: một trường hợp thành công, một trường hợp lỗi do người gọi, và trường hợp sai tenant nếu dữ liệu thuộc về tenant.
