import unittest

from support import REPO, TempDirCase, run

HOOK = str(REPO / "git-local" / "commit-msg")


class CommitMsgTest(TempDirCase):
    def check(self, message, env=None):
        path = self.tmp / "MSG"
        path.write_text(message)
        return run(["bash", HOOK, str(path)], env=env)

    def test_accepts_one_typed_line(self):
        self.assertEqual(self.check("fix(auth): reject expired refresh token\n").returncode, 0)

    def test_accepts_type_without_scope(self):
        self.assertEqual(self.check("chore: bump deps\n").returncode, 0)

    def test_rejects_unknown_type(self):
        out = self.check("wip: stuff\n")
        self.assertEqual(out.returncode, 1)
        self.assertIn("expected type(scope): what", out.stderr)

    def test_rejects_subject_over_72(self):
        out = self.check("feat: " + "x" * 70 + "\n")
        self.assertEqual(out.returncode, 1)
        self.assertIn("max 72", out.stderr)

    def test_accepts_subject_of_exactly_72(self):
        self.assertEqual(self.check("feat: " + "x" * 66 + "\n").returncode, 0)

    def test_rejects_body(self):
        out = self.check("feat: add thing\n\nmore detail\n")
        self.assertEqual(out.returncode, 1)
        self.assertIn("one line only", out.stderr)

    def test_body_allowed_with_env(self):
        out = self.check("feat: add thing\n\nmore detail\n", env={"DEVKIT_COMMIT_BODY": "1"})
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_body_env_does_not_skip_type_check(self):
        out = self.check("oops\n\nbody\n", env={"DEVKIT_COMMIT_BODY": "1"})
        self.assertEqual(out.returncode, 1)

    def test_rejects_ai_attribution(self):
        for line in (
            "Co-Authored-By: Claude <noreply@anthropic.com>",
            "Generated with [Claude Code](https://claude.com/claude-code)",
        ):
            out = self.check(f"feat: add thing\n\n{line}\n", env={"DEVKIT_COMMIT_BODY": "1"})
            self.assertEqual(out.returncode, 1, line)
            self.assertIn("AI attribution", out.stderr)

    def test_bypasses_merge_and_fixup(self):
        for subject in ("Merge branch 'x'", "Revert \"feat: a\"", "fixup! feat: a", "squash! feat: a"):
            self.assertEqual(self.check(subject + "\n").returncode, 0, subject)

    def test_ignores_comment_lines(self):
        self.assertEqual(self.check("fix: a thing\n# Please enter the commit message\n").returncode, 0)


if __name__ == "__main__":
    unittest.main()
