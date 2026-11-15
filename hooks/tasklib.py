"""Shared helpers for the task hooks: find the TASK.md a session or subagent is working on."""
import json
import re
import sys
from pathlib import Path

TASK_REF = re.compile(r"[\w./~-]*?[\w.-]+/TASK\.md")
TAIL_BYTES = 300_000


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def tail(path, size=TAIL_BYTES):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - size))
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def head(path, size=TAIL_BYTES):
    try:
        with open(path, "rb") as f:
            return f.read(size).decode("utf-8", "replace")
    except OSError:
        return ""


def subagent_transcript(data):
    explicit = data.get("agent_transcript_path")
    if explicit:
        return explicit
    main, agent_id = data.get("transcript_path"), data.get("agent_id")
    if not (main and agent_id):
        return None
    p = Path(main)
    return str(p.with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl")


def resolve(ref, cwd):
    p = Path(ref.replace("\\/", "/")).expanduser()
    if not p.is_absolute():
        p = Path(cwd) / p
    return p if p.is_file() else None


def find_task(data):
    """A subagent is briefed with its TASK.md path, so take the first reference; a main session may switch tasks, so take the last."""
    cwd = data.get("cwd") or "."
    sub = subagent_transcript(data) if data.get("agent_id") or data.get("agent_transcript_path") else None
    sources = [(head(sub), False)] if sub else []
    sources.append((tail(data.get("transcript_path") or ""), True))
    for text, newest_first in sources:
        refs = TASK_REF.findall(text.replace("\\/", "/"))
        for ref in (reversed(refs) if newest_first else refs):
            task = resolve(ref, cwd)
            if task:
                return task
    return None
