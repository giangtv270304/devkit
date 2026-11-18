---
name: tdd
description: Cách viết code theo test trước (red, green, refactor), từng hành vi một vòng. Dùng khi thêm hành vi mới, sửa bug cần test hồi quy, hoặc khi người dùng nói "tdd", "viết test trước".
---

# tdd: test fail đúng lý do rồi mới code

Skill này là cách làm. Agent `tester` viết và chạy test theo bảng tiêu chí trong TASK.md; skill này dùng khi bạn tự lặp vòng test và code trong một bước, hoặc khi `developer` cần thêm test cho phần mình viết. Test theo tiêu chí TASK.md vẫn do `tester` giữ.

## Mỗi vòng, một hành vi

1. **Red.** Viết một test cho một hành vi, đặt theo hành vi (`rejects expired token`), không theo hàm. Theo mẫu test gần nhất của repo. Chạy nó.
2. **Xem nó fail đúng lý do.** Đọc output: lỗi phải là "hành vi chưa có" (assert sai, hàm chưa tồn tại ở chỗ test gọi), không phải lỗi cú pháp, import, fixture hay môi trường. Fail sai lý do thì sửa test, chưa viết code.
3. **Green.** Viết code ít nhất đủ cho test qua. Không thêm hành vi chưa có test.
4. **Chạy cả bộ test** của repo. Test cũ vẫn qua.
5. **Refactor** khi cả bộ đang xanh, chạy lại sau mỗi bước nhỏ. Rồi sang hành vi tiếp theo.

Sửa bug: viết test tái hiện lỗi trước, thấy nó fail, sửa, thấy nó qua. Cách tìm nguyên nhân nằm ở skill `debug`.

## Gotchas

- Test chưa từng thấy fail thì chưa chứng minh gì. Test qua ngay ở vòng đầu: kiểm tra nó có thật sự chạy và assert điều cần không.
- Không sửa test cho khớp code. Test fail sau khi code: code sai, hoặc yêu cầu đổi (hỏi người dùng). Chỉ sửa test khi chứng minh được test sai.
- Đừng viết nhiều test rồi mới code. Một vòng một hành vi, để lỗi chỉ về một chỗ.
- Mock quá tay thì test chỉ kiểm tra mock. Dùng thật khi rẻ (DB test, server giả của repo).
- Không thêm thư viện test mới. Dùng cái repo đang dùng.
- Test phụ thuộc thời gian, thứ tự hoặc mạng sẽ flaky: ép đồng hồ, seed, dữ liệu cố định.
