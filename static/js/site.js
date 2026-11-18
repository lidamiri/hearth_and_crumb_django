document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.querySelectorAll(".stepper button[data-step]").forEach(function (button) {
    button.addEventListener("click", function () {
      var input = button.parentElement.querySelector("input");
      var max = parseInt(input.getAttribute("max"), 10) || 50;
      var next = (parseInt(input.value, 10) || 1) + parseInt(button.dataset.step, 10);
      input.value = Math.min(Math.max(next, 1), max);
    });
  });

  document.querySelectorAll(".messages").forEach(function (list) {
    setTimeout(function () {
      list.style.transition = "opacity 0.6s";
      list.style.opacity = "0";
      setTimeout(function () { list.remove(); }, 700);
    }, 6000);
  });
});
