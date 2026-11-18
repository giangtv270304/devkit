# Kiểm tra (work)

Bạn tự kiểm tra, không tin báo cáo của agent. Chạy bộ kiểm tra của mỗi repo đã sửa: các lệnh trong mục "Checks" của project.md, hoặc trong CLAUDE.md của repo. Nếu API thay đổi, chạy lại lệnh sinh spec của repo.

Mỗi lời khẳng định cần đúng một loại bằng chứng, vừa chạy xong:

| Lời khẳng định | Bằng chứng bắt buộc |
|---|---|
| test qua | output và mã thoát của lệnh test, chạy sau lần sửa cuối |
| lint sạch | output của lệnh lint |
| agent đã làm xong | `git diff` của repo, không phải lời của agent |
| bug đã sửa | triệu chứng ban đầu được thử lại và không còn |
| tiêu chí N đạt | test tên X qua, hoặc request và response thật |

Sau đó lấy bằng chứng chạy thật:
- API hoặc handler: chạy service trên máy, gọi endpoint cho trường hợp đúng và ít nhất một trường hợp lỗi. Ghi request, status, response rút gọn. Xóa token, API key và dữ liệu cá nhân.
- Giao diện: mở trang bằng browser, chụp màn hình, lưu vào `<task>/proof/`.
- Có biến bật/tắt: kiểm tra cả lúc bật và lúc tắt.
- Không chạy được trên máy: ghi rõ là chưa chạy thật và vì sao. Không bịa bằng chứng.

Ghi mỗi kết quả một dòng vào "Quyết định và bằng chứng". Nếu có gì fail, gửi lại cho developer kèm output lỗi.
