#!/usr/bin/env python3
"""SessionStart(compact) hook: point the resumed session back at the TASK.md it was working on. Never blocks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasklib  # noqa: E402

LOG_LINES = 5


def main():
    task = tasklib.find_task(tasklib.read_input())
    if not task:
        return
    print(f"Context was just compacted. The active task is {task}. Read it before the next step: its plan, phase and > NOTE: lines outrank the summary.")
    log = task.parent / "log.md"
    if log.is_file():
        last = log.read_text(encoding="utf-8", errors="replace").splitlines()[-LOG_LINES:]
        if last:
            print("Last lines of log.md:")
            print("\n".join(last))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"task_resume: {e!r}", file=sys.stderr)
