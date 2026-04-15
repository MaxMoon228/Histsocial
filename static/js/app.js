document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("a[href='#']").forEach((node) => {
    node.addEventListener("click", (event) => event.preventDefault());
  });
});

document.body.addEventListener("htmx:configRequest", (event) => {
  const fromMeta = document.querySelector("meta[name='csrf-token']")?.getAttribute("content");
  if (fromMeta && fromMeta !== "NOTPROVIDED") {
    event.detail.headers["X-CSRFToken"] = fromMeta;
    return;
  }
  const cookie = document.cookie
    .split(";")
    .map((entry) => entry.trim())
    .find((entry) => entry.startsWith("csrftoken="));
  if (cookie) {
    event.detail.headers["X-CSRFToken"] = cookie.split("=")[1];
  }
});
