---
name: herdr-dispatch
description: Mở agent riêng trong Herdr app, mỗi agent một pane cạnh session hiện tại hoặc một tab. Hai cách dùng - việc lẻ (kiểm tra, tra cứu) với template helper, và các bước ghi code của một task đã duyệt với template worker (nhiều repo thì mỗi repo một agent, một repo thì mỗi bước một git worktree). Dùng khi session chạy trong Herdr (có biến HC_TERMINAL_ID) và người dùng nói "mở một agent khác", "mở agent", "agent riêng", "giao việc", "dispatch", "mở tab cho từng repo", "chia worktree", hoặc khi /lead, /work giao các bước song song.
---

# herdr-dispatch: lead giao việc, agent con làm, lead ghi lại

Bạn là session điều phối. Bạn không sửa code. Bạn mở agent cho từng bước, giao việc, nhận báo cáo và là người duy nhất ghi TASK.md.

## Việc lẻ: template helper
Người dùng bảo mở một agent cho một việc không thuộc kế hoạch nào (kiểm tra database, tra log, thử một lệnh): không cần TASK.md hay kế hoạch đã duyệt.
```sh
python3 ~/.claude/skills/herdr-dispatch/dispatch.py <thư mục> <tên> "<việc, chỉ đọc hay được ghi gì>" --template helper
```
Agent helper mặc định chỉ đọc và báo về bằng `hc send`. Pane mới lấy biến môi trường của Herdr, không lấy của shell nơi bạn đang chạy: việc cần biến kết nối thì nói tên biến trong câu giao việc, không chép giá trị. Phần còn lại của skill này dành cho các bước ghi code của một task.

## Điều kiện (bước ghi code của một task)
- `echo $HC_TERMINAL_ID` ra một địa chỉ (ví dụ `t3`). Nếu trống thì session không chạy trong Herdr: báo người dùng và dừng.
- Kế hoạch đã được người dùng duyệt: TASK.md đã qua ĐIỂM DỪNG 1 của `/work`, hoặc người dùng đã duyệt TASK.md ngắn do `/lead` viết, hoặc mục "Đồng ý sẵn" trong `LEAD.md` cho phép đúng loại việc này. Chưa duyệt thì không giao việc.
- Mục Kế hoạch ghi file của từng bước trong dấu backtick. Script đặt `DEVKIT_ROLE=worker` cho agent, nên hook `plan_gate` hỏi người dùng khi agent sửa file không có trong Kế hoạch, giống developer của `/work`.
- Template `~/.config/herdr-core/templates/worker.md` có sẵn. Script tự chép luật trong đó vào câu giao việc, nên bạn không chép lại.

## Chọn chế độ
Đọc `Layout:` trong `.claude/project.md` của project, hoặc nhìn mục Kế hoạch.

| Trường hợp | Chế độ | Vì sao |
|---|---|---|
| Các bước nằm ở các repo khác nhau (`Layout: multi-repo`) | Mỗi repo một agent, không có `--worktree` | Mỗi repo đã là một thư mục riêng, không agent nào giẫm lên agent khác |
| Nhiều bước độc lập trong cùng một repo (`Layout: single-repo`) | Mỗi bước một worktree: `--worktree <branch>` | Hai agent ghi vào cùng một thư mục sẽ ghi đè nhau |
| Các bước cùng repo nhưng nối tiếp nhau | Một agent, giao lần lượt bằng `hc send` | Worktree không giúp gì khi bước sau cần code của bước trước |
| Repo đó đang bận: bản checkout chính không ở branch mặc định, có thay đổi chưa commit, hoặc `hc ls` có agent của task khác đang làm trong đó | Luôn dùng worktree, kể cả `Layout: multi-repo`: `--worktree <slug>/<repo> --base <branch mặc định>` | Bản checkout chính chỉ đứng trên một branch, hai task dùng chung sẽ đổi branch hoặc ghi đè file của nhau. `--base` vì HEAD lúc đó là branch của task kia |

Kế hoạch mà hai bước song song cùng sửa một file thì đừng chia worktree: gộp thành một bước, hoặc hỏi người dùng. Worktree chỉ tránh ghi đè trong lúc làm, không tránh xung đột khi gộp.

## Các bước
1. Đọc mục Kế hoạch của TASK.md. Lập danh sách: bước, repo, bước nào phụ thuộc bước nào. Với mỗi repo, kiểm tra nó có đang bận không (`git -C <repo> branch --show-current`, `git -C <repo> status --short`, `hc ls`) để chọn chế độ ở bảng trên. Nhiều repo thì repo cung cấp đi trước, repo sử dụng đi sau (xem skill `cross-repo-change`).
2. Giao các bước không phụ thuộc bước nào trước. Không chạy quá 3 agent ghi code cùng lúc, vì người dùng phải review kịp. Với mỗi bước, chạy:
   ```sh
   python3 ~/.claude/skills/herdr-dispatch/dispatch.py <đường dẫn repo> "<tên>" "<câu giao việc>" [--worktree <branch>] [--place auto|tab|right|down]
   ```
   - Tên: ngắn, ví dụ `user-svc`, hoặc `step-2` khi dùng worktree.
   - `--worktree <branch>`: script tạo worktree cho branch đó (hoặc dùng lại worktree đã có), bắt đầu từ HEAD của repo, đổi bằng `--base <ref>`. Đặt tên branch theo task, ví dụ `<slug>/step-2`. Thư mục worktree lấy từ `worktrees.directory` trong `~/.config/herdr-app/settings.json`, mặc định `~/.herdr/worktrees`.
   - Không có `--worktree`, agent được đọc thư mục cha của repo (các repo khác). Có `--worktree`, agent chỉ được đọc repo chính.
   - Mặc định `--place auto`: tối đa 3 agent mở thành cột dọc cạnh bạn (cuối cùng là 4 cột bằng nhau), từ agent thứ 4 mở tab mới. Người dùng muốn thấy bạn và agent con cùng lúc, nhưng pane quá nhỏ thì không đọc được. Người dùng nói "mở tab" thì dùng `--place tab`.
   - Câu giao việc: một hai câu, gồm đường dẫn tuyệt đối tới TASK.md, số bước, và branch chưa merge của phần khác nếu bước này cần.
   - Script in ra `terminal`. Ghi lại để gửi tin sau.
3. Worktree mới: lần đầu Claude chạy ở đó, nó hỏi có tin thư mục này không. Agent hiện "Blocked" cho tới khi người dùng duyệt. Báo người dùng bấm vào agent đó để duyệt. Bạn không tự trả lời câu hỏi này.
4. Ghi vào TASK.md: bước nào giao cho terminal nào, branch nào, lúc nào.
5. Chờ báo cáo bằng `hc wait --children any`. Không dùng `sleep`. Agent báo về bằng `hc send`, tin nhắn hiện trong ô nhập của bạn.
6. Agent báo về bằng một trong bốn trạng thái của developer (`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_REPLAN`, `BLOCKED`) và xử lý theo bước 4 của `/work`. `NEEDS_REPLAN` thì dừng các bước phụ thuộc, sửa Kế hoạch, và hỏi người dùng nếu đổi tiêu chí, hợp đồng hoặc file thân. Khi agent báo xong, đừng tin ngay tin nhắn. Kiểm tra: commit có thật và mới hơn lúc giao việc (`git -C <thư mục của agent> log -1 --format='%h %ci'`), đúng branch. Rồi tự ghi một dòng vào TASK.md: branch, commit, kết quả test, còn thiếu gì. Rồi giao các bước đang chờ bước đó.
7. Khi agent báo kẹt: trả lời bằng `hc send <terminal> "..."` nếu bạn tự quyết được trong phạm vi kế hoạch. Ngoài phạm vi thì hỏi người dùng.
8. Hết bước:
   - Nhiều repo: tóm tắt trong TASK.md branch và commit của từng repo.
   - Worktree: gộp các branch vào branch của task theo thứ tự trong kế hoạch (`git merge --no-ff <branch>` trong repo chính). Có xung đột thì dừng và hỏi người dùng. Gộp xong mới dọn: hỏi người dùng rồi `git worktree remove <thư mục>` và `git branch -d <branch>`. Không dọn worktree của branch chưa gộp.
   - Rồi đi tiếp `/work` (kiểm tra, review). Push và PR theo ~/.claude/rules/preferences.md.

## Lệnh hay dùng
- `hc ls`: các agent đang chạy.
- `hc read <terminal> --lines 80`: xem màn hình của một agent.
- `hc send <terminal> "..."`: gửi việc tiếp hoặc trả lời.
- `hc interrupt <terminal>`: dừng lượt hiện tại của agent.
- `dispatch.py <repo> review-<slug> "<TASK.md>, branch <b>, commit gốc <sha>" --template reviewer`: một phiên review chỉ đọc. Phiên đó giao cho agent `reviewer` (và `security-reviewer` khi task high-risk), nên luật review chỉ có một nguồn là `~/.claude/agents/`.
- `git -C <repo> worktree list`: các worktree đang có.

Agent trong tab do người dùng đóng thì coi như bước đó dừng. Ghi vào TASK.md và hỏi người dùng.
