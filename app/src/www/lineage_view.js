// lineage_view.js - the lineage panel of HOME (Audit mode): a list (the reader and the text twin of every dot) and a map of dots, to choose the place of an audit step (D-0629, D-0634)
//
// Vanilla JS, no external dependencies, ADR-071 compliant (no CDN). First-party script, not a vendored asset.
//
// The server draws the container once per recipe (app/handlers/lineage_handlers.py) with the data of app/modules/lineage_view.py in a <script type="application/json"> tag;
// this script builds the list and the map from it and handles hover, focus, keyboard and choice in the browser, so that a click never makes the server draw the panel again
// (ui_implementation_contract.md section 14, R4). The server is told the choice with Shiny.setInputValue('lineage_chosen', [...ids], {priority:'event'}); it checks the choice again
// at confirm (RecipeGraph.chosen_places_problem). The only rules kept here: one chosen place for each independent graph, and "all original tables of this group" (the first places
// of the group). A choice that is a set of first places is accepted by the server's rule too (no place lies below another).
// The marks of the places that hold an audit step come from the server (custom message 'lineage_marks': {place: number of steps}).
// PROVISIONAL words and colours (D-0634: the exact colours and words are not decided).
(function () {
  if (window.__spvLineage) return;
  window.__spvLineage = true;
  var NS = "http://www.w3.org/2000/svg";
  var HINT = "Hover, focus or choose a place to read what it is and what is built from it. Choose one place for each independent graph, or all its original tables.";
  var lastMarks = {};
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

  function build(root) {
    var script = root.querySelector("script[type='application/json']");
    if (!script || root.getAttribute("data-built") === "1") return;
    var data;
    try { data = JSON.parse(script.textContent); } catch (e) { root.appendChild(el("div", "spv-lin-error", "The lineage cannot be read (the data of the panel is not valid).")); return; }
    root.setAttribute("data-built", "1");
    var byId = {};
    data.nodes.forEach(function (n) { byId[n.id] = n; });
    var st = { chosen: {}, mode: "whole", hot: null, last: null };
    var refs = {};

    var bar = el("div", "spv-lin-bar");
    var whole = el("button", "spv-lin-switch active", "Whole recipe");
    var around = el("button", "spv-lin-switch", "Around my selection");
    [whole, around].forEach(function (b) { b.type = "button"; b.setAttribute("role", "radio"); });
    bar.appendChild(el("span", "spv-lin-switch-label", "Show:"));
    bar.appendChild(whole); bar.appendChild(around);
    var chosenInfo = el("span", "spv-lin-chosen", "No place chosen.");
    bar.appendChild(chosenInfo);
    root.appendChild(bar);

    var body = el("div", "spv-lin-body");
    var list = el("div", "spv-lin-list");
    list.setAttribute("role", "list");
    list.setAttribute("aria-label", "The tables and plots of the recipe, in the order of the lineage");
    var mapWrap = el("div", "spv-lin-map");
    body.appendChild(list); body.appendChild(mapWrap);
    root.appendChild(body);
    var text = el("div", "spv-lin-text");
    text.setAttribute("aria-live", "polite");
    root.appendChild(text);
    var actions = el("div", "spv-lin-actions");
    var create = el("button", "btn btn-primary spv-lin-create", "Create an audit step here...");
    create.type = "button"; create.disabled = true;
    var createNote = el("span", "spv-lin-note", "Choose a place first.");
    actions.appendChild(create); actions.appendChild(createNote);
    root.appendChild(actions);

    // ---- the list, grouped by independent graph
    data.groups.forEach(function (g) {
      var head = el("div", "spv-lin-group");
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
        line.appendChild(el("span", "spv-lin-swatch " + n.cls));
        line.appendChild(el("span", "spv-lin-line-text", n.line));
        if (n.no_plot) line.appendChild(el("span", "spv-lin-tag", "no plot"));
        var mark = el("span", "spv-lin-mark");
        line.appendChild(mark);
        wire(line, id);
        list.appendChild(line);
        refs[id] = refs[id] || {};
        refs[id].line = line; refs[id].mark = mark;
      });
    });

    // ---- the map
    var map = svg("svg", { "class": "spv-lin-svg", role: "group", "aria-label": "Map of the lineage: one dot for each table or plot, arrows from a table to what is built from it" });
    var defs = svg("defs");
    var marker = svg("marker", { id: "spv-lin-arrow", viewBox: "0 0 6 6", refX: "6", refY: "3", markerWidth: "5", markerHeight: "5", orient: "auto" });
    marker.appendChild(svg("path", { d: "M0,0 L6,3 L0,6 z", "class": "spv-lin-arrowhead" }));
    defs.appendChild(marker); map.appendChild(defs);
    var edgeLayer = svg("g"), dotLayer = svg("g");
    map.appendChild(edgeLayer); map.appendChild(dotLayer);
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
      d.appendChild(svg("title")).textContent = n.name + " - " + n.tier_word;
      dotLayer.appendChild(d);
      var m = svg("text", { "class": "spv-lin-dotmark", "aria-hidden": "true" });
      m.textContent = "";
      dotLayer.appendChild(m);
      wire(d, n.id);
      refs[n.id] = refs[n.id] || {};
      refs[n.id].dot = d; refs[n.id].dotmark = m;
    });

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

    function flat() {
      var out = [];
      Object.keys(st.chosen).forEach(function (g) { st.chosen[g].forEach(function (id) { out.push(id); }); });
      return out;
    }

    function choose(group, ids) {
      if (ids.length) st.chosen[group] = ids; else delete st.chosen[group];
      if (ids.length) st.last = ids[0];
      root.setAttribute("data-chosen", JSON.stringify(flat()));
      send("lineage_chosen", flat());
      paint();
    }

    // the dots shown: the whole recipe, or around the chosen place (one place: its own compact layout; several: the union at the places of the whole map)
    function shown() {
      var chosen = flat();
      if (st.mode === "around" && chosen.length) {
        if (chosen.length === 1) {
          var ids = byId[chosen[0]].around, pos = data.layouts[chosen[0]], size = data.sizes[chosen[0]];
          return { ids: ids, pos: pos, size: size };
        }
        var keep = {};
        chosen.forEach(function (c) { byId[c].around.forEach(function (i) { keep[i] = true; }); });
        return { ids: data.nodes.map(function (n) { return n.id; }).filter(function (i) { return keep[i]; }), pos: data.layouts[""], size: data.sizes[""] };
      }
      return { ids: data.nodes.map(function (n) { return n.id; }), pos: data.layouts[""], size: data.sizes[""] };
    }

    function paint() {
      var s = shown();
      var visible = {};
      s.ids.forEach(function (i) { visible[i] = true; });
      var chosen = flat();
      var chosenSet = {}, built = {};
      chosen.forEach(function (c) { chosenSet[c] = true; byId[c].built_from.forEach(function (b) { built[b] = true; }); });
      var hot = st.hot;
      var hotBuilt = {};
      if (hot && byId[hot].choosable) byId[hot].built_from.forEach(function (b) { hotBuilt[b] = true; });
      map.setAttribute("viewBox", "0 0 " + Math.max(s.size[0], 60) + " " + Math.max(s.size[1], 40));
      map.setAttribute("width", Math.max(s.size[0], 60));
      map.setAttribute("height", Math.max(s.size[1], 40));
      data.nodes.forEach(function (n) {
        var r = refs[n.id], on = !!visible[n.id];
        var cls = (chosenSet[n.id] ? " chosen" : "") + (built[n.id] ? " built" : "") + (hot === n.id ? " hot" : "") + (hotBuilt[n.id] && !built[n.id] ? " built-hint" : "") + (lastMarks[n.id] ? " marked" : "");
        r.line.style.display = on ? "" : "none";
        r.line.className = "spv-lin-line " + n.cls + (n.choosable ? "" : " not-choosable") + cls;
        r.line.setAttribute("aria-selected", chosenSet[n.id] ? "true" : "false");
        r.dot.style.display = on ? "" : "none";
        r.dotmark.style.display = on && lastMarks[n.id] ? "" : "none";
        var base = (n.kind === "T3" ? "spv-lin-dot " : "spv-lin-dot ") + n.cls;
        r.dot.setAttribute("class", base + cls);
        r.dot.setAttribute("aria-pressed", chosenSet[n.id] ? "true" : "false");
        r.dot.setAttribute("aria-label", n.line + (n.choosable ? "" : " (cannot be chosen)") + (chosenSet[n.id] ? ", chosen" : "") + (built[n.id] ? ", built from the chosen place" : "") + (lastMarks[n.id] ? ", holds audit step(s)" : ""));
        if (on) {
          var p = s.pos[n.id];
          if (n.kind === "T3") { r.dot.setAttribute("x", p[0] - 5.5); r.dot.setAttribute("y", p[1] - 5.5); }
          else { r.dot.setAttribute("cx", p[0]); r.dot.setAttribute("cy", p[1]); }
          r.dotmark.setAttribute("x", p[0] + 7); r.dotmark.setAttribute("y", p[1] - 5);
          r.dotmark.textContent = lastMarks[n.id] ? "*" : "";
        }
        var mk = lastMarks[n.id];
        r.mark.textContent = mk ? ("audit step" + (mk > 1 ? "s: " + mk : "")) : "";
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
      // the text area: the hovered or focused node, else the last chosen place
      var shownId = hot || (chosen.length ? (chosenSet[st.last] ? st.last : chosen[0]) : null);
      text.textContent = "";
      if (shownId) {
        byId[shownId].detail.forEach(function (ln, i) { text.appendChild(el("div", i === 0 ? "spv-lin-text-head" : "spv-lin-text-line", ln)); });
        if (lastMarks[shownId]) text.appendChild(el("div", "spv-lin-text-line", "This place holds " + lastMarks[shownId] + " audit step(s): see the Pipeline Audit panel on the right (reason, remove)."));
      } else {
        text.appendChild(el("div", "spv-lin-text-line", HINT));
      }
      chosenInfo.textContent = chosen.length ? ("Chosen: " + chosen.map(function (c) { return byId[c].name; }).join(", ") + ".") : "No place chosen.";
      create.disabled = !chosen.length;
      createNote.textContent = chosen.length ? (st.mode === "around" ? "" : "The dialog opens with the chosen place(s) ticked, for the step you staged in the Filters panel (view T3).") : "Choose a place first.";
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
    create.addEventListener("click", function () { send("lineage_create", Date.now()); });

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
