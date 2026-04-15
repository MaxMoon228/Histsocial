document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#axis-form");
  if (!form) return;

  const bindToggle = (groupName, inputId) => {
    const group = form.querySelector(`[data-axis-toggle='${groupName}']`);
    const hidden = form.querySelector(`#${inputId}`);
    if (!group || !hidden) return;
    group.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-value]");
      if (!button) return;
      group.querySelectorAll("button").forEach((node) => node.classList.remove("is-active"));
      button.classList.add("is-active");
      hidden.value = button.dataset.value;
    });
  };

  bindToggle("scope", "axis-scope");
  bindToggle("scale", "axis-scale");

  const setActiveNode = (nodeButton) => {
    if (!nodeButton) return;
    document.querySelectorAll(".timeline-node-btn").forEach((node) => {
      node.classList.remove("is-active");
      node.setAttribute("aria-pressed", "false");
    });
    nodeButton.classList.add("is-active");
    nodeButton.setAttribute("aria-pressed", "true");
  };

  document.body.addEventListener("click", (event) => {
    const nodeButton = event.target.closest(".timeline-node-btn");
    if (!nodeButton) return;
    setActiveNode(nodeButton);
  });

  document.body.addEventListener("htmx:beforeRequest", (event) => {
    const triggerEl = event.detail?.elt;
    if (triggerEl && triggerEl.classList && triggerEl.classList.contains("timeline-node-btn")) {
      setActiveNode(triggerEl);
    }
  });
});

document.body.addEventListener("htmx:afterSwap", (event) => {
  if (event.target.id !== "axis-results") return;
  const firstNode = event.target.querySelector(".timeline-node-btn");
  if (firstNode) {
    firstNode.classList.add("is-active");
    htmx.ajax("GET", `/htmx/axis/node/${firstNode.dataset.axisNodeId}/`, {
      target: "#axis-detail",
      swap: "innerHTML",
    });
  } else {
    const detail = document.querySelector("#axis-detail");
    if (detail) {
      detail.innerHTML = "<article class='card axis-empty'><h3>Ничего не найдено</h3><p>Измените параметры фильтра и повторите запрос.</p></article>";
    }
  }
});
