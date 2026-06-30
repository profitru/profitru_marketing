/**
 * Stacked dropdown nav: desktop flyouts, mobile accordions; click-outside and Escape to close.
 */
(function () {
  "use strict";

  var groups = document.querySelectorAll(".nav-mega[data-nav-dropdown]");
  if (!groups.length) return;

  function getPanel(btn) {
    var id = btn.getAttribute("aria-controls");
    if (!id) return null;
    return document.getElementById(id);
  }

  function setOpen(mega, btn, panel, open) {
    if (!btn || !panel) return;
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      panel.removeAttribute("hidden");
      mega.classList.add("nav-mega--open");
    } else {
      panel.setAttribute("hidden", "");
      mega.classList.remove("nav-mega--open");
    }
  }

  function closeAll() {
    groups.forEach(function (mega) {
      var btn = mega.querySelector(".nav-mega__btn");
      var panel = btn ? getPanel(btn) : null;
      if (btn && panel) setOpen(mega, btn, panel, false);
    });
  }

  function closeOthers(keepMega) {
    groups.forEach(function (mega) {
      if (mega === keepMega) return;
      var btn = mega.querySelector(".nav-mega__btn");
      var panel = btn ? getPanel(btn) : null;
      if (btn && panel) setOpen(mega, btn, panel, false);
    });
  }

  groups.forEach(function (mega) {
    var btn = mega.querySelector(".nav-mega__btn");
    var panel = btn ? getPanel(btn) : null;
    if (!btn || !panel) return;
    if (!panel.hasAttribute("hidden")) panel.setAttribute("hidden", "");
    setOpen(mega, btn, panel, false);

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var expanded = btn.getAttribute("aria-expanded") === "true";
      if (expanded) {
        setOpen(mega, btn, panel, false);
      } else {
        closeOthers(mega);
        setOpen(mega, btn, panel, true);
      }
    });
  });

  document.addEventListener("click", function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    if (t.closest(".nav-mega")) return;
    closeAll();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" || e.key === "Esc") {
      closeAll();
    }
  });

  document.querySelectorAll(".nav-mega__panel a[href]").forEach(function (a) {
    a.addEventListener("click", function () {
      closeAll();
    });
  });

  var navRoot = document.querySelector(".nav-links--mega");
  if (navRoot && typeof MutationObserver !== "undefined") {
    var lastOpen = navRoot.classList.contains("open");
    var ob = new MutationObserver(function () {
      var o = navRoot.classList.contains("open");
      if (lastOpen && !o) closeAll();
      lastOpen = o;
    });
    ob.observe(navRoot, { attributes: true, attributeFilter: ["class"] });
  }
})();
