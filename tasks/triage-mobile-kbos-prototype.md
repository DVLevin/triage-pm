---
schema_version: 1.1
id: triage-mobile-kbos-prototype
created: 2026-11-20
owner: conny
tier: A1
type: build
state: done
terminal_states: [READY, READY WITH NOTES, BLOCKED]
dod:
  - "The local app lists configured KBOS projects and reads real TASK_CARD v1.1 files without changing their bytes → evidence: automated adapter tests plus source-hash check in .planning/01-mobile-kbos-prototype/VERIFICATION.md"
  - "On a phone-sized viewport Dima can select a project, inspect sourced context, change context/hard-rule settings, review one readable ticket, and see review/delivery signals and blockers → evidence: mobile browser run in .planning/01-mobile-kbos-prototype/VERIFICATION.md and gitignored screenshots under .runtime/verification/"
  - "Approve, needs-work, comments, rules, history, and undo persist in Triage's own local store; repeated decisions against the same content version are rejected → evidence: automated API/store tests"
  - "No Jira, Linear, Telegram, Slack, or KBOS write occurs; network access requires the runtime token and source data is not copied into git → evidence: code inspection, API tests, and git status"
  - "The app runs from a documented command and is reachable on the laptop's LAN address; the private GitHub remote contains the verified commit → evidence: live HTTP readback and git ls-remote"
scope_not: "Not production hosting, multi-user auth, a native app, a Telegram Mini App, Jira publication, AI-generated summaries, automatic task closure, or a claim that file metadata proves delivery progress."
artifacts: [app/, static/, tests/, docs/PROTOTYPE.md, .planning/01-mobile-kbos-prototype/01-UI-SPEC.md]
verdict_file: .planning/01-mobile-kbos-prototype/VERDICT.md
sources:
  - "Dima, Telegram, 20 Nov 2026: proceed with the GitHub ticket-review repo and make a usable mobile prototype with project selection, KBOS context, context cleanup/hard rules, readable task-methodology review, timeline, and blockers."
  - "docs/PROJECT_CHARTER.md — original implementation gates"
  - "docs/REQUIREMENTS.md — review, trust, persistence, and accessibility requirements"
context:
  - "docs/PRODUCT_VISION.md and docs/ARCHITECTURE.md — source-grounded human review; Triage is not another active backlog"
  - "~/Desktop/nous_claw/conny-home/templates/TASK_CARD.md — sources answer why; context answers what to load first; null is preferable to invention"
  - "~/Desktop/nous_claw/conny-home/VERDICT_PROTOCOL.md — this file names where the review terminates"
  - "Real local KBOS roots are supplied through ignored config.local.json; private source content must not be committed."
next: "Phase 1 accepted by Dima on 20 Nov 2026. Continue with tasks/triage-jira-sync-pilot.md after its CR credential blocker is resolved."
updated: 2026-11-20
---
# Build the mobile KBOS ticket-review prototype

## Why

The existing baseline correctly stopped before implementation. Dima's 20 Nov request explicitly opens that gate and expands the first useful prototype from fictional swipe cards to a **read-only KBOS-connected review surface**. The human problem is not "approve faster" alone: Dima needs enough current project truth to judge whether a proposed task deserves to exist, who owns it, and what it affects.

## Product choice

Build a mobile-first local web application with PWA metadata, not a native app or Telegram Mini App. It runs on Dima's laptop and is opened from a phone on the same network. The prototype uses real local source files at runtime and keeps every review artifact in its own SQLite database.

## Trust boundary

Approving here means **reviewed locally**, not published or completed. Source files remain the authority. Missing fields, stale context, duplicate IDs, and uncertain schedule signals are shown explicitly rather than repaired with invented content.
