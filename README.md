# Triage

**A source-grounded quality gate and feedback loop for AI-generated engineering work.**

> **Status: product baseline. Implementation has not started.**
> This repository currently demonstrates product discovery, requirements, and architecture. It does not claim a working application or customer results.

## Why this project

As engineering teams use AI to turn calls, documents, and project history into tickets, they create a new review bottleneck. Generated tickets may contain irrelevant detail, contradictory requirements, duplicate work, or tasks nobody requested. Engineers must decode and correct tickets before they can start delivering.

The project owner’s recent interviews with more than 10 companies using AI in engineering workflows surfaced recurring frustration with ticket quality and context overload. Public practitioner complaints show the same pattern, but do not establish market size or willingness to pay. See [market evidence](docs/MARKET_EVIDENCE.md).

## The proposed product

Triage presents one proposed ticket at a time with its original source, project context, acceptance criteria, open questions, and relevant delivery evidence. Before a proposal reaches the team’s active backlog, a project manager or team lead can approve it, return it for revision, or discuss unresolved details.

Review decisions become structured feedback: unclear, contradictory, duplicated, stale, already completed, or disconnected from the source. Teams can use that evidence to evaluate and improve future ticket generation instead of repeatedly correcting the same failures.

A swipe-based interface, individual points, and levels are intended to make consistent review feel lighter. The experience rewards useful review and feedback, not raw ticket volume or approval speed.

**AI handles synthesis across large volumes of project context. People retain judgment over intent, scope, priorities, and trade-offs.**

## Decision semantics

- **Approve:** this proposal is clear, source-grounded, and ready for the team.
- **Needs work:** return the proposal for revision with its context and discussion attached.
- **Never implied:** approval does not mean the implementation is complete, and commit evidence never closes work automatically.

## Product documents

- [Product vision](docs/PRODUCT_VISION.md) — problem, users, value, principles, and non-goals
- [Project charter](docs/PROJECT_CHARTER.md) — scope, stakeholders, constraints, and decisions
- [Requirements](docs/REQUIREMENTS.md) — functional and trust requirements
- [Conceptual architecture](docs/ARCHITECTURE.md) — review gate and integration boundaries
- [Current-state baseline](docs/CURRENT_STATE.md) — assumptions and the integration audit
- [Market evidence](docs/MARKET_EVIDENCE.md) — practitioner signals, alternatives, and validation questions
- [Roadmap](docs/ROADMAP.md) — phases with explicit approval gates
- [Source traceability](docs/TRACEABILITY.md) — sanitized retrospective evidence behind major requirements

## Non-negotiables

1. Human review happens before engineers receive generated work.
2. Original intent stays linked to every generated ticket.
3. Triage stages proposals; it must not become another competing active backlog.
4. Commit evidence informs review but never closes work automatically.
5. Raw transcripts, credentials, and client-confidential data do not belong in this repository.

## Next gate

The product owner reviews the baseline and resolves the open decisions in the [project charter](docs/PROJECT_CHARTER.md). Implementation starts only after that explicit go-ahead.

## License

[MIT](LICENSE). The published baseline may be reused and adapted, including commercially, under the license terms.
