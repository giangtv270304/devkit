import json
import shutil
import unittest

from support import REPO, TempDirCase, run

GUARD = str(REPO / "hooks" / "bash-guard.sh")
CWD = "/work/repo"

BLOCKED = [
    "git push --force",
    "git push -f origin main",
    "git push origin main --force",
    "git -C /x push -fu origin main",
    "rm -rf /",
    "rm -rf ~",
    "rm -rf $HOME",
    "rm -rf ..",
    "rm -fr src",
    "rm -r -f /Users/me/project",
    "rm -rf /tmp",
    "rm -rf /tmp/../etc",
    "rm -rf node_modules/../src",
    "cd x && git reset --hard HEAD~1",
    "git clean -fd",
    "git clean -fdx",
    "git clean -f -d",
    "cat .env",
    "head -n 3 apps/api/.env.production",
    "grep KEY .env.local",
    "source .env",
    ". .env",
    "echo hi; cat .env",
    "ls | sed s/a/b/ .env",
    "cat < .env",
    "FOO=1 sudo rm -rf /var/data",
    "/bin/rm -rf /usr/local",
]

ALLOWED = [
    "git push",
    "git push --force-with-lease origin feat",
    "git push -u origin feat",
    'git commit -m "remove rm -rf and git push --force"',
    "echo 'git reset --hard'",
    "rm -rf /tmp/build-123",
    "rm -rf /private/tmp/x/y",
    "rm -rf $TMPDIR/cache",
    "rm -rf node_modules",
    "rm -rf ./dist",
    "rm -rf packages/web/build",
    "rm -rf src/__pycache__",
    "rm -rf /work/repo/dist",
    "rm -rf .claude/worktrees/feat-a",
    "rm file.txt",
    "rm -r build_old_notes.txt",
    "git reset --soft HEAD~1",
    "git clean -n",
    "git clean -f",
    "cat .env.example",
    "cat .env.sample .env.template",
    "cp .env.example .env",
    "grep -r TOKEN src/",
    "cat environment.md",
    "cat README.md | grep env",
]


@unittest.skipUnless(shutil.which("jq"), "jq not installed")
class BashGuardTest(TempDirCase):
    def guard(self, command):
        payload = {"tool_name": "Bash", "cwd": CWD, "tool_input": {"command": command}}
        return run(["bash", GUARD], input=json.dumps(payload), env={"TMPDIR": str(self.tmp) + "/"})

    def test_blocked_commands(self):
        for command in BLOCKED:
            with self.subTest(command=command):
                out = self.guard(command)
                self.assertEqual(out.returncode, 2, out.stderr)
                self.assertEqual(len(out.stderr.strip().splitlines()), 1)
                self.assertTrue(out.stderr.startswith("bash-guard:"))

    def test_allowed_commands(self):
        for command in ALLOWED:
            with self.subTest(command=command):
                out = self.guard(command)
                self.assertEqual(out.returncode, 0, out.stderr)

    def test_real_tmpdir_is_allowed(self):
        self.assertEqual(self.guard(f"rm -rf {self.tmp}/sub").returncode, 0)

    def test_empty_input_is_allowed(self):
        self.assertEqual(run(["bash", GUARD], input="{}").returncode, 0)


if __name__ == "__main__":
    unittest.main()
