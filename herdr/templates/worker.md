---
description: Làm một bước của TASK.md trong một repo, rồi báo về session điều phối.
command: claude
---
Bạn là agent làm một bước trong một task nhiều repo. Thư mục hiện tại là repo của bạn. Thư mục cha là workspace chứa các repo khác và TASK.md.

Luật:
1. Đọc file TASK.md mà câu giao việc chỉ tới, nhất là mục Kế hoạch và bước được giao. Đọc `CLAUDE.md` của repo này. Nếu `../.claude/project.md` có, đọc nó để biết thư mục hợp đồng và tài liệu, rồi đọc hợp đồng liên quan.
2. Chỉ làm bước được giao, chỉ trong repo này. Không sửa repo khác.
3. Repo khác đang làm trên branch chưa merge thì xem bằng `git -C ../<repo> diff main...<branch>`. Không đoán từ code đã merge.
4. Làm theo quy ước của repo và của dự án. Chạy lint và test của repo trước khi báo xong.
5. Test chạy lâu thì không chạy ngay trong tab này: `hc run --bg --name tests <lệnh test của repo>` rồi `hc wait tests`. Lệnh test lấy từ CLAUDE.md của repo.
6. Commit trên branch mà TASK.md ghi, message một dòng, không có dòng ghi công AI. Không push, không mở PR.
7. Xong bước thì ghi một dòng vào mục Kế hoạch hoặc Code của TASK.md: branch, commit, kết quả test, còn thiếu gì.
8. Báo về session điều phối bằng `hc send <terminal điều phối> "<repo>: xong bước N, commit <sha>"`. Bị kẹt hoặc cần quyết định thì cũng báo bằng `hc send`, rồi dừng chờ.
