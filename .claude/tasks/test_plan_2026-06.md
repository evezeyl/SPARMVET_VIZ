# SPARMVET_VIZ — Live App Test Plan

**Owner:** @evezeyl (tester) · @dasharch (fixer)
**Created:** 2026-06-19
**Baseline:** `dev` branch @ Phase 34 (TEST_LAB built, BLUEPRINT full feature set, legacy removals, 8 personas)
**Supersedes:** [`tasks_test_ui_current.md`](tasks_test_ui_current.md) (pinned to Phase 26 — stale; its still-open items are folded in here, see each `(carried)` tag)
**Scope:** All four user spaces (HOME · BLUEPRINT · GALLERY · TEST_LAB) + configuration-file gating + cross-space workflow + regressions. Comprehensive, but **prioritised** — see §0.4.

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
| `[ ]` | Not yet tested | — | no |
| `[x]` | PASS — works as expected | Eve | no |
| `[!]` | **FAIL** — broken / error / wrong behaviour | Eve | **yes** |
| `[~]` | **POLISH** — works but needs a tweak (styling, wording, UX) | Eve | **yes** |
| `[?]` | **DECISION** — needs a design choice before code | Eve | **yes (discuss)** |
| `[b]` | BLOCKED / not built yet — can't test (note why) | Eve | maybe |
| `[-]` | N/A for this persona/config | Eve | no |

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

---

## 1. Launch & environment (PRE)

> **Architecture note (2026-08-10 — read this before §2):** "Persona" is not a fixed
> enum the app understands — it's just a naming convention for a config file. The
> `SPARMVET_PERSONA` env var is passed straight to `Bootloader.set_persona()`, which
> either resolves a shortname to `config/ui/templates/<name>_template.yaml` **or**
> accepts a direct path to any YAML file (`app/src/bootloader.py:260-276`). What
> actually drives app behaviour is the **flags inside that file** — nothing else.
> So we test **configuration files**, not "personas": §2 below launches each file
> directly and confirms what its flags actually produce, exactly as
> `rules_persona_feature_flags.md`'s own anti-pattern rule says the *app code* must
> do (`bootloader.is_enabled(flag)`, never a persona-name check) — the test process
> should mirror that, not contradict it.

> **Verified working launch command** (boots to HTTP 200; checked 2026-06-19):
>
> ```bash
> cd /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
> PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/developer_template.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
> ```
> Then open <http://127.0.0.1:8000>. `--reload` auto-restarts on code edits (useful during fix rounds).
> **Note:** `python app/src/main.py` does **not** start a server (that file only prints banners) — the old checklist's launch line was wrong. Use `shiny run`.

> **Switching config file = relaunch** pointing `SPARMVET_PERSONA` at a different file. There is **no** in-app selector. All 8 files live in `config/ui/templates/` — full launch command per file in §2.

- [~] PRE-01 — App boots clean (no Python traceback); browser console had 1 real bug + 2 noise items, 1 fixed. → [20260810_testing_part1.md#pre-01](20260810_testing_part1.md#pre-01-console-errors-on-first-launch) — RETEST ↻
- [ ] PRE-02 — Browser loads at :8000 with no red error banner on first paint.
- [ ] PRE-03 — Default manifest **ST22 Dummy Dataset** loads; center theater shows analysis-group tabs (Quality Control · Curiosity · Results · Cat 🐱).
- [ ] PRE-04 — Relaunch pointing at `config/ui/templates/qa_template.yaml` → terminal shows `Persona: config/ui/templates/qa_template.yaml`; app still boots clean. (qa's flags: everything on, `ghost_save: false`.)
- [ ] PRE-05 — Switch manifest in the **Manifest Choice** sidebar dropdown to `2_test_data_ST22_dummy` → tabs change to AMR Profiling Insight · Plasmid Dynamics; plots reload, no traceback.

---

## 2. Configuration-file gating (CFG) — what each file's flags actually produce

Relaunch once per file below and confirm the surfaces it produces. This is fast (just "is it there or not") and catches positive-inclusion (ADR-071) regressions. Authoritative flag matrix: `rules_persona_feature_flags.md`. This section replaced the old persona-framed "PER" checklist on 2026-08-10 — same content, reframed around the actual driver (the file), see the note in §1.

**Launch commands** (paste directly, only the file path changes):

```bash
PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/pipeline-static_template.yaml               ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/demo-vetinst_template.yaml                  ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/pipeline-exploration-simple_template.yaml   ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/web-demo_template.yaml                      ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/pipeline-exploration-advanced_template.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/project-independent_template.yaml           ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/developer_template.yaml                     ./.venv/bin/shiny run app/src/main.py --reload --port 8000
PYTHONPATH=. SPARMVET_PERSONA=config/ui/templates/qa_template.yaml                            ./.venv/bin/shiny run app/src/main.py --reload --port 8000
```

**Compact expectation grid** — confirm each cell against the file's actual flags (`rules_persona_feature_flags.md` full matrix). Mark the row's checkbox `[x]` if the whole row matches, `[!]` if any cell is wrong (note which).

| | pipeline-static | pipeline-exploration-simple | pipeline-exploration-advanced | project-independent | developer | qa |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Filters panel (left) | absent | yes | yes | yes | yes | yes |
| Tier toggle T3 | no | no | yes | yes | yes | yes |
| Right sidebar (Audit) | absent | absent | yes | yes | yes | yes |
| Session Mgmt panel | no | yes | yes | yes | yes | yes |
| Export panel | yes | yes | yes | yes | yes | yes |
| Data Import panel | no | no | yes | yes | yes | yes |
| **Gallery** nav | no | no | no | yes | yes | yes |
| **Blueprint** nav | no | no | no | yes | yes | yes |
| **Test Lab** nav | no | no | no | no | yes | yes |

- [ ] CFG-01 `pipeline-static_template.yaml` — read-only: no Filters, no T3, no right sidebar, no Gallery/Blueprint/Test Lab nav. Export present. *(carried: old PER-01, passed at Phase 26 — confirm still true.)*
- [ ] CFG-02 `pipeline-exploration-simple_template.yaml` — Filters present, no T3, no right sidebar, no Gallery/Blueprint/Test Lab.
- [ ] CFG-03 `pipeline-exploration-advanced_template.yaml` — Filters + T3 + right Audit sidebar; **no** Gallery/Blueprint/Test Lab nav.
- [ ] CFG-04 `project-independent_template.yaml` — adds **Gallery** + **Blueprint** nav; still **no** Test Lab.
- [ ] CFG-05 `developer_template.yaml` — everything incl. **Test Lab** nav.
- [ ] CFG-06 `qa_template.yaml` — same surfaces as `developer_template.yaml` (used for deterministic testing; `automation.ghost_save: false`).
- [ ] CFG-07 `demo-vetinst_template.yaml` — boots; intentionally minimal (most flags off, export off). Confirm no crash and that it looks like a locked-down reference deployment.
- [ ] CFG-08 `web-demo_template.yaml` — boots; minimal-interaction demo. Confirm no crash.
- [ ] CFG-09 — Display name under the nav pills reflects each file's own `display_name` field (not hardcoded, not derived from the filename). *(carried: old PER-09.)*
- [ ] CFG-10 `[?]` **NEW** — Point `SPARMVET_PERSONA` at a **custom** YAML (copy `developer_template.yaml`, flip one flag, e.g. `gallery_enabled: false`, save under a new name) and confirm the app respects it correctly with no code changes. This is the actual proof that behaviour is config-driven, not persona-enum-driven — worth doing once.

---

## 3. TEST_LAB (LAB) — **new in Phase 34, highest priority**

> Config file: `developer_template.yaml` or `qa_template.yaml` (only these two set `test_lab_enabled: true`). Click the **Test Lab** nav pill.
> Design: `.claude/design/spaces/TEST_LAB.md`. Rules: `rules_test_lab.md`.
> **Principle to keep in mind while testing:** every tool is **stateless** — it runs, hands you a downloadable file, and resets when you close its panel. Nothing persists except files you explicitly save. If you find state leaking between tools/panels, that's a `[!]`.

### 3a. Space loads
- [ ] LAB-01 — Test Lab nav pill present (developer/qa); clicking it switches the center to the TEST_LAB toolbox; left sidebar shows the tool panels (one accordion per tool).
- [ ] LAB-02 — Left sidebar lists the tool categories: Reformatter, ID Reconciliation, Manifest Scaffolding, Anonymiser, AquaSynthesizer (synthetic data). Note any that are missing/greyed.
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
- [ ] LAB-11 — Save the **transformation recipe** as YAML → downloads; reload it back into the tool → same steps restored (round-trip).
- [ ] LAB-12 — Many-to-many ID collisions are flagged (not silently joined).
- [ ] LAB-13 — Boundary check: composite/multi-key reconciliation is **out of scope** here — confirm the tool only offers single-key (no composite-key UI). *(That belongs in BLUEPRINT Joint Designer.)*

### 3d. Manifest Scaffolding (boilerplate ZIP)
- [ ] LAB-14 — Upload one or more data files; tool infers structure and produces a **boilerplate manifest ZIP** (basename-mirroring dirs).
- [ ] LAB-15 — Generated manifest has: `id`/`info`, `data_schemas` with inferred `input_fields` types, empty `tier1: []`/`tier2: []` stubs, `join_manifests: {}` stub, PK-candidate **hints as comments** (e.g. `# Candidate PK: sample_id (100% unique)`).
- [ ] LAB-16 — Generated manifest does **NOT** invent `analysis_groups`, plot specs, or `final_contract` (those are BLUEPRINT's job). Confirm they're absent.
- [ ] LAB-17 — The generated boilerplate **loads cleanly** (no ConfigManager error) when selected as a manifest in HOME, or via the import path. *(This is the key correctness gate — old Bootstrapper wrote `plotting:` instead of `analysis_groups:`; confirm that's fixed.)*
- [ ] LAB-18 — If ID Reconciliation was run this session, Scaffolding offers an **opt-in checkbox** to bake those reconciliation steps into `tier1:`. With it off, scaffolding still works fully standalone.

### 3e. Anonymiser
- [ ] LAB-19 — Load a TSV with identifying columns; run anonymisation → produces an **anonymised TSV + a mapping TSV** (both downloadable).
- [ ] LAB-20 — Same original ID → same anonymised ID **within the file**; types/value-ranges remain plausible.
- [ ] LAB-21 — Multi-file: the output documents how to keep IDs consistent across files (recommends reconciling first; advisory, never blocking).

### 3f. AquaSynthesizer (synthetic data)
- [ ] LAB-22 — Generate **demo** synthetic data from a schema → downloadable TSV + a `synthetic_data_config` YAML.
- [ ] LAB-23 — The config YAML's first two lines are the mandatory header (`# NOT a pipeline manifest...`) and root key `synthetic_data_config:`. *(Firewall — it must not be mistaken for a manifest.)*
- [ ] LAB-24 — **stress_test** mode injects errors (nulls/dupes/edge cases) per the config.
- [ ] LAB-25 — Save a **named scenario** → reload it → all fields match (round-trip).
- [ ] LAB-26 — Loading a synthetic config via the normal manifest path is **rejected/ignored** (not processed by the data engine).

### 3g. TEST_LAB audit & isolation
- [ ] LAB-27 — File-generation operations log what was produced (filename, schema, row count) to the notification/audit log.
- [ ] LAB-28 — Closing the browser tab / refreshing loses in-progress (unsaved) work but keeps explicitly-saved files. No ghost-save in TEST_LAB.

---

## 4. BLUEPRINT (BLU) — visual manifest IDE (mostly new since Phase 26)

> Config file: `developer_template.yaml` or `qa_template.yaml` (full edit mode); `project-independent_template.yaml` gives the non-edit subset (`manifest_edit_enabled: false`). Click **Blueprint Architect** nav pill.
> Design: `.claude/design/spaces/BLUEPRINT.md`. Feature lock: ADR-082. Rules: `rules_ui_dashboard.md §7`.
> **Reality-check note:** BLUEPRINT had known build-gaps as of 2026-05-20 (add-node primitive UI, component/plot forms, group/meta/new-manifest/validate were YAML-only); several closed in Phase 32–33. Where a feature is simply **absent**, mark `[b]` and note it — discovering the doc/reality gap is itself a useful result, not a failure.

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
- [ ] BLU-21 — **YAML escape hatch** visible. For `developer_template.yaml`/`qa_template.yaml` it's an **editable** textarea (`manifest_edit_enabled: true`); for other config files it's **read-only**. Confirm the right mode for the file you launched.
- [ ] BLU-22 — Editing YAML in the escape hatch and saving emits a change the rest of the IDE reflects (and, per design, a `developer_raw_yaml` node).
- [ ] BLU-23 — **Undo**: make several node changes → undo steps back through them (up to 20). Redo if present.
- [ ] BLU-24 — **Branch** (lineage bifurcation at a node): split a lineage so upstream stays shared and the child diverges as a new `!include` fragment. Confirm it does **not** duplicate the whole manifest. *(Canonical example: Summary vs Summary_quality.)*
- [ ] BLU-25 — **AI agent** chat panel present (developer/qa). Send a plain-language request ("add a step to filter identity ≥ 90"). It responds; it **advises, never blocks**. Note backend status (it uses `claude_cli`; if not authed it should degrade gracefully to a disabled banner, not crash).
- [ ] BLU-26 — Agent respects scope: it proposes manifest structure / actions that actually exist in the loaded libraries (doesn't hallucinate unregistered actions).

### 4f. Save / load
- [ ] BLU-27 — Save the manifest → writes YAML to disk and/or downloads. The saved file is valid and reloads.
- [ ] BLU-28 — A manifest saved from BLUEPRINT can be selected and **run in HOME** end-to-end.
- [ ] BLU-29 `[?]` — Join-component save: confirm the `on:` key is correctly quoted in saved YAML (known serialization risk — `on` is a YAML boolean trap). If a saved join reloads with `True` as a key, that's a `[!]`.

---

## 5. HOME (HOM) — analysis space (re-verify + new)

> Config file: `developer_template.yaml`, `qa_template.yaml`, `project-independent_template.yaml`, or `pipeline-exploration-advanced_template.yaml` for full surface (all four set `t3_sandbox_enabled: true`).
> Most of this passed at Phase 26 but on a stale baseline — re-verify the core, then test the genuinely-new palette/cascade/apply-UX items (marked **NEW**).
> EVE: user facing template for testing is `developer_template.yaml`, manifest choice is 1_test_data_ST22_dummy

### 5a. Tabs, plots, preview (core)
- [x] HOM-01 — Group tabs = manifest `analysis_groups` (Quality Control · Curiosity · Results · Cat 🐱). No hardcoded tabs.
  > EVE: ok - tested by changing manifest and observing changes in analyses groups
- [x] HOM-02 — Each tab's plots render as static images; multi-plot groups expose plot **sub-tabs**.
  > EVE: ok
- [x] HOM-03 — **Data Preview** accordion below the plot shows ~100 rows of the active plot's dataset; updates on sub-tab switch.
  > EVE: ok
- [~] HOM-04 — Header strip shows dataset label (left) + tier-toggle radios (right).
  > EVE: Yes but data set shown are not totally correct ! 
- [!] HOM-37 — "All rows" toggle in Data Preview blanks the table entirely, no error shown. → [20260810_testing_part1.md#hom-37](20260810_testing_part1.md#hom-37--all-rows-toggle-blanks-the-data-preview-table-bug) — needs a terminal traceback to root-cause, see note.
- [ ] HOM-38 `[?]` — "Plot" accordion title above each plot reads as redundant next to the plot's own title. By design (ADR-043) — your call on whether to change it. → [20260810_testing_part1.md#hom-38](20260810_testing_part1.md#hom-38--redundant-plot-accordion-title-above-each-plot)
- [ ] HOM-39 `[~]` — Data Preview doesn't make the 100-row cap clear to the user; the total row count of the underlying table isn't shown anywhere. → [20260810_testing_part1.md#hom-39](20260810_testing_part1.md#hom-39--data-preview-100-row-cap-not-communicated)

### 5b. Tier toggle
- [ ] HOM-05 — T1 → T2 on the `year_distribution` plot (Results tab): T1 shows all years, T2 filters to 2023–2025 (missing bars prove the toggle). No flicker / duplicate renders in terminal.
- [ ] HOM-06 — T2 → T3 (advanced+): Filters "Apply" button relabels to `➜ Audit (N)`; right sidebar shows Tier 2 (inherited) + Tier 3 (my adjustments) sections.
- [ ] HOM-07 — Toggling T1→T3→T1 keeps the active plot sub-tab. *(carried: old §4c.)*
- [ ] HOM-08 — Home→Gallery→Home **restores** the previously active group tab + sub-tab + tier. *(carried: old §4c had two boxes left unchecked — verify on current build.)*

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
- [ ] HOM-22 **NEW** — If a manifest declares `plot_defaults.palette` or a per-plot `palette:`, plots render in that palette. Switching manifests changes palette accordingly.
- [ ] HOM-23 **NEW** — `aesthetic_override` (T3 plot colour/fill/alpha/shape), **if an authoring path exists**, actually changes the rendered plot (not just recorded). If there's no UI to author it yet, mark `[b]` (VIZFAC-T3-OVERRIDE-1 may still be pending).
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
- [ ] HOM-32 — Bundle contains `plots/`, `data/` (T1+T2; T3 when advanced+T3 active), `recipes/`, `report.qmd` (with a **T3 Audit Trail** section when T3 nodes exist), `README.txt`. Filters present → `FILTERS.txt` included ("no trace, no export").
- [ ] HOM-33 — `report.qmd` front-matter records manifest id + sha; methods text reads in plain English from active T3 nodes; PK-touching nodes carry the ⚠️ marker.

### 5h. Data Import (advanced+/independent)
- [ ] HOM-34 — Data Import accordion: upload a TSV matching a schema → assignment table appears with the right dataset id pre-selected → Apply → plots reload, no traceback.
- [ ] HOM-35 — Upload a file with wrong columns → per-file validation error (missing/mistyped columns); no data written, cache not busted.
- [ ] HOM-36 — Multi-file (Ctrl/⌘-select two) → independent dataset dropdowns; both apply.

---

## 6. GALLERY (GAL) — recipe browser (re-verify)

> Config file: `project-independent_template.yaml`, `developer_template.yaml`, or `qa_template.yaml` (all set `gallery_enabled: true`). Click **Gallery** nav pill. Mature space — lighter pass.

- [ ] GAL-01 — Gallery loads: recipe browser in center; left sidebar shows Recipe selector + collapsible taxonomy filters (Family / Data Pattern / Difficulty).
- [ ] GAL-02 — Taxonomy filter choices come from `gallery_index.json` (not hardcoded); "Select all" toggles a group's checkboxes; "Apply" filters the recipe list.
- [ ] GAL-03 — Click a recipe card → center shows its preview PNG + guidance (Visual Cookbook) panes; both accordions collapse/expand independently.
- [ ] GAL-04 — Recipe shows: description, required columns, raw manifest YAML; YAML is copyable (the GALLERY→BLUEPRINT handoff is copy-paste, per design — no direct "send to").
- [ ] GAL-05 — Taxonomy tag strip renders (`📊 Family · 🔢 Pattern · 📈 Difficulty …`).
- [ ] GAL-06 `[~]` — **(carried, old §12)** The recipe-title icons should use the **same** icon set as the taxonomy tag strip, fetched when the taxonomy auto-populates the sidebar (consistency). Confirm; if mismatched, `[~]`.
- [ ] GAL-07 `[~]` — **(carried, old §12)** "Select all" row still has a slightly large gap below it. Low priority.
- [ ] GAL-08 — Click Home → returns to plots; left sidebar tools reappear; selected manifest preserved.
- [ ] GAL-09 `[b]` — Search, community contribution/request, "Open in BLUEPRINT" — **not built** (per GALLERY.md). Confirm absent; don't fail.

---

## 7. Cross-space workflow (XSP) — the producer arc

> Tests the file-based handoffs (export here → choose there). There are **no in-app "send to" buttons** by design — handoffs are deliberately file-based so spaces stay independently persona-gated. Use **developer/qa**.

- [ ] XSP-01 — TEST_LAB Scaffolding ZIP → load that manifest in BLUEPRINT → it opens and is editable.
- [ ] XSP-02 — TEST_LAB Reformatter TSV → use it as input to ID Reconciliation (choose the file) → works as any standalone input.
- [ ] XSP-03 — GALLERY recipe YAML (copied) → paste into BLUEPRINT escape hatch → it parses.
- [ ] XSP-04 — BLUEPRINT saved manifest → appears in HOME's manifest selector → runs.
- [ ] XSP-05 — Anonymiser anon-TSV + mapping-TSV → can be re-joined (de-anonymised) following the printed recipe.
- [ ] XSP-06 — Confirm there is **no** cross-space coupling: disabling a space's flag never strands another space's output (the artifact is a file on disk).

---

## 8. Regression & legacy guards (REG)

> Quick confirmations that previously-fixed bugs stay fixed and Phase-34 legacy removals didn't break the happy path.

- [ ] REG-01 — STATE-1: no plot flicker on T3 toggle / panel switch.
- [ ] REG-02 — STATE-2 / AUDIT-4: comparison T2/T3 toggle stays on the correct plot after a sub-tab switch.
- [ ] REG-03 — UX-1 / BUG-PERF-1: plot rendering is reasonably fast; terminal shows `materialize_tier1` only on cache miss, not repeatedly.
- [ ] REG-04 `[~]` — **(carried, old §17 UX-2)** "Visible columns" multiselect in Data Preview is narrower than its panel. Confirm; `[~]` if still present.
- [ ] REG-05 — Comparison mode (advanced+): toggle on in T3 → 2-column reference-vs-adjusted layout; toggle off → single pane.
- [ ] REG-06 — Notification log (`🔔 Alerts (N)`) in right sidebar: actions append newest-first with timestamps + colour; max 20 kept; persists across nav within a session.
- [ ] REG-07 — Sidebar collapse: hide left sidebar → content fills width → re-show works after several cycles. *(carried: old §12 sidebar — left untested at Phase 26.)*
- [ ] REG-08 — **Critical (carried)**: hide **both** sidebars (advanced+) → both toggles remain clickable → each sidebar can be re-expanded independently.
- [ ] REG-09 — Legacy-removal smoke: the default manifests load and render without `ConfigurationError`/`TransformationError` (Phase 34 removed flat `plots:`, `string`/`character` type aliases, flat `wrangling:` lists — none of the shipped manifests should trip these).
- [~] REG-10 — Duplicate Shiny IDs (`notification_log_accordion`/`notification_log_panel_ui`) at launch. → [20260810_testing_part1.md#reg-10](20260810_testing_part1.md#reg-10--duplicate-shiny-ids-notification_log_accordion--notification_log_panel_ui) — root-caused + fixed, RETEST ↻

---

## 9. Aesthetic / CSS homogenisation backlog (CSS)

> Eve's carried-over styling consistency items. Low urgency, batch-fixable. Authoritative palette/scale: `rules_css_style_spec.md` — I'll fix against that, not invent values.

- [ ] CSS-01 `[~]` — **(carried, old §6/§10)** Trash/bin button in **filter** staged rows must match the trash/bin in the **audit** panel (same `btn-link` red style). Re-confirm they're identical on the current build.
- [ ] CSS-02 `[~]` — **(carried)** "Visible columns" multiselect width (= REG-04) — make it span the panel.
- [ ] CSS-03 `[~]` — **(carried, old §12)** Gallery recipe-title icons ↔ taxonomy tag-strip icons consistency (= GAL-06).
- [ ] CSS-04 `[~]` — **(carried, old §11)** "Blueprint Surgeon" right-sidebar styling homogenised with the "Pipeline Audit" right sidebar (= BLU-03).
- [ ] CSS-05 — Free-find: while testing, note any colour/spacing/font that looks off-palette (Bootstrap blue `#0d6efd`, success green, etc.) with the panel name — I'll reconcile against the style spec.
- [ ] CSS-06 `[~]` — "All rows" switch not aligned with "Data Preview" label in the Data Preview accordion header. → [20260810_testing_part1.md#css-06](20260810_testing_part1.md#css-06--all-rows-switch-not-aligned-with-data-preview-label)

---

## Appendix A — Known gaps / not-expected-to-work (don't fail these)

These are designed-but-unbuilt or deferred; mark `[b]` if you wander into them:

- GALLERY: search, community contribute/request, "Open in BLUEPRINT" (GALLERY.md).
- BLUEPRINT: unified add-node form, full plot/component forms, inline validate, new-manifest-from-scratch UI, lineage isolation (v2) — some may have landed in Phase 32–33; report what you find.
- HOME: T3 `aesthetic_override` render path (VIZFAC-T3-OVERRIDE-1), plot-panel collapse (THEATER-1), "show all rows" preview toggle.
- Maps / flow / network chart types (deferred — MAP-A-* in progress, not in default manifests).
- Galaxy / IRIDA deployment paths (23-C/D/E — backlog).

## Appendix B — When something fails (reminder)

1. Note the **item ID** + what you saw vs expected.
2. Flip the box to `[!]`/`[~]`/`[?]` and add one `> EVE:` line. Screenshot path / terminal snippet welcome.
3. Don't fix inline. Ping me; I grep §0.5, fix, stamp `RETEST ↻`.

## Appendix C — Reference docs

- `.claude/design/spaces/{HOME,BLUEPRINT,GALLERY,TEST_LAB}.md` — space specs
- `.claude/design/developer_workflow.md` — the cross-space producer arc (§7 here)
- `.claude/rules/rules_persona_feature_flags.md` — authoritative persona matrix (§2 here)
- `.claude/rules/rules_ui_dashboard.md`, `ui_implementation_contract.md` — UI contract
- `.claude/rules/rules_css_style_spec.md` — palette/typography (§9 here)
- `.claude/knowledge/architecture_decisions.md` — ADRs (082 BLUEPRINT lock, 084 TEST_LAB, 073 sidebar, 071 positive inclusion)
</content>
</invoke>
