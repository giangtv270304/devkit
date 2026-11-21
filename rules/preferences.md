# Working preferences (all projects)

## Third-party tools
- Prefer what needs no third-party code: built-in Claude Code features, and notes, rules, skills and hooks written here.
- Suggest a third-party repo, plugin or MCP server only with its risks stated: telemetry, network calls, what content leaves the machine, license.
- Never install one without the user's explicit yes.
- Before asking to install a tool, check whether it is already there (`command -v <tool>`, the repo's devDependencies, `npx --no-install <tool> --version`). If it is, run it without asking, because the user already made the install decision. Still ask if running it sends repo content off the machine.

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
- When a command needs a value that only `.env` or a credential you were not given holds (database URL, password, API key), do not fetch it another way (`$(grep ...)`, another host, a service file). Give the user the exact query or command to run themselves, read-only for checks (`begin read only`), plus what the output should look like. Because a blocked read retried in another form is still a secret read, and the user answers these blocks with "give me the query, I'll run it".
- When a hook or the permission check denies a command, do not send it again unchanged. Switch to the hand-over above, or ask.

## Asking the user to decide
- When you ask the user to choose (AskUserQuestion or a question in chat), make each question answerable from its own text: what the thing is in plain words, what each option changes, and your recommendation with a one-line reason.
- Quote the part that matters instead of pointing to something they have not read (another pane's report, a file, a subagent hand-back). Explain an internal name the first time it appears.
- Because the user answers from the question alone: a question that needs "explain more" costs a round trip and is often answered wrongly.

## Drafting messages to other people
- When the user asks you to draft or rewrite a reply to a partner, provider or colleague (chat, email), answer only what they asked: one to three short sentences per question. No background, no restating their question, no list of extra offers. Because the user sends it as is and has asked "shorter" on almost every draft.
- Answer every question in the incoming message, in its numbering and order. Because a missing one costs a round trip.
- When the draft is not in Vietnamese, put a Vietnamese translation of the draft under it, and a translation of the incoming message if the user has not seen one yet. Because the user checks the meaning in Vietnamese before sending.
- When the user asks to expand one point, expand only that point and keep the rest as it was.
