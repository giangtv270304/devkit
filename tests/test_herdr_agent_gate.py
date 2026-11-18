import json
import sys
import unittest

from support import REPO, run

HOOK = REPO / "hooks" / "herdr_agent_gate.py"


class HerdrAgentGateTest(unittest.TestCase):
    def gate(self, subagent_type, terminal="t1"):
        data = {"tool_name": "Agent", "tool_input": {"subagent_type": subagent_type, "prompt": "x"}}
        return run([sys.executable, str(HOOK)], env={"HC_TERMINAL_ID": terminal}, input=json.dumps(data)).stdout

    def test_developer_is_denied_in_herdr(self):
        self.assertIn('"deny"', self.gate("developer"))

    def test_tester_is_denied_in_herdr(self):
        self.assertIn('"deny"', self.gate("tester"))

    def test_reviewer_passes_in_herdr(self):
        self.assertEqual(self.gate("reviewer"), "")

    def test_developer_passes_outside_herdr(self):
        self.assertEqual(self.gate("developer", terminal=""), "")
