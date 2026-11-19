# Log (go-service)

Mục tiêu: tra được lỗi trên Grafana/Loki mà không cần đọc code. Log chi tiết nghĩa là mỗi dòng có đủ field để lọc, không phải nhiều dòng. Log thừa làm Loki chậm và làm dòng cần tìm bị chìm.

## Cách viết
- Dùng `h.log` (logger mà `ExecuteStandardized` truyền vào, có `handler`). Ngoài handler, nhận `zerolog.Logger` qua constructor. Không dùng logger global `log.Info()` trong code nghiệp vụ.
- gframework (đã kiểm tra tới v1.8.0) chỉ gắn `request_id` vào dòng "Request started". `h.log` lấy logger từ context của request, nên chỉ có `request_id` khi service có middleware gắn sẵn logger đó vào context, đặt ngay sau `middleware.RequestID`. Thiếu middleware này thì log của handler không lọc được theo `request_id`. Trước khi viết log, kiểm tra repo đã có middleware đó chưa.
  ```go
  func ContextLogger(base zerolog.Logger) echo.MiddlewareFunc {
  	return func(next echo.HandlerFunc) echo.HandlerFunc {
  		return func(c *echo.Context) error {
  			l := base.With().Str("request_id", gfmiddleware.GetRequestID(c)).Logger()
  			c.SetRequest(c.Request().WithContext(l.WithContext(c.Request().Context())))
  			return next(c)
  		}
  	}
  }
  ```
- Log là JSON một dòng ra stdout. Không dùng `ConsoleWriter` ở môi trường chạy thật, vì bộ thu log đọc `level` từ JSON.
- Khóa log viết snake_case: `.Str("widget_id", id).Int("tenant_id", tenantID)`.
- `Msg` viết chữ thường, ngắn, thì quá khứ cho sự kiện: `"widget created"`, `"cache get failed"`. Gợi ý cho người vận hành đặt trong `Msg`, không đặt trong comment.
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

## Log ở đâu
| Chỗ | Level | Field bắt buộc |
|---|---|---|
| Mỗi request HTTP | gframework tự ghi, không tự viết thêm | |
| Lỗi: chỉ ở tầng xử lý lỗi đó | Error hoặc Warn | `Err(err)` và mọi id đang có |
| Mỗi lần gọi bên ngoài (provider, service khác) | Info khi xong; Warn hoặc Error khi lỗi | `provider`, `op`, `http_status`, `duration_ms`, `attempt` |
| Thay đổi dữ liệu quan trọng: tạo, đổi trạng thái, thu hồi, chuyển tiền | Info | id của đối tượng và trạng thái mới |
| Quyết định làm đổi kết quả: bỏ qua một bước, chọn route, retry | Info hoặc Warn | `reason` và dữ liệu dẫn tới quyết định |
| Job nền và worker: bắt đầu, xong, lỗi | Info hoặc Error | `task_id`, `attempt`, `duration_ms` |
| Khởi động service | Info | cấu hình không bí mật: port, level, các flag |

Không log:
- Mỗi lần đọc thành công.
- Từng phần tử trong vòng lặp ở level Info.
- Trong hàm repo. Repo bọc lỗi (`fmt.Errorf("get user: %w", err)`) rồi trả lên.
- Cùng một lỗi ở nhiều tầng.

Lỗi mà handler trả về: `httpserver.New` không bật `LogErrors` của error handler (đã kiểm tra tới v1.8.0), nên gframework **không** log lỗi đó. Handler phải tự log lỗi 5xx đúng một lần, ngay trước khi trả `httpserver.InternalError`. Lỗi 4xx do input của người gọi thì ghi Warn, hoặc không ghi.

## Chọn level
- **Error**: request thất bại vì lỗi của mình, hoặc cần người xử lý. Mỗi dòng Error phải đáng được cảnh báo.
- **Warn**: chuyện bất thường nhưng đã xử lý: bên ngoài trả 4xx, retry, bỏ qua một bước.
- **Info**: sự kiện nghiệp vụ ở bảng trên.
- **Debug**: chi tiết để tra lỗi, như payload đã che hay giá trị trung gian. Tắt ở prod bằng biến `LOG_LEVEL`, bật tạm khi cần.

## Khóa field chung
Dùng đúng tên này trong mọi repo, để một câu lọc trên Loki chạy được với mọi service.

| Khóa | Nghĩa |
|---|---|
| `request_id` | middleware `ContextLogger` gắn (xem mục Cách viết). Phải đi theo vào goroutine và job nền |
| `tenant_id` | id số của tenant |
| `user_id` | UUID công khai của user, là id mà API và các service khác dùng |
| `user_db_id` | id số của user trong DB, khi cần. Không ghi id số dưới khóa `user_id` |
| `provider`, `op` | tên provider viết thường; tên thao tác, ví dụ `submit_kyc` |
| `order_id`, `task_id`, `session_id` | id của đối tượng |
| `duration_ms` | số nguyên (`.Int64("duration_ms", d.Milliseconds())`), không dùng chuỗi như `"1.2s"` |
| `reason` | lý do của một quyết định, viết ngắn bằng snake_case: `missing_fields`, `provider_disabled` |

Repo đang dùng khóa camelCase (xem "Go notes" trong `.claude/project.md`) thì giữ camelCase, nhưng dùng cùng nghĩa: `userId`, `durationMs`.

## Log trong goroutine và job nền
- Truyền logger đã có `request_id` vào, hoặc lấy từ context bằng `zerolog.Ctx(ctx)`. Không dùng logger gốc của struct, vì logger đó không có `request_id`.
  ```go
  log := zerolog.Ctx(reqCtx).With().Str("user_id", userUUID).Logger()
  bgCtx := log.WithContext(context.WithoutCancel(reqCtx))
  go h.service.notifier.Send(bgCtx, userUUID)
  // bên trong: zerolog.Ctx(ctx).Info().Msg("notification sent")
  ```
- Job đưa vào taskqueue: đưa `request_id` vào payload, rồi worker gắn lại vào logger.
- Như vậy một lần gọi API và mọi việc nền nó sinh ra đều tra được bằng cùng một `request_id`.

## Tra trên Grafana (Loki)
- Label chỉ gồm `service` và `level`. Không đưa id vào label: mỗi giá trị label mới tạo ra một luồng mới, và Loki chậm dần.
- Lọc theo id bằng JSON:
  - `{service="<svc>", level="error"} | json`
  - `{service="<svc>"} | json | user_id="<uuid>"`
  - `{service=~".+"} | json | request_id="<id>"`: lần theo một request qua nhiều service.

## Không bao giờ log
- Secret, API key đầy đủ, token, header `Authorization`, mật khẩu, số thẻ.
- Dữ liệu cá nhân và dữ liệu KYC: họ tên, email, phone, ngày sinh, số giấy tờ, địa chỉ, ảnh. Định danh user bằng `user_id`.
- Body request hoặc response có các thứ trên.
- Chuỗi lỗi hoặc body lỗi của bên ngoài khi chưa làm sạch. Chúng có thể chứa dữ liệu user. Chỉ log mã lỗi, `http_status` và thông điệp đã cắt bỏ dữ liệu.
