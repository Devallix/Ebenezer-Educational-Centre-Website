/* Ebenezer Educational Centre - dashboard interactions */
(function () {
  "use strict";

  function initSidebar() {
    var sidebar = document.querySelector(".dash-sidebar");
    var main = document.querySelector(".dash-main");
    var backdrop = document.querySelector(".sidebar-backdrop");
    var toggle = document.querySelector("[data-sidebar-toggle]");
    if (!sidebar || !toggle) return;

    function isMobile() { return window.matchMedia("(max-width: 991.98px)").matches; }

    toggle.addEventListener("click", function () {
      if (isMobile()) {
        sidebar.classList.toggle("open");
        if (backdrop) backdrop.classList.toggle("show", sidebar.classList.contains("open"));
      } else {
        sidebar.classList.toggle("collapsed");
        if (main) main.classList.toggle("expanded", sidebar.classList.contains("collapsed"));
        try { localStorage.setItem("ec-sidebar-collapsed", sidebar.classList.contains("collapsed") ? "1" : "0"); } catch (e) {}
      }
    });
    if (backdrop) {
      backdrop.addEventListener("click", function () {
        sidebar.classList.remove("open");
        backdrop.classList.remove("show");
      });
    }
    if (!isMobile()) {
      try {
        if (localStorage.getItem("ec-sidebar-collapsed") === "1") {
          sidebar.classList.add("collapsed");
          if (main) main.classList.add("expanded");
        }
      } catch (e) {}
    }
  }

  /* Live colour picker <-> hex text sync */
  function initColourInputs() {
    var inputs = document.querySelectorAll('input[type="color"][data-colour]');
    inputs.forEach(function (picker) {
      var text = document.querySelector('[data-colour-text="' + picker.name + '"]');
      if (!text) {
        // Fall back: pair with the next text input in the same column.
        var wrap = picker.closest(".colour-row");
        text = wrap ? wrap.querySelector('input[type="text"]') : null;
      }
      if (!text) return;
      picker.addEventListener("input", function () { text.value = picker.value.toUpperCase(); });
      text.addEventListener("input", function () {
        if (/^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(text.value.trim())) {
          picker.value = text.value.trim();
        }
      });
    });
  }

  /* Live theme preview (updates public tokens on the fly) */
  function initThemePreview() {
    var form = document.querySelector("[data-theme-form]");
    if (!form) return;
    var preview = form.querySelector("[data-theme-preview]");
    if (!preview) return;
    form.querySelectorAll('input[type="color"]').forEach(function (input) {
      input.addEventListener("input", function () {
        if (input.name === "primary_color") preview.style.background = input.value;
        if (input.name === "accent_color") {
          var accent = preview.querySelector(".tp-accent");
          if (accent) accent.style.background = input.value;
        }
      });
    });
  }

  /* Confirm destructive actions */
  function initConfirm() {
    document.querySelectorAll("[data-confirm]").forEach(function (el) {
      el.addEventListener("submit", function (e) {
        if (!window.confirm(el.dataset.confirm)) e.preventDefault();
      });
    });
  }

  /* Auto-dismiss success alerts */
  function initAlerts() {
    document.querySelectorAll("[data-autodismiss]").forEach(function (el) {
      setTimeout(function () {
        el.style.transition = "opacity .4s ease";
        el.style.opacity = "0";
        setTimeout(function () { el.remove(); }, 400);
      }, 6000);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initSidebar();
    initColourInputs();
    initThemePreview();
    initConfirm();
    initAlerts();
  });
})();
