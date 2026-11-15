#!/usr/bin/env python3
"""Print a markdown table of tasks in work/: phase, date, what the user must do, git state."""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project  # noqa: E402

ROOT = project.root()
WORK = ROOT / project.config(ROOT)["task dir"]
LEGACY_NEXT = ("việc tiếp theo", "tiếp theo", "next")
BRANCH_LINE = re.compile(r"^\s*[-*]\s*`?([\w.-]+)`?\s*:\s*`?([\w./-]+)`?")


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def sections(text):
    out, name = {}, ""
    out[name] = []
    for line in text.splitlines():
        if line.startswith("## "):
            name = line[3:].strip().lower()
            out[name] = []
        else:
            out[name].append(line)
    return out


def clip(s, n=100):
    return s if len(s) <= n else s[: n - 3] + "..."


def first_item(lines):
    for line in lines:
        s = line.strip()
        if s and not s.startswith("<!--"):
            return clip(re.sub(r"^[-*]\s+", "", s))
    return ""


def field(text, *names):
    for n in names:
        m = re.search(rf"^[-*\s]*{n}:\s*(.+)$", text, re.M)
        if m:
            return m.group(1).strip()
    return ""


def branch_state(repo_name, branch):
    repo = project.repo_path(repo_name, ROOT)
    if not (repo / ".git").exists():
        return f"{repo_name}: không thấy repo"
    if git(repo, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}") is None:
        if git(repo, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{branch}") is not None:
            return f"{repo_name}@{branch}: chỉ có trên origin"
        return f"{repo_name}@{branch}: không có branch"
    parts = []
    if git(repo, "symbolic-ref", "--short", "HEAD") == branch:
        dirty = git(repo, "status", "--porcelain", "--untracked-files=no")
        if dirty:
            parts.append(f"{len(dirty.splitlines())} file chưa commit")
    ahead = git(repo, "rev-list", "--count", f"refs/heads/{branch}@{{upstream}}..refs/heads/{branch}")
    if ahead is None:
        ahead = git(repo, "rev-list", "--count", f"refs/remotes/origin/{branch}..refs/heads/{branch}")
    if ahead is None:
        parts.append("chưa có trên origin")
    elif ahead != "0":
        parts.append(f"{ahead} commit chưa push")
    return f"{repo_name}@{branch}: " + (", ".join(parts) or "sạch")


def branches_from(lines):
    return [branch_state(m.group(1), m.group(2)) for m in map(BRANCH_LINE.match, lines) if m]


def task_row(d):
    task = d / "TASK.md"
    if task.exists():
        text = task.read_text(encoding="utf-8")
        secs = sections(text)
        head = secs[""]
        try:
            i = next(n for n, l in enumerate(head) if l.startswith("Branch:"))
            blines = []
            for l in head[i + 1 :]:
                if not BRANCH_LINE.match(l):
                    break
                blines.append(l)
        except StopIteration:
            blines = []
        need = field("\n".join(secs.get("tóm tắt", [])), "CẦN BẠN") or "?"
        return d.name, field(text, "Phase") or "?", field(text, "Cập nhật"), clip(need), "; ".join(branches_from(blines)) or "chưa ghi branch"
    ctx = d / "CONTEXT.md"
    if not ctx.exists():
        return d.name, "intent", "", "(mẫu cũ) chưa có CONTEXT.md", ""
    text = ctx.read_text(encoding="utf-8")
    secs = sections(text)
    nxt = next((first_item(secs[h]) for h in LEGACY_NEXT if h in secs), "")
    return d.name, field(text, "Phase") or "?", field(text, "Cập nhật", "Updated"), "(mẫu cũ) " + nxt, "; ".join(branches_from(secs.get("branch", []))) or "chưa ghi branch"


def main():
    if not WORK.is_dir():
        print(f"Không có thư mục task: {WORK}")
        return
    rows = [task_row(d) for d in sorted(WORK.iterdir()) if d.is_dir()]
    rows.sort(key=lambda r: r[2], reverse=True)
    rows.sort(key=lambda r: r[1] == "done")
    print("| Task | Phase | Cập nhật | Cần bạn | Git |")
    print("|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(c.replace("|", "\\|") for c in r) + " |")


if __name__ == "__main__":
    main()
