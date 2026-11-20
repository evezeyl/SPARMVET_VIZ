// gallery_select_all.js - the "Select all" box of a Gallery filter group ticks or clears the group in the page itself
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// Why: when the server did this (it answered the box with an update of the group), the answer could arrive after the
// user had already ticked one term, and it wiped that tick: the filter then did nothing (found 2026-11-20, 30 of 30
// fast tries; GALLERY-CHECK-1 finding 9). Done in the page, the group changes in the same step as the box, and the
// server only receives the new values, in the order the user made them.
//
// Contract with app/modules/gallery_viewer.py: the box has id "gallery_all_<axis>", the group's checkboxes have the
// name "gallery_filter_<axis>".
(function () {
  "use strict";

  var PREFIX = "gallery_all_";

  document.addEventListener("change", function (event) {
    var box = event.target;
    if (!box || !box.id || box.id.indexOf(PREFIX) !== 0 || box.type !== "checkbox") { return; }
    var axis = box.id.slice(PREFIX.length);
    var items = document.querySelectorAll("input[type=checkbox][name='gallery_filter_" + axis + "']");
    if (!items.length) { return; }
    items.forEach(function (item) { item.checked = box.checked; });
    // One change event on the group makes Shiny read all of its boxes; it bubbles, as a click would.
    items[0].dispatchEvent(new Event("change", { bubbles: true }));
  });
})();
