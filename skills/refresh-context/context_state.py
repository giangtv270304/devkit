#!/usr/bin/env python3
"""Track which repo commits the project context (CLAUDE.md, docs, notes) was written against.

Silent in projects that never ran `record` (no state file), so it is safe as a user-level SessionStart hook.

check  (SessionStart hook): print repos and docs/notes whose code moved since they were last surveyed.
record [repo ...]: mark repos (default: all) as surveyed at their current HEAD.
"""
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "work"))
import project  # noqa: E402

ROOT = project.root()
CFG = project.config(ROOT)
STATE = ROOT / CFG["context state"]
NOTES = ROOT / CFG["notes dir"]
MAX_LINES = 30


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(project.repo_path(repo, ROOT)), *args], capture_output=True, text=True, timeout=10)
    return r.stdout.strip() if r.returncode == 0 else None


def repos():
    return project.repos(ROOT, CFG)


def based_on_docs():
    """Markdown files whose `based_on:` frontmatter is checked: the notes dir, or the files and dirs in `Based-on docs`."""
    targets = [t.strip() for t in CFG.get("based-on docs", "").split(",") if t.strip()] or [CFG["notes dir"]]
    found = []
    for t in targets:
        p = ROOT / t
        if p.is_file():
            found.append(p)
        elif p.is_dir():
            found.extend(sorted(p.rglob("*.md")))
    return found


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def changes(repo, sha):
    head = git(repo, "rev-parse", "HEAD")
    if not head or head.startswith(sha) or not sha:
        return None
    commits = git(repo, "rev-list", "--count", f"{sha}..HEAD")
    files = git(repo, "diff", "--name-only", sha, "HEAD")
    if files is None:
        return {"commits": commits or "?", "areas": "base commit not found locally (fetch?)"}
    if not files:
        return None
    top = Counter("/".join(f.split("/")[:2]) if f.count("/") > 1 else f for f in files.splitlines())
    areas = ", ".join(f"{a} ({n})" for a, n in top.most_common(4))
    return {"commits": commits or "?", "areas": areas, "files": len(files.splitlines())}


def check():
    if not STATE.exists():
        return
    state = load()
    lines = []
    for repo in repos():
        entry = state.get(repo)
        if not entry:
            lines.append(f"- {repo}: never surveyed (no context state); run refresh-context before relying on its CLAUDE.md")
            continue
        c = changes(repo, entry["sha"])
        if c:
            branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
            moved = f" (now on {branch}, surveyed on {entry['branch']})" if branch != entry["branch"] else ""
            lines.append(f"- {repo}: {c['commits']} commits since {entry['refreshed_at'][:10]}{moved}; changed {c['areas']}")
    for note in based_on_docs():
        m = re.search(r"^based_on:\s*(.+)$", note.read_text(), re.M)
        if not m:
            continue
        stale = []
        for ref in m.group(1).split(","):
            repo, _, sha = ref.strip().partition("@")
            if (project.repo_path(repo, ROOT) / ".git").exists() and changes(repo, sha):
                stale.append(repo)
        if stale:
            lines.append(f"- {note.relative_to(ROOT)}: code changed in {', '.join(stale)} since it was written; verify before trusting it")
    if lines:
        print("Project context drift (CLAUDE.md / docs written before these changes). Re-read only the changed areas, "
              "and offer to run refresh-context for these repos:")
        print("\n".join(lines[:MAX_LINES]))
        if len(lines) > MAX_LINES:
            print(f"- ...and {len(lines) - MAX_LINES} more")


def record(targets):
    state = load()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for repo in targets or repos():
        sha = git(repo, "rev-parse", "--short", "HEAD")
        if not sha:
            print(f"skip {repo}: not a git repo")
            continue
        state[repo] = {"sha": sha, "branch": git(repo, "rev-parse", "--abbrev-ref", "HEAD"), "refreshed_at": now}
        print(f"recorded {repo}@{sha}")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(dict(sorted(state.items())), indent=2) + "\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "record":
        record(sys.argv[2:])
    else:
        try:
            check()
        except Exception as e:
            print(f"(context drift check skipped: {e})")
