---
name: design
description: Thiết kế kiến trúc cho một hệ thống, service hoặc luồng mới - bối cảnh, ràng buộc, yêu cầu phi chức năng, các phương án, quyết định ghi thành ADR kèm sơ đồ và hợp đồng. Dùng khi người dùng chạy /design, hỏi "nên thiết kế thế nào", cần chọn giữa các kiến trúc, thêm service hoặc tích hợp mới, hoặc khi /work gặp task có lựa chọn thiết kế lớn.
argument-hint: "<hệ thống, service hoặc luồng cần thiết kế>"
---

# /design: từ bài toán tới một quyết định có thể review

Kết quả là một ADR người dùng đọc được trong năm phút, không phải bài luận. Code chưa viết ở bước này.

Ý còn mơ hồ (chưa biết muốn gì) thì dùng skill `brainstorm` trước. Đã biết muốn gì, cần chọn cách làm, thì dùng skill này.

## 1. Bối cảnh
Đọc `.claude/project.md`, tài liệu kiến trúc và hợp đồng mà nó chỉ tới, và code thật của các service liên quan. Giao cho agent `architect` khi phải đọc nhiều repo. Viết:
- Bài toán trong hai câu: ai cần gì, vì sao bây giờ.
- Hệ thống hiện tại liên quan: service nào, dữ liệu nào, ai gọi ai. Chỉ ghi điều đã kiểm tra trong code.
- Ràng buộc: thứ không được đổi, hạn chót, nhà cung cấp, luật.

## 2. Yêu cầu phi chức năng
Mỗi dòng một con số hoặc "chưa biết, hỏi người dùng". Không đoán số:
- Tải: bao nhiêu request hoặc bản ghi mỗi giây, lúc đỉnh.
- Độ trễ chấp nhận được.
- Khi hỏng: phần nào được phép chậm, phần nào phải dừng hẳn, dữ liệu nào không được mất. Gửi lại nhiều lần thì sao.
- Bảo mật và dữ liệu cá nhân.
- Chi phí và người vận hành: ai trực, ai deploy.

## 3. Phương án
Hai tới ba phương án thật sự khác nhau. Mỗi phương án: sơ đồ một hình, cách nó đáp ứng từng yêu cầu ở mục 2, cái giá phải trả, và cách lùi khi sai. Một phương án luôn là "làm ít nhất có thể trong hệ thống hiện tại".

Sơ đồ viết bằng mermaid trong file markdown: `flowchart` cho thành phần, `sequenceDiagram` cho luồng. Mỗi sơ đồ tối đa khoảng 10 hộp. Khi bàn phương án với người dùng, dựng trang trực quan theo skill `visual-plan`, mỗi phương án một tab Tổng quan và Luồng để so sánh; mermaid vẫn là bản lưu trong ADR.

## 4. Quyết định
- Đề xuất một phương án và một câu lý do. Hỏi người dùng khi các phương án đổi chi phí, người vận hành hay hợp đồng với bên ngoài.
- Ghi ADR vào thư mục ADR của dự án. Mẫu: `<ADR dir>/0000-template.md` nếu dự án có, không thì `~/.claude/devkit/templates/adr.md`. Viết theo ngôn ngữ tài liệu trong project.md.
- Thay đổi dữ liệu: theo skill `data-design`. Thay đổi deploy, hạ tầng, CI: theo skill `ops-change`. Nhiều repo hoặc đổi hợp đồng: skill `cross-repo-change`.
- Ghi hợp đồng mới hoặc thay đổi vào tài liệu hợp đồng của dự án (đường dẫn trong project.md).

## 5. Sang làm
Khi người dùng duyệt ADR: đánh dấu ADR là đã chấp nhận, rồi mở `/work <slug>` với link ADR trong Mục tiêu. Kế hoạch của `/work` chia ADR thành các bước nhỏ review được.
