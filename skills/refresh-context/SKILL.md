---
name: refresh-context
description: Dùng khi được nhờ tạo, làm mới hoặc rà soát CLAUDE.md của một repo hay tài liệu kiến trúc của dự án, hoặc sau khi một repo thay đổi lớn.
---

Đọc `.claude/project.md` ở gốc dự án nếu có: đường dẫn tài liệu kiến trúc, hợp đồng và note.

Khi thông báo lệch tài liệu của hook SessionStart liệt kê các repo, các repo đó nằm trong phạm vi. Chỉ đọc `git -C <repo> log --stat <sha đã ghi>..HEAD` và các file đã đổi, không đọc cả repo.

Với mỗi repo trong phạm vi:
1. Đọc README, `.env.example` (chỉ tên biến, không bao giờ đọc .env thật), Makefile hoặc phần scripts của file build, thư mục config, và các file service/route.
2. Viết lại `<repo>/CLAUDE.md`, dưới 60 dòng, chỉ gồm những gì Claude không tự đoán được: mục đích, lệnh chạy/lint/test/sinh code, cấu trúc thư mục, service phía trên và phía dưới, điểm dễ sai và quy tắc. Đánh dấu điều suy đoán là "(unverified)". Giữ các phần do người viết, trừ khi phần đó sai; hỏi trước khi xóa.
   CLAUDE.md viết bằng tiếng Anh.
3. Cập nhật tài liệu kiến trúc (sơ đồ, luồng, port, chỗ còn thiếu) và tài liệu hợp đồng nếu quan hệ phụ thuộc thay đổi.
4. Dự án nhiều repo: giữ CLAUDE.md ở thư mục gốc dưới khoảng 80 dòng. File đó là tấm bản đồ, không phải sách hướng dẫn.
5. Ghi lại lần rà soát: `python3 ${CLAUDE_SKILL_DIR}/context_state.py record <repo> [<repo> ...]`, chạy từ thư mục gốc dự án (dự án một repo: `record .`). Nhờ vậy, lần kiểm tra lệch tài liệu tiếp theo bắt đầu từ HEAD mới. Lần `record` đầu tiên tạo file trạng thái và bật việc kiểm tra cho dự án đó.
6. Nếu một note hoặc một trang tài liệu có `based_on` (trang luồng, hợp đồng) về repo này bị đánh dấu cũ, kiểm tra nó với code. Cập nhật nội dung, `based_on` và `updated`. Hook kiểm tra thư mục note, hoặc các file và thư mục ghi ở dòng `Based-on docs:` trong `.claude/project.md`.
7. Báo lại những gì đã đổi và những gì bạn không kiểm tra được.

Dạng của một note (trong thư mục note của dự án):
```
---
topic: <một dòng>
based_on: <repo>@<short sha>, <repo>@<short sha>
updated: YYYY-MM-DD
---
<câu trả lời trước, rồi đường đi qua code với file:hàm, rồi điểm dễ sai>
```
