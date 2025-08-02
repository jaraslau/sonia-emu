document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("analog-toggle");
  toggle.addEventListener("change", () => {
    const analog = document.querySelectorAll(".analog-trigger");
    const digital = document.querySelectorAll(".button-trigger");
    const topButtons = document.getElementById("top-buttons");
    if (toggle.checked) {
      analog.forEach((el) => (el.style.display = "flex"));
      digital.forEach((el) => (el.style.display = "none"));
      topButtons.style.top = "-10%";
    } else {
      analog.forEach((el) => (el.style.display = "none"));
      digital.forEach((el) => (el.style.display = "flex"));
      topButtons.style.top = "10%";
    }
  });
});
