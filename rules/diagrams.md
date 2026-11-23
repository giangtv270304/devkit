# Pictures while discussing and planning

When a discussion or plan covers a new API, a new flow, a logic change across three or more components, or a data change, show the user a picture before asking for approval, because they check the shape of a change faster from a picture than from a list of steps.

- Plan exists (`/work` step 3, `/design` options): build the page with the `visual-plan` skill. It holds the diagrams plus contract examples, decision tables and worked examples, which a diagram alone does not show.
- Still discussing, no plan yet: sketch with the Excalidraw MCP (`create_view`). Use role names only (Client, API, Worker, DB, Queue, Payment provider; Service A/B with the key in chat), because Excalidraw is a remote server (`rules/preferences.md`) and company, client and internal service names, table names and code stay out of it.
- Either way, the mermaid of the main flow with real names goes under `## Kế hoạch` in TASK.md or in the ADR, because reviewers and later sessions read the file, not the chat or the page.

Skip pictures for a single-file fix, a config change or a rename.
