from __future__ import annotations

import datetime as dt
import hashlib
import tempfile
import unittest
from pathlib import Path

from triage.kbos import KBOSAdapter, default_settings


def card(card_id="T-1", **overrides):
    data = {
        "schema_version": "1.1", "id": card_id, "created": "2026-11-01",
        "owner": "conny", "tier": "A1", "type": "build", "state": "todo",
        "priority": "P1", "due": "2026-11-25",
        "terminal_states": ["READY", "READY WITH NOTES", "BLOCKED"],
        "dod": ['"Test passes → evidence: result.txt"'],
        "scope_not": "No external write", "artifacts": ["result.txt"],
        "verdict_file": "verdicts/T-1.md", "sources": ["Dima, 20 Nov"],
        "context": ["README.md"], "next": "Run the test", "updated": "2026-11-20",
    }
    data.update(overrides)
    return data


def render_card(meta, body="# Example ticket\n\nA concrete reason for this work.\n"):
    import yaml
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n" + body


class KBOSTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "tickets").mkdir()
        (self.root / "verdicts").mkdir()
        (self.root / "README.md").write_text("# Fixture project\nCurrent context.\n")
        self.project = {"id": "demo", "name": "Demo", "root": str(self.root), "ticket_dirs": ["tickets"], "context_files": ["README.md", "WEEK.md"]}

    def tearDown(self): self.temp.cleanup()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def scan(self):
        adapter = KBOSAdapter([self.project], as_of=dt.date(2026, 11, 20))
        return adapter.scan("demo", default_settings(self.project))

    def test_v11_bom_crlf_and_plain_note(self):
        self.write("tickets/one.md", "\ufeff" + render_card(card("T-1", schema_version=1.1)).replace("\n", "\r\n"))
        self.write("tickets/notes.md", "# Ordinary note\n\n---\nNot a card.\n")
        result = self.scan()
        self.assertEqual(result["summary"]["total_cards"], 1)
        self.assertEqual(result["summary"]["parser_errors"], 0)
        self.assertEqual(result["tickets"][0]["profile"], "task_card_v1_1")

    def test_malformed_task_is_isolated(self):
        self.write("tickets/good.md", render_card(card()))
        self.write("tickets/bad.md", "---\nid: BAD-1\ntitle: Bad: unquoted\n---\n# Bad\n")
        result = self.scan()
        self.assertEqual(result["summary"]["total_cards"], 1)
        self.assertEqual(result["summary"]["parser_errors"], 1)
        self.assertEqual(result["errors"][0]["path"], "tickets/bad.md")

    def test_duplicate_ids_make_dependencies_ambiguous(self):
        self.write("tickets/a.md", render_card(card("DUP", depends_on=[])))
        self.write("tickets/nested/b.md", render_card(card("DUP", depends_on=[])))
        self.write("tickets/c.md", render_card(card("T-3", depends_on=["DUP"])))
        result = self.scan()
        target = next(t for t in result["tickets"] if t["display_id"] == "T-3")
        self.assertEqual(target["dependencies"][0]["status"], "ambiguous")
        self.assertFalse(target["blocker_details"])
        self.assertEqual(result["summary"]["duplicate_display_ids"], 1)

    def test_unknown_state_verdict_and_progress_are_separate(self):
        meta = card("T-1", state=None, dod=["one", "two"], verdict_file="verdicts/T-1.md")
        self.write("tickets/one.md", render_card(meta, "# T\n\nNo checkboxes here. Prose says done but state is absent.\n"))
        self.write("verdicts/T-1.md", "**Latest verdict: READY WITH NOTES**\n")
        ticket = self.scan()["tickets"][0]
        self.assertEqual(ticket["work_status"], "unknown")
        self.assertEqual(ticket["review_verdict"], "READY WITH NOTES")
        self.assertIsNone(ticket["recorded_checks"])
        self.assertEqual(len(ticket["dod"]), 2)

    def test_only_full_iso_due_enters_timeline(self):
        self.write("tickets/a.md", render_card(card("A", due="2026-11-20 (Jira DEMO-1)")))
        self.write("tickets/b.md", render_card(card("B", due="2026-11-19", state="in-progress")))
        self.write("tickets/c.md", render_card(card("C", due="2026-11-19", state=None)))
        result = self.scan()
        self.assertEqual(result["summary"]["scheduled"], 2)
        self.assertEqual(result["summary"]["ambiguous_due"], 1)
        self.assertEqual(result["summary"]["past_due"], 1)

    def test_explicit_blockers_impact_and_checks(self):
        body = "# T\n\n## Dependencies\n- Blocked by: design approval\n- Blocks: Monday launch\n\n## Work\n- [x] Draft\n- [ ] Verify\n"
        self.write("tickets/a.md", render_card(card("A", depends_on=[]), body))
        ticket = self.scan()["tickets"][0]
        self.assertEqual(ticket["blocker_details"][0]["text"], "design approval")
        self.assertEqual(ticket["impacts"], ["Monday launch"])
        self.assertEqual(ticket["recorded_checks"], {"checked": 1, "total": 2})

    def test_approval_rules_fail_closed(self):
        meta = card("A", sources=[], owner=None, dod=[], next=None)
        self.write("tickets/a.md", render_card(meta))
        ticket = self.scan()["tickets"][0]
        joined = " ".join(ticket["approval_problems"])
        self.assertIn("Source intent", joined)
        self.assertIn("owner", joined)
        self.assertIn("Definition of Done", joined)
        self.assertIn("Next action", joined)

    def test_context_is_bounded_and_source_bytes_unchanged(self):
        (self.root / "WEEK.md").write_text("> STALE — old week\n" + "x" * 9000)
        path = self.write("tickets/a.md", render_card(card()))
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        result = self.scan()
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
        week = next(source for source in result["context_sources"] if source["path"] == "WEEK.md")
        self.assertTrue(week["self_declared_stale"])
        self.assertTrue(week["truncated"])


if __name__ == "__main__": unittest.main()
