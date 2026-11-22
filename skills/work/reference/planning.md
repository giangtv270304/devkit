# Kế hoạch (work)

- feature, cross-repo, high-risk, spike: giao cho `architect`, kèm đường dẫn TASK.md. Bug: bạn tự viết kế hoạch từ mục "Nguyên nhân bug".
- Ghi kế hoạch thành checklist trong mục "Kế hoạch". Mỗi bước: repo, kết quả cần đạt, số tiêu chí mà bước đó làm xong, agent, các file kèm thân/lá (file thân trước).
- Kế hoạch chi tiết mà sai còn tệ hơn kế hoạch ngắn. Chỉ ghi đường dẫn file đã được mở và đọc. Khi bước thêm khóa mới vào file cấu hình hay dữ liệu mà code khác đọc hoặc gộp, mở code đó và ghi vào bước nếu nó phải đổi, vì code đọc thường bỏ qua khóa lạ. Không đoán tên file, tên hàm.
- Bước có bên khác dùng (repo khác, client): thêm một dòng hợp đồng, nhận gì và trả gì.
- Luôn có dòng "Cách tắt khi có lỗi". Chỉ có ba cách: biến môi trường bật/tắt, route mới chưa nối vào luồng cũ, hoặc deploy lại bản cũ. Với dòng tiền và xác thực, ưu tiên biến bật/tắt, mặc định tắt. Tên biến phải có trong `.env.example` và có test cho cả hai trạng thái.
- High-risk: dưới mỗi bước, thêm đoạn code đề xuất ngắn (tối đa ~20 dòng, dạng `diff`) cho từng file thân. Kiểm tra mọi đoạn "code hiện tại" với file thật. Không đưa code cho file lá.
- Branch mỗi repo: `feat/<slug>` (bug: `fix/<slug>`). Ghi vào `Branch:`.
- Nếu architect đề xuất ADR, viết bản nháp trong thư mục ADR của dự án.

Rà kế hoạch trước khi dừng:
- Mọi task: tự kiểm tra mỗi tiêu chí có bước làm xong nó, và không còn chỗ "sẽ quyết sau".
- High-risk và cross-repo: giao cho `reviewer` rà kế hoạch (phần "Khi được giao rà kế hoạch"). Chỉ đưa đường dẫn TASK.md, không đưa lý do của bạn. Sửa kế hoạch theo kết quả.
