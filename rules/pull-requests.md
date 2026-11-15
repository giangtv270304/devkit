# PR descriptions: short, for an engineer who skims

Readers are engineers who open the diff. They read the first lines of the description and skip the rest. Describe only what the change does.

## Shape
- Title: same style as the commit message (`type(scope): what`).
- Body: at most ~5 lines. No headings.
- First line: what changes and why, in one or two sentences.
- Then bullets only for what a reviewer would miss in the diff: behaviour on failure, a contract or data another service reads, a deliberate trade-off.

## Leave out
- Restating the diff (which files, which function was added, the SQL).
- Verification narrative: lint/build output, pre-existing lint issues, how you tested locally. One line `Not run end to end: <reason>` is allowed when it matters for review.
- "Follow-up", "out of scope", "no migration / no API change" lists. Mention a missing thing only if a reviewer would expect it.
- Background the reviewer does not need to judge the change. Long reasons go in TASK.md or an ADR; link it only if the repo can see it.
- Checklists of any kind (`Before deploy`, `TODO`, test plan). Nobody ticks them. Work needed before deploy goes in TASK.md and is told to the user in chat.
- AI attribution lines.

## Example
```
New users get a default row in `notification_settings`, so the digest job no longer crashes for a user without one.

- Best effort: if the insert fails, the user is still created and the error is logged with `user_id`.
- Skips the insert if the user already has a row (the table has no unique index).
```
