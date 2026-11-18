#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write|MultiEdit|NotebookEdit): ask the user before a gated agent edits a file
that the plan section of its TASK.md does not list. A gated agent is a subagent whose type is listed, or a
session started with a listed DEVKIT_ROLE (herdr-dispatch workers). Anything it cannot decide, it allows."""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasklib  # noqa: E402

GATED_AGENTS = set(filter(None, os.environ.get("PLAN_GATE_AGENTS", "developer,tester,worker").split(",")))
PLAN_HEADINGS = ("kế hoạch", "plan")
ALWAYS_OK = re.compile(r"(_test\.go|\.(test|spec)\.[cm]?[jt]sx?|/testdata/.*|/__snapshots__/.*)$")
BACKTICKED = re.compile(r"`([^`\s]+)`")


def plan_paths(task):
    paths, inside = set(), False
    for line in task.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower() in PLAN_HEADINGS
        elif inside:
            paths.update(p.strip("/") for p in BACKTICKED.findall(line) if "/" in p or "." in p)
    return paths


def listed(target, paths):
    return any(target == p or target.endswith("/" + p) for p in paths)


def main():
    data = tasklib.read_input()
    role = data.get("agent_type") or os.environ.get("DEVKIT_ROLE")
    if role not in GATED_AGENTS:
        return
    tool_input = data.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        return
    task = tasklib.find_task(data)
    if not task:
        return
    if ALWAYS_OK.search(target) or Path(target).resolve().is_relative_to(task.parent.resolve()):
        return
    paths = plan_paths(task)
    if not paths or listed(target, paths):
        return
    reason = f"{role} muốn sửa file không có trong Kế hoạch của {task.parent.name}/TASK.md: {target}"
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": reason,
    }}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"plan_gate: {e!r}", file=sys.stderr)
