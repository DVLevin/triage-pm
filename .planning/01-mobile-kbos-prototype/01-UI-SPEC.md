---
phase: 1
slug: mobile-kbos-prototype
status: approved
shadcn_initialized: false
preset: none
created: 2026-11-20
---
# Phase 1 — UI Design Contract

> GSD-compatible contract produced manually because `gsd-sdk` is unavailable. Independent UX findings from 20 Nov are incorporated.

## Design System

- Tool: semantic CSS tokens; no UI framework or build step
- Component library: native HTML controls + vanilla JS
- Icons: inline SVG, Lucide-style 24px rounded outline
- Fonts: native system stack; no external requests
- Canonical tokens: `design-system/triage/MASTER.md`

## Screens

### Project selection
First launch shows four configured projects with pending count, recorded snapshot time, parser warnings, and latest card update. Later launches restore the selected project, tab, ticket, and scroll position. A project switcher remains in the header.

### Review
The first viewport identifies project, queue position, snapshot time, title, state/priority, why, owner/next, and evidence health. One card only. Vertical reading; no deck or horizontal content gesture. Native `<details>` accordions expose delivery impact, DoD/recorded checks, source intent, load-first context, open questions, scope fence, artifacts, and the complete record.

The fixed action bar has **Needs work** and **Approve**. Approve is disabled with a visible reason when the current hard rules fail. Needs work opens a bottom sheet requiring at least one structured reason and allowing a comment. Every decision produces a persistent Undo affordance.

### Progress
Separate blocks for review coverage, recorded work states, recorded timeline, explicit/reported blockers, downstream impact, data-quality warnings, review history, and noncompetitive reviewer points. No single blended health score.

### Context
A recorded KBOS snapshot lists only configured source files with modified time, freshness/self-declared-stale warnings, and bounded excerpts. Source checkboxes and enforceable hard-rule switches are edited as a draft. **Apply to new review snapshot** commits the settings, rescans, and versions the basis; existing decisions retain their prior snapshot ID. No source edit control exists.

## Spacing Scale

- xs 4px — inline icon gaps
- sm 8px — compact metadata
- md 12px — chips and tight groups
- lg 16px — mobile gutters/default groups
- xl 24px — card and section padding
- 2xl 32px — major section breaks

## Typography

- Body 16px / 400 / 1.55
- Label 12px / 650 / 1.3
- Heading 26px / 720 / 1.18
- Display 30px / 740 / 1.12

## Color

Semantic tokens live in MASTER.md. Brand green identifies Triage and selected navigation; approve green is reserved for the approve action; rust is reserved for needs-work; amber is reserved for warnings. State is always accompanied by text.

## Copywriting Contract

- Primary CTA: **Approve proposal**
- Secondary CTA: **Needs work**
- Context CTA: **Apply to new review snapshot**
- Empty queue heading: **Review queue clear**
- Empty queue body: **No unreviewed cards match this snapshot. Refresh KBOS or review the decision history.**
- Empty project: **No readable task cards in this scope** + parser/scope guidance
- Error: **Couldn’t read this snapshot. Retry; your local decisions are unchanged.**
- Approval semantics: **Local review only — nothing is published or marked complete.**
- Unknown value: **Not stated** / **State not declared**, never a guessed value
- Timeline label: **Past recorded due date**, not “project late”
- Reset/offline: no offline card cache by default; **Offline snapshot unavailable** + Retry

## Accessibility and device contract

- 375px and 390px phone portrait, phone landscape, 768px, 1024px, 1440px
- 48px targets; visible focus; labeled controls; heading order; screen-reader live decision feedback
- Light and dark token pairs; reduced motion; 200% text without horizontal overflow
- Safe-area padding around fixed action/tab bars
- App shell may cache only in a secure context; confidential card data is not cached offline

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS — decision semantics and unknowns are explicit
- [x] Dimension 2 Visuals: PASS — source-first hierarchy, no swipe-first or ratings pattern
- [x] Dimension 3 Color: PASS — semantic tokens plus text labels; runtime contrast test remains required
- [x] Dimension 4 Typography: PASS — native readable scale and wrapping
- [x] Dimension 5 Spacing: PASS — 4px rhythm, safe areas, fixed-bar offsets
- [x] Dimension 6 Registry Safety: PASS — no registry or third-party blocks

**Approval:** approved 2026-11-20 for implementation; final implementation verification is separate in VERDICT.md.
