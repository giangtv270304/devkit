import json
import os
import sys
import unittest

from support import REPO, TempDirCase, run

INSTALL = str(REPO / "install.py")


class InstallTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.home = self.tmp / "home"
        self.claude = self.tmp / "claude"
        self.templates = self.tmp / "templates"
        self.bin = self.tmp / "bin"
        self.home.mkdir()
        self.env = {
            "HOME": str(self.home),
            "CLAUDE_CONFIG_DIR": str(self.claude),
            "DEVKIT_HERDR_TEMPLATES": str(self.templates),
            "DEVKIT_BIN_DIR": str(self.bin),
        }

    def install(self, *args):
        return run([sys.executable, INSTALL, *args], env=self.env)

    def settings(self):
        return json.loads((self.claude / "settings.json").read_text())

    def test_dry_run_writes_nothing(self):
        out = self.install()
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("DRY RUN", out.stdout)
        for path in (self.claude, self.templates, self.bin):
            self.assertFalse(path.exists(), path)

    def test_apply_links_everything_and_merges_settings(self):
        out = self.install("--apply")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual((self.claude / "devkit").resolve(), REPO)
        self.assertTrue((self.claude / "skills" / "work").is_symlink())
        self.assertTrue((self.claude / "agents" / "developer.md").is_symlink())
        self.assertTrue((self.templates / "worker.md").is_symlink())
        self.assertTrue((self.bin / "herdr-task").is_symlink())
        data = self.settings()
        self.assertIn("Read(./**/.env)", data["permissions"]["deny"])
        self.assertIn("PreToolUse", data["hooks"])
        self.assertFalse((self.home / ".claude").exists())
        self.assertFalse((self.home / ".local").exists())
        self.assertFalse((self.home / ".config").exists())

    def test_apply_twice_is_in_sync(self):
        self.install("--apply")
        before = (self.claude / "settings.json").read_text()
        out = self.install("--apply")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual((self.claude / "settings.json").read_text(), before)
        self.assertEqual(list(self.claude.glob("settings.json.devkit-bak-*")), [])
        self.assertNotIn("linked", out.stdout)

    def test_existing_settings_are_kept_and_backed_up(self):
        self.claude.mkdir()
        (self.claude / "settings.json").write_text(json.dumps({"model": "x", "permissions": {"deny": ["Bash(rm:*)"]}}))
        self.install("--apply")
        data = self.settings()
        self.assertEqual(data["model"], "x")
        self.assertIn("Bash(rm:*)", data["permissions"]["deny"])
        self.assertEqual(len(list(self.claude.glob("settings.json.devkit-bak-*"))), 1)

    def test_uninstall_removes_only_our_entries(self):
        self.claude.mkdir()
        mine = {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo mine"}]}
        (self.claude / "settings.json").write_text(
            json.dumps({"model": "x", "hooks": {"PreToolUse": [mine]}})
        )
        self.install("--apply")
        out = self.install("--uninstall", "--apply")
        self.assertEqual(out.returncode, 0, out.stderr)
        data = self.settings()
        self.assertEqual(data, {"model": "x", "hooks": {"PreToolUse": [mine]}})
        self.assertFalse((self.claude / "devkit").exists())
        self.assertFalse((self.claude / "skills" / "work").exists())
        self.assertFalse((self.bin / "herdr-task").exists())

    def test_enabled_plugin_is_added_kept_and_removed(self):
        name = "gopls-lsp@claude-plugins-official"
        self.claude.mkdir()
        (self.claude / "settings.json").write_text(json.dumps({"enabledPlugins": {"other@m": True}}))
        dry = self.install()
        self.assertRegex(dry.stdout, rf"plugin\s+{name}\s+would add")
        self.install("--apply")
        self.assertEqual(self.settings()["enabledPlugins"], {"other@m": True, name: True})
        self.install("--uninstall", "--apply")
        self.assertEqual(self.settings(), {"enabledPlugins": {"other@m": True}})

    def test_plugin_the_user_disabled_stays_disabled(self):
        name = "gopls-lsp@claude-plugins-official"
        self.claude.mkdir()
        (self.claude / "settings.json").write_text(json.dumps({"enabledPlugins": {name: False}}))
        self.install("--apply")
        self.assertIs(self.settings()["enabledPlugins"][name], False)

    def test_foreign_file_is_not_overwritten(self):
        (self.claude / "agents").mkdir(parents=True)
        mine = self.claude / "agents" / "developer.md"
        mine.write_text("mine")
        out = self.install("--apply")
        self.assertEqual(mine.read_text(), "mine")
        self.assertIn("skipped", out.stdout)

    def test_broken_settings_json_stops_without_changes(self):
        self.claude.mkdir()
        (self.claude / "settings.json").write_text("{ not json")
        out = self.install("--apply")
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("not valid JSON", out.stderr)
        self.assertEqual((self.claude / "settings.json").read_text(), "{ not json")
        self.assertFalse((self.claude / "devkit").exists())
        self.assertFalse(self.bin.exists())

    def test_copy_agents_copies_files(self):
        self.install("--apply", "--copy-agents")
        agent = self.claude / "agents" / "developer.md"
        self.assertTrue(agent.is_file() and not agent.is_symlink())
        self.assertEqual(agent.read_bytes(), (REPO / "agents" / "developer.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
