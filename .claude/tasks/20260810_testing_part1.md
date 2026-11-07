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

Data analysis recipe opened by default: `figshare_integration`. App features: developer ("Active:
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

---

## HOM-39 `[~]` — Data Preview 100-row cap not communicated

> EVE: screenshot, "Data Preview" accordion — need to make clear that the table is
> capped at 100 rows. Either show "Viewing rows 1 through 100 of XX" where XX is
> the real total row count of the underlying table (not the 100 cap), or simpler:
> relabel the header "Data Preview (first 100 rows)".

> Not fixed yet — registering only, per your request. Implementation note for later:
> `home_data_preview` (`app/handlers/home_theater.py:1015-1042`) already computes
> `df = lf.head(100).collect()` when `show_all=False` — the total row count isn't
> currently fetched at all, so either option needs one extra cheap call
> (`lf.select(pl.len()).collect().item()`) to get the real total without
> materialising the whole frame. Your simpler option (static "(first 100 rows)"
> label) avoids that extra query entirely — worth considering purely on cost, not
> just simplicity. Your call which one; note it here or on the checklist line when
> you decide.

---

## HOM-04 follow-ups: tier toggle + audit scope (2026-08-10)

Your HOM-04 note described four distinct problems in one observation. I traced each
one in the code before registering — one is a confirmed bug, three are design
questions. Splitting them so the bug fix isn't blocked on the design discussion.

### HOM-41 — T3 audit nodes leak into T1/T2 reference views (CONFIRMED BUG)

> EVE: "When adding to audit that transform all the T1, T2 and T3 data shown - It
> should only transform the T3."

**Confirmed by reading the code, not yet re-verified live in the browser** (worth
doing after the fix). The tier toggle itself is fine — `_resolve_active_lf`
(`app/handlers/home_theater.py:241`) correctly branches: T1 → raw T1 lazyframe,
T2/T3 → T1 + the data analysis recipe's tier2 wrangling. That part works as designed.

The bug is downstream: `_t3_filter_rows()` and `_t3_drop_columns()`
(`home_theater.py:280`, `:328`) return the **committed** T3 audit nodes for the
active plot with **no check on `tier_toggle` anywhere** — they always return
whatever is committed, regardless of which tier button is selected. And both
consumers apply them unconditionally:

- Plot renderer `_group_plot_handler` (`:407`, `:437`): `filter_rows = applied_filters + _t3_filter_rows(...)`, and drops applied the same way — no tier check.
- `home_data_preview` (`:1026`, `:1028`): identical pattern.

Net effect: once you commit a filter or column-drop via the Pipeline Audit, it
shows up in the T1 and T2 views too, not just T3. This breaks the invariant the
whole audit/reproducibility model depends on — T1/T2 are supposed to be the
untouched reference you compare T3 against (`ui_implementation_contract.md §5`).

> **FIXED (2026-08-10).** Gated every consumer behind `tier_toggle.get() == "T3"`:
> `_group_plot_handler` (filter injection `home_theater.py:407-410`, drop
> application `:436-440`), `home_data_preview` (`:1026-1031`), and
> `home_col_selector_ui` (`:1074-1076` — traced this one during the fix, it had
> the identical gap: a T3-committed drop was removing the column from the T1/T2
> selector too). `col_drop_audit_btn_ui` needed no change — it already early-returns
> when `tier_toggle != "T3"` (line 1104), so its internal use of
> `_t3_drop_columns()` was already correctly scoped.
>
> Verified: `from app.src.main import app` clean, `test_filter_operators.py`
> 24/24 pass, Playwright smoke suite 14 passed/3 skipped (expected). Uncommitted
> on `dev`.
>
> RETEST ↻ — commit a filter and a column-drop to the audit on one plot, then
> switch the tier toggle to T1 and T2 — neither should show the filter or the
> dropped column. Switch back to T3 — both should reappear.

### HOM-40 — No explicit "viewing tier X" indicator `[?]`

> EVE: "When T1 selected T1 should be showed, When T2 T2 should be shown when T3
> the selected filters should be shown."

Code-wise the data *is* correctly tied to the toggle (see HOM-41 above — that part
works). What's likely driving this observation: there's no on-screen confirmation
of which tier is actually feeding the current plot/table other than the toggle's
own selected state — if a given plot's T1 and T2 outputs happen to look similar
for the loaded dataset (unlike `year_distribution`, which HOM-05 specifically
picked because T1→T2 removes visible bars), it can read as "nothing changed = the
button isn't doing anything." Possible fix: a small badge near the plot/table
("Viewing: T2 — Processed") so the tier is unambiguous regardless of whether the
data happens to visibly differ. Decision needed on whether/how to add this.

### HOM-42 — (discuss later) Show T2 + T3 side-by-side under one graph `[?]`

> EVE: "could we have the data from T2 and the data from T3 shown under each
> graph — this is a possible improvement to discuss after — but it should make
> clear at least that it shows T3 otherwise."

Explicitly flagged by you as a later discussion, not a bug — Comparison Mode
already does a 2-column T1/T2-vs-T3 layout (`ui_implementation_contract.md §5`)
but it's a separate toggle, not "always visible under every graph." The narrower,
immediate part of this ask (a "Viewing: T3" label) is the same fix as HOM-40 — no
separate work needed there, just note it satisfies both.

### HOM-43 — T3 mode has no exploration-only filter path `[?]`

> EVE: "if a filter is not added to the pipeline audit, then the data is not shown
> as filter for exploration... the user should be able to filter for exploration
> the data BUT should not be able to write those changes as definitive manner."

This is real and matches the code: in T1/T2 mode, the Filters panel's "Apply (N)"
commits straight to `applied_filters` — no audit trail, fully exploratory, exactly
as designed (`ui_implementation_contract.md §4`: "Ref Table Filter... NONE
(Transient)"). But per `rules_ui_dashboard.md §1` and HOM-06, once you're in T3
mode the *same* Apply button relabels to `➜ Audit (N)` and routes through the
propagation-modal + reason-gate — i.e. **every** filter typed while in T3 mode
becomes a permanent, audited decision. There's currently no "just try this filter
in T3 without committing it" path. Decision needed: does T3 mode get its own
exploration-only filter layer (separate from `applied_filters` and the audit
recipe), or is the current behaviour intentional (T3 = "you're already in the
definitive-decision zone, exploration happens in T1/T2 first")? This is a real
product decision, not a small tweak — worth its own conversation.

> **DECIDED + FIXED (2026-08-10).** EVE's proposal: a T3-specific exploration
> path that becomes permanent only on an explicit second action. Turned out to
> map almost exactly onto existing plumbing — the fix is a split, not new
> machinery: `_filter_apply` (`app/handlers/filter_and_audit_handlers.py:389`)
> previously branched on `tier_toggle`, skipping `applied_filters` entirely in
> T3 and jumping straight to building audit-pending nodes. Split into two
> handlers:
> - **`filter_apply`** — always commits to `applied_filters` (exploration,
>   transient, visible on every tier), no tier branch left at all.
> - **`filter_send_to_audit`** (new) — the old T3 promotion logic, unchanged
>   internally (primary-key stamping, propagation dialog), now its own button.
>
> `filter_controls_ui` renders `filter_send_to_audit` only when
> `tier_toggle.get() == "T3"` — this is transitively flag-safe with no new
> gate needed: the tier toggle itself only offers "T3" when
> `t3_sandbox_enabled` is on (`home_theater.py:711`), and the whole Filters
> panel only renders when `interactivity_enabled` is on
> (`filter_and_audit_handlers.py:71`), so the button can never appear in a
> config where it shouldn't.
>
> Both buttons carry a `title=` hover tooltip explaining the consequence (EVE's
> ask) — Apply says it's exploration-only, not exported; Send to Audit says it
> writes to the permanent log and is included in exports. Kept the "Audit"
> wording (not "Make Permanent") to stay consistent with the existing "Pipeline
> Audit" panel name rather than introduce a second term for the same concept —
> flag if you'd rather change it, it's a one-line label swap.
>
> Verified: `from app.src.main import app` clean, `test_filter_operators.py`
> 24/24 pass, Playwright smoke suite 14 passed/3 skipped (expected, same as
> baseline). Uncommitted on `dev`.
>
> RETEST ↻ — in T3 mode: add a filter row, click Apply → plot/table update
> immediately, nothing in the audit panel yet. Click Send to Audit → propagation
> modal opens as before; after committing, HOM-41's tier isolation should also
> hold (T1/T2 still unaffected). In T1/T2 mode: only the Apply button should
> appear (Send to Audit hidden), same as before this change.

---

## HOM-41 / HOM-43 — ADR-085 amendment (same day, second round)

After the first round of fixes above, live testing (your screenshot + direct
report) surfaced two more things the first pass didn't cover — both folded into
**ADR-085** (architecture_decisions.md), not a new ADR:

1. **Exploration filters (`applied_filters`) had the identical T1/T2 leak** as the
   committed audit nodes — pre-existing behavior, not introduced by the HOM-43
   split, but only surfaced once Apply started actually working everywhere.
   Fixed the same way: gated behind `tier_toggle == "T3"` in
   `_group_plot_handler` and `home_data_preview`. T1 and T2 are now **fully**
   pure — no exploration filter, no audit-committed filter/drop, ever.

2. **"My view" (T3) decoupled from audit capability entirely** — your proposal.
   The tier toggle now offers "My view" whenever the Filters panel exists
   (`interactivity_enabled`), not only when `t3_sandbox_enabled` is on
   (`home_theater.py` `tier_choices`, was gated on `t3_sandbox_enabled`, now
   isn't). Without `t3_sandbox_enabled`, "My view" is a pure scratchpad: filters
   apply and render there for the session, but "Send to Audit" doesn't appear
   (now double-gated: `tier_toggle == "T3"` AND `t3_sandbox_enabled`, both in
   `filter_controls_ui` and defensively re-checked in `_filter_send_to_audit`).

**No config file changes needed** — `pipeline-exploration-simple_template.yaml`
already has exactly `interactivity_enabled: true` + `t3_sandbox_enabled: false`,
which is precisely the combination that now produces "My view without audit."
The fix changed what the flags *mean* in code, not their values per app features.

**Documented in:** `architecture_decisions.md` ADR-085 (rewritten to the final
form, not left as a superseded stub), `ui_implementation_contract.md` §4/§5/§8/§12a,
`rules_app_features_flags.md` Group B, `test_plan_2026-06.md` CFG-02 + the CFG
matrix row. `@deps` blocks updated in both modified files; dependency graph
regenerated (144 nodes, 278 edges).

Verified: import clean, `test_filter_operators.py` 24/24, Playwright smoke suite
14 passed / 3 skipped (unchanged baseline — `qa` app features has `t3_sandbox_enabled:
true`, so the automated suite doesn't exercise the new scratchpad-only path;
that needs a live check under `pipeline-exploration-simple_template.yaml`,
tracked as CFG-02).

---

## HOM-44 — Year axis discrete on T2 but continuous on T3/My view

> EVE: "A fix associated to the Compare T2 VS T3 - example using
> '1_test_data_ST22_dummy - AMR and Virulence' and then Year distribution: The
> scale of the graph for the year is good in year (appears discrete for T2) but
> for T3 it looks like continuous - we have to find a way to make it look
> continuous as T2 (but that is not most urgent)."

Not yet investigated. Likely candidate area: `viz_factory.render()`'s discrete-
axis handling (`rules_data_analysis_recipe_structure.md §6` — "Biological Typing & Discrete
Plotting" mandates casting integer-year columns to `int`/`string` for discrete
scales) combined with whatever wrangling step T3's "My view" pipeline applies
that T2's doesn't — worth checking whether the T3 code path re-casts Year back
to a numeric/float type somewhere between T2's wrangling and the plot render.
EVE flagged this as low urgency — parking until higher-priority HOM items are
through a round.

---

## CSS-07 — "Compare Result vs My view" toggle rename + alignment

> EVE: "The 'Compare T2 vs T3' toggle could be renamed to 'Compare Result VS My
> view' and then in grey under (same as check buttons - if possible then put
> 'T2 vs T3'). Also I would move the toggle a bit to the right side - it is too
> close to the other checkbox, and try to align at the same height - so it
> looks nicer."

Not yet implemented — cosmetic, low priority, and the exact wording should wait
for the HOM-40/42 "viewing tier" indicator decision since they're the same UI
real estate (a label near the tier controls explaining what you're looking at).
Batching this with that decision rather than styling it twice.
