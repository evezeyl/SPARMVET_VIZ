// audit_places_path.js - the places of the audit dialog read as the path of the lineage, and the places that follow from a ticked place are shown as derived
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// The server computes, when the dialog opens, for each place its depth on the path and what ticking it derives (the places below) and blocks (the places above):
// `data-path` on #propagation_places_wrapper, from `audit_places.path_rows` (one rule: `RecipeGraph.chosen_places_problem`). This script only combines them for the ticks
// the user has made, so that the list is NOT drawn again on a click (ui_implementation_contract.md section 14, R4). The refusal on the server at confirm stays the safety net.
// PROVISIONAL words: the two notes.
(function () {
  if (window.__spvAuditPlaces) return;
  window.__spvAuditPlaces = true;
  var DERIVED_NOTE = "~ follows from the place chosen above";
  var BLOCKED_NOTE = "a place below it is chosen: one place on a path";

  function rowOf(input) {
    var label = input.closest("label");
    return (label && label.parentElement) || input.parentElement;
  }

  function note(row, text) {
    var n = row.querySelector(".spv-place-note");
    if (!text) { if (n) n.remove(); return; }
    if (!n) { n = document.createElement("small"); n.className = "spv-place-note text-muted d-block"; row.appendChild(n); }
    n.textContent = text;
  }

  function apply(wrapper) {
    var data;
    try { data = JSON.parse(wrapper.getAttribute("data-path") || "{}"); } catch (e) { return; }
    var rows = data.rows || {};
    var inputs = Array.prototype.slice.call(wrapper.querySelectorAll("input[type=checkbox]"));
    var derived = {}, blocked = {};
    inputs.forEach(function (input) {
      var info = rows[input.value];
      if (!input.checked || !info) return;
      (info.derived || []).forEach(function (p) { derived[p] = true; });
      (info.blocked || []).forEach(function (p) { blocked[p] = true; });
    });
    inputs.forEach(function (input) {
      var info = rows[input.value] || {};
      var row = rowOf(input);
      row.classList.add("spv-place-row");
      row.style.setProperty("--spv-depth", String(info.depth || 0));
      var isDerived = !input.checked && derived[input.value];
      var isBlocked = !input.checked && !isDerived && blocked[input.value];
      input.disabled = !!(isDerived || isBlocked);
      row.classList.toggle("spv-place-derived", !!isDerived);
      row.classList.toggle("spv-place-blocked", !!isBlocked);
      note(row, isDerived ? DERIVED_NOTE : (isBlocked ? BLOCKED_NOTE : ""));
    });
  }

  function start(root) {
    var w = (root.id === "propagation_places_wrapper") ? root : (root.querySelector && root.querySelector("#propagation_places_wrapper"));
    if (w) apply(w);
  }

  document.addEventListener("change", function (e) {
    var w = e.target && e.target.closest && e.target.closest("#propagation_places_wrapper");
    if (w) apply(w);
  });
  new MutationObserver(function (mutations) {
    mutations.forEach(function (m) { m.addedNodes.forEach(function (n) { if (n.nodeType === 1) start(n); }); });
  }).observe(document.documentElement, { childList: true, subtree: true });
})();
