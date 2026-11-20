# <tên task>

Phase: intent
Cập nhật: YYYY-MM-DD
Loại: small | bug | feature | cross-repo | spike | high-risk (thêm: data | ops | ui)
Ưu tiên: P2
Hạn:
Branch:
- <repo>: <branch>

## Tóm tắt
<!-- Tối đa 4 dòng. Luôn đúng với trạng thái hiện tại. Người dùng có thể chỉ đọc mục này. -->
Đang làm: ...
Đã tới: ...
CẦN BẠN: không

## Mục tiêu và phạm vi
<!-- Tối đa khoảng 25 dòng. -->
Vấn đề: ...
Mục tiêu: ...
- Có làm: ...
- Không làm: ...
- Không được đổi: <hành vi, hợp đồng hoặc dữ liệu phải giữ nguyên>

| # | Tiêu chí (cho trước / khi / thì) | Test (repo: tên test) |
|---|---|---|
| 1 | | |

Hợp đồng thay đổi: không | <API, event, khóa Redis, migration, biến môi trường>

## Kế hoạch
<!-- Checklist. Đánh dấu [x] khi xong. Dài hơn một màn hình nghĩa là task quá to: tách ra. -->
<!-- Mỗi bước nói kết quả cần đạt và tiêu chí nó làm xong. Đường dẫn chính xác chỉ ghi cho file đã đọc code. -->
- [ ] 1. <repo>: <kết quả cần đạt> (tiêu chí 1, 2) — tester -> developer
  - thân: `path/to/file.go` (<vì sao>)
  - lá: `path/to/other.go`
  - hợp đồng: nhận <...>, trả <...>  <!-- chỉ khi bước này có bên khác dùng -->
- [ ] 2. verify: lint, test, chạy thật
- [ ] 3. review

Cách tắt khi có lỗi: <biến bật/tắt `TEN_BIEN` mặc định tắt | route mới chưa nối vào luồng cũ | deploy lại bản cũ>. Người dùng hiện tại bị ảnh hưởng không: ...

Lệch kế hoạch: không
<!-- Mỗi dòng: ngày, lệch gì, vì sao. Dừng và lập lại kế hoạch nếu phải đổi tiêu chí, hợp đồng hoặc thêm file thân. -->

<!-- Chỉ cho high-risk: mỗi file thân một đoạn code đề xuất ngắn (tối đa ~20 dòng), ngay dưới bước của nó. -->

## Nguyên nhân bug
<!-- Chỉ cho bug. Gốc lỗi (repo/file:dòng), bằng chứng, giả thuyết đã loại và vì sao. -->

## Quyết định và bằng chứng
<!-- Mỗi dòng một ý, có ngày. Bằng chứng: lệnh đã chạy và kết quả; ảnh trong proof/. Xóa token, key, dữ liệu cá nhân. -->

## Review
<!-- Từ reviewer / security-reviewer. Chỉ blocker và major ở bảng; minor gom một dòng. -->
| Mức độ | Thân / lá | Repo / file:dòng | Vấn đề | Cách sửa |
|---|---|---|---|---|

Kết luận: ...
