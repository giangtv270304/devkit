import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class TempDirCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name).resolve()


def run(cmd, env=None, input=None, cwd=None):
    full = dict(os.environ)
    full.update(env or {})
    return subprocess.run(cmd, input=input, capture_output=True, text=True, env=full, cwd=cwd)
