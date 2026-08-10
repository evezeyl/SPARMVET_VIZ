Notes while claude is busy (to organize after)

Testing full mode still  - actually the all rows toogle works (at least with figshare - was a bit slow) - Buy what is confusing in the data preview with toogle of it shows 100 (eg. Viewing rows 1 through 4 of 100) - we should make it clear that its a sample/preview of the dataset NOT the full dataset (maybe change the text Viewing rows 1 through 4 of 100 out of TOTAL?)f

# Testing notes — 2026-08-10 (part 1)

Raw evidence + fix log. Kept separate from `test_plan_2026-06.md` on purpose: the
checklist stays a thin, quick-to-scan ledger (one line per item); everything long
(console pastes, root-cause writeups, retest instructions) lives here instead,
anchored by the same ID the checklist line points to.

**Convention going forward:** when you hit something new while testing, jot it here
under a `## <ID>` heading (make up a short ID if it's not already in the checklist —
I'll fold it into `test_plan_2026-06.md` as a one-liner). When I fix something, I
append a `> FIX:` line under the same heading, not in the checklist.

---

## PRE-01 — Console errors on first launch

Manifest opened by default: `figshare_integration`. Persona: developer ("Active:
Workflow Developer"). Terminal: only `ConfigManager` auto-unnesting info lines, no
traceback. Chrome console showed:

```
bootstrap-datepicker.min.js:1 DEPRECATED: This filename doesn't follow the convention...
bootstrap-datepicker.min.js:1 DEPRECATED: The language code "kh"/"kr"/"rs-latin"/"rs" ...
bp_expr_editor.js:138 Uncaught TypeError: Failed to execute 'observe' on 'MutationObserver':
    parameter 1 is not of type 'Node'.
VM624:1 Uncaught ReferenceError: jw is not defined   (×2, plus 5× "VI is not defined")
```

> **NOISE** — `bootstrap-datepicker` deprecation warnings: the vendored library
> complaining about its own locale files (Khmer/Korean/Serbian codes). Not our code.
> No action.
>
> **NOISE** — `VM624…VM638: jw`/`VI is not defined`: grepped every vendored JS file
> in `app/src/www/vendor/`, no match for either name anywhere in the codebase, and
> the stack traces (`<anonymous>:1:9`) show zero connection to any of our files.
> Classic signature of a browser-extension-injected script. Sanity check: open the
> app in an Incognito window with extensions off — if they vanish there, ignore.
>
> **FIX** — `bp_expr_editor.js:138`: the script loads in `<head>` with no `defer`
> (`app/src/ui.py:58`), so `document.body` is still `null` when
> `observer.observe(document.body, …)` runs. It throws, and the MutationObserver
> that's supposed to watch for later-added expression-editor textareas never
> starts — meaning BLUEPRINT's column-autocomplete only worked on textareas
> present at first paint. Changed to observe `document.documentElement` (exists
> immediately, still catches everything added to `<body>` later). Commit: not yet
> committed — uncommitted on `dev`.
>
> RETEST ↻ — hard-refresh (Ctrl+Shift+R), reopen console, confirm the
> `bp_expr_editor.js:138` TypeError is gone. Then open an expression-editor
> textarea that appears *after* a reactive re-render (e.g. add a `mutate` node in
> BLUEPRINT) and confirm `pl.col('` autocomplete fires there too — that's the part
> that was actually broken, not just the console noise.
>
> **2026-08-10 retest round 1:** error still showed after Ctrl+Shift+R, but pinned
> to line 138 (the *old* file's line — the fixed file's `observe()` call is on
> line 140). Confirmed via `curl localhost:8000/bp_expr_editor.js` that the server
> is serving the fixed version — this was a stale browser cache of the `<script
> src>`, not an unfixed bug. Fix for the confusion, not the bug: `Disable cache`
> in DevTools → Network tab while reloading, or fully close/reopen the tab.
> **Real follow-up (small, not urgent):** `app/src/ui.py:58` has no cache-busting
> on any vendored/first-party `<script src>` — every future JS edit will hit this
> same "did my fix even load" confusion during dev. Worth a one-line fix later
> (e.g. `?v=<mtime>` query param on the script tags) but not blocking testing.
>
> **Also confirmed 2026-08-10:** the `VM8xx: jw`/`VI is not defined` batch is the
> **Zotero Connector browser extension** — round 1 console paste also showed
> `zotero.js:334` and `inject.js:90` in the same dump. Fully external, ignore.

---

## REG-10 — Duplicate Shiny IDs: `notification_log_accordion` / `notification_log_panel_ui`

```
The following ID was used for more than one input: "notification_log_accordion": 2 inputs
The following IDs were used for more than one input/output:
  "notification_log_panel_ui": 2 outputs
  "notification_log_accordion": 2 inputs
```

> **ROOT CAUSE** — `sidebar_tools_ui` (LEFT sidebar, `app/handlers/home_theater.py`)
> hardcoded `ui.output_ui("notification_log_panel_ui")` unconditionally into the
> Gallery and Blueprint ("Wrangle Studio") branches. Meanwhile `right_sidebar_content_ui`
> (RIGHT sidebar) *also* mounts it for Home (config-driven, correct), but its Gallery
> and Blueprint branches never read their own `notification_log` slot despite
> `gallery_focus_right.yaml` / `blueprint_standard_right.yaml` declaring it. Net
> effect: for Gallery/Blueprint the only working copy was the left-sidebar hardcode;
> during a sidebar-switch reactive tick, that stale left copy and the newly-computed
> right copy could transiently coexist → duplicate id.
>
> **FIX** — Removed the two hardcoded left-sidebar mounts (Gallery, Blueprint) and
> added proper config-driven mounts to the RIGHT sidebar's Gallery and Blueprint
> branches (same pattern Home already used: check `get_sidebar_config(ws, "right")`
> for `notification_log` in the slot list). Single source of truth now: the right
> sidebar only, matching ADR-073. `app/handlers/home_theater.py`, verified
> `from app.src.main import app` still imports clean. Uncommitted on `dev`.
>
> RETEST ↻ — reload, switch Home → Gallery → Blueprint → Home a few times, confirm
> no more duplicate-ID console warnings, and confirm the 🔔 Alerts panel still shows
> up in Gallery's and Blueprint's right sidebar (it should — that's the point of the
> fix, not just silencing the warning).

---

## HOM-37 `[!]` — "All rows" toggle blanks the data preview table (BUG)

> EVE: Toggling "All rows" on removes the view entirely — no table shown.

> **STATUS: not yet root-caused.** `home_data_preview` (`app/handlers/home_theater.py:1015`)
> wraps the collect in a try/except that renders an "Error" grid on failure — so a
> silent blank (not even an error grid) suggests either (a) the full `.collect()`
> genuinely returns 0 rows for this dataset once filters apply to the whole frame
> instead of just the first 100, or (b) an exception outside that try/except (e.g.
> in Shiny's own render pipeline). Need one more piece of evidence before touching
> code: **next time you toggle it on, check the terminal running `shiny run` at
> that exact moment** — paste any traceback here, even a partial one. Without that
> I'd be guessing.

---

## HOM-38 `[?]` — Redundant "Plot" accordion title above each plot

> EVE: There is a "Plot" title or bold text in each plot, under each category —
> would be nice to remove, seems independent of each plot's own title.

> This is intentional by design (ADR-043, `rules_ui_dashboard.md §4`): plots are
> wrapped in a collapsible accordion literally titled "Plot" (`app/handlers/home_theater.py:592`),
> separate from the "Data Preview" accordion below it. Your point stands — it reads
> as redundant next to each plot's own matplotlib title. Options: (1) leave as-is,
> (2) blank the accordion label (keep it collapsible, just no visible text), (3)
> rename to something more useful (e.g. the plot's own label). Your call — flagged
> `[?]` in the checklist, not changing anything until you decide.

---

## CSS-06 `[~]` — "All rows" switch not aligned with "Data Preview" label

> EVE: Toggle "All rows" should be aligned to "Data Preview".

> Low priority, batched with the rest of the CSS backlog (`app/handlers/home_theater.py:751-762`,
> the `d-flex align-items-center` row holding both the label and the switch). Will
> fix in the CSS homogenisation pass along with CSS-01..05.
