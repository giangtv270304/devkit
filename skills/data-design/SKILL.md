---
name: data-design
description: Cách thiết kế và đổi dữ liệu - mô hình bảng, khóa, index, ràng buộc, migration an toàn trên database đang chạy, backfill, sổ cái và audit, dữ liệu cá nhân. Dùng khi thêm hoặc đổi bảng, cột, index, enum, khi viết migration hay backfill, khi chọn cách lưu một khái niệm mới, hoặc khi architect và reviewer gặp thay đổi schema.
argument-hint: "<khái niệm hoặc bảng cần thiết kế>"
---

# data-design: dữ liệu sống lâu hơn code

Code sai thì deploy lại. Dữ liệu sai thì phải sửa từng dòng, và có khi không sửa được. Vì vậy thay đổi dữ liệu luôn là file thân (~/.claude/rules/review-levels.md).

Đọc trước: `.claude/project.md` (database, thư mục migration, tài liệu hợp đồng), CLAUDE.md của repo, và các migration gần nhất để chép đúng kiểu viết của repo. Skill quy ước của ngôn ngữ (ví dụ `go-service`) thắng ở chỗ hai bên khác nhau.

## 1. Mô hình
Viết ra trước khi viết SQL, mỗi ý một dòng trong TASK.md hoặc ADR:
- Khái niệm là gì, ai tạo, ai đọc, sống bao lâu, có bị xóa không.
- Khóa: khóa chính, khóa tự nhiên (thứ làm một dòng là duy nhất ngoài đời thật) và ràng buộc `UNIQUE` cho nó. Thiếu ràng buộc thì hai request đồng thời tạo hai dòng.
- Trạng thái: liệt kê các trạng thái và chuyển trạng thái được phép. Lưu trạng thái là text hoặc enum có kiểm tra, không lưu nhiều cờ boolean ghép lại.
- Quan hệ: khóa ngoại khi hai bảng cùng một database. Khác service thì chỉ lưu id, ghi rõ bên nào là nguồn sự thật.
- Tiền: kiểu decimal hoặc số nguyên đơn vị nhỏ nhất, luôn đi kèm mã tiền tệ. Không float.
- Thời gian: lưu UTC có múi giờ (`timestamptz`). Có `created_at`, `updated_at`.
- Dữ liệu cá nhân: đánh dấu cột nào là dữ liệu cá nhân, ai được đọc, có cần mã hóa hay che khi xuất không.

Chuẩn hóa là mặc định. Chỉ sao chép dữ liệu sang bảng khác (denormalize) khi có truy vấn đo được là chậm, và ghi rõ cách giữ hai bản khớp nhau.

## 2. Index
- Mỗi index phải trỏ tới một truy vấn có thật: ghi truy vấn đó cạnh index.
- Index nhiều cột: cột lọc bằng `=` trước, cột lọc theo khoảng hoặc sắp xếp sau.
- Bảng lớn đang chạy: tạo index không khóa bảng (Postgres: `CREATE INDEX CONCURRENTLY`, migration không nằm trong transaction).

## 3. Migration trên database đang chạy
Đổi theo kiểu mở rộng rồi thu lại (expand / contract), mỗi bước deploy riêng:
1. Mở rộng: thêm cột, bảng hoặc index mới. Cột mới cho phép null hoặc có default rẻ. Code cũ vẫn chạy.
2. Ghi cả hai: code mới ghi vào chỗ cũ và chỗ mới.
3. Backfill: chép dữ liệu cũ theo lô (vài nghìn dòng một lần, có điểm dừng để chạy lại được), không một câu `UPDATE` cho cả bảng.
4. Đọc chỗ mới, kiểm tra số dòng và giá trị khớp.
5. Thu lại: bỏ ghi chỗ cũ, rồi mới xóa cột hay bảng cũ ở một migration sau.

Luật:
- Không sửa migration đã merge. Sửa bằng migration mới.
- Mỗi migration có bản down, hoặc ghi rõ vì sao không lùi được và cách khôi phục.
- Thêm `NOT NULL`, đổi kiểu cột, đổi tên cột trên bảng lớn: tách thành các bước ở trên, vì làm một lần sẽ khóa bảng hoặc làm code cũ lỗi.
- Script sửa dữ liệu theo luật script ops trong ~/.claude/rules/preferences.md: chạy thử mặc định, `-apply` mới ghi.
- Không chạy migration trên database dùng chung khi người dùng chưa đồng ý trong session này.

## 4. Sổ cái và audit
Số dư, giao dịch, trạng thái thanh toán: chỉ thêm dòng, không sửa dòng cũ. Số dư là tổng các dòng, hoặc là bảng tóm tắt được cập nhật cùng transaction với dòng sổ cái. Mỗi thay đổi có idempotency key với ràng buộc `UNIQUE`.

## 5. Ghi vào kế hoạch
Mỗi thay đổi dữ liệu trong Kế hoạch có: file migration, bước expand/contract nào, có backfill không và chạy thế nào, cách lùi, ai đang đọc bảng này (service, báo cáo, job xuất dữ liệu). Hợp đồng dữ liệu dùng chung thì cập nhật tài liệu hợp đồng của dự án.
