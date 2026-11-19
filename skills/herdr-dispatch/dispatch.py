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
                    others = [o for o in terminals if o.get("terminal") != terminal and o.get("pane")]
                    others.sort(key=lambda o: opened_order(o.get("terminal")))
                    return space["id"], t.get("pane"), [o["pane"] for o in others]
    return None, None, []


def opened_order(terminal):
    # herdr-app ls lists panes by layout; terminal ids (t39, t3b, ...) grow in the order they were opened.
    try:
        return int((terminal or "")[1:], 36)
    except ValueError:
        return 0


def auto_place(lead_pane, others):
    # Herdr halves the pane it splits. Agents 1-3 make four equal columns (lead, 3, 1, 2); agents 4-6 split
    # those worker columns in opening order, agent 7 splits the lead's column last, then tabs.
    n = len(others)
    if n == 0:
        return "right", lead_pane
    if n == 1:
        return "right", others[0]
    if n == 2:
        return "right", lead_pane
    if n <= 5:
        return "down", others[n - 3]
    if n == 6:
        return "down", lead_pane
    return "tab", None


def lead_folder(terminal):
    out = subprocess.run(["hc", "get", terminal, "--json"], capture_output=True, text=True, timeout=15)
    if out.returncode != 0:
        return os.getcwd()
    d = json.loads(out.stdout)
    return (d.get("foreground") or {}).get("cwd") or d.get("cwd") or os.getcwd()


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
                   help="auto: four columns, then each column split in two (eight panes), then tabs")
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

    # Only the lead's own folder is added: the user trusted it when starting the lead, so no
    # per-session "add this directory?" prompt appears (that prompt defaults to exit).
    root = lead_folder(lead)
    created = False
    if a.worktree:
        main_repo = git(repo, "rev-parse", "--show-toplevel")
        folder, created = ensure_worktree(main_repo, a.worktree, a.base)
        where = (f"Bạn làm trong git worktree {folder}, branch {a.worktree}. "
                 f"Repo chính ở {main_repo}: chỉ đọc (TASK.md, tài liệu), không sửa, không đổi branch của nó. "
                 f"Các bước khác có thể đang chạy song song ở worktree khác.")
    else:
        folder = repo
        where = f"Bạn làm trong {folder}."
    readable = root if root and os.path.realpath(root) != os.path.realpath(folder) else None
    if readable:
        where += f" Thư mục {readable} (TASK.md, tài liệu, repo khác): chỉ đọc."
    add_dir = ["--add-dir", readable] if readable else []
    task = f"{rules} {where} Terminal điều phối: {lead}. Việc của bạn: {a.task}"

    if place == "tab":
        req = {
            "name": a.name,
            "space": space,
            "folder": folder,
            "argv": ["env", f"DEVKIT_ROLE={a.template}", "claude", *add_dir, "--"],
            "task": task,
            "focus": a.focus,
        }
        res = herdr("do", "tab.new", json.dumps(req, ensure_ascii=False))
    else:
        if not split_pane:
            sys.exit(f"could not find the pane of terminal {lead}")
        script = 'cd "$1" && export DEVKIT_ROLE="$2" && shift 2 && exec claude "$@"'
        req = {
            "direction": place,
            "pane": split_pane,
            "argv": ["sh", "-c", script, "sh", folder, a.template, *add_dir, "--", task],
        }
        res = herdr("do", "pane.split", json.dumps(req, ensure_ascii=False))
    print(json.dumps({"place": place, "terminal": res.get("terminal"), "pane": res.get("pane"),
                      "tab": res.get("tab"), "folder": folder, "worktree": bool(a.worktree),
                      "new_worktree": created, "name": a.name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
