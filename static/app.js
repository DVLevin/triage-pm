"use strict";

const $ = selector => document.querySelector(selector);
const main = $("#main");
const dialog = $("#app-dialog");
const decisionBar = $("#decision-bar");
const nav = $("#bottom-nav");
const toastRegion = $("#toast-region");

const state = {
  token: localStorage.getItem("triage_token") || "",
  projects: [],
  projectId: localStorage.getItem("triage_project") || "",
  snapshot: null,
  tab: ["review", "progress", "context"].includes(localStorage.getItem("triage_tab")) ? localStorage.getItem("triage_tab") : "review",
  currentKey: "",
  contextDraft: null,
  busy: false,
  resetScroll: true,
};
const REASON_LABELS = {
  missing_source: "Missing source", contradicts_context: "Contradicts context",
  duplicate: "Duplicate", stale: "Stale", already_done: "Already done",
  unclear_scope: "Unclear scope", wrong_owner: "Wrong owner", other: "Other",
};
const STATUS_LABELS = {
  not_started: "Not started", active: "In progress", review: "In review",
  delivered: "Delivered (recorded)", blocked: "Blocked",
  completed_recorded: "Done (recorded)", closed_without_success_claim: "Closed",
  unknown: "State not declared",
};
const RULE_COPY = {
  require_sources: ["Require source intent", "Approval stops when the card has no sources."],
  require_methodology: ["Require TASK_CARD v1.1", "Approval stops for missing fields or null load-bearing values."],
  require_owner: ["Require an owner", "Approval stops when nobody owns the next action."],
  require_dod: ["Require Definition of Done", "Approval stops without binary acceptance criteria."],
  require_next: ["Require a literal next action", "Approval stops when execution would start from ambiguity."],
  exclude_completed: ["Hide recorded closed work", "Done/closed/delivered cards leave the review queue; history is preserved."],
};
let toastTimer;
let scrollTimer;
let gesture = null;

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
}
function multiline(value) { return esc(value).replace(/\n/g, "<br>"); }
function clamp(text, length = 900) {
  const value = String(text || "");
  if (value.length <= length) return value;
  const slice = value.slice(0, length);
  const lastSpace = slice.lastIndexOf(" ");
  return slice.slice(0, lastSpace > length * .75 ? lastSpace : length).trimEnd() + "…";
}
function icon(name) {
  const paths = {
    review: '<rect x="4" y="3" width="16" height="18" rx="3"/><path d="M8 8h8M8 12h6m-6 4 2 2 4-5"/>',
    progress: '<path d="M4 20V10m6 10V4m6 16v-7m4 7H2"/>',
    context: '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>',
    refresh: '<path d="M20 11a8 8 0 1 0-2.34 5.66M20 4v7h-7"/>',
    chevron: '<path d="m9 6 6 6-6 6"/>',
    down: '<path d="m6 9 6 6 6-6"/>',
    close: '<path d="m6 6 12 12M18 6 6 18"/>',
    undo: '<path d="M9 7 4 12l5 5M4 12h9a6 6 0 0 1 6 6"/>',
    alert: '<path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v4m0 4h.01"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    comment: '<path d="M20 15a3 3 0 0 1-3 3H9l-5 3v-6a3 3 0 0 1-1-2V6a3 3 0 0 1 3-3h11a3 3 0 0 1 3 3v9Z"/>',
  };
  return `<svg viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.review}</svg>`;
}
function formatDate(value, withTime = false) {
  if (!value) return "Not stated";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat("en", withTime
    ? {day: "numeric", month: "short", hour: "2-digit", minute: "2-digit"}
    : {day: "numeric", month: "short", year: "numeric"}).format(date);
}
function statusBadge(ticket) {
  const cls = ticket.work_status === "blocked" || ticket.past_due ? "warning" : "";
  return `<span class="badge ${cls}">${esc(STATUS_LABELS[ticket.work_status] || ticket.raw_state || "State not declared")}</span>`;
}
function showToast(message, undo = false) {
  clearTimeout(toastTimer);
  toastRegion.innerHTML = `<div class="toast"><span>${esc(message)}</span>${undo ? `<button type="button" data-action="undo">Undo</button>` : ""}</div>`;
  toastTimer = setTimeout(() => { toastRegion.innerHTML = ""; }, undo ? 8000 : 5000);
}
function openDialog(content) {
  dialog.innerHTML = content;
  if (!dialog.open) dialog.showModal();
}
function closeDialog() { if (dialog.open) dialog.close(); }
function dialogHeader(title) {
  return `<div class="sheet-header"><h2 id="dialog-title">${esc(title)}</h2><button class="icon-button" type="button" data-action="close-dialog" aria-label="Close dialog">${icon("close")}</button></div>`;
}
function saveScroll() {
  if (!state.projectId) return;
  localStorage.setItem(`triage_scroll:${state.projectId}:${state.tab}:${state.currentKey}`, String(window.scrollY));
}
function restoreScroll() {
  const top = state.resetScroll ? 0 : Number(localStorage.getItem(`triage_scroll:${state.projectId}:${state.tab}:${state.currentKey}`) || 0);
  setTimeout(() => {
    window.scrollTo({top, left: 0, behavior: "instant"});
    state.resetScroll = false;
  }, 60);
}
function setTicket(key) {
  if (!key) return;
  saveScroll();
  state.currentKey = key;
  localStorage.setItem(`triage_ticket:${state.projectId}`, key);
  state.resetScroll = true;
  render();
}

async function api(path, options = {}) {
  if (!state.token) {
    renderPairing();
    throw new Error("Pair this device first");
  }
  const response = await fetch(path, {
    ...options,
    headers: {"Authorization": `Bearer ${state.token}`, "Content-Type": "application/json", ...(options.headers || {})},
  });
  let payload = {};
  try { payload = await response.json(); } catch { payload = {error: `HTTP ${response.status}`}; }
  if (response.status === 401) {
    localStorage.removeItem("triage_token");
    state.token = "";
    renderPairing();
  }
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

function renderPairing() {
  state.snapshot = null;
  decisionBar.innerHTML = "";
  nav.innerHTML = "";
  main.classList.add("no-actions");
  main.innerHTML = `<section class="page-section"><p class="eyebrow">Private local connection</p><h1>Pair this phone</h1><p>Run <strong>python3 run.py --lan</strong> on the laptop, then open the printed URL. The token protects KBOS data on your local network.</p><form data-form="pair" class="field-group"><label class="field-label" for="pair-token">Local pairing token</label><input id="pair-token" name="token" type="password" autocomplete="off" required><p class="field-hint">The token stays in this browser. No account or cloud service is involved.</p><button class="primary-button full-width" type="submit">Connect to Triage</button></form></section>`;
}

async function bootstrap() {
  try {
    const payload = await api("/api/bootstrap");
    state.projects = payload.projects;
    if (state.projectId && state.projects.some(project => project.id === state.projectId && project.available)) {
      await loadSnapshot(localStorage.getItem(`triage_ticket:${state.projectId}`) || "");
    } else {
      state.snapshot = null;
      render();
      openProjects();
    }
  } catch (error) {
    if (state.token) renderFatal(error.message);
  }
}
function renderFatal(message) {
  decisionBar.innerHTML = "";
  nav.innerHTML = "";
  main.classList.add("no-actions");
  main.innerHTML = `<div class="empty-state"><div>${icon("alert")}<h1>Couldn’t read the snapshot</h1><p>${esc(message)}</p><p>Your local decisions are unchanged.</p><button class="primary-button" type="button" data-action="retry">Retry</button></div></div>`;
}
async function loadSnapshot(preferredKey = "", resetScroll = false) {
  if (!state.projectId) return;
  state.busy = true;
  try {
    const snapshot = await api(`/api/project/${encodeURIComponent(state.projectId)}`);
    state.snapshot = snapshot;
    const saved = preferredKey || localStorage.getItem(`triage_ticket:${state.projectId}`) || "";
    state.currentKey = snapshot.queue.includes(saved) ? saved : (snapshot.queue[0] || "");
    if (state.currentKey) localStorage.setItem(`triage_ticket:${state.projectId}`, state.currentKey);
    state.contextDraft = null;
    state.resetScroll = resetScroll;
    render();
  } catch (error) {
    renderFatal(error.message);
  } finally {
    state.busy = false;
  }
}
async function selectProject(projectId) {
  saveScroll();
  state.projectId = projectId;
  localStorage.setItem("triage_project", projectId);
  state.snapshot = null;
  state.tab = "review";
  localStorage.setItem("triage_tab", "review");
  state.currentKey = "";
  state.contextDraft = null;
  closeDialog();
  main.innerHTML = `<div class="loading-state" role="status"><span class="spinner"></span><p>Reading ${esc(projectId)}…</p></div>`;
  await loadSnapshot("", true);
}

function projectStrip() {
  const snapshot = state.snapshot;
  return `<div class="project-strip"><button class="project-select" type="button" data-action="projects" aria-label="Switch from ${esc(snapshot.project.name)}">${icon("down")}<strong>${esc(snapshot.project.name)}</strong><span>KBOS snapshot · ${esc(formatDate(snapshot.scanned_at, true))}</span></button></div>`;
}
function overview() {
  const s = state.snapshot;
  const reviewed = s.review_summary.reviewed_current;
  const eligible = s.review_summary.eligible;
  const percent = eligible ? Math.round(reviewed / eligible * 100) : 0;
  const alerts = [s.summary.past_due ? `${s.summary.past_due} past due` : "", s.summary.cards_with_blockers ? `${s.summary.cards_with_blockers} blocker cards` : "", s.summary.parser_errors ? `${s.summary.parser_errors} unreadable` : ""].filter(Boolean).join(" · ");
  return `${projectStrip()}<section class="review-overview"><div class="overview-line"><h1>${s.review_summary.pending ? `${s.review_summary.pending} to review` : "Queue clear"}</h1><button class="text-button queue-count" type="button" data-action="queue">Queue ${icon("chevron")}</button></div><div class="progress-caption"><span>${reviewed}/${eligible} reviewed${alerts ? ` · ${esc(alerts)}` : ""}</span><span>${percent}%</span></div></section>`;
}
function currentTicket() {
  return state.snapshot?.tickets.find(ticket => ticket.key === state.currentKey) || null;
}
function detail(title, content, open = false) {
  return `<details class="ticket-details" ${open ? "open" : ""}><summary>${esc(title)}</summary><div class="details-content">${content}</div></details>`;
}
function stringList(items, empty = "Not stated") {
  if (!items || !items.length) return `<p>${esc(empty)}</p>`;
  return `<ul>${items.map(item => `<li>${multiline(item)}</li>`).join("")}</ul>`;
}
function commentsBlock(ticket) {
  const comments = ticket.comments.length
    ? `<ul>${ticket.comments.map(comment => `<li><strong>${esc(comment.author)}</strong> · ${esc(formatDate(comment.created_at, true))}<br>${multiline(comment.body)}</li>`).join("")}</ul>`
    : "<p>No local comments yet.</p>";
  return `${comments}<form class="inline-comment-form" data-form="comment"><input type="hidden" name="ticket_key" value="${esc(ticket.key)}"><label class="field-label" for="comment-${esc(ticket.key)}">Add a local comment</label><textarea id="comment-${esc(ticket.key)}" name="body" required placeholder="What should the next reviewer or agent know?"></textarea><button class="secondary-button" type="submit">Save comment</button></form>`;
}
function renderTicket(ticket) {
  const pending = ticket.pending;
  const approvalNotice = ticket.approval_problems.length
    ? `<div class="notice compact-notice" id="approval-problems"><p><strong>Approval needs enrichment</strong></p>${ticket.approval_problems.map(problem => `<p>${esc(problem)}</p>`).join("")}</div>` : "";
  const changedNotice = ticket.changed_since_review ? `<div class="notice compact-notice"><p><strong>Changed since previous review.</strong> This is a new content version; the old decision remains in history.</p></div>` : "";
  const reviewNotice = ticket.local_review ? `<div class="notice compact-notice"><p><strong>${ticket.local_review.decision === "approve" ? "Approved locally" : "Returned for revision"}</strong> · ${esc(formatDate(ticket.local_review.created_at, true))}. Nothing was published or marked complete.</p></div>` : "";
  const due = ticket.due_date ? `${formatDate(ticket.due_date)}${ticket.past_due ? " · past date" : ""}` : (ticket.due_raw || "Not stated");
  const why = ticket.why || "Not stated";
  const whyPreview = clamp(why, 140);
  const whyBlock = why.length > 140
    ? `<details class="why-disclosure"><summary><span class="section-label">Why this exists</span><span class="why-text">${multiline(whyPreview)}</span><span class="why-more">Read full why</span></summary><div class="why-full">${multiline(why)}</div></details>`
    : `<div><p class="section-label">Why this exists</p><p class="why-text">${multiline(why)}</p></div>`;
  const nextText = ticket.next || "Not stated";
  const nextBlock = nextText.length > 140
    ? `<details class="next-action next-disclosure"><summary><span class="section-label">Next action</span><span class="next-preview">${multiline(clamp(nextText, 140))}</span><span class="why-more">Full next action</span></summary><div class="why-full">${multiline(nextText)}</div></details>`
    : `<div class="next-action"><p class="section-label">Next action</p><p>${multiline(nextText)}</p></div>`;
  const impact = [
    ...(ticket.impacts.length ? [`<h3>Downstream impact</h3>${stringList(ticket.impacts)}`] : []),
    ...(ticket.dependencies.length ? [`<h3>Dependencies</h3><ul>${ticket.dependencies.map(dep => `<li>${esc(dep.ref)} · ${esc(dep.status.replaceAll("_", " "))}${dep.target_title ? ` — ${esc(dep.target_title)}` : ""}</li>`).join("")}</ul>`] : []),
    ...(!ticket.impacts.length && !ticket.dependencies.length ? ["<p>Delivery impact and dependencies are not stated in a machine-readable field.</p>"] : []),
  ].join("");
  const checks = ticket.recorded_checks ? `<p><strong>Recorded checkboxes:</strong> ${ticket.recorded_checks.checked}/${ticket.recorded_checks.total}. This is not verified completion.</p>` : "<p>No explicit body checkboxes. DoD criterion count is not completion.</p>";
  const sourceContent = `${ticket.why_evidence ? `<p class="source-quote">${multiline(ticket.why_evidence)}</p>` : ""}<h3>Sources — why this exists</h3>${stringList(ticket.sources, "Source intent is missing")}`;
  const contextContent = `${stringList(ticket.context, "Load-first context is missing")}${ticket.open_questions.length ? `<h3>Open questions</h3>${stringList(ticket.open_questions)}` : ""}`;
  const scopeContent = `<h3>Scope fence</h3><p>${multiline(ticket.scope_not || "Not stated")}</p><h3>Artifacts</h3>${stringList(ticket.artifacts)}<h3>Review verdict target</h3><p>${esc(ticket.verdict_file || "Not stated")}</p><p>Verdict status: ${esc(ticket.review_verdict || "unknown")} · ${esc(ticket.verdict_status)}</p>`;
  return `<article class="ticket-card" data-ticket="${esc(ticket.key)}"><div class="ticket-hero" data-swipe="${esc(ticket.key)}"><div class="badge-row">${statusBadge(ticket)}<span class="badge">${esc(ticket.priority)}</span><span class="badge">${esc(ticket.tier || "Tier missing")}</span><span class="ticket-id">${esc(ticket.display_id)}</span></div><h1 title="${esc(ticket.title)}" aria-label="${esc(ticket.title)}">${esc(ticket.title)}</h1></div><section class="ticket-section decision-brief">${whyBlock}<div class="compact-meta"><span><strong>Owner</strong> ${esc(ticket.owner || "Not stated")}</span><span><strong>Due</strong> ${esc(due)}</span><span><strong>Updated</strong> ${esc(formatDate(ticket.updated))}</span></div>${nextBlock}<div class="evidence-line" aria-label="Evidence health"><span><strong>${ticket.sources.length}</strong> sources</span><span><strong>${ticket.dod.length}</strong> DoD</span><span><strong>${ticket.blocker_details.length}</strong> blocker${ticket.blocker_details.length === 1 ? "" : "s"}</span></div>${pending ? `<p class="swipe-hint">Swipe header or use buttons · keys A / N / U</p>` : ""}${changedNotice}${reviewNotice}${approvalNotice}</section>${detail("Delivery impact & dependencies", impact)}${detail(`Definition of Done (${ticket.dod.length})`, checks + stringList(ticket.dod, "Definition of Done is missing"))}${detail(`Source intent (${ticket.sources.length})`, sourceContent)}${detail("Load-first context & open questions", contextContent)}${detail("Scope, artifacts & verdict", scopeContent)}${detail(`Local comments (${ticket.comments.length})`, commentsBlock(ticket))}${detail("Complete source record", `<p>${esc(ticket.path)}</p><p>SHA-256 ${esc(ticket.content_hash)}</p><pre class="raw-record">${esc(ticket.body)}${ticket.body_truncated ? "\n… truncated at 30,000 characters" : ""}</pre>`)}<a class="kingdom-link" href="/kingdom?project=${encodeURIComponent(state.projectId)}&ticket=${encodeURIComponent(ticket.key)}">Discuss this exact ticket with Conny · Royal Decree concept →</a></article>`;
}
function renderReview() {
  const s = state.snapshot;
  if (!s.queue.length) {
    decisionBar.innerHTML = "";
    main.classList.add("no-actions");
    main.innerHTML = `${overview()}<div class="empty-state"><div>${icon("check")}<h2>Review queue clear</h2><p>No unreviewed cards match this snapshot.</p><p>Refresh KBOS or inspect decision history in Progress.</p><button class="secondary-button" type="button" data-action="refresh">Refresh KBOS</button></div></div>`;
    return;
  }
  const ticket = currentTicket();
  if (!ticket) {
    state.currentKey = s.queue[0];
    return renderReview();
  }
  main.classList.remove("no-actions");
  main.innerHTML = `${overview()}${renderTicket(ticket)}<p class="field-hint" style="margin-top:16px">Local review only — approval does not publish, assign, or complete work.</p>`;
  decisionBar.innerHTML = `<button class="action-button needs-button" type="button" data-action="needs-work" title="Keyboard shortcut: N">Needs work</button><button class="action-button approve-button" type="button" data-action="approve" title="Keyboard shortcut: A" ${ticket.approval_problems.length ? 'disabled aria-describedby="approval-problems"' : ""}>Approve proposal</button>`;
}
function stateBlock() {
  const summary = state.snapshot.summary;
  const counts = summary.state_counts;
  const total = summary.total_cards || 1;
  return Object.entries(counts).map(([status, count]) => `<div class="state-row"><span>${esc(STATUS_LABELS[status] || status)}</span><div class="state-bar" aria-hidden="true"><span style="width:${Math.round(count / total * 100)}%"></span></div><strong>${count}</strong></div>`).join("") || "<p>No readable cards.</p>";
}
function historyBlock() {
  const history = state.snapshot.history;
  if (!history.length) return "<p>No local decisions yet.</p>";
  const tickets = Object.fromEntries(state.snapshot.tickets.map(ticket => [ticket.key, ticket]));
  return `<ul class="history-list">${history.map(row => `<li class="history-item"><strong>${esc(tickets[row.ticket_key]?.title || row.ticket_display_id)}</strong><p>${row.decision === "approve" ? "Approved locally" : "Needs work"} · ${esc(formatDate(row.created_at, true))}${row.undone_at ? " · Undone" : ""}</p>${row.reasons.length ? `<p>${row.reasons.map(reason => esc(REASON_LABELS[reason])).join(", ")}</p>` : ""}${row.comment ? `<p>${multiline(row.comment)}</p>` : ""}<small>${esc(row.ticket_display_id)} · ${esc(row.content_hash.slice(0, 12))}</small></li>`).join("")}</ul>`;
}
function renderProgress() {
  decisionBar.innerHTML = "";
  main.classList.add("no-actions");
  const s = state.snapshot;
  const r = s.review_summary;
  const reviewPercent = r.eligible ? Math.round(r.reviewed_current / r.eligible * 100) : 0;
  const blockers = s.blockers.length
    ? `<ul class="plain-list">${s.blockers.slice(0, 20).map(row => `<li class="context-card"><strong>${esc(row.title)}</strong><p>${multiline(row.text)}</p><small>${esc(row.display_id)} · ${esc(row.kind.replaceAll("_", " "))} · updated ${esc(row.updated || "unknown")}</small></li>`).join("")}</ul>${s.blockers.length > 20 ? `<p>${s.blockers.length - 20} more signals remain in ticket records.</p>` : ""}`
    : "<p>No blockers are declared in readable cards. That is not proof that none exist.</p>";
  const timeline = s.timeline.length
    ? s.timeline.map(row => `<div class="timeline-item"><strong>${esc(row.title)}</strong><small>${esc(formatDate(row.due))} · ${esc(STATUS_LABELS[row.state])}${row.past_due ? " · past recorded due date" : ""}</small></div>`).join("")
    : "<p>No complete ISO due dates are recorded.</p>";
  const errors = s.errors.length ? `<ul class="plain-list">${s.errors.map(error => `<li class="context-card"><strong>${esc(error.path)}</strong><p>${esc(error.error)}</p></li>`).join("")}</ul>` : "<p>No parser errors in this snapshot.</p>";
  const activeHistory = s.history.find(row => !row.undone_at);
  main.innerHTML = `${projectStrip()}<section class="page-section"><p class="eyebrow">Signals, not certainty</p><h1>Progress</h1><p>As of ${esc(s.as_of)}. Review, execution state, verdicts, and delivery evidence stay separate.</p></section><section class="page-section"><h2>Review coverage</h2><div class="metric-grid"><div class="metric-card"><strong>${reviewPercent}%</strong><span>current eligible versions reviewed</span></div><div class="metric-card"><strong>${r.pending}</strong><span>waiting for review</span></div><div class="metric-card"><strong>${s.summary.state_counts.completed_recorded || 0}</strong><span>done in source records</span></div><div class="metric-card"><strong>${s.summary.unknown_state}</strong><span>state not declared</span></div></div></section><section class="page-section"><h2>Recorded work states</h2>${stateBlock()}<p class="field-hint">A source saying “done” is not destination-verified delivery.</p></section><section class="page-section"><h2>Timeline</h2><div class="metric-grid"><div class="metric-card"><strong>${s.summary.past_due}</strong><span>past recorded due dates</span></div><div class="metric-card"><strong>${s.summary.scheduled}</strong><span>complete ISO dates</span></div><div class="metric-card"><strong>${s.summary.unscheduled}</strong><span>no due date</span></div><div class="metric-card"><strong>${s.summary.ambiguous_due}</strong><span>ambiguous date context</span></div></div><div class="context-card" style="margin-top:12px">${timeline}</div></section><section class="page-section"><h2>Blocker signals</h2>${blockers}</section><section class="page-section"><h2>Data quality</h2><div class="signal-row"><span class="signal ${s.summary.parser_errors ? "warning" : "good"}">${s.summary.parser_errors} parser errors</span><span class="signal ${s.summary.duplicate_display_ids ? "warning" : "good"}">${s.summary.duplicate_display_ids} duplicate display IDs</span></div><div style="margin-top:12px">${errors}</div></section><section class="page-section"><div class="overview-line"><h2>Decision history</h2>${activeHistory ? `<button class="text-button" type="button" data-action="undo">${icon("undo")}Undo latest</button>` : ""}</div>${historyBlock()}</section><section class="page-section"><h2>Your review rhythm</h2><div class="metric-card"><strong>Level ${s.reviewer_progress.level} · ${s.reviewer_progress.points} pts</strong><span>${s.reviewer_progress.reviews} active reviews · 10 points for either decision · no leaderboard</span></div></section>`;
}
function contextForm() {
  const s = state.snapshot;
  if (!state.contextDraft) state.contextDraft = JSON.parse(JSON.stringify(s.settings));
  const draft = state.contextDraft;
  const sources = s.context_sources.map((source, index) => {
    const checked = draft.sources[source.path] ? "checked" : "";
    const warnings = [source.self_declared_stale ? "self-declared stale" : "", source.age_days > 7 ? `modified ${source.age_days} days ago` : ""].filter(Boolean).join(" · ");
    return `<div class="context-card"><label class="checkbox-option"><input type="checkbox" name="source-${index}" ${checked} ${source.exists ? "" : "disabled"}><span><strong>${esc(source.path)}</strong><small>${source.exists ? `Modified ${esc(formatDate(source.modified_at, true))}${warnings ? ` · ${esc(warnings)}` : ""}` : "File not found in this snapshot"}</small></span></label>${source.included && source.content ? `<details class="context-excerpt"><summary>Read ${esc(source.excerpt_mode === "tail" ? "latest tail" : "opening")} excerpt</summary><pre>${esc(source.content)}${source.truncated ? "\n… bounded excerpt" : ""}</pre></details>` : ""}</div>`;
  }).join("");
  const rules = Object.entries(RULE_COPY).map(([key, copy]) => `<label class="checkbox-option"><input type="checkbox" name="rule-${esc(key)}" ${draft.rules[key] ? "checked" : ""}><span><strong>${esc(copy[0])}</strong><small>${esc(copy[1])}</small></span></label>`).join("");
  return `<form data-form="context"><section class="page-section"><h2>KBOS sources</h2><p>Choose what enters the next review snapshot. Excerpts are bounded; source files remain untouched.</p>${sources}</section><section class="page-section"><h2>Enforced review rules</h2><p>These are deterministic gates, not AI judgments. Existing decisions retain their old context version.</p><div class="checkbox-grid">${rules}</div></section><button class="primary-button full-width" type="submit">Apply to new review snapshot</button></form>`;
}
function renderContext() {
  decisionBar.innerHTML = "";
  main.classList.add("no-actions");
  const s = state.snapshot;
  main.innerHTML = `${projectStrip()}<section class="page-section"><p class="eyebrow">Context engineering</p><h1>Review basis</h1><p>Snapshot ${esc(s.context_snapshot_id.slice(0, 10))} · recorded ${esc(formatDate(s.scanned_at, true))}.</p><div class="offline-note">Only Triage settings and decisions are saved. Raw context excerpts are never copied into the review database.</div></section>${contextForm()}`;
}
function renderNav() {
  if (!state.snapshot) { nav.innerHTML = ""; return; }
  const items = [["review", "Review"], ["progress", "Progress"], ["context", "Context"]];
  nav.innerHTML = items.map(([id, label]) => `<button class="nav-button" type="button" data-tab="${id}" ${state.tab === id ? 'aria-current="page"' : ""}>${icon(id)}<span>${label}</span></button>`).join("");
}
function render() {
  renderNav();
  if (!state.snapshot) {
    decisionBar.innerHTML = "";
    main.classList.add("no-actions");
    main.innerHTML = `<div class="loading-state"><div><h1>Choose a KBOS project</h1><p>Your source files stay read-only.</p><button class="primary-button" type="button" data-action="projects">Select project</button></div></div>`;
    return;
  }
  if (state.tab === "progress") renderProgress();
  else if (state.tab === "context") renderContext();
  else renderReview();
  restoreScroll();
}

function openProjects() {
  const options = state.projects.map(project => `<button class="project-option" type="button" data-action="select-project" data-project="${esc(project.id)}" ${project.available ? "" : "disabled"}><strong>${esc(project.name)}</strong><span class="project-number">${project.available ? esc(project.pending) : "—"}</span><small>${project.available ? `${project.total_cards} cards · ${project.past_due} past recorded due · ${project.parser_errors} parser errors` : `Unavailable: ${esc(project.error)}`}</small></button>`).join("");
  openDialog(`${dialogHeader("Choose a project")}<div class="sheet-body"><p class="field-hint">Pending means no active local decision for the current file version. No mixed-project queue.</p><div class="project-options">${options}</div></div>`);
}
function openQueue() {
  const s = state.snapshot;
  const tickets = Object.fromEntries(s.tickets.map(ticket => [ticket.key, ticket]));
  const items = s.queue.map(key => `<li><button class="queue-item" type="button" data-action="select-ticket" data-key="${esc(key)}"><strong>${esc(tickets[key].title)}</strong><span>${esc(tickets[key].display_id)} · ${esc(tickets[key].owner || "No owner")} · ${esc(tickets[key].due_date || "No ISO due date")}</span></button></li>`).join("");
  openDialog(`${dialogHeader("Review queue")}<div class="sheet-body"><ul class="queue-list">${items || "<li>No pending cards.</li>"}</ul></div>`);
}
function openNeedsWork() {
  const ticket = currentTicket();
  if (!ticket || !ticket.pending) return;
  const reasons = Object.entries(REASON_LABELS).map(([key, label]) => `<label class="checkbox-option"><input type="checkbox" name="reason" value="${esc(key)}"><span><strong>${esc(label)}</strong></span></label>`).join("");
  openDialog(`${dialogHeader("Return for revision")}<form class="sheet-body" data-form="needs-work"><p class="field-hint">${esc(ticket.title)}</p><fieldset class="field-group" style="border:0;padding:0;margin:0 0 18px"><legend>What is wrong? Choose at least one.</legend><div class="checkbox-grid">${reasons}</div></fieldset><div class="field-group"><label class="field-label" for="needs-comment">Comment for the next revision</label><textarea id="needs-comment" name="comment" placeholder="Specific, actionable correction (optional)"></textarea></div><button class="action-button needs-button full-width" type="submit">Save needs-work decision</button><p class="field-hint" style="margin-top:12px">This does not delete or edit the source ticket.</p></form>`);
}
async function decide(direction, reasons = [], comment = "") {
  const ticket = currentTicket();
  if (!ticket || state.busy) return;
  state.busy = true;
  decisionBar.querySelectorAll("button").forEach(button => { button.disabled = true; });
  try {
    await api("/api/decisions", {method: "POST", body: JSON.stringify({
      project_id: state.projectId, ticket_key: ticket.key, content_hash: ticket.content_hash,
      context_snapshot_id: state.snapshot.context_snapshot_id, decision: direction, reasons, comment,
    })});
    closeDialog();
    await loadSnapshot("", true);
    showToast(direction === "approve" ? "Approved locally" : "Returned for revision", true);
  } catch (error) {
    showToast(error.message);
    render();
  } finally {
    state.busy = false;
  }
}
async function undo() {
  if (!state.projectId || state.busy) return;
  state.busy = true;
  try {
    const result = await api("/api/decisions/undo", {method: "POST", body: JSON.stringify({project_id: state.projectId})});
    if (!result.undone) { showToast("No active decision to undo"); return; }
    await loadSnapshot(result.decision.ticket_key, true);
    showToast("Decision undone; ticket returned to the queue");
  } catch (error) { showToast(error.message); }
  finally { state.busy = false; }
}
async function refresh() {
  if (!state.projectId || state.busy) { if (!state.projectId) openProjects(); return; }
  state.busy = true;
  showToast("Refreshing the recorded KBOS snapshot…");
  try {
    const snapshot = await api(`/api/project/${encodeURIComponent(state.projectId)}/refresh`, {method: "POST", body: "{}"});
    state.snapshot = snapshot;
    if (!snapshot.queue.includes(state.currentKey)) state.currentKey = snapshot.queue[0] || "";
    state.contextDraft = null;
    state.resetScroll = true;
    render();
    showToast("Fresh snapshot recorded");
  } catch (error) { showToast(error.message); }
  finally { state.busy = false; }
}

// Navigation and command delegation.
document.addEventListener("click", async event => {
  const tab = event.target.closest("[data-tab]");
  if (tab) {
    saveScroll();
    state.tab = tab.dataset.tab;
    localStorage.setItem("triage_tab", state.tab);
    if (state.tab === "context") state.contextDraft = null;
    render();
    return;
  }
  const target = event.target.closest("[data-action]");
  if (!target) return;
  const action = target.dataset.action;
  if (action === "projects") openProjects();
  else if (action === "select-project") await selectProject(target.dataset.project);
  else if (action === "close-dialog") closeDialog();
  else if (action === "queue") openQueue();
  else if (action === "select-ticket") { closeDialog(); setTicket(target.dataset.key); }
  else if (action === "approve") await decide("approve");
  else if (action === "needs-work") openNeedsWork();
  else if (action === "undo") await undo();
  else if (action === "refresh") await refresh();
  else if (action === "retry") await bootstrap();
});

document.addEventListener("submit", async event => {
  const form = event.target;
  const kind = form.dataset.form;
  if (!kind) return;
  event.preventDefault();
  const data = new FormData(form);
  if (kind === "pair") {
    state.token = String(data.get("token") || "").trim();
    localStorage.setItem("triage_token", state.token);
    await bootstrap();
  } else if (kind === "needs-work") {
    const reasons = data.getAll("reason");
    if (!reasons.length) { showToast("Choose at least one reason"); return; }
    await decide("needs_work", reasons, String(data.get("comment") || ""));
  } else if (kind === "comment") {
    const body = String(data.get("body") || "").trim();
    if (!body) return;
    try {
      await api("/api/comments", {method: "POST", body: JSON.stringify({project_id: state.projectId, ticket_key: data.get("ticket_key"), body})});
      await loadSnapshot(state.currentKey);
      showToast("Comment saved locally");
    } catch (error) { showToast(error.message); }
  } else if (kind === "context") {
    const sources = {};
    state.snapshot.context_sources.forEach((source, index) => { sources[source.path] = data.get(`source-${index}`) === "on"; });
    const rules = {};
    Object.keys(RULE_COPY).forEach(rule => { rules[rule] = data.get(`rule-${rule}`) === "on"; });
    const submit = form.querySelector("button[type=submit]");
    submit.disabled = true;
    submit.textContent = "Applying snapshot…";
    try {
      const snapshot = await api(`/api/project/${encodeURIComponent(state.projectId)}/context`, {method: "POST", body: JSON.stringify({settings: {sources, rules}})});
      state.snapshot = snapshot;
      state.currentKey = snapshot.queue[0] || "";
      state.contextDraft = null;
      state.tab = "review";
      localStorage.setItem("triage_tab", "review");
      state.resetScroll = true;
      render();
      showToast("New context snapshot applied");
    } catch (error) { showToast(error.message); render(); }
  }
});

// Keyboard equivalents; never fire while typing or while a dialog owns focus.
document.addEventListener("keydown", async event => {
  if (dialog.open || event.ctrlKey || event.metaKey || event.altKey || event.target.closest("input,textarea,select,[contenteditable=true]")) return;
  const key = event.key.toLowerCase();
  if (key === "a" && currentTicket()?.pending && !currentTicket()?.approval_problems.length) { event.preventDefault(); await decide("approve"); }
  else if (key === "n" && currentTicket()?.pending) { event.preventDefault(); openNeedsWork(); }
  else if (key === "u") { event.preventDefault(); await undo(); }
});

// Optional swipe on the ticket header only. Vertical scrolling always wins.
document.addEventListener("pointerdown", event => {
  const hero = event.target.closest("[data-swipe]");
  if (!hero || !event.isPrimary || event.button > 0 || !currentTicket()?.pending) return;
  gesture = {hero, x: event.clientX, y: event.clientY, dx: 0, active: false};
});
document.addEventListener("pointermove", event => {
  if (!gesture) return;
  const dx = event.clientX - gesture.x;
  const dy = event.clientY - gesture.y;
  if (!gesture.active && Math.abs(dx) > 14 && Math.abs(dx) > Math.abs(dy) * 1.35) gesture.active = true;
  if (!gesture.active) return;
  gesture.dx = dx;
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    gesture.hero.classList.add("dragging");
    gesture.hero.style.transform = `translateX(${Math.max(-110, Math.min(110, dx))}px)`;
    gesture.hero.style.background = dx > 0 ? "var(--brand-soft)" : "var(--needs-soft)";
  }
});
async function finishGesture() {
  if (!gesture) return;
  const current = gesture;
  gesture = null;
  current.hero.classList.remove("dragging");
  current.hero.style.transform = "";
  current.hero.style.background = "";
  if (!current.active || Math.abs(current.dx) < 92) return;
  if (current.dx > 0) {
    if (currentTicket()?.approval_problems.length) showToast("Resolve the listed approval gates first");
    else await decide("approve");
  } else openNeedsWork();
}
document.addEventListener("pointerup", finishGesture);
document.addEventListener("pointercancel", finishGesture);

window.addEventListener("scroll", () => {
  clearTimeout(scrollTimer);
  scrollTimer = setTimeout(saveScroll, 120);
}, {passive: true});
window.addEventListener("online", () => showToast("Connection restored"));
window.addEventListener("offline", () => showToast("Offline — card data is not cached on this device"));
dialog.addEventListener("click", event => {
  if (event.target === dialog) {
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) closeDialog();
  }
});

(async function init() {
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  const pair = new URLSearchParams(location.search).get("pair");
  if (pair) {
    state.token = pair;
    localStorage.setItem("triage_token", pair);
    history.replaceState({}, document.title, location.pathname);
  }
  if (window.isSecureContext && "serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
  if (!state.token) renderPairing();
  else await bootstrap();
})();
