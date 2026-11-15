---
paths:
  - "**/TASK.md"
---
# Mức review: thân và lá

Skill `work` và skill `review-pr` dùng chung file này. Mỗi file bị sửa có một mức review. Hãy hình dung code base như một cái cây. Gãy một chiếc lá thì cây không sao. Nứt thân thì cả cây đổ.

- **Thân**: người dùng đọc từng dòng. Một file là thân nếu nó đụng tới ít nhất một thứ sau:
  - xác thực và phân quyền (đăng nhập, token, chữ ký, API key, role),
  - dòng tiền: số dư, thanh toán, phí, tỷ giá, sổ cái,
  - migration database, hoặc dữ liệu cũ bị sửa,
  - hợp đồng mà bên khác đang dùng: API, event, webhook, khóa cache dùng chung, schema,
  - code dùng chung trong một repo: middleware, config, client gọi nhà cung cấp, khởi động server,
  - dữ liệu cá nhân,
  - luồng đang chạy cho người dùng thật, khi thay đổi không có biến bật/tắt hay route riêng,
  - mọi thứ mà mục "Thân riêng của dự án" trong `.claude/project.md` liệt kê.
- **Lá**: người dùng đọc lướt. Một file là lá khi nó đứng riêng và không thuộc danh sách thân. Ví dụ: một handler mới chưa nối vào luồng chính, một màn hình quản trị mới, một hàm chỉ đọc dữ liệu, test, tài liệu.

Khi không chắc, chọn thân. Mọi bảng tóm tắt xếp file thân lên trước.

Một thay đổi là **high-risk** khi có ít nhất một file thân thuộc nhóm tiền, xác thực, dữ liệu cá nhân, hoặc ký webhook. Thay đổi high-risk luôn cần thêm `security-reviewer`.
