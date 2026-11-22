---
name: resolve-conflicts
description: Gộp branch mặc định vào branch đang làm và gỡ xung đột (conflict) theo ý định của cả hai bên, có người dùng duyệt cách gỡ trước khi sửa. Dùng khi người dùng nói "resolve conflict", "gộp main vào", "rebase", "PR bị conflict", khi `git merge` hoặc `git rebase` dừng vì xung đột, hoặc khi gộp các branch worktree của herdr-dispatch bị xung đột.
argument-hint: "[branch nguồn, mặc định là branch mặc định của repo]"
---

# resolve-conflicts: hiểu cả hai bên rồi mới gỡ

Một xung đột là hai thay đổi có lý do riêng. Gỡ đúng là giữ được ý định của cả hai, không phải chọn bên nào ít dòng hơn.

Adapted from humanlayer/humanlayer `merge-resolve-conflicts` (Apache-2.0).

## 1. Định hướng
- `git status`: đang có merge hoặc rebase dở thì sang bước 3. Có thay đổi chưa commit không thuộc xung đột thì dừng và hỏi; không stash hộ.
- `git fetch origin`. Branch mặc định: `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. Repo có cả `upstream` (bản fork) thì lấy branch mặc định từ `upstream`.
- Đang ở branch mặc định: không gộp gì, báo người dùng.
- Merge hay rebase: theo `.claude/project.md` hoặc cách repo đang làm (`git log --merges -5`). Branch đã push và có người khác dùng thì merge, vì rebase phải force push (bash-guard chặn, và cần người dùng đồng ý).

## 2. Gộp
`git merge origin/<mặc định>` (hoặc `git rebase origin/<mặc định>`). Không xung đột thì sang bước 5.

## 3. Hiểu từng xung đột
Danh sách file: `git diff --name-only --diff-filter=U`. Với mỗi file:
- Đọc cả file, không chỉ đoạn có dấu `<<<<<<<`.
- Ý định của mỗi bên: `git log --oneline --merge -- <file>`, rồi `git show <sha>` cho commit liên quan. Bên mình đọc thêm TASK.md nếu có.
- Gom xung đột cùng một lý do (hàm đổi và import của nó) thành một mục.

Xong bước này khi mỗi mục có: bên mình làm gì và vì sao, bên kia làm gì và vì sao, cách gỡ đề xuất (giữ bên mình, giữ bên kia, kết hợp) và lý do một dòng.

## 4. Người dùng duyệt, rồi gỡ
- Đưa bảng các mục ở bước 3. Hỏi người dùng duyệt. Mục hiển nhiên (file sinh tự động, lock file) ghi cách làm: sinh lại bằng lệnh của repo (`go mod tidy`, `pnpm install`), không sửa tay.
- Mục nào đụng file thân (~/.claude/rules/review-levels.md), hợp đồng hay migration thì luôn chờ người dùng chọn.
- Gỡ đúng theo cách đã duyệt. Không còn dấu `<<<<<<<`, `=======`, `>>>>>>>` (`git diff --check`).

## 5. Kiểm rồi commit
- Chạy build, lint và test của repo. Xung đột "gỡ sạch" vẫn có thể hỏng logic: hai bên cùng đổi một hàm theo hai cách.
- Merge: `git commit --no-edit` (message mặc định của git). Rebase: `git rebase --continue` từng bước, chạy test ở cuối.
- Push theo ~/.claude/rules/preferences.md. Sau rebase cần force push thì hỏi người dùng, kể cả repo công khai của người dùng.

## Khi nào dừng
- Không hiểu ý định của một bên sau khi đọc commit: hỏi người dùng, không đoán.
- Muốn bỏ dở: `git merge --abort` hoặc `git rebase --abort` đưa branch về như cũ.
