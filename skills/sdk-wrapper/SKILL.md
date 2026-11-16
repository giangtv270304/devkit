---
name: sdk-wrapper
description: Quy ước bắt buộc khi viết hoặc sửa một SDK bọc HTTP API (thư viện client cho Go hoặc TypeScript mà bên ngoài cài về dùng). Gồm cách tổ chức file, client, ký request, kiểu dữ liệu, lỗi, test với server giả và test trên sandbox, README và checklist phát hành. Dùng khi tạo SDK mới, thêm hoặc sửa endpoint trong SDK, hoặc đồng bộ SDK giữa các ngôn ngữ.
---

# sdk-wrapper: cách viết một SDK bọc HTTP API

Skill này là quy ước cứng. Code mẫu nằm trong `reference/` cạnh file này, cho một API giả tên "widget". Code mẫu Go đã build, test và qua `golangci-lint` mặc định. Code mẫu TS đã qua `tsc --noEmit`, `vitest` và `tsup`. **Chép cấu trúc của code mẫu, đừng tự nghĩ ra cấu trúc mới.**

| Cần viết | Go | TypeScript |
|---|---|---|
| Client, option, hàm gửi request duy nhất | `reference/go/client.go` | `reference/ts/src/client.ts` |
| Request nội bộ, envelope response | `request.go`, `response.go` | `src/request.ts`, `src/response.ts` |
| Kiểu lỗi và hàm kiểm tra lỗi | `errors.go` | `src/errors.ts` |
| Ký request | `signer/signer.go` | `src/signer.ts` |
| Endpoint đọc một / tạo / danh sách | `widget_get_by_id.go`, `widget_create.go`, `widget_list.go` | `src/widget_*.ts` |
| Test với server giả | `*_unit_test.go`, `test_helper_test.go` | `src/__tests__/widgets.test.ts`, `helpers.ts` |
| Test trên sandbox | `widget_integration_test.go` | `src/__tests__/sandbox.test.ts` |
| Test chữ ký dùng chung | `signer/signer_test.go` | `src/__tests__/signer.test.ts` |
| Ví dụ chạy được | `example/quickstart/main.go` | đoạn Quick start trong README |
| Khung README, file mô tả API | `reference/README.example.md`, `reference/api-spec.example.md` | dùng chung |

"widget" chỉ là tên giả. Đổi thành tên thật của API và của tài nguyên.

**Repo SDK đã có sẵn code:** theo cấu trúc và cách đặt tên mà repo đó đang dùng. Không sửa code cũ cho giống skill, trừ khi người dùng yêu cầu. Thấy chỗ lệch với skill thì nêu ra khi bàn giao.

## 1. Đầu vào: mô tả API nằm ngoài skill

Skill không chứa gì riêng của một API. Trước khi viết, cần có đủ các thông tin sau, lấy từ tài liệu API hoặc mã nguồn service, và ghi vào `api-spec.md` ở repo SDK (mẫu: `reference/api-spec.example.md`):

- Tên SDK, tên package, base URL của sandbox và production.
- Cách xác thực: header nào, chuỗi nào được ký, thuật toán, cách mã hóa chữ ký.
- Dạng envelope khi thành công và dạng body khi lỗi. Một API có thể có hơn một dạng: ghi rõ endpoint nào dùng dạng nào.
- Danh sách endpoint: method, path, tham số path/query/body, response, field nào có thể null, field nào là tiền.

Thiếu mục nào thì hỏi người dùng. Không đoán path, tên field hay cách ký.

## 2. Cách tổ chức file

- Một package phẳng. Mọi method gắn thẳng vào client: `client.CreateWidget(...)`, `client.getWidgetById(...)`. Không tạo client con theo tài nguyên.
- Mỗi endpoint một file, tên `<tài_nguyên>_<hành_động>`: `widget_create.go`, `widget_get_by_id.ts`. File đó chứa request, response và method của endpoint.
- Tên file giống nhau giữa các ngôn ngữ. Tên method giống nhau, chỉ khác kiểu chữ của ngôn ngữ: `GetWidgetByID` và `getWidgetById`.
- Kiểu dùng chung của một tài nguyên (`Widget`, `WidgetStatus`) đặt trong file endpoint đọc chính (`widget_get_by_id`). File khác lấy ra dùng.
- Mỗi endpoint có `XRequest` và `XResponse`, kể cả khi request rỗng hoặc response là alias của kiểu chung. Thêm field sau này không làm đổi chữ ký hàm.
- File lõi cố định: `client`, `request`, `response`, `errors`, `signer`. Không tạo `utils`, `helpers`, `common`.
- Số dependency lúc chạy: không có, hoặc ít nhất có thể. Muốn thêm thì hỏi người dùng trước.

## 3. Client và cấu hình

- Tham số bắt buộc: base URL, API key, secret key. Thiếu thì báo lỗi ngay lúc tạo client, không đợi tới lời gọi đầu tiên.
- Base URL của sandbox và production là hằng số public. Base URL luôn đổi được, để test trỏ vào server giả.
- Tùy chọn: HTTP client (Go) hoặc `fetch` (TS) tự cấp; logger; timeout. Timeout mặc định 30 giây và luôn có.
- Chỉ một hàm gửi request (`execute`). Mọi endpoint đi qua nó. Hàm này làm theo thứ tự: mã hóa body, dựng query, ký, gửi, đọc body, đổi status từ 400 trở lên thành lỗi, giải mã response.
- Gửi `User-Agent: <tên-sdk>/<phiên bản>`.
- Log debug chỉ ghi method, URL và status. Không bao giờ log header, chữ ký, key, hay body.
- Secret key chỉ dùng ở phía server. Ghi rõ điều này trong README và trong doc của option.

## 4. Ký request

- Ký đúng chuỗi byte sẽ gửi đi: mã hóa body một lần, ký trên kết quả đó, rồi gửi chính kết quả đó. Không mã hóa lại sau khi ký.
- Query được sắp xếp theo tên khóa trước khi ký, để mọi ngôn ngữ ký cùng một chuỗi.
- Đồng hồ là tham số thay được (`now`), để test ra chữ ký cố định.
- `reference/signature-vectors.json` chứa các vector chữ ký. Test signer của mọi ngôn ngữ đọc cùng file này. SDK thật giữ một file như vậy, với vector tính theo cách ký thật của API, và chép y nguyên sang repo của từng ngôn ngữ.
- Cách ký trong code mẫu (HMAC-SHA256, base64 URL-safe, ba header) chỉ là ví dụ. Thay bằng cách ký ghi trong `api-spec.md`.

## 5. Kiểu dữ liệu

- Tiền là chuỗi thập phân (`"12.50"`) hoặc kiểu decimal. Không bao giờ dùng `float64` hay `number` cho tiền. Nếu API trả tiền dạng số JSON, nêu ra với người dùng: phía TS không sửa được ở SDK.
- Enum: Go dùng kiểu `string` có tên và hằng số; TS dùng union chuỗi. Giá trị lạ từ server không được làm hỏng việc giải mã.
- Field có thể null: con trỏ (Go), `T | null` (TS). Field tùy chọn trong request: `omitempty` (Go), `?` (TS).
- Thời gian: giữ chuỗi như API trả, trừ khi tài liệu cam kết định dạng.
- Tham số path luôn được escape (`url.PathEscape`, `encodeURIComponent`).
- Trả nguyên envelope của API (`requestId`, `data`), cùng một dạng ở mọi ngôn ngữ.

## 6. Lỗi

- Một kiểu lỗi cho mọi response có status từ 400 trở lên, mang: status, mã lỗi của API, message, request id, body thô. Body lỗi không phải JSON (trang HTML của proxy) vẫn được giữ lại.
- Go: `*APIError`, đọc bằng `errors.As`. Hàm `IsNotFound`, `IsUnauthorized`, `IsConflict`, `IsRateLimited` dùng `errors.As`, không dùng type assertion. Lỗi mạng được bọc bằng `%w`, để `errors.Is(err, context.DeadlineExceeded)` vẫn đúng.
- TS: một class lỗi có `kind`: `api`, `timeout`, `network`, `invalid_response`. Timeout và lỗi mạng là hai loại riêng.
- Thông điệp lỗi nói được ba điều: lời gọi nào, sai gì, và request id nếu có. Ví dụ: `widget: api error: status=404 code=widget_not_found message=widget not found request_id=req_2`.
- Response 2xx mà body không giải mã được là lỗi. Không trả `nil, nil` hay `null`.
- Tham số bắt buộc bị rỗng (id trong path): báo lỗi trước khi gọi API.

## 7. Test

Hai tầng, cả hai đều bắt buộc.

**Tầng 1, server giả.** Chạy bằng `go test ./...` và `npm test`, không cần mạng hay key. Mỗi endpoint có ít nhất:
- một trường hợp thành công, kiểm tra method, path, query hoặc body đã gửi, và giá trị trả về;
- một trường hợp API trả lỗi, kiểm tra kiểu lỗi, status và mã lỗi.

Lõi có thêm: header xác thực và `User-Agent` có mặt, body lỗi không phải JSON, body 2xx hỏng, lỗi mạng, timeout, tham số bắt buộc rỗng, và test signer theo vector dùng chung.

**Tầng 2, sandbox thật.** Tối thiểu:
- một lời gọi đọc cho mỗi nhóm tài nguyên;
- một luồng chính chạy từ đầu tới cuối (tạo rồi đọc lại);
- một trường hợp lỗi thật từ server (ví dụ 404), để biết SDK đọc đúng body lỗi thật.

Quy tắc của test sandbox:
- Key lấy từ biến môi trường. Tên biến có trong `.env.example`. Thiếu key thì test tự bỏ qua, không báo fail.
- Go: tên test bắt đầu bằng `TestSandbox_`, đặt trong `*_integration_test.go`. Chạy riêng: `go test -run TestSandbox_ ./...`.
- TS: đặt trong `sandbox.test.ts`. `npm test` loại file này; `npm run test:sandbox` chạy nó.
- Không bao giờ gọi production. Helper tạo client phải dừng test nếu base URL là production.
- Test tạo dữ liệu thì dùng tên dễ nhận ra (`sdk-sandbox-test`), và README ghi rõ test để lại gì trên sandbox.
- Không commit file `.env` thật.

Khi bàn giao, nói rõ test sandbox đã chạy hay bị bỏ qua.

## 8. README và ví dụ

Theo thứ tự trong `reference/README.example.md`: cài đặt, lời gọi đầu tiên, xác thực, từng luồng chính, xử lý lỗi, cấu hình, cách chạy test.

- Lời gọi đầu tiên dài không quá 15 dòng, chép ra là chạy được với key sandbox.
- Mỗi luồng chính có một ví dụ chạy được trong `example/` (Go). Ví dụ phải build cùng với SDK.
- Ví dụ xử lý lỗi dùng đúng kiểu lỗi của SDK và in request id.
- Mọi đoạn code trong README phải khớp tên hàm và tên field hiện tại. Đổi API public thì sửa README trong cùng commit.

## 9. Comment

SDK là thư viện public, nên doc comment trên type, hàm và field public là tài liệu của sản phẩm: bắt buộc có, một tới ba dòng, nói điều người gọi cần biết (đơn vị, định dạng, khi nào lỗi). Ngoài ra không viết comment, trừ một dòng cho điều trông như lỗi nhưng cố ý (ví dụ thứ tự mã hóa rồi mới ký). Không ghi lịch sử thay đổi, không ghi "giống SDK kia", không để lại code chết kèm lời giải thích.

## 10. Phiên bản và phát hành

- Semver. Đổi tên hàm, tên field hoặc kiểu trả về là thay đổi phá vỡ: tăng số major khi đã từ 1.0 trở lên.
- Số phiên bản nằm ở một chỗ trong code (`Version`, `VERSION`) và khớp với tag git, `package.json`. `User-Agent` lấy từ hằng số đó.
- Go từ v2 trở lên: đường dẫn module phải có hậu tố `/v2`.
- Các SDK của cùng một API giữ cùng danh sách endpoint. Thêm endpoint ở một ngôn ngữ thì thêm ở ngôn ngữ kia, hoặc ghi rõ chỗ thiếu trong README.
- Không publish lên registry (npm, pkg.go.dev qua tag, PyPI) khi người dùng chưa bảo.

## 11. Trước khi nói "xong"

1. Go: `gofmt -l .` không in gì, `go vet ./...` và `go test ./...` qua, lint của repo qua. TS: `npm run type-check`, `npm test`, `npm run build` qua.
2. Test sandbox đã chạy và qua. Nếu không chạy được, nói rõ lý do.
3. Mỗi endpoint mới có file riêng, test thành công, test lỗi, và có mặt ở mọi ngôn ngữ của SDK.
4. Vector chữ ký giống nhau ở mọi ngôn ngữ và test signer qua.
5. Không có `float` cho tiền. Không có key, secret hay `.env` thật trong repo, trong log hay trong ví dụ.
6. README và `example/` khớp với API public hiện tại. `.env.example` có đủ biến mà test sandbox cần.
7. Số phiên bản khớp ở code, tag và file package.
