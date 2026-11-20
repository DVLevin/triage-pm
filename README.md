# Triage

**A source-grounded quality gate and feedback loop for AI-generated engineering work.**

> **Status: working local mobile prototype.** The app reads configured KBOS task cards and context without modifying them. Review decisions, comments, rules, history, and undo live in a separate local store. Nothing publishes to Jira/Linear or claims implementation completion.

## Open the prototype

```bash
python3 run.py --lan
```

If needed, install the single Python dependency first with `python3 -m pip install -r requirements.txt`. Open the printed pairing URL from a phone on the same Wi-Fi. Full instructions and trust semantics: [prototype guide](docs/PROTOTYPE.md).

The interactive **KBOS Kingdom / Royal Decree** visual concept is available at `/kingdom`. It demonstrates the original pixel-art cast and voice-approval UX with demo data only; it records no audio and performs no Jira writes. See [Kingdom concept](docs/KINGDOM.md).

## Why this project

As engineering teams use AI to turn calls, documents, and project history into tickets, they create a new review bottleneck. Generated tickets may contain irrelevant detail, contradictory requirements, duplicate work, or tasks nobody requested. Engineers must decode and correct tickets before they can start delivering.

The project owner’s recent interviews with more than 10 companies using AI in engineering workflows surfaced recurring frustration with ticket quality and context overload. Public practitioner complaints show the same pattern, but do not establish market size or willingness to pay. See [market evidence](docs/MARKET_EVIDENCE.md).

## The product

Triage presents one proposed ticket at a time with current project context, original intent, owner, next action, acceptance criteria, open questions, delivery impact, and explicit blocker signals. Before a proposal reaches the team’s active backlog, a project manager or team lead can approve it locally or return it for revision with a structured reason and comment.

The mobile web interface provides three focused surfaces:

- **Review:** one readable decision brief, visible controls, optional swipe/keyboard equivalents, and undo.
- **Progress:** review coverage kept separate from recorded execution state, timeline, verdicts, blockers, and data quality.
- **Context:** configurable KBOS sources and deterministic hard rules, versioned for every decision.

Review decisions become structured feedback: unclear, contradictory, duplicated, stale, already completed, wrong owner, or disconnected from the source. That evidence can later improve generation without giving the prototype authority over the active backlog.

**AI handles synthesis across large volumes of project context. People retain judgment over intent, scope, priorities, and trade-offs.**

## Decision semantics

- **Approve:** this exact proposal version passed local review under the recorded context snapshot.
- **Needs work:** return the proposal for revision with reasons and discussion attached.
- **Never implied:** approval does not publish, assign, start, or complete work; commit evidence and source status never close work automatically.

## Product and implementation documents

- [Prototype guide](docs/PROTOTYPE.md) — run, phone pairing, workflow, and data semantics
- [Prototype discovery](docs/PROTOTYPE_DISCOVERY.md) — competitive patterns and real-data findings
- [Prototype architecture](docs/PROTOTYPE_ARCHITECTURE.md) — adapters, identity, storage, privacy, and verification
- [UI design contract](.planning/01-mobile-kbos-prototype/01-UI-SPEC.md) — mobile interaction and visual rules
- [Product vision](docs/PRODUCT_VISION.md) — problem, users, value, principles, and non-goals
- [Project charter](docs/PROJECT_CHARTER.md) — scope, stakeholders, constraints, and decisions
- [Requirements](docs/REQUIREMENTS.md) — functional and trust requirements
- [Conceptual architecture](docs/ARCHITECTURE.md) — review gate and future integration boundaries
- [Current-state baseline](docs/CURRENT_STATE.md) — assumptions and the integration audit
- [Market evidence](docs/MARKET_EVIDENCE.md) — practitioner signals, alternatives, and validation questions
- [Roadmap](docs/ROADMAP.md) — phases with explicit approval gates
- [Source traceability](docs/TRACEABILITY.md) — sanitized retrospective evidence behind major requirements

## Non-negotiables

1. Human review happens before engineers receive generated work.
2. Original intent stays linked to every generated ticket.
3. Triage stages proposals; it must not become another competing active backlog.
4. Commit evidence informs review but never closes work automatically.
5. Raw transcripts, credentials, runtime source snapshots, and client-confidential data do not belong in this repository.
6. Missing facts remain visible as unknown; the interface never invents certainty.

## Verification

```bash
python3 -m unittest discover -s tests -v
node --check static/app.js
```

The current build card and terminal verdict live in `tasks/triage-mobile-kbos-prototype.md` and `.planning/01-mobile-kbos-prototype/VERDICT.md`.

## License

[MIT](LICENSE).
