(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const STATUS = {not_started:"Not started",active:"In progress",review:"In review",delivered:"Delivered (recorded)",blocked:"Blocked",completed_recorded:"Done (recorded)",closed_without_success_claim:"Closed",unknown:"State not declared"};
  const params = new URLSearchParams(location.search);
  if (params.get("pair")) localStorage.setItem("triage_token", params.get("pair"));
  params.delete("pair");
  history.replaceState({}, "", location.pathname + (params.toString() ? `?${params}` : ""));
  const token = localStorage.getItem("triage_token") || "";
  let snapshot = null;
  let ticket = null;
  let mode = "kbos";

  function formatDate(value) {
    if (!value) return "Not stated";
    const date = new Date(`${value}T12:00:00`);
    return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat("en", {day:"numeric",month:"short",year:"numeric"}).format(date);
  }
  function list(items, ordered = false) {
    if (!items.length) return "";
    const tag = ordered ? "ol" : "ul";
    return `<${tag}>${items.map(item => `<li>${esc(item)}</li>`).join("")}</${tag}>`;
  }
  function missing(text) { return `<p class="missing-fact">${esc(text)}</p>`; }
  function showError(message) {
    $("#load-error").hidden = false;
    $("#load-error").innerHTML = `<strong>Engineer view unavailable.</strong><p>${esc(message)}</p><a href="/">Open Triage to pair and select a ticket.</a>`;
  }
  function renderContext() {
    const refs = ticket.context.length ? `<h4>Load-first references in the card</h4>${list(ticket.context)}` : missing("No load-first references are declared in the card.");
    const files = snapshot.context_sources.filter(source => source.included);
    const current = files.length ? `<h4>Current KBOS snapshot</h4>${files.map(source => `<div class="context-file"><strong>${esc(source.path)}</strong><small>${source.exists ? `Modified ${esc(new Date(source.modified_at).toLocaleString("en"))}` : "Missing"}</small>${source.content ? `<details><summary>Read actual excerpt</summary><pre>${esc(source.content)}</pre></details>` : ""}</div>`).join("")}` : missing("No KBOS context files are included in this snapshot.");
    return refs + current;
  }
  function render() {
    const currentDue = ticket.due_date ? formatDate(ticket.due_date) : (ticket.due_raw || "Not stated");
    $("#kbos-tab").setAttribute("aria-selected", String(mode === "kbos"));
    $("#jira-tab").setAttribute("aria-selected", String(mode === "jira"));
    $("#truth-banner").innerHTML = mode === "kbos"
      ? `<strong>KBOS now.</strong> Exact structured fields from the current card; no AI rewrite. This is not a live Jira screen. Snapshot ${esc(new Date(snapshot.scanned_at).toLocaleString("en"))}.`
      : `<strong>Jira preview.</strong> A deterministic proposed payload from the same fields. This screen does not fetch or create a Jira issue; the actual Jira layout/workflow still needs live validation.`;
    $("#ticket-id").textContent = `${ticket.display_id} · ${ticket.priority} · ${STATUS[ticket.work_status] || ticket.work_status}`;
    $("#ticket-title").textContent = ticket.title;
    $("#ticket-meta").textContent = `${mode === "jira" ? "Proposed assignee" : "Owner"} ${ticket.owner || "Not stated"} · Due ${currentDue} · Updated ${formatDate(ticket.updated)}`;
    $("#ticket-next").textContent = ticket.next || "Not stated. The engineer has no literal next action.";
    $("#ticket-why").textContent = ticket.why || "Not stated. The reason behind the task is missing.";
    $("#why-evidence-wrap").hidden = !ticket.why_evidence;
    $("#why-evidence").textContent = ticket.why_evidence || "";
    $("#ticket-dod").innerHTML = ticket.dod.length ? list(ticket.dod, true) : missing("No binary Definition of Done is present.");
    const impact = [
      ticket.impacts.length ? `<h4>Downstream impact</h4>${list(ticket.impacts)}` : "",
      ticket.dependencies.length ? `<h4>Dependencies</h4><ul>${ticket.dependencies.map(dep => `<li>${esc(dep.ref)} · ${esc(dep.status.replaceAll("_", " "))}${dep.target_title ? ` — ${esc(dep.target_title)}` : ""}</li>`).join("")}</ul>` : "",
    ].join("");
    $("#ticket-impact").innerHTML = impact || missing("No downstream impact or dependency is declared in a machine-readable field.");
    const blockers = ticket.blocker_details.length ? `<h4>Blocker signals</h4>${list(ticket.blocker_details.map(item => `${item.kind.replaceAll("_", " ")}: ${item.text}`))}` : `<p>No blocker signal is declared. This is not proof that none exists.</p>`;
    const questions = ticket.open_questions.length ? `<h4>Open questions</h4>${list(ticket.open_questions)}` : `<p>No open-questions section is declared.</p>`;
    $("#ticket-blockers").innerHTML = blockers + questions;
    $("#ticket-context").innerHTML = renderContext();
    $("#ticket-scope").textContent = ticket.scope_not || "Not stated. The task has no explicit scope fence.";
    $("#ticket-artifacts").innerHTML = ticket.artifacts.length ? list(ticket.artifacts) : missing("No artifacts are declared.");
    $("#ticket-sources").innerHTML = ticket.sources.length ? list(ticket.sources) : missing("Source intent is missing; the engineer cannot trace why this was requested.");
    $("#ticket-path").textContent = `${ticket.path} · SHA-256 ${ticket.content_hash}`;
    $("#ticket-raw").textContent = ticket.body + (ticket.body_truncated ? "\n… truncated at 30,000 characters" : "");
    const checks = [
      {kind:ticket.next ? "good" : "gap", label:ticket.next ? "Next action present" : "Next action missing"},
      {kind:ticket.why ? "good" : "gap", label:ticket.why ? "Reason present" : "Reason missing"},
      {kind:ticket.owner ? "good" : "gap", label:ticket.owner ? `Owner: ${ticket.owner}` : "Owner missing"},
      {kind:ticket.dod.length ? "good" : "gap", label:`${ticket.dod.length} DoD criteria`},
      {kind:ticket.sources.length ? "good" : "gap", label:`${ticket.sources.length} source intents`},
      {kind:ticket.impacts.length || ticket.dependencies.length ? "good" : "warn", label:ticket.impacts.length || ticket.dependencies.length ? "Impact declared" : "Impact not declared"},
      {kind:ticket.past_due ? "warn" : (ticket.due_date ? "good" : "warn"), label:ticket.past_due ? `Past due: ${currentDue}` : `Due: ${currentDue}`},
      {kind:ticket.open_questions.length ? "warn" : "", label:`${ticket.open_questions.length} open questions`},
    ];
    $("#coverage-list").innerHTML = checks.map(item => `<span class="coverage-item ${item.kind}">${esc(item.label)}</span>`).join("");
    $("#dima-link").href = `/kingdom?project=${encodeURIComponent(snapshot.project.id)}&ticket=${encodeURIComponent(ticket.key)}`;
    localStorage.setItem("triage_project", snapshot.project.id);
    localStorage.setItem(`triage_ticket:${snapshot.project.id}`, ticket.key);
    $("#engineer-content").hidden = false;
  }
  async function load() {
    if (!token) { showError("No local pairing token is stored on this device."); return; }
    const projectId = params.get("project") || localStorage.getItem("triage_project") || "granat";
    try {
      const response = await fetch(`/api/project/${encodeURIComponent(projectId)}`, {headers:{Authorization:`Bearer ${token}`}});
      if (!response.ok) throw new Error(response.status === 401 ? "Pairing failed or expired." : `Snapshot returned HTTP ${response.status}.`);
      snapshot = await response.json();
      const requested = params.get("ticket") || localStorage.getItem(`triage_ticket:${projectId}`) || "";
      ticket = snapshot.tickets.find(item => item.key === requested) || snapshot.tickets.find(item => item.key === snapshot.queue[0]) || snapshot.tickets[0];
      if (!ticket) throw new Error("This project has no readable ticket in the current snapshot.");
      render();
    } catch (error) { showError(error.message); }
  }
  $("#kbos-tab").addEventListener("click", () => { if (ticket) { mode = "kbos"; render(); } });
  $("#jira-tab").addEventListener("click", () => { if (ticket) { mode = "jira"; render(); } });
  load();
})();
