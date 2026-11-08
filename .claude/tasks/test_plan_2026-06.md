# SPARMVET_VIZ — Live App Test Plan

**Owner:** @evezeyl (tester) · @dasharch (fixer)
**Created:** 2026-06-19
**Baseline:** `dev` branch @ Phase 34 (TEST_LAB built, BLUEPRINT full feature set, legacy removals, 8 app features files)
**Supersedes:** [`tasks_test_ui_current.md`](tasks_test_ui_current.md) (pinned to Phase 26 — stale; its still-open items are folded in here, see each `(carried)` tag)
**Scope:** **Phase 2** — BLUEPRINT · GALLERY · TEST_LAB + configuration-file gating + cross-space workflow + the regression/CSS items not specific to HOME. **HOME itself was split out on 2026-11-08** into [`test_plan_home_2026-11.md`](test_plan_home_2026-11.md) (Eve: test what you actually see on launch, in that order, by itself, before anything else) — do that file first, then come back here. Comprehensive, but **prioritised** — see §0.4.

> EVE: testing in google chrome - developper console - network - cache deactivated 
---

## 0. How this document works (read first — this is the efficiency engine)

This is a **living test/fix ledger**, not a one-shot checklist. We loop over it several times. The whole design exists so that each round is cheap for both of us:

- You walk the app, flip a status marker, and (only on problems) write one note.
- I scan for the failure markers, fix, and stamp the item so you know exactly what to re-test.
- Nothing gets lost between chats: every item has a stable ID and lives in one file.

### 0.1 Status markers (the one thing that matters)

Change the checkbox. That's the whole protocol. I grep the three "needs-me" markers every round.

| Marker | Meaning | Who sets it | I act on it? |
|---|---|---|---|
| `> EVE:` | Eve commented / added information for claude | - | **yes** claude must read information |
| `[ ]` | Not yet tested | — | no |
| `[x]` | PASS — works as expected | Eve | no |
| `[!]` | **FAIL** — broken / error / wrong behaviour | Eve | **yes** |
| `[~]` | **POLISH** — works but needs a tweak (styling, wording, UX) | Eve | **yes** |
| `[?]` | **DECISION** — needs a design choice before code | Eve | **yes (discuss)** |
| `[b]` | BLOCKED / not built yet — can't test (note why) | Eve | maybe |
| `[-]` | N/A for this app features/config | Eve | no |

### 0.2 How to write a finding (only on `[!]` `[~]` `[?]`)

Flip the box, then add **one indented note line** starting with `>`. Keep it short — symptom, not diagnosis.

```
[!] HOM-XX — Tier toggle resets active sub-tab on Home→Gallery→Home
    > EVE: lands back on first plot instead of the one I left. Terminal had no traceback.
```
*(In a real item the line starts `- [!] …`; the leading `- ` is dropped here only so this example isn't caught by the open-items grep.)*

You can attach a screenshot path or terminal snippet the same way. Don't fix anything inline — just report.

**Backtick hint tags:** some items carry a small tag after the ID like `` `[?]` ``, `` `[~]` `` or `` `[b]` `` — that is *my pre-flag* of the likely disposition (decision / polish / not-built), to save you guessing. The **checkbox is still the real status you set** — leave it `[ ]` until you've actually looked, then flip it.

**Keep this file thin (added 2026-08-10):** the checklist line stays **one line** — ID, marker, short symptom, and a link if there's evidence. Raw material (console pastes, screenshots, my root-cause writeups, retest steps) goes in a dated findings file — `.claude/tasks/YYYYMMDD_testing_partN.md` — under a `## <ID>` heading matching the checklist ID, e.g. [`20260810_testing_part1.md`](20260810_testing_part1.md). Link the checklist line to `filename.md#anchor`. Anything you jot in the raw file that isn't a checklist line yet, I fold into a one-liner here with a link back.

### 0.3 The round-trip (what each side does)

1. **Eve tests** a section, flips boxes, writes `> EVE:` notes on any `[!]/[~]/[?]`.
2. **Ping me** ("LAB section done", or just "go"). I run the grep in §0.5, and for each open item I either fix it or ask. I stamp the item:
   ```
   [!] HOM-XX — Tier toggle resets active sub-tab ...
       > EVE: lands back on first plot ...
       > FIX: home_theater.py — restored selected= on dynamic_tabs (isolate read). commit abc1234
       > RETEST ↻
   ```
3. **Eve re-tests** only the `RETEST ↻` items → flip to `[x]` (done) or back to `[!]` with a fresh note (re-opened).
4. Repeat. The **Iteration Log** (§0.6) is the running heartbeat.

Rules of the loop: I never mark `[x]` (only you confirm a pass). You never edit my `FIX:` lines. One file, append-don't-delete on notes so history survives.

### 0.4 Suggested testing order (priority — highest risk first)

**2026-11-08: HOME moved to its own file** (`test_plan_home_2026-11.md`) and goes first, by itself,
end to end — that file has its own launch section and its own copy of the relevant REG/CSS items.
Once it's done, this file picks up where it left off:

1. **§3 TEST_LAB** — brand new in Phase 34, never live-tested → highest payoff
2. **§4 BLUEPRINT** — mostly new since Phase 26 (forms, joint designer, escape hatch, undo, branch, AI agent)
3. **§6 GALLERY** — mature; lighter re-verify
4. **§2 Configuration-file gating** — quick, can be done any time; this is where HOME's own
   *limitations* under `pipeline-static` etc. get checked, now that you've seen it at full capability
5. **§7 Cross-space**, remaining **§8 Regression**/**§9 CSS backlog** (nothing HOME-specific left
   here — see `test_plan_home_2026-11.md` §9/§10 for those) — last

### 0.5 Grep commands (self-serve at any time)

```bash
cd .claude/tasks
# everything still open (fail / polish / decision):
grep -nE '^\s*- \[[!~?]\]' test_plan_2026-06.md
# just hard failures:
grep -nE '^\s*- \[!\]' test_plan_2026-06.md
# items I've marked ready for you to re-test:
grep -n 'RETEST ↻' test_plan_2026-06.md
# progress tally:
grep -coE '^\s*- \[x\]' test_plan_2026-06.md   # passed
grep -coE '^\s*- \[ \]' test_plan_2026-06.md   # untested
```

### 0.6 Iteration Log (heartbeat — I maintain this)

| Round | Date | Tested | Open after round | Notes |
|---|---|---|---|---|
| 0 | 2026-06-19 | — | — | Plan authored. Awaiting first pass. |
| 1 | 2026-11-05 | HOME header strip, tier badges, Data Import, plot render, broken-data message | 24 passed, 128 untested, 5 blocked or polish (HOM-44 open bug in a draft) | Issues #1 to #18 handled on `dev`. Obsolete or duplicate items removed (CSS-02/03/04, HOM-04 rewritten). TEST_LAB, BLUEPRINT, GALLERY and the config-file items (CFG) not yet tested. |
| — | 2026-11-08 | No new Eve testing this round — plan reviewed before she resumes (she asked to verify independent tasks were done, then review the plan). Checked §0.5 grep: only `PRE-01`/`REG-10` open, both already fixed and `RETEST ↻`, nothing new for me. Added `HOM-52` and `BLU-31` for two surfaces built this session that were never live-tested: the new left-sidebar "Processing Issues" panel (moved there after finding it was built but never mounted at all — F-26, `uml_findings.md`), and BLUEPRINT's inline error display for recipe-load/YAML-hatch failures (fix text shown in-panel, not just a toast). Confirmed `HOM-44` already covers the year-axis continuous-vs-filter bug Eve re-noted in `issue-drafts/20261105_notes_testing.md` — no new issue needed there, same bug, already reproduced. Section §2's config-file list (8 files) still matches what's shipped. | — |

---

## 1. Launch & environment (PRE)

> **PRE-01/02/03/05 moved to `test_plan_home_2026-11.md` §0** (first launch, default recipe,
> switching recipe — all observed from inside HOME, tested there first). Only the config-file-switch
> check stays here, since it's about a *different* config file, not HOME itself.

> **Architecture note (2026-08-10 — read this before §2):** "App features" is not a fixed
> enum the app understands — it's just a naming convention for a config file. The
> `SPARMVET_APP_FEATURES` env var is passed straight to `Bootloader.set_app_features()`, which
> either resolves a shortname to `config/app_features/<name>_template.yaml` **or**
> accepts a direct path to any YAML file (`app/src/bootloader.py:260-276`). What
> actually drives app behaviour is the **flags inside that file** — nothing else.
> So we test **configuration files**, not "app features files": §2 below launches each file
> directly and confirms what its flags actually produce, exactly as
> `rules_app_features_flags.md`'s own anti-pattern rule says the *app code* must
> do (`bootloader.is_enabled(flag)`, never an app features name check) — the test process
> should mirror that, not contradict it.

> **Switching config file = relaunch** pointing `SPARMVET_APP_FEATURES` at a different file. There is **no** in-app selector. All 8 files live in `config/app_features/` — full launch command per file in §2.

- [ ] PRE-04 — Relaunch pointing at `config/app_features/qa.yaml` → terminal shows `App features: config/app_features/qa.yaml`; app still boots clean. (qa's flags: everything on, `ghost_save: false`.)

---

## 2. Configuration-file gating (CFG) — what each file's flags actually produce

Relaunch once per file below and confirm the surfaces it produces. This is fast (just "is it there or not") and catches positive-inclusion (ADR-071) regressions. Authoritative flag matrix: `rules_app_features_flags.md`. This section replaced the old app features framed "PER" checklist on 2026-08-10 — same content, reframed around the actual driver (the file), see the note in §1.

**Launch commands** (paste directly). Since ADR-091 the four app features that hide the data analysis recipe selector need a named data analysis recipe: `pipeline-static` and `pipeline-exploration-simple` get it from `SPARMVET_DATA_ANALYSIS_RECIPE`; the two demos start from their demo deployment (`config/deployment/demo/`), which names the data analysis recipe and carries the banner and stylesheet:

```bash
PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/pipeline-static.yaml SPARMVET_DATA_ANALYSIS_RECIPE=1_test_data_ST22_dummy ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_DEPLOYMENT=config/deployment/demo/demo-vetinst.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/pipeline-exploration-simple.yaml SPARMVET_DATA_ANALYSIS_RECIPE=1_test_data_ST22_dummy ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_DEPLOYMENT=config/deployment/demo/web-demo.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/pipeline-exploration-advanced.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/standalone.yaml           ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/developer.yaml                     ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/qa.yaml                            ./.venv/bin/shiny run app/src/main.py --reload --port 8000
```

**Compact expectation grid** — confirm each cell against the file's actual flags (`rules_app_features_flags.md` full matrix). Mark the row's checkbox `[x]` if the whole row matches, `[!]` if any cell is wrong (note which).

| | pipeline-static | pipeline-exploration-simple | pipeline-exploration-advanced | standalone | developer | qa |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Filters panel (left) | absent | yes | yes | yes | yes | yes |
| Tier toggle "My view" (ADR-085: gated on Filters existing, not audit) | no | **yes** | yes | yes | yes | yes |
| "Send to Audit" button + right sidebar (Audit) | absent | absent | yes | yes | yes | yes |
| Session Mgmt panel | no | yes | yes | yes | yes | yes |
| Export panel | yes | yes | yes | yes | yes | yes |
| Data Import panel | no | no | yes | yes | yes | yes |
| **Gallery** nav | no | no | no | yes | yes | yes |
| **Blueprint** nav | no | no | no | yes | yes | yes |
| **Test Lab** nav | no | no | no | no | yes | yes |

- [ ] CFG-01 `pipeline-static.yaml` — read-only: no Filters, no T3, no right sidebar, no Gallery/Blueprint/Test Lab nav. Export present. *(carried: old PER-01, passed at Phase 26 — confirm still true.)*
- [ ] CFG-02 `pipeline-exploration-simple.yaml` — Filters present; tier toggle now includes **"My view"** as a scratchpad (ADR-085, 2026-08-10) — filters apply there, but no "Send to Audit" button and no right sidebar appear. No Gallery/Blueprint/Test Lab.
- [ ] CFG-03 `pipeline-exploration-advanced.yaml` — Filters + T3 + right Audit sidebar; **no** Gallery/Blueprint/Test Lab nav.
- [ ] CFG-04 `standalone.yaml` — adds **Gallery** + **Blueprint** nav; still **no** Test Lab.
- [ ] CFG-05 `developer.yaml` — everything incl. **Test Lab** nav.
- [ ] CFG-06 `qa.yaml` — same surfaces as `developer.yaml` (used for deterministic testing; `automation.ghost_save: false`).
- [ ] CFG-07 `demo-vetinst.yaml` — boots; intentionally minimal (most flags off, export off). Confirm no crash and that it looks like a locked-down reference deployment.
- [ ] CFG-08 `web-demo.yaml` — boots; minimal-interaction demo. Confirm no crash.
- [ ] CFG-09 — Display name under the nav pills reflects each file's own `display_name` field (not hardcoded, not derived from the filename). *(carried: old PER-09.)*
- [ ] CFG-10 `[?]` **NEW** — Point `SPARMVET_APP_FEATURES` at a **custom** YAML (copy `developer.yaml`, flip one flag, e.g. `gallery_enabled: false`, save under a new name) and confirm the app respects it correctly with no code changes. This is the actual proof that behaviour is config-driven, not app features enum-driven — worth doing once.

---

### 2b. Names, launch rules and old files (ADR-091, issue evezeyl/SPARMVET_VIZ#27)

Most of this is already checked by automatic tests (`app/tests/test_bootloader_launch.py`, `test_legacy_formats.py`, `libs/utils/tests/test_path_expansion.py`); the items below are what a person must see once.

- [ ] CFG-11 — Start `pipeline-static` **without** `SPARMVET_DATA_ANALYSIS_RECIPE` (remove it from the command): the terminal shows a `[FATAL]` block that names both `default_data_analysis_recipe` (deployment file) and `SPARMVET_DATA_ANALYSIS_RECIPE`, and the app does not start. Readable?
- [ ] CFG-12 — Start with the old variable (`SPARMVET_PERSONA=qa` or `SPARMVET_PROFILE=...`): the app stops and the message names the new variable. <!-- audit:allow-old-word -->
- [ ] CFG-13 — Demo deployments (`config/deployment/demo/web-demo.yaml`, `demo-vetinst.yaml`): the banner (logo, title) and the demo colours appear; with `developer.yaml` they do not. The data analysis recipe selector is absent.
- [ ] CFG-14 — `SPARMVET_DATA_ANALYSIS_RECIPE=2_test_data_ST22_dummy` with `developer.yaml`: that data analysis recipe is the one open at start; the selector (visible) still lets you switch.
- [ ] CFG-15 — A wrong data analysis recipe name (`SPARMVET_DATA_ANALYSIS_RECIPE=nope`): `[FATAL]` naming the name and the data analysis recipes that exist.
- [ ] CFG-16 — `~` in a deployment folder: copy `config/deployment/local/local.yaml`, set `cache: "~/sparmvet_test/cache"`, start with `SPARMVET_DEPLOYMENT=<copy>`: the folder is created under your home. Then write `${NOT_SET}/x` instead: the app stops and names `NOT_SET`.
- [ ] CFG-17 — Session panel with an old session (one written before the rename; your `tmp/UI_TEST` has some): it is listed with a red message and the conversion command, not hidden. After `python assets/scripts/migrate_config_vocabulary.py --sessions tmp/UI_TEST/user --apply` it restores normally.
- [ ] CFG-18 — Labels in the user interface read well: the left panel says "Data analysis recipe" (not "Manifest"), the gallery says "Example" (not "Recipe"), the audit panel says audit steps. Note any awkward wording (`[~]`). <!-- audit:allow-old-word -->
- [ ] CFG-19 — The "Info" panel (top of the left panel) shows what is written under `info:` of the open data analysis recipe (title, subtitle, description, version). Open `1_test_data_ST22_dummy`, then `retest_tier2`: the panel changes with the recipe, and the Filters and Export panels keep working after the switch. Add a line such as `contact: x` under `info:` of a copy: it shows without any code change. <!-- audit:allow-old-word -->
- [ ] CFG-20 — The dropdown is labelled "Data analysis recipe"; no screen says "Project" for it. The app features name is `standalone` (not `project-independent`). The colour widget in BLUEPRINT says "Deployment palette". <!-- audit:allow-old-word -->

## 3. TEST_LAB (LAB) — **new in Phase 34, highest priority**

> Config file: `developer.yaml` or `qa.yaml` (only these two set `test_lab_enabled: true`). Click the **Test Lab** nav pill.
> Design: `.claude/design/spaces/TEST_LAB.md`. Rules: `rules_test_lab.md`.
> **Principle to keep in mind while testing:** every tool is **stateless** — it runs, hands you a downloadable file, and resets when you close its panel. Nothing persists except files you explicitly save. If you find state leaking between tools/panels, that's a `[!]`.

### 3a. Space loads
- [ ] LAB-01 — Test Lab nav pill present (developer/qa); clicking it switches the center to the TEST_LAB toolbox; left sidebar shows the tool panels (one accordion per tool).
- [ ] LAB-02 — Left sidebar lists the tool categories: Reformatter, ID Reconciliation, Data Analysis Recipe Scaffolding, Anonymiser, AquaSynthesizer (synthetic data). Note any that are missing/greyed.
- [ ] LAB-03 — Opening a tool panel and closing it resets it to empty (stateless). Open tool A, then tool B → A's inputs are not carried into B.

### 3b. Reformatter (XLSX/CSV → TSV)
- [ ] LAB-04 — Upload an `.xlsx` (or odd-delimiter CSV). Tool reads sheet names / detects format.
- [ ] LAB-05 — Convert → produces downloadable TSV(s). Download works; file opens as clean tab-separated.
- [ ] LAB-06 — No data sent anywhere external (conversion is server-side; nothing in terminal suggests a network call).

### 3c. ID Reconciliation (single-key pairwise matching)
- [ ] LAB-07 — Load two files each with an ID column; pick the key column on each side.
- [ ] LAB-08 — Exact matches are detected and shown in a match table (certainty 1.0 for exact).
- [ ] LAB-09 — When IDs don't line up (e.g. `sample_001` vs `001`), the tool **suggests a transformation** (prefix/suffix strip, delimiter extract, case-normalise).
- [ ] LAB-10 — Apply a suggested pattern → match count increases; remaining unmatched fall to fuzzy (rapidfuzz) with <1.0 certainty.
- [ ] LAB-11 — Save the **id transformation** as YAML → downloads; reload it back into the tool → same steps restored (round-trip).
- [ ] LAB-12 — Many-to-many ID collisions are flagged (not silently joined).
- [ ] LAB-13 — Boundary check: composite/multi-key reconciliation is **out of scope** here — confirm the tool only offers single-key (no composite-key UI). *(That belongs in BLUEPRINT Joint Designer.)*

### 3d. Data analysis recipe Scaffolding (boilerplate ZIP)
- [ ] LAB-14 — Upload one or more data files; tool infers structure and produces a **boilerplate data analysis recipe ZIP** (basename-mirroring dirs).
- [ ] LAB-15 — Generated data analysis recipe has: `id`/`info`, `data_schemas` with inferred `input_fields` types, empty `tier1: []`/`tier2: []` stubs, `joins: {}` stub, PK-candidate **hints as comments** (e.g. `# Candidate PK: sample_id (100% unique)`).
- [ ] LAB-16 — Generated data analysis recipe does **NOT** invent `analysis_groups`, plot specs, or `final_contract` (those are BLUEPRINT's job). Confirm they're absent.
- [ ] LAB-17 — The generated boilerplate **loads cleanly** (no ConfigManager error) when selected as a data analysis recipe in HOME, or via the import path. *(This is the key correctness gate — old Bootstrapper wrote `plotting:` instead of `analysis_groups:`; confirm that's fixed.)*
- [ ] LAB-18 — If ID Reconciliation was run this session, Scaffolding offers an **opt-in checkbox** to bake those reconciliation steps into `tier1:`. With it off, scaffolding still works fully standalone.

### 3e. Anonymiser
- [ ] LAB-19 — Load a TSV with identifying columns; run anonymisation → produces an **anonymised TSV + a mapping TSV** (both downloadable).
- [ ] LAB-20 — Same original ID → same anonymised ID **within the file**; types/value-ranges remain plausible.
- [ ] LAB-21 — Multi-file: the output documents how to keep IDs consistent across files (recommends reconciling first; advisory, never blocking).

### 3f. AquaSynthesizer (synthetic data)
- [ ] LAB-22 — Generate **demo** synthetic data from a schema → downloadable TSV + a `synthetic_data_config` YAML.
- [ ] LAB-23 — The config YAML's first two lines are the mandatory header (`# NOT a pipeline data_analysis_recipe...`) and root key `synthetic_data_config:`. *(Firewall — it must not be mistaken for a data analysis recipe.)*
- [ ] LAB-24 — **stress_test** mode injects errors (nulls/dupes/edge cases) per the config.
- [ ] LAB-25 — Save a **named scenario** → reload it → all fields match (round-trip).
- [ ] LAB-26 — Loading a synthetic config via the normal data analysis recipe path is **rejected/ignored** (not processed by the data engine).

### 3g. TEST_LAB audit & isolation
- [ ] LAB-27 — File-generation operations log what was produced (filename, schema, row count) to the notification/audit log.
- [ ] LAB-28 — Closing the browser tab / refreshing loses in-progress (unsaved) work but keeps explicitly-saved files. No ghost-save in TEST_LAB.

---

## 4. BLUEPRINT (BLU) — visual data analysis recipe IDE (mostly new since Phase 26)

> Config file: `developer.yaml` or `qa.yaml` (full edit mode); `standalone.yaml` gives the non-edit subset (`data_analysis_recipe_edit_enabled: false`). Click **Blueprint Architect** nav pill.
> Design: `.claude/design/spaces/BLUEPRINT.md`. Feature lock: ADR-082. Rules: `rules_ui_dashboard.md §7`.
> **Reality-check note:** BLUEPRINT had known build-gaps as of 2026-05-20 (add-node primitive UI, component/plot forms, group/meta/new-data_analysis_recipe/validate were YAML-only); several closed in Phase 32–33. Where a feature is simply **absent**, mark `[b]` and note it — discovering the doc/reality gap is itself a useful result, not a failure.

### 4a. Navigation layer (TubeMap + Lineage + contract viewer)
- [ ] BLU-01 — Center switches to the **TubeMap** DAG; nodes render (Cytoscape, vendored — works offline).
- [ ] BLU-02 — TubeMap is collapsible to free workspace.
- [ ] BLU-03 — Right sidebar header changes to **"Blueprint Surgeon"** (or current name); shows "No node selected" until a node is clicked. *(carried: old §11 — styling should be homogenised with the Audit panel, see CSS-04.)*
- [ ] BLU-04 — Click a TubeMap node → right sidebar shows "Focused: `<node_id>`" + its logic-stack step count; the 3-column contract viewer (input → wrangling → output) populates.
- [ ] BLU-05 — Lineage Rail: from a selected node you can trace its lineage back toward the source.
- [ ] BLU-06 — Switch to Home and back → BLUEPRINT keeps its own selected-node state (panel independence).

### 4b. Forms layer (action picker + parameter forms)
- [ ] BLU-07 — Action **picker** opens; is searchable; filters to actions valid for the selected node's position (T1/T2/assembly/plot).
- [ ] BLU-08 — Selecting an action renders a **parameter form** (dropdowns, column pickers, value inputs) — no raw YAML typing required for the action params.
- [ ] BLU-09 — Editing an existing node's params via the form and re-applying updates the node; the live preview reflects it (see 4c).
- [ ] BLU-10 — Help panel: an action shows its `description` + `yaml_example` (BP-HELP). Note any action with blank help.
- [ ] BLU-11 `[b]?` — Add-node UI vs edit-node form: confirm whether add-node now uses the rich form or still the primitive UI (known gap BP-FORMS-UNIFY-1). Report what you see.
- [ ] BLU-12 `[b]?` — Plot/component node configuration via form (known gap — only a few components schemed). Report whether plot nodes are form-configurable or YAML-only.

### 4c. Joint Designer (joins — BP-JOINT-1)
- [ ] BLU-13 — Dedicated **Joint Designer** tab/pane exists in the center theater.
- [ ] BLU-14 — Left + right ingredient schemas show side-by-side; you can pick the join key column(s).
- [ ] BLU-15 — **Live key-match preview** on real data: shows overlap stats (materialises each ingredient; String-cast key overlap). Numbers look sane for the test data.
- [ ] BLU-16 — Composite (multi-column) keys are supported here (unlike TEST_LAB).
- [ ] BLU-17 — Apply is **comment-gated** (needs a justification) and emits a canonical `join` step (`on:` symmetric / `left_on`+`right_on` asymmetric).
- [ ] BLU-18 — Selecting an existing join node pre-fills the designer for editing.

### 4d. Data view layer (live preview)
- [ ] BLU-19 — "Preview on Apply": after applying a node change, a data **glimpse** (table) + plot update in the center stack. Not live-on-every-keystroke (push model).
- [ ] BLU-20 — Preview uses real orchestrator execution (values are real, not placeholder).

### 4e. Helpers layer (escape hatch · undo · branch · AI agent)
- [ ] BLU-21 — **YAML escape hatch** visible. For `developer.yaml`/`qa.yaml` it's an **editable** textarea (`data_analysis_recipe_edit_enabled: true`); for other config files it's **read-only**. Confirm the right mode for the file you launched.
- [ ] BLU-22 — Editing YAML in the escape hatch and saving emits a change the rest of the IDE reflects (and, per design, a `developer_raw_yaml` node).
- [ ] BLU-31 **NEW (2026-11-08, never live-tested)** — Break the YAML in the escape hatch on purpose (delete a colon, mis-indent) and Save: the error shows **inline, right in the escape hatch panel** — problem + a "Fix" line — not just a generic toast in the corner. Then separately: pick a data analysis recipe whose file set includes a deliberately broken `!include` target (or temporarily rename one), load it in BLUEPRINT: a similar inline error appears at the top of the "Master data analysis recipe" panel (`bp_import_error_ui`), not just a toast. Both clear once you fix the underlying problem and retry.
- [ ] BLU-23 — **Undo**: make several node changes → undo steps back through them (up to 20). Redo if present.
- [ ] BLU-24 — **Branch** (lineage bifurcation at a node): split a lineage so upstream stays shared and the child diverges as a new `!include` fragment. Confirm it does **not** duplicate the whole data analysis recipe. *(Canonical example: Summary vs Summary_quality.)*
- [ ] BLU-25 — **AI agent** chat panel present (developer/qa). Send a plain-language request ("add a step to filter identity ≥ 90"). It responds; it **advises, never blocks**. Note backend status (it uses `claude_cli`; if not authed it should degrade gracefully to a disabled banner, not crash).
- [ ] BLU-26 — Agent respects scope: it proposes data analysis recipe structure / actions that actually exist in the loaded libraries (doesn't hallucinate unregistered actions).

### 4f. Save / load
- [ ] BLU-27 — Save the data analysis recipe → writes YAML to disk and/or downloads. The saved file is valid and reloads.
- [ ] BLU-28 — A data analysis recipe saved from BLUEPRINT can be selected and **run in HOME** end-to-end.
- [ ] BLU-30 **NEW (from issue [#9](https://github.com/evezeyl/SPARMVET_VIZ/issues/9), ADR-089)** — Edit a file of the data analysis recipe in BLUEPRINT (an included wrangling or step list fragment), save, then reload Home: the new rows appear **without restarting the server** (Tier 1 parquet rebuilt when the change is in Tier 1; only Tier 2 recomputed when the change is in a Tier 2 step). Test while testing BLUEPRINT, together with BLU-09 and BLU-28. *(The cache rules are also covered by `app/tests/test_cache_chain.py`; the BLUEPRINT click-through is still yours.)*
- [ ] BLU-29 `[?]` — Join-component save: confirm the `on:` key is correctly quoted in saved YAML (known serialization risk — `on` is a YAML boolean trap). If a saved join reloads with `True` as a key, that's a `[!]`.

---

## 5. HOME — moved to its own file

See [`test_plan_home_2026-11.md`](test_plan_home_2026-11.md). Tested first, by itself, before
anything in this file. All `HOM-*`, and the HOME-relevant `REG-*`/`CSS-*` items, live there now.

---

## 6. GALLERY (GAL) — example browser (re-verify)

> Config file: `standalone.yaml`, `developer.yaml`, or `qa.yaml` (all set `gallery_enabled: true`). Click **Gallery** nav pill. Mature space — lighter pass.

- [ ] GAL-01 — Gallery loads: example browser in center; left sidebar shows Example selector + collapsible taxonomy filters (Family / Data Pattern / Difficulty).
- [ ] GAL-02 — Taxonomy filter choices come from `gallery_index.json` (not hardcoded); "Select all" toggles a group's checkboxes; "Apply" filters the example list.
- [ ] GAL-03 — Click a data analysis recipe card → center shows its preview PNG + guidance (Visual Cookbook) panes; both accordions collapse/expand independently.
- [ ] GAL-04 — Example shows: description, required columns, raw data analysis recipe YAML; YAML is copyable (the GALLERY→BLUEPRINT handoff is copy-paste, per design — no direct "send to").
- [ ] GAL-05 — Taxonomy tag strip renders (`📊 Family · 🔢 Pattern · 📈 Difficulty …`).
- [ ] GAL-06 `[~]` — **(carried, old §12)** The example-title icons should use the **same** icon set as the taxonomy tag strip, fetched when the taxonomy auto-populates the sidebar (consistency). Confirm; if mismatched, `[~]`.
- [ ] GAL-07 `[~]` — **(carried, old §12)** "Select all" row still has a slightly large gap below it. Low priority.
- [ ] GAL-08 — Click Home → returns to plots; left sidebar tools reappear; selected data analysis recipe preserved.
- [ ] GAL-09 `[b]` — Search, community contribution/request, "Open in BLUEPRINT" — **not built** (per GALLERY.md). Confirm absent; don't fail.

---

## 7. Cross-space workflow (XSP) — the producer arc

> Tests the file-based handoffs (export here → choose there). There are **no in-app "send to" buttons** by design — handoffs are deliberately file-based so spaces stay independently flag-gated. Use **developer/qa**.

- [ ] XSP-01 — TEST_LAB Scaffolding ZIP → load that data analysis recipe in BLUEPRINT → it opens and is editable.
- [ ] XSP-02 — TEST_LAB Reformatter TSV → use it as input to ID Reconciliation (choose the file) → works as any standalone input.
- [ ] XSP-03 — Gallery examples YAML (copied) → paste into BLUEPRINT escape hatch → it parses.
- [ ] XSP-04 — BLUEPRINT saved data analysis recipe → appears in HOME's data analysis recipe selector → runs.
- [ ] XSP-05 — Anonymiser anon-TSV + mapping-TSV → can be re-joined (de-anonymised) following the printed step list.
- [ ] XSP-06 — Confirm there is **no** cross-space coupling: disabling a space's flag never strands another space's output (the artifact is a file on disk).

---

## 8. Regression & legacy guards — HOME items moved

All of `REG-01` through `REG-10` were HOME-observed and moved to
[`test_plan_home_2026-11.md`](test_plan_home_2026-11.md) §9. Non-HOME regression items (if any
surface while testing TEST_LAB/BLUEPRINT/GALLERY) get added here as they're found.

---

## 9. Aesthetic / CSS homogenisation backlog — HOME items moved

All of `CSS-01`, `CSS-05`, `CSS-06`, `CSS-07` were HOME-observed and moved to
[`test_plan_home_2026-11.md`](test_plan_home_2026-11.md) §10. `GAL-06`/`GAL-07` (Gallery's own CSS
carries) stay in §6 below, unaffected by the split. Authoritative palette/scale:
`rules_css_style_spec.md`.

---

## 10. Re-check with a real data analysis recipe (REAL)

> The shipped test data analysis recipes use dummy data, so some plots look odd (for example after a valid Data Import, HOM-34). Repeat these checks with a real data analysis recipe and real data before the demo.

- [ ] REAL-01 — Repeat HOM-34 to HOM-36 (Data Import) and look at the redrawn plots: do they look right with real data?
- [ ] REAL-02 — Check jitter plots (seed written as a number, then `random`), and the row order of axes and legends (ADR-090).
- [ ] REAL-03 — Check the export (HOM-46): the data analysis recipe and the record state the data actually used.
- [b] REAL-04 — (was: check the Plot Style panel on a real plot.) The panel is off in HOME, so there is nothing to check until it is brought back (HOM-47, issue [#15](https://github.com/evezeyl/SPARMVET_VIZ/issues/15)).

---

## Appendix A — Known gaps / not-expected-to-work (don't fail these)

These are designed-but-unbuilt or deferred; mark `[b]` if you wander into them:

- GALLERY: search, community contribute/request, "Open in BLUEPRINT" (GALLERY.md).
- BLUEPRINT: unified add-node form, full plot/component forms, inline validate, new-data-analysis-recipe-from-scratch UI, lineage isolation (v2) — some may have landed in Phase 32–33; report what you find.
- HOME: T3 `aesthetic_override` render path (VIZFAC-T3-OVERRIDE-1), plot-panel collapse (THEATER-1).
- Maps / flow / network chart types (deferred — MAP-A-* in progress, not in default data analysis recipes).
- Galaxy / IRIDA deployment paths (23-C/D/E — backlog).

## Appendix B — When something fails (reminder)

1. Note the **item ID** + what you saw vs expected.
2. Flip the box to `[!]`/`[~]`/`[?]` and add one `> EVE:` line. Screenshot path / terminal snippet welcome.
3. Don't fix inline. Ping me; I grep §0.5, fix, stamp `RETEST ↻`.

## Appendix C — Reference docs

- `.claude/design/spaces/{HOME,BLUEPRINT,GALLERY,TEST_LAB}.md` — space specs
- `.claude/design/developer_workflow.md` — the cross-space producer arc (§7 here)
- `.claude/rules/rules_app_features_flags.md` — authoritative app features matrix (§2 here)
- `.claude/rules/rules_ui_dashboard.md`, `ui_implementation_contract.md` — UI contract
- `.claude/rules/rules_css_style_spec.md` — palette/typography (§9 here)
- `.claude/knowledge/architecture_decisions.md` — ADRs (082 BLUEPRINT lock, 084 TEST_LAB, 073 sidebar, 071 positive inclusion)
</content>
</invoke>
