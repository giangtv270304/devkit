---
name: cross-repo-change
description: Dùng khi một thay đổi đụng tới nhiều hơn một repo, hoặc đổi một hợp đồng (API, webhook, event, database) mà service hay client khác đang dựa vào.
---

Đọc `.claude/project.md` ở gốc dự án nếu có: đường dẫn tài liệu kiến trúc và hợp đồng, lệnh kiểm tra, mục "Public docs".

1. Tìm mọi repo bị ảnh hưởng. Bắt đầu từ tài liệu kiến trúc và tài liệu hợp đồng của dự án. Sau đó xác nhận trong code: grep đường dẫn endpoint, tên event hoặc biến môi trường trên tất cả các repo. Tài liệu có thể đã cũ; code mới là sự thật.
2. Trong mục Kế hoạch của TASK.md, ghi: các repo theo thứ tự phụ thuộc (repo cung cấp trước, repo sử dụng sau), các bước cho từng repo kèm file thân/lá, một dòng hợp đồng cho mỗi bước (nhận gì, trả gì), thứ tự migration và deploy, cách giữ tương thích ngược. Hợp đồng thay đổi ghi ở dòng "Hợp đồng thay đổi" trong mục tiêu.
   Viết TASK.md và mọi ADR theo ~/.claude/rules/writing-vi.md. Dừng lại ở ĐIỂM DỪNG 1 của /work trước khi sửa code.
3. Làm phía repo cung cấp trước. Giữ tương thích ngược (field mới là tùy chọn, route cũ vẫn giữ) cho tới khi các repo sử dụng đã deploy xong. Giống như mở đường mới nhưng chưa đóng đường cũ, cho tới khi mọi xe đã chuyển sang.
4. Trong mỗi repo: làm theo CLAUDE.md của repo, chạy lệnh lint/test của repo, sinh lại spec nếu API thay đổi và repo có lệnh cho việc đó.
5. Nếu API công khai thay đổi, cập nhật những gì mục "Public docs" của project.md liệt kê.
6. Cập nhật tài liệu hợp đồng. Nếu có quyết định thiết kế, thêm một ADR.
7. Giữ TASK.md luôn mới: Tóm tắt, checklist, quyết định. Cuối cùng, tóm tắt branch và commit của từng repo. Không bao giờ push hay mở PR khi chưa hỏi.
