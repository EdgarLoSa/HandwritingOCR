document.addEventListener("DOMContentLoaded", () => {
  const zones = document.querySelectorAll("[data-dropzone]");
  zones.forEach((zone) => {
    const input = zone.querySelector("input[type='file']");
    const label = zone.querySelector(".dropzone-subtitle");

    input.addEventListener("change", () => {
      label.textContent = input.files.length
        ? `${input.files.length} file(s) selected`
        : "or click to select multiple files";
    });

    zone.addEventListener("dragover", (event) => {
      event.preventDefault();
      zone.classList.add("is-dragging");
    });
    zone.addEventListener("dragleave", () => zone.classList.remove("is-dragging"));
    zone.addEventListener("drop", () => zone.classList.remove("is-dragging"));
  });

  const cards = document.querySelectorAll("[data-job-card]");
  cards.forEach((card) => {
    const jobUuid = card.dataset.jobUuid;
    const statusNode = card.querySelector("[data-job-status]");
    const progressNode = card.querySelector("[data-job-progress]");
    const totalNode = card.querySelector("[data-job-total]");
    const textNode = card.querySelector("[data-job-text]");

    const refresh = async () => {
      try {
        const response = await fetch(`/api/jobs/${jobUuid}`);
        if (!response.ok) {
          return;
        }
        const job = await response.json();
        statusNode.textContent = job.status;
        progressNode.textContent = job.progress;
        totalNode.textContent = job.total;
        if (job.text) {
          textNode.textContent = job.text;
          textNode.hidden = false;
        }
        if (job.status === "completed" || job.status === "failed") {
          clearInterval(timer);
        }
      } catch (error) {
        console.error(error);
      }
    };

    const timer = setInterval(refresh, 3000);
    refresh();
  });
});
