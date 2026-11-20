from __future__ import annotations

import copy
import threading
from pathlib import Path
from typing import Any

from .kbos import KBOSAdapter, default_settings, normalize_settings
from .store import ReviewStore

REASONS = {
    "missing_source", "contradicts_context", "duplicate", "stale",
    "already_done", "unclear_scope", "wrong_owner", "other",
}


class TriageApplication:
    def __init__(self, config: dict[str, Any], db_path: str | Path):
        self.config = config
        self.projects = {project["id"]: project for project in config["projects"]}
        self.adapter = KBOSAdapter(config["projects"])
        self.store = ReviewStore(db_path)
        self.cache: dict[str, dict[str, Any]] = {}
        self.lock = threading.RLock()

    def close(self) -> None:
        self.store.close()

    def _scan(self, project_id: str) -> dict[str, Any]:
        project = self.projects[project_id]
        settings = normalize_settings(project, self.store.get_settings(project_id, default_settings(project)))
        snapshot = self.adapter.scan(project_id, settings)
        snapshot["context_snapshot_id"] = self.store.create_context_snapshot(
            project_id, snapshot["settings"], snapshot["context_sources"]
        )
        return self._annotate(snapshot)

    def _annotate(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        project_id = snapshot["project"]["id"]
        active = self.store.active_reviews(project_id)
        history = self.store.history(project_id)
        active_by_version = {(row["ticket_key"], row["content_hash"]): row for row in active}
        latest_by_ticket = {}
        for row in history:
            latest_by_ticket.setdefault(row["ticket_key"], row)
        queue = []
        reviewed_current = 0
        eligible = 0
        for ticket in snapshot["tickets"]:
            review = active_by_version.get((ticket["key"], ticket["content_hash"]))
            previous = latest_by_ticket.get(ticket["key"])
            ticket["local_review"] = review
            ticket["changed_since_review"] = bool(previous and previous["content_hash"] != ticket["content_hash"])
            ticket["comments"] = self.store.comments(project_id, ticket["key"])
            ticket["pending"] = ticket["queue_eligible"] and review is None
            if ticket["queue_eligible"]:
                eligible += 1
                if review:
                    reviewed_current += 1
            if ticket["pending"]:
                queue.append(ticket["key"])
        snapshot["queue"] = queue
        snapshot["history"] = history
        snapshot["review_summary"] = {
            "eligible": eligible,
            "reviewed_current": reviewed_current,
            "pending": len(queue),
            "decisions_total": len(active),
        }
        snapshot["reviewer_progress"] = self.store.reviewer_progress(project_id)
        return snapshot

    def get_snapshot(self, project_id: str, refresh: bool = False) -> dict[str, Any]:
        with self.lock:
            if project_id not in self.projects:
                raise KeyError("Unknown project")
            if refresh or project_id not in self.cache:
                self.cache[project_id] = self._scan(project_id)
            else:
                self.cache[project_id] = self._annotate(self.cache[project_id])
            return copy.deepcopy(self.cache[project_id])

    def list_projects(self) -> list[dict[str, Any]]:
        result = []
        for project_id, project in self.projects.items():
            try:
                snapshot = self.get_snapshot(project_id)
                result.append({
                    "id": project_id,
                    "name": project["name"],
                    "available": True,
                    "scanned_at": snapshot["scanned_at"],
                    "pending": snapshot["review_summary"]["pending"],
                    "total_cards": snapshot["summary"]["total_cards"],
                    "past_due": snapshot["summary"]["past_due"],
                    "blockers": snapshot["summary"]["cards_with_blockers"],
                    "parser_errors": snapshot["summary"]["parser_errors"],
                    "latest_update": max((t["updated_raw"] for t in snapshot["tickets"]), default=""),
                })
            except Exception as exc:
                result.append({"id": project_id, "name": project["name"], "available": False, "error": type(exc).__name__})
        return result

    def apply_context(self, project_id: str, settings: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            normalized = normalize_settings(self.projects[project_id], settings)
            self.store.save_settings(project_id, normalized)
            self.cache.pop(project_id, None)
            return self.get_snapshot(project_id, refresh=True)

    def decide(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = {"project_id", "ticket_key", "content_hash", "context_snapshot_id", "decision"}
        if not required.issubset(payload):
            raise ValueError("Incomplete decision payload")
        with self.lock:
            snapshot = self.get_snapshot(payload["project_id"])
            if payload["context_snapshot_id"] != snapshot["context_snapshot_id"]:
                raise ValueError("Context snapshot changed; review the current ticket again")
            ticket = next((t for t in snapshot["tickets"] if t["key"] == payload["ticket_key"]), None)
            if not ticket:
                raise KeyError("Ticket is not in the current snapshot")
            if ticket["content_hash"] != payload["content_hash"]:
                raise ValueError("Ticket changed on disk; review the new version")
            if not ticket["queue_eligible"]:
                raise ValueError("Ticket is excluded from this review queue")
            decision = payload["decision"]
            reasons = payload.get("reasons", [])
            if decision == "needs_work":
                if not isinstance(reasons, list) or not reasons or any(reason not in REASONS for reason in reasons):
                    raise ValueError("Needs work requires at least one valid reason")
            elif decision == "approve":
                if ticket["approval_problems"]:
                    raise ValueError("Approval blocked: " + "; ".join(ticket["approval_problems"]))
                reasons = []
            else:
                raise ValueError("Unknown decision")
            result = self.store.add_decision({
                "project_id": payload["project_id"],
                "ticket_key": ticket["key"],
                "ticket_display_id": ticket["display_id"],
                "content_hash": ticket["content_hash"],
                "context_snapshot_id": snapshot["context_snapshot_id"],
                "decision": decision,
                "reasons": reasons,
                "comment": str(payload.get("comment") or "")[:10000],
                "reviewer": "Dima",
            })
            self.cache[payload["project_id"]] = self._annotate(self.cache[payload["project_id"]])
            return result

    def undo(self, project_id: str) -> dict[str, Any] | None:
        with self.lock:
            result = self.store.undo_latest(project_id)
            if result:
                self.cache[project_id] = self._annotate(self.cache[project_id])
            return result

    def comment(self, project_id: str, ticket_key: str, body: str) -> dict[str, Any]:
        with self.lock:
            snapshot = self.get_snapshot(project_id)
            if not any(t["key"] == ticket_key for t in snapshot["tickets"]):
                raise KeyError("Ticket is not in the current snapshot")
            result = self.store.add_comment(project_id, ticket_key, body)
            self.cache[project_id] = self._annotate(self.cache[project_id])
            return result
