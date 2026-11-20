from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from triage.app import TriageApplication


class RealSourceTest(unittest.TestCase):
    def test_real_sources_read_only_and_errors_isolated(self):
        repo = Path(__file__).parents[1]
        config_path = repo / "config.local.json"
        if not config_path.exists():
            self.skipTest("Local source configuration is not present")
        config = json.loads(config_path.read_text())
        configured_files = []
        for project in config["projects"]:
            root = Path(project["root"]).expanduser()
            for folder in project["ticket_dirs"]:
                base = root / folder
                if base.exists():
                    configured_files.extend(path for path in base.rglob("*.md") if not path.is_symlink())
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in configured_files}
        with tempfile.TemporaryDirectory() as tmp:
            app = TriageApplication(config, Path(tmp) / "review.db")
            try:
                projects = app.list_projects()
                self.assertTrue(all(project["available"] for project in projects))
                snapshots = {project["id"]: app.get_snapshot(project["id"]) for project in projects}
                self.assertGreater(snapshots["granat"]["summary"]["total_cards"], 0)
                self.assertGreater(snapshots["cone-red"]["summary"]["total_cards"], 0)
                self.assertEqual(snapshots["getdeal"]["summary"]["parser_errors"], 3)
                self.assertGreater(snapshots["getdeal"]["summary"]["total_cards"], 0)
                self.assertGreater(snapshots["cone-red"]["summary"]["duplicate_display_ids"], 0)
                self.assertGreater(snapshots["nous-claw"]["summary"]["unknown_state"], 0)
            finally:
                app.close()
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in configured_files}
        self.assertEqual(before, after)


if __name__ == "__main__": unittest.main()
