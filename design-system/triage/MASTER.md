# Triage design system — mobile review instrument

> Curated 20 Nov 2026 after the automated tool returned an unrelated e-commerce ratings/Buy pattern. That pattern is explicitly rejected. The applicable database findings are touch-first mobile, dense operations, neutral surfaces, and semantic status colors.

## Product character

**Calm field instrument, not a backlog and not a swipe toy.** Flat surfaces, crisp borders, compact metadata, readable prose, almost no decorative motion. Source and state labels do more work than color.

## Semantic tokens

### Light
- Background `#F3F4F1`; surface `#FFFFFF`; raised `#E9EEEA`
- Text `#17231F`; secondary `#56645F`; border `#D7DDD8`
- Brand/action `#175A4C`; on-action `#FFFFFF`
- Approve `#0B6248`; on-approve `#FFFFFF`
- Needs-work surface `#F8E9E4`; needs-work text `#873323`
- Warning surface `#FFF4D6`; warning text `#765000`
- Error `#A83232`; focus `#2864DC`

### Dark
- Background `#101714`; surface `#18211D`; raised `#222E28`
- Text `#F1F5F2`; secondary `#B1BDB6`; border `#35433C`
- Brand/action `#8BD4B8`; on-action `#10231B`
- Approve `#9DE2C2`; on-approve `#0B3527`
- Needs-work surface `#3A2521`; needs-work text `#FFC5B8`
- Warning surface `#392F17`; warning text `#F5D78E`
- Error `#FFB4AB`; focus `#9BB8FF`

## Typography

- System stack only: `-apple-system`, BlinkMacSystemFont, `Segoe UI`, sans-serif. No network font dependency.
- Body 16px / 1.55 / 400; secondary 14px / 1.45; labels 12px / 1.3 / 650 with modest letter spacing.
- Ticket title 26px / 1.18 / 720; screen title 30px / 1.12 / 740 on larger phones.
- Numeric counts use tabular figures. Text wraps rather than truncating the task title or why.

## Spacing and shape

- Scale: 4, 8, 12, 16, 24, 32px.
- Mobile gutter 16px; desktop content max 1180px; long prose max 70 characters.
- Card radius 20px; compact controls 12px; pills fully rounded.
- Borders and one consistent low elevation level; no glass, glow, gradients, or decorative animation.

## Interaction

- Minimum targets 48×48px with at least 8px separation.
- Bottom tabs: Review, Progress, Context. Fixed decision bar sits above the tab bar and reserves safe-area/content space.
- Approve and Needs work are visible labeled buttons. Swipe may be added only as an equivalent shortcut after mobile usability passes.
- Async controls disable and show explicit feedback. Decisions offer Undo.
- Focus ring 3px; keyboard navigation follows visual order; dialogs trap focus and close with Escape.
- `prefers-reduced-motion` removes nonessential transitions. No horizontal scroll, no zoom disabling, safe-area insets required.

## Iconography

One inline SVG family: 24px grid, 1.8px rounded strokes. Every structural icon has an accessible label or adjacent text. No emoji icons.

## Information order

1. Project + pending count + recorded snapshot time.
2. Ticket title + state/priority.
3. Why this exists.
4. Owner + literal next action + due context.
5. Evidence strip: sources, DoD, explicit blockers, content/review warnings.
6. Expandable impact, acceptance, sources, context, scope, full record.
7. Fixed Needs work / Approve decision bar.

Points, levels, upcoming-card decks, and context settings never occupy the first review viewport.
