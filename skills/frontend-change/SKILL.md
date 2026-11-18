---
name: frontend-change
description: Cách làm và kiểm tra một thay đổi giao diện web hoặc mobile - màn hình, component, gọi API, trạng thái, form, điều hướng - theo quy ước của repo, với bằng chứng chạy thật trên trình duyệt hoặc simulator. Dùng trước khi sửa code giao diện web (React, Next.js, Vue...) hoặc mobile (React Native, Flutter, Swift, Kotlin), khi thêm màn hình hay gọi API mới từ client, hoặc khi review một thay đổi giao diện.
---

# frontend-change: người dùng thấy gì mới là thứ cần kiểm tra

Quy ước của từng stack nằm trong repo, không nằm ở đây: đọc CLAUDE.md của repo, mục "Conventions" trong `.claude/project.md`, và màn hình gần nhất cùng loại để chép cấu trúc. Không thêm thư viện giao diện, quản lý state hay gọi API mới khi chưa hỏi.

## Trước khi code
- Hợp đồng API mà màn hình dùng: đọc ở tài liệu hợp đồng của dự án hoặc spec do backend sinh ra, không đoán từ code backend. Kiểu dữ liệu ở client sinh từ spec nếu repo có lệnh cho việc đó.
- Liệt kê các trạng thái của màn hình: đang tải, có dữ liệu, rỗng, lỗi, không có quyền, mất mạng (mobile). Mỗi trạng thái là một tiêu chí trong TASK.md.
- Có file thiết kế hoặc ảnh thì ghi link vào TASK.md. Không có thì làm theo màn hình gần nhất.

## Khi code
- Tiền và số: định dạng bằng hàm chung của repo, tính toán bằng kiểu decimal hoặc để backend tính. Không cộng trừ tiền bằng số thực ở client.
- Không giữ token hay dữ liệu cá nhân trong `localStorage`, log hay thông báo lỗi. Mobile: secret trong Keychain / Keystore.
- Chữ hiển thị đi qua hệ thống dịch của repo nếu có. Không viết cứng chuỗi.
- Truy cập: nút và ô nhập có nhãn, dùng được bằng bàn phím (web), chữ đủ tương phản.
- Gọi lại khi lỗi, nút gửi chặn bấm hai lần.

## Kiểm tra
- Test theo cách repo đang có (unit cho logic, component test, e2e nếu có). Assert vào thứ người dùng thấy, không vào state bên trong.
- Web: chạy dev server, mở trang trong trình duyệt (browser pane của Claude desktop, hoặc trình duyệt trong Herdr), đi qua từng trạng thái, chụp màn hình vào `<task>/proof/`. Xem console không có lỗi mới.
- Mobile: chạy trên simulator hoặc emulator, chụp màn hình từng trạng thái, kiểm tra cả màn hình nhỏ và chế độ tối nếu app hỗ trợ.
- Không chạy được giao diện trên máy: ghi rõ là chưa xem thật và vì sao.
