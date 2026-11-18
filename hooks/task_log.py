#!/usr/bin/env python3
"""Stop / SubagentStop hook: append one line to log.md next to the TASK.md in use. Never blocks."""
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasklib  # noqa: E402

MAX_CHARS = 240
SECRET = re.compile(
    r"(?i)((?:api[_-]?key|secret|token|password|authorization)\s*[:=]\s*(?:bearer\s+)?\S+|bearer\s+[\w.~+/=-]{12,}|eyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{5,}|sk-[\w-]{16,}|gh[pousr]_\w{20,})"
)


def one_line(text):
    text = SECRET.sub("[redacted]", " ".join((text or "").split()))
    return text if len(text) <= MAX_CHARS else text[: MAX_CHARS - 3] + "..."


def main():
    data = tasklib.read_input()
    if data.get("stop_hook_active"):
        return
    task = tasklib.find_task(data)
    if not task:
        return
    who = data.get("agent_type") or "main"
    session = (data.get("session_id") or "")[:8]
    summary = one_line(data.get("last_assistant_message")) or "(no final message)"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(task.parent / "log.md", "a", encoding="utf-8") as f:
        f.write(f"- {stamp} | {who} | session {session} | {summary}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"task_log: {e!r}", file=sys.stderr)
