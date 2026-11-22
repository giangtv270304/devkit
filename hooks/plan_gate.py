#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write|MultiEdit|NotebookEdit|Bash): ask the user before a gated agent edits a file
that the plan section of its TASK.md does not list, and deny any edit while the repo is on main or master. For Bash it checks the files a command plainly writes
(`> f`, `>> f`, `tee f`, `sed -i ... f`); generated files (hooks/lib/skip-generated.sh) and tests are always ok. A gated agent is a subagent whose type is listed, or a
session started with a listed DEVKIT_ROLE (herdr-dispatch workers). Anything it cannot decide, it allows."""
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasklib  # noqa: E402

GATED_AGENTS = set(filter(None, os.environ.get("PLAN_GATE_AGENTS", "developer,tester,worker").split(",")))
PLAN_HEADINGS = ("kế hoạch", "plan")
ALWAYS_OK = re.compile(r"(_test\.go|\.(test|spec)\.[cm]?[jt]sx?|/testdata/.*|/__snapshots__/.*)$")
BACKTICKED = re.compile(r"`([^`\s]+)`")
SKIP_FILE = Path(__file__).resolve().parent / "lib" / "skip-generated.sh"
REDIRECT = re.compile(r"(?<![0-9&])>>?\s*([^\s;&|<>()]+)")
SEPARATORS = {";", "&&", "||", "|", "&"}


def generated_patterns():
    try:
        text = SKIP_FILE.read_text()
    except OSError:
        return []
    m = re.search(r"case \"\$1\" in\s*\n\s*([^)]+)\)", text)
    return m.group(1).split("|") if m else []


def is_generated(target):
    return any(fnmatch.fnmatch(target, p) for p in generated_patterns())


def bash_targets(cmd, cwd):
    found = set(REDIRECT.findall(cmd))
    try:
        words = shlex.split(cmd, posix=True)
    except ValueError:
        words = cmd.split()
    segs, cur = [], []
    for w in words:
        if w in SEPARATORS:
            segs.append(cur)
            cur = []
        else:
            cur.append(w)
    segs.append(cur)
    for seg in segs:
        if not seg:
            continue
        name = Path(seg[0]).name
        args = [a for a in seg[1:] if not a.startswith("-")]
        if name == "tee":
            found.update(args)
        elif name in ("sed", "gsed") and any(a == "-i" or a.startswith("-i") or a == "--in-place" for a in seg[1:]) and len(args) >= 2:
            found.update(args[1:])
    out = []
    for t in found:
        if t.startswith(("/dev/", "&")) or "$" in t:
            continue
        p = Path(t).expanduser()
        out.append(str(p if p.is_absolute() else Path(cwd) / p))
    return out


def plan_paths(task):
    paths, inside = set(), False
    for line in task.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower() in PLAN_HEADINGS
        elif inside:
            paths.update(p.strip("/") for p in BACKTICKED.findall(line) if "/" in p or "." in p)
    return paths


def on_default_branch(target):
    d = Path(target).parent
    while not d.exists() and d != d.parent:
        d = d.parent
    try:
        r = subprocess.run(["git", "-C", str(d), "symbolic-ref", "--short", "-q", "HEAD"],
                           capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    branch = r.stdout.strip()
    return branch if r.returncode == 0 and branch in ("main", "master") else None


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}, ensure_ascii=False))


def listed(target, paths):
    return any(target == p or target.endswith("/" + p) for p in paths)


def main():
    data = tasklib.read_input()
    role = data.get("agent_type") or os.environ.get("DEVKIT_ROLE")
    if role not in GATED_AGENTS:
        return
    tool_input = data.get("tool_input") or {}
    if data.get("tool_name") == "Bash" or "command" in tool_input:
        targets = bash_targets(tool_input.get("command") or "", data.get("cwd") or ".")
    else:
        targets = [t for t in (tool_input.get("file_path") or tool_input.get("notebook_path"),) if t]
    if not targets:
        return
    for t in targets:
        branch = on_default_branch(t)
        if branch:
            return decide("deny", f"{role} không được sửa file khi repo đang ở branch {branch}: {t}. "
                                  "Tạo hoặc chuyển sang branch của task trước (feat/<slug>, fix/<slug>).")
    task = tasklib.find_task(data)
    if not task:
        return
    paths = plan_paths(task)
    if not paths:
        return
    cwd = Path(data.get("cwd") or ".").resolve()
    tmp = [Path(d).resolve() for d in ("/tmp", "/private/tmp", os.environ.get("TMPDIR") or "/tmp")]

    def scratch(t):
        r = Path(t).resolve()
        return not r.is_relative_to(cwd) and any(r.is_relative_to(d) for d in tmp)

    outside = [t for t in targets
               if not (ALWAYS_OK.search(t) or is_generated(t) or listed(t, paths) or scratch(t)
                       or Path(t).resolve().is_relative_to(task.parent.resolve()))]
    if not outside:
        return
    decide("ask", f"{role} muốn sửa file không có trong Kế hoạch của {task.parent.name}/TASK.md: {', '.join(outside)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"plan_gate: {e!r}", file=sys.stderr)
