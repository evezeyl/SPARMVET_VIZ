# SPARMVET_VIZ — Live App Test Plan

**Owner:** @evezeyl (tester) · @dasharch (fixer)
**Created:** 2026-06-19
**Baseline:** `dev` branch @ Phase 34 (TEST_LAB built, BLUEPRINT full feature set, legacy removals, 8 app features files)
**Supersedes:** [`tasks_test_ui_current.md`](tasks_test_ui_current.md) (pinned to Phase 26 — stale; its still-open items are folded in here, see each `(carried)` tag)
**Scope:** All four user spaces (HOME · BLUEPRINT · GALLERY · TEST_LAB) + configuration-file gating + cross-space workflow + regressions. Comprehensive, but **prioritised** — see §0.4.

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

You don't have to do it all at once. Recommended path:

1. **§1 Launch** (must pass before anything else)
2. **§3 TEST_LAB** — brand new in Phase 34, never live-tested → highest payoff
3. **§4 BLUEPRINT** — mostly new since Phase 26 (forms, joint designer, escape hatch, undo, branch, AI agent)
4. **§5 HOME** — mature but on a stale baseline; re-verify core + new palette/cascade/apply UX
5. **§6 GALLERY** — mature; lighter re-verify
6. **§2 Configuration-file gating** — quick, can be done any time
7. **§7 Cross-space**, **§8 Regression**, **§9 CSS backlog** — last

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

---

## 1. Launch & environment (PRE)

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

> **Verified working launch command** (boots to HTTP 200; checked 2026-06-19):
>
> ```bash
> cd /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
> PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/developer.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
> ```
> Then open <http://127.0.0.1:8000>. `--reload` auto-restarts on code edits (useful during fix rounds).
> **Note:** `python app/src/main.py` does **not** start a server (that file only prints banners) — the old checklist's launch line was wrong. Use `shiny run`.

> **Switching config file = relaunch** pointing `SPARMVET_APP_FEATURES` at a different file. There is **no** in-app selector. All 8 files live in `config/app_features/` — full launch command per file in §2.

- [~] PRE-01 — App boots clean (no Python traceback); browser console had 1 real bug + 2 noise items, 1 fixed. → [20260810_testing_part1.md#pre-01](20260810_testing_part1.md#pre-01-console-errors-on-first-launch) — RETEST ↻
- [ ] PRE-02 — Browser loads at :8000 with no red error banner on first paint.
- [ ] PRE-03 — Default data analysis recipe **ST22 Dummy Dataset** loads; center theater shows analysis-group tabs (Quality Control · Curiosity · Results · Cat 🐱).
- [ ] PRE-04 — Relaunch pointing at `config/app_features/qa.yaml` → terminal shows `App features: config/app_features/qa.yaml`; app still boots clean. (qa's flags: everything on, `ghost_save: false`.)
- [ ] PRE-05 — Switch data analysis recipe in the **Data analysis recipe Choice** sidebar dropdown to `2_test_data_ST22_dummy` → tabs change to AMR Profiling Insight · Plasmid Dynamics; plots reload, no traceback.

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

## 5. HOME (HOM) — analysis space (re-verify + new)

> Config file: `developer.yaml`, `qa.yaml`, `standalone.yaml`, or `pipeline-exploration-advanced.yaml` for full surface (all four set `t3_sandbox_enabled: true`).
> Most of this passed at Phase 26 but on a stale baseline — re-verify the core, then test the genuinely-new palette/cascade/apply-UX items (marked **NEW**).
> EVE: user facing template for testing is `developer.yaml`, data analysis recipe choice is 1_test_data_ST22_dummy

### 5a. Tabs, plots, preview (core)
- [x] HOM-01 — Group tabs = data analysis recipe `analysis_groups` (Quality Control · Curiosity · Results · Cat 🐱). No hardcoded tabs.
  > EVE: ok - tested by changing data analysis recipe and observing changes in analyses groups
- [x] HOM-02 — Each tab's plots render as static images; multi-plot groups expose plot **sub-tabs**.
  > EVE: ok
- [x] HOM-03 — **Data Preview** accordion below the plot shows ~100 rows of the active plot's dataset; updates on sub-tab switch.
  > EVE: ok
- [x] HOM-50 — The AMR heatmap (Results, `amr_heatmap`) draws, coloured by `predicted_phenotype`. Eve 2026-11-05. [#13](https://github.com/evezeyl/SPARMVET_VIZ/issues/13). *(Automated: all plots of the test data analysis recipes render, `app/tests/test_render_every_plot.py`.)*
- [x] HOM-04 — (superseded, 2026-11-05) The old header strip (dataset label + tier radios) no longer exists: it is now the two-row strip of HOM-45 (ADR-086). The follow-ups it raised are HOM-40 to HOM-43, all done. → [20260810_testing_part1.md#hom-04-follow-ups](20260810_testing_part1.md#hom-04-follow-ups-tier-toggle--audit-scope-2026-08-10).
- [x] HOM-37 — "All rows" toggle in Data Preview blanks the table entirely, no error shown. → [20260810_testing_part1.md#hom-37](20260810_testing_part1.md#hom-37--all-rows-toggle-blanks-the-data-preview-table-bug) — needs a terminal traceback to root-cause, see note. [#1](https://github.com/evezeyl/SPARMVET_VIZ/issues/1)
> EVE: this was an error - all rows are showing correctly when toogle activated (can be delay if many rows). BUT the message is not clear - we need to know if it shows only a portion of the data or all the data. Would be nice to indicate data dimension of the full dataset that is shown (and when preview only - not all rows to know that is max first 100) 
  > Merged into HOM-39 — same underlying ask (row-count clarity).
- [x] HOM-38 — The word "Plot" in the plot panel header is blanked (redundant). Retested by Eve 2026-11-05 (open and collapse, single and Compare). [#16](https://github.com/evezeyl/SPARMVET_VIZ/issues/16) → [20260810_testing_part1.md#hom-38](20260810_testing_part1.md#hom-38--redundant-plot-accordion-title-above-each-plot)
- [x] HOM-39 — Data Preview doesn't make the 100-row cap clear to the user; the total row count of the underlying table isn't shown anywhere, and (per HOM-37) it should also be clear whether "All rows" is showing a portion or everything. → [20260810_testing_part1.md#hom-39](20260810_testing_part1.md#hom-39--data-preview-100-row-cap-not-communicated) [#1](https://github.com/evezeyl/SPARMVET_VIZ/issues/1)
- [x] HOM-41 — **FIXED**: committed T3 audit filters/column-drops no longer leak into T1/T2. → [20260810_testing_part1.md#hom-41](20260810_testing_part1.md#hom-41--t3-audit-nodes-leak-into-t1t2-reference-views-confirmed-bug)
- [x] HOM-40 — A "Viewing: Raw / Result / My view" badge shows above each plot and in the Data Preview header, with "T2=T1" and "T3=T2" notes (the badge is not in the plot image, so not exported). Retested by Eve 2026-11-05. [#17](https://github.com/evezeyl/SPARMVET_VIZ/issues/17) → [20260810_testing_part1.md#hom-40](20260810_testing_part1.md#hom-40--no-explicit-viewing-tier-x-indicator)
- [x] HOM-42 — **DECIDED**: covered by the "Compare" choice of **Plot to show** (T2 on the left, My view on the right), ADR-086, [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3). A one-line My view summary under the plot may follow later. — RETEST ↻
- [x] HOM-43 — **FIXED**: Apply (exploration, every tier) and Send to Audit (T3-only, permanent) are now two distinct buttons instead of one that changed meaning by tier. → [20260810_testing_part1.md#hom-43](20260810_testing_part1.md#hom-43--t3-mode-has-no-exploration-only-filter-path) — RETEST ↻

### 5b. Tier toggle
- [x] HOM-05 — **Data to show** Raw → Result on `year_distribution` (AMR and Virulence group): the data preview shows all years on Raw and only 2023–2025 on Result. The plot does not change when you switch Raw/Result (plots never show T1, ADR-086). [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3) — RETEST ↻
- [x] HOM-06 — My view (advanced+): Apply always explores; **"Send to Audit" appears when either "Plot to show" or "Data to show" is on My view** (and `t3_sandbox_enabled`); right sidebar Pipeline Audit shows Tier 2 (inherited) + Tier 3 (my adjustments) once something is committed. See HOM-43, ADR-085/086. [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3) — RETEST ↻
- [ ] HOM-07 — Changing **Data to show** (T1→My view→T1) keeps the active plot sub-tab. *(carried: old §4c.)*
- [ ] HOM-08 — Home→Gallery→Home **restores** the previously active group tab + sub-tab + tier. *(carried: old §4c had two boxes left unchecked — verify on current build.)*
- [ ] HOM-44 `[!]` — On `year_distribution` (data analysis recipe "1_test_data_ST22_dummy", AMR and Virulence group), the Year axis renders discrete on T2 but continuous on T3/My view — same data, should look the same. → [20260810_testing_part1.md#hom-44](20260810_testing_part1.md#hom-44--year-axis-discrete-on-t2-but-continuous-on-t3my-view) — low urgency per EVE. Reproduced 2026-11-05: the axis turns continuous when the filter is on the year column itself (draft `issue-drafts/003_year-axis-continuous-in-my-view.md`).
- [x] HOM-45 **NEW** — Header strip (ADR-086): two labelled rows "Plot to show" (Result / My view / Compare) and "Data to show" (Raw / Result / My view), defaults both Result. Plot choice affects only plots, data choice only the data preview/table. Compare absent when `comparison_mode_enabled` is false. Strip absent when `interactivity_enabled` is false. [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3) — RETEST ↻

### 5c. Filters (T1/T2)
- [ ] HOM-09 — String column: operators are `=` / `≠` / `∈ any of` / `∉ none of` (no `between`). Add row → staged; Apply → preview + plot update; Reset clears.
- [ ] HOM-10 — Numeric column: operators include `↔ between` → two lo/hi inputs; inclusivity radios read `≤ inclusive` / `< exclusive` (single symbol).
- [ ] HOM-11 — Int column shows integer default (`2022` not `2022.0`), step = 1.
- [ ] HOM-12 — Multiple staged rows AND together; removing one updates the count and result.
- [ ] HOM-13 `[?]` — **(carried, old §5b)** Filter selectize choices are **not** refreshed after Apply (excluded values still show in the picker). Decision: refresh choices from filtered data (cleaner) vs keep all so you can add filters back without Reset. Your call.

### 5d. T3 audit (advanced+) — the reproducibility core
- [ ] HOM-14 — Build a filter on a non-key column → `➜ Audit (1)` → **propagation modal** ("choose scope", no PK warning). Pick "This plot only" → pending yellow node with required reason input.
- [ ] HOM-15 — Apply is **blocked** until the reason is non-empty; once filled, Apply commits; notification confirms; plot + preview reflect it; **other sub-tabs unaffected** (per-plot scoping).
- [ ] HOM-16 — Filter on a **primary-key** column → modal shows ⚠️ PK warning; node renders with the PK-warning banner; operator is preserved verbatim (no silent flip to exclusion).
- [ ] HOM-17 — "All plots" scope → node copied to every plot's stack (same id); "All plots except…" → multiselect excludes chosen plots.
- [ ] HOM-18 — Drop a non-key column via the Data-Preview column selector → `➜ Audit drops (1)` → drop_column node; reason required; applies; column gone for this plot only.
- [ ] HOM-19 — Attempt to drop a **join-key** column → blocked with a red "cannot drop join key" notification; no node added.
- [ ] HOM-20 — Delete a committed node (🗑) → removed across all plots it was propagated to; data reverts.
- [ ] HOM-21 `[~]` — **(carried, old §10)** Primary-key concept is unfamiliar to non-CS users. Add a short, plain-language hover/tooltip when filtering/removing a PK ("this is the column that links your tables; removing rows here changes what appears everywhere"). Confirm whether any such hint exists today; if not, mark `[~]` for me to add. Longer doc-page welcome too.

### 5e. NEW — palette / plot-config cascade / apply UX
- [ ] HOM-22 **NEW** — If a data analysis recipe declares `plot_defaults.palette` or a per-plot `palette:`, plots render in that palette. Switching data analysis recipes changes palette accordingly.
- [b] HOM-23 `[b]` **(blocked since 2026-11-05: the Plot Style panel is not shown in HOME, issue [#15](https://github.com/evezeyl/SPARMVET_VIZ/issues/15); no authoring path)** **NEW** — `aesthetic_override` (T3 plot colour/fill/alpha/shape), **if an authoring path exists**, actually changes the rendered plot (not just recorded). If there's no UI to author it yet, mark `[b]` (VIZFAC-T3-OVERRIDE-1 may still be pending).
- [b] HOM-47 — **Plot Style panel: decided 2026-11-05.** The panel (right sidebar of HOME, added 2026-05-11, commit fa5a78d) is the authoring UI of the T3 `aesthetic_override` (ADR-082). Using it broke the plot, and letting users change in HOME what the data analysis recipe defines is too much for now. **Decision (Eve):** the panel is **not shown in HOME**; its code is kept, unused, with a pointer comment at the mount point (`home_theater.py`); BLUEPRINT and ADR-082 are unchanged. It stays an **eventual enhancement** ([#15](https://github.com/evezeyl/SPARMVET_VIZ/issues/15), task UX-PLOTSTYLE-1 deferred), when we will also find why it broke the plot. Plot style that belongs to the data analysis recipe is a separate, later BLUEPRINT matter. Related: HOM-23 (blocked: no authoring path). Check: no "Plot Style" in the right sidebar (verified in a browser on 2026-11-05).
- [ ] HOM-24 **NEW** — Apply-button UX improvements (UX-APPLY-IMPROVE-1, Phase 34): confirm the apply/pending states read clearly (disabled reason, pending badge). Note anything confusing.
- [ ] HOM-25 — Integer axis breaks: `year_distribution` x-axis shows whole years (`2018`…`2025`), no `.0`; survives T1↔T2 toggling; no `MaxNLocator` traceback.

### 5f. Session management (advanced+)
- [ ] HOM-26 — Open Session Management; commit ≥2 T3 nodes across plots; save a named session.
- [ ] HOM-27 — Restart app → session ghost auto-restores (or via "Restore"); committed T3 nodes reappear in their per-plot panels.
- [ ] HOM-28 — Export Active Session (.zip) downloads the full session dir.
- [ ] HOM-29 `[~]` — **(carried, old §14)** Show "Last auto-save: <timestamp>" in the Session Management panel so the user knows the ghost-save fired. Confirm if present; if not, `[~]`.
- [ ] HOM-30 `[?]` — **(carried, old §14)** During the auto-save window, "Export Active Session" should either be disabled or trigger a save first (avoid exporting a stale/partial session). Decide the behaviour.

### 5g. Export bundle
- [ ] HOM-31 — Export panel: set a bundle label, pick format (PNG/SVG/PDF), pick scope (global / group / plot), click Export → `.zip` downloads.
- [ ] HOM-32 — Bundle contains `plots/`, `data/` (T1+T2; T3 when advanced+T3 active), `data_analysis_recipes/`, `report.qmd` (with a **T3 Audit Trail** section when T3 nodes exist), `README.txt`. Filters present → `FILTERS.txt` included ("no trace, no export").
- [ ] HOM-33 — `report.qmd` front-matter records data analysis recipe id + sha; methods text reads in plain English from active T3 nodes; PK-touching nodes carry the ⚠️ marker.
- [ ] HOM-46 `[?]` **NEW (note from Eve, 2026-11-05)** — Export after an audit: the exported data analysis recipe must state **the data actually used**, not the default data. Check with a deployment that has `prefer_discovery: true` (data delivered into `raw_data`) and after a Data Import. Suspected gap: the bundle's `data_analysis_recipes/` holds a verbatim copy of the data analysis recipe, which still shows the default `source.path`, while the README/report list the data really used (`data_source_paths`). Decide how the bundle states which data was used. [ADR-088 point 5](../knowledge/architecture_decisions.md)

### 5h. Data Import (advanced+/independent)
- [x] HOM-34 — **Files: [`assets/test_uploads/`](../../assets/test_uploads/README.md) (`FastP_valid_changed.tsv`); restore afterwards with `git restore assets/test_data/`.** Data Import accordion: upload a TSV matching a schema → assignment table appears with the right dataset id pre-selected → Apply → plots reload, no traceback.
- [x] HOM-35 — **Files: `assets/test_uploads/FastP_error_*.tsv` (4 files, expected result for each in its README).** Upload a file with wrong columns → per-file validation error (missing/mistyped columns); no data written, cache not busted.
- [x] HOM-36 — **Files: `FastP_valid_changed.tsv` + `Bracken_valid_changed.tsv`.** Multi-file (Ctrl/⌘-select two) → independent dataset dropdowns; both apply.
- [x] HOM-48 — **Files: `FastP_gap_text_in_numeric_column.tsv`.** Text in a numeric column is rejected at import with the column and the value named ("column 'total_reads' (numeric): 'abc'"); nothing is written; valid files still import. Eve 2026-11-05. [#11](https://github.com/evezeyl/SPARMVET_VIZ/issues/11)
- [x] HOM-49 — The message for a rejected import file is readable (banner, normal text size, hint on its own line). Eve 2026-11-05. [#14](https://github.com/evezeyl/SPARMVET_VIZ/issues/14)
- [x] HOM-51 — Rename a column header of a test data file (then `git restore assets/test_data/`) and open Home: it says "Data Assembly Failed" with the dataset and the reason, not a silently wrong plot. Eve 2026-11-05. [#18](https://github.com/evezeyl/SPARMVET_VIZ/issues/18)

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

## 8. Regression & legacy guards (REG)

> Quick confirmations that previously-fixed bugs stay fixed and Phase-34 legacy removals didn't break the happy path.

- [ ] REG-01 — STATE-1: no plot flicker on T3 toggle / panel switch.
- [ ] REG-02 — STATE-2 / AUDIT-4: comparison T2/T3 toggle stays on the correct plot after a sub-tab switch.
- [ ] REG-03 — UX-1 / BUG-PERF-1: plot rendering is reasonably fast; terminal shows `materialize_tier1` only on cache miss, not repeatedly. *(Also covered by automated tests since 2026-11-05: `app/tests/test_cache_chain.py`, `test_cache_keys.py`. The browser check is still yours.)*
- [ ] REG-04 `[~]` — **(carried, old §17 UX-2)** "Visible columns" multiselect in Data Preview is narrower than its panel. Confirm; `[~]` if still present.
- [x] REG-05 — **Plot to show** → Compare (advanced+): two panes, left labelled "T2 — Result (Reference)", right "My view"; on `year_distribution` both show only the T2 years (2023–2024) until a filter is applied. Back to Result → single plot. No stale compare state after leaving My view. [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3) — RETEST ↻
- [ ] REG-06 — Notification log (`🔔 Alerts (N)`) in right sidebar: actions append newest-first with timestamps + colour; max 20 kept; persists across nav within a session.
- [ ] REG-07 — Sidebar collapse: hide left sidebar → content fills width → re-show works after several cycles. *(carried: old §12 sidebar — left untested at Phase 26.)*
- [ ] REG-08 — **Critical (carried)**: hide **both** sidebars (advanced+) → both toggles remain clickable → each sidebar can be re-expanded independently.
- [ ] REG-09 — Legacy-removal smoke: the default data analysis recipes load and render without `ConfigurationError`/`TransformationError` (Phase 34 removed flat `plots:`, `string`/`character` type aliases, flat `wrangling:` lists — none of the shipped data analysis recipes should trip these). *(Also covered by automated tests since 2026-11-05: `app/tests/test_render_every_plot.py` renders all 15 plots of 3 data analysis recipes, `test_data_analysis_recipe_validator.py`, `test_data_analysis_recipe_data_check.py`. The browser check is still yours.)*
- [~] REG-10 — Duplicate Shiny IDs (`notification_log_accordion`/`notification_log_panel_ui`) at launch. → [20260810_testing_part1.md#reg-10](20260810_testing_part1.md#reg-10--duplicate-shiny-ids-notification_log_accordion--notification_log_panel_ui) — root-caused + fixed, RETEST ↻

---

## 9. Aesthetic / CSS homogenisation backlog (CSS)

> Eve's carried-over styling consistency items. Low urgency, batch-fixable. Authoritative palette/scale: `rules_css_style_spec.md` — I'll fix against that, not invent values.

- [ ] CSS-01 `[~]` — **(carried, old §6/§10)** Trash/bin button in **filter** staged rows must match the trash/bin in the **audit** panel (same `btn-link` red style). Re-confirm they're identical on the current build.
- [ ] CSS-05 — Free-find: while testing, note any colour/spacing/font that looks off-palette (Bootstrap blue `#0d6efd`, success green, etc.) with the panel name — I'll reconcile against the style spec.
- [x] CSS-06 — "All rows" switch not aligned with "Data Preview" label in the Data Preview accordion header. → [20260810_testing_part1.md#css-06](20260810_testing_part1.md#css-06--all-rows-switch-not-aligned-with-data-preview-label) [#2](https://github.com/evezeyl/SPARMVET_VIZ/issues/2).
- [x] CSS-07 — **Covered** by the "Compare" choice (sub-label "Result vs My view") in the **Plot to show** row, ADR-086, [#3](https://github.com/evezeyl/SPARMVET_VIZ/issues/3). Check that the strip reads well: two aligned rows, labels not truncated. — RETEST ↻

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
