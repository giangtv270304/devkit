# When the user corrects how you worked

Fix the instruction that produced the mistake, not only this output, so the next session does not repeat it.

1. Name the wrong decision in one sentence: what you concluded, and what you should have concluded.
2. Find the passage that drove it in the layers you had: `~/.claude/rules/`, the workspace `CLAUDE.md`, the repo `CLAUDE.md`, `.claude/project.md`, and the skill or agent that ran. It is usually one of three shapes: the case is missing; a tool is described but not the decision it serves; a ban stands without the action to take instead.
3. Propose a rewrite in the layer that owns the topic: a rule for every project, the workspace `CLAUDE.md` for its repos, a repo `CLAUDE.md` for its own tools, a skill for its workflow. Write it as "when X, do Y, because Z"; the reason lets a later session handle a case the text did not list.
4. Read the rewrite against the failing case and against the case the old text was written for. Both must come out right.
5. If the text was already right and the slip happened anyway, propose a hook or script instead of more text.
6. Save to memory only what no instruction file can own: a fact about the user or an outside system.

Show the proposed edit and wait for a yes before changing a `CLAUDE.md`, rule, skill or agent, because they steer every later session. A one-off correction to the current output needs none of this.
