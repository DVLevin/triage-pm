from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from pathlib import Path
from typing import Any

from .kbos import utc_now


class DuplicateDecision(Exception):
    pass


class ReviewStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._migrate()

    def close(self) -> None:
        with self.lock:
            self.conn.close()

    def _migrate(self) -> None:
        with self.lock, self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS settings (
                    project_id TEXT PRIMARY KEY,
                    settings_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS context_snapshots (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    settings_json TEXT NOT NULL,
                    sources_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    ticket_key TEXT NOT NULL,
                    ticket_display_id TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    context_snapshot_id TEXT NOT NULL,
                    decision TEXT NOT NULL CHECK(decision IN ('approve','needs_work')),
                    reasons_json TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    undone_at TEXT,
                    FOREIGN KEY(context_snapshot_id) REFERENCES context_snapshots(id)
                );
                CREATE INDEX IF NOT EXISTS decisions_project ON decisions(project_id, id DESC);
                CREATE INDEX IF NOT EXISTS decisions_ticket ON decisions(project_id, ticket_key, content_hash);
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    ticket_key TEXT NOT NULL,
                    author TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS comments_ticket ON comments(project_id, ticket_key, id);
            """)

    @staticmethod
    def _decision(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["reasons"] = json.loads(result.pop("reasons_json"))
        return result

    def get_settings(self, project_id: str, defaults: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            row = self.conn.execute("SELECT settings_json FROM settings WHERE project_id=?", (project_id,)).fetchone()
        return {**defaults, **json.loads(row["settings_json"])} if row else defaults

    def save_settings(self, project_id: str, settings: dict[str, Any]) -> None:
        with self.lock, self.conn:
            self.conn.execute(
                "INSERT INTO settings(project_id,settings_json,updated_at) VALUES(?,?,?) "
                "ON CONFLICT(project_id) DO UPDATE SET settings_json=excluded.settings_json,updated_at=excluded.updated_at",
                (project_id, json.dumps(settings, ensure_ascii=False, sort_keys=True), utc_now()),
            )

    def create_context_snapshot(self, project_id: str, settings: dict[str, Any], sources: list[dict[str, Any]]) -> str:
        snapshot_id = uuid.uuid4().hex
        safe_sources = [
            {"path": source.get("path"), "content_hash": source.get("content_hash"), "modified_at": source.get("modified_at"), "included": source.get("included")}
            for source in sources
        ]
        with self.lock, self.conn:
            self.conn.execute(
                "INSERT INTO context_snapshots(id,project_id,created_at,settings_json,sources_json) VALUES(?,?,?,?,?)",
                (snapshot_id, project_id, utc_now(), json.dumps(settings, ensure_ascii=False, sort_keys=True), json.dumps(safe_sources, ensure_ascii=False, sort_keys=True)),
            )
        return snapshot_id

    def get_context_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        with self.lock:
            row = self.conn.execute("SELECT * FROM context_snapshots WHERE id=?", (snapshot_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["settings"] = json.loads(result.pop("settings_json"))
        result["sources"] = json.loads(result.pop("sources_json"))
        return result

    def add_decision(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            try:
                self.conn.execute("BEGIN IMMEDIATE")
                duplicate = self.conn.execute(
                    "SELECT id FROM decisions WHERE project_id=? AND ticket_key=? AND content_hash=? AND undone_at IS NULL",
                    (payload["project_id"], payload["ticket_key"], payload["content_hash"]),
                ).fetchone()
                if duplicate:
                    raise DuplicateDecision("This ticket version already has an active review decision")
                created = utc_now()
                cursor = self.conn.execute(
                    "INSERT INTO decisions(project_id,ticket_key,ticket_display_id,content_hash,context_snapshot_id,decision,reasons_json,comment,reviewer,created_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        payload["project_id"], payload["ticket_key"], payload["ticket_display_id"], payload["content_hash"],
                        payload["context_snapshot_id"], payload["decision"], json.dumps(payload.get("reasons", []), ensure_ascii=False),
                        payload.get("comment", "").strip(), payload.get("reviewer", "Dima"), created,
                    ),
                )
                decision_id = cursor.lastrowid
                if payload.get("comment", "").strip():
                    self.conn.execute(
                        "INSERT INTO comments(project_id,ticket_key,author,body,created_at) VALUES(?,?,?,?,?)",
                        (payload["project_id"], payload["ticket_key"], payload.get("reviewer", "Dima"), payload["comment"].strip(), created),
                    )
                row = self.conn.execute("SELECT * FROM decisions WHERE id=?", (decision_id,)).fetchone()
                self.conn.commit()
                return self._decision(row)
            except Exception:
                self.conn.rollback()
                raise

    def undo_latest(self, project_id: str) -> dict[str, Any] | None:
        with self.lock, self.conn:
            row = self.conn.execute(
                "SELECT * FROM decisions WHERE project_id=? AND undone_at IS NULL ORDER BY id DESC LIMIT 1", (project_id,)
            ).fetchone()
            if not row:
                return None
            self.conn.execute("UPDATE decisions SET undone_at=? WHERE id=?", (utc_now(), row["id"]))
            updated = self.conn.execute("SELECT * FROM decisions WHERE id=?", (row["id"],)).fetchone()
            return self._decision(updated)

    def history(self, project_id: str, limit: int = 200) -> list[dict[str, Any]]:
        with self.lock:
            rows = self.conn.execute("SELECT * FROM decisions WHERE project_id=? ORDER BY id DESC LIMIT ?", (project_id, limit)).fetchall()
        return [self._decision(row) for row in rows]

    def active_reviews(self, project_id: str) -> list[dict[str, Any]]:
        with self.lock:
            rows = self.conn.execute("SELECT * FROM decisions WHERE project_id=? AND undone_at IS NULL ORDER BY id", (project_id,)).fetchall()
        return [self._decision(row) for row in rows]

    def add_comment(self, project_id: str, ticket_key: str, body: str, author: str = "Dima") -> dict[str, Any]:
        if not body.strip():
            raise ValueError("Comment cannot be empty")
        with self.lock, self.conn:
            cursor = self.conn.execute(
                "INSERT INTO comments(project_id,ticket_key,author,body,created_at) VALUES(?,?,?,?,?)",
                (project_id, ticket_key, author, body.strip(), utc_now()),
            )
            row = self.conn.execute("SELECT * FROM comments WHERE id=?", (cursor.lastrowid,)).fetchone()
            return dict(row)

    def comments(self, project_id: str, ticket_key: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM comments WHERE project_id=?"
        params: list[Any] = [project_id]
        if ticket_key:
            query += " AND ticket_key=?"
            params.append(ticket_key)
        query += " ORDER BY id"
        with self.lock:
            rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def reviewer_progress(self, project_id: str | None = None) -> dict[str, int]:
        query = "SELECT COUNT(*) AS count FROM decisions WHERE undone_at IS NULL"
        params: tuple[Any, ...] = ()
        if project_id:
            query += " AND project_id=?"
            params = (project_id,)
        with self.lock:
            count = self.conn.execute(query, params).fetchone()["count"]
        points = count * 10
        return {"reviews": count, "points": points, "level": points // 100 + 1, "level_progress": points % 100}
