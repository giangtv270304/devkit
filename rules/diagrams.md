# Draw the picture while planning

When a plan or a discussion covers a new API, a new flow, or a logic change that touches three or more components or changes the order of steps, draw it with the Excalidraw MCP (`create_view`) while you write the plan, and show it before you ask for approval, because the user checks the shape of a change faster from a picture than from a list of steps.

1. Draw one picture of what changes: a sequence for a flow (caller -> API -> service -> store or provider, with the failure and retry branch), or the components and the calls between them. Mark new parts green, changed parts amber, removed parts red. Keep it to about 12 boxes; split a bigger change into one picture per flow.
2. Use role names only (Client, API, Worker, DB, Queue, Payment provider). Excalidraw is a remote server (`rules/preferences.md`), so company, client and internal service names, table names and code stay out of it. If role names cannot tell two parts apart, number them (Service A, Service B) and give the key in chat.
3. Write the same picture as mermaid with the real names under `## Kế hoạch` in TASK.md, or in the ADR, and note the Excalidraw `checkpointId` next to it. The chat drawing is gone after the session, and reviewers and later sessions read the file.
4. When the plan changes (`NEEDS_REPLAN`, a `> NOTE:` that moves a step), redraw from the checkpoint and update the mermaid in the same turn.

Skip the drawing for a single-file fix, a config change or a rename, where the picture adds nothing to the steps. When the session has no Excalidraw tool (an architect subagent, a Herdr worker, the MCP not connected), the session that talks to the user draws it after the plan comes back; if none can, write the mermaid only and say so in one line.
