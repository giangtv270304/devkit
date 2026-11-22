---
name: dependency-upgrade
description: Cách nâng phiên bản thư viện an toàn - xem đang dùng bản nào, đọc changelog, nâng theo lô nhỏ, chạy test, giữ đường lùi. Gồm Go modules và npm/pnpm/yarn, cả khi vá lỗ hổng (CVE). Dùng khi người dùng nói "nâng version", "update dependency", "vá CVE", "govulncheck", "npm audit", "dependabot", hoặc khi một lỗi do phiên bản thư viện.
---

# dependency-upgrade: nâng thư viện từng bước, lùi được

## 1. Xem hiện trạng
Settings chặn đọc `go.sum`, `package-lock.json`, `pnpm-lock.yaml`. Dùng lệnh thay vì mở file:
- Go: `go list -m all` (mọi module và phiên bản), `go list -m -u all` (có bản mới), `go mod why -m <module>` (vì sao cần), `govulncheck ./...` nếu đã cài.
- Node: `npm ls <pkg>` / `pnpm why <pkg>` / `yarn why <pkg>`, `npm outdated`, `npm audit --omit=dev`.
- Lệnh `npm audit` và `govulncheck` gửi tên và phiên bản thư viện ra ngoài, không gửi code. Chạy được nếu công cụ đã có, theo ~/.claude/rules/preferences.md.

## 2. Chọn phạm vi
- Một lô là một thư viện, hoặc một nhóm đi cùng nhau (ví dụ mọi gói `@aws-sdk/*`). Không nâng tất cả một lần, vì test fail thì không biết do gói nào.
- Vá CVE: nâng tới bản nhỏ nhất đã vá, không nhảy major nếu không cần. Kiểm tra code có thật sự gọi tới phần bị lỗi không (`govulncheck` báo điều này), ghi vào báo cáo.
- Nâng major: đọc changelog và hướng dẫn chuyển đổi trước. Liệt kê thay đổi phá vỡ chạm tới code của repo (grep các API bị đổi). Nhiều chỗ thì đây là một task `/work`, không phải một lô nâng cấp.

## 3. Nâng
- Go: `go get <module>@<version>`, `go mod tidy`. Xem thay đổi bằng `git diff -- go.mod` (không gọi tên `go.sum`, xem ~/.claude/rules/go.md). Toolchain đổi (`go` hoặc `toolchain` trong go.mod) là thay đổi riêng, hỏi trước.
- Node: dùng đúng trình quản lý gói của repo (lock file nào có thì dùng cái đó). Không xóa lock file để cài lại từ đầu.
- Thư viện mới hoặc thay thư viện: hỏi người dùng trước.

## 4. Kiểm tra
- Lint, build, test của repo sau mỗi lô. Fail thì sửa code theo changelog, hoặc lùi lô đó.
- Thư viện chạm tới tiền, xác thực, crypto, HTTP client gọi nhà cung cấp: file thân, chạy thử luồng thật (skill `work` mục Kiểm tra).
- Ghi mỗi lô một dòng: gói, từ bản nào lên bản nào, lý do, kết quả test.

## 5. Đường lùi
Mỗi lô một commit, theo ~/.claude/rules/commits.md (ví dụ `chore(deps): bump pgx to v5.7.2`), để `git revert` từng lô. Mô tả PR nói thay đổi phá vỡ nào đã xử lý, theo ~/.claude/rules/pull-requests.md.
