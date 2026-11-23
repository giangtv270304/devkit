---
name: code-graph
description: Dựng graph quan hệ code (ai gọi ai, ai import ai, các cụm subsystem) của một repo bằng graphify CLI ghim bản, chạy trên máy, rồi hỏi graph thay vì grep cả repo. Dùng khi lập Kế hoạch cho feature, cross-repo hoặc high-risk trong một repo lạ hoặc lớn, khi người dùng hỏi "cái này gọi tới đâu", "đổi X ảnh hưởng gì", "đường đi từ A tới B", hoặc khi visual-plan cần sơ đồ thành phần đúng với code.
---

# code-graph: hỏi graph trước khi grep

Graph cho biết nhanh một hàm có những ai gọi và một thay đổi lan tới đâu. Nó chỉ là gợi ý: trước khi ghi một đường dẫn vào Kế hoạch, mở file đó ra đọc, như `work/reference/planning.md` yêu cầu.

## Khi nào dựng
- Dựng: repo có từ khoảng 50 file code, task là feature, cross-repo hoặc high-risk, hoặc người dùng hỏi về đường đi và phạm vi ảnh hưởng.
- Không dựng: repo nhỏ đọc hết được, bug đã biết nguyên nhân, đổi config.
- Máy không có `uvx`: nói một dòng rằng bỏ qua bước này, rồi grep như thường.

## 1. Dựng graph
Output để ngoài repo, tại `~/.cache/jigkit-graphs/<tên repo>`, để không có file lạ trong git. Mặc định chỉ đọc code, vì đường này chạy hoàn toàn trên máy:

```bash
GRAPHIFY_BACKEND=none GRAPHIFY_OUT="$HOME/.cache/jigkit-graphs/<repo>" uvx --from 'graphifyy[mcp]==0.9.118' graphify extract <đường dẫn repo> --code-only
```

```bash
GRAPHIFY_BACKEND=none GRAPHIFY_OUT="$HOME/.cache/jigkit-graphs/<repo>" uvx --from 'graphifyy[mcp]==0.9.118' graphify cluster-only <đường dẫn repo>
```

Bước hai ghi `GRAPH_REPORT.md` (các thành phần nhiều liên kết nhất, các cụm) và `graph.html`. Chạy lại bước một khi `Built from commit` trong report khác `git rev-parse HEAD`; file không đổi được lấy từ cache.

Xong khi: report có dòng `Graph: N nodes` và commit khớp HEAD.

## 2. Hỏi graph
Cùng hai biến môi trường như trên:
- `graphify explain "<tên>"`: các liên kết của một file, hàm hay type, kèm dòng code.
- `graphify path "<A>" "<B>"`: đường ngắn nhất, ví dụ từ handler tới bảng.
- `graphify query "<câu hỏi>"`: hỏi tự do.

Exit code 3 là tên mơ hồ: chọn một tên trong danh sách nó trả về rồi hỏi lại. Exit code 4 là không có node đó: kiểm tra lại tên bằng grep.

## 3. Dùng kết quả
- Lập Kế hoạch: với mỗi file thân, chạy `explain` để thấy ai gọi nó, rồi mở các file đó trước khi ghi vào bước. Đưa cho architect đường dẫn `GRAPH_REPORT.md` và đoạn kết quả `explain`/`path` cần thiết, vì architect không chạy được lệnh.
- `visual-plan`: sơ đồ Tổng quan lấy các cạnh từ `explain`, không vẽ theo trí nhớ.
- Chỉ chép vào TASK.md vài dòng kết quả cần thiết, không chép cả report.

## Repo nhiều markdown (graph nghèo)
`--code-only` bỏ qua docs, nên một repo chủ yếu là markdown (skill, tài liệu) cho ra graph thưa. Đọc được markdown thì phải có lượt LLM, và nội dung file sẽ rời máy. Chỉ làm khi repo là public hoặc người dùng đồng ý trong phiên này, rồi dùng gói Claude của chính người dùng:

```bash
OBSIDIAN_DAILY=off DEVKIT_VERIFY=0 GRAPHIFY_CLAUDE_CLI_MODEL=sonnet GRAPHIFY_OUT="$HOME/.cache/jigkit-graphs/<repo>" uvx --from 'graphifyy[mcp]==0.9.118' graphify extract <đường dẫn repo> --backend claude-cli
```

Backend này gọi `claude -p` cho từng nhóm file. Mỗi lần gọi chạy cả hook của người dùng, nên `OBSIDIAN_DAILY=off` để prompt của graphify không bị ghi vào note Obsidian, và `DEVKIT_VERIFY=0` để hook kiểm tra không chạy build ở mỗi lần dừng. Tốn lượt dùng của gói: nói trước số file docs mà lệnh `--code-only` đã báo bị bỏ qua.

## Không làm
- Không chạy `graphify install`, `graphify claude install` hay `graphify hook install`: chúng ghi hook PreToolUse chạy trước mọi lần đọc file và ghi vào `CLAUDE.md`, chồng lên hook của jigkit và để lại file AI trong repo.
- Không dùng Graphify Cloud, không dùng `graphify add <url>`, và không dùng backend nào khác với repo công ty. Không đặt `GRAPHIFY_BACKEND` thì nó tự chọn nhà cung cấp theo API key có trong môi trường, có khi là server ở Trung Quốc.
- Nâng bản `0.9.118`: soát lại theo skill `vet-third-party` trước, vì gói phát hành gần như mỗi ngày.
