---
schema_version: 1.1
id: triage-jira-sync-pilot
created: 2026-11-20
owner: conny
tier: A2
type: integration
state: blocked
terminal_states: [READY, READY WITH NOTES, BLOCKED]
dod:
  - "A dedicated local Jira connector authenticates to the intended Cone Red CR destination without using an interactive AI CLI as the sync engine → evidence: connector tests and live read-only discovery in .planning/02-jira-sync-pilot/VERIFICATION.md"
  - "An approved local proposal can be published or linked exactly once to CR; the mapping stores ticket key, Jira key, content hash, and sync version → evidence: idempotency tests and destination read-back"
  - "Linked tickets expose only currently valid Jira workflow transitions; every external transition is separately confirmed, audited, and read back → evidence: transition tests plus Dima-approved live pilot"
  - "Inbound refresh reconciles Jira execution state with the KBOS record, labels conflicts, and never silently overwrites source intent or KBOS bytes → evidence: conflict fixtures and source-hash checks"
  - "No unmapped ticket gains a status editor; no automatic closure, last-write-wins, cross-project publication, or polling through a paid AI session → evidence: code review and negative tests"
  - "Terminal review is written → evidence: .planning/02-jira-sync-pilot/VERDICT.md with READY, READY WITH NOTES, or BLOCKED and numbered fixes"
scope_not: "No Rust rewrite, no GetDeal/Nous Claw publication, no global field mirroring, no automatic external write on local approval, no leaderboard or approval-rate gamification. Granat is included through its verified partition inside CR, not a separate Jira project."
artifacts: [triage/jira.py, triage/app.py, static/app.js, docs/JIRA_SYNC.md, .planning/02-jira-sync-pilot/VERIFICATION.md]
verdict_file: .planning/02-jira-sync-pilot/VERDICT.md
sources:
  - "Dima, Telegram, 20 Nov 2026: option to change status if applicable; tickets synced with Jira; two-way Jira sync."
  - "Dima, Telegram, 20 Nov 2026 follow-up: Granat lives inside the CR Jira project; Nous Claw and GetDeal remain separate for now."
  - "Read-only Atlassian discovery, 20 Nov 2026: cone-red.atlassian.net exposes Cone Red CR (id 10002) and Personal Tasks PT (id 10003)."
  - "nous_claw/AGENTS.md team-delivery rule: Jira is the client-delivery record and Eugene owns it."
  - "granat/DECISIONS.md 16 Nov 2026: the card is the record and Jira may show it; expansion requires resolving this conflict."
context:
  - "docs/PROTOTYPE_ARCHITECTURE.md — local review authority and read-only source boundary"
  - "CR_Brain/playbooks/TICKETS_AS_FILES.md §Backwards compatibility — explicit ticket mapping and audited state transitions"
  - "~/.claude/projects/-Users-dmytrolevin-Desktop-CR-Brain/memory/reference-slack-atlassian-mcp-via-plugins.md — existing OAuth connector context"
  - "The existing Claude MCP connection is useful for destination discovery, but paid interactive CLI calls are not an acceptable polling or sync backend."
depends_on: []
blockers:
  - "The local Python app has no dedicated Jira credential. Hermes env has no Jira/Atlassian keys; a new broad MCP OAuth grant was not approved."
  - "Granat uses the same CR credential; its label/component partition still needs read-only verification before mapping."
next: "Dima or Eugene provisions a dedicated credential/connection authorized for Cone Red CR only; Conny then implements the connector and deterministic sync tests before any live write."
updated: 2026-11-20
---
# Controlled Jira sync pilot

## Decision structure

- **Jira:** execution state, assignee, resolution, and work activity for the CR pilot.
- **KBOS:** source intent, methodology, context, DoD, and scope.
- **Triage:** local review decisions, needs-work reasons, mapping, and sync audit history.

Approval remains local. **Publish to Jira** is a separate action. Status editing is available only for mapped tickets and uses Jira's current workflow transitions. Inbound changes are shown as a Jira overlay/conflict; the prototype does not rewrite KBOS. Granat is part of CR; Nous Claw and GetDeal remain disconnected.

## Why blocked

Read-only discovery is complete, but there is no dedicated credential for the local app. Reusing Claude's interactive OAuth through repeated paid CLI calls would be slow, costly, and unnecessarily nondeterministic. A new broad OAuth authorization was stopped rather than silently accepted.
