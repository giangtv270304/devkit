# Project config

Read by the devkit skills, agents and hooks. Copy to `<project root>/.claude/project.md` and fill in. Every line is optional; delete what you don't need. Keep the `Key: value` lines exactly in this form, scripts parse them.

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
Docs language: vi

## Checks
Commands a change must pass, per language or per repo.
- <language or repo>: `<lint command>`, `<test command>`; regenerate API spec: `<command>`

## Conventions
Which skill or document holds the coding conventions.
- Go: skill `go-service`
- <language>: <path to conventions doc>

## Project trunk
Files, services or data that are always "thân" (read line by line) in this project, on top of ~/.claude/rules/review-levels.md.
-

## Project security checks
Concrete mechanisms the security-reviewer must find intact (auth scheme, signature headers, limits, data exports).
-

## Public docs
What else must be updated when a public API or contract changes.
-
