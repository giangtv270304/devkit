import json
import sys
import unittest

from support import REPO, run

HOOK = REPO / "hooks" / "herdr_agent_gate.py"


class HerdrAgentGateTest(unittest.TestCase):
    def gate(self, subagent_type, terminal="t1", role=""):
        data = {"tool_name": "Agent", "tool_input": {"subagent_type": subagent_type, "prompt": "x"}}
        env = {"HC_TERMINAL_ID": terminal, "DEVKIT_ROLE": role}
        return run([sys.executable, str(HOOK)], env=env, input=json.dumps(data)).stdout

    def test_developer_is_denied_in_herdr(self):
        self.assertIn('"deny"', self.gate("developer"))

    def test_tester_is_denied_in_herdr(self):
        self.assertIn('"deny"', self.gate("tester"))

    def test_reviewer_is_denied_in_lead_session(self):
        self.assertIn('"deny"', self.gate("reviewer"))

    def test_security_reviewer_is_denied_in_worker_pane(self):
        self.assertIn('"deny"', self.gate("security-reviewer", role="worker"))

    def test_reviewer_pane_may_not_call_review_agents(self):
        self.assertIn('"deny"', self.gate("reviewer", role="reviewer"))
        self.assertIn('"deny"', self.gate("security-reviewer", role="reviewer"))

    def test_reviewer_pane_may_not_call_developer(self):
        self.assertIn('"deny"', self.gate("developer", role="reviewer"))

    def test_architect_and_explore_pass_in_herdr(self):
        self.assertEqual(self.gate("architect"), "")
        self.assertEqual(self.gate("Explore"), "")

    def test_everything_passes_outside_herdr(self):
        self.assertEqual(self.gate("developer", terminal=""), "")
        self.assertEqual(self.gate("reviewer", terminal=""), "")
