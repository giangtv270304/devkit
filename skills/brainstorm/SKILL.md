---
name: brainstorm
description: Cùng người dùng đi từ một ý còn mơ hồ tới một quyết định, cho mọi chủ đề, gồm sản phẩm, kiến trúc, cách làm, bài viết, lựa chọn cá nhân. Dùng khi người dùng chạy /brainstorm, nói "nghĩ giúp", "có những hướng nào", "nên làm thế nào", hoặc khi mục tiêu chưa đủ rõ để lập kế hoạch.
argument-hint: "<chủ đề hoặc vấn đề>"
---

# /brainstorm: từ ý mơ hồ tới quyết định

Kết quả của skill này là một bản quyết định, không phải code và không phải kế hoạch. Không viết code, không tạo file dự án, không lập kế hoạch chi tiết trước khi người dùng chọn xong.

Vấn đề nhỏ (một lựa chọn giữa hai thứ): làm nhanh, bỏ bước 4 và 5, trả lời trong chat.

## 1. Hiểu vấn đề
Đọc những gì đã có trước khi hỏi: code, tài liệu, file task, cuộc trò chuyện. Không hỏi điều mà chúng trả lời được.

Viết lại vấn đề trong 2-3 câu: ai gặp vấn đề, họ cần gì, điều gì đang cản. Nêu các ràng buộc bạn biết (thời gian, tiền, bảo mật, thứ không được đổi).

## 2. Hỏi, mỗi lần một câu
- Chỉ hỏi khi câu trả lời làm đổi các phương án. Nếu không, tự nêu giả định và đi tiếp.
- Mỗi lần một câu. Kèm câu trả lời bạn đề xuất và một dòng lý do, để người dùng chỉ cần nói "đúng" hoặc sửa.
- Tối đa 5 câu. Câu mở (vì sao, cho ai) hỏi trước, câu chi tiết hỏi sau.
- Sau khi hỏi xong, đọc lại cho người dùng: vấn đề, ràng buộc, thế nào là thành công. Hỏi "sai hay thiếu chỗ nào". Chờ họ xác nhận.

## 3. Mở rộng: nhiều phương án, chưa phán xét
- Viết ít nhất 12 phương án, mỗi phương án một dòng. Chưa chê, chưa xếp hạng.
- Ý tưởng của mô hình hay dồn về một cụm. Sau lượt đầu, làm thêm một lượt: "các phương án này giống nhau ở điểm nào", rồi viết thêm những phương án phá điểm giống đó.
- Lấy ý từ vài người bình thường khác nhau, không phải "chuyên gia sáng tạo": người mới dùng lần đầu, người vận hành lúc nửa đêm, người trả tiền, người sẽ phải bảo trì sau hai năm.
- Dùng một hoặc hai góc nhìn khi bí: làm ngược lại thì sao; lĩnh vực khác giải việc này thế nào; nếu chỉ có một ngày; nếu không được dùng thứ đang dùng; không làm gì cả thì sao.

## 4. Thu hẹp
Gom các phương án thành nhóm. Giữ 3 ứng viên khác nhau về bản chất, không phải ba biến thể của một ý. "Không làm gì" hoặc "làm bản nhỏ nhất" thường xứng đáng là một ứng viên.

Với mỗi ứng viên: một đoạn mô tả, được gì, mất gì, điều phải đúng thì nó mới chạy được.

## 5. Phản biện
Giao cho một agent con, không cho nó biết người dùng hay bạn đang nghiêng về phương án nào. Việc của nó, cho từng ứng viên:
- Giả sử sáu tháng sau phương án này đã thất bại. Kể 3 lý do có khả năng nhất.
- Giả định nào yếu nhất, và kiểm tra nó rẻ nhất bằng cách nào.

Chủ đề nhỏ thì tự làm bước này, không cần agent.

## 6. Nêu ý kiến của bạn
Nói thẳng bạn chọn ứng viên nào và một dòng lý do. Nếu bạn không đồng ý với hướng người dùng đang nghiêng về, nói rõ và nêu bằng chứng. Không đổi ý chỉ vì người dùng nhắc lại ý của họ; chỉ đổi khi có thông tin mới.

Nếu cần so sánh chặt hơn: hỏi người dùng 3-4 tiêu chí và trọng số, rồi chấm điểm trong một bảng.

Người dùng quyết định.

## 7. Ghi bản quyết định
Hỏi người dùng muốn lưu ở đâu: ADR của dự án (đường dẫn trong `.claude/project.md`), mục "Mục tiêu và phạm vi" của một TASK.md, hoặc chỉ trong chat. Viết theo ~/.claude/rules/writing-vi.md.

```
## Quyết định: <một dòng>
Ngày: YYYY-MM-DD
Vấn đề: ...
Đã chọn: ... Vì: ...
Đã bỏ: <phương án> — <lý do một dòng>
Giả định phải đúng: ...
Xem lại khi: <điều kiện cụ thể làm quyết định này hết đúng>
```

Bước tiếp theo, đề xuất trong một dòng: `/research` nếu còn giả định chưa kiểm tra; `/work <slug>` nếu đã đủ rõ để làm; `/retro` nếu trong phiên người dùng đã phải sửa cách bạn làm.
