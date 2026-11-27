// lineage_view.js - the lineage panel of HOME (Audit mode): a list (the reader and the text twin of every dot) and a map of dots, to choose the place of an audit step (D-0629, D-0634)
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// The server draws the container once per recipe (app/handlers/lineage_handlers.py) with the data of app/modules/lineage_view.py in a <script type="application/json"> tag;
// this script builds the list and the map from it and handles hover, focus, keyboard, choice, pan, zoom and the size of the parts in the browser, so that a click never makes the
// server draw the panel again (ui_implementation_contract.md section 14, R4). The server is told the choice with Shiny.setInputValue('lineage_chosen', [...ids], {priority:'event'});
// it checks the choice again at Try (RecipeGraph.chosen_places_problem). The only rules kept here: one chosen place for each independent graph, and "all original tables of this
// group" (the first places of the group). A choice that is a set of first places is accepted by the server's rule too (no place lies below another).
// The marks of the places that hold an audit step come from the server (custom message 'lineage_marks': {place: number of steps}).
//
// CHOOSING ONLY STAGES (slice 3a, D-0655): a choice changes nothing in the preview or the plots. The chosen places are listed under the bar ("Chosen places") with a button "Show" on each
// line and one button "Show selection" (the place clicked first: the browser keeps the order of the clicks). A button sends Shiny.setInputValue('lineage_show', {place, t}, {priority:'event'})
// (place null for "Show selection"); the server makes it the shown item and tells the browser which place is shown (custom message 'lineage_shown': {place}). The shown place is marked in the
// list and on the map with the word "shown", so that it differs from the chosen places by more than colour. The list of the chosen places is built again only when the choice or the shown place
// changes (never at a hover), so that a click on a button is never lost to a redraw. PROVISIONAL words.
//
// THE SIZES (PROVISIONAL, the owner's remark of 2026-11-26): a drag handle between the list and the map (left and right arrows move it), one under the list and the map (up and down arrows:
// their height) and one under the text area (its height); a double click on a handle gives its default back. The choice is kept in the browser's local storage (key
// spv.lineage_layout.v1; every access inside try/catch; a missing or broken value gives the default silently), like the width of the side panels. Nothing is sent to the server.
// THE MAP: drag the background to move, the buttons (and + and - and 0 on the keyboard, the arrows to move) to zoom and reset; the wheel zooms only with Ctrl held (it never steals the
// scroll of the page). The list stays the accessible twin: everything the map does can be done in the list.
// PROVISIONAL words and colours (D-0634: the exact colours and words are not decided).
(function () {
  if (window.__spvLineage) return;
  window.__spvLineage = true;
  var NS = "http://www.w3.org/2000/svg";
  var HINT = "Hover, focus or choose a place to read what it is and what is built from it. Choose one place for each independent graph, or all its original tables.";
  var STORE = "spv.lineage_layout.v1";
  var DEFAULTS = { split: 0.45, bodyH: 360 };                 // the text area has no default height of its own (it grows with its words up to a limit)
  var LIMITS = { split: [0.2, 0.8], bodyH: [140, 900], textH: [60, 600] };
  var ZOOM = [0.5, 4];
  var lastMarks = {};
  var lastShown = null;
  var panels = [];

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function svg(tag, attrs) {
    var e = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    return e;
  }
  function send(name, value) {
    if (window.Shiny && Shiny.setInputValue) Shiny.setInputValue(name, value, { priority: "event" });
  }
  function clamp(v, lim) { return Math.max(lim[0], Math.min(lim[1], v)); }

  // ---- the kept sizes: only a finite number inside its limits is used, anything else is ignored
  function readPrefs() {
    var out = {};
    try {
      var raw = JSON.parse(window.localStorage.getItem(STORE) || "{}");
      Object.keys(LIMITS).forEach(function (k) {
        var v = raw && raw[k];
        if (typeof v === "number" && isFinite(v) && v >= LIMITS[k][0] && v <= LIMITS[k][1]) out[k] = v;
      });
    } catch (e) { /* a private window or a broken value: the defaults stay */ }
    return out;
  }
  function writePrefs(prefs) {
    try {
      if (Object.keys(prefs).length) window.localStorage.setItem(STORE, JSON.stringify(prefs));
      else window.localStorage.removeItem(STORE);
    } catch (e) { /* not kept: the sizes still work for this page */ }
  }

  // ---- a drag handle: axis "x" (a vertical bar, left and right) or "y" (a horizontal bar, up and down). get() is the value now, set(v) applies it, reset() gives the default back
  function makeHandle(cls, axis, label, hooks) {
    var h = el("div", "spv-lin-handle " + cls);
    h.setAttribute("role", "separator");
    h.setAttribute("aria-orientation", axis === "x" ? "vertical" : "horizontal");
    h.setAttribute("aria-label", label);
    h.title = label + ". Drag, or use the arrow keys. Double-click to reset.";
    h.tabIndex = 0;
    var start = null;
    function shown() { h.setAttribute("aria-valuenow", String(Math.round(hooks.get() * (axis === "x" ? 100 : 1)))); }
    h.addEventListener("pointerdown", function (ev) {
      if (ev.button !== 0) return;
      ev.preventDefault();
      h.setPointerCapture(ev.pointerId);
      start = { p: axis === "x" ? ev.clientX : ev.clientY, v: hooks.get() };
    });
    h.addEventListener("pointermove", function (ev) {
      if (!start) return;
      var d = (axis === "x" ? ev.clientX : ev.clientY) - start.p;
      hooks.set(hooks.fromPixels(start.v, d));
      shown();
    });
    function stop() { if (start) { start = null; hooks.save(); } }
    h.addEventListener("pointerup", stop);
    h.addEventListener("pointercancel", stop);
    h.addEventListener("keydown", function (ev) {
      var back = axis === "x" ? "ArrowLeft" : "ArrowUp", fwd = axis === "x" ? "ArrowRight" : "ArrowDown";
      if (ev.key !== back && ev.key !== fwd) return;
      ev.preventDefault();
      hooks.set(hooks.fromPixels(hooks.get(), ev.key === fwd ? 24 : -24));
      shown(); hooks.save();
    });
    h.addEventListener("dblclick", function () { hooks.reset(); shown(); hooks.save(); });
    shown();
    h.refresh = shown;
    return h;
  }

  function build(root) {
    var script = root.querySelector("script[type='application/json']");
    if (!script || root.getAttribute("data-built") === "1") return;
    var data;
    try { data = JSON.parse(script.textContent); } catch (e) { root.appendChild(el("div", "spv-lin-error", "The lineage cannot be read (the data of the panel is not valid).")); return; }
    root.setAttribute("data-built", "1");
    var byId = {};
    data.nodes.forEach(function (n) { byId[n.id] = n; });
    var st = { chosen: {}, order: [], mode: "whole", hot: null, last: null, layoutKey: null, reveal: null, stagedKey: null };
    var view = { k: 1, tx: 0, ty: 0 };
    var prefs = readPrefs();
    var refs = {};

    var bar = el("div", "spv-lin-bar");
    var whole = el("button", "spv-lin-switch active", "Whole recipe");
    var around = el("button", "spv-lin-switch", "Around my selection");
    [whole, around].forEach(function (b) { b.type = "button"; b.setAttribute("role", "radio"); });
    bar.appendChild(el("span", "spv-lin-switch-label", "Show:"));
    bar.appendChild(whole); bar.appendChild(around);
    var chosenInfo = el("span", "spv-lin-chosen none", "No place chosen.");
    chosenInfo.setAttribute("aria-live", "polite");
    bar.appendChild(chosenInfo);
    root.appendChild(bar);

    // the chosen places, to be shown one by one (choosing only stages them)
    var staged = el("div", "spv-lin-staged");
    staged.setAttribute("aria-label", "Chosen places");
    staged.appendChild(el("span", "spv-lin-staged-title", "Chosen places"));
    var stagedList = el("div", "spv-lin-staged-list");
    var showSel = el("button", "btn btn-primary spv-lin-showsel", "Show selection");
    showSel.type = "button"; showSel.disabled = true;
    showSel.title = "Show the first place you chose in the data preview. Choosing a place does not change what is shown.";
    showSel.addEventListener("click", function () { send("lineage_show", { place: null, t: Date.now() }); });
    staged.appendChild(stagedList);
    staged.appendChild(showSel);
    root.appendChild(staged);

    var body = el("div", "spv-lin-body");
    var list = el("div", "spv-lin-list");
    list.setAttribute("role", "list");
    list.setAttribute("aria-label", "The tables and plots of the recipe, in the order of the lineage");
    var mapCol = el("div", "spv-lin-mapcol");
    var tools = el("div", "spv-lin-tools");
    var zoomOut = el("button", "spv-lin-zoom", "-"), zoomIn = el("button", "spv-lin-zoom", "+"), zoomReset = el("button", "spv-lin-zoom wide", "Reset view");
    [[zoomOut, "Zoom out (the key -)"], [zoomIn, "Zoom in (the key +)"], [zoomReset, "Back to the first view (the key 0)"]].forEach(function (b) {
      b[0].type = "button"; b[0].title = b[1]; b[0].setAttribute("aria-label", b[1]); tools.appendChild(b[0]);
    });
    tools.appendChild(el("span", "spv-lin-note", "Drag the map to move it. Ctrl and the wheel zoom."));
    var mapWrap = el("div", "spv-lin-map");
    mapWrap.tabIndex = 0;
    mapWrap.setAttribute("role", "group");
    mapWrap.setAttribute("aria-label", "Map of the lineage. The arrow keys move the map, + and - zoom, 0 resets. The list beside it holds the same places.");
    mapCol.appendChild(tools); mapCol.appendChild(mapWrap);
    var handleV = makeHandle("v", "x", "Width of the list against the map", {
      get: function () { return prefs.split !== undefined ? prefs.split : DEFAULTS.split; },
      fromPixels: function (v, d) { return clamp(v + d / Math.max(body.clientWidth, 1), LIMITS.split); },
      set: function (v) { prefs.split = clamp(v, LIMITS.split); sizeParts(); },
      reset: function () { delete prefs.split; sizeParts(); },
      save: function () { writePrefs(prefs); }
    });
    body.appendChild(list); body.appendChild(handleV); body.appendChild(mapCol);
    root.appendChild(body);
    var handleH = makeHandle("h", "y", "Height of the list and the map", {
      get: function () { return prefs.bodyH !== undefined ? prefs.bodyH : DEFAULTS.bodyH; },
      fromPixels: function (v, d) { return clamp(v + d, LIMITS.bodyH); },
      set: function (v) { prefs.bodyH = clamp(v, LIMITS.bodyH); sizeParts(); },
      reset: function () { delete prefs.bodyH; sizeParts(); },
      save: function () { writePrefs(prefs); }
    });
    root.appendChild(handleH);
    var text = el("div", "spv-lin-text");
    text.setAttribute("aria-live", "polite");
    root.appendChild(text);
    var handleT = makeHandle("h", "y", "Height of the text area", {
      get: function () { return prefs.textH !== undefined ? prefs.textH : text.offsetHeight; },
      fromPixels: function (v, d) { return clamp(v + d, LIMITS.textH); },
      set: function (v) { prefs.textH = clamp(v, LIMITS.textH); sizeParts(); },
      reset: function () { delete prefs.textH; sizeParts(); },
      save: function () { writePrefs(prefs); }
    });
    root.appendChild(handleT);

    function sizeParts() {
      var split = prefs.split !== undefined ? prefs.split : DEFAULTS.split;
      list.style.flex = "0 0 " + (split * 100).toFixed(2) + "%";
      body.style.height = (prefs.bodyH !== undefined ? prefs.bodyH : DEFAULTS.bodyH) + "px";
      text.style.height = prefs.textH !== undefined ? prefs.textH + "px" : "";
      text.style.maxHeight = prefs.textH !== undefined ? "none" : "";
      [handleV, handleH, handleT].forEach(function (h) { if (h.refresh) h.refresh(); });
    }
    sizeParts();

    // ---- the list, grouped by independent graph
    var heads = [];
    data.groups.forEach(function (g) {
      var head = el("div", "spv-lin-group");
      heads.push({ el: head, nodes: g.nodes });
      head.appendChild(el("span", "spv-lin-gnum", String(g.id + 1)));
      head.appendChild(el("span", "spv-lin-group-title", "Independent graph " + (g.id + 1) + " (" + g.nodes.length + (g.nodes.length === 1 ? " node)" : " nodes)")));
      var all = el("button", "spv-lin-all", "All original tables of this group");
      all.type = "button";
      all.disabled = !g.first_places.length;
      all.addEventListener("click", function () { choose(g.id, g.first_places.slice()); });
      var clear = el("button", "spv-lin-clear", "Clear");
      clear.type = "button";
      clear.addEventListener("click", function () { choose(g.id, []); });
      head.appendChild(all); head.appendChild(clear);
      list.appendChild(head);
      g.nodes.forEach(function (id) {
        var n = byId[id];
        var line = el("div", "spv-lin-line " + n.cls + (n.choosable ? "" : " not-choosable"));
        line.setAttribute("role", "listitem");
        line.tabIndex = 0;
        line.setAttribute("data-id", id);
        var chip = el("span", "spv-lin-gnum", String(n.gnum));
        chip.title = "Independent graph " + n.gnum;
        line.appendChild(chip);
        line.appendChild(el("span", "spv-lin-swatch " + n.cls));
        line.appendChild(el("span", "spv-lin-line-text", n.line));
        if (n.no_plot) { var tag = el("span", "spv-lin-tag", "no plot"); tag.title = "No plot reads this table."; line.appendChild(tag); }
        var shownTag = el("span", "spv-lin-shown");
        line.appendChild(shownTag);
        var mark = el("span", "spv-lin-mark");
        line.appendChild(mark);
        wire(line, id);
        list.appendChild(line);
        refs[id] = refs[id] || {};
        refs[id].line = line; refs[id].mark = mark; refs[id].shownTag = shownTag;
      });
    });

    // ---- the map: the headings stay at the top and follow the columns; the dots and arrows move and zoom together
    var map = svg("svg", { "class": "spv-lin-svg", role: "group", "aria-label": "Map of the lineage: one dot for each table or plot, arrows from a table to what is built from it" });
    var defs = svg("defs");
    var marker = svg("marker", { id: "spv-lin-arrow", viewBox: "0 0 6 6", refX: "6", refY: "3", markerWidth: "5", markerHeight: "5", orient: "auto" });
    marker.appendChild(svg("path", { d: "M0,0 L6,3 L0,6 z", "class": "spv-lin-arrowhead" }));
    defs.appendChild(marker); map.appendChild(defs);
    var headLayer = svg("g", { "class": "spv-lin-heads" });
    var vp = svg("g", { "class": "spv-lin-vp" });
    var edgeLayer = svg("g"), dotLayer = svg("g"), numLayer = svg("g");
    vp.appendChild(edgeLayer); vp.appendChild(dotLayer); vp.appendChild(numLayer);
    map.appendChild(vp); map.appendChild(headLayer);
    mapWrap.appendChild(map);
    var edgeEls = data.edges.map(function (e) {
      var l = svg("line", { "class": "spv-lin-edge", "marker-end": "url(#spv-lin-arrow)" });
      edgeLayer.appendChild(l);
      return { from: e[0], to: e[1], el: l };
    });
    data.nodes.forEach(function (n) {
      var d;
      if (n.kind === "T3") d = svg("rect", { width: 11, height: 11, rx: 2, "class": "spv-lin-dot " + n.cls });
      else d = svg("circle", { r: n.kind === "result" ? 6 : 5, "class": "spv-lin-dot " + n.cls });
      d.setAttribute("data-id", n.id);
      d.setAttribute("tabindex", "0");
      d.setAttribute("role", "button");
      d.appendChild(svg("title")).textContent = n.line + " (graph " + n.gnum + ")";
      dotLayer.appendChild(d);
      var m = svg("text", { "class": "spv-lin-dotmark", "aria-hidden": "true" });
      m.textContent = "";
      dotLayer.appendChild(m);
      var sm = svg("text", { "class": "spv-lin-shownmark", "aria-hidden": "true" });
      sm.textContent = "";
      dotLayer.appendChild(sm);
      wire(d, n.id);
      refs[n.id] = refs[n.id] || {};
      refs[n.id].dot = d; refs[n.id].dotmark = m; refs[n.id].shownmark = sm;
    });
    var numEls = {};                    // one small number for each independent graph: the same N as the list heading
    data.groups.forEach(function (g) {
      var t = svg("text", { "class": "spv-lin-gnum-svg", "aria-hidden": "true", "text-anchor": "end" });
      t.textContent = String(g.id + 1);
      numLayer.appendChild(t);
      numEls[g.id + 1] = t;
    });
    var headEls = [];                   // the headings of the columns of the layout now shown, rebuilt when the layout changes

    function wire(e, id) {
      e.addEventListener("mouseenter", function () { st.hot = id; paint(); });
      e.addEventListener("mouseleave", function () { if (st.hot === id) { st.hot = null; paint(); } });
      e.addEventListener("focus", function () { st.hot = id; paint(); });
      e.addEventListener("blur", function () { if (st.hot === id) { st.hot = null; paint(); } });
      e.addEventListener("click", function () { activate(id); });
      e.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); activate(id); }
      });
    }

    function activate(id) {
      var n = byId[id];
      st.last = id;
      if (!n.choosable) { st.hot = id; paint(); return; }
      var cur = st.chosen[n.group] || [];
      choose(n.group, (cur.length === 1 && cur[0] === id) ? [] : [id]);
    }

    // the places chosen in the order the user chose them (an object's keys would sort the graph numbers): the first one is what "Show selection" shows
    function flat() {
      var out = [];
      st.order.forEach(function (g) { (st.chosen[g] || []).forEach(function (id) { out.push(id); }); });
      return out;
    }

    function choose(group, ids) {
      st.order = st.order.filter(function (g) { return String(g) !== String(group); });
      if (ids.length) { st.chosen[group] = ids; st.order.push(group); } else delete st.chosen[group];
      if (ids.length) { st.last = ids[0]; st.reveal = ids[0]; }
      root.setAttribute("data-chosen", JSON.stringify(flat()));
      send("lineage_chosen", flat());
      paint();
    }

    // the dots shown: the whole recipe, or around the chosen place (one place: its own compact layout; several: the union at the places of the whole map)
    function shown() {
      var chosen = flat();
      if (st.mode === "around" && chosen.length) {
        if (chosen.length === 1) {
          var ids = byId[chosen[0]].around;
          return { key: chosen[0], ids: ids, pos: data.layouts[chosen[0]], size: data.sizes[chosen[0]], union: false };
        }
        var keep = {};
        chosen.forEach(function (c) { byId[c].around.forEach(function (i) { keep[i] = true; }); });
        return { key: "", ids: data.nodes.map(function (n) { return n.id; }).filter(function (i) { return keep[i]; }), pos: data.layouts[""], size: data.sizes[""], union: true };
      }
      return { key: "", ids: data.nodes.map(function (n) { return n.id; }), pos: data.layouts[""], size: data.sizes[""], union: false };
    }

    // ---- pan and zoom: a transform of the group of dots; the strokes keep their width (CSS vector-effect)
    function applyView() {
      vp.setAttribute("transform", "translate(" + view.tx.toFixed(1) + " " + view.ty.toFixed(1) + ") scale(" + view.k.toFixed(3) + ")");
      headEls.forEach(function (h) {
        var x = h.x * view.k + view.tx;
        h.el.setAttribute("x", (x - 9).toFixed(1));
        h.el.style.display = h.visible && x > -40 && x < mapWrap.clientWidth ? "" : "none";
        h.tn.nodeValue = h.dx * view.k < 76 ? h.short : h.text;       // the text node only: the <title> child (the hover text) stays
      });
    }
    function resetView() { view.k = 1; view.tx = 0; view.ty = 0; applyView(); }
    function zoomAt(factor, cx, cy) {
      var k = clamp(view.k * factor, ZOOM);
      var f = k / view.k;
      view.tx = cx - (cx - view.tx) * f; view.ty = cy - (cy - view.ty) * f; view.k = k;
      applyView();
    }
    function centre() { return [mapWrap.clientWidth / 2, mapWrap.clientHeight / 2]; }
    zoomIn.addEventListener("click", function () { var c = centre(); zoomAt(1.25, c[0], c[1]); });
    zoomOut.addEventListener("click", function () { var c = centre(); zoomAt(0.8, c[0], c[1]); });
    zoomReset.addEventListener("click", resetView);
    var pan = null;
    mapWrap.addEventListener("pointerdown", function (ev) {
      if (ev.button !== 0 || (ev.target.closest && ev.target.closest(".spv-lin-dot"))) return;
      mapWrap.setPointerCapture(ev.pointerId);
      pan = { x: ev.clientX, y: ev.clientY, tx: view.tx, ty: view.ty };
      mapWrap.classList.add("panning");
    });
    mapWrap.addEventListener("pointermove", function (ev) {
      if (!pan) return;
      view.tx = pan.tx + ev.clientX - pan.x; view.ty = pan.ty + ev.clientY - pan.y;
      applyView();
    });
    function endPan() { pan = null; mapWrap.classList.remove("panning"); }
    mapWrap.addEventListener("pointerup", endPan);
    mapWrap.addEventListener("pointercancel", endPan);
    mapWrap.addEventListener("wheel", function (ev) {
      if (!ev.ctrlKey) return;                       // without Ctrl the wheel scrolls the page, as everywhere
      ev.preventDefault();
      var r = mapWrap.getBoundingClientRect();
      zoomAt(ev.deltaY < 0 ? 1.15 : 1 / 1.15, ev.clientX - r.left, ev.clientY - r.top);
    }, { passive: false });
    mapWrap.addEventListener("keydown", function (ev) {
      if (ev.target !== mapWrap) return;             // a dot keeps its own keys
      var c = centre(), step = 40, handled = true;
      if (ev.key === "ArrowLeft") view.tx += step;
      else if (ev.key === "ArrowRight") view.tx -= step;
      else if (ev.key === "ArrowUp") view.ty += step;
      else if (ev.key === "ArrowDown") view.ty -= step;
      else if (ev.key === "+" || ev.key === "=") zoomAt(1.25, c[0], c[1]);
      else if (ev.key === "-") zoomAt(0.8, c[0], c[1]);
      else if (ev.key === "0") resetView();
      else handled = false;
      if (handled) { ev.preventDefault(); applyView(); }
    });

    // the chosen place is brought into view in the other part too: a line chosen in the list is panned into the map, a dot chosen in the map is scrolled into the list
    function revealInMap(id, pos) {
      var p = pos[id];
      if (!p) return;
      var x = p[0] * view.k + view.tx, y = p[1] * view.k + view.ty, w = mapWrap.clientWidth, h = mapWrap.clientHeight, m = 28;
      if (x < m || x > w - m) view.tx += w / 2 - x;
      if (y < m + 20 || y > h - m) view.ty += h / 2 - y;
      applyView();
    }
    function revealInList(id) {
      var line = refs[id] && refs[id].line;
      if (!line || line.style.display === "none") return;
      var top = line.offsetTop, bottom = top + line.offsetHeight;
      if (top < list.scrollTop) list.scrollTop = Math.max(top - 28, 0);
      else if (bottom > list.scrollTop + list.clientHeight) list.scrollTop = bottom - list.clientHeight + 8;
    }

    function drawHeadings(s) {
      headLayer.textContent = "";
      headEls = [];
      var heads = data.heads[s.key] || [];
      heads.forEach(function (h, i) {
        var t = svg("text", { "class": "spv-lin-head", y: 13, "aria-hidden": "true" });
        var tn = document.createTextNode(h.text);
        t.appendChild(tn);
        if (!s.union) t.appendChild(svg("title")).textContent = h.title;
        headLayer.appendChild(t);
        var next = heads[i + 1];
        headEls.push({ el: t, tn: tn, x: h.x, text: h.text, short: h.short, dx: next ? next.x - h.x : 78, visible: true });
      });
    }

    // the list of the chosen places: built again only when the choice or the shown place changes
    function paintStaged(chosen) {
      var key = chosen.join("|") + "#" + lastShown;
      showSel.disabled = !chosen.length;
      if (st.stagedKey === key) return;
      st.stagedKey = key;
      stagedList.textContent = "";
      if (!chosen.length) {
        stagedList.appendChild(el("span", "spv-lin-note", "No place chosen. Choosing a place only stages it: press Show to see its table."));
        return;
      }
      chosen.forEach(function (id) {
        var row = el("div", "spv-lin-staged-line");
        row.appendChild(el("span", "spv-lin-staged-name", byId[id].line));
        if (lastShown === id) row.appendChild(el("span", "spv-lin-shown", "shown"));
        var b = el("button", "spv-lin-show", "Show");
        b.type = "button";
        b.setAttribute("data-place", id);
        b.title = "Show " + byId[id].shown + " in the data preview";
        b.setAttribute("aria-label", "Show " + byId[id].line);
        b.addEventListener("click", function () { send("lineage_show", { place: id, t: Date.now() }); });
        row.appendChild(b);
        stagedList.appendChild(row);
      });
    }

    function paint() {
      var s = shown();
      var layoutKey = s.key + "|" + (s.union ? s.ids.join(",") : "");
      if (st.layoutKey !== layoutKey) {
        st.layoutKey = layoutKey;
        drawHeadings(s);
        resetView();
      }
      var visible = {};
      s.ids.forEach(function (i) { visible[i] = true; });
      var chosen = flat();
      var chosenSet = {}, built = {};
      chosen.forEach(function (c) { chosenSet[c] = true; byId[c].built_from.forEach(function (b) { built[b] = true; }); });
      var hot = st.hot;
      var hotBuilt = {};
      if (hot && byId[hot].choosable) byId[hot].built_from.forEach(function (b) { hotBuilt[b] = true; });
      data.nodes.forEach(function (n) {
        var r = refs[n.id], on = !!visible[n.id];
        var cls = (chosenSet[n.id] ? " chosen" : "") + (built[n.id] ? " built" : "") + (hot === n.id ? " hot" : "") + (hotBuilt[n.id] && !built[n.id] ? " built-hint" : "") + (lastMarks[n.id] ? " marked" : "");
        r.line.style.display = on ? "" : "none";
        r.line.className = "spv-lin-line " + n.cls + (n.choosable ? "" : " not-choosable") + cls + (lastShown === n.id ? " shown" : "");
        r.shownTag.textContent = lastShown === n.id ? "shown" : "";
        r.line.setAttribute("aria-selected", chosenSet[n.id] ? "true" : "false");
        r.dot.style.display = on ? "" : "none";
        r.dotmark.style.display = on && lastMarks[n.id] ? "" : "none";
        r.dot.setAttribute("class", "spv-lin-dot " + n.cls + cls);
        r.dot.setAttribute("aria-pressed", chosenSet[n.id] ? "true" : "false");
        r.shownmark.style.display = on && lastShown === n.id ? "" : "none";
        r.dot.setAttribute("aria-label", n.line + (n.choosable ? "" : " (cannot be chosen)") + (lastShown === n.id ? ", shown" : "") + (chosenSet[n.id] ? ", chosen" : "") + (built[n.id] ? ", built from the chosen place" : "") + (lastMarks[n.id] ? ", holds audit step(s)" : "") + ", graph " + n.gnum);
        if (on) {
          var p = s.pos[n.id];
          if (n.kind === "T3") { r.dot.setAttribute("x", p[0] - 5.5); r.dot.setAttribute("y", p[1] - 5.5); }
          else { r.dot.setAttribute("cx", p[0]); r.dot.setAttribute("cy", p[1]); }
          r.dotmark.setAttribute("x", p[0] + 7); r.dotmark.setAttribute("y", p[1] - 5);
          r.dotmark.textContent = lastMarks[n.id] ? "*" : "";
          r.shownmark.setAttribute("x", p[0] + 7); r.shownmark.setAttribute("y", p[1] + 12);
          r.shownmark.textContent = lastShown === n.id ? "shown" : "";
        }
        var mk = lastMarks[n.id];
        r.mark.textContent = mk ? ("audit step" + (mk > 1 ? "s: " + mk : "")) : "";
      });
      heads.forEach(function (h) {
        h.el.style.display = h.nodes.some(function (i) { return visible[i]; }) ? "" : "none";
      });
      edgeEls.forEach(function (e) {
        var on = visible[e.from] && visible[e.to];
        e.el.style.display = on ? "" : "none";
        if (on) {
          var a = s.pos[e.from], b = s.pos[e.to];
          e.el.setAttribute("x1", a[0] + 6); e.el.setAttribute("y1", a[1]); e.el.setAttribute("x2", b[0] - 7); e.el.setAttribute("y2", b[1]);
        }
        e.el.setAttribute("class", "spv-lin-edge" + ((chosenSet[e.from] || built[e.from]) && built[e.to] ? " built" : ""));
      });
      // the number of each independent graph, at its first dot among the dots shown (the rule of graph_labels in lineage_view.py: the lowest x, then the lowest y)
      var firsts = {};
      s.ids.forEach(function (i) {
        var p = s.pos[i], g = byId[i].gnum;
        if (!firsts[g] || p[0] < firsts[g][0] || (p[0] === firsts[g][0] && p[1] < firsts[g][1])) firsts[g] = p;
      });
      Object.keys(numEls).forEach(function (g) {
        var t = numEls[g], p = firsts[g];
        t.style.display = p ? "" : "none";
        if (p) { t.setAttribute("x", p[0] - 10); t.setAttribute("y", p[1] + 4); }
      });
      // a column heading is drawn only over a column that has a dot shown
      var cols = {};
      s.ids.forEach(function (i) { cols[s.pos[i][0]] = true; });
      headEls.forEach(function (h) { h.visible = !!cols[h.x]; });
      applyView();
      if (st.reveal && visible[st.reveal]) { revealInMap(st.reveal, s.pos); revealInList(st.reveal); }
      st.reveal = null;
      // the text area: the hovered or focused node, else the last chosen place
      var shownId = hot || (chosen.length ? (chosenSet[st.last] ? st.last : chosen[0]) : null);
      text.textContent = "";
      if (shownId) {
        byId[shownId].detail.forEach(function (ln, i) { text.appendChild(el("div", i === 0 ? "spv-lin-text-head" : "spv-lin-text-line", ln)); });
        if (lastMarks[shownId]) text.appendChild(el("div", "spv-lin-text-line", "This place holds " + lastMarks[shownId] + " audit step(s): see the Pipeline Audit panel on the right (reason, remove)."));
      } else {
        text.appendChild(el("div", "spv-lin-text-line", HINT));
      }
      chosenInfo.textContent = chosen.length ? ("Chosen: " + chosen.map(function (c) { return byId[c].shown; }).join(", ") + ".") : "No place chosen.";
      chosenInfo.className = "spv-lin-chosen" + (chosen.length ? "" : " none");
      paintStaged(chosen);
      whole.className = "spv-lin-switch" + (st.mode === "whole" ? " active" : "");
      around.className = "spv-lin-switch" + (st.mode === "around" ? " active" : "");
      whole.setAttribute("aria-checked", st.mode === "whole" ? "true" : "false");
      around.setAttribute("aria-checked", st.mode === "around" ? "true" : "false");
    }

    whole.addEventListener("click", function () { st.mode = "whole"; paint(); });
    around.addEventListener("click", function () {
      st.mode = "around";
      if (!flat().length) text.textContent = "Choose a place first: this view shows what that place is built from and what is built from it.";
      paint();
    });

    panels.push({ paint: paint });
    paint();
    send("lineage_chosen", []);
    send("lineage_ready", Date.now());
  }

  function scan(root) {
    if (!root || root.nodeType !== 1) return;
    if (root.matches && root.matches(".spv-lineage")) build(root);
    else if (root.querySelectorAll) root.querySelectorAll(".spv-lineage").forEach(build);
  }

  function register() {
    if (window.Shiny && Shiny.addCustomMessageHandler) {
      Shiny.addCustomMessageHandler("lineage_marks", function (marks) {
        lastMarks = marks || {};
        panels.forEach(function (p) { try { p.paint(); } catch (e) { /* the panel left the page */ } });
      });
      Shiny.addCustomMessageHandler("lineage_shown", function (msg) {
        lastShown = (msg && msg.place) || null;
        panels.forEach(function (p) { try { p.paint(); } catch (e) { /* the panel left the page */ } });
      });
    } else {
      document.addEventListener("shiny:connected", register, { once: true });
    }
  }
  register();
  new MutationObserver(function (mutations) {
    mutations.forEach(function (m) { m.addedNodes.forEach(scan); });
  }).observe(document.documentElement, { childList: true, subtree: true });
  scan(document.documentElement);
})();
