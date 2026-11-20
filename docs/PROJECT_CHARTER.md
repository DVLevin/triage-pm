# Project charter

## Objective

Establish the smallest trustworthy review layer between AI-generated ticket proposals and the team’s active backlog.

## Current deliverable

**Superseded 20 Nov 2026:** Dima explicitly approved a working mobile prototype connected read-only to real local KBOS projects. The current deliverable is the local web/PWA prototype described in `docs/PROTOTYPE.md`, with Triage-owned local review persistence and no external publication.

The original docs-only baseline below remains the historical Phase 0 record. No production integration or customer result is claimed.

## Original Phase 0 deliverable

Phase 0 delivered only the aligned product baseline: vision, requirements, conceptual architecture, current-state assumptions, roadmap, and source traceability. No application, integration, deployment, or production claim belonged to that phase.

## Initial scope

**Included later, after approval:**

- One-at-a-time ticket review with swipe and accessible button equivalents.
- Full ticket context and source intent.
- Approve / needs-work decisions, comments, history, and undo.
- Points and levels for the individual reviewer.
- Read-only source and commit evidence before any write integration.
- Controlled publication into the chosen system of record.

**Excluded for now:**

- Changes to the AI ticket generator itself.
- Automatic closure or implementation-status claims.
- Migration of historical Jira or file-based backlogs.
- Broad team rollout.
- Raw transcript storage in this repository.

## Stakeholders

- **Decision owner:** the product owner.
- **Primary workflow owner:** the PM / person creating or publishing generated tickets.
- **Review users:** the product owner first, then other accountable leads if the pilot succeeds.
- **Consumers:** engineers receiving approved work.
- **Integration owners:** owners of the existing AI-PM, Jira, Confluence, and GitHub workflows.

## Constraints

- Jira was named the team’s intended task source of truth in the retro.
- The existing AI-PM documentation describes file-based generated tickets and human review before commit.
- These two positions must be reconciled architecturally, not hidden.
- Transcript content may be confidential; only sanitized requirements belong in the repository.
- Integration choices depend on inspecting the real target repository and current Jira workflow.

## Decisions needed before implementation

1. **Review position:** should Triage review proposals **before Jira publication** or review already-created Jira issues?  
   *Recommendation:* before publication, so unreviewed generation never becomes team work.
2. **Proposal staging:** should pending proposals live in the existing file-based vault, a new staging store, or another current system?  
   *Recommendation:* reuse the existing pipeline if its real implementation supports a pending state.
3. **Integration home:** which existing repository should own production integration, and what remains in this standalone repository?
4. **Decision propagation:** do comments and needs-work reasons return to the generator, Jira, or both?
5. **Pilot boundary:** one project, one reviewer, and one proposal source — which exact combination?

## Baseline acceptance

This phase is complete when the product owner approves the vision and records answers or explicit deferrals for decisions 1–5. No build work is implied by delivery of these documents.
