(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const STATUS = {not_started:"Not started",active:"In progress",review:"In review",delivered:"Delivered (recorded)",blocked:"Blocked",completed_recorded:"Done (recorded)",closed_without_success_claim:"Closed",unknown:"State not declared"};
  const params = new URLSearchParams(location.search);
  const pair = params.get("pair");
  if (pair) localStorage.setItem("triage_token", pair);
  params.delete("pair");
  history.replaceState({}, "", location.pathname + (params.toString() ? `?${params}` : ""));
  const token = localStorage.getItem("triage_token") || "";
  let chosenDate = "";
  let ticket = null;

  function formatDate(value) {
    if (!value) return "Not stated";
    const date = new Date(`${value}T12:00:00`);
    return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat("en", {day:"numeric",month:"short",year:"numeric"}).format(date);
  }
  function list(items, emptyText) {
    return items.length ? `<ul>${items.map(item => `<li>${esc(item)}</li>`).join("")}</ul>` : `<p class="missing-fact">${esc(emptyText)}</p>`;
  }
  function showError(message) {
    const error = $("#load-error");
    error.hidden = false;
    error.innerHTML = `<strong>Real ticket unavailable.</strong><p>${esc(message)}</p><a href="/">Open the main Triage app to pair and select a ticket.</a>`;
    $("#approve").disabled = true;
  }
  function render(snapshot, selected) {
    ticket = selected;
    localStorage.setItem("triage_project", snapshot.project.id);
    localStorage.setItem(`triage_ticket:${snapshot.project.id}`, ticket.key);
    $("#project-label").textContent = `${snapshot.project.name.toUpperCase()} · KBOS ${new Date(snapshot.scanned_at).toLocaleString("en", {day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"})}`;
    $("#ticket-id").textContent = `${ticket.display_id} · ${ticket.priority} · ${STATUS[ticket.work_status] || ticket.work_status}`;
    $("#ticket-title").textContent = ticket.title;
    const currentDue = ticket.due_date ? formatDate(ticket.due_date) : (ticket.due_raw || "Not stated");
    $("#ticket-meta").textContent = `Owner ${ticket.owner || "Not stated"} · Due ${currentDue} · Updated ${formatDate(ticket.updated)}`;
    $("#ticket-why").textContent = ticket.why || "Not stated. The card does not explain its origin.";
    if (ticket.why_evidence) {
      $("#why-evidence-wrap").hidden = false;
      $("#why-evidence").textContent = ticket.why_evidence;
    }
    const impacts = [
      ...(ticket.impacts.length ? [`<h4>Downstream items</h4>${list(ticket.impacts, "")}`] : []),
      ...(ticket.dependencies.length ? `<h4>Dependencies</h4><ul>${ticket.dependencies.map(dep => `<li>${esc(dep.ref)} · ${esc(dep.status.replaceAll("_", " "))}${dep.target_title ? ` — ${esc(dep.target_title)}` : ""}</li>`).join("")}</ul>` : []),
    ];
    $("#ticket-impact").innerHTML = impacts.join("") || `<p class="missing-fact">No downstream impact or dependency is stated in a machine-readable field. This is a review gap, not permission to invent one.</p>`;
    $("#ticket-sources").innerHTML = ticket.sources.length ? ticket.sources.map(source => `<li>${esc(source)}</li>`).join("") : `<li class="missing-fact">Source intent is missing. The suggestion cannot be traced from this card.</li>`;
    const loadFirst = ticket.context.length ? `<h4>Load-first references in the card</h4>${list(ticket.context, "")}` : `<p class="missing-fact">No load-first references are declared in the card.</p>`;
    const included = snapshot.context_sources.filter(source => source.included);
    const contextFiles = included.length ? `<h4>Current KBOS context snapshot</h4>${included.map(source => `<div class="context-file"><strong>${esc(source.path)}</strong><small>${source.exists ? `Modified ${esc(new Date(source.modified_at).toLocaleString("en"))}` : "Missing"}</small>${source.content ? `<details><summary>Read actual excerpt</summary><pre>${esc(source.content)}</pre></details>` : ""}</div>`).join("")}` : `<p class="missing-fact">No KBOS context files are included in this snapshot.</p>`;
    $("#ticket-context").innerHTML = loadFirst + contextFiles;
    $("#ticket-path").textContent = `${ticket.path} · content SHA-256 ${ticket.content_hash.slice(0, 16)}…`;
    $("#status-change").textContent = `${STATUS[ticket.work_status] || ticket.work_status} → Blocked`;
    $("#current-due").textContent = `Current card due: ${currentDue}. Any new date here comes only from the example voice.`;
    const ownerMatch = (ticket.owner || "").toLowerCase().includes("takhir");
    $("#comment-rationale").textContent = ownerMatch ? "The example voice named Takhir, who also owns this card." : `The example voice named Takhir; the card owner is ${ticket.owner || "not stated"}. That mismatch needs review.`;
    $("#advisor-line").textContent = !ticket.sources.length
      ? "This card has no source intent. I can point at the void, but I won’t decorate it and call it context."
      : !ticket.impacts.length && !ticket.dependencies.length
        ? "The ticket has source intent, but no machine-readable delivery impact. The Scope Goblin denies everything."
        : "Now you have the ticket, its why, its impact, and its sources. Friday still comes only from the example voice—not from KBOS.";
    $("#ticket-brief").hidden = false;
  }
  async function load() {
    if (!token) { showError("No local pairing token is stored on this device."); return; }
    const projectId = params.get("project") || localStorage.getItem("triage_project") || "granat";
    try {
      const response = await fetch(`/api/project/${encodeURIComponent(projectId)}`, {headers:{Authorization:`Bearer ${token}`}});
      if (!response.ok) throw new Error(response.status === 401 ? "Pairing failed or expired." : `Snapshot returned HTTP ${response.status}.`);
      const snapshot = await response.json();
      const requested = params.get("ticket") || localStorage.getItem(`triage_ticket:${projectId}`) || "";
      const selected = snapshot.tickets.find(item => item.key === requested) || snapshot.tickets.find(item => item.key === snapshot.queue[0]) || snapshot.tickets[0];
      if (!selected) throw new Error("This project has no readable ticket in the current snapshot.");
      render(snapshot, selected);
    } catch (error) { showError(error.message); }
  }

  document.querySelectorAll("[data-date]").forEach((button) => {
    button.addEventListener("click", () => {
      chosenDate = button.dataset.date;
      document.querySelectorAll("[data-date]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
      $("#approve").disabled = !ticket;
      $("#approve").textContent = "Approve demo decree";
      $("#advisor-line").textContent = `${chosenDate}. A date with an actual day and month. The Calendar Lich is furious.`;
      $("#toast").textContent = `Selected ${chosenDate} as your explicit choice—not a source-derived date.`;
    });
  });
  $("#approve").addEventListener("click", () => {
    if (!chosenDate || !ticket) return;
    $("#toast").textContent = `Demo only: no update was sent for ${ticket.display_id}.`;
    $("#advisor-line").textContent = "A clean decision. Somewhere, a Project Manager Demon bursts into flames.";
    $("#approve").textContent = "Demo approved · no write";
  });
  $("#reject").addEventListener("click", () => {
    $("#advisor-line").textContent = "Excellent. The unsupported decree has been returned to the backlog without supper.";
    $("#toast").textContent = "Returned without writing anything. As all good banishments should be.";
  });
  load();
})();
