# Cách giữ TASK.md (work)

- **Tóm tắt** ở đầu file luôn đúng với trạng thái hiện tại. Tối đa 4 dòng. Dòng `CẦN BẠN:` nói đúng việc người dùng phải làm, hoặc `không`.
- Viết ngắn. Không chép lại điều đã có ở mục khác. Không chép code vào file, trừ đoạn ngắn cho file thân của task high-risk.
- Mục "Mục tiêu và phạm vi" tối đa khoảng 25 dòng. Mục "Kế hoạch" tối đa một màn hình. Nếu dài hơn, task quá to: đề xuất tách thành nhiều task.
- File thay cho bàn giao giữa các session. Session sau chỉ biết những gì ghi trong file này.

Cập nhật TASK.md ở mọi ĐIỂM DỪNG, khi xong mỗi mục trong Kế hoạch, và trước khi kết thúc mỗi lượt trả lời có việc mới: Tóm tắt, `Phase:`, `Cập nhật:`, checklist, quyết định mới.
- `Phase:` chỉ chứa đúng một giá trị: `intent`, `plan`, `build`, `verify`, `review`, `ship`, `done`.
- `Cập nhật:` dạng `YYYY-MM-DD`.
- `Ưu tiên:` đúng một giá trị, chọn bằng câu hỏi đầu tiên trả lời "có":
  - `P0`: người dùng thật, tiền hoặc bảo mật đang bị ảnh hưởng. Làm ngay, bỏ việc khác.
  - `P1`: có người đang bị chặn vì chờ việc này (tenant, đồng nghiệp, PR), hoặc hạn trong 3 ngày.
  - `P2`: quan trọng nhưng chưa gấp. Mặc định.
  - `P3`: làm khi rảnh.
- `Hạn:` dạng `YYYY-MM-DD` khi có hạn đã hứa với ai đó; để trống khi không có. `status.py` coi task còn 2 ngày hoặc quá hạn là `P1`, dù dòng `Ưu tiên:` ghi thấp hơn.
- `Branch:` mỗi dòng `- <repo>: <branch>`. Dự án một repo thì ghi tên thư mục gốc.

Viết file bằng tiếng Việt, theo ~/.claude/rules/writing-vi.md. Giữ nguyên chính xác code, đường dẫn, lệnh và tên test.
