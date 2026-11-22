import json
import shutil
import unittest

from support import REPO, TempDirCase, run

LIB = str(REPO / "hooks" / "lib" / "skip-generated.sh")
GUARD = str(REPO / "hooks" / "comment-guard.sh")


class IsGeneratedTest(unittest.TestCase):
    def is_generated(self, path):
        return run(["bash", "-c", f'. "{LIB}"; is_generated "$1"', "_", path]).returncode == 0

    def test_generated_paths(self):
        for path in (
            "/r/apispec/docs.go",
            "/r/node_modules/a/b.js",
            "/r/dist/app.js",
            "/r/mocks/m.go",
            "/r/x.generated.ts",
            "/r/store_gen.go",
            "/r/a.pb.go",
            "/r/a.gen.ts",
            "/r/types.d.ts",
            "/r/api/docs/swagger.json",
            "/r/docs/docs.go",
        ):
            self.assertTrue(self.is_generated(path), path)

    def test_hand_written_paths(self):
        for path in ("/r/main.go", "/r/internal/repo/get_widget.go", "/r/src/app.ts", "/r/README.md"):
            self.assertFalse(self.is_generated(path), path)


@unittest.skipUnless(shutil.which("jq"), "jq not installed")
class CommentGuardTest(TempDirCase):
    def guard(self, tool_input, tool="Edit", response=None):
        payload = {"tool_name": tool, "tool_input": tool_input}
        if response is not None:
            payload["tool_response"] = response
        return run(["bash", GUARD], input=json.dumps(payload))

    def edit(self, path, old, new):
        return self.guard({"file_path": path, "old_string": old, "new_string": new})

    def test_new_comment_is_blocked(self):
        out = self.edit("/r/a.go", "x := 1", "// set x\nx := 1")
        self.assertEqual(out.returncode, 2)
        self.assertIn("// set x", out.stderr)

    def test_comment_already_in_old_text_is_allowed(self):
        out = self.edit("/r/a.go", "// keep\nx := 1", "// keep\nx := 2")
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_directives_are_allowed(self):
        for line in ("//nolint:nilnil // cache miss", "//go:generate mockgen", "// @Router /widgets [post]"):
            out = self.edit("/r/a.go", "", f"{line}\nx := 1")
            self.assertEqual(out.returncode, 0, line)

    def test_doc_comment_on_exported_declaration_is_allowed(self):
        cases = [("/r/a.go", "// CreateWidget stores a widget.\nfunc (s *Service) CreateWidget() {}"),
                 ("/r/a.go", "// Widget is a thing.\ntype Widget struct{}"),
                 ("/r/a.ts", "/**\n * Lists widgets.\n */\nexport function list() {}")]
        for path, new in cases:
            with self.subTest(new=new):
                self.assertEqual(self.edit(path, "", new).returncode, 0)

    def test_comment_on_unexported_or_inside_body_is_blocked(self):
        for new in ("// helper\nfunc helper() {}", "// loop over\nfor _, x := range xs {}", "// note\n\nfunc A() {}"):
            with self.subTest(new=new):
                self.assertEqual(self.edit("/r/a.go", "", new).returncode, 2)

    def test_generated_file_is_skipped(self):
        out = self.edit("/r/a.pb.go", "", "// big comment")
        self.assertEqual(out.returncode, 0)

    def test_other_extension_is_skipped(self):
        self.assertEqual(self.edit("/r/a.py", "", "// not checked").returncode, 0)

    def test_sql_comment_is_blocked(self):
        self.assertEqual(self.edit("/r/a.sql", "", "-- note\nSELECT 1;").returncode, 2)

    def test_new_file_write_is_checked(self):
        out = self.guard(
            {"file_path": "/r/new.ts", "content": "// hi\nexport const a = 1\n"},
            tool="Write",
            response={"type": "create"},
        )
        self.assertEqual(out.returncode, 2)

    def test_write_over_existing_file_keeps_old_comments(self):
        out = self.guard(
            {"file_path": "/r/a.ts", "content": "// old\nexport const a = 2\n"},
            tool="Write",
            response={"type": "update", "originalFile": "// old\nexport const a = 1\n"},
        )
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_runs_through_symlink(self):
        link = self.tmp / "comment-guard.sh"
        link.symlink_to(GUARD)
        payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": "/r/a.go", "old_string": "", "new_string": "// c"}})
        self.assertEqual(run(["bash", str(link)], input=payload).returncode, 2)


class FormatHookTest(TempDirCase):
    def test_generated_file_is_left_alone_and_exit_zero(self):
        target = self.tmp / "a.pb.go"
        target.write_text("package   a\n")
        payload = json.dumps({"tool_input": {"file_path": str(target)}})
        out = run(["bash", str(REPO / "hooks" / "format-edited-file.sh")], input=payload)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(target.read_text(), "package   a\n")


if __name__ == "__main__":
    unittest.main()
