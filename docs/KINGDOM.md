# KBOS Kingdom — Royal Decree concept

Open `/kingdom` on the running local server, or use **Discuss this exact ticket with Conny** at the bottom of a real Review card. This is an interactive **real-ticket / demo-action concept**, not a voice or Jira implementation. It reads the authenticated current snapshot, records no audio, and performs no writes.

## What the concept demonstrates

- Original adult DnD-inspired pixel-art presentation.
- The real selected ticket's title, owner, current due, why, direct why evidence, delivery impact, source intent, load-first references, and current KBOS context excerpts.
- Conny's adviser persona with profanity and dark tavern humor, after the actual decision context.
- A clearly marked **sample text command**, not a claimed recording or Parakeet transcript, transformed into proposed changes.
- Per-change provenance: ticket/source, voice, inference, or explicit user choice. Friday is explicitly attributed only to the sample voice and never to KBOS.
- Ambiguity gating: approval remains disabled until the user chooses an exact date.
- Approve/reject interaction feedback without pretending that execution happened.
- Clear `LOCAL · DEMO ONLY` wording for the concept; production must not claim read-only once writes exist.

## Art and copy rules

- Original characters and assets only; franchise references describe energy, not copied characters.
- Monsters represent scope creep, stale evidence, blockers, and bureaucracy—not employees.
- 18+ means adult/profane/dark humor, not explicit imagery.
- Humor belongs in adviser copy. Approval, source, status, and execution controls stay unambiguous.
- The High Arbiter is symbolic, not Dima's likeness. Employee likeness avatars require supplied reference photos.

## Production path

1. Private HTTPS for phone microphone capture.
2. Authenticated audio upload with size/duration limits and a local-only retention policy.
3. `~/Desktop/nous_claw/tools/stt/stt.py` / Parakeet first; no cloud STT.
4. Kimi/Conny converts the transcript into a structured action proposal with citations and uncertainty.
5. Dima sees the original audio, transcript, and exact before/after changes before approving.
6. Only allowlisted execution paths run; external effects receive their own confirmation and read-back.
7. KiwiFS is evaluated as the indexed KBOS retrieval and attributed-git-commit layer.

## Verified concept behavior

- 390×844 and 320×640 phone layouts: no horizontal overflow; actions reachable by scrolling.
- Review → Kingdom carries the exact project + ticket key; the same real Granat ticket survives the round trip.
- Real why, impact, four source-intent entries, six KBOS context files, and a readable context excerpt load successfully.
- Friday is explicitly attributed only to the sample voice; the real card's Mon 9 Nov due remains visible.
- All three images load; sprites are 1024×1024 with exactly 32 colors and 47–56 KB each.
- Every button is at least 44px; approval starts disabled, date selection enables it, approve/reject feedback works.
- Measured text/action contrast ranges from 6.37:1 to 16.18:1.
- Existing 14-test suite and both JavaScript syntax checks pass.

Source art and prompts: `assets/kingdom/`. Page sprites and manifest: `static/ASSETS.md`.
