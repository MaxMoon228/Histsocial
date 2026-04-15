document.addEventListener("DOMContentLoaded", () => {
  const modal = document.querySelector("#external-go-modal");
  if (!modal) return;

  const titleNode = modal.querySelector("#external-go-item-title");
  const domainNode = modal.querySelector("#external-go-domain");
  const labelNode = modal.querySelector("#external-go-content-label");
  const confirmNode = modal.querySelector("#external-go-confirm");
  let pendingUrl = "";

  const setOpen = (isOpen) => {
    modal.classList.toggle("is-open", isOpen);
    modal.setAttribute("aria-hidden", isOpen ? "false" : "true");
    document.body.classList.toggle("has-modal-open", isOpen);
  };

  const close = () => setOpen(false);

  document.body.addEventListener("click", (event) => {
    const trigger = event.target.closest(".js-external-go");
    if (trigger) {
      event.preventDefault();
      const itemTitle = trigger.dataset.itemTitle || "материалу";
      const domain = trigger.dataset.sourceDomain || "внешнему ресурсу";
      const contentLabel = trigger.dataset.contentLabel || "материалу";

      titleNode.textContent = `«${itemTitle}»`;
      domainNode.textContent = domain;
      labelNode.textContent = contentLabel;
      pendingUrl = trigger.getAttribute("href") || "";
      setOpen(true);
      return;
    }

    if (event.target.closest("[data-external-close]")) {
      close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close();
  });

  confirmNode.addEventListener("click", () => {
    if (!pendingUrl) return;
    window.location.assign(pendingUrl);
  });
});
