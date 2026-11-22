import json
import os
import stat
import subprocess
import sys
import time

from support import REPO, TempDirCase, run

HOOK = REPO / "hooks" / "verify_before_stop.py"


class VerifyBeforeStopTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.repo = self.tmp / "repo"
        self.bin = self.tmp / "bin"
        self.repo.mkdir()
        self.bin.mkdir()
        self.git("init", "-q")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init")

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def fake(self, name, body):
        p = self.bin / name
        p.write_text("#!/bin/sh\n" + body + "\n")
        p.chmod(p.stat().st_mode | stat.S_IEXEC)

    def write(self, rel, text="x"):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def hook(self, role="worker", agent_type=None, active=False, last=None, **env):
        data = {"cwd": str(self.repo), "stop_hook_active": active}
        if last is not None:
            data["last_assistant_message"] = last
        if agent_type:
            data["agent_type"] = agent_type
        full = {"DEVKIT_ROLE": role, "PATH": f"{self.bin}:{os.environ['PATH']}", "DEVKIT_VERIFY": ""}
        full.update(env)
        return run([sys.executable, str(HOOK)], env=full, input=json.dumps(data))

    def failing_go(self):
        self.fake("go", 'for i in $(seq 1 30); do echo "line $i"; done; echo "boom $1"; exit 1')
        self.write("svc/a.go", "package svc")

    # 1
    def test_go_failure_blocks_with_last_20_lines(self):
        self.failing_go()
        r = self.hook()
        out = json.loads(r.stdout)
        self.assertEqual(out["decision"], "block")
        self.assertIn("go build ./svc", out["reason"])
        self.assertIn("boom build", out["reason"])
        self.assertNotIn("line 1\n", out["reason"])
        self.assertEqual(out["reason"].split("\n", 1)[1].count("\n") + 1, 20)

    def test_go_only_changed_packages_and_all_three_commands(self):
        self.fake("go", 'echo "$@" >> "$GOLOG"; exit 0')
        self.write("svc/a.go")
        self.write("other/b.go")
        self.git("add", "other/b.go")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
        self.write("svc/c.go")
        log = self.tmp / "go.log"
        r = self.hook(GOLOG=str(log))
        self.assertEqual(r.stdout, "")
        self.assertEqual(log.read_text().split("\n")[:3], ["build ./svc", "vet ./svc", "test ./svc"])

    def test_developer_subagent_and_tester_are_checked(self):
        self.failing_go()
        for kind in ("developer", "tester"):
            self.assertIn("block", self.hook(role="", agent_type=kind).stdout)

    def test_tester_skips_go_test_so_new_failing_tests_can_stop(self):
        self.fake("go", 'echo "$@" >> "$GOLOG"; [ "$1" = test ] && exit 1; exit 0')
        self.write("svc/a_test.go", "package svc")
        log = self.tmp / "go.log"
        r = self.hook(role="", agent_type="tester", GOLOG=str(log))
        self.assertEqual(r.stdout, "")
        self.assertEqual(log.read_text().split("\n")[:2], ["build ./svc", "vet ./svc"])
        self.assertNotIn("test ./svc", log.read_text())

    def test_needs_replan_or_blocked_report_is_let_through(self):
        self.failing_go()
        for last in ("NEEDS_REPLAN: plan misses config.go", "`BLOCKED`: no DB url"):
            self.assertEqual(self.hook(last=last).stdout, "")
        self.assertIn("block", self.hook(last="DONE: all green").stdout)

    def test_report_status_read_from_transcript(self):
        self.failing_go()
        tr = self.tmp / "t.jsonl"
        tr.write_text(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "BLOCKED: x"}]}}) + "\n")
        data = {"cwd": str(self.repo), "transcript_path": str(tr)}
        env = {"DEVKIT_ROLE": "worker", "PATH": f"{self.bin}:{os.environ['PATH']}", "DEVKIT_VERIFY": ""}
        r = run([sys.executable, str(HOOK)], env=env, input=json.dumps(data))
        self.assertEqual(r.stdout, "")

    def test_developer_role_is_checked(self):
        self.failing_go()
        self.assertIn("block", self.hook(role="developer").stdout)

    # 2
    def test_allows_when_stop_hook_active(self):
        self.failing_go()
        self.assertEqual(self.hook(active=True).stdout, "")

    def test_allows_when_nothing_changed(self):
        self.fake("go", "exit 1")
        self.assertEqual(self.hook().stdout, "")

    def test_allows_when_only_non_code_changed(self):
        self.fake("go", "exit 1")
        self.write("README.md")
        self.assertEqual(self.hook().stdout, "")

    def test_allows_when_disabled(self):
        self.failing_go()
        self.assertEqual(self.hook(DEVKIT_VERIFY="0").stdout, "")

    def test_allows_for_other_roles(self):
        self.failing_go()
        self.assertEqual(self.hook(role="reviewer").stdout, "")
        self.assertEqual(self.hook(role="").stdout, "")
        self.assertEqual(self.hook(role="", agent_type="reviewer").stdout, "")

    # 3
    def node_repo(self, scripts):
        self.write("package.json", json.dumps({"scripts": scripts}))
        self.write("src/a.ts")

    def test_node_runs_type_check_and_test(self):
        self.node_repo({"type-check": "tsc", "test": "jest"})
        self.fake("npm", 'echo "$@" >> "$NPMLOG"; [ "$2" = test ] && { echo "jest red"; exit 1; }; exit 0')
        log = self.tmp / "npm.log"
        out = json.loads(self.hook(NPMLOG=str(log)).stdout)
        self.assertEqual(log.read_text().split("\n")[:2], ["run type-check", "run test"])
        self.assertIn("npm run test", out["reason"])
        self.assertIn("jest red", out["reason"])

    def test_node_without_scripts_passes(self):
        self.node_repo({"build": "x"})
        self.fake("npm", "exit 1")
        self.assertEqual(self.hook().stdout, "")

    def test_node_uses_pnpm_when_lockfile(self):
        self.node_repo({"test": "jest"})
        self.write("pnpm-lock.yaml")
        self.fake("pnpm", "echo pnpm red; exit 1")
        self.assertIn("pnpm run test", json.loads(self.hook().stdout)["reason"])

    def test_node_ignores_when_no_ts_changed(self):
        self.write("package.json", json.dumps({"scripts": {"test": "x"}}))
        self.write("a.md")
        self.fake("npm", "exit 1")
        self.assertEqual(self.hook().stdout, "")

    # 4
    def test_timeout_allows_with_warning(self):
        self.fake("go", "sleep 30")
        self.write("svc/a.go")
        start = time.monotonic()
        r = self.hook(DEVKIT_VERIFY_TIMEOUT="1")
        self.assertLess(time.monotonic() - start, 10)
        self.assertEqual(r.stdout, "")
        self.assertIn("bỏ qua kiểm tra", r.stderr)

    def test_go_runs_per_module_in_nearest_go_mod_dir(self):
        self.fake("go", 'echo "$(basename $PWD): $@" >> "$GOLOG"; exit 0')
        self.write("a/go.mod")
        self.write("a/x/one.go")
        self.write("b/go.mod")
        self.write("b/two.go")
        log = self.tmp / "go.log"
        self.assertEqual(self.hook(GOLOG=str(log)).stdout, "")
        lines = log.read_text().split("\n")
        self.assertEqual(lines[:3], ["a: build ./x", "a: vet ./x", "a: test ./x"])
        self.assertEqual(lines[3:6], ["b: build .", "b: vet .", "b: test ."])

    def test_non_ascii_file_name_is_not_dropped(self):
        self.failing_go()
        (self.repo / "svc" / "a.go").unlink()
        self.write("svc/tên.go")
        self.git("add", "svc/tên.go")
        self.assertIn("go build ./svc", json.loads(self.hook().stdout)["reason"])
