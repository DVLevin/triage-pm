from __future__ import annotations

import hashlib
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from triage.app import TriageApplication
from triage.server import create_server
from triage.store import DuplicateDecision
from test_kbos import card, render_card


class AppTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "tickets").mkdir()
        (self.root / "README.md").write_text("# Demo\n")
        self.paths = []
        for number in (1, 2):
            path = self.root / "tickets" / f"T-{number}.md"
            path.write_text(render_card(card(f"T-{number}"), f"# Ticket {number}\n\nWhy ticket {number} exists.\n"))
            self.paths.append(path)
        self.config = {"projects": [{"id": "demo", "name": "Demo", "root": str(self.root), "ticket_dirs": ["tickets"], "context_files": ["README.md"]}]}
        self.app = TriageApplication(self.config, self.root / "review.db")

    def tearDown(self):
        self.app.close()
        self.temp.cleanup()

    def snapshot(self): return self.app.get_snapshot("demo")

    def decision_payload(self, direction="approve"):
        snapshot = self.snapshot()
        ticket = next(t for t in snapshot["tickets"] if t["pending"])
        return {"project_id": "demo", "ticket_key": ticket["key"], "content_hash": ticket["content_hash"], "context_snapshot_id": snapshot["context_snapshot_id"], "decision": direction, "reasons": ["unclear_scope"] if direction == "needs_work" else [], "comment": "Check this"}

    def test_approve_duplicate_undo_and_points(self):
        payload = self.decision_payload()
        decision = self.app.decide(payload)
        self.assertEqual(decision["decision"], "approve")
        self.assertEqual(self.snapshot()["review_summary"]["pending"], 1)
        with self.assertRaises(DuplicateDecision): self.app.decide(payload)
        self.assertEqual(self.snapshot()["reviewer_progress"]["points"], 10)
        undone = self.app.undo("demo")
        self.assertIsNotNone(undone)
        self.assertEqual(undone["id"], decision["id"])
        self.assertEqual(self.snapshot()["review_summary"]["pending"], 2)
        self.assertEqual(self.snapshot()["reviewer_progress"]["points"], 0)

    def test_needs_work_requires_reason_and_comment_survives_revision(self):
        payload = self.decision_payload("needs_work")
        payload["reasons"] = []
        with self.assertRaises(ValueError): self.app.decide(payload)
        payload = self.decision_payload("needs_work")
        ticket_key = payload["ticket_key"]
        self.app.decide(payload)
        self.assertEqual(len(self.app.store.comments("demo", ticket_key)), 1)
        path = self.root / ticket_key.split(":", 1)[1]
        original = path.read_text()
        path.write_text(original + "\nRevision detail.\n")
        revised = self.app.get_snapshot("demo", refresh=True)
        revised_ticket = next(t for t in revised["tickets"] if t["key"] == ticket_key)
        self.assertTrue(revised_ticket["pending"])
        self.assertTrue(revised_ticket["changed_since_review"])
        self.assertEqual(len(revised_ticket["comments"]), 1)

    def test_context_application_versions_decision_basis(self):
        snapshot = self.snapshot()
        old_id = snapshot["context_snapshot_id"]
        settings = snapshot["settings"]
        settings["rules"]["require_sources"] = False
        updated = self.app.apply_context("demo", settings)
        self.assertNotEqual(updated["context_snapshot_id"], old_id)
        self.assertFalse(updated["settings"]["rules"]["require_sources"])
        payload = self.decision_payload()
        payload["context_snapshot_id"] = old_id
        with self.assertRaises(ValueError): self.app.decide(payload)

    def test_source_files_never_change(self):
        before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in self.paths]
        self.app.decide(self.decision_payload())
        self.app.undo("demo")
        self.app.apply_context("demo", self.snapshot()["settings"])
        after = [hashlib.sha256(path.read_bytes()).hexdigest() for path in self.paths]
        self.assertEqual(before, after)


class HTTPTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        (root / "tickets").mkdir()
        (root / "tickets" / "T-1.md").write_text(render_card(card()))
        config = {"projects": [{"id": "demo", "name": "Demo", "root": str(root), "ticket_dirs": ["tickets"], "context_files": []}]}
        self.app = TriageApplication(config, root / "review.db")
        self.server = create_server("127.0.0.1", 0, self.app, "test-token", Path(__file__).parents[1] / "static")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.app.close(); self.temp.cleanup()

    def request(self, path, auth=True):
        request = urllib.request.Request(self.url + path, headers={"Authorization": "Bearer test-token"} if auth else {})
        try:
            with urllib.request.urlopen(request) as response: return response.status, response.read()
        except urllib.error.HTTPError as error: return error.code, error.read()

    def test_auth_health_static_and_traversal(self):
        self.assertEqual(self.request("/api/health", False)[0], 200)
        self.assertEqual(self.request("/api/bootstrap", False)[0], 401)
        self.assertEqual(self.request("/api/bootstrap")[0], 200)
        self.assertEqual(self.request("/styles.css", False)[0], 200)
        self.assertEqual(self.request("/../../config.local.json", False)[0], 404)
        payload = json.loads(self.request("/api/project/demo")[1])
        self.assertEqual(payload["summary"]["total_cards"], 1)


if __name__ == "__main__": unittest.main()
