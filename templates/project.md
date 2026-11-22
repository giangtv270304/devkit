# Project config

Read by the devkit skills, agents and hooks. Agents look sections up by these exact English headings, so keep them. Copy to `<project root>/.claude/project.md` and fill in. Every line is optional; delete what you don't need. Keep the `Key: value` lines exactly in this form, scripts parse them.

Layout: single-repo
GitHub org:
Task dir: .claude/work
ADR dir: docs/adr
Notes dir: docs/notes
Research dir: .claude/research
Architecture doc:
Contracts doc:
Review worktrees: .review-worktrees
Context state: .claude/context-state.json
Based-on docs:
Docs language: vi

## Checks
Commands a change must pass, per language or per repo.
- <language or repo>: `<lint command>`, `<test command>`; regenerate API spec: `<command>`

## Conventions
Which skill or document holds the coding conventions.
- Go: skill `go-service`
- Web: <framework>, <path to conventions doc>, reference screen: <path>
- Mobile: <framework>, <path to conventions doc>, how to run on simulator: <command>
- <language>: <path to conventions doc>

## Go notes
Per repo, which style it already uses for log keys, "not found" and error wrapping, and which golangci-lint config (skill `go-service`).
- <repo>: log keys snake_case | camelCase; not found `(nil, false, nil)` | `ErrNotFound`; lint v1 | v2

## Project trunk
Files, services or data that are always "thân" (read line by line) in this project, on top of ~/.claude/rules/review-levels.md.
-

## Project security checks
Concrete mechanisms the security-reviewer must find intact (auth scheme, signature headers, limits, data exports).
-

## Public docs
What else must be updated when a public API or contract changes.
-
