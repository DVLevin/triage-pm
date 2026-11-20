# Prototype implementation contract

**Phase:** 1 — mobile KBOS review prototype  
**Date:** 20 Nov 2026  
**Implementation approval:** Dima's 20 Nov Telegram request.

## Runtime

One local Python process serves a same-origin HTML/CSS/vanilla-JS application. PyYAML safely parses frontmatter; SQLite stores only Triage-owned settings, context-snapshot metadata, comments, and decisions. There is no Node build, external analytics, CDN, external font, or external integration.

```text
Configured KBOS roots (read-only)
  → immutable, timestamped snapshot
  → project-specific ticket/context adapters
  → authenticated local JSON API
  → mobile review UI
       ├─ decisions/comments/rules → Triage SQLite only
       └─ no write path → KBOS / Jira / Linear / chat
```

## Identity and versioning

- Canonical ticket key: `project_id + relative_file_path`.
- Display IDs such as `CR-T-085` are not unique and cannot resolve dependencies alone.
- Proposal version: SHA-256 of the exact source bytes.
- Context version: random ID + settings JSON + allowed source paths/hashes + scan timestamp. Raw context excerpts are not persisted in SQLite.
- A changed source hash becomes reviewable again; the old decision remains history.

## Read semantics

- `title`: frontmatter title → first body H1 → display ID, with the source of the title retained.
- `state`: normalized into not_started, active, review, blocked, completed_recorded, closed_without_success_claim, or unknown. Raw state remains visible. Missing state never becomes open or done by prose inference.
- `review verdict`: read from the named verdict target when resolvable. READY/READY WITH NOTES/BLOCKED are review outcomes, not execution states. Artifact freshness is not claimed unless separately checked.
- `progress`: explicit Markdown checkboxes become `recorded_checks=x/y`; no checkboxes means null. DoD length is criterion count, not completion. Emoji tables are not parsed as verified progress.
- `timeline`: only a complete ISO `YYYY-MM-DD` value enters computed schedule signals. Annotated/multi-date values remain due context. “Past recorded due date” uses the explicit local as-of date and known nonterminal states.
- `blockers`: declared blocked state, nonempty `blockers[]`, or explicit Dependencies/Blocked by text. These are reported signals with dates, not verified current incidents. Waiting language and unchecked DoD do not create blockers.
- `impact`: explicit `blocks` metadata or Dependencies/Blocks text. Otherwise “Not stated.”
- Board/open-loop conflicts are shown as source-context warnings; the prototype does not fuzzy-join or overwrite them.

## Approval eligibility

Default hard rules require source intent, all TASK_CARD v1.1 keys, and non-null/nonempty owner, tier, DoD, verdict target, terminal states, and next action for nonterminal cards. Dima can change enforceable switches only by applying a new context snapshot. Legacy or malformed cards remain visible for needs-work review; malformed files have no Approve path.

Local approval means **this version passed this review under this context snapshot**. It does not publish, assign, start, or complete work.

## Storage

SQLite tables:

- `settings`: current per-project source/rule configuration.
- `context_snapshots`: provenance metadata, never source excerpts.
- `decisions`: ticket key/hash, context snapshot, direction, structured reasons, comment, reviewer, timestamp, undo timestamp.
- `comments`: ticket-key discussion independent of proposal version.

A transaction rejects a second active decision for the same ticket content hash. Only the latest active project decision can be undone. Needs-work and approve earn equal points; no leaderboard.

## Privacy and network

- Default bind is loopback. `--lan` is explicit and generates/uses a random pairing token in ignored local storage.
- API requests require `Authorization: Bearer`; the pairing URL hands the token to the app, which stores it locally and strips it from the visible URL.
- No arbitrary path endpoint. Details come only from snapshot keys. No symlink following, transcript directory recursion, URL fetching, or HTML execution of card text.
- Only configured roots/files are read. Source content and runtime data are gitignored.
- LAN HTTP supports online phone viewing. Service workers/app-shell caching require a secure context; confidential ticket data is never cached offline by this prototype.

## Verification boundary

Automated tests cover parsing, malformed-file isolation, duplicate IDs, unknown states, verdict semantics, dates, blockers, source immutability, authentication, decision integrity, undo, comments, and progress. Real browser checks cover phone layouts, context application, decision flow, history/undo, keyboard/focus, reduced motion, dark mode, and network-failure recovery. Results land in `.planning/01-mobile-kbos-prototype/VERDICT.md`.
