# Current-state baseline

This document separates observed assets from assumptions. It is not an implementation audit, and it intentionally omits private repository paths, account details, meeting identifiers, and transcript locations.

## Known inputs and documentation

- **Retrospective evidence:** an internal engineering retrospective on 13 Nov 2026 documents problems with generated ticket quality and review behavior. The raw source remains private.
- **AI-PM design:** existing internal documentation describes transcript extraction → ticket synthesis → file-based ticket generation → human review before commit.
- **Provenance rule:** the documented approach requires source location, raw intent, interpreter, and as-of date; missing sources must be flagged rather than invented.
- **Ticket-file convention:** an existing internal playbook documents a file-based ticket substrate.
- **Team direction from the retrospective:** Jira for active tasks, Confluence pages linked to transcripts, Slack for communication, and GitHub history as delivery evidence.

## Important distinction

The AI-PM documentation proves a **documented design**, not the current state of its code. Before implementation, we must verify which stages actually run, their input/output schemas, and whether a pending-proposal state exists.

## Apparent conflict to resolve

- Retrospective direction: **Jira is the single active task source of truth.**
- Existing AI-PM design: **generated tickets are written as files before human review and commit.**

Recommended reconciliation: files may hold **pending proposals and audit history**, while Jira holds **approved active work**. The product owner must approve this interpretation.

## Audit required before any build

1. Identify the actual AI-PM producer repository, entry point, and current output location.
2. Inspect one real generated proposal and its source references without copying confidential content into this repo.
3. Determine whether pending, approved, returned, and published states already exist.
4. Inspect the current Jira project/workflow and whether generated issues are already published before review.
5. Confirm the Confluence/transcript linking mechanism and access model.
6. Confirm how ticket IDs appear in GitHub commits and whether evidence retrieval already exists.
7. Decide which repository owns production integration and which owns the standalone review experience.
8. Record available credentials by name and location only; never copy secrets into product documents.

## Not yet established

- Technology stack for the production app.
- Hosting and authentication model.
- Jira / Confluence / GitHub write permissions.
- Historical backlog migration need.
- Multi-user or multi-project rollout scope.
