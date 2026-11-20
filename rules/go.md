---
paths:
  - "**/*.go"
---
Before writing or changing Go in a backend service, load the `go-service` skill and copy the closest file from its `reference/` folder. The repo's own CLAUDE.md and the project's `.claude/project.md` win where they differ.

When you check whether dependencies changed, run `git diff -- go.mod` and never name `go.sum` in a Bash command. The settings deny `Read(./**/go.sum)`, and that deny rejects the whole command, including any `go build` or `go test` chained to it. Every version change shows up in go.mod; `go mod verify` checks go.sum without naming it.
