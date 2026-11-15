# Initial requirements

Priority means proposed pilot scope, not a committed delivery plan.

## P0 — review prototype

### Review queue

- Show one pending proposal at a time.
- Preserve a deterministic queue order and support project filtering.
- Clearly distinguish fictional/demo proposals from real integrated work.

### Ticket card

Each card must expose:

- Project, ticket/proposal ID, title, summary, priority, owner, estimate, and due context.
- The problem context and why the work exists.
- Original intent excerpt plus a resolvable source reference.
- Acceptance criteria, explicit out-of-scope items, and open questions.
- A visible warning when source evidence is missing or scope is suspected to be invented.
- Relevant commit evidence when available, labeled as evidence rather than proof of completion.
- Access to the complete ticket without losing the reviewer’s queue position.

### Decisions

- **Right swipe / Approve:** the ticket is clear, source-grounded, and ready for publication.
- **Left swipe / Needs work:** the proposal returns for revision; it is not deleted.
- Provide buttons and keyboard alternatives for every gesture.
- Record reviewer, decision, timestamp, and proposal version.
- Prevent duplicate decisions for the same proposal version.
- Support undo of the latest decision.
- Keep a chronological decision history.

### Discussion

- Add and read comments attached to the proposal.
- Preserve comments across decisions and revisions.
- Allow a needs-work reason to travel with the returned proposal.

### Motivation

- Award a small, fixed number of points per completed review.
- Show individual level progress and reviewed count.
- Do not rank people, reward approval over rejection, or treat points as a productivity metric.

### Prototype behavior

- Persist queue decisions, comments, and progress locally.
- Use fictional data until the integration audit is approved.
- Make reset / demo restoration explicit.

## P0 — trust and safety

- Missing required source intent blocks publication and explains what is needed.
- Approving a ticket does not claim its implementation is complete.
- Commit evidence never closes a ticket automatically.
- A newer transcript does not automatically supersede an older one.
- Integration writes must be idempotent and auditable.
- Raw transcripts and secrets stay outside the repository.

## P1 — integrations after separate approval

- Import pending proposals from the existing AI-PM output.
- Resolve Confluence / transcript source links.
- Publish approved tickets to Jira or Linear with their source and discussion links.
- Return needs-work feedback to the proposal producer.
- Read relevant GitHub commits for delivery-evidence review.
- Send Slack notifications without creating another task system.
- Measure review coverage, latency, return reasons, and stale-work signals.

## Explicit non-requirements

- No autonomous approval or closure.
- No leaderboard or team surveillance.
- No automatic historical backlog migration.
- No second active backlog competing with Jira.
- No native mobile requirement for the first prototype.
