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
| **Entry points** (you type them) | |
| `skills/work` | one `TASK.md` per task: goal, plan, build, verify, review, ship; two approval stops |
| `skills/lead` | `/lead` in a Herdr tab: the session coordinates a project; each plain request is answered, done in place, or delegated through `herdr-dispatch`, with `LEAD.md` as its memory |
| `skills/design` | `/design`: context, non-functional needs, options, an ADR with diagrams |
| `skills/review-pr` | review someone else's PR in a separate worktree |
| `skills/research` | sourced answers at three depths, any domain |
| `skills/brainstorm` | from a vague idea to a decision record |
| **Conventions** (loaded before writing code) | |
| `skills/go-service` | Go service conventions with a reference service |
| `skills/sdk-wrapper` | an SDK that wraps an HTTP API, with a reference SDK in Go and TypeScript |
| `skills/data-design` | data model, keys, indexes, expand/contract migrations, backfills, ledgers |
| `skills/ops-change` | Dockerfile, CI/CD, deploy config, secrets, monitoring, rollback, runbooks |
| `skills/frontend-change` | web and mobile screens: states, API contract, verification in a browser or simulator |
| **Methods** | |
| `skills/tdd`, `skills/debug` | test first; find the root cause before fixing |
| `skills/cross-repo-change`, `skills/refresh-context` | multi-repo changes; keeping CLAUDE.md and notes current |
| **Herdr** (see the Herdr section) | |
| `skills/herdr-dispatch` | open an agent as a pane or tab: a one-off with `helper`, or plan steps with `worker` (one agent per repo, or one git worktree per step) |
| `herdr/templates` | `worker.md` (a plan step), `reviewer.md` (reviews the diff itself by the rules in `agents/reviewer.md` or `agents/security-reviewer.md`), `helper.md` (a one-off, read-only by default): rules copied into an agent's first message; linked to `~/.config/herdr-core/templates/` |
| `bin/herdr-task` | `herdr-task <slug> [first message] [--root DIR]`: open a Herdr space with a lead `claude`; linked to `~/.local/bin/` |
| **Shared** | |
| `agents/` | architect, tester, developer, reviewer, security-reviewer |
| `rules/` | comments, commits, Go, pull requests, review levels, writing style, preferences, fixing an instruction after a correction, opening agents inside Herdr |
| `output-styles/` | `engineer-brief` and `plain-words` reply styles |
| `templates/project.md`, `templates/adr.md` | starting points for a project's `.claude/project.md` and for an ADR when the project has no template |
| `settings/user.fragment.json` | hooks and deny rules that `install.py` merges into `~/.claude/settings.json` |
| `denylist.example.txt` | format of `~/.config/devkit/denylist.txt`, read by the pre-commit hook |
| `.githooks/` | this repo's own `pre-commit` (secrets, IPs, denylist) and `commit-msg`; enable with `core.hooksPath` |
| `hooks/task_log.py` | on Stop and SubagentStop, appends one line to `log.md` next to the active `TASK.md` |
| `hooks/plan_gate.py` | asks before developer, tester or a Herdr worker (`DEVKIT_ROLE=worker`) edits a file the plan does not list |
| `hooks/herdr_agent_gate.py` | inside Herdr, denies developer, tester, reviewer and security-reviewer subagents so the work runs in a visible pane, reviewer panes included |
| `hooks/format-edited-file.sh` | formats the file just edited |
| `hooks/lib/` | `skip-generated.sh`: the generated-file list that both edit hooks share |
| `hooks/task_resume.py` | after a compaction, tells the session which `TASK.md` it was on and shows the last `log.md` lines |
| `hooks/comment-guard.sh` | after an edit to Go, TS/JS or SQL, sends new comment lines back to Claude to delete unless they pass `rules/comments.md` |
| `git-local/` | hide AI files from git, block pushing them, and reject commit messages that break `rules/commits.md`, in any repo |
| `tests/`, `Makefile` | `make test` runs the unit tests; `make lint` runs `bash -n`, `py_compile` and `shellcheck`/`ruff` when installed |

## Herdr

In a single repo, `herdr-dispatch` gives each independent step its own worktree (`dispatch.py --worktree <branch>`); the lead merges the branches in plan order and removes a worktree only after its branch is merged. Worktrees go to `worktrees.directory` in `~/.config/herdr-app/settings.json` (default `~/.herdr/worktrees`). Claude asks to trust the folder the first time it runs in a new worktree, so that agent shows Blocked until you answer.

Claude desktop and Herdr run the same flow. `/work` uses subagents outside Herdr and `herdr-dispatch` panes inside it (worker for code, reviewer for review; only architect and search stay subagents); either way a step is test first, edits outside the plan go through `plan_gate`, the agent reports `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_REPLAN` or `BLOCKED`, and only the coordinator writes `TASK.md`. A Herdr reviewer pane reviews by reading `agents/reviewer.md` (or `security-reviewer.md` in a separate pane), so review rules live only in `agents/`. A repo that another task is already using (not on its default branch, uncommitted changes, or an agent in it) always gets a worktree.

## Rules for this repo

- No company, client, repo, service or vendor names. No secrets. No real `.env`.
- Third-party code is not vendored here.
- File names are lowercase with hyphens, except `SKILL.md`, `README.md` and the `TASK.md` files skills create.
