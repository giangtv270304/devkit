---
paths:
  - "**/*.go"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.sql"
---
# Code comments: default is none

Readers are experienced engineers. They read the code, the names, the commit and the PR. A comment is a cost: it goes stale and hides the code. Write none unless the test below forces one.

## Where the "why" goes instead
- The reason for a design decision (why we log instead of failing, why a call ignores cancellation, why a step is not in the transaction) goes in the commit message, the PR description, TASK.md or an ADR. Not in the code.
- Intent goes in names: a function, variable or constant named for what it means (`createAuditRowBestEffort`, `errAuditRowMissing`) instead of a comment.
- Operational hints go in the log message itself: `Msg("user created without audit row, add it manually")`.

## The test
Add a comment only if all three are true:
1. A competent engineer who knows Go/TypeScript and the standard library would likely change this line and break something.
2. A better name, a small function or a log message cannot carry the point.
3. It fits in one line (about 100 characters).

What usually passes:
- A provider or external-system quirk the code cannot show: `// The card provider reports FROZEN only via webhook, never in the API response.`
- Something that looks like a bug but is required: `// Order matters: the provider signs the raw body, not the parsed JSON.`
- The reason on a `//nolint:<linter>` directive.
- Required doc comments: swag blocks on handlers, godoc/JSDoc where the repo's linter demands it.

## Never write
- Explanations of standard behaviour (`context.WithoutCancel`, `defer`, `errors.Is`, pgx, echo, React hooks).
- Explanations of the error-handling choice or its consequences ("the row is already committed, so...", "so ops can fix it by hand").
- Narration of the business flow step by step, or of what the next lines do.
- More than one line for a single point, or more than one comment in a short function.
- Restating code (`// get user`, `// build response`), banners, change logs, author/date notes, "added for task X", commented-out code.
- TODOs without an owner and a ticket link.
- Anything that narrates what you (the AI) did or changed.

## Example
Bad:
```go
// The user row is already committed, so a failed audit row is only logged for ops to add by hand.
// WithoutCancel keeps a client disconnect from leaving the new user without an audit row.
if err := h.repo.CreateAuditRow(context.WithoutCancel(reqCtx), user.ID); err != nil {
	h.log.Error().Err(err).Int("user_id", user.ID).Msg("Failed to create audit row")
}
```
Good (the reason lives in the PR description; the log tells ops what to do):
```go
if err := h.repo.CreateAuditRow(context.WithoutCancel(reqCtx), user.ID); err != nil {
	h.log.Error().Err(err).Int("user_id", user.ID).Msg("user created without audit row, add it manually")
}
```

## When editing
Delete comments your change made wrong. Don't add comments to code you didn't otherwise touch. Before finishing, re-read every comment you added against the test above and delete the ones that fail it.
