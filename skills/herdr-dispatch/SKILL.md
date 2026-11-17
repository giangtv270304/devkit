---
name: herdr-dispatch
description: Giao từng bước của một task nhiều repo cho các agent riêng, mỗi agent một tab trong Herdr app. Dùng khi session đang chạy trong Herdr (có biến HC_TERMINAL_ID), kế hoạch trong TASK.md đã được duyệt, và người dùng muốn các repo làm song song hoặc nói "giao việc", "dispatch", "mở tab cho từng repo".
---

# herdr-dispatch: mỗi repo một agent, mỗi agent một tab

Bạn là session điều phối. Bạn không sửa code trong repo. Bạn mở tab cho từng repo, giao việc, nhận báo cáo và giữ TASK.md luôn mới.

## Điều kiện
- `echo $HC_TERMINAL_ID` ra một địa chỉ (ví dụ `t3`). Nếu trống thì session không chạy trong Herdr: báo người dùng và dừng.
- TASK.md đã qua ĐIỂM DỪNG 1 của `/work` (người dùng đã duyệt kế hoạch). Chưa duyệt thì không giao việc.
- Template `~/.config/herdr-core/templates/worker.md` có sẵn. Template này chứa luật chung cho agent làm việc. Script tự chép luật đó vào câu giao việc, nên bạn không chép lại.
- Script mở agent bằng `claude --add-dir <thư mục cha của repo>`, để agent đọc được TASK.md, `thư mục hợp đồng (theo `.claude/project.md`)` và repo khác mà không cần sửa settings.

## Các bước
1. Đọc mục Kế hoạch của TASK.md. Lập danh sách: repo, số bước, bước nào phụ thuộc bước nào. Repo cung cấp đi trước, repo sử dụng đi sau (xem skill `cross-repo-change`).
2. Mỗi repo chỉ một agent ghi code cùng lúc. Hai bước cùng repo thì giao lần lượt cho cùng một tab (bằng `hc send`), hoặc hỏi người dùng có muốn dùng worktree không.
3. Giao các bước không phụ thuộc bước nào trước. Với mỗi bước, chạy:
   ```sh
   python3 ~/.claude/skills/herdr-dispatch/dispatch.py <đường dẫn repo> "<tên tab>" "<câu giao việc>"
   ```
   - Tên tab: tên repo ngắn, ví dụ `user-svc`, `card-svc`.
   - Mặc định mỗi agent một tab mới. Thêm `--place right` hoặc `--place down` để mở agent thành pane cạnh lead, trong cùng tab. Dùng pane khi có 2–3 repo và người dùng muốn thấy tất cả trên một màn hình, hoặc khi người dùng nói "mở cạnh nhau", "chia pane". Nhiều hơn 3 repo thì dùng tab, vì pane chia đều và sẽ quá hẹp.
   - Câu giao việc: một hai câu, gồm đường dẫn tuyệt đối tới TASK.md, số bước, branch, và branch chưa merge của repo khác nếu bước này cần. Ví dụ: `Task: /path/to/workspace/work/user-new-fields/TASK.md, làm bước 2 trên branch feat/user-new-fields. user-svc đang ở branch feat/user-new-fields, chưa merge.`
   - Script in ra `terminal` của agent mới. Ghi lại để gửi tin sau.
4. Ghi vào TASK.md: bước nào giao cho terminal nào, lúc nào.
5. Chờ báo cáo bằng `hc wait --children any`. Không dùng `sleep`. Agent báo về bằng `hc send`, tin nhắn hiện trong ô nhập của bạn.
6. Khi một bước xong: kiểm tra commit (`git -C <repo> log -1`) và dòng agent ghi vào TASK.md. Rồi giao các bước đang chờ bước đó.
7. Khi agent báo kẹt: trả lời bằng `hc send <terminal> "..."` nếu bạn tự quyết được trong phạm vi kế hoạch. Ngoài phạm vi thì hỏi người dùng.
8. Hết bước: tóm tắt trong TASK.md branch và commit của từng repo, rồi đi tiếp `/work` (kiểm tra, review). Không push, không mở PR khi chưa hỏi.

## Lệnh hay dùng
- `hc ls`: các agent đang chạy.
- `hc read <terminal> --lines 80`: xem màn hình của một agent.
- `hc send <terminal> "..."`: gửi việc tiếp hoặc trả lời.
- `hc interrupt <terminal>`: dừng lượt hiện tại của agent.

Agent trong tab do người dùng đóng thì coi như bước đó dừng. Ghi vào TASK.md và hỏi người dùng.
