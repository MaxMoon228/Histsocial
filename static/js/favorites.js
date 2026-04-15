document.body.addEventListener("htmx:afterSwap", (event) => {
  const xhr = event.detail?.xhr;
  const isFavoriteToggle = xhr && xhr.responseURL.includes("/htmx/favorites/toggle/");
  if (isFavoriteToggle || event.target.closest?.(".favorite-btn")) {
    htmx.ajax("GET", "/htmx/favorites/count/", { target: "#favorites-counter", swap: "outerHTML" });
  }
});
