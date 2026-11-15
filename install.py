#!/usr/bin/env python3
"""Link this repo into ~/.claude. Dry run by default.

  ./install.py                 show what would change
  ./install.py --apply         do it
  ./install.py --apply --copy-agents   copy agent files instead of linking them
  ./install.py --uninstall [--apply]   remove links and the hook entries this repo added
"""
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
CLAUDE = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
SETTINGS = CLAUDE / "settings.json"
FRAGMENT = REPO / "settings" / "user.fragment.json"
MARK = "/.claude/devkit/"
APPLY = "--apply" in sys.argv
UNINSTALL = "--uninstall" in sys.argv
COPY_AGENTS = "--copy-agents" in sys.argv
rows = []


def row(kind, name, result, note=""):
    rows.append((kind, name, result, note))


def items():
    yield "link", CLAUDE / "devkit", REPO
    for d in sorted((REPO / "skills").iterdir()):
        if (d / "SKILL.md").exists():
            yield "skill", CLAUDE / "skills" / d.name, d
    for kind, folder in (("agent", "agents"), ("rule", "rules"), ("style", "output-styles")):
        for f in sorted((REPO / folder).glob("*.md")):
            yield kind, CLAUDE / folder / f.name, f


def ours(dst, src):
    return dst.is_symlink() and Path(os.readlink(dst)) == src


def link(kind, dst, src):
    copy = kind == "agent" and COPY_AGENTS
    if ours(dst, src):
        return row(kind, dst.name, "in sync")
    if copy and dst.is_file() and not dst.is_symlink() and dst.read_bytes() == src.read_bytes():
        return row(kind, dst.name, "in sync", "copy")
    if dst.exists() or dst.is_symlink():
        if not (copy and dst.is_file() and not dst.is_symlink()):
            return row(kind, dst.name, "skipped", f"{dst} already exists and is not ours")
    if APPLY:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if copy:
            shutil.copyfile(src, dst)
        else:
            dst.symlink_to(src)
    verb = "copied" if copy else "linked"
    row(kind, dst.name, verb if APPLY else f"would {verb[:-2] if copy else 'link'}", f"-> {src}")


def unlink(kind, dst, src):
    if ours(dst, src):
        if APPLY:
            dst.unlink()
        return row(kind, dst.name, "removed" if APPLY else "would remove")
    row(kind, dst.name, "skipped", "not a link to this repo")


def hook_commands(entry):
    return [h.get("command", "") for h in entry.get("hooks", [])]


def merge_settings():
    current = json.loads(SETTINGS.read_text()) if SETTINGS.exists() else {}
    merged = json.loads(json.dumps(current))
    fragment = json.loads(FRAGMENT.read_text())
    changes = []

    deny = merged.setdefault("permissions", {}).setdefault("deny", [])
    for rule in fragment["permissions"]["deny"]:
        if UNINSTALL:
            continue
        if rule not in deny:
            deny.append(rule)
            changes.append(("deny", rule, "add"))

    hooks = merged.setdefault("hooks", {})
    for event, entries in fragment["hooks"].items():
        have = hooks.setdefault(event, [])
        if UNINSTALL:
            keep = [e for e in have if not any(MARK in c for c in hook_commands(e))]
            if len(keep) != len(have):
                changes.append(("hook", event, "remove"))
            hooks[event] = keep
            if not keep:
                del hooks[event]
            continue
        existing = {c for e in have for c in hook_commands(e)}
        for entry in entries:
            if not set(hook_commands(entry)) <= existing:
                have.append(entry)
                changes.append(("hook", event, "add"))
    if not merged["hooks"]:
        del merged["hooks"]

    if not changes:
        return row("settings", SETTINGS.name, "in sync")
    backup = ""
    if APPLY:
        if SETTINGS.exists():
            backup = f"{SETTINGS}.devkit-bak-{datetime.now():%Y%m%d-%H%M%S}"
            shutil.copy2(SETTINGS, backup)
        SETTINGS.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    for kind, name, action in changes:
        done = {"add": "added", "remove": "removed"}[action]
        row(kind, name, done if APPLY else f"would {action}", f"backup: {backup}" if backup else "")


def main():
    print(f"repo:   {REPO}")
    print(f"target: {CLAUDE}")
    mode = "APPLY" if APPLY else "DRY RUN (nothing is written)"
    print(f"mode:   {mode}{' / UNINSTALL' if UNINSTALL else ''}\n")
    for kind, dst, src in items():
        (unlink if UNINSTALL else link)(kind, dst, src)
    merge_settings()
    w = [max(len(r[i]) for r in rows) for i in range(3)]
    for r in rows:
        print(f"{r[0]:<{w[0]}}  {r[1]:<{w[1]}}  {r[2]:<{w[2]}}  {r[3]}".rstrip())
    counts = {}
    for r in rows:
        counts[r[2]] = counts.get(r[2], 0) + 1
    print("\n" + ", ".join(f"{n} {k}" for k, n in counts.items()))
    if not APPLY:
        print("Nothing was changed. Run again with --apply.")


if __name__ == "__main__":
    main()
