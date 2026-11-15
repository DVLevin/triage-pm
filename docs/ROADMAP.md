# Product roadmap

No dates are committed here. Each phase has an explicit gate.

## Phase 0 — product baseline (current)

**Deliverables**

- Product and project vision.
- Initial requirements and decision semantics.
- Conceptual architecture and current-state assumptions.
- Source traceability and integration audit checklist.

**Exit gate:** the product owner approves the baseline and rules on review position, proposal staging, integration home, feedback propagation, and pilot boundary.

## Phase 1 — isolated review prototype

**Deliverables**

- Fictional proposal data only.
- One-card review, swipe plus accessible controls, full ticket view, comments, undo, history, points, levels, and local persistence.
- Basic tests for decision integrity, undo, comment attachment, and progress calculation.

**Exit gate:** the product owner can review the complete fictional queue without instructions and confirms the interaction is faster than reading a conventional backlog.

## Phase 2 — read-only integration

**Deliverables**

- Real pending-proposal import from the approved source.
- Source-link resolution and read-only GitHub evidence.
- No Jira writes and no automatic status changes.
- Baseline measurement of review latency, coverage, and return reasons.

**Exit gate:** source links and proposal states reconcile with the real pipeline; no duplicate active backlog is introduced.

## Phase 3 — controlled publication pilot

**Deliverables**

- Approved proposals publish to one approved Jira or Linear team/project.
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
