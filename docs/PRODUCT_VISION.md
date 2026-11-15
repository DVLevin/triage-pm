# Product vision

## One-liner

**Triage turns reviewing AI-generated tickets from a backlog chore into a fast, source-grounded decision flow.**

## Problem

An internal engineering retrospective on 13 Nov 2026 exposed a broken review loop:

- Generated tasks can contradict prior agreements or describe work nobody requested.
- Engineers lose confidence when the expected outcome and current source of truth are unclear.
- Context is spread across transcripts, tasks, chat, and repositories.
- Completed work can remain open when ticket state is not checked against delivery evidence.
- The accountable reviewer does not reliably read generated tickets before the team acts on them.

The root problem is not only generation quality. It is **the absence of a usable human approval gate**.

## Vision

Make the safest workflow the easiest one:

1. A proposed ticket arrives with its original intent and full context.
2. The reviewer sees one card, not another backlog.
3. A right swipe approves the ticket; a left swipe returns it for revision.
4. Questions and discussion remain attached to the ticket and its decision.
5. Source and commit evidence remain inspectable, while humans retain authority.
6. Points and levels make consistent review visible without turning work into a competition.

## Users and jobs to be done

**Primary user — accountable product or engineering leader**

“When AI creates work, I want to approve or return it in a few focused minutes, with enough context to trust my decision, so engineers receive clear tasks without requiring me to read the whole backlog.”

**Secondary users — PM / team lead**  
“I want generated proposals to become coherent, deduplicated, source-linked tickets before publication.”

**Beneficiaries — engineers**  
“I want one current ticket, visible acceptance criteria, original intent, and a place to resolve ambiguity.”

## Product principles

- **Review before execution.** Unreviewed generation is a proposal, not team work.
- **Source before synthesis.** The original words remain available beside the generated interpretation.
- **One active system of record.** Triage coordinates review; it must not become another competing backlog.
- **Evidence supports, humans decide.** Transcript and commit signals do not auto-approve or auto-close.
- **Fast enough to use.** A card should be understandable before the reviewer’s attention is gone.
- **Return, do not bury.** “Needs work” creates a visible revision loop, not silent rejection.

## Non-goals

- Replacing Jira, Linear, Confluence, GitHub, or the existing transcript pipeline.
- Fully autonomous ticket approval, closure, or assignment.
- A native mobile app in the first phase.
- A gamified leaderboard or productivity surveillance.
- Solving every AI-PM generation problem in the review interface.

## Success measures

These are measurement definitions, not current results:

- **Review coverage:** generated proposals reviewed before team assignment ÷ all generated proposals.
- **Review latency:** proposal created → human decision.
- **Source coverage:** approved tickets with resolvable source intent ÷ all approved tickets.
- **Return reasons:** missing source, contradiction, duplicate, stale state, unclear scope, other.
- **Stale-work rate:** open tickets with credible completion evidence requiring review.
- **Engineer clarity:** recurring team rating of ticket clarity and context sufficiency.

Targets are set only after a baseline is measured.
