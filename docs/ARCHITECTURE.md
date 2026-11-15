# Conceptual architecture

## Recommended position in the workflow

```text
Meeting transcripts / other inputs
        │
        ▼
Existing AI-PM proposal generator
        │
        ▼
PENDING PROPOSAL STAGING  ◄──── needs-work feedback
        │                           │
        ▼                           │
      TRIAGE                        │
  one card + context                │
  source + evidence                 │
  comments + points                 │
        │                           │
        ├── needs work ─────────────┘
        │
        └── approve ──► Jira / Linear: active system of record
                              │
                              ▼
                       Engineering execution
                              │
                              ▼
                    GitHub delivery evidence
```

**Core recommendation:** pending proposals are not active team tasks. Only approved proposals become Jira issues. This resolves the apparent conflict between “Jira is the source of truth” and a file-based AI-PM generator: files can stage proposals without becoming a second active backlog.

This is a hypothesis for product-owner approval, not an implemented decision.

## Conceptual components

- **Proposal adapter:** reads the existing generator’s pending output without changing it.
- **Review queue:** orders pending proposals and tracks the current review position.
- **Ticket view:** presents context, original intent, scope, questions, and evidence.
- **Decision service:** validates and records approve / needs-work decisions and undo.
- **Discussion service:** keeps reviewer and engineer context attached to the proposal.
- **Progress service:** tracks individual points and levels; it has no authority over work state.
- **Source resolver:** opens the original transcript or Confluence location.
- **Evidence provider:** finds relevant commits and presents them without completion claims.
- **Tracker publisher:** creates or updates Jira or Linear only after an eligible approval.
- **Audit log:** records proposal version, reviewer, decision, comments, and external references.

## Minimum domain objects

- **Proposal:** generated ticket content plus version and pending state.
- **SourceRef:** source location, timestamp/line range, and verbatim intent excerpt.
- **EvidenceRef:** commit or other delivery evidence with its origin and retrieval time.
- **ReviewDecision:** proposal version, reviewer, direction, timestamp, and optional reason.
- **Comment:** author, body, timestamp, and proposal reference.
- **ReviewerProgress:** points and level derived from valid review decisions.

## Integration boundaries

The implementation phase should define small interfaces rather than hard-code a vendor into the review experience:

- `ProposalSource` → pending proposals and revision feedback.
- `SourceResolver` → transcript / Confluence evidence.
- `CommitEvidenceProvider` → read-only GitHub evidence.
- `TicketPublisher` → approved Jira or Linear publication.
- `NotificationGateway` → optional Slack updates.

No technology stack or vendor SDK is selected in this baseline. The target repository audit comes first.

## Trust boundaries

- Source excerpts are verified against the original source before approval is possible.
- AI output is always treated as untrusted proposal content.
- Tracker publication requires an explicit human decision.
- Commit evidence is read-only and cannot change workflow state by itself.
- External writes use idempotency keys so retries do not duplicate Jira issues.
- Credentials live in the eventual runtime’s secret store, never in git.
- Raw transcripts remain in their approved storage location.

## Architecture questions still open

- Where pending proposals currently exist in the real pipeline.
- Whether Jira already contains unreviewed generated issues that need a separate cleanup path.
- Whether comments originate in Triage or remain mirrored from another system.
- Whether the first integration belongs in this repository or the existing AI-PM repository.
