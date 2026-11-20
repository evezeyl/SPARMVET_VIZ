// panel_widths.js - the drag of the two side panels of the app frame (D-0381, D-0382, D-0384).
//
// bslib already draws a drag handle on each side panel and writes the dragged width as the inline variable --_sidebar-width of the layout.
// This script, in the page itself (nothing is sent to the server):
//   1. after each drag step, limits the width: not below the floor, and the two panels together at most half of the window, so the
//      main panel keeps at least half (D-0384). A drag that goes further stops at the limit.
//   2. after a drag, keeps the width of that panel in the browser's local storage as a SHARE of the window width, one value per side
//      (the frame is shared by all user spaces) (D-0382).
//   3. at page load, restores it: only a finite number between the stored-share limits is used, turned into px and limited as in 1;
//      anything else (missing, text, negative, out of range, broken JSON) is ignored and the default width stays. The number goes to
//      a style as a number of px built here, never as stored text.
//   4. on a window resize, applies the stored share again; a double click on the handle removes the stored value and gives the default
//      width back.
// All numbers (floors, ceilings, shares, the half rule) are read from data attributes of #spv_frame_widths, written by
// app/modules/frame_widths.py: they are not repeated here. Every access to local storage is inside try/catch (private windows).
(function () {
  "use strict";
  var KEY = "spv.panel_widths.v1";
  var IDS = { left: "nav_sidebar", right: "audit_sidebar" };
  var TITLE = "Drag to change the panel width. Double-click to reset.";   // PROVISIONAL words
  var cfg = null;
  var original = {};                  // the inline width the server built, to give back on a reset
  var shares = { left: null, right: null };   // user choice as a share of the window (null: the default)
  var current = { left: null, right: null };  // user choice in px now (null: the default)
  var moved = { left: false, right: false };

  function attr(el, name) {
    var v = parseFloat(el.getAttribute("data-" + name));
    return isFinite(v) ? v : null;
  }

  function readConfig() {
    var el = document.getElementById("spv_frame_widths");
    if (!el) return null;
    var c = { mainMin: attr(el, "main-min-share"), sMin: attr(el, "stored-share-min"), sMax: attr(el, "stored-share-max") };
    var ok = c.mainMin !== null && c.sMin !== null && c.sMax !== null;
    ["left", "right"].forEach(function (s) {
      c[s] = { share: attr(el, s + "-share"), floor: attr(el, s + "-floor"), ceiling: attr(el, s + "-ceiling") };
      ok = ok && c[s].share !== null && c[s].floor !== null && c[s].ceiling !== null;
    });
    return ok ? c : null;
  }

  function layoutOf(side) {
    var aside = document.getElementById(IDS[side]);
    return aside ? aside.closest(".bslib-sidebar-layout") : null;
  }

  function other(side) { return side === "left" ? "right" : "left"; }

  function defaultPx(side) {
    var p = cfg[side];
    return Math.min(Math.max(p.share * window.innerWidth, p.floor), p.ceiling);
  }

  function widthOf(side) { return current[side] !== null ? current[side] : defaultPx(side); }

  // the width a panel may take: the floor at least, and both panels together at most one minus the main-panel minimum
  function limit(side, px) {
    var most = window.innerWidth * (1 - cfg.mainMin) - widthOf(other(side));
    return Math.max(cfg[side].floor, Math.min(px, most));
  }

  function setWidth(side, px) {
    var layout = layoutOf(side);
    if (!layout) return;
    layout.style.setProperty("--_sidebar-width", Math.round(px) + "px");
    current[side] = px;
  }

  function loadStored() {
    var raw = null;
    try { raw = JSON.parse(window.localStorage.getItem(KEY) || "{}"); } catch (e) { return {}; }
    var out = {};
    if (!raw || typeof raw !== "object") return out;
    ["left", "right"].forEach(function (s) {
      var v = raw[s];
      if (typeof v === "number" && isFinite(v) && v >= cfg.sMin && v <= cfg.sMax) out[s] = v;
    });
    return out;
  }

  function store() {
    try {
      var o = {};
      ["left", "right"].forEach(function (s) { if (shares[s] !== null) o[s] = shares[s]; });
      if (Object.keys(o).length) window.localStorage.setItem(KEY, JSON.stringify(o));
      else window.localStorage.removeItem(KEY);
    } catch (e) { /* private window: the width is kept for this page only */ }
  }

  function applyShares() {
    ["left", "right"].forEach(function (s) {
      if (shares[s] === null) return;
      current[s] = null;                       // the other panel counts at its default until it is set
    });
    ["left", "right"].forEach(function (s) {
      if (shares[s] !== null) setWidth(s, limit(s, shares[s] * window.innerWidth));
    });
  }

  function sideOfEvent(ev) {
    var t = ev.target && ev.target.closest ? ev.target.closest("aside.sidebar") : null;
    var id = t ? t.id : "";
    return id === IDS.left ? "left" : id === IDS.right ? "right" : null;
  }

  function onResize(ev) {
    if (!cfg) return;
    var side = sideOfEvent(ev);
    var d = ev.detail || {};
    if (!side) return;
    if (d.phase === "start") { moved[side] = false; return; }
    if (d.phase !== "move" && d.phase !== "end" && d.phase !== "keyboard") return;
    var width = d.width;
    if (typeof width !== "number" || !isFinite(width)) return;
    if (d.phase === "move" || d.phase === "keyboard") moved[side] = true;
    if (d.phase === "end" && !moved[side]) return;       // a click on the handle changes nothing
    var limited = limit(side, width);
    if (Math.abs(limited - width) > 0.5) setWidth(side, limited); else current[side] = width;
    if (d.phase === "end" || d.phase === "keyboard") {
      shares[side] = current[side] / window.innerWidth;
      store();
    }
  }

  function reset(side) {
    var layout = layoutOf(side);
    shares[side] = null;
    current[side] = null;
    if (layout) {
      if (original[side]) layout.style.setProperty("--_sidebar-width", original[side]);
      else layout.style.removeProperty("--_sidebar-width");
    }
    store();
  }

  function onDoubleClick(ev) {
    if (!cfg || !ev.target || !ev.target.closest) return;
    var handle = ev.target.closest(".bslib-sidebar-resize-handle");
    if (!handle) return;
    var layout = handle.closest(".bslib-sidebar-layout");
    ["left", "right"].forEach(function (s) { if (layout && layout === layoutOf(s)) reset(s); });
  }

  function markHandles() {
    Array.prototype.forEach.call(document.querySelectorAll(".bslib-sidebar-resize-handle"), function (h) { h.setAttribute("title", TITLE); });
  }

  function init() {
    cfg = readConfig();
    if (!cfg) return;                           // no numbers on the page: the default widths stay, nothing is limited
    ["left", "right"].forEach(function (s) {
      var layout = layoutOf(s);
      original[s] = layout ? layout.style.getPropertyValue("--_sidebar-width") : "";
    });
    var stored = loadStored();
    shares.left = stored.left === undefined ? null : stored.left;
    shares.right = stored.right === undefined ? null : stored.right;
    applyShares();
    markHandles();
    document.addEventListener("bslib.sidebar.resize", onResize);
    document.addEventListener("dblclick", onDoubleClick);
    // bslib sets its own title on the handle when it starts: the tooltip is set again when the pointer comes to the handle
    document.addEventListener("mouseover", function (ev) {
      var h = ev.target && ev.target.closest ? ev.target.closest(".bslib-sidebar-resize-handle") : null;
      if (h && h.getAttribute("title") !== TITLE) h.setAttribute("title", TITLE);
    });
    document.addEventListener("shiny:connected", markHandles);
    window.addEventListener("resize", applyShares);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
