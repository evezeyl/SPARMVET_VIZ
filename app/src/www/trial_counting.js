// trial_counting.js - the line "Counting the rows each place loses..." appears at the click on "Try", not after the answer
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// Why: the trial of an audit step is computed by the server in one go (the engine builds the tables of the places), which can take seconds. The server cannot show a line while it works: its outputs go
// out when the work is done. So the page shows the line itself, at the click (a class on <html>), and takes it away when Shiny is idle again. The line is a static element of the Filters panel
// (`.spv-try-counting`, hidden by `config/ui/theme.css` unless `html.spv-try-counting-on`); the answer is the panel `trial_panel_ui`.
(function () {
  if (window.__spvTrialCounting) return;
  window.__spvTrialCounting = true;
  var on = "spv-try-counting-on";
  window.addEventListener("click", function (e) {
    var t = e.target;
    if (t && t.closest && t.closest("#filter_try")) document.documentElement.classList.add(on);
  }, true);
  function idle() { document.documentElement.classList.remove(on); }
  if (window.jQuery) window.jQuery(document).on("shiny:idle", idle);
  else document.addEventListener("shiny:idle", idle);
})();
