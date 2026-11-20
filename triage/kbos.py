from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

REQUIRED_KEYS = [
    "schema_version", "id", "created", "owner", "tier", "type",
    "terminal_states", "dod", "scope_not", "artifacts", "verdict_file",
    "sources", "context", "next", "updated",
]
LOAD_BEARING = ["tier", "dod", "verdict_file", "terminal_states", "owner", "next"]
DEFAULT_RULES = {
    "require_sources": True,
    "require_methodology": True,
    "require_owner": True,
    "require_dod": True,
    "require_next": True,
    "exclude_completed": True,
}
STATUS_MAP = {
    "open": "not_started", "todo": "not_started", "backlog": "not_started",
    "in-progress": "active", "in_progress": "active", "doing": "active",
    "review": "review", "in_review": "review", "in-review": "review",
    "blocked": "blocked", "delivered": "delivered",
    "done": "completed_recorded", "closed": "completed_recorded",
    "cancelled": "closed_without_success_claim", "canceled": "closed_without_success_claim",
    "dropped": "closed_without_success_claim", "superseded": "closed_without_success_claim",
    "retired": "closed_without_success_claim",
}
TERMINAL_STATES = {"completed_recorded", "closed_without_success_claim"}
NONTERMINAL_STATES = {"not_started", "active", "review", "blocked", "delivered"}
EMPTY_WORDS = {"", "none", "no", "нет", "null", "n/a", "na", "—", "-"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_safe(value: Any) -> Any:
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    return value


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(json_safe(v)).strip() for v in value if v is not None and str(json_safe(v)).strip()]
    text = str(json_safe(value)).strip()
    return [text] if text else []


def plain(value: Any) -> str:
    text = str(json_safe(value) or "")
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`~]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def split_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise ValueError("No complete YAML frontmatter block")
    return match.group(1), text[match.end():]


def markdown_section(body: str, names: set[str]) -> str:
    wanted = {name.lower() for name in names}
    lines = body.splitlines()
    start = None
    level = None
    for index, line in enumerate(lines):
        match = re.match(r"^(#{2,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = plain(match.group(2)).lower()
        if start is None and heading in wanted:
            start = index + 1
            level = len(match.group(1))
        elif start is not None and len(match.group(1)) <= (level or 2):
            return "\n".join(lines[start:index]).strip()
    return "\n".join(lines[start:]).strip() if start is not None else ""


def containing_section(body: str, needles: tuple[str, ...]) -> str:
    lines = body.splitlines()
    start = None
    level = None
    for index, line in enumerate(lines):
        match = re.match(r"^(#{2,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = plain(match.group(2)).lower()
        if start is None and any(needle in heading for needle in needles):
            start = index + 1
            level = len(match.group(1))
        elif start is not None and len(match.group(1)) <= (level or 2):
            return "\n".join(lines[start:index]).strip()
    return "\n".join(lines[start:]).strip() if start is not None else ""


def first_h1(body: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return plain(match.group(1)) if match else ""


def first_paragraph(body: str) -> str:
    body = re.sub(r"^#\s+.+$", "", body, flags=re.MULTILINE)
    chunks = re.split(r"\r?\n\s*\r?\n", body)
    for chunk in chunks:
        lines = []
        for line in chunk.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "|", "---", "<!--", ">")):
                continue
            if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
                continue
            lines.append(stripped)
        result = plain(" ".join(lines))
        if len(result) >= 20:
            return result
    return ""


def list_lines(section: str) -> list[str]:
    result = []
    for line in section.splitlines():
        match = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.+)$", line)
        if match:
            result.append(plain(match.group(1)))
    return result


def named_section_values(section: str, label: str) -> list[str]:
    values = []
    for line in section.splitlines():
        match = re.match(rf"^\s*(?:[-*]\s*)?{re.escape(label)}\s*:\s*(.+?)\s*$", line, re.IGNORECASE)
        if match:
            value = plain(match.group(1))
            if value.lower() not in EMPTY_WORDS:
                values.append(value)
    return values


def iso_date(value: Any) -> tuple[str | None, str]:
    raw = str(json_safe(value) or "").strip()
    if not raw or raw.lower() == "null":
        return None, "missing"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        try:
            return dt.date.fromisoformat(raw).isoformat(), "iso"
        except ValueError:
            return None, "invalid"
    return None, "annotated"


def priority_rank(value: Any) -> int:
    text = str(json_safe(value) or "").upper().strip()
    if re.fullmatch(r"P[0-4]", text):
        return int(text[1])
    if text in {"1", "2", "3", "4"}:
        return int(text) - 1
    return 8


def file_time(path: Path) -> str:
    return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_settings(project: dict[str, Any]) -> dict[str, Any]:
    return {
        "sources": {path: path not in {"AGENTS.md", "CLAUDE.md", "BOARD.md"} for path in project.get("context_files", [])},
        "rules": dict(DEFAULT_RULES),
    }


def normalize_settings(project: dict[str, Any], candidate: dict[str, Any] | None) -> dict[str, Any]:
    base = default_settings(project)
    if not isinstance(candidate, dict):
        return base
    source_input = candidate.get("sources", {})
    rule_input = candidate.get("rules", {})
    if isinstance(source_input, dict):
        for path in base["sources"]:
            if isinstance(source_input.get(path), bool):
                base["sources"][path] = source_input[path]
    if isinstance(rule_input, dict):
        for rule in base["rules"]:
            if isinstance(rule_input.get(rule), bool):
                base["rules"][rule] = rule_input[rule]
    return base


def approval_problems(ticket: dict[str, Any], rules: dict[str, bool]) -> list[str]:
    problems = []
    if rules.get("require_methodology", True):
        if ticket["missing_keys"]:
            problems.append("Missing TASK_CARD fields: " + ", ".join(ticket["missing_keys"]))
        if ticket["null_load_bearing"]:
            problems.append("Draft load-bearing fields: " + ", ".join(ticket["null_load_bearing"]))
    if rules.get("require_sources", True) and not ticket["sources"]:
        problems.append("Source intent is missing")
    if rules.get("require_owner", True) and not ticket["owner"]:
        problems.append("Owner is missing")
    if rules.get("require_dod", True) and not ticket["dod"]:
        problems.append("Definition of Done is missing")
    if rules.get("require_next", True) and not ticket["next"]:
        problems.append("Next action is missing")
    return list(dict.fromkeys(problems))


class KBOSAdapter:
    def __init__(self, projects: list[dict[str, Any]], as_of: dt.date | None = None):
        self.projects = {project["id"]: project for project in projects}
        self.as_of = as_of or dt.date.today()

    def scan(self, project_id: str, settings: dict[str, Any]) -> dict[str, Any]:
        project = self.projects[project_id]
        root = Path(os.path.expanduser(project["root"])).resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"Configured root is unavailable: {root}")
        settings = normalize_settings(project, settings)
        tickets, errors = self._read_tickets(project, root)
        self._resolve_dependencies(tickets)
        duplicates = {key for key, count in Counter(t["display_id"] for t in tickets).items() if count > 1}
        for ticket in tickets:
            ticket["duplicate_id"] = ticket["display_id"] in duplicates
            ticket["approval_problems"] = approval_problems(ticket, settings["rules"])
            ticket["queue_eligible"] = not (
                settings["rules"].get("exclude_completed", True)
                and ticket["work_status"] in TERMINAL_STATES | {"delivered"}
            )
        tickets.sort(key=lambda t: (
            priority_rank(t["priority"]),
            t["due_date"] or "9999-12-31",
            t["updated_raw"] and str(t["updated_raw"]) or "",
            t["path"],
        ))
        # Stable newest-first within the same priority/due without sacrificing determinism.
        groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
        for ticket in tickets:
            groups[(priority_rank(ticket["priority"]), ticket["due_date"] or "9999-12-31")].append(ticket)
        tickets = [t for group in groups.values() for t in sorted(group, key=lambda x: (str(x["updated_raw"]), x["path"]), reverse=True)]

        context_sources = self._read_context(project, root, settings)
        state_counts = Counter(t["work_status"] for t in tickets)
        verdict_counts = Counter(t["review_verdict"] or "unknown" for t in tickets)
        blocker_rows = [
            {"ticket_key": t["key"], "display_id": t["display_id"], "title": t["title"], "updated": t["updated_raw"], **blocker}
            for t in tickets for blocker in t["blocker_details"]
        ]
        timeline = [
            {"key": t["key"], "display_id": t["display_id"], "title": t["title"], "due": t["due_date"], "past_due": t["past_due"], "state": t["work_status"]}
            for t in tickets if t["due_date"]
        ]
        timeline.sort(key=lambda row: (row["due"], row["key"]))
        summary = {
            "total_cards": len(tickets),
            "state_counts": dict(sorted(state_counts.items())),
            "verdict_counts": dict(sorted(verdict_counts.items())),
            "source_coverage": sum(bool(t["sources"]) for t in tickets),
            "scheduled": len(timeline),
            "unscheduled": sum(t["due_kind"] == "missing" for t in tickets),
            "ambiguous_due": sum(t["due_kind"] in {"annotated", "invalid"} for t in tickets),
            "past_due": sum(t["past_due"] for t in tickets),
            "unknown_state": state_counts.get("unknown", 0),
            "cards_with_blockers": sum(bool(t["blocker_details"]) for t in tickets),
            "parser_errors": len(errors),
            "duplicate_display_ids": len(duplicates),
            "queue_eligible": sum(t["queue_eligible"] for t in tickets),
        }
        return {
            "project": {"id": project_id, "name": project["name"]},
            "scanned_at": utc_now(),
            "as_of": self.as_of.isoformat(),
            "settings": settings,
            "context_sources": context_sources,
            "tickets": tickets,
            "errors": errors,
            "blockers": blocker_rows,
            "timeline": timeline,
            "summary": summary,
            "integrity_note": "Recorded KBOS snapshot. File states and verdicts are not external delivery verification.",
        }

    def _ticket_files(self, project: dict[str, Any], root: Path) -> list[tuple[Path, str]]:
        found = []
        for folder in project.get("ticket_dirs", ["tickets"]):
            base = root / folder
            if not base.is_dir() or base.is_symlink():
                continue
            for current, dirs, files in os.walk(base, followlinks=False):
                dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in {"node_modules", "archive", "verdicts", "_context"} and not (Path(current) / d).is_symlink())
                for name in sorted(files):
                    path = Path(current) / name
                    if not name.lower().endswith(".md") or name.startswith("_") or "TEMPLATE" in name.upper() or path.is_symlink():
                        continue
                    found.append((path, path.relative_to(root).as_posix()))
        return found

    def _read_tickets(self, project: dict[str, Any], root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        tickets = []
        errors = []
        for path, relative in self._ticket_files(project, root):
            try:
                raw = path.read_bytes()
                digest = hashlib.sha256(raw).hexdigest()
                text = raw.decode("utf-8-sig")
                if not text.startswith("---"):
                    continue
                try:
                    yaml_text, body = split_frontmatter(text)
                except ValueError:
                    # Ordinary Markdown notes are not ticket candidates.
                    continue
                try:
                    metadata = yaml.safe_load(yaml_text)
                except Exception:
                    # Only task-shaped frontmatter earns a parser error; door
                    # contracts and other YAML documents remain outside scope.
                    if re.search(r"^(?:id|schema_version|title)\s*:", yaml_text, re.MULTILINE):
                        raise
                    continue
                if not isinstance(metadata, dict):
                    raise ValueError("Frontmatter is not a mapping")
                if not any(key in metadata for key in ("id", "schema_version", "title")):
                    continue
                tickets.append(self._ticket_from_card(project, root, path, relative, digest, metadata, body))
            except Exception as exc:
                errors.append({"path": relative, "error": f"{type(exc).__name__}: {str(exc).splitlines()[0]}"})
        return tickets, errors

    def _ticket_from_card(self, project: dict[str, Any], root: Path, path: Path, relative: str, digest: str, meta: dict[str, Any], body: str) -> dict[str, Any]:
        display_id = str(json_safe(meta.get("id")) or Path(relative).stem)
        raw_state = str(json_safe(meta.get("state")) or "").strip()
        work_status = STATUS_MAP.get(raw_state.lower(), "unknown")
        title = plain(meta.get("title")) or first_h1(body) or display_id
        title_source = "frontmatter" if plain(meta.get("title")) else ("body_h1" if first_h1(body) else "id")
        why = plain(meta.get("why")) or plain(markdown_section(body, {"why", "context"})) or first_paragraph(body)
        why_source = "frontmatter" if plain(meta.get("why")) else "body"
        due_date, due_kind = iso_date(meta.get("due"))
        updated_date, _ = iso_date(meta.get("updated"))
        created_date, _ = iso_date(meta.get("created"))
        checks = re.findall(r"^\s*(?:[-*]|\d+\.)\s+\[([ xX])\]\s+", body, re.MULTILINE)
        check_count = len(checks)
        checked = sum(mark.lower() == "x" for mark in checks)
        missing_keys = [key for key in REQUIRED_KEYS if key not in meta]
        null_load_bearing = [] if work_status in TERMINAL_STATES else [
            key for key in LOAD_BEARING if key not in meta or meta.get(key) is None or meta.get(key) == [] or meta.get(key) == ""
        ]
        dependencies = markdown_section(body, {"dependencies", "dependency", "зависимости"})
        blockers = as_list(meta.get("blockers"))
        blocker_details = [{"kind": "reported", "text": text} for text in blockers]
        if work_status == "blocked":
            blocker_details.append({"kind": "declared", "text": "Work state is declared blocked"})
        for text in named_section_values(dependencies, "Blocked by"):
            blocker_details.append({"kind": "reported", "text": text})
        impacts = as_list(meta.get("blocks")) + named_section_values(dependencies, "Blocks")
        verdict, verdict_status = self._read_verdict(root, relative, meta.get("verdict_file"), body)
        ticket = {
            "key": f"{project['id']}:{relative}",
            "path": relative,
            "display_id": display_id,
            "content_hash": digest,
            "modified_at": file_time(path),
            "title": title,
            "title_source": title_source,
            "why": why,
            "why_source": why_source,
            "why_evidence": plain(meta.get("why_evidence")),
            "profile": "task_card_v1_1" if str(json_safe(meta.get("schema_version")) or "") == "1.1" else "legacy",
            "frontmatter": json_safe(meta),
            "body": body[:30000],
            "body_truncated": len(body) > 30000,
            "raw_state": raw_state,
            "work_status": work_status,
            "priority": str(json_safe(meta.get("priority")) or "Not stated"),
            "owner": plain(meta.get("owner") or meta.get("assignee")),
            "assignee": plain(meta.get("assignee")),
            "reviewer": plain(meta.get("reviewer")),
            "tier": plain(meta.get("tier")),
            "type": plain(meta.get("type")),
            "epic": plain(meta.get("epic")),
            "created": created_date,
            "updated": updated_date,
            "updated_raw": str(json_safe(meta.get("updated")) or ""),
            "due_date": due_date,
            "due_kind": due_kind,
            "due_raw": str(json_safe(meta.get("due")) or ""),
            "past_due": bool(due_date and work_status in NONTERMINAL_STATES and dt.date.fromisoformat(due_date) < self.as_of),
            "dod": as_list(meta.get("dod")),
            "scope_not": plain(meta.get("scope_not")),
            "artifacts": as_list(meta.get("artifacts")),
            "sources": as_list(meta.get("sources")),
            "context": as_list(meta.get("context")),
            "next": plain(meta.get("next")),
            "terminal_states": as_list(meta.get("terminal_states")),
            "verdict_file": str(json_safe(meta.get("verdict_file")) or ""),
            "review_verdict": verdict,
            "verdict_status": verdict_status,
            "depends_on": as_list(meta.get("depends_on")),
            "dependencies": [],
            "blocker_details": blocker_details,
            "impacts": list(dict.fromkeys(impacts)),
            "open_questions": list_lines(containing_section(body, ("open questions", "открытые вопросы"))),
            "recorded_checks": {"checked": checked, "total": check_count} if check_count else None,
            "missing_keys": missing_keys,
            "null_load_bearing": null_load_bearing,
        }
        return ticket

    def _resolve_dependencies(self, tickets: list[dict[str, Any]]) -> None:
        by_path = {t["path"]: t for t in tickets}
        by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for ticket in tickets:
            by_id[ticket["display_id"]].append(ticket)
        for ticket in tickets:
            for ref in ticket["depends_on"]:
                clean = ref.split("#", 1)[0]
                target = by_path.get(clean)
                if target is None and clean in by_id and len(by_id[clean]) == 1:
                    target = by_id[clean][0]
                if target:
                    state = "resolved_terminal" if target["work_status"] in TERMINAL_STATES else "resolved_nonterminal"
                    ticket["dependencies"].append({"ref": ref, "status": state, "target_key": target["key"], "target_title": target["title"]})
                    if state == "resolved_nonterminal":
                        ticket["blocker_details"].append({"kind": "dependency_waiting", "text": f"Waiting on {target['display_id']}: {target['title']}"})
                else:
                    status = "ambiguous" if len(by_id.get(clean, [])) > 1 else "unresolved"
                    ticket["dependencies"].append({"ref": ref, "status": status})

    def _read_verdict(self, root: Path, ticket_path: str, value: Any, body: str) -> tuple[str | None, str]:
        raw = str(json_safe(value) or "").strip()
        if not raw:
            return None, "not_declared"
        target_raw = os.path.expanduser(raw.split("#", 1)[0])
        if raw.split("#", 1)[0] == ticket_path:
            section = markdown_section(body, {"verdict"})
            return self._verdict_from_text(section), "same_card"
        target = Path(target_raw) if os.path.isabs(target_raw) else root / target_raw
        try:
            resolved = target.resolve()
            resolved.relative_to(root)
        except (ValueError, OSError):
            return None, "outside_read_scope"
        if not resolved.is_file() or target.is_symlink():
            return None, "missing"
        try:
            return self._verdict_from_text(resolved.read_text(errors="replace")[:150000]), "resolved"
        except OSError:
            return None, "unreadable"

    @staticmethod
    def _verdict_from_text(text: str) -> str | None:
        if not text or "not reviewed yet" in text.lower():
            return None
        latest = re.search(r"Latest verdict\s*:\s*(READY WITH NOTES|READY|BLOCKED)", text, re.IGNORECASE)
        if latest:
            return latest.group(1).upper()
        matches = re.findall(r"\b(READY WITH NOTES|READY|BLOCKED)\b", text, re.IGNORECASE)
        return matches[-1].upper() if matches else None

    def _read_context(self, project: dict[str, Any], root: Path, settings: dict[str, Any]) -> list[dict[str, Any]]:
        sources = []
        for relative in project.get("context_files", []):
            included = settings["sources"].get(relative, False)
            path = root / relative
            row = {"path": relative, "included": included, "exists": False}
            if path.is_symlink() or not path.is_file():
                sources.append(row)
                continue
            try:
                raw = path.read_bytes()
                text = raw.decode("utf-8-sig", errors="replace")
                modified = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc)
                age_days = max(0, (dt.datetime.now(dt.timezone.utc).date() - modified.date()).days)
                row.update({
                    "exists": True,
                    "modified_at": modified.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                    "age_days": age_days,
                    "content_hash": hashlib.sha256(raw).hexdigest(),
                    "self_declared_stale": "stale" in text[:1000].lower(),
                })
                if included:
                    recent = path.name in {"JOURNAL.md", "DECISIONS.md"}
                    limit = 7000
                    row["content"] = text[-limit:] if recent and len(text) > limit else text[:limit]
                    row["excerpt_mode"] = "tail" if recent else "head"
                    row["truncated"] = len(text) > limit
                sources.append(row)
            except OSError as exc:
                row["error"] = type(exc).__name__
                sources.append(row)
        return sources
