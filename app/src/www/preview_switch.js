// preview_switch.js - a click on the "All rows" switch of the data preview must not fold or open the data panel
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// Why: the switch sits in the header of the accordion panel, which is one <button data-bs-toggle="collapse">. Bootstrap listens for
// that click on the document in the CAPTURE phase, so a stopPropagation on the switch or on an element around it comes too late.
// A capture listener on the window runs before the document's, and stops the click there. The switch still changes: its checking is
// the default action of the click, not a handler, and Shiny reads the change event.
(function () {
  if (window.__spvPreviewSwitch) return;
  window.__spvPreviewSwitch = true;
  window.addEventListener("click", function (e) {
    var t = e.target;
    if (t && t.closest && t.closest("#preview_all_rows, label[for='preview_all_rows']")) e.stopPropagation();
  }, true);
})();
