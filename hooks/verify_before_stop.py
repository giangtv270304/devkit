#!/usr/bin/env python3
"""Stop / SubagentStop hook: a code role (DEVKIT_ROLE worker|developer, or subagent developer|tester) may not stop
while build, vet or tests of the packages it changed are failing. Go: go build/vet/test per changed package.
Node: package.json scripts type-check/test when .ts files changed. Anything it cannot decide, it allows.
Env: DEVKIT_VERIFY=0 disables; DEVKIT_VERIFY_TIMEOUT seconds (default 240) after which it allows with a warning."""
import json
import os
import signal
import subprocess
import sys
import time

ROLES = {"worker", "developer"}
AGENTS = {"developer", "tester"}
TAIL = 20


class Timeout(Exception):
    pass


def git(cwd, *args):
    r = subprocess.run(["git", "-C", cwd, "-c", "core.quotepath=off", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def changed_files(cwd):
    top = git(cwd, "rev-parse", "--show-toplevel").strip()
    if not top:
        return None, []
    names = set(git(top, "diff", "--name-only", "HEAD").split("\n"))
    names |= set(git(top, "ls-files", "--others", "--exclude-standard").split("\n"))
    return top, sorted(n for n in names if n and os.path.exists(os.path.join(top, n)))


def run_limited(cmd, cwd, deadline):
    left = deadline - time.monotonic()
    if left <= 0:
        raise Timeout
    try:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             start_new_session=True)
    except OSError:
        return 0, ""
    try:
        out, _ = p.communicate(timeout=left)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        p.communicate()
        raise Timeout
    return p.returncode, out


def module_root(top, d):
    while True:
        if os.path.exists(os.path.join(top, d, "go.mod")):
            return d
        if not d:
            return ""
        d = os.path.dirname(d)


def go_checks(top, files):
    modules = {}
    for f in files:
        if f.endswith(".go"):
            d = os.path.dirname(f)
            root = module_root(top, d)
            modules.setdefault(root, set()).add(os.path.relpath(d, root or "."))
    checks = []
    for root in sorted(modules):
        pkgs = ["./" + d if d != "." else "." for d in sorted(modules[root])]
        where = f" (in {root})" if root else ""
        for sub in ("build", "vet", "test"):
            checks.append((f"go {sub} {' '.join(pkgs)}{where}", ["go", sub, *pkgs], os.path.join(top, root)))
    return checks


def node_checks(top, files):
    roots = set()
    for f in files:
        if not f.endswith((".ts", ".tsx")):
            continue
        d = os.path.dirname(f)
        while True:
            if os.path.exists(os.path.join(top, d, "package.json")):
                roots.add(d)
                break
            if not d:
                break
            d = os.path.dirname(d)
    checks = []
    for d in sorted(roots):
        root = os.path.join(top, d)
        try:
            with open(os.path.join(root, "package.json")) as fh:
                scripts = (json.load(fh).get("scripts") or {})
        except (OSError, ValueError):
            continue
        pm = "pnpm" if os.path.exists(os.path.join(root, "pnpm-lock.yaml")) else \
            "yarn" if os.path.exists(os.path.join(root, "yarn.lock")) else "npm"
        for name in ("type-check", "test"):
            if name in scripts:
                checks.append((f"{pm} run {name} (in {d or '.'})", [pm, "run", name], root))
    return checks


def main():
    data = json.load(sys.stdin)
    if data.get("stop_hook_active") or os.environ.get("DEVKIT_VERIFY") == "0":
        return
    if os.environ.get("DEVKIT_ROLE") not in ROLES and data.get("agent_type") not in AGENTS:
        return
    top, files = changed_files(data.get("cwd") or os.getcwd())
    if not files:
        return
    checks = go_checks(top, files) + node_checks(top, files)
    if not checks:
        return
    limit = float(os.environ.get("DEVKIT_VERIFY_TIMEOUT") or 240)
    deadline = time.monotonic() + limit
    for label, cmd, cwd in checks:
        try:
            code, out = run_limited(cmd, cwd, deadline)
        except Timeout:
            print(f"verify_before_stop: quá {limit:g}s, bỏ qua kiểm tra (lệnh dở: {label})", file=sys.stderr)
            return
        if code != 0:
            tail = "\n".join(out.rstrip().split("\n")[-TAIL:])
            print(json.dumps({"decision": "block", "reason":
                              f"`{label}` fail (exit {code}). Sửa rồi mới báo xong. {TAIL} dòng cuối:\n{tail}"},
                             ensure_ascii=False))
            return


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"verify_before_stop: {e!r}", file=sys.stderr)
