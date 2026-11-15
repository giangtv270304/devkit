---
paths:
  - "**/TASK.md"
  - "**/work/**/*.md"
  - "**/adr/*.md"
  - "**/notes/*.md"
  - "**/research/*.md"
---
# Cách viết file md cho task, ADR, note và kết quả research

Các file md mà skill tạo ra cho người đọc phải viết bằng tiếng Việt: file task `TASK.md`, ADR, note, file kết quả của skill `research` và `brainstorm`.

Các thứ sau vẫn giữ tiếng Anh:
- Code, comment trong code, tên hàm, tên biến, tên test.
- `CLAUDE.md`, `.claude/project.md`, tài liệu hợp đồng và tài liệu API công khai của dự án.
- Commit message và mô tả PR.
- Khóa trong frontmatter (ví dụ `based_on`, `topic`, `updated`) và các giá trị cố định mà skill dùng (ví dụ `Phase: build`, `Loại: bug`, `CẦN BẠN:`).

Nếu `.claude/project.md` của dự án ghi một ngôn ngữ khác cho tài liệu, làm theo file đó.

## Văn phong: dễ hiểu như giải thích cho trẻ 5 tuổi

Viết theo tinh thần ASD-STE100 (chuẩn tiếng Anh đơn giản dùng cho tài liệu bảo trì máy bay), áp dụng cho tiếng Việt, khoảng 80% mức chặt của chuẩn đó.

- Mỗi câu một ý. Câu ngắn, đoạn ngắn.
- Dùng câu chủ động, có chủ ngữ rõ ràng. Viết "Service gửi webhook", không viết "Webhook được gửi".
- Dùng từ thông dụng. Một từ giữ một nghĩa trong cả file. Đã gọi là "lệnh rút tiền" thì không đổi sang "giao dịch payout" ở đoạn sau.
- Không dùng từ viết tắt hay thuật ngữ kỹ thuật, trừ khi người dùng đã dùng nó trước, hoặc có giải thích ngắn ngay trong câu đó. Ví dụ: "idempotent (gửi lại nhiều lần vẫn chỉ tạo một kết quả)".
- Không tự đặt ra từ viết tắt, nhãn hay từ chuyên ngành mới.
- Với ý khó, đưa một ví dụ so sánh đời thường.
- Giữ nguyên chính xác đường dẫn, lệnh, tên sản phẩm, tên repo và con số.
- Tiêu đề mục viết bằng tiếng Việt, theo mẫu của skill.
- Viết ngắn. Người đọc lười đọc. Không chép lại điều đã ghi ở mục khác.
