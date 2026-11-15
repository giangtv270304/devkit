"""Read `<project root>/.claude/project.md` (Key: value lines). Shared by the devkit scripts; keep it stdlib only."""
import os
import re
from pathlib import Path

DEFAULTS = {
    "layout": "",
    "task dir": "",
    "notes dir": "docs/notes",
    "context state": ".claude/context-state.json",
}


def root():
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def config(base=None):
    base = base or root()
    cfg = dict(DEFAULTS)
    f = base / ".claude" / "project.md"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                break
            m = re.match(r"^([A-Za-z][A-Za-z ]+):\s*(.*)$", line)
            if m and m.group(2).strip():
                cfg[m.group(1).strip().lower()] = m.group(2).strip()
    if not cfg["layout"]:
        cfg["layout"] = "single-repo" if (base / ".git").exists() else "multi-repo"
    if not cfg["task dir"]:
        cfg["task dir"] = "work" if (base / "work").is_dir() else ".claude/work"
    return cfg


def repos(base=None, cfg=None):
    base = base or root()
    cfg = cfg or config(base)
    if cfg["layout"] == "single-repo":
        return ["."] if (base / ".git").exists() else []
    return sorted(p.name for p in base.iterdir() if (p / ".git").exists())


def repo_path(name, base=None):
    base = base or root()
    p = base / name
    if (p / ".git").exists():
        return p
    if (base / ".git").exists() and name in (".", base.name):
        return base
    return p
