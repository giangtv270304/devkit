import json
import sys

from support import REPO, TempDirCase, run

SCRIPT = REPO / "skills" / "retro" / "signals.py"
FAKE_TOKEN = "gh" + "p_" + "ABCDEFGHIJKLMNOP1234"


def entry(kind, content, **extra):
    return json.dumps({"type": kind, "cwd": "/w", "timestamp": "2026-11-19T10:00:00Z",
                       "message": {"role": kind, "content": content}, **extra})


class RetroSignalsTest(TempDirCase):
    def write_session(self, name, lines):
        folder = self.tmp / "projects" / "p"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{name}.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def signals(self, *args):
        return run([sys.executable, str(SCRIPT), "--projects", str(self.tmp / "projects"), *args]).stdout

    def test_collects_corrections_errors_interrupts_and_reports(self):
        self.write_session("s1", [
            entry("user", "thêm endpoint mới"),
            entry("assistant", [{"type": "tool_use", "id": "u1", "name": "Bash", "input": {"command": "make lint"}}]),
            entry("user", [{"type": "tool_result", "tool_use_id": "u1", "is_error": True, "content": "exit 2"}]),
            entry("user", [{"type": "text", "text": "[Request interrupted by user for tool use]"}]),
            entry("user", "không phải, xong rồi mà"),
            entry("user", '<hc from="t3">step-1 NEEDS_REPLAN: thiếu bảng</hc>'),
            entry("user", "<system-reminder>ignored</system-reminder>"),
            entry("user", "sidechain sai", isSidechain=True),
        ])
        out = self.signals()
        self.assertIn("user       thêm endpoint mới", out)
        self.assertIn("error      Bash: make lint -> exit 2", out)
        self.assertIn("interrupt", out)
        self.assertIn("correction không phải, xong rồi mà", out)
        self.assertIn("report", out)
        self.assertNotIn("ignored", out)
        self.assertNotIn("sidechain", out)

    def test_redacts_secrets_and_emails(self):
        self.write_session("s2", [entry("user", "sai rồi, token: abc123secret, mail a.b@example.com, "
                                                f"key {FAKE_TOKEN}")])
        out = self.signals()
        self.assertNotIn("abc123secret", out)
        self.assertNotIn("example.com", out)
        self.assertNotIn(FAKE_TOKEN, out)

    def test_redacts_connection_url_and_password_variables(self):
        self.write_session("s3", [entry("user", "sai rồi, dùng postgres://app:hunter2pw@db.local:5432/x "
                                                "và PGPASSWORD='s3cr3tpw' psql")])
        out = self.signals()
        self.assertNotIn("hunter2pw", out)
        self.assertNotIn("s3cr3tpw", out)
        self.assertIn("postgres://app:<redacted>@db.local", out)

    def test_skips_sessions_without_friction_and_honours_grep(self):
        self.write_session("calm", [entry("user", "thêm endpoint mới")])
        self.write_session("other", [entry("user", "không phải task-x")])
        self.assertIn("0 sessions", self.signals("--grep", "task-y"))
        out = self.signals()
        self.assertNotIn("calm", out)
        self.assertIn("1 sessions with signals out of 2", out)

    def test_reads_task_notes(self):
        task = self.tmp / "task"
        task.mkdir()
        (task / "TASK.md").write_text("# t\nLệch kế hoạch: 2026-11-19 thêm file\n> NOTE: đừng đổi API\n",
                                      encoding="utf-8")
        (task / "log.md").write_text("step-1 BLOCKED: thiếu quyền\n", encoding="utf-8")
        out = self.signals("--task", str(task))
        self.assertIn("TASK.md:3  task       > NOTE: đừng đổi API", out)
        self.assertIn("Lệch kế hoạch: 2026-11-19", out)
        self.assertIn("log.md:1", out)
