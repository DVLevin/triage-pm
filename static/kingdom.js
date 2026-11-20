(() => {
  let chosenDate = "";
  const approve = document.querySelector("#approve");
  const advisor = document.querySelector("#advisor-line");
  const toast = document.querySelector("#toast");
  document.querySelectorAll("[data-date]").forEach((button) => {
    button.addEventListener("click", () => {
      chosenDate = button.dataset.date;
      document.querySelectorAll("[data-date]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      approve.disabled = false;
      approve.textContent = "Approve decree";
      advisor.textContent = `${chosenDate}. A date with an actual day and month. The Calendar Lich is furious.`;
      toast.textContent = `Ready to preview the ${chosenDate} update.`;
    });
  });
  approve.addEventListener("click", () => {
    if (!chosenDate) return;
    toast.textContent = "Concept only: no Jira write. The live version would now show the exact payload and confirmation.";
    advisor.textContent = "A clean decision. Somewhere, a Project Manager Demon bursts into flames.";
    approve.textContent = "Decree previewed";
  });
  document.querySelector("#reject").addEventListener("click", () => {
    advisor.textContent = "Excellent. The Scope Goblin has been returned to the backlog without supper.";
    toast.textContent = "Returned without writing anything. As all good banishments should be.";
  });
})();
