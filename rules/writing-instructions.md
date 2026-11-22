---
paths:
  - "**/SKILL.md"
  - "**/CLAUDE.md"
  - "**/AGENTS.md"
  - "**/.claude/project.md"
  - "**/agents/*.md"
  - "**/rules/*.md"
  - "**/herdr/templates/*.md"
  - "**/output-styles/*.md"
---
# Writing text an agent reads: skills, agents, rules, CLAUDE.md

These files steer every later session, so a weak line repeats as a mistake many times. Write for the same process every run, not for one good output.

Adapted from mattpocock/skills `writing-for-agents` and obra/superpowers `writing-skills` (both MIT).

## The description is the trigger
- A skill's `description`, an agent's `description` and a CLAUDE.md line that points to a doc decide when the material is reached. A must-have body behind a weak pointer is skipped. Sharpen the pointer before moving text into an always-loaded file.
- Start with what the thing is, then one trigger per distinct case ("Dùng khi ..."). Synonyms of one case are one trigger; keep the clearest.
- Always-loaded text (descriptions, rules without `paths:`, CLAUDE.md) costs tokens on every turn. Prune it harder than a body.

## Steps and where text sits
- Steps first, in order. Reference (tables, rules, gotchas) after them or in a sibling file the step points to. Push out what only some cases need; keep inline what every case needs.
- End every step on a check the agent can tell done from not done ("every changed file listed", "test is red on the bug"), not "understand X". A vague end invites rushing to the next step.
- Keep one concept's rule, reason and exceptions under one heading.

## Phrasing
- Say the action to take. A ban alone puts the banned action in context and gives no path. When a ban is needed (safety, secrets), pair it with what to do instead.
- Write "when X, do Y, because Z" (see `rules/instructions.md`). The reason lets a later session handle a case the text did not list.
- Reuse one plain word for one idea across files ("bằng chứng", "phạm vi", `NEEDS_REPLAN`). The same word in prompts, skills and code makes the agent link them.
- Delete a sentence that does not change behaviour against the model's default ("be careful", "write clean code"). If the default is the problem, use a stronger, concrete rule.

## Match the form to the failure
| The agent... | Write | Not |
|---|---|---|
| skips a rule it knows, under pressure | a hard rule, the excuse it used and the answer to it | "prefer", "consider" |
| leaves out a part of something it already produces | a required slot in the template or report format | a prose reminder near the template |
| does not know how | numbered steps with one example | a list of principles |
| keeps slipping although the text is right | a hook or script | more text |

## One source of truth
- Each meaning lives in one file; others point to it by path. A copy in two places drifts.
- Do not restate what the environment answers in one lookup (`Makefile` targets, `package.json` scripts, `--help`, directory layout). Write what no file says: the unwritten convention, the reason, the gotcha.
- When a line goes stale, delete it. Adding feels safe and removing feels risky; old layers bury the live rules.

## Test a change before keeping it
For a rule or skill that fixes a seen failure: replay the task that failed, without the change, in a fresh subagent or session, and confirm the failure shows. Then replay with the change. No failure without the change means there is nothing to fix: drop it. Run each variant a few times; one sample can mislead.
