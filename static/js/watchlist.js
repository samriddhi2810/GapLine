document.addEventListener("submit", async (event) => {
  const form = event.target.closest("#add-stock-form");
  if (!form) return;
  event.preventDefault();
  const symbol = new FormData(form).get("symbol");
  const button = form.querySelector("button[type='submit']");
  if (button) button.disabled = true;
  try {
    const response = await window.gaplineFetch("/watchlists/api/items/", {
      method: "POST",
      body: JSON.stringify({ symbol }),
    });
    const data = await response.json().catch(() => ({}));
    if (response.ok) window.location.reload();
    else alert(data.detail || "Could not add stock.");
  } catch (error) {
    alert("Network error while adding stock.");
  } finally {
    if (button) button.disabled = false;
  }
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest(".mark-understood");
  if (!button) return;
  button.disabled = true;
  try {
    const response = await window.gaplineFetch(`/watchlists/api/items/${button.dataset.itemId}/mark-understood/`, { method: "POST", body: "{}" });
    const data = await response.json().catch(() => ({}));
    if (response.ok) window.location.reload();
    else alert(data.detail || "Could not mark understood.");
  } catch (error) {
    alert("Network error while marking understood.");
  } finally {
    button.disabled = false;
  }
});
