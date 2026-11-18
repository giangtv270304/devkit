#!/usr/bin/env python3
"""Start claude with a worker task in the lead's Herdr space: as a new tab, or as a pane beside the lead.

Usage:
  dispatch.py <repo_dir> <name> <task> [--place tab|right|down] [--template NAME] [--focus]
  dispatch.py <repo_dir> <name> <task> --worktree <branch> [--base REF] [...]

Without --worktree the agent works in <repo_dir> and may read its parent folder (a folder of repos).
With --worktree the agent works in a git worktree of <repo_dir> on <branch> and may read only the main checkout.
"""
import argparse
import json
import os
import subprocess
import sys


def herdr(*args):
    out = subprocess.run(["herdr-app", *args], capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        sys.exit(f"herdr-app {' '.join(args[:2])} failed: {out.stderr.strip() or out.stdout.strip()}")
    return json.loads(out.stdout)


def git(repo, *args):
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        sys.exit(f"git {' '.join(args[:2])} failed: {out.stderr.strip() or out.stdout.strip()}")
    return out.stdout.strip()


def find_lead(terminal):
    for space in herdr("ls").get("spaces", []):
        for tab in space.get("tabs", []):
            terminals = tab.get("terminals", [])
            for t in terminals:
                if t.get("terminal") == terminal:
                    others = [o.get("pane") for o in terminals if o.get("terminal") != terminal and o.get("pane")]
                    return space["id"], t.get("pane"), others
    return None, None, []


def auto_place(lead_pane, others):
    # Herdr halves the pane it splits, so this order ends with four equal columns.
    if not others:
        return "right", lead_pane
    if len(others) == 1:
        return "right", others[0]
    if len(others) == 2:
        return "right", lead_pane
    return "tab", None


def worktrees_root():
    try:
        with open(os.path.expanduser("~/.config/herdr-app/settings.json"), encoding="utf-8") as f:
            d = json.load(f)
        configured = (d.get("worktrees") or {}).get("directory")
    except (OSError, ValueError):
        configured = None
    return os.path.expanduser(configured or "~/.herdr/worktrees")


def ensure_worktree(main, branch, base):
    for block in git(main, "worktree", "list", "--porcelain").split("\n\n"):
        lines = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
        if lines.get("branch") == f"refs/heads/{branch}":
            return lines["worktree"], False
    path = os.path.join(worktrees_root(), os.path.basename(main), branch.replace("/", "-"))
    if os.path.exists(path):
        sys.exit(f"{path} exists but is not a worktree of branch {branch}; pick another branch or remove it")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    exists = subprocess.run(["git", "-C", main, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
                            capture_output=True).returncode == 0
    if exists:
        git(main, "worktree", "add", path, branch)
    else:
        git(main, "worktree", "add", "-b", branch, path, base)
    return path, True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("repo_dir")
    p.add_argument("name")
    p.add_argument("task")
    p.add_argument("--place", choices=["auto", "tab", "right", "down"], default="auto",
                   help="auto: up to three agents as columns beside the lead, then tabs")
    p.add_argument("--template", default="worker")
    p.add_argument("--worktree", metavar="BRANCH")
    p.add_argument("--base", default="HEAD", help="where a new worktree branch starts (default: HEAD of repo_dir)")
    p.add_argument("--focus", action="store_true")
    a = p.parse_args()

    lead = os.environ.get("HC_TERMINAL_ID")
    if not lead:
        sys.exit("not inside a Herdr terminal (HC_TERMINAL_ID is unset)")
    repo = os.path.realpath(os.path.expanduser(a.repo_dir))
    if not os.path.isdir(repo):
        sys.exit(f"no such folder: {repo}")
    template = os.path.expanduser(f"~/.config/herdr-core/templates/{a.template}.md")
    if not os.path.isfile(template):
        sys.exit(f"no template: {template}")
    space, lead_pane, other_panes = find_lead(lead)
    if not space:
        sys.exit(f"could not find the space of terminal {lead}")
    place, split_pane = a.place, lead_pane
    if place == "auto":
        place, split_pane = auto_place(lead_pane, other_panes)

    with open(template, encoding="utf-8") as f:
        body = f.read()
    if body.startswith("---"):
        body = body.split("---", 2)[2]
    rules = " ".join(line.strip() for line in body.strip().splitlines() if line.strip())

    created = False
    if a.worktree:
        main_repo = git(repo, "rev-parse", "--show-toplevel")
        folder, created = ensure_worktree(main_repo, a.worktree, a.base)
        readable = main_repo
        where = (f"Bạn làm trong git worktree {folder}, branch {a.worktree}. "
                 f"Repo chính ở {main_repo}: chỉ đọc (TASK.md, tài liệu), không sửa, không đổi branch của nó. "
                 f"Các bước khác có thể đang chạy song song ở worktree khác.")
    else:
        folder = repo
        readable = os.path.dirname(repo)
        where = f"Bạn làm trong repo {folder}. Thư mục {readable} chứa các repo khác: chỉ đọc."
    task = f"{rules} {where} Terminal điều phối: {lead}. Việc của bạn: {a.task}"

    if place == "tab":
        req = {
            "name": a.name,
            "space": space,
            "folder": folder,
            "argv": ["claude", "--add-dir", readable, "--"],
            "task": task,
            "focus": a.focus,
        }
        res = herdr("do", "tab.new", json.dumps(req, ensure_ascii=False))
    else:
        if not split_pane:
            sys.exit(f"could not find the pane of terminal {lead}")
        req = {
            "direction": place,
            "pane": split_pane,
            "argv": ["sh", "-c", 'cd "$1" && exec claude --add-dir "$2" -- "$3"', "sh", folder, readable, task],
        }
        res = herdr("do", "pane.split", json.dumps(req, ensure_ascii=False))
    print(json.dumps({"place": place, "terminal": res.get("terminal"), "pane": res.get("pane"),
                      "tab": res.get("tab"), "folder": folder, "worktree": bool(a.worktree),
                      "new_worktree": created, "name": a.name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
