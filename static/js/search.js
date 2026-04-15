document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll(".search-form[data-suggest-url]");
  forms.forEach((form) => {
    const input = form.querySelector("input[name='q']");
    const target = form.querySelector("[data-suggest-target]");
    const suggestUrl = form.dataset.suggestUrl;
    if (!input || !target || !suggestUrl) return;
    let timeout;
    input.addEventListener("input", () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        const q = input.value.trim();
        if (q.length < 2) {
          target.innerHTML = "";
          return;
        }
        fetch(`${suggestUrl}?q=${encodeURIComponent(q)}`)
          .then((response) => response.text())
          .then((html) => {
            target.innerHTML = html;
          });
      }, 250);
    });
  });
});
