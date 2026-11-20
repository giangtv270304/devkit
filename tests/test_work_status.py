import sys
from datetime import date, timedelta

from support import REPO, TempDirCase, run

SCRIPT = REPO / "skills" / "work" / "status.py"


class WorkStatusPriorityTest(TempDirCase):
    def task(self, slug, phase="build", updated="2026-11-01", priority=None, due=None):
        folder = self.tmp / "work" / slug
        folder.mkdir(parents=True)
        lines = [f"# {slug}", "", f"Phase: {phase}", f"Cập nhật: {updated}", "Loại: feature"]
        lines.append(f"Ưu tiên: {priority}" if priority else "Ưu tiên:")
        lines.append(f"Hạn: {due}" if due else "Hạn:")
        lines += ["Branch:", "", "## Tóm tắt", "CẦN BẠN: không", ""]
        (folder / "TASK.md").write_text("\n".join(lines), encoding="utf-8")

    def order(self):
        out = run([sys.executable, str(SCRIPT)], env={"CLAUDE_PROJECT_DIR": str(self.tmp)}).stdout
        rows = [line.split(" | ") for line in out.splitlines()[2:]]
        return [(r[0].lstrip("| "), r[1], r[2]) for r in rows]

    def test_sorts_by_priority_then_deadline_and_keeps_done_last(self):
        far = (date.today() + timedelta(days=30)).isoformat()
        self.task("calm", priority="P3", updated="2026-11-19")
        self.task("default", updated="2026-11-18")
        self.task("waiting", priority="P1", due=far)
        self.task("incident", priority="P0")
        self.task("shipped", phase="done", priority="P0")
        self.assertEqual([r[0] for r in self.order()], ["incident", "waiting", "default", "calm", "shipped"])

    def test_same_priority_puts_nearly_done_first(self):
        self.task("new-idea", phase="intent", updated="2026-11-20")
        self.task("in-review", phase="review", updated="2026-11-10")
        self.task("ready", phase="ship", updated="2026-11-01")
        self.assertEqual([r[0] for r in self.order()], ["ready", "in-review", "new-idea"])

    def test_due_soon_or_overdue_counts_as_p1(self):
        soon = (date.today() + timedelta(days=1)).isoformat()
        late = (date.today() - timedelta(days=3)).isoformat()
        self.task("plain", priority="P1")
        self.task("soon", priority="P3", due=soon)
        self.task("late", priority="P2", due=late)
        rows = {r[0]: r for r in self.order()}
        self.assertEqual(rows["soon"][1], "P3→P1")
        self.assertEqual(rows["soon"][2], f"{soon} (còn 1 ngày)")
        self.assertEqual(rows["late"][2], f"{late} (quá hạn)")
        self.assertEqual([r[0] for r in self.order()][0], "late")

    def test_blank_fields_do_not_read_the_next_line(self):
        self.task("blank")
        rows = {r[0]: r for r in self.order()}
        self.assertEqual(rows["blank"][1], "?")
        self.assertEqual(rows["blank"][2], "")
