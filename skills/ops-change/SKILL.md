---
name: ops-change
description: Cách thay đổi hạ tầng và vận hành an toàn - Dockerfile, CI/CD, cấu hình deploy (Kubernetes, compose, Terraform), biến môi trường và secret, giám sát, cảnh báo, rollback, runbook. Dùng khi sửa file CI, Dockerfile, manifest deploy, hạ tầng dạng code, thêm biến môi trường, đổi cách deploy, thêm dashboard hoặc cảnh báo, hoặc viết runbook xử lý sự cố.
argument-hint: "<thay đổi vận hành>"
---

# ops-change: thay đổi hạ tầng phải lùi được

Lỗi trong code hỏng một tính năng. Lỗi trong hạ tầng hỏng mọi tính năng cùng lúc. Vì vậy mọi file deploy, CI, hạ tầng và cấu hình dùng chung là file thân (~/.claude/rules/review-levels.md).

Đọc trước: `.claude/project.md`, CLAUDE.md của repo, và cách repo đang deploy (thư mục CI, manifest, Makefile). Chép kiểu viết đang có, không mang công cụ mới vào khi chưa hỏi.

## Luật
- Không chạy lệnh ghi lên môi trường thật (apply, deploy, xóa tài nguyên, đổi DNS, xoay secret) khi người dùng chưa đồng ý trong session này. Lệnh xem trước (`terraform plan`, `kubectl diff`, `--dry-run`, `helm template`) thì chạy được và đưa kết quả cho người dùng.
- Secret không nằm trong code, image hay log. Biến mới thêm vào `.env.example` với giá trị giả, và ghi nơi giá trị thật được cấp (secret manager, biến CI).
- Ghim phiên bản: image base, action CI, chart, provider. Không dùng `latest`.
- Image: build nhiều tầng, chạy bằng user không phải root, chỉ chép thứ cần chạy.
- Thay đổi ảnh hưởng nhiều service (gateway, mạng, database dùng chung, CI chung): ghi danh sách service bị ảnh hưởng và thứ tự làm.

## Mỗi thay đổi ghi vào Kế hoạch
1. Thay đổi gì, ở môi trường nào trước (dev hoặc staging trước, production sau).
2. Cách kiểm tra trước khi áp dụng: lệnh xem trước và kết quả mong đợi.
3. Cách biết là chạy đúng sau khi áp dụng: health check, log, chỉ số, dashboard.
4. Cách lùi: lệnh hoặc bước cụ thể, mất bao lâu, dữ liệu có bị ảnh hưởng không.
5. Ai cần biết: người trực, team khác.

## Giám sát và cảnh báo
- Mỗi tính năng mới đụng tiền hoặc nhà cung cấp bên ngoài có ít nhất: đếm lỗi, độ trễ, và một cảnh báo khi lỗi vượt ngưỡng.
- Log có trường để lần theo một request (request id, id nghiệp vụ), không có dữ liệu cá nhân hay secret.
- Cảnh báo phải dẫn tới một việc cụ thể. Cảnh báo không ai xử lý thì bỏ.

## Runbook
Sự cố đã xảy ra hai lần thì viết runbook: dấu hiệu, cách xác nhận, cách xử lý tạm, cách sửa gốc, ai cần báo. Lưu trong thư mục tài liệu của dự án (project.md). Script sửa dữ liệu theo luật script ops trong ~/.claude/rules/preferences.md.
