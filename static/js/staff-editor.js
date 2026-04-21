(function () {
  const drawer = document.getElementById("staff-editor-drawer");
  if (!drawer) return;

  const body = document.getElementById("staff-editor-body");
  const toast = document.getElementById("staff-toast");
  let isDirty = false;

  function openDrawer() {
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
  }

  function closeDrawer() {
    if (isDirty && !window.confirm("Есть несохраненные изменения. Закрыть редактор?")) return;
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    body.innerHTML = "";
    isDirty = false;
  }

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    setTimeout(() => toast.classList.remove("is-visible"), 1800);
  }

  document.addEventListener("click", function (event) {
    const closeTarget = event.target.closest("[data-staff-close]");
    if (closeTarget) {
      event.preventDefault();
      closeDrawer();
      return;
    }
    const trigger = event.target.closest("[hx-get^='/staff/materials/'], [hx-get^='/staff/events/'], [hx-get^='/staff/axis-nodes/'], [hx-get^='/staff/tests/']");
    if (trigger) openDrawer();
  });

  document.addEventListener("change", function (event) {
    if (event.target.closest("[data-staff-form]")) isDirty = true;
  });

  document.addEventListener("keydown", function (event) {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
      const form = document.querySelector("[data-staff-form]");
      if (!form) return;
      event.preventDefault();
      form.requestSubmit();
    }
    if (event.key === "Escape" && drawer.classList.contains("is-open")) {
      closeDrawer();
    }
  });

  document.body.addEventListener("htmx:afterSwap", function (event) {
    if (event.target && event.target.id === "staff-editor-body") {
      openDrawer();
      isDirty = false;
      const success = event.target.querySelector("[data-staff-success]");
      if (success) {
        const message = success.getAttribute("data-message") || "Сохранено";
        showToast(message);
        closeDrawer();
        window.setTimeout(() => window.location.reload(), 300);
      }
    }
  });

  document.body.addEventListener("material-updated", function () {
    showToast("Изменения применены");
    window.setTimeout(() => window.location.reload(), 300);
  });

  document.body.addEventListener("staff-updated", function () {
    showToast("Изменения применены");
    window.setTimeout(() => window.location.reload(), 300);
  });

  document.addEventListener("click", function (event) {
    const runBtn = event.target.closest(".js-staff-bulk-run");
    if (!runBtn) return;
    const actionSelect = document.querySelector(runBtn.dataset.targetAction);
    if (!actionSelect || !actionSelect.value) return;
    const selected = Array.from(document.querySelectorAll(".js-staff-select:checked")).map((input) => input.value);
    if (!selected.length) {
      window.alert("Выберите карточки для массового действия.");
      return;
    }
    const csrfMeta = document.querySelector("meta[name='csrf-token']");
    const formData = new FormData();
    formData.append("ids", selected.join(","));
    formData.append("action", actionSelect.value);
    fetch("/staff/materials/bulk/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfMeta ? csrfMeta.content : "",
      },
      body: formData,
    }).then(() => {
      showToast("Массовое действие выполнено");
      window.location.reload();
    });
  });
})();
