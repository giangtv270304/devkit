#!/usr/bin/env python3
"""Start claude with a worker task in the lead's Herdr space: as a new tab, or as a pane beside the lead.

Usage: dispatch.py <repo_dir> <name> <task> [--place tab|right|down] [--template NAME] [--focus]
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


def find_lead(terminal):
    for space in herdr("ls").get("spaces", []):
        for tab in space.get("tabs", []):
            for t in tab.get("terminals", []):
                if t.get("terminal") == terminal:
                    return space["id"], t.get("pane")
    return None, None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("repo_dir")
    p.add_argument("name")
    p.add_argument("task")
    p.add_argument("--place", choices=["tab", "right", "down"], default="tab")
    p.add_argument("--template", default="worker")
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
    space, lead_pane = find_lead(lead)
    if not space:
        sys.exit(f"could not find the space of terminal {lead}")

    with open(template, encoding="utf-8") as f:
        body = f.read()
    if body.startswith("---"):
        body = body.split("---", 2)[2]
    rules = " ".join(line.strip() for line in body.strip().splitlines() if line.strip())
    task = f"{rules} Terminal điều phối: {lead}. Việc của bạn: {a.task}"
    workspace = os.path.dirname(repo)

    if a.place == "tab":
        req = {
            "name": a.name,
            "space": space,
            "folder": repo,
            "argv": ["claude", "--add-dir", workspace, "--"],
            "task": task,
            "focus": a.focus,
        }
        res = herdr("do", "tab.new", json.dumps(req, ensure_ascii=False))
    else:
        if not lead_pane:
            sys.exit(f"could not find the pane of terminal {lead}")
        req = {
            "direction": a.place,
            "pane": lead_pane,
            "argv": ["sh", "-c", 'cd "$1" && exec claude --add-dir "$2" -- "$3"', "sh", repo, workspace, task],
        }
        res = herdr("do", "pane.split", json.dumps(req, ensure_ascii=False))
    print(json.dumps({"place": a.place, "terminal": res.get("terminal"), "pane": res.get("pane"),
                      "tab": res.get("tab"), "repo": repo, "name": a.name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
