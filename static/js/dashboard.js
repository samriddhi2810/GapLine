document.addEventListener("click", async (event) => {
  const button = event.target.closest(".mark-understood");
  if (!button) return;
  button.disabled = true;
  const itemId = button.dataset.itemId;
  try {
    const response = await window.gaplineFetch(`/watchlists/api/items/${itemId}/mark-understood/`, { method: "POST", body: "{}" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      alert(data.detail || "Could not mark understood.");
      return;
    }
    window.location.reload();
  } catch (error) {
    alert("Network error while marking understood.");
  } finally {
    button.disabled = false;
  }
});

document.addEventListener("submit", (event) => {
  const form = event.target.closest(".write-form");
  if (!form) return;
  const button = form.querySelector("button[type='submit']");
  if (button) button.disabled = true;
});
