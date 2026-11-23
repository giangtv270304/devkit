---
name: visual-plan
description: Dựng một trang trực quan (Artifact) cho thay đổi đang bàn - sơ đồ thành phần và luồng, hợp đồng API kèm ví dụ, trạng thái, bảng quyết định và ví dụ chạy với số thật, dữ liệu trước/sau - để người dùng thấy cách nó hoạt động trước khi duyệt. Dùng khi tới bước Kế hoạch của /work hoặc phương án của /design mà task là API mới, luồng mới, đổi logic qua từ ba thành phần hoặc đổi dữ liệu; hoặc khi người dùng nói "vẽ ra", "cho xem trực quan", "visualize", "nó chạy thế nào".
---

# visual-plan: xem thay đổi trước khi duyệt

Một sơ đồ cho thấy các phần nối với nhau, nhưng không cho thấy "với dữ liệu này thì ra gì". Lỗi logic nằm ở câu hỏi thứ hai, nên trang này luôn có ví dụ với giá trị thật bên cạnh hình.

## Khi nào dựng
- Dựng: API mới hoặc đổi hợp đồng, luồng mới, đổi logic qua từ ba thành phần hoặc đổi thứ tự bước, đổi bảng hay migration.
- Không dựng: sửa một file, đổi config, đổi tên. Khi đó mermaid trong TASK.md (nếu cần) là đủ.
- Đang bàn ý tưởng, chưa có plan: phác nhanh bằng Excalidraw theo ~/.claude/rules/diagrams.md. Dựng trang này khi đã có Mục tiêu và bản Kế hoạch đầu tiên.

## 1. Gom nội dung
Đọc Mục tiêu, tiêu chí nghiệm thu và Kế hoạch trong TASK.md (hoặc ADR nháp của /design), cùng code đã đọc khi lập plan. Mọi tên service, endpoint, bảng, trường trên trang phải lấy từ file đã mở. Chỗ chưa biết ghi "chưa biết" kèm câu hỏi, không đoán.

Xong khi: có danh sách tiêu chí, các thành phần bị đụng, và ít nhất ba ví dụ đầu vào (một bình thường, một biên, một lỗi).

## 2. Chọn các tab
Chỉ đưa tab có nội dung thật. Tab đầu luôn là Tổng quan.

| Tab | Có khi | Nội dung |
|---|---|---|
| Tổng quan | luôn | mục tiêu một câu; sơ đồ thành phần, phần mới xanh lá, phần sửa vàng cam, phần bỏ đỏ; "Cách tắt khi có lỗi" |
| Luồng | API, flow | `sequenceDiagram` gồm cả nhánh lỗi, timeout, retry, gọi lặp lại (idempotency) |
| Hợp đồng | API, webhook, event | bảng endpoint/event; ví dụ request và response JSON; mã lỗi và ý nghĩa; trước và sau khi đổi |
| Trạng thái | có cột status hay vòng đời | `stateDiagram-v2`; bảng ai chuyển, khi nào, chuyển sai thì sao |
| Logic | quy tắc tính, phân nhánh | bảng quyết định đầu vào -> kết quả; ví dụ chạy với số thật; bộ chạy từng bước: chọn một ví dụ, bấm "Bước tiếp" để tô sáng nhánh đang đi và giá trị ở mỗi bước |
| Dữ liệu | đổi bảng, migration, backfill | `erDiagram` phần bị đụng; vài dòng trước và sau; thứ tự expand -> backfill -> contract theo skill `data-design` |

Xong khi: mỗi tiêu chí nghiệm thu xuất hiện ở ít nhất một tab, trong một ví dụ hoặc một nhánh của sơ đồ.

## 3. Dựng trang
1. Gọi Artifact `quickstart` với intent `other`, rồi làm theo trang hướng dẫn nó trả về (skill `artifact-design`).
2. Viết `<task>/visual/index.html`. Mỗi tab là một `<section id=...>` xếp dọc, thanh tab là các link `#id` dính trên đầu; không ẩn section, vì mermaid vẽ trong phần tử ẩn ra kích thước 0. Sơ đồ đặt trong `<pre class="mermaid">`: Artifact tự vẽ, không tải thư viện. Màu trong `classDef` của mermaid là màu cố định, nên chọn màu nền nhạt có chữ tối để đọc được ở cả hai theme. Dữ liệu ví dụ để thẳng trong trang. Chữ trên trang viết tiếng Việt theo ~/.claude/rules/writing-vi.md; tên trong code giữ nguyên.
3. Publish với `icon: "diagram"`, `description` một câu nói task. Trang để riêng tư; chỉ gửi link cho người ngoài khi người dùng bảo, vì trang có tên thật của hệ thống.
4. Ghi link vào TASK.md dưới `## Kế hoạch`: `Trang trực quan: <url>`. Mermaid của luồng chính vẫn nằm trong Kế hoạch (diagrams.md mục 3), vì reviewer và session sau đọc file chứ không mở trang.

Xong khi: trang mở được, mọi sơ đồ vẽ ra không lỗi cú pháp, link đã ở TASK.md.

## 4. Đưa cho người dùng
Ở ĐIỂM DỪNG 1 của /work (hoặc lúc chọn phương án của /design), đưa link trang cùng link TASK.md, và nói một dòng nên xem tab nào trước: tab có ví dụ biên hoặc nhánh lỗi.

## 5. Khi kế hoạch đổi
`NEEDS_REPLAN`, `> NOTE:` đổi bước, hoặc người dùng sửa luồng: sửa `<task>/visual/index.html` rồi publish lại cùng đường dẫn, để link giữ nguyên. Sửa mermaid trong TASK.md cùng lượt.

## Khi không có tool Artifact
- Architect subagent và Herdr worker không dựng trang. Session đang nói chuyện với người dùng (hoặc lead trong Herdr) dựng sau khi nhận plan.
- Session không có tool Artifact: vẫn viết `<task>/visual/index.html` theo mục 3, thêm `<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script><script>mermaid.initialize({startOnLoad:true})</script>` vì trình duyệt thường không tự vẽ mermaid, rồi mở bằng `open <task>/visual/index.html`. Nói một dòng rằng trang chỉ có trên máy này.
