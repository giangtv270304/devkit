#!/usr/bin/env python3
"""PreToolUse hook (Agent|Task): inside Herdr (HC_TERMINAL_ID set), deny subagents whose work the user wants to
watch, so it runs in a visible herdr-dispatch pane instead. A reviewer pane (DEVKIT_ROLE=reviewer) may still call
the review agents. Anything it cannot decide, it allows."""
import json
import os
import sys

CODE = {"developer", "tester"}
REVIEW = {"reviewer", "security-reviewer"}


def reason(kind):
    if kind in CODE:
        return (f"Đang chạy trong Herdr: không giao bước ghi code cho subagent {kind}. Mở pane worker: "
                "python3 ~/.claude/skills/herdr-dispatch/dispatch.py <repo> <tên> \"<việc>\" --template worker "
                "(tester và developer của một bước gộp vào một pane).")
    return (f"Đang chạy trong Herdr: không chạy {kind} bằng subagent. Mở pane review: "
            "python3 ~/.claude/skills/herdr-dispatch/dispatch.py <repo> review-<slug> "
            "\"<TASK.md>, branch <b>, commit gốc <sha>\" --template reviewer, rồi chờ bằng hc wait --children any.")


def main():
    if not os.environ.get("HC_TERMINAL_ID"):
        return
    data = json.load(sys.stdin)
    kind = (data.get("tool_input") or {}).get("subagent_type")
    if kind in REVIEW and os.environ.get("DEVKIT_ROLE") == "reviewer":
        return
    if kind not in CODE | REVIEW:
        return
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason(kind),
    }}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"herdr_agent_gate: {e!r}", file=sys.stderr)
