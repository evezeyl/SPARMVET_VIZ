// gallery_select_all.js - the "Select all" box of a Gallery filter group ticks or clears the group in the page itself
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// Why: when the server did this (it answered the box with an update of the group), the answer could arrive after the
// user had already ticked one term, and it wiped that tick: the filter then did nothing (found 2026-11-20, 30 of 30
// fast tries; GALLERY-CHECK-1 finding 9). Done in the page, the group changes in the same step as the box, and the
// server only receives the new values, in the order the user made them.
//
// "Clear all ticks" (D-0379 follow-up, PROVISIONAL label): the button with id "gallery_clear_ticks" unticks the
// "Select all" box and every term of every group, in the same step. It changes ticks only: the list changes after
// Apply, like any tick (the rule of APPLY_RULE_TEXT). A group with nothing ticked does not filter.
//
// Contract with app/modules/gallery_viewer.py: the box has id "gallery_all_<axis>", the group's checkboxes have the
// name "gallery_filter_<axis>", the clear button has id "gallery_clear_ticks".
(function () {
  "use strict";

  var PREFIX = "gallery_all_";

  document.addEventListener("click", function (event) {
    var button = event.target && event.target.closest ? event.target.closest("#gallery_clear_ticks") : null;
    if (!button) { return; }
    document.querySelectorAll("input[type=checkbox][id^='" + PREFIX + "']").forEach(function (box) {
      box.checked = false;
      // The change handler below unticks the terms of the group and tells Shiny; a second event on the box tells it
      // the box itself changed.
      box.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });

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
