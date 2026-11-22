---
name: fix-ci
description: Sửa check CI đang fail trên PR hoặc branch của chính người dùng - đọc log của job fail, nói nguyên nhân trước khi sửa, tái hiện ở máy, sửa gốc, chạy lại đúng check đó ở máy rồi mới push. Dùng khi người dùng nói "CI fail", "check đỏ", "fix CI", "build trên GitHub hỏng", đưa link một run hoặc PR có check fail, hoặc khi /work tới bàn giao mà PR còn check đỏ.
argument-hint: "[số PR hoặc link run]"
---

# fix-ci: đọc log, nói nguyên nhân, rồi mới sửa

Check đỏ là triệu chứng. Đọc log tới dòng lỗi đầu tiên, không đoán từ tên job. Comment review thì dùng skill `address-review`; branch cần gộp `main` thì dùng `resolve-conflicts`.

Adapted from getsentry/skills `iterate-pr` (Apache-2.0) and openai/skills `gh-fix-ci`.

## 1. Tìm check fail
- PR: `gh pr view <số> --json number,url,headRefName,isDraft` rồi `gh pr checks <số> --json name,state,bucket,link,workflow`. Không có số thì lấy PR của branch hiện tại.
- Với mỗi check `fail`: lấy run id từ `link`, rồi `gh run view <run-id> --log-failed`. Log quá dài thì lưu vào scratchpad và `grep -n -m5 -iE "error|fail|panic|FAIL:"`.
- Check không chạy trên GitHub Actions (link sang dịch vụ khác): chỉ báo tên và link, không đoán.
- Check còn `pending`: chờ bằng `gh pr checks <số> --watch --fail-fast` chạy nền, không `sleep`.
- Xong bước này khi mỗi check fail có: tên, run id, dòng lỗi đầu tiên trích từ log.

## 2. Phân loại từng lỗi
| Loại | Dấu hiệu | Làm gì |
|---|---|---|
| code | test, build, type, lint fail ở file của PR | sửa ở bước 3 |
| môi trường | máy CI khác máy mình: phiên bản Go/Node, biến môi trường, service phụ chưa lên | so sánh file workflow với máy mình, sửa cấu hình |
| chập chờn | cùng commit có lần pass, lỗi timeout hay thứ tự | `gh run rerun <run-id> --failed` một lần; fail lại thì coi là lỗi code (skill `debug`) |
| hạ tầng | runner chết, hết quota, registry lỗi, thiếu secret | dừng, báo người dùng, không sửa code để vòng qua |
| không thuộc PR | `main` cũng đỏ ở cùng check (`gh run list --branch main --workflow <tên> -L 3`) | báo người dùng, không sửa trong PR này |

Viết nguyên nhân một câu trước khi sửa: "fail vì X, ở `file:dòng`, do Y".

## 3. Tái hiện và sửa
- Chạy đúng lệnh mà job chạy (đọc trong `.github/workflows/<file>.yml`), ở máy, trên branch của PR. Đỏ ở máy với cùng lỗi là đã tái hiện.
- Không tái hiện được: so phiên bản công cụ và biến môi trường với job, rồi mới nghi code.
- Sửa nguyên nhân, không sửa triệu chứng: không thêm `skip`, không nới timeout, không tắt lint rule, không sửa test cho khớp hành vi sai, trừ khi người dùng đồng ý. Lỗi logic thì viết test tái hiện trước (skill `tdd`).
- Tìm chỗ khác có cùng kiểu lỗi (`grep`) và sửa luôn trong phạm vi PR.

## 4. Kiểm ở máy rồi mới push
- Chạy lại lệnh của từng check đã fail. Xanh hết mới commit.
- Commit một dòng theo ~/.claude/rules/commits.md. Push theo ~/.claude/rules/preferences.md: repo không phải repo công khai của người dùng thì hỏi trước.
- Sau khi push, theo dõi `gh pr checks <số> --watch` chạy nền và báo kết quả thật.

## Khi nào dừng
- Cùng một check fail sau hai lần sửa: dừng, báo hai lần đã thử và điều còn nghi.
- Lỗi đòi đổi file workflow, secret, quyền của token, hay cấu hình repo: đó là file thân (~/.claude/rules/review-levels.md); hỏi người dùng và theo skill `ops-change`.
- Chỉ còn chờ người duyệt hoặc PR đang draft: báo, không tự bấm ready hay merge.
