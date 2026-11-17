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
- Keep AI files out of the project's git and block pushes that carry them: `git-local/install.sh <repo or folder of repos>`.

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
| `skills/herdr-dispatch` | give each step of a multi-repo plan to its own agent in a Herdr tab or pane |
| `herdr/templates` | `worker.md` and `reviewer.md`: rules `herdr-dispatch` copies into an agent's first message; linked to `~/.config/herdr-core/templates/` |
| `bin/herdr-task` | `herdr-task <slug> [first message] [--root DIR]`: open a Herdr space with a lead `claude`; linked to `~/.local/bin/` |
| `agents/` | architect, tester, developer, reviewer, security-reviewer |
| `rules/` | comments, commits, pull requests, review levels, writing style, preferences |
| `hooks/task_log.py` | on Stop and SubagentStop, appends one line to `log.md` next to the active `TASK.md` |
| `hooks/plan_gate.py` | asks before developer or tester edits a file the plan does not list |
| `hooks/format-edited-file.sh` | formats the file just edited |
| `git-local/` | hide AI files from git and block pushing them, in any repo |
| `bin/` | command-line tools (reserved) |

## Herdr

Set `worktrees.directory` in `~/.config/herdr-app/settings.json` so agents work in worktrees outside the repo. Claude asks to trust the folder the first time it runs in a new worktree, so that agent shows Blocked until you answer.

## Rules for this repo

- No company, client, repo, service or vendor names. No secrets. No real `.env`.
- Third-party code is not vendored here.
- File names are lowercase with hyphens, except `SKILL.md`, `README.md` and the `TASK.md` files skills create.
