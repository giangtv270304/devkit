---
name: debug
description: Cách tìm và sửa lỗi theo root cause, không đoán mò. Dùng khi gặp bug, test fail không rõ lý do, lỗi chỉ xảy ra đôi khi, hoặc khi đã sửa một lần mà lỗi vẫn còn.
---

# debug: root cause trước, sửa sau

Skill này là cách làm. Agent `tester` viết và chạy test theo tiêu chí trong TASK.md; agent `developer` sửa code theo kế hoạch. Skill này nói cách tìm ra chỗ cần sửa.

## Quy trình

1. **Tái hiện.** Có một lệnh hoặc một test fail ổn định, in đúng triệu chứng. Chưa tái hiện được thì chưa sửa gì; thu thập thêm (log, input, phiên bản, môi trường). Test tái hiện giữ lại làm test hồi quy.
2. **Thu hẹp.** Tìm commit hoặc input nhỏ nhất còn gây lỗi (`git bisect`, cắt bớt input, tắt từng phần). Đọc đường đi của dữ liệu từ nơi lỗi hiện ra ngược về nơi nó sinh ra.
3. **Một giả thuyết một lần.** Viết giả thuyết thành câu kiểm chứng được: "nếu X đúng thì lệnh Y sẽ in Z". Chạy Y. Kết quả loại trừ giả thuyết thì ghi lại.
4. **Sửa đúng một chỗ.** Chỉ sửa khi bằng chứng chỉ vào nguyên nhân, không chỉ vào triệu chứng. Không sửa nhiều chỗ cùng lúc, vì lỗi hết rồi cũng không biết chỗ nào có tác dụng.
5. **Xác nhận.** Chạy lại bước 1: hết lỗi. Chạy cả bộ test của repo. Gỡ log và code dò lỗi tạm.

## Sổ ghi

Giữ một danh sách ngắn trong báo cáo (hoặc mục "Nguyên nhân bug" của TASK.md nếu task có):
- Triệu chứng và lệnh tái hiện.
- Đã loại trừ: giả thuyết, cách thử, kết quả.
- Nguyên nhân gốc, bằng chứng, và vì sao chỗ sửa là chỗ đúng.

## Khi nào dừng

Ba giả thuyết liên tiếp bị loại hoặc ba lần sửa không qua: dừng, báo ba lần đã thử và điều nghi ngờ về thiết kế. Đừng thử lần thứ tư.

## Gotchas

- Thêm `try/catch`, retry, `sleep` hoặc nới điều kiện để lỗi biến mất là che triệu chứng, không phải sửa.
- Lỗi "chỉ đôi khi" thường là thứ tự chạy, thời gian, dữ liệu dùng chung hoặc cache. Tái hiện bằng cách ép điều kiện (chạy lặp, đổi seed, thêm độ trễ), đừng chờ may.
- Log ở nơi lỗi hiện ra hay sai chỗ: nguyên nhân thường nằm ở bước trước đó.
- Sửa test cho khớp với hành vi sai là đổi bằng chứng. Chỉ sửa test khi chứng minh được test sai.
- Đừng tin tên hàm, comment hay tài liệu cũ; chạy code để xem nó làm gì.
- Lỗi chỉ ở môi trường khác (CI, prod): so sánh phiên bản, biến môi trường, dữ liệu trước khi nghi code.
