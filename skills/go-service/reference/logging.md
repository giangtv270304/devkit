# Log (go-service)

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
