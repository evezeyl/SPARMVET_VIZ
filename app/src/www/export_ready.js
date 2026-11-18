// export_ready.js - the Export button is ready only when the server holds the values on the screen (D-0270)
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// Why: Shiny applies the input messages of the page under the reactive lock, but it handles a download request without
// it. A tick or a label changed a moment before a press on Export could arrive after the download request and be lost.
// So the button is grey from each change of the Export panel until the server has echoed the values it holds and they
// are equal to the values now on the screen. The echo is a real round trip, not a delay.
//
// Contract with app/handlers/export_handlers.py (system_tools_ui, _confirm_export_inputs):
//   - the panel block has id "export_ready_panel" and the attributes data-ready-fields (JSON list of input ids),
//     data-text-waiting, data-text-lost, data-timeout-ms. The texts live only in Python (EXPORT_READY_TEXTS).
//   - the page sends the input "export_client_ping" (event priority) at each change, also at a change the server made
//     (Shiny's "shiny:inputchanged" event).
//   - the server answers with the custom message "export_ready_echo": {ping: last ping it has seen, values: {field id: value it holds}}.
(function () {
  "use strict";

  var PANEL_ID = "export_ready_panel";
  var BUTTON_ID = "export_bundle_download";
  var pending = false;      // a change was made and the server has not confirmed it yet
  var pingCount = 0;
  var timer = null;
  var readyHtml = null;     // what the button shows when it is ready (its own text, set by the server)
  var observer = null;

  function panel() { return document.getElementById(PANEL_ID); }
  function button() { return document.getElementById(BUTTON_ID); }

  function attr(name, fallback) {
    var p = panel();
    var v = p ? p.getAttribute(name) : null;
    return v === null || v === undefined ? fallback : v;
  }

  function fields() {
    try { return JSON.parse(attr("data-ready-fields", "[]")); } catch (e) { return []; }
  }

  // the id of the Export field an event came from (a radio's element has the name of its field)
  function fieldOf(target) {
    var list = fields();
    for (var el = target; el && el !== document; el = el.parentElement) {
      if (el.id && list.indexOf(el.id) >= 0) return el.id;
      if (el.name && list.indexOf(el.name) >= 0) return el.name;
    }
    return null;
  }

  // the value the page would send for a field now, read the way Shiny reads it
  function screenValue(id) {
    var el = document.getElementById(id);
    if (!el || !window.jQuery) return undefined;
    var binding = window.jQuery(el).data("shiny-input-binding");
    return binding ? binding.getValue(el) : undefined;
  }

  function same(a, b) { return JSON.stringify(a === undefined ? null : a) === JSON.stringify(b === undefined ? null : b); }

  function render() {
    var b = button();
    if (!b) return;
    if (readyHtml === null && !b.classList.contains("export-not-ready")) readyHtml = b.innerHTML;
    var greyed = b.classList.contains("export-not-ready");
    if (pending) {
      if (!greyed) {
        if (readyHtml === null) readyHtml = b.innerHTML;
        b.classList.add("export-not-ready");
      }
      // Shiny removes aria-disabled from a download link when it has received the output's value, which can come after the
      // page greyed the button (a change made at load); the mark must be there as long as the button is grey.
      b.setAttribute("aria-disabled", "true");
      var waiting = attr("data-text-waiting", "");
      if (b.textContent.trim() !== waiting) b.textContent = waiting;
    } else if (greyed) {
      b.classList.remove("export-not-ready");
      b.removeAttribute("aria-disabled");
      if (readyHtml !== null) b.innerHTML = readyHtml;
    }
  }

  function settle() {
    pending = false;
    if (timer) { clearTimeout(timer); timer = null; }
    render();
  }

  function startWaiting() {
    pending = true;
    render();
    if (timer) clearTimeout(timer);
    var ms = parseInt(attr("data-timeout-ms", "5000"), 10) || 5000;
    timer = setTimeout(function () {
      // the confirmation did not come: the button must not stay grey for ever
      if (!pending) return;
      lastSeen = {};   // the server's values are not known any more
      settle();
      var text = attr("data-text-lost", "");
      if (text && window.Shiny && window.Shiny.notifications) {
        window.Shiny.notifications.show({ html: text, type: "warning", duration: 15000 });
      }
    }, ms);
    if (window.Shiny && window.Shiny.setInputValue) {
      pingCount += 1;
      window.Shiny.setInputValue("export_client_ping", pingCount, { priority: "event" });
    }
  }

  // The value of each field the last time this script saw it change. The browser fires "change" when a text field loses
  // focus, which happens at the mouse-down on the Export button itself: that is not a new value, and greying the button
  // between the mouse-down and the mouse-up would swallow the click.
  var lastSeen = {};

  function noteValue(id) {
    var value = JSON.stringify(screenValue(id) === undefined ? null : screenValue(id));
    if (Object.prototype.hasOwnProperty.call(lastSeen, id) && lastSeen[id] === value) return;
    lastSeen[id] = value;
    startWaiting();
  }

  function onChange(event) {
    var id = fieldOf(event.target);
    if (id === null) return;
    noteValue(id);
  }

  // A value the SERVER sets (a recipe switch puts the fields of that session in the panel) raises no native "input" or "change"
  // event on the page, but Shiny announces every change of an input, whoever made it, with "shiny:inputchanged". The button is
  // grey from that moment until the server confirms that it holds the shown values, as for a value the user typed. (A custom
  // message from the server cannot do this: it is sent before the input messages and would arrive before the new values.)
  function onShinyInput(event) {
    var id = event && event.name;
    if (!id || fields().indexOf(id) < 0 || !document.getElementById(id)) return;
    noteValue(id);
  }

  // a press on a grey button does nothing: not a click, not Enter, not Space
  function blockIfGrey(event) {
    var b = button();
    if (!b || !pending) return;
    if (event.target === b || b.contains(event.target)) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  }

  function onKey(event) {
    if (event.key === "Enter" || event.key === " " || event.key === "Spacebar") blockIfGrey(event);
  }

  function onEcho(message) {
    if (!pending) return;
    var held = (message && message.values) || {};
    // the server must have seen the last ping: every input message sent before it was applied (the websocket is ordered)
    if (!message || typeof message.ping !== "number" || message.ping < pingCount) return;
    var list = fields();
    for (var i = 0; i < list.length; i++) {
      var id = list[i];
      if (!document.getElementById(id)) continue;      // a field that is not on this page (for example Scope)
      if (!Object.prototype.hasOwnProperty.call(held, id)) return;
      if (!same(held[id], screenValue(id))) return;    // the server holds an older value; a newer echo will come
    }
    // what the server holds is now known: a later event with the same value is not a change
    lastSeen = {};
    for (var j = 0; j < list.length; j++) {
      if (document.getElementById(list[j])) lastSeen[list[j]] = JSON.stringify(held[list[j]] === undefined ? null : held[list[j]]);
    }
    settle();
  }

  function registerHandler() {
    if (window.Shiny && window.Shiny.addCustomMessageHandler && window.jQuery) {
      window.Shiny.addCustomMessageHandler("export_ready_echo", onEcho);
      window.jQuery(document).on("shiny:inputchanged", onShinyInput);
      return true;
    }
    return false;
  }

  document.addEventListener("input", onChange, true);
  document.addEventListener("change", onChange, true);
  document.addEventListener("click", blockIfGrey, true);
  // a middle click does not fire "click" but "auxclick", and it also starts the download of a link
  document.addEventListener("auxclick", blockIfGrey, true);
  document.addEventListener("keydown", onKey, true);
  document.addEventListener("keyup", onKey, true);

  // the button may be drawn again by the server: show the waiting state on the new one
  // The server redraws the panel after a user-space switch: the new element is not the one whose values were remembered,
  // so a later change to the same value must count as a change again.
  var lastPanel = null;
  observer = new MutationObserver(function () {
    var p = panel();
    if (p !== lastPanel) { lastPanel = p; lastSeen = {}; }
    if (pending || (button() && button().classList.contains("export-not-ready"))) render();
  });
  function observe() {
    if (document.body) observer.observe(document.body, { childList: true, subtree: true });
    else document.addEventListener("DOMContentLoaded", observe);
  }
  observe();

  (function wait() { if (!registerHandler()) setTimeout(wait, 50); })();
})();
