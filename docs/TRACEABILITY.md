# Source traceability

## Primary source

- **Source:** internal AI engineering retrospective
- **Date:** 13 Nov 2026
- **Privacy:** participant names, meeting identifiers, account details, and storage locations are intentionally omitted. The raw transcript is not committed.
- **Quotation policy:** short quotes below are attributed by role; other rows are paraphrases.

## Evidence → product response

| Timestamp | Evidence | Product response |
|---|---|---|
| 01:23–02:41 | An engineer describes contradictory AI-generated tasks, nonexistent work, and unclear expectations. | Full context, source intent, scope boundaries, open questions, and needs-work return loop. |
| 02:41–04:28 | An engineer warns that conflicting transcript history can produce meaningless tasks on a fast-changing project. | Source and as-of context remain visible; newer content must not automatically supersede older intent. |
| 06:28–07:47 | A project lead proposes Jira as the single task source; an engineer values direct transcript links. | Jira publisher boundary plus source resolver; pending proposals remain separate from active work. |
| 12:52–13:20 | The product owner asks for examples of good and bad tasks to improve the pipeline. | Needs-work reasons and discussion become structured feedback for later generator improvement. |
| 13:44 | An engineer: **“the only issue with the tasks right now is that you don’t read them.”** | One-card review queue designed to make the human gate usable. |
| 14:27–14:58 | An engineer recommends checking recent commits when assessing whether a task is done. | Read-only commit evidence, never automatic closure. |
| 15:05 | The product owner: **“Yes, I need to read the tasks.”** | Review coverage and latency become primary product measures. |
| 15:26 | The product owner: **“I will quickly create something like a Tinder app with tasks.”** | Swipe-based approve / needs-work interaction with non-gesture alternatives. |
| 15:49 | The product owner describes getting points and progressing through levels. | Individual points and levels, with no leaderboard or quality-distorting incentives. |
| 31:15 | The product owner confirms switching to Jira for tasks while retaining the need to fix context. | Triage is a review layer, not a replacement backlog or generator rewrite. |

## Interpretation boundary

The retrospective does **not** specify the technology stack, data model, Jira API design, authentication, deployment, visual design, or delivery dates. Those remain open rather than being retroactively attributed to the team.
