# Working preferences (all projects)

## Third-party tools
- Prefer what needs no third-party code: built-in Claude Code features, and notes, rules, skills and hooks written here.
- Suggest a third-party repo, plugin or MCP server only with its risks stated: telemetry, network calls, what content leaves the machine, license.
- Never install one without the user's explicit yes.

## AI tooling stays local
- AI files (`CLAUDE.md`, `.claude/`, task files) are not committed to a company or shared repo unless the user says so for that repo.
- No AI attribution in commits, PRs or review comments.

## Ops and data-fix scripts
- Dry run by default; a flag such as `-apply` writes.
- Print a short header first: environment, target (database, API base URL), mode (`DRY RUN (nothing is written)` or `APPLY`), scope.
- Then one aligned table row per item: id, our value, their value, a short result ("in sync", "would update X -> Y", "updated X -> Y", "skipped", "failed"), a note.
- End with a one-line summary with counts per result.

## Secrets
- Never read, print or commit real `.env` files. Read `.env.example` for variable names only.
