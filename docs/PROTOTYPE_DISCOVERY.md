# Mobile prototype — discovery and competitive patterns

**Date:** 20 Nov 2026  
**Decision owner:** Dima approved implementation in the 20 Nov Telegram request.  
**Evidence standard:** vendor material shows advertised behavior, not proof of customer outcomes.

## Format decision

**Build a mobile-first local web app with PWA metadata.** A native app and a Telegram Mini App add distribution, public hosting, and credential work without improving the core review hypothesis. A local web app can read Dima's KBOS directly, run on his laptop, and open on his phone over the LAN.

PWA manifest/service-worker support is included where the browser permits it. Plain HTTP LAN access is not represented as guaranteed offline installation; installability and offline behavior need a secure-context test or HTTPS later.

## What existing products establish

- **[Linear Triage](https://linear.app/docs/triage):** incoming issues can be accepted, declined, marked duplicate, snoozed, or commented on before entering a team's workflow. This validates the pre-backlog gate, not our exact interface.
- **[Linear Mobile Diffs / Guided Reviews](https://linear.app/now/mobile-diffs):** mobile review starts with what changed and why, keeps the originating issue beside the work, and lets feedback return to an agent. This supports a guided, source-connected reading order.
- **[Rills](https://rills.ai/integrations/linear):** advertises mobile swipe approval for proposed Linear actions. It establishes precedent for phone approval; its marketing also demonstrates why consequential actions need explicit state and a human veto.
- **[SwipeFlow](https://swipeflow.io/features):** advertises approve/reject/request-changes, revision history, and feedback returning to the producer. These are established patterns, not defensible novelty.
- **[Accessibility guidance on swipe interfaces](https://a11ypatterns.org/?r=/patterns/gesture-interface):** critical gestures need visible alternatives and recoverability. Therefore buttons, keyboard commands, and undo are first-class; swipe is optional.
- **[ServiceNow mobile swipe guidance](https://horizon.servicenow.com/native-mobile/components/mobile-component-swipe-actions):** swipe is discouraged when a decision needs more context. Triage therefore presents the evidence before the decision bar rather than asking for blind swipes from a list.

## Differentiation worth testing

Not "Tinder for tickets." The testable combination is:

1. Current KBOS context beside the proposed work.
2. TASK_CARD v1.1 translated into a human decision brief: why, source, owner, next action, scope, DoD, and downstream impact.
3. Structured needs-work reasons that can later improve generation.
4. Honest delivery signals: declared states and dates, explicit blockers, source freshness, and unknowns.
5. Local review persistence without silently modifying the active source of truth.

## Observed local-data implications

A 20 Nov read-only audit found:

- **CR_Brain:** 64 non-template v1.1 cards under `tickets/`; declared states include todo, in-progress, review, in_review, and done. Ten IDs occur in more than one epic folder, so file path + content hash—not ID alone—must identify a proposal version.
- **Granat:** 12 non-template v1.1 cards under `tickets/`; current cards carry owners, priorities, states, dates, DoD, dependencies, and sources. Some body tables contain finer-grained work than the card itself.
- **Nous Claw:** 73 non-template v1.1 cards across `tasks/` and `conny_notes/tasks/`; no declared `state` in the audited cards. The UI must show "state not declared" rather than inventing delivery completion.
- **GetDeal:** no parseable non-template v1.1 cards under the current `tickets/` adapter scope; malformed/template files are excluded and reported. Other historical task-shaped files are not silently promoted into active work.

These counts are an audit snapshot, not hard-coded application data.

## UX rules derived from the evidence

- First screen answers: **which project, what needs review, what is at risk, what changed most recently.**
- One ticket at a time; vertical reading remains primary. No horizontal gesture hijacking of the whole page.
- Lead with title, state, owner, and **why this exists**. Then source intent, delivery impact, DoD, context, and full source.
- Approve is not "done"; Needs work is not deletion. Both decisions attach to the exact content hash.
- Show review progress separately from execution progress. Never combine them into one misleading percentage.
- Unknown timeline is labeled unknown. Overdue means only "recorded due date passed"; it is not a prediction of project failure.
- Raw context stays on the laptop and is never embedded in committed fixtures or documentation.
