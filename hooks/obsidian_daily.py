#!/usr/bin/env python3
"""Write today's Obsidian daily note: /work tasks from TASK.md files and the prompts given to Claude today.

Usage:
  obsidian_daily.py            update now (CLI)
  obsidian_daily.py --hook     Stop hook mode: throttled, silent, never blocks
  obsidian_daily.py --off|--on disable or enable the hook
  obsidian_daily.py --status   print config and last run

Env: OBSIDIAN_VAULT, OBSIDIAN_DAILY_DIR (default Daily), OBSIDIAN_DAILY_WORKSPACES (paths joined by ':'; else one path per line in ~/.config/obsidian-daily/workspaces),
OBSIDIAN_DAILY_EVERY (seconds between hook runs, default 300), OBSIDIAN_DAILY=off disables the hook.
"""
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

HOME = Path.home()
VAULT = Path(os.environ.get("OBSIDIAN_VAULT", HOME / "Documents" / "Obsidian Vault"))
DAILY_DIR = os.environ.get("OBSIDIAN_DAILY_DIR", "Daily")
WORKSPACES_FILE = HOME / ".config" / "obsidian-daily" / "workspaces"


def _workspaces() -> list:
    raw = os.environ.get("OBSIDIAN_DAILY_WORKSPACES", "")
    if not raw and WORKSPACES_FILE.exists():
        raw = ":".join(line.strip() for line in WORKSPACES_FILE.read_text().splitlines() if line.strip())
    return [Path(os.path.expanduser(p)) for p in raw.split(":") if p]


WORKSPACES = _workspaces()
EVERY = int(os.environ.get("OBSIDIAN_DAILY_EVERY", "300"))
STATE = HOME / ".cache" / "obsidian-daily"
OFF_FLAG = STATE / "off"
LAST_RUN = STATE / "last_run"
PROJECTS = HOME / ".claude" / "projects"
WORK_SKILL = HOME / ".claude" / "skills" / "work"

SECRET = re.compile(
    r"(?i)((?:api[_-]?key|secret|token|password|authorization)\s*[:=]\s*(?:bearer\s+)?\S+|bearer\s+[\w.~+/=-]{12,}|eyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{5,}|sk-[\w-]{16,}|gh[pousr]_\w{20,})"
)
SKIP_PROMPT = ("This session is being continued", "<", "Caveat:", "[Request interrupted")
AUTO = ("tasks", "sessions")
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


def clean(text, n=160):
    text = SECRET.sub("[redacted]", " ".join((text or "").split())).replace("|", "\\|")
    return text if len(text) <= n else text[: n - 1] + "…"


def load_status(ws):
    os.environ["CLAUDE_PROJECT_DIR"] = str(ws)
    sys.path.insert(0, str(WORK_SKILL))
    for m in ("status", "project"):
        sys.modules.pop(m, None)
    import status  # noqa: E402

    return status


def summary_lines(task_md):
    if not task_md.exists():
        return {}
    out, inside = {}, False
    for line in task_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower() == "tóm tắt"
            continue
        m = inside and re.match(r"^\s*(Đang làm|Đã tới):\s*(.+)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def collect_tasks(today):
    tasks = []
    for ws in WORKSPACES:
        try:
            status = load_status(ws)
        except Exception as e:
            tasks.append({"error": f"{ws}: không đọc được ({e})"})
            continue
        if not status.WORK.is_dir():
            continue
        for d in sorted(status.WORK.iterdir()):
            if not d.is_dir():
                continue
            slug, phase, updated, need, git = status.task_row(d)
            done = phase.strip().lower().startswith("done")
            if done and updated != today:
                continue
            path = next((p for p in (d / "TASK.md", d / "CONTEXT.md") if p.exists()), d)
            tasks.append({
                "ws": ws.name, "slug": slug, "phase": phase, "updated": updated, "need": need,
                "git": git, "done": done, "path": path, "summary": summary_lines(d / "TASK.md"),
            })
    return tasks


def needs_you(t):
    need = t["need"].strip().lower().rstrip(".")
    return bool(need) and need not in ("không", "?", "no", "none")


def render_tasks(tasks):
    errors = [t["error"] for t in tasks if "error" in t]
    tasks = [t for t in tasks if "error" not in t]
    groups = [
        ("Cần bạn", [t for t in tasks if not t["done"] and needs_you(t)]),
        ("Đang chạy", [t for t in tasks if not t["done"] and not needs_you(t)]),
        ("Xong hôm nay", [t for t in tasks if t["done"]]),
    ]
    out = [f"_Tự cập nhật {datetime.now():%H:%M} từ `work/`. Phần này bị ghi đè, ghi chú riêng để ở mục bên dưới._", ""]
    for title, items in groups:
        if not items:
            continue
        out.append(f"### {title} ({len(items)})")
        items.sort(key=lambda t: t["updated"] or "", reverse=True)
        for t in items:
            box = "x" if t["done"] else " "
            link = f"[{t['path'].name if t['path'].is_file() else 'thư mục'}](<file://{t['path']}>)"
            upd = f" · {t['updated']}" if t["updated"] else ""
            out.append(f"- [{box}] **{t['slug']}** · `{t['phase']}`{upd} · {link}")
            for k in ("Đang làm", "Đã tới"):
                if t["summary"].get(k):
                    out.append(f"    - {k}: {clean(t['summary'][k], 200)}")
            if needs_you(t) and not t["done"]:
                out.append(f"    - CẦN BẠN: {clean(t['need'], 200)}")
            if t["git"] and t["git"] != "chưa ghi branch":
                out.append(f"    - Branch: {clean(t['git'], 240)}")
        out.append("")
    if errors:
        out += ["### Lỗi", *[f"- {e}" for e in errors], ""]
    return "\n".join(out).rstrip()


def user_prompt(d):
    if d.get("type") != "user" or d.get("isMeta") or d.get("isSidechain"):
        return None
    c = d.get("message", {}).get("content")
    if isinstance(c, list):
        texts = [x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text"]
        texts = [t for t in texts if not t.lstrip().startswith("<system-reminder>")]
        if not texts or any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
            return None
        c = " ".join(texts)
    if isinstance(c, str):
        c = REMINDER.sub("", c)
    if not isinstance(c, str) or not c.strip() or c.lstrip().startswith(SKIP_PROMPT):
        return None
    return c


def local_day(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
    except Exception:
        return None


def collect_sessions(day):
    start = datetime.combine(day, datetime.min.time()).timestamp()
    sessions = []
    for f in PROJECTS.glob("*/*.jsonl"):
        try:
            if f.stat().st_mtime < start:
                continue
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        title, cwd, first, count = "", "", None, 0
        for line in lines:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") in ("custom-title", "ai-title"):
                title = d.get("customTitle") or d.get("aiTitle") or title
            text = user_prompt(d)
            when = text and local_day(d.get("timestamp", ""))
            if not when or when.date() != day:
                continue
            count += 1
            cwd = d.get("cwd") or cwd
            if first is None:
                first = (when, text)
        if first:
            sessions.append({"when": first[0], "text": first[1], "title": title, "cwd": cwd, "count": count, "id": f.stem[:8]})
    sessions.sort(key=lambda s: s["when"])
    return sessions


def render_sessions(sessions):
    if not sessions:
        return "_Chưa có phiên Claude nào hôm nay._"
    out = [f"_{len(sessions)} phiên. Dòng đầu là câu giao việc đầu tiên trong ngày của phiên đó._", ""]
    for s in sessions:
        where = Path(s["cwd"]).name if s["cwd"] else "?"
        name = f"**{clean(s['title'], 80)}** · " if s["title"] else ""
        task = s["text"]
        parts = re.split(r"(?:^|\n)Task(?: \(from the session that started this one\))?:\s*", task)
        if len(parts) > 1:
            task = "(phiên con) " + parts[-1]
        out.append(f"- {s['when']:%H:%M} · {name}`{where}` · {s['count']} lượt · `{s['id']}`")
        out.append(f"    - {clean(task, 220)}")
    return "\n".join(out)


def block(name, body):
    return f"<!-- auto:{name} start -->\n{body}\n<!-- auto:{name} end -->"


def replace_block(text, name, body):
    pat = re.compile(rf"<!-- auto:{name} start -->.*?<!-- auto:{name} end -->", re.S)
    return pat.sub(lambda _: block(name, body), text, count=1)


def open_items(note):
    """Unchecked items in the user's own section of a previous note, to carry over."""
    text = note.read_text(encoding="utf-8")
    m = re.search(r"^## Việc riêng\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return []
    return [l for l in m.group(1).splitlines() if re.match(r"^\s*- \[ \] ", l)]


def previous_note(folder, day):
    for i in range(1, 31):
        p = folder / f"{day - timedelta(days=i):%Y-%m-%d}.md"
        if p.exists():
            return p
    return None


def new_note(folder, day, tasks_md, sessions_md):
    prev = previous_note(folder, day)
    carried = open_items(prev) if prev else []
    nav = f"← [[{prev.stem}]]" if prev else ""
    carry_md = "\n".join(carried) if carried else "- [ ] "
    if carried:
        carry_md = f"_Mang sang từ [[{prev.stem}]]:_\n" + carry_md
    return f"""---
date: {day:%Y-%m-%d}
tags: [daily]
---
# {day:%Y-%m-%d} {nav}

## Tasks
{block("tasks", tasks_md)}

## Việc giao Claude hôm nay
{block("sessions", sessions_md)}

## Việc riêng
{carry_md}

## Ghi chú
"""


def write_note(day):
    folder = VAULT / DAILY_DIR
    folder.mkdir(parents=True, exist_ok=True)
    note = folder / f"{day:%Y-%m-%d}.md"
    tasks_md = render_tasks(collect_tasks(f"{day:%Y-%m-%d}"))
    sessions_md = render_sessions(collect_sessions(day))
    if note.exists():
        text = note.read_text(encoding="utf-8")
        for name, body in zip(AUTO, (tasks_md, sessions_md)):
            if f"<!-- auto:{name} start -->" in text:
                text = replace_block(text, name, body)
            else:
                text += f"\n## {'Tasks' if name == 'tasks' else 'Việc giao Claude hôm nay'}\n{block(name, body)}\n"
    else:
        text = new_note(folder, day, tasks_md, sessions_md)
    tmp = note.with_suffix(".md.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(note)
    return note


def hook():
    if os.environ.get("OBSIDIAN_DAILY", "").lower() == "off" or OFF_FLAG.exists():
        return
    try:
        if time.time() - LAST_RUN.stat().st_mtime < EVERY:
            return
    except OSError:
        pass
    STATE.mkdir(parents=True, exist_ok=True)
    LAST_RUN.touch()
    write_note(date.today())


def main(argv):
    STATE.mkdir(parents=True, exist_ok=True)
    if "--hook" in argv:
        sys.stdin.read() if not sys.stdin.isatty() else None
        try:
            hook()
        except Exception as e:
            (STATE / "error.log").open("a").write(f"{datetime.now():%F %T} {e!r}\n")
        return
    if "--off" in argv:
        OFF_FLAG.touch()
        print("Đã tắt hook tự cập nhật daily note. Bật lại: obsidian_daily.py --on")
        return
    if "--on" in argv:
        OFF_FLAG.unlink(missing_ok=True)
        print("Đã bật hook tự cập nhật daily note.")
        return
    if "--status" in argv:
        last = datetime.fromtimestamp(LAST_RUN.stat().st_mtime).strftime("%F %T") if LAST_RUN.exists() else "chưa chạy"
        print(f"vault: {VAULT}\nfolder: {DAILY_DIR}\nworkspaces: {':'.join(map(str, WORKSPACES))}")
        print(f"hook: {'tắt' if OFF_FLAG.exists() else 'bật'} (mỗi {EVERY}s)\nlần chạy hook cuối: {last}")
        return
    if not (VAULT / ".obsidian").is_dir():
        sys.exit(f"Không thấy vault Obsidian ở {VAULT} (đặt OBSIDIAN_VAULT)")
    LAST_RUN.touch()
    print(write_note(date.today()))


if __name__ == "__main__":
    main(sys.argv[1:])
