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

    def gate(self, target, agent_type=None, role=None):
        data = {"cwd": str(self.tmp), "transcript_path": str(self.transcript),
                "tool_input": {"file_path": str(self.tmp / target)}}
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
