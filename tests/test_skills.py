import re
import unittest

from support import REPO

TRIGGERS = ("Dùng khi", "Dùng sau", "Dùng trước", "Use when")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if line.startswith("#") or ":" not in line or line[0] in " \t":
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def check(path, expected_name, need_tools):
    problems = []
    fm = frontmatter(path)
    if fm is None:
        return [f"{path.name}: no frontmatter"]
    if fm.get("name") != expected_name:
        problems.append(f"name {fm.get('name')!r} != {expected_name!r}")
    desc = fm.get("description", "")
    if not desc:
        problems.append("missing description")
    elif len(desc) >= 1024:
        problems.append(f"description is {len(desc)} chars, limit 1023")
    elif not any(t in desc for t in TRIGGERS):
        problems.append(f"description has no trigger phrase {TRIGGERS}")
    if need_tools and not fm.get("tools"):
        problems.append("missing tools:")
    return [f"{path.parent.name}/{path.name}: {p}" for p in problems]


class SkillLintTest(unittest.TestCase):
    def test_skills(self):
        files = sorted((REPO / "skills").glob("*/SKILL.md"))
        self.assertTrue(files)
        problems = [p for f in files for p in check(f, f.parent.name, False)]
        self.assertEqual(problems, [])

    def test_agents(self):
        files = sorted((REPO / "agents").glob("*.md"))
        self.assertTrue(files)
        problems = [p for f in files for p in check(f, f.stem, True)]
        self.assertEqual(problems, [])

    def test_checker_catches_violations(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "x.md"
            bad.write_text("---\nname: y\ndescription: does things\n---\nbody\n", encoding="utf-8")
            problems = check(bad, "x", True)
        self.assertEqual(len(problems), 3)


if __name__ == "__main__":
    unittest.main()
