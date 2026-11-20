# Product roadmap

No dates are committed here. Each phase has an explicit gate.

> **20 Nov 2026:** Dima approved implementation and real read-only KBOS sources. Phase 1 therefore combines the isolated review overlay with local read-only adapters. External publication and feedback propagation remain in Phase 3; no external writes were added.

## Phase 0 — product baseline (approved)

**Deliverables**

- Product and project vision.
- Initial requirements and decision semantics.
- Conceptual architecture and current-state assumptions.
- Source traceability and integration audit checklist.

**Exit gate:** the product owner approves the baseline and rules on review position, proposal staging, integration home, feedback propagation, and pilot boundary.

## Phase 1 — mobile KBOS review prototype (accepted 20 Nov 2026)

**Deliverables**

- Real read-only KBOS proposal/context import with explicit v1.1 and legacy profiles.
- Mobile-first Review / Progress / Context surfaces.
- One-card review, swipe plus accessible controls, full ticket view, comments, undo, history, points, levels, and local persistence.
- Configurable source inclusion and deterministic hard rules, versioned with each review.
- Tests for decision integrity, undo, comment attachment, source immutability, and progress calculation.

**Exit gate:** **PASSED 20 Nov 2026.** Dima marked the phone prototype done. Independent mobile review was READY and 14 tests passed.

## Phase 2 — read-only integration

**Deliverables**

- Real pending-proposal import from the approved source.
- Source-link resolution and read-only GitHub evidence.
- No Jira writes and no automatic status changes.
- Baseline measurement of review latency, coverage, and return reasons.
- Read-only Atlassian destination discovery: Cone Red CR and Personal Tasks PT verified 20 Nov 2026; no other projects claimed.

**Exit gate:** source links and proposal states reconcile with the real pipeline; no duplicate active backlog is introduced.

## Phase 3 — controlled Jira sync pilot (next; blocked on dedicated CR credential)

**Deliverables**

- Approved proposals publish or link to one approved Jira project through a separate explicit action.
- Mapped tickets expose valid Jira workflow transitions; inbound Jira state reconciles without overwriting KBOS intent.
- Needs-work feedback returns to the proposal producer.
- Idempotent writes, audit history, failure handling, and rollback procedure.
- One reviewer, one project, one proposal source.

**Exit gate:** engineers confirm improved clarity and no unreviewed generated proposal reaches their active queue.

## Phase 4 — evaluate and expand

**Deliverables**

- Compare review coverage, latency, source coverage, return reasons, stale-work signals, and engineer clarity against baseline.
- Tune card density and points based on observed use.
- Decide whether additional projects, reviewers, or mobile packaging are justified.

**Exit gate:** expansion follows measured value, not feature volume.
