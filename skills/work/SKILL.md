---
name: work
description: Điều phối một task từ đầu đến cuối trong một file duy nhất TASK.md (mục tiêu -> kế hoạch -> code -> kiểm tra -> review -> bàn giao). Skill chọn đường đi theo loại task và giao việc cho các agent architect, tester, developer, reviewer và security-reviewer. Dùng khi người dùng chạy /work, bắt đầu hoặc tiếp tục một task, xem các task đang làm, hoặc muốn biến một ý tưởng thành thay đổi code.
---

# /work: điều phối task

Bạn chạy trong session chính, từ thư mục gốc của dự án. Bạn điều phối các subagent (agent con). Subagent không gọi được nhau, chỉ bạn giao việc cho chúng.

## Cấu hình của dự án
Trước tiên đọc `.claude/project.md` ở gốc dự án, nếu có. File đó cho biết: dự án là một repo hay một thư mục chứa nhiều repo, thư mục task, thư mục ADR và note, tài liệu kiến trúc và hợp đồng, lệnh kiểm tra, skill quy ước cho từng ngôn ngữ, và danh sách thân riêng. Mẫu: `templates/project.md` trong repo devkit (`~/.claude/devkit/templates/project.md`).

Không có file đó thì dùng mặc định: thư mục task là `work/` nếu đã có, không thì `.claude/work/`; lệnh kiểm tra lấy từ CLAUDE.md của repo. Không tự tạo project.md khi chưa hỏi.

Bên dưới, `<task>` nghĩa là `<thư mục task>/<slug>`.

## Một task = một file
Mỗi task có đúng một file: `<task>/TASK.md`, chép từ `${CLAUDE_SKILL_DIR}/task-template.md`. Không tạo thêm file kế hoạch hay file ghi chú nào khác. Chỉ thêm `<task>/proof/` khi có ảnh chụp.

`<task>/log.md` do hook ghi tự động: mỗi lần một session hoặc agent dừng là một dòng. Bạn không sửa file đó. Đọc 20 dòng cuối khi tiếp tục một task, để biết session khác đã làm gì.

Người dùng không muốn đọc nhiều. Vì vậy:
- **Tóm tắt** ở đầu file luôn đúng với trạng thái hiện tại. Tối đa 4 dòng. Dòng `CẦN BẠN:` nói đúng việc người dùng phải làm, hoặc `không`.
- Viết ngắn. Không chép lại điều đã có ở mục khác. Không chép code vào file, trừ đoạn ngắn cho file thân của task high-risk.
- Mục "Mục tiêu và phạm vi" tối đa khoảng 25 dòng. Mục "Kế hoạch" tối đa một màn hình. Nếu dài hơn, task quá to: đề xuất tách thành nhiều task.
- File thay cho bàn giao giữa các session. Session sau chỉ biết những gì ghi trong file này.

Cập nhật TASK.md ở mọi ĐIỂM DỪNG, khi xong mỗi mục trong Kế hoạch, và trước khi kết thúc mỗi lượt trả lời có việc mới: Tóm tắt, `Phase:`, `Cập nhật:`, checklist, quyết định mới.
- `Phase:` chỉ chứa đúng một giá trị: `intent`, `plan`, `build`, `verify`, `review`, `ship`, `done`.
- `Cập nhật:` dạng `YYYY-MM-DD`.
- `Branch:` mỗi dòng `- <repo>: <branch>`. Dự án một repo thì ghi tên thư mục gốc.

Viết file bằng tiếng Việt, theo ~/.claude/rules/writing-vi.md. Giữ nguyên chính xác code, đường dẫn, lệnh và tên test.

## Ghi chú của người dùng (NOTE)
Người dùng sửa task bằng cách viết ghi chú ngay trong TASK.md, ở dòng bắt đầu bằng `> NOTE:`. Họ không cần trả lời từng câu trong chat.
- Mỗi lần bắt đầu lượt mới với một task, tìm `> NOTE:` trong TASK.md.
- Sửa nội dung theo từng ghi chú, rồi xóa ghi chú đó. Ghi các quyết định quan trọng vào mục "Quyết định và bằng chứng".
- Khi đang ở điểm dừng, sửa xong ghi chú thì dừng lại. Không code tiếp cho tới khi người dùng nói đồng ý.

## 0. Bắt đầu hoặc tiếp tục
- Không có tham số: chạy `python3 ${CLAUDE_SKILL_DIR}/status.py` và đưa bảng cho người dùng. Hỏi họ muốn tiếp tục task nào. Không đọc thêm file nào trước khi họ chọn.
- Tham số là một slug (`/work card-freeze-reason`) hoặc một câu mô tả tự do. Nếu cần, tự đặt một slug ngắn dạng kebab-case (chữ thường, nối bằng dấu gạch ngang).
- Nếu `<task>/TASK.md` đã có: đọc nó, đọc cuối `log.md`, xử lý NOTE, nói task đang ở đâu, và làm tiếp.
- Task mới: tạo `<task>/TASK.md` từ mẫu. Điền những gì bạn biết từ lời người dùng.

## 1. Phân loại và chọn đường đi
Xem nhanh các repo được nhắc tới (CLAUDE.md của repo, tài liệu kiến trúc). Chọn một loại và ghi vào `Loại:`.

| Loại | Dấu hiệu | Đường đi |
|---|---|---|
| small | mô tả được trong một câu, một repo, không đổi hợp đồng | Không tạo TASK.md. Bạn tự làm rồi kiểm tra, không dùng subagent |
| bug | có thứ đang hỏng | hỏi ngắn -> tìm nguyên nhân (mục 2b) -> kế hoạch -> ĐIỂM DỪNG 1 -> tester tái hiện lỗi -> developer -> kiểm tra -> review -> ĐIỂM DỪNG 2 |
| feature | hành vi mới trong một repo, hợp đồng giữ nguyên hoặc chỉ thêm | hỏi ngắn -> architect lập kế hoạch -> ĐIỂM DỪNG 1 -> tester -> developer -> kiểm tra -> review -> ĐIỂM DỪNG 2 |
| cross-repo | nhiều hơn một repo, hoặc đổi bất kỳ hợp đồng nào (API, event, khóa cache, schema database) | như feature + skill cross-repo-change + ADR nếu có lựa chọn thiết kế; làm repo cung cấp trước repo sử dụng |
| spike | câu hỏi hoặc so sánh phương án, không cần code | skill `research` hoặc architect so sánh phương án -> ghi câu trả lời vào TASK.md hoặc ADR. Không code |
| high-risk | đụng tới dòng tiền, xác thực, dữ liệu cá nhân, ký webhook (chi tiết trong ~/.claude/rules/review-levels.md) | đường đi gốc + đoạn code ngắn cho file thân trong Kế hoạch + bắt buộc security-reviewer |

Một task có thể vừa là cross-repo vừa là high-risk. Khi đó áp dụng cả hai. Nói loại và đường đi cho người dùng trong một dòng. Không dừng để hỏi xác nhận loại: người dùng sửa bằng NOTE ở điểm dừng 1 nếu cần.

Mục tiêu còn mơ hồ (chưa biết làm gì, có nhiều hướng): đề xuất skill `brainstorm` trước, rồi quay lại đây với bản quyết định.

## 2. Hỏi ngắn (không áp dụng cho small)
Chỉ hỏi về phần khó: hành vi chưa rõ, trường hợp biên, cách xử lý lỗi, tương thích ngược, những gì nằm ngoài phạm vi. Chỉ hỏi khi câu trả lời làm đổi thứ sẽ làm. Mỗi câu kèm câu trả lời bạn đề xuất. Một vòng AskUserQuestion, tối đa 4 câu. Không hỏi những gì bạn tìm được trong code. Nếu không có gì khó, bỏ qua bước này.

Ghi kết quả vào "Mục tiêu và phạm vi", gồm dòng "Không được đổi". Mỗi tiêu chí thành một test có tên.

## 2b. Tìm nguyên nhân (chỉ cho bug)
Tìm gốc lỗi trước khi viết test. Nếu chưa biết gốc lỗi, test chỉ bắt được triệu chứng. Giống như bác sĩ cho thuốc hạ sốt khi chưa biết vì sao sốt.

1. Viết ra triệu chứng: input nào, kết quả mong đợi, kết quả thật.
2. Đưa ra 1-3 giả thuyết. Mỗi giả thuyết chỉ tới một chỗ cụ thể (`repo/file:dòng`).
3. Kiểm tra từng giả thuyết bằng bằng chứng: đọc code, `git log -S`/`git blame`, log hay dữ liệu nếu có. Mỗi lần chỉ thử một giả thuyết, bằng thay đổi nhỏ nhất. Loại giả thuyết không khớp. Không đoán.
4. Ghi vào mục "Nguyên nhân bug": gốc lỗi, bằng chứng, giả thuyết đã loại và vì sao, chỗ khác có cùng kiểu lỗi.
5. Nếu vẫn còn hơn một giả thuyết, hỏi người dùng thêm dữ liệu.

Đưa mục "Nguyên nhân bug" cho tester. Test tái hiện phải fail vì đúng gốc lỗi đó.

## 3. Kế hoạch
- feature, cross-repo, high-risk, spike: giao cho `architect`, kèm đường dẫn TASK.md. Bug: bạn tự viết kế hoạch từ mục "Nguyên nhân bug".
- Ghi kế hoạch thành checklist trong mục "Kế hoạch". Mỗi bước: repo, kết quả cần đạt, số tiêu chí mà bước đó làm xong, agent, các file kèm thân/lá (file thân trước).
- Kế hoạch chi tiết mà sai còn tệ hơn kế hoạch ngắn. Chỉ ghi đường dẫn file đã được mở và đọc. Không đoán tên file, tên hàm.
- Bước có bên khác dùng (repo khác, client): thêm một dòng hợp đồng, nhận gì và trả gì.
- Luôn có dòng "Cách tắt khi có lỗi". Chỉ có ba cách: biến môi trường bật/tắt, route mới chưa nối vào luồng cũ, hoặc deploy lại bản cũ. Với dòng tiền và xác thực, ưu tiên biến bật/tắt, mặc định tắt. Tên biến phải có trong `.env.example` và có test cho cả hai trạng thái.
- High-risk: dưới mỗi bước, thêm đoạn code đề xuất ngắn (tối đa ~20 dòng, dạng `diff`) cho từng file thân. Kiểm tra mọi đoạn "code hiện tại" với file thật. Không đưa code cho file lá.
- Branch mỗi repo: `feat/<slug>` (bug: `fix/<slug>`). Ghi vào `Branch:`.
- Nếu architect đề xuất ADR, viết bản nháp trong thư mục ADR của dự án.

Rà kế hoạch trước khi dừng:
- Mọi task: tự kiểm tra mỗi tiêu chí có bước làm xong nó, và không còn chỗ "sẽ quyết sau".
- High-risk và cross-repo: giao cho `reviewer` rà kế hoạch (phần "Khi được giao rà kế hoạch"). Chỉ đưa đường dẫn TASK.md, không đưa lý do của bạn. Sửa kế hoạch theo kết quả.

**ĐIỂM DỪNG 1**: Phase `plan`. Tóm tắt ghi `CẦN BẠN: đọc Mục tiêu và Kế hoạch; sửa bằng > NOTE: hoặc nói đồng ý`. Đưa link TASK.md. Hỏi luôn agent có được commit trên máy hay không. Mặc định là không commit.

## 4. Code
Làm từng mục trong Kế hoạch, theo thứ tự:
1. Trong repo của bước đó, chạy `git status`. Nếu có thay đổi chưa commit không thuộc task này, dừng lại và hỏi. Tạo hoặc chuyển sang branch của task. Ghi commit gốc (`git rev-parse --short HEAD`) vào "Quyết định và bằng chứng": diff để review lấy từ commit này.
2. `tester` viết các test bị fail cho tiêu chí của bước đó (bug: test tái hiện lỗi trước).
3. `developer` code cho tới khi các test đó và bộ kiểm tra của repo đều qua.
4. Đọc dòng trạng thái đầu báo cáo của developer:
   - `DONE`: đánh dấu `[x]`.
   - `DONE_WITH_CONCERNS`: đánh dấu `[x]`, ghi `file:dòng` còn lo vào "Quyết định và bằng chứng".
   - `NEEDS_REPLAN`: dừng. Ghi một dòng vào "Lệch kế hoạch", cập nhật Kế hoạch, và hỏi người dùng nếu phải đổi tiêu chí, đổi hợp đồng hoặc thêm file thân.
   - `BLOCKED`: giải quyết thứ đang thiếu, hoặc hỏi người dùng.

Đưa cho tester và developer: đường dẫn TASK.md và số thứ tự bước. Không đưa thêm ý kiến của bạn.

Hook chặn sửa ngoài kế hoạch: khi developer hoặc tester sắp sửa một file không có trong mục Kế hoạch, Claude Code hỏi người dùng. Nếu người dùng từ chối, coi như `NEEDS_REPLAN`.

Chỉ chạy song song các bước ở những repo khác nhau, và chỉ khi Kế hoạch nói chúng độc lập. Không bao giờ chạy hai developer trong cùng một repo cùng lúc.

## 5. Kiểm tra
Bạn tự kiểm tra, không tin báo cáo của agent. Chạy bộ kiểm tra của mỗi repo đã sửa: các lệnh trong mục "Checks" của project.md, hoặc trong CLAUDE.md của repo. Nếu API thay đổi, chạy lại lệnh sinh spec của repo.

Mỗi lời khẳng định cần đúng một loại bằng chứng, vừa chạy xong:

| Lời khẳng định | Bằng chứng bắt buộc |
|---|---|
| test qua | output và mã thoát của lệnh test, chạy sau lần sửa cuối |
| lint sạch | output của lệnh lint |
| agent đã làm xong | `git diff` của repo, không phải lời của agent |
| bug đã sửa | triệu chứng ban đầu được thử lại và không còn |
| tiêu chí N đạt | test tên X qua, hoặc request và response thật |

Sau đó lấy bằng chứng chạy thật:
- API hoặc handler: chạy service trên máy, gọi endpoint cho trường hợp đúng và ít nhất một trường hợp lỗi. Ghi request, status, response rút gọn. Xóa token, API key và dữ liệu cá nhân.
- Giao diện: mở trang bằng browser, chụp màn hình, lưu vào `<task>/proof/`.
- Có biến bật/tắt: kiểm tra cả lúc bật và lúc tắt.
- Không chạy được trên máy: ghi rõ là chưa chạy thật và vì sao. Không bịa bằng chứng.

Ghi mỗi kết quả một dòng vào "Quyết định và bằng chứng". Nếu có gì fail, gửi lại cho developer kèm output lỗi.

## 6. Review
Giao cho `reviewer`: đường dẫn TASK.md, các repo, branch và commit gốc. Với task high-risk, giao thêm cho `security-reviewer` cùng lúc. Không đưa cho reviewer báo cáo của developer hay tóm tắt của bạn.

Trước khi chấp nhận một vấn đề blocker hoặc major, tự mở đúng `file:dòng` và kiểm tra nó có thật. Bỏ vấn đề không đúng với code, và ghi một dòng lý do bỏ.

Ghi vào mục "Review": chỉ blocker và major ở bảng, minor gom thành một dòng. Lỗi blocker và major quay lại developer, rồi review lại. Tối đa 2 vòng sửa. Sau đó dừng và cho người dùng thấy những gì còn lại.

**ĐIỂM DỪNG 2**: Phase `review`. Tóm tắt ghi `CẦN BẠN: đọc diff các file thân <danh sách>; đồng ý để bàn giao`. Đưa cho người dùng lệnh xem diff thật của từng file thân (`git -C <repo> diff <branch gốc>...<branch> -- <file>`), không chép diff vào TASK.md.

## 7. Bàn giao
Tóm tắt theo từng repo trong chat: branch, commit (nếu được phép), kết quả kiểm tra, các mục review còn mở.

Commit message theo ~/.claude/rules/commits.md.

Không bao giờ push, mở PR, chạy migration trên database dùng chung, hay deploy, nếu người dùng chưa đồng ý rõ ràng trong session này. Khi được nhờ mở PR, viết mô tả PR theo ~/.claude/rules/pull-requests.md: ngắn, không chép lại TASK.md.

## 8. Rút kinh nghiệm
Đề xuất trong một dòng, làm khi người dùng đồng ý:
- thêm một dòng vào CLAUDE.md của repo cho lỗi đã xảy ra hai lần, hoặc cho sự thật khó đoán vừa phát hiện,
- cập nhật tài liệu hợp đồng, tài liệu kiến trúc, tài liệu công khai và quy ước (đường dẫn trong project.md),
- viết một note cho luồng khó đã phải lần theo, và chạy `python3 ~/.claude/skills/refresh-context/context_state.py record <repo>` cho repo có CLAUDE.md vừa cập nhật,
- đánh dấu ADR là đã chấp nhận.

Đặt Phase thành `done`.

## Quy tắc về chi phí và phạm vi
- Task small: không dùng subagent, không tạo TASK.md trừ khi người dùng yêu cầu.
- Không giao việc cho agent nếu đọc hai file là trả lời được.
- Không bao giờ mở rộng phạm vi ra ngoài "Mục tiêu và phạm vi". Ý tưởng mới ghi một dòng vào "Quyết định và bằng chứng" với chữ "Để sau:", để người dùng quyết định.
