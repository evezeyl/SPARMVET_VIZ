// step_bar.js - the plain switch of the step bar ("Condition on rows" | "Drop columns") shows one part of the bar at a time
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// Why in the browser: the form of the condition must stay mounted (its inputs keep what the user typed), so the server does not draw it again when the switch changes; the switch only sets the
// attribute `data-kind` of the bar, and the style sheet (`config/ui/theme.css`, section 33) shows the part that the kind names. The server reads the switch (`step_kind`) when Try is pressed.
(function () {
  if (window.__spvStepBar) return;
  window.__spvStepBar = true;
  document.addEventListener("change", function (e) {
    var t = e.target;
    if (!t || t.name !== "step_kind" || !t.closest) return;
    var bar = t.closest(".spv-stepbar-inner");
    if (bar) bar.setAttribute("data-kind", t.value);
  });
})();
