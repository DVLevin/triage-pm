# Engineer recipient view

Open `/engineer` directly, use **View this exact task as the engineer** on a Review card, or switch from Royal Decree. The project + ticket key is preserved through every lens.

## Two deliberately separate modes

### KBOS now

The current card rendered as an engineer-facing action brief. Structured fields come from the authenticated current snapshot with no AI rewrite. The original Markdown and content hash are available at the bottom for comparison.

### Jira preview

A deterministic proposed payload from the same fields. It does **not** fetch or create a Jira issue and does not claim to reproduce Jira's eventual layout, permissions, or workflow. Live Jira validation remains part of the connector pilot.

The unapproved Royal Decree sample changes, including Friday, do not leak into either current-task view.

## What Dima can validate

- Exact title, owner/assignee, current due, state, and priority
- Literal next action
- Why the task matters and direct why evidence
- Binary Definition of Done
- Delivery impact and dependencies
- Blocker signals and open questions
- Load-first references and current KBOS context excerpts
- Scope fence, artifacts, and source intent
- Original Markdown, path, and content hash

The **Can they start?** preflight measures field coverage and flags gaps/past dates. It does not claim engineer comprehension; only the recipient can verify that.

## Verified 20 Nov 2026

- Real Granat ticket: literal next action, why, 4 DoD, 4 sources, declared impact, 6 context files, original record.
- KBOS/Jira mode toggle preserves the same ticket and contains no sample Friday change.
- Review → Engineer → Royal Decree → Engineer preserves exact ticket identity.
- 390×844 and 320×640 have no horizontal overflow; mode targets are 46px.
- Existing 14 tests and JavaScript syntax checks pass.

No voice recording, Jira write, KBOS write, or delivery/completion claim occurs.
