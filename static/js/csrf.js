function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}

window.gaplineFetch = function gaplineFetch(url, options = {}) {
  return fetch(url, {
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
      ...(options.headers || {}),
    },
    ...options,
  });
};

document.addEventListener("submit", (event) => {
  const form = event.target.closest(".write-form");
  if (!form) return;
  const button = form.querySelector("button[type='submit']");
  if (button) button.disabled = true;
});
