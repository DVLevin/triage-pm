# KBOS Kingdom — Royal Decree concept

Open `/kingdom` on the running local server. This is an interactive **visual/product concept**, not a voice or Jira implementation. It records no audio and performs no writes.

## What the concept demonstrates

- Original adult DnD-inspired pixel-art presentation.
- Conny's adviser persona with profanity and dark tavern humor.
- A demo voice transcript transformed into explicit proposed changes.
- Ambiguity gating: approval remains disabled until the user chooses an exact date.
- Approve/reject interaction feedback without pretending that execution happened.
- Clear `LOCAL · APPROVAL-GATED` wording for the future writable product.

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
- All three images load; sprites are 1024×1024 with exactly 32 colors and 47–56 KB each.
- Every button is at least 44px; approval starts disabled, date selection enables it, approve/reject feedback works.
- Measured text/action contrast ranges from 6.37:1 to 16.18:1.
- Existing 14-test suite and both JavaScript syntax checks pass.

Source art and prompts: `assets/kingdom/`. Page sprites and manifest: `static/ASSETS.md`.
