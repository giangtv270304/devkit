#!/usr/bin/env python3
"""PreToolUse hook (Agent|Task): inside Herdr (HC_TERMINAL_ID set), deny code-writing subagents so the
work runs in a visible herdr-dispatch worker pane instead. Read-only subagents pass. Anything it cannot
decide, it allows."""
import json
import os
import sys

BLOCKED = set(filter(None, os.environ.get("HERDR_GATED_SUBAGENTS", "developer,tester").split(",")))


def main():
    if not os.environ.get("HC_TERMINAL_ID"):
        return
    data = json.load(sys.stdin)
    kind = (data.get("tool_input") or {}).get("subagent_type")
    if kind not in BLOCKED:
        return
    reason = (f"Đang chạy trong Herdr: không giao bước ghi code cho subagent {kind}. "
              "Mở pane worker bằng skill herdr-dispatch: python3 ~/.claude/skills/herdr-dispatch/dispatch.py "
              "<repo> <tên> \"<việc>\" --template worker (tester và developer của một bước gộp vào một pane).")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"herdr_agent_gate: {e!r}", file=sys.stderr)
