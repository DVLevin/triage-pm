# Phase 1 verification — mobile KBOS prototype

**Date:** 20 Nov 2026  
**Verifier:** Conny + independent UX/architecture reviewers  
**Source boundary:** real configured KBOS roots; all browser writes used an isolated `.runtime/browser-test.db`, never Dima's real review database.

## Automated evidence

Command: `python3 -m unittest discover -s tests -v`

- 14/14 tests passed on 20 Nov 2026.
- Real-source test hashed every configured Markdown input before and after scanning; all hashes matched.
- GetDeal's three malformed task cards were isolated while 23 valid legacy cards remained readable.
- Duplicate CR display IDs remained separate by project + path; ambiguous dependency references did not become confirmed blockers.
- Unknown Nous Claw states stayed unknown; verdict READY WITH NOTES remained separate from execution state.
- Approve, needs-work validation, duplicate-decision rejection, comments across revisions, undo, context-version rejection, points, authentication, path traversal, and static serving passed.

Command: `node --check static/app.js`

- Passed; no JavaScript syntax errors.

## Real snapshot smoke

The 20 Nov adapter smoke read all four configured projects successfully:

- Cone Red: v1.1 + explicitly labeled legacy cards; duplicate display IDs surfaced.
- Granat: 12 v1.1 cards, no parser errors.
- GetDeal: 23 legacy cards readable, three task-shaped malformed files reported individually.
- Nous Claw: 73 cards across the two configured task stores; undeclared states not inferred from prose.

These are dated scan results, not hard-coded application content.

## Browser evidence

Screenshots are ignored because they contain real task content:

- `.runtime/verification/review-light-390.png`
- `.runtime/verification/review-dark-390.png`
- `.runtime/verification/context-light-390.png`
- `.runtime/verification/progress-light-390.png`

Verified in a real browser with touch/mobile emulation:

- Project selection and all four real project summaries.
- Granat review: why, owner, due, next action, evidence strip, expandable full record, and fixed Needs work / Approve controls.
- Needs-work reason required; reason + comment saved; pending count changed; decision persisted after reload.
- Undo restored the exact ticket and preserved an undone history row.
- Approval persisted after reload; context application created a new snapshot while retaining prior decision history.
- GetDeal legacy approval was disabled with the missing fields named; parser errors appeared in Progress.
- 390×844 and 375×667 portrait, 844×390 landscape, and 1440×1000 desktop: no horizontal document overflow.
- All visible buttons/form controls/summary targets measured at least 44px in the phone audits.
- Dark mode and reduced-motion media queries were active and rendered successfully.
- Offline refresh returned feedback and retained the current snapshot; online refresh recovered.
- Secure localhost registered the service worker and cached only the app shell; no `/api/` response was cached.

## Contrast evidence

Computed WCAG relative-luminance ratios for all primary text, secondary text, brand, warning, needs-work, and action pairs in both themes. Every pair passed 4.5:1; the lowest measured pair was light secondary/background at **5.62:1**.

## Runtime evidence

- Live health endpoint returned HTTP 200 on the documented local port.
- Unauthenticated bootstrap returned HTTP 401.
- Pairing token is stored in ignored `data/access-token` with mode 600.
- Request-line logging is suppressed so the pairing query is not copied into server logs.

## Fix verification after independent BLOCKED review

The 20 Nov recipient-eyes review blocked the first render on action-label contrast and first-viewport information order. Only those findings and its notes were rechecked:

- Settled computed light colors are Needs work `rgb(135,51,35)` on `rgb(248,233,228)` (**7.03:1**) and Approve proposal white on `rgb(11,98,72)` (**7.36:1**). The earlier light capture had caught an unsettled theme transition.
- At 390×844 on the real long Granat card, action-bar top is 703px; title bottom 333.17px, why 467.97px, owner/due 542.75px, next action 655.13px, and evidence health 697.72px. All required decision context is visible before the controls. Long why/next content has explicit full-text disclosures.
- Full why expands on tap; the CTA now says **Approve proposal**.
- Project, ticket, tab, and a deliberate 500px scroll position restore after navigation.
- Context excerpt summaries measure 48px. Checkbox inputs sit inside 48px+ labels, so the whole row is the touch target.
- The four verification screenshots were recaptured only after theme settling.

## Not checked / not claimed

- No physical phone was used in this session; browser mobile emulation and LAN listener checks were used.
- No externally reachable HTTPS deployment, offline card cache, Jira/Linear publication, or AI-generated summary was built.
- Recorded source states, blockers, dates, and checkboxes were not independently validated against external delivery systems.
- Phase 1 product exit still requires Dima to use the prototype and confirm that review is faster than a conventional backlog.
