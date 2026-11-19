# Working preferences (all projects)

## Third-party tools
- Prefer what needs no third-party code: built-in Claude Code features, and notes, rules, skills and hooks written here.
- Suggest a third-party repo, plugin or MCP server only with its risks stated: telemetry, network calls, what content leaves the machine, license.
- Never install one without the user's explicit yes.

## AI tooling stays local
- AI files (`CLAUDE.md`, `.claude/`, task files) are not committed to a company or shared repo unless the user says so for that repo.
- No AI attribution in commits, PRs or review comments.

## Commit, push and merge
- Public repo owned by the personal account `giangtv270304`: commit, push and merge into the default branch without asking, because the user owns it alone and wants finished work landed. Report the commit sha and pushed branch afterwards.
- Every other repo (private ones, including private `giangtv270304` repos, and any repo owned by an organization): never commit to the default branch, push, open a PR or merge until the user says so in this session.
- Exception: in the devkit repo (the one `~/.claude/devkit` links to), the `retro` skill may create, commit and push branches named `retro/*` without asking, because main stays untouched until the user reviews. Merging a `retro/*` branch into main still needs the user's "ok" in this session.
- Decide from `gh repo view <origin> --json owner,visibility` right before the push, not from memory, because visibility can change.
- Even in a public personal repo, ask before a force push, a history rewrite of the default branch, or deleting a branch, because they lose work. Since a push there publishes, check the diff for secrets, `.env` content and company or client names first, and stop and ask if any appear.

## Ops and data-fix scripts
- Dry run by default; a flag such as `-apply` writes.
- Print a short header first: environment, target (database, API base URL), mode (`DRY RUN (nothing is written)` or `APPLY`), scope.
- Then one aligned table row per item: id, our value, their value, a short result ("in sync", "would update X -> Y", "updated X -> Y", "skipped", "failed"), a note.
- End with a one-line summary with counts per result.

## Secrets
- Never read, print or commit real `.env` files. Read `.env.example` for variable names only.
