# Cách giữ TASK.md (work)

- **Tóm tắt** ở đầu file luôn đúng với trạng thái hiện tại. Tối đa 4 dòng. Dòng `CẦN BẠN:` nói đúng việc người dùng phải làm, hoặc `không`.
- Viết ngắn. Không chép lại điều đã có ở mục khác. Không chép code vào file, trừ đoạn ngắn cho file thân của task high-risk.
- Mục "Mục tiêu và phạm vi" tối đa khoảng 25 dòng. Mục "Kế hoạch" tối đa một màn hình. Nếu dài hơn, task quá to: đề xuất tách thành nhiều task.
- File thay cho bàn giao giữa các session. Session sau chỉ biết những gì ghi trong file này.

Cập nhật TASK.md ở mọi ĐIỂM DỪNG, khi xong mỗi mục trong Kế hoạch, và trước khi kết thúc mỗi lượt trả lời có việc mới: Tóm tắt, `Phase:`, `Cập nhật:`, checklist, quyết định mới.
- `Phase:` chỉ chứa đúng một giá trị: `intent`, `plan`, `build`, `verify`, `review`, `ship`, `done`.
- `Cập nhật:` dạng `YYYY-MM-DD`.
- `Branch:` mỗi dòng `- <repo>: <branch>`. Dự án một repo thì ghi tên thư mục gốc.

Viết file bằng tiếng Việt, theo ~/.claude/rules/writing-vi.md. Giữ nguyên chính xác code, đường dẫn, lệnh và tên test.
