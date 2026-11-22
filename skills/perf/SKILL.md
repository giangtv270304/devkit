---
name: perf
description: Cách tìm và sửa chỗ chậm bằng số đo, không đoán - đặt mục tiêu, đo trước, profile, sửa một chỗ, đo lại. Gồm Go (pprof, benchmark), Postgres (EXPLAIN ANALYZE, index) và web (Lighthouse, bundle). Dùng khi người dùng nói "chậm", "tối ưu", "tốn CPU/RAM", "query lâu", "timeout", hoặc khi một tiêu chí trong TASK.md có con số về độ trễ hay tải.
---

# perf: đo trước, sửa sau

Tối ưu mà không đo là đoán. Giống như sửa xe mà không mở nắp máy: có khi thay nhầm bánh xe.

## 1. Mục tiêu và số đo gốc
- Viết mục tiêu bằng con số: "p95 của `GET /orders` dưới 200ms với 500 request/giây", không phải "nhanh hơn".
- Đo bản hiện tại trên máy hoặc staging, ghi lệnh và kết quả. Không đo được thì dừng và nói thiếu gì.
- Chạy ít nhất 3 lần. Kết quả lệch nhau hơn 10% thì môi trường chưa ổn định: tắt việc khác, cố định dữ liệu.

## 2. Tìm chỗ tốn
- Go: `go test -bench=. -benchmem -count=5 ./pkg/...`, `go test -cpuprofile cpu.out -memprofile mem.out`, rồi `go tool pprof -top cpu.out`. Service đang chạy: `net/http/pprof`, chỉ bật ở máy local hoặc sau xác thực.
- Postgres: `EXPLAIN (ANALYZE, BUFFERS)` trên dữ liệu cỡ thật, chỉ trên database local hoặc bản sao. Tìm `Seq Scan` trên bảng lớn, số dòng ước tính lệch xa số dòng thật, sort trên đĩa.
- Gọi ra ngoài: đếm số lần gọi mỗi request. N+1 (một query cho mỗi dòng) thường là thủ phạm.
- Web: Lighthouse hoặc tab Performance, kích thước bundle, số request.
- Chỉ sửa chỗ chiếm phần lớn thời gian. Hàm chiếm 2% thì nhanh gấp đôi cũng chỉ lợi 1%.

## 3. Sửa một chỗ, đo lại
- Mỗi lần một thay đổi, đo lại bằng đúng lệnh ở bước 1. So số trước và sau trong cùng một bảng.
- Index mới theo skill `data-design` (mỗi index trỏ tới một truy vấn thật, tạo không khóa bảng).
- Cache là quyết định thiết kế, không phải cách sửa nhanh: ghi rõ khóa, thời gian sống, cách xóa khi dữ liệu đổi, và dữ liệu cũ được phép tới mức nào. Hỏi người dùng trước.
- Giữ benchmark lại trong repo nếu repo đã có benchmark, để lần sau phát hiện chậm lại.

## 4. Ghi kết quả
Vào "Quyết định và bằng chứng" của TASK.md: mục tiêu, lệnh đo, số trước, số sau, chỗ đã sửa. Không đạt mục tiêu thì nói thẳng, kèm chỗ tốn tiếp theo trong profile.

## Gotchas
- Benchmark Go bị trình biên dịch bỏ qua kết quả không dùng: gán vào biến ở ngoài vòng lặp.
- Dữ liệu test nhỏ cho kế hoạch query khác hẳn dữ liệu thật.
- Lần chạy đầu chậm vì cache lạnh, JIT, kết nối mới: bỏ lần đầu hoặc chạy làm nóng trước.
