import json
import sys

from support import REPO, TempDirCase, run

HOOK = REPO / "hooks" / "plan_gate.py"


class PlanGateTest(TempDirCase):
    def setUp(self):
        super().setUp()
        task_dir = self.tmp / "work" / "demo"
        task_dir.mkdir(parents=True)
        self.task = task_dir / "TASK.md"
        self.task.write_text("# demo\n\n## Kế hoạch\n- [ ] svc: `internal/service/create_x.go`\n\n## Review\n", encoding="utf-8")
        self.transcript = self.tmp / "t.jsonl"
        self.transcript.write_text(json.dumps({"text": f"Việc của bạn: {self.task}"}) + "\n", encoding="utf-8")

    def gate(self, target, agent_type=None, role=None, command=None):
        tool_input = {"command": command} if command is not None else {"file_path": str(self.tmp / target)}
        data = {"cwd": str(self.tmp), "transcript_path": str(self.transcript), "tool_input": tool_input}
        if command is not None:
            data["tool_name"] = "Bash"
        if agent_type:
            data["agent_type"] = agent_type
        env = {"DEVKIT_ROLE": role or ""}
        return run([sys.executable, str(HOOK)], env=env, input=json.dumps(data)).stdout

    def test_worker_session_is_asked_for_file_outside_plan(self):
        self.assertIn('"ask"', self.gate("internal/service/other.go", role="worker"))

    def test_worker_session_may_edit_planned_file(self):
        self.assertEqual(self.gate("internal/service/create_x.go", role="worker"), "")

    def test_developer_subagent_is_asked(self):
        self.assertIn('"ask"', self.gate("internal/repo/x.go", agent_type="developer"))

    def test_plain_session_is_not_gated(self):
        self.assertEqual(self.gate("internal/repo/x.go"), "")

    def test_reviewer_role_is_not_gated(self):
        self.assertEqual(self.gate("internal/repo/x.go", role="reviewer"), "")

    def test_generated_swagger_is_not_gated(self):
        self.assertEqual(self.gate("api/docs/swagger.json", role="worker"), "")
        self.assertEqual(self.gate("internal/mocks/repo.go", role="worker"), "")

    def test_bash_write_outside_plan_is_asked(self):
        for cmd in ("echo x > internal/repo/x.go", "sed -i '' s/a/b/ internal/repo/x.go", "printf y | tee -a cfg/app.yaml"):
            with self.subTest(cmd=cmd):
                self.assertIn('"ask"', self.gate(None, role="worker", command=cmd))

    def test_bash_read_or_planned_write_is_not_gated(self):
        for cmd in ("go test ./... 2>&1 | tail", "cat a.go > /dev/null", "echo x > internal/service/create_x.go",
                    "go build -o /tmp/bin ./... > /tmp/out.log", "ls >&2"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.gate(None, role="worker", command=cmd), "")
