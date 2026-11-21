#!/usr/bin/env python3
"""Collect signals of friction from Claude Code transcripts (and a task folder) for the improver agent.

Usage:
  signals.py [--days N] [--grep TEXT] [--exclude SESSION_ID] [--task DIR] [--projects DIR]

Reads ~/.claude/projects/*/*.jsonl changed in the last N days (default 1). --grep keeps only transcripts that
contain TEXT (for example a task slug). --task also reads TASK.md and log.md in DIR. Output is redacted text,
one line per signal, grouped by session.
"""
import argparse
import glob
import json
import os
import re
import sys
import time

CORRECTION = re.compile(
    r"\b(không phải|sai|vẫn (còn|như|chưa|bị)|xong rồi mà|chưa (đúng|làm)|lại (bị|nữa)|đừng|tại sao|sao lại|"
    r"không (đúng|có thay đổi)|nhầm|bị lỗi|wrong|not what|again|why did|don't)\b",
    re.I,
)
REPORT = re.compile(r"\b(NEEDS_REPLAN|BLOCKED|DONE_WITH_CONCERNS)\b")
TASK_LINE = re.compile(r"^\s*(> NOTE:|.*người dùng quyết:|.*NEEDS_REPLAN|.*BLOCKED|.*DONE_WITH_CONCERNS)", re.I)
SECRET = [
    (re.compile(r"\b([a-z][\w+.-]*://[^:/@\s]+:)[^@\s]+@", re.I), r"\1<redacted>@"),
    (re.compile(r"\b(\w*(?:PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY)\w*)=('[^']*'|\"[^\"]*\"|\S+)", re.I), r"\1=<redacted>"),
    (re.compile(r"(?i)\b(bearer|token|secret|password|passwd|api[_-]?key)\b(\s*[:=]\s*|\s+)\S+"), r"\1=<redacted>"),
    (re.compile(r"\b(sk|pk|ghp|gho|xox[abp])[-_][A-Za-z0-9_-]{10,}"), "<redacted>"),
    (re.compile(r"\b[A-Fa-f0-9]{32,}\b"), "<hex>"),
    (re.compile(r"\b[A-Za-z0-9+/_-]{40,}={0,2}"), "<blob>"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<email>"),
]
WIDTH = 240
NOT_TYPED = ("<", "This session is being continued", "Base directory for this skill", "Caveat:")
PROMPT_LEN = 400


def clean(text, width=WIDTH):
    text = " ".join(str(text).split())
    for pat, rep in SECRET:
        text = pat.sub(rep, text)
    return text if len(text) <= width else text[: width - 1] + "…"


def texts(content):
    if isinstance(content, str):
        return [content]
    out = []
    for it in content or []:
        if isinstance(it, dict) and it.get("type") == "text":
            out.append(it.get("text", ""))
        elif isinstance(it, dict) and it.get("type") == "tool_result":
            out.extend(texts(it.get("content")))
    return out


def tool_label(use):
    inp = use.get("input") or {}
    detail = inp.get("command") or inp.get("file_path") or inp.get("subagent_type") or inp.get("description") or ""
    return f"{use.get('name')}: {clean(detail, 120)}"


def session_signals(path):
    uses, out, meta = {}, [], {"cwd": "", "first": ""}
    for line in open(path, encoding="utf-8", errors="ignore"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("isSidechain") or d.get("type") not in ("user", "assistant"):
            continue
        meta["cwd"] = meta["cwd"] or d.get("cwd", "")
        ts = (d.get("timestamp") or "")[:16].replace("T", " ")
        content = (d.get("message") or {}).get("content")
        if d["type"] == "assistant":
            for it in content if isinstance(content, list) else []:
                if isinstance(it, dict) and it.get("type") == "tool_use":
                    uses[it.get("id")] = it
            continue
        items = content if isinstance(content, list) else [{"type": "text", "text": content or ""}]
        for it in items:
            if not isinstance(it, dict):
                continue
            if it.get("type") == "tool_result":
                if not it.get("is_error"):
                    continue
                body = " ".join(texts(it.get("content")))
                kind = "rejected" if "was rejected" in body or "doesn't want to proceed" in body else "error"
                label = tool_label(uses.get(it.get("tool_use_id"), {}))
                out.append((ts, kind, f"{label} -> {clean(body, 160)}"))
            elif it.get("type") == "text":
                text = (it.get("text") or "").strip()
                if not text:
                    continue
                if text.startswith("[Request interrupted"):
                    out.append((ts, "interrupt", clean(text, 80)))
                elif text.startswith("<hc from="):
                    if REPORT.search(text):
                        out.append((ts, "report", clean(text)))
                elif text.startswith(NOT_TYPED) or "Terminal điều phối:" in text:
                    continue
                else:
                    meta["first"] = meta["first"] or clean(text, 100)
                    typed_fix = len(text) <= PROMPT_LEN and CORRECTION.search(text)
                    out.append((ts, "correction" if typed_fix else "user", clean(text)))
    return meta, out


def task_signals(folder):
    out = []
    for name in ("TASK.md", "log.md"):
        p = os.path.join(folder, name)
        if os.path.isfile(p):
            for i, line in enumerate(open(p, encoding="utf-8", errors="ignore"), 1):
                if TASK_LINE.match(line):
                    out.append((f"{name}:{i}", "task", clean(line)))
    lines = open(os.path.join(folder, "TASK.md"), encoding="utf-8", errors="ignore").read().splitlines() \
        if os.path.isfile(os.path.join(folder, "TASK.md")) else []
    for i, line in enumerate(lines, 1):
        if line.startswith("Lệch kế hoạch:") and line.split(":", 1)[1].strip() not in ("", "không"):
            out.append((f"TASK.md:{i}", "task", clean(line)))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=float, default=1)
    p.add_argument("--grep")
    p.add_argument("--exclude", action="append", default=[])
    p.add_argument("--task")
    p.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    a = p.parse_args()

    since = time.time() - a.days * 86400
    files = sorted((f for f in glob.glob(os.path.join(a.projects, "*", "*.jsonl")) if os.path.getmtime(f) >= since),
                   key=os.path.getmtime)
    counts, sessions = {}, 0
    for f in files:
        sid = os.path.basename(f)[:-6]
        if sid in a.exclude:
            continue
        if a.grep and a.grep not in open(f, encoding="utf-8", errors="ignore").read():
            continue
        meta, sigs = session_signals(f)
        if not any(k != "user" for _, k, _ in sigs):
            continue
        sessions += 1
        print(f"## session {sid[:8]}  cwd={meta['cwd']}  first={meta['first']!r}")
        for ts, kind, text in sigs:
            counts[kind] = counts.get(kind, 0) + 1
            print(f"{ts}  {kind:<10} {text}")
        print()
    if a.task:
        sigs = task_signals(a.task)
        if sigs:
            print(f"## task {a.task}")
            for where, kind, text in sigs:
                counts[kind] = counts.get(kind, 0) + 1
                print(f"{where}  {kind:<10} {text}")
            print()
    summary = ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "none"
    print(f"# {sessions} sessions with signals out of {len(files)} transcripts; {summary}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
