# devkit

Personal Claude Code toolkit: skills, agents, rules, hooks and output styles that work in any project. Project-specific facts live in each project's `.claude/project.md`, never here.

## New machine

```bash
git clone <this repo> ~/devkit
```

```bash
~/devkit/install.py
```

```bash
~/devkit/install.py --apply
```

The first run is a dry run and prints one row per item. `--apply` links each skill, agent, rule and output style into `~/.claude/`, links `~/.claude/devkit` to this repo, and merges `settings/user.fragment.json` (hooks and deny rules) into `~/.claude/settings.json` after writing a backup next to it. It never overwrites a file it did not create.

If agents do not show up after install, run `./install.py --apply --copy-agents` (copies instead of links; re-run after each pull).

Update: `git pull`. Links point into the repo, so changes apply to the next session. Re-run `install.py --apply` only when a file was added or `settings/user.fragment.json` changed.

Remove: `./install.py --uninstall --apply`.

## Once per clone

```bash
git -C ~/devkit config core.hooksPath .githooks
```

Then create `~/.config/devkit/denylist.txt` (see `denylist.example.txt`). The pre-commit hook blocks secrets, env files, IP addresses and every name on that list. The list itself stays off the repo.

## Per project

- Copy `templates/project.md` to `<project>/.claude/project.md` and fill in what differs from the defaults.
- Keep AI files out of the project's git and block pushes that carry them: `git-local/install.sh <repo or folder of repos>`. It copies the hooks, so run it again after you change a hook in `git-local/`.

## Layout

| Path | What |
|---|---|
| `skills/work` | one `TASK.md` per task: goal, plan, build, verify, review, ship; two approval stops |
| `skills/review-pr` | review someone else's PR in a separate worktree |
| `skills/research` | sourced answers at three depths, any domain |
| `skills/brainstorm` | from a vague idea to a decision record |
| `skills/cross-repo-change`, `skills/refresh-context` | multi-repo changes; keeping CLAUDE.md and notes current |
| `skills/go-service` | Go service conventions with a reference service |
| `skills/sdk-wrapper` | conventions for an SDK that wraps an HTTP API, with a reference SDK in Go and TypeScript |
| `skills/lead` | `/lead` in any Herdr tab: the session becomes the project's coordinator; each plain request is answered, done in place, or delegated through `herdr-dispatch`, with `LEAD.md` as its memory |
| `skills/herdr-dispatch` | give each step of a plan to its own agent in a Herdr tab or pane: one agent per repo, or one git worktree per step in a single repo |
| `herdr/templates` | `worker.md` and `reviewer.md`: rules `herdr-dispatch` copies into an agent's first message; linked to `~/.config/herdr-core/templates/` |
| `bin/herdr-task` | `herdr-task <slug> [first message] [--root DIR]`: open a Herdr space with a lead `claude`; linked to `~/.local/bin/` |
| `agents/` | architect, tester, developer, reviewer, security-reviewer |
| `rules/` | comments, commits, Go, pull requests, review levels, writing style, preferences, fixing an instruction after a correction |
| `output-styles/` | `engineer-brief` and `plain-words` reply styles |
| `templates/project.md` | starting point for a project's `.claude/project.md` |
| `settings/user.fragment.json` | hooks and deny rules that `install.py` merges into `~/.claude/settings.json` |
| `denylist.example.txt` | format of `~/.config/devkit/denylist.txt`, read by the pre-commit hook |
| `.githooks/` | this repo's own `pre-commit` (secrets, IPs, denylist) and `commit-msg`; enable with `core.hooksPath` |
| `hooks/task_log.py` | on Stop and SubagentStop, appends one line to `log.md` next to the active `TASK.md` |
| `hooks/plan_gate.py` | asks before developer or tester edits a file the plan does not list |
| `hooks/format-edited-file.sh` | formats the file just edited |
| `hooks/lib/` | `skip-generated.sh`: the generated-file list that both edit hooks share |
| `hooks/task_resume.py` | after a compaction, tells the session which `TASK.md` it was on and shows the last `log.md` lines |
| `hooks/comment-guard.sh` | after an edit to Go, TS/JS or SQL, sends new comment lines back to Claude to delete unless they pass `rules/comments.md` |
| `git-local/` | hide AI files from git, block pushing them, and reject commit messages that break `rules/commits.md`, in any repo |
| `tests/`, `Makefile` | `make test` runs the unit tests; `make lint` runs `bash -n`, `py_compile` and `shellcheck`/`ruff` when installed |

## Herdr

In a single repo, `herdr-dispatch` gives each independent step its own worktree (`dispatch.py --worktree <branch>`); the lead merges the branches in plan order and removes a worktree only after its branch is merged. Worktrees go to `worktrees.directory` in `~/.config/herdr-app/settings.json` (default `~/.herdr/worktrees`). Claude asks to trust the folder the first time it runs in a new worktree, so that agent shows Blocked until you answer.

## Rules for this repo

- No company, client, repo, service or vendor names. No secrets. No real `.env`.
- Third-party code is not vendored here.
- File names are lowercase with hyphens, except `SKILL.md`, `README.md` and the `TASK.md` files skills create.
