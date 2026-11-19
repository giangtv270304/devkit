---
name: work
description: Điều phối một task từ đầu đến cuối trong một file duy nhất TASK.md (mục tiêu -> kế hoạch -> code -> kiểm tra -> review -> bàn giao). Skill chọn đường đi theo loại task và giao việc cho các agent architect, tester, developer, reviewer và security-reviewer. Quản lý vòng đời của MỘT task. Dùng khi người dùng chạy /work, bắt đầu hoặc tiếp tục một task, xem các task đang làm, hoặc muốn biến một ý tưởng thành thay đổi code. Nhiều yêu cầu liên tiếp trong một phiên thì do /lead lo; giao việc cho agent trong Herdr thì gọi herdr-dispatch.
---

# /work: điều phối task

Bạn chạy trong session chính, từ thư mục gốc của dự án. Bạn điều phối các agent. Agent không gọi được nhau, chỉ bạn giao việc cho chúng.

Kiểm tra `echo $HC_TERMINAL_ID` trước khi giao việc đầu tiên:
- Có giá trị (session chạy trong Herdr): mỗi bước ghi code mở thành một pane bằng skill `herdr-dispatch` với `--template worker`, kể cả khi chỉ có một bước. Worker tự viết test trước, nên tester và developer của cùng một bước gộp vào một pane. Review cũng mở thành một pane `--template reviewer` (mục 6). Subagent (Agent tool) chỉ dùng cho architect và tìm kiếm, vì bạn cần kết quả của chúng ngay để viết Kế hoạch. Lý do: người dùng cần thấy agent đang làm và chen vào được, còn subagent chạy nền thì không, và bạn bị khóa trong lúc chờ nó. Hook `herdr_agent_gate` chặn subagent tester, developer, reviewer và security-reviewer trong Herdr.
- Trống (Claude desktop, terminal thường): dùng subagent tester và developer như mô tả bên dưới.

## Cấu hình của dự án
Trước tiên đọc `.claude/project.md` ở gốc dự án, nếu có. File đó cho biết: dự án là một repo hay một thư mục chứa nhiều repo, thư mục task, thư mục ADR và note, tài liệu kiến trúc và hợp đồng, lệnh kiểm tra, skill quy ước cho từng ngôn ngữ, và danh sách thân riêng. Mẫu: `templates/project.md` trong repo devkit (`~/.claude/devkit/templates/project.md`).

Không có file đó thì dùng mặc định: thư mục task là `work/` nếu đã có, không thì `.claude/work/`; lệnh kiểm tra lấy từ CLAUDE.md của repo. Không tự tạo project.md khi chưa hỏi.

Bên dưới, `<task>` nghĩa là `<thư mục task>/<slug>`.

## Một task = một file
Mỗi task có đúng một file: `<task>/TASK.md`, chép từ `${CLAUDE_SKILL_DIR}/task-template.md`. Không tạo thêm file kế hoạch hay file ghi chú nào khác. Chỉ thêm `<task>/proof/` khi có ảnh chụp.

`<task>/log.md` do hook ghi tự động: mỗi lần một session hoặc agent dừng là một dòng. Bạn không sửa file đó. Đọc 20 dòng cuối khi tiếp tục một task, để biết session khác đã làm gì.

Người dùng không muốn đọc nhiều: **Tóm tắt** ở đầu file (tối đa 4 dòng, có dòng `CẦN BẠN:`) luôn đúng với trạng thái hiện tại; viết ngắn, không chép lại; Mục tiêu tối đa ~25 dòng, Kế hoạch một màn hình. Cập nhật TASK.md ở mọi ĐIỂM DỪNG và trước khi kết thúc mỗi lượt có việc mới. Viết bằng tiếng Việt theo ~/.claude/rules/writing-vi.md. Quy tắc chi tiết của `Phase:`, `Cập nhật:`, `Branch:`: `reference/task-file.md`.

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

Mục tiêu còn mơ hồ (chưa biết làm gì, có nhiều hướng): đề xuất skill `brainstorm` trước, rồi quay lại đây với bản quyết định. Đã rõ mục tiêu nhưng có lựa chọn kiến trúc lớn (service mới, tích hợp mới, đổi luồng giữa các service): đề xuất `/design` trước, rồi quay lại với ADR.

Task đụng schema hoặc migration, hạ tầng hoặc deploy, hay giao diện thì ghi vào `Loại:` thêm `data`, `ops` hoặc `ui`. Architect và developer áp dụng skill `data-design`, `ops-change` hoặc `frontend-change` tương ứng. Thay đổi `data` và `ops` luôn có file thân.

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

Feature, cross-repo, high-risk, spike: giao cho `architect` kèm đường dẫn TASK.md; bug: tự viết kế hoạch từ "Nguyên nhân bug". Mỗi bước ghi repo, kết quả, tiêu chí, agent, file thân/lá. Chỉ ghi đường dẫn đã mở và đọc. Luôn có dòng "Cách tắt khi có lỗi". High-risk: thêm đoạn code đề xuất cho file thân. High-risk và cross-repo: giao `reviewer` rà kế hoạch trước khi dừng. Chi tiết: `reference/planning.md`.

**ĐIỂM DỪNG 1**: Phase `plan`. Tóm tắt ghi `CẦN BẠN: đọc Mục tiêu và Kế hoạch; sửa bằng > NOTE: hoặc nói đồng ý`. Đưa link TASK.md. Hỏi luôn agent có được commit trên máy hay không. Mặc định là không commit.

Chuyển sang Herdr: session chạy ngoài Herdr (`HC_TERMINAL_ID` trống) và người dùng đã đồng ý, thì đề nghị chạy phần code trong Herdr để họ thấy các agent. Họ đồng ý thì:
1. Ghi vào "Quyết định và bằng chứng" mọi quyết định đã chốt trong cuộc trò chuyện mà TASK.md chưa có (lựa chọn lúc brainstorm, có commit hay không). Lead trong Herdr chỉ đọc TASK.md, không thấy cuộc trò chuyện này.
2. Đặt Phase là `code`, rồi chạy `herdr-task <slug> --root <gốc dự án>`. Lệnh mở một space trong Herdr với lead chạy `/work <slug>`.
3. Từ đó chỉ lead ghi TASK.md. Session này dừng ghi, chỉ đọc TASK.md để trả lời người dùng. Hai nơi cùng ghi thì đè nhau.

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

Chỉ chạy song song các bước khi Kế hoạch nói chúng độc lập và mỗi bước có thư mục riêng: repo khác nhau, hoặc git worktree riêng của cùng một repo. Không bao giờ để hai agent ghi vào cùng một thư mục cùng lúc, vì chúng ghi đè file và đổi branch của nhau. Trong Herdr, mỗi bước song song là một pane worker riêng (xem đầu file); ngoài Herdr thì dùng subagent như trên.

## 5. Kiểm tra

Bạn tự kiểm tra, không tin báo cáo của agent: chạy bộ kiểm tra của mỗi repo đã sửa, mỗi lời khẳng định cần đúng một loại bằng chứng vừa chạy xong, rồi lấy bằng chứng chạy thật (API, giao diện, biến bật/tắt). Không chạy được thì ghi rõ, không bịa. Ghi mỗi kết quả một dòng vào "Quyết định và bằng chứng"; có gì fail thì gửi lại developer kèm output lỗi. Bảng bằng chứng và chi tiết: `reference/verification.md`.

## 6. Review
Giao cho `reviewer`: đường dẫn TASK.md, các repo, branch và commit gốc. Với task high-risk, giao thêm cho `security-reviewer` cùng lúc. Không đưa cho reviewer báo cáo của developer hay tóm tắt của bạn.

Trong Herdr: mỗi repo một pane review, `dispatch.py <repo> review-<slug> "<TASK.md>, branch <b>, commit gốc <sha>" --template reviewer`. Pane đó tự giao cho `reviewer` và `security-reviewer`, rồi báo về bằng `hc send`. Bạn chờ bằng `hc wait --children any` chạy nền, nên vẫn nhận tin của người dùng trong lúc chờ.

Trước khi chấp nhận một vấn đề blocker hoặc major, tự mở đúng `file:dòng` và kiểm tra nó có thật. Bỏ vấn đề không đúng với code, và ghi một dòng lý do bỏ.

Ghi vào mục "Review": chỉ blocker và major ở bảng, minor gom thành một dòng. Lỗi blocker và major quay lại developer, rồi review lại. Tối đa 2 vòng sửa. Sau đó dừng và cho người dùng thấy những gì còn lại.

**ĐIỂM DỪNG 2**: Phase `review`. Tóm tắt ghi `CẦN BẠN: đọc diff các file thân <danh sách>; đồng ý để bàn giao`. Đưa cho người dùng lệnh xem diff thật của từng file thân (`git -C <repo> diff <branch gốc>...<branch> -- <file>`), không chép diff vào TASK.md.

## 7. Bàn giao
Tóm tắt theo từng repo trong chat: branch, commit (nếu được phép), kết quả kiểm tra, các mục review còn mở.

Commit theo ~/.claude/rules/commits.md, mô tả PR theo ~/.claude/rules/pull-requests.md, push và PR theo ~/.claude/rules/preferences.md. Thêm: không chạy migration trên database dùng chung, không deploy, nếu người dùng chưa đồng ý rõ ràng trong session này.

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
