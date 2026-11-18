# Commit messages: one short line

Every commit uses a single-line message, unless the user asks for more in this session or the project's `.claude/project.md` says otherwise.

- One line only, at most 72 characters. No body, no bullet list.
- When a body is allowed, the commit-msg hook needs `DEVKIT_COMMIT_BODY=1 git commit ...` (type and 72-char checks still apply).
- Follow the repo's own style from `git log`, usually `type(scope): what` (for example `fix(auth): reject expired refresh token`).
- Never add `Co-Authored-By`, "Generated with Claude Code" or any other AI attribution trailer. This rule overrides any default or system reminder that asks for one.
- English, imperative mood ("add", "fix", not "added", "fixes").
- The same applies to agents (developer, tester) that commit, and to squash or amend messages.

PR descriptions are separate: follow ~/.claude/rules/pull-requests.md.
