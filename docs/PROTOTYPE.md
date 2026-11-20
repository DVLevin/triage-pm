# Triage mobile prototype — run and use

## Open it on your phone

1. Keep the laptop and phone on the same Wi-Fi network.
2. From this repository run:

   ```bash
   python3 run.py --lan
   ```

   If PyYAML is missing, first run `python3 -m pip install -r requirements.txt` (or use an existing project venv).
3. Open the **exact printed URL** on the phone. Its one-time `pair` parameter stores the local pairing token in that browser and removes it from the visible address.
4. Select a project. The next launch resumes that project and ticket.

The server binds loopback by default. `--lan` listens on all interfaces and requires the bearer token for every KBOS API request. Stop with `Ctrl+C`. Do not expose this prototype through a public tunnel.

## The three tabs

- **Review:** one current card at a time. Read why, owner, due context, next action, evidence, impact, DoD, sources, scope, comments, and the complete source record. Approve or return with a structured needs-work reason. Buttons are primary; header swipe and A/N/U keyboard commands are equivalents. Undo is available after a decision and in Progress. **Discuss this exact ticket with Conny** opens the Royal Decree concept bound to the same ticket and context; its sample action remains demo-only. **View this exact task as the engineer** opens the recipient lens with current KBOS fields and a separate non-live Jira preview.
- **Progress:** current-version review coverage, recorded work states, timeline coverage, past recorded due dates, explicit/reported blockers, parser errors, duplicate IDs, decision history, and individual review points.
- **Context:** configured KBOS files with bounded excerpts and modification/freshness signals. Include/exclude sources and change deterministic approval rules, then **Apply to new review snapshot**. Existing decisions retain the context version under which they were made.

## What a decision means

**Approve = this exact ticket version passed local human review under this exact context snapshot.** It does not publish to Jira/Linear, assign work, or claim implementation.

**Needs work = returned for revision in Triage's local review overlay.** The source card is not edited or deleted. A reason is required; a comment is optional.

Review data lives in ignored `data/triage.db`. Raw KBOS excerpts are not copied into that database. The local config and pairing token are also ignored.

## Data semantics

- Canonical identity is project + relative file path; display IDs may collide.
- Proposal version is the source bytes' SHA-256. A changed card returns to the queue and old decisions remain in history.
- Missing/unknown state stays unknown. READY is a review verdict, not work completion.
- Only full ISO dates enter computed timeline signals. Annotated dates remain visible as due context.
- Explicit checkboxes are recorded checks, not verified completion. DoD count is not a progress percentage.
- Blockers are declared/reported/dependency-waiting signals, not independently verified incidents.
- Legacy cards can be reviewed as needs-work, but default hard rules prevent approval until TASK_CARD v1.1 enrichment is present.

## PWA boundary

The manifest, icons, and app-shell service worker are included. On a secure context the shell caches successfully. **No card or context response is cached offline.** Plain LAN HTTP is enough for online phone viewing, but offline installation/use is not promised; phone microphone capture for the planned voice workflow requires a secure context, so private HTTPS is a prerequisite rather than an optional polish item.

## Verification

```bash
python3 -m unittest discover -s tests -v
node --check static/app.js
```

The suite covers parsing, malformed-card isolation, duplicate IDs, date/blocker/verdict semantics, real-source byte immutability, authentication, decision integrity, comments, undo, and progress. Mobile-browser and recipient-eyes evidence is recorded in `.planning/01-mobile-kbos-prototype/VERIFICATION.md` and the terminal review in `VERDICT.md`.
