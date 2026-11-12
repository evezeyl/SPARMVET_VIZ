# HOME: gating of filters by configuration, and configurations for automatic tests (decision paper)

> **CORRECTION (2026-11-12, Eve, P1): audit requires export, Compare and sessions. Rule 6 is correct; problem P4 and section 5 (R-a/R-b/R-c) and the configurations `test-audit` and `test-audit-no-sessions` are WRONG and withdrawn. Only R-a stands.**
>
> **STATUS CHANGE (2026-11-12, after Eve's correction): this paper is stage 5 of `home_design_first_roadmap_2026-11-12.md` and is PAUSED.** It describes how the code works **today** (sections 2 and 3.2) and proposes gating and test files **before** the behaviour is agreed, which is the wrong order. Read the roadmap first: the design (what each kind of configuration shows and can do) is agreed first, then the mechanism, then the code; gating and test configurations are derived from the agreed behaviour table. Use this paper only as input: its verified facts tell the build plan what has to change. Its questions Q1, Q2 and Q7 are now Q3, Q2 and Q5 of the roadmap; Q3-Q6 and Q8 wait.

**Written for:** Eve, to review in one place. **Written:** 2026-11-12, after your answers of the same day. **Status:** problem, alternatives with pros and cons, and my recommendation for each. Nothing here is decided and nothing was built or changed in code, configuration or diagrams.
**Method and words:** as in `home_audit_forensics_2026-11-12.md` (evidence: **verified** / **reasoned** / **not verified**; status: **DECIDED**, **CONFIRM**, **OPEN**, **MINE**). Points of view: **S** scientist who publishes, **DS** data scientist, **Dev** developer, **QA** checker, **Ops** operator, **N** novice user.
**Scripts (scratch, not committed):** `tmpAI/architect/flag_combinations.py` (the 32 combinations through the real validator), `tmpAI/architect/scan.py`.
**The order I judge every option by:** (1) does it keep the science sound (nothing can change a plot, the data or an export without an audit step, a reason and a record); (2) does it follow what you decided; (3) can it be tested automatically; (4) cost. The demo is not a criterion (your answer).

## 1. Your answers of 2026-11-12, and how I read them

| You said | I read it as | Please confirm (Q = question in section 8) |
|---|---|---|
| "The filters, if they are not active, should be hidden" | A control whose capability is switched off by the configuration is **not in the page at all** (not greyed, not disabled). This is also the rule of ADR-071 (positive inclusion) that the app already uses for panels | Q1 |
| "They need the gated update depending on the configuration choice, and this needs to be gated cleverly" | One clear gating model that every filter-related control follows, instead of a check written by hand at each place (section 4) | Q3 |
| "Remember the difference between the preview filters and the filters that change and send to audit" | Two **separate capabilities** with separate gates. They share the form (decided) but never the permission: preview never grants audit, audit never replaces preview (section 3) | none |
| "We need correct configuration files that you can use for testing automatically" | A set of configuration files made for tests, valid by the validator, covering the combinations that matter, independent of the shipped and demo files (section 6) | Q5, Q6 |
| "My demo will show the functionalities, so I might use different configurations; the demo is not your concern now" | No demo requirement in the design. It is also a reason to keep test configurations apart from the shipped ones: a demo change must not change what the tests check | none |
| "Your concern is a sound design that works for the science; put everything else in the document" | This paper | none |

One sentence of yours can be read two ways, so Q2 asks: "hidden if not active" can mean (A) off **by the configuration** (my main reading) and (B) off **by the state of the page**, for example the preview filters while audit mode is on. Both are covered below.

## 2. The problem, in six verified facts

**P1. Gating is written by hand in two layers, in many places.** Panels are gated by a flag in `PANEL_REGISTRY` plus the slot list of the feature file (ADR-073). Controls inside a panel are gated by `bootloader.is_enabled(flag)` written at each place: **17 checks of the three flags that decide filters, the strip and the audit** (`interactivity_enabled` 7, `t3_sandbox_enabled` 8, `comparison_mode_enabled` 2) in four files (`server.py`, `home_theater.py`, `filter_and_audit_handlers.py`, `export_handlers.py`), and 41 literal checks of all flags in 9 files. The decided audit mode adds about a dozen new controls (section 3.2); each one needs its gate. *Verified: grep.*

**P2. One control is gated by a proxy that is wrong for other files.** The "Exploration only, filters are not saved" notice in the Filters panel appears when `metadata_ingestion_enabled` is **false**, and the code says why: "Proxy: ... identifies simple/passive-only app features files" (`filter_and_audit_handlers.py:91-93`). A custom file with the audit off and metadata ingestion on gets no notice. *Verified: read, and **run**: the scratch file `test-preview-meta` (audit off, metadata ingestion on, valid) launches and its page has no "Exploration only" notice, while `test-preview` (metadata ingestion off) has it.*

**P3. A text appears in a configuration where its subject does not exist.** The Export panel says "Only steps sent to audit are exported. Filters you are only exploring with are not." whenever `interactivity_enabled` is on (`export_handlers.py:470-476`), also when the audit is off and no step can ever be sent. *Verified: read, and **run**: with `test-preview-export` (audit off, export on) the Export panel shows that sentence.*

**P4. The validator contradicts the decided design.** `AppFeaturesValidator` Rule 6 makes it a **fatal error** to switch the audit on without Compare, sessions and export. The decided design says audit mode may run without Compare ("Off: the audited plot uses the full width", `home_audit_steps.md` 3). Result, from running all 32 combinations of the five gating flags through the real validator: **11 clean, 7 warn only, 14 fatal; with interactivity on, exactly one combination with the audit on is legal today** (audit + compare + sessions + export). Two rules the design **decided** ("comparison requires the audit flag"; "the audit flag requires the `audit_stack` slot", `home_audit_steps.md` 14 and 16) are not built, and `SidebarValidator` does not check that a capability has a place (it skips gate-disabled panels silently by design). *Verified: `flag_combinations.py`, `app_features_validator.py:112-137`, `sidebar_validator.py:166-175`.*

**P5. The shipped files cover 5 of the 11 legal combinations, and the browser tests mostly run under one file.** The 8 shipped files use 5 of the 11 clean combinations (the all-on combination four times); 6 legal combinations are never run (for example preview only with export, or sessions without audit). The browser suite runs under `qa` (everything on): the tests that need another file are skipped (9 `skipif` in `test_shiny_smoke.py`, 16 in `test_shiny_smoke_blueprint.py`, decided by the launch variable `SPARMVET_APP_FEATURES`). `test_every_app_features_starts.py` launches each shipped file (15 s each) but checks three things, and the expected Blueprint tab comes from a hard-coded name set (`WITH_BLUEPRINT`), not from the flags. One shipped file carries a dead flag (`pipeline-exploration-simple`: comparison on, audit off; legal today, to be refused by the decided rule). *Verified: grep, read, the 32-combination run.*

**P5b. In a configuration without the audit the page still offers My view.** Launched with `test-preview` (audit off, compare off): "Data to show" offers T1, T2 and T3 (My view) and "Plot to show" offers T2 and T3; the Filters form, "Apply", "+ Add" and "Reset" exist; "Send to Audit", "Audit drops" and the right audit sidebar do not exist (they are already hidden). So the plot-changing preview of My view is reachable where there is no audit (the interim catch of forensics F8, now seen in a running page). *Verified: run (`probe_config.py`).*

**P6. Two things that must stay different are easy to blur.** A preview filter changes the table you look at and nothing else. A filter sent to audit changes a plot, the data and the export, and needs a reason. Today the same panel offers "Apply" always and "Send to Audit" only with the audit flag and only on My view (`filter_and_audit_handlers.py:303-330`), so the distinction is kept by a few `if`s. The decided design keeps one form with two actions (`home_preview_filters.md` 2). Without a clear gating model the distinction can erode with every new control. *Verified: read.*

## 3. The gating model that the options below are judged against

### 3.1 Capabilities, and two kinds of gate (MINE, to review)

- **Capabilities** (the words I propose; the flags keep their names, as decided): `preview_filters` = the Exploration filters (flag `interactivity_enabled`); `audit_steps` = everything that can change a plot, the data or the export (flag `t3_sandbox_enabled`, needs `interactivity_enabled` and the `audit_stack` slot); `compare` = the Compare toggle (flag `comparison_mode_enabled`, needs `audit_steps`); `sessions`, `export` as today.
- **Static gate (configuration):** decided once at start, never changes during a session. Decides whether a control **exists in the page**. Hidden means absent, as for panels (ADR-071), and also its server code is not registered (as `server.py:213-214` already does for the audit handlers).
- **Dynamic gate (page state):** depends on the mode (Exploration or Audit mode), the data view (Raw or Result) and what the user chose. Decides whether an existing control is shown or enabled now. It must follow the shell-stability rules R2-R4 (`ui_implementation_contract.md` 14) so that a mode change does not destroy and re-create inputs.
- **The invariant that protects the science (testable):** *in a configuration without `audit_steps`, no control in the page can change a plot, a data file or an export.* It is the executable form of your rule, and the first thing the test configurations of section 6 check.

### 3.2 The filter-related controls: today and target (verified in the code of today, and in the decided texts and pictures)

"Hidden when off" is the rule you gave; the right column says how each control follows it.

| Control | Kind | Gate today | Target gate | When its capability is off |
|---|---|---|---|---|
| Filters panel (accordion) | shared | registry `filters` <- `interactivity_enabled`, and in the slot list | same | absent |
| Filter form (column, operator, value, "+ Add") | shared | the shell returns empty without `interactivity_enabled` (`filter_and_audit_handlers.py:83`) | `preview_filters` | absent |
| "Apply (n)" now, "Add to preview" in the target | preview | always, with interactivity | `preview_filters`, Exploration | absent |
| "Reset" | preview | always, with interactivity | `preview_filters` | absent |
| Column selector (hide columns, table only) | preview | `interactivity_enabled` (`home_theater.py:1379`) | `preview_filters`, Exploration | absent |
| Badge "N preview filter(s) on, not saved" | preview | `interactivity_enabled` (`home_theater.py:736,1315`) | `preview_filters` | absent |
| Notice "Exploration only, filters are not saved" | preview | **proxy** `metadata_ingestion_enabled` false (P2) | `preview_filters` and not `audit_steps` (or always in Exploration: Q2) | absent |
| "Send to Audit (n)" now, "Create audit step" in the target | audit | audit flag and My view (`filter_and_audit_handlers.py:303`) | `audit_steps`, Audit mode | absent (already hidden today) |
| "Audit drops (n)" button | audit | audit flag and My view (`home_theater.py:1458`) | `audit_steps`, Audit mode | absent (already hidden today) |
| Notice "Sandbox: only steps sent to audit are exported" | audit | audit flag and My view | `audit_steps` | absent |
| Export-panel notice about audit and exploration (P3) | info | `interactivity_enabled` | two texts: with `audit_steps` as today; without it "exploration filters are never exported" | the right text, never the wrong one |
| Header strip: "Data to show / Plot to show", My view, Compare | strip | interactivity (`home_theater.py:974`); Compare by `comparison_mode_enabled` | **decided target:** "Data: Raw \| Result" only; no "Plot to show", no My view, no Compare in Exploration | see Q7 (the interim) |
| Mode switch "Exploration \| Audit mode" | audit | does not exist | `audit_steps` | absent |
| Pipeline Audit panel (right) with the step list, Undo, Revert | audit | registry `audit_stack` <- `t3_sandbox_enabled`, and the slot | `audit_steps`, and the slot must exist (decided validator rule) | the whole right sidebar absent |
| Compare toggle | audit | `comparison_mode_enabled` | `compare` | absent |
| Dialogs: new audit step, project overview, lineage map; pre-export review; badge "N audit steps active" | audit | do not exist | `audit_steps` | absent |

### 3.3 When the preview filters are not active because the page is in Audit mode (reading B of your sentence; OPEN)

The decided design keeps the preview lists while audit mode is on but does not apply them ("kept for when the user returns", `home_audit_steps.md` 3). What does the page show for them?

| Option | S | DS | Dev | QA | N |
|---|---|---|---|---|---|
| **(a) Hidden in Audit mode**, kept in memory, shown again in Exploration | no stale filters on screen that could be mistaken for applied | the plot and table always follow one source | a dynamic gate on one output (shell-stable) | one rule: "what is not active is not shown" | simplest picture; the "Add to preview" button is replaced by "Create audit step" |
| **(b) Shown but greyed, "not applied in Audit mode"** | the user sees what is kept | risk of reading a greyed filter as active | the same dynamic gate plus a style | two states per control | more to explain |
| **(c) Shown and applied** | | breaks the decided "audit mode never applies preview filters" | | | rejected by the design |

**Recommendation: (a)**, because it is the rule you gave ("not active, hidden"). **Reversibility:** high.

## 4. How to gate: alternatives (the "clever" part)

| Option | What it is | S | DS | Dev | QA | Ops / N |
|---|---|---|---|---|---|---|
| **G1. As today** | `bootloader.is_enabled(flag)` at each place; proxies where a flag does not fit | the distinction preview/audit rests on `if`s (P6) | the same | no new code now; about a dozen new sites with the audit build; proxies (P2) and wrong texts (P3) keep appearing | expectations cannot be derived from the flags; hand-written per test | operators cannot read "what shows when" in one place |
| **G2. Capability resolver (MINE, recommended)** | one **pure** function turns the flags (and the slot lists) into a small immutable `Capabilities` object, computed once at start; every control asks it (`caps.audit_steps`); the validator rules are invariants over the same object; `is_enabled` stays and is answered from it during the migration | the invariant of 3.1 is one line and one test; no proxy | the same rule everywhere | one new module (about 100 lines) and table tests; migrate the filter-related sites first (17), the rest later, no big bang; the config files and flag names do not change (decided names kept) | the whole "configuration -> capabilities" map is a headless table test over all 32 combinations (less than a second); controls are tested against capabilities | one place to read; the docs matrix can be generated from it; a risk to manage: two vocabularies (flags, capabilities) while migrating |
| **G3. Capability levels in the file** | replace the booleans by levels (static, explore, audit) plus add-ons | illegal combinations cannot be written | | every shipped and custom file, the docs, the tests and `renamed_keys` change | fewer combinations to test | a hard migration; less freedom in custom files; conflicts with "flag names kept" (ADR-099 point 9) |
| **G4. A registry of controls** (like `PANEL_REGISTRY`): each control declares `requires` (a capability) and `mode`; the page is built from it | gating is data next to the control | | natural for independent controls, awkward for Shiny outputs that are re-rendered together; needs G2 first | one generic test walks configurations x registry and checks presence and absence in the page | the most uniform |

**Recommendation: G2 now (small, incremental, filter-related controls first), G4 only for the controls that are independent, G3 not now.** It fits the decided names, it is what makes the test configurations of section 6 verifiable, and it removes the proxy and the wrong text (P2, P3) as a side effect. **Reversibility:** high (G2 can be removed by inlining it). **Status:** MINE.

## 5. The companion rule (Rule 6) and the decided validator rules (P4)

The audit currently requires compare, sessions and export. The decided design says audit mode may run without Compare, and the decided new rule says Compare requires the audit. What should the rule about the other flags be? Counts are for interactivity on (the 16 combinations of audit, compare, sessions, export), computed:

| Option | Rule | Legal combinations | S | DS | Dev | QA | N |
|---|---|---|---|---|---|---|---|
| **R-a. Keep Rule 6** and add "compare requires audit" | audit needs compare, sessions and export; compare needs audit | **5** (audit with all three; four without audit) | an audit is always exportable and recorded | | nothing to change except the new rule | few combinations to test | "audit mode without Compare" of the design can never exist |
| **R-b. Audit needs export only**, plus "compare requires audit" | steps are useful only if they can leave the session | **8** | an audit is always exportable | steps are recorded (check how below) | one rule changes | a few more combinations | Compare is optional, as designed |
| **R-c. Only the decided rule, the rest as warnings** (your own principle: the software informs and warns, and blocks only the technical) | fatal only for what is technically impossible (the audit flag without its `audit_stack` slot; compare without audit); "audit without export: steps cannot leave the session" is a **warning** | **12** | the operator is told, not blocked | | the resolver (G2) prints the warnings; the validator keeps the fatal ones | the most combinations, all derived from the table | a clear message at start |

**Recommendation: R-b or R-c; R-c fits your principle best** (a lab may want an audit without sessions, or a read-only audit demo). **What I did not verify and need for this choice:** whether audit steps are written to disk when `session_management_enabled` is off (the ghost is controlled by `automation.ghost_save`, which is separate); if they are not, "audit without sessions" should at least warn. **Reversibility:** high (a rule in one place). **Status:** the two new rules are DECIDED; Rule 6 is code, not a decision, and it contradicts a decided text, so changing it is MINE.

## 6. Configuration files for automatic tests

### 6.1 What "correct" means (MINE)

A test configuration is correct when: it passes `AppFeaturesValidator` and `SidebarValidator` with no error and no warning (the CLI `scripts/validate_app_features_config.py --strict` does this for a file given by path); its slot lists match its flags (a capability that is on has its panel in the slot list: the decided rule B, extended); it is deterministic (`automation.ghost_save.enabled: false`, the recipe selector visible so a test can pick the recipe, as `qa` does); it is paired with a deployment that has the test recipe; and it **declares what it should show** (a capability profile) so that a test can compare the page with the declaration.

### 6.2 Alternatives

| Option | What it is | S / DS | Dev | QA | Ops |
|---|---|---|---|---|---|
| **C1. Shipped files only** (today) | add checks to `test_every_app_features_starts.py` | | nothing new | 6 legal combinations never run (P5); a demo change to a shipped file changes what the tests check | none |
| **C2. Committed test files** | one small file per capability profile in a test folder (given by path; the app accepts a path, `bootloader.py:292-307`), each validated in a headless test | the files can be read and reviewed by you | about 6 files to keep; `!include` paths of the sidebars are relative to the file, so they point at `config/ui/sidebars/` | complete and independent of the shipped and demo files; usable by hand for debugging | the shipped files can change freely |
| **C3. Generated** | a helper writes a temporary feature file from `qa` plus overrides at test time | | no committed duplicates; all 32 combinations are possible | the tested file is not a file you can open and read | |
| **C4. C2 for the browser set plus C3-style exhaustive headless table** (recommended) | the 6-7 representative files are launched in the browser; all 32 combinations go through validator and resolver in a headless table test | each file you can read | both costs, both small | the exhaustive map is under a second; the browser set about 90 s (15 s per launch) | |

**Recommendation: C4.** **Where the files live (Q6):** `app/tests/config/app_features/` (kept with the tests, not shipped) or `config/app_features/test-*.yaml` (next to the others, validated by the existing `--all` CLI and by `test_every_shipped_app_features_is_covered`). I recommend the first: a file in `config/app_features/` is product configuration and would be picked up as a shipped file by `test_every_app_features_starts.py` and the flag-matrix doc test; the tests folder keeps test configuration out of both.

### 6.3 The proposed set (checked with the real validator today; "needs R-b/R-c" means it cannot exist under Rule 6)

| Name | Audit (S) | Compare (C) | Sessions (M) | Export (X) | Interactivity (I) | Validator today | What the browser test checks |
|---|---|---|---|---|---|---|---|
| `test-static` | - | - | - | yes | no | clean | no Filters panel, no filter notice, no column selector, no strip |
| `test-preview` | - | - | - | - | yes | clean | the strip is "Data: Raw \| Result" (the decided target); the Filters form and "Add to preview" exist; **no** audit button, no mode switch, no right sidebar, no Compare; the Result plot image is identical before and after a preview filter (the invariant of 3.1) |
| `test-preview-export` | - | - | - | yes | yes | clean | as `test-preview`, plus the export panel says that exploration filters are never exported (P3 fixed) and an export holds no preview filter |
| `test-audit` | yes | - | yes | yes | yes | **fatal (Rule 6)**; needs R-b or R-c | mode switch and "Create audit step" exist; **no Compare toggle**, the audited plot uses the full width; preview controls hidden in Audit mode (3.3 a) |
| `test-audit-compare` | yes | yes | yes | yes | yes | clean | as `test-audit`, plus the Compare toggle |
| `test-audit-no-sessions` | yes | - | - | yes | yes | **fatal (Rule 6)**; needs R-c | the warning at start; the page works |
| `qa` (exists) | yes | yes | yes | yes | yes | clean | everything on; the current browser suite |

Test configurations for the capabilities that are about other user spaces (Blueprint, Gallery, Test Lab, ingestion) are outside this paper.

### 6.3b What I ran (scratch files in `tmpAI/architect/test_configs/`, not committed, not shipped)

| File | Validator CLI by path, `--strict` | Launched with `config/deployment/local/local.yaml` | What the page showed |
|---|---|---|---|
| `test-static` | PASS, 0 errors, 0 warnings | yes, no server error | no strip, no Filters panel, no filter notice |
| `test-preview` | PASS | yes | strip with My view (P5b); Filters form and Apply/+ Add/Reset; no audit buttons, no right sidebar; "Exploration only" notice |
| `test-preview-export` | PASS | yes | as above, plus the Export panel with the wrong sentence (P3) |
| `test-preview-meta` | PASS | yes | as `test-preview`, **without** the "Exploration only" notice (P2) |
| `test-audit-compare` | PASS | not launched | |
| `test-audit` | **FATAL**: "t3_sandbox_enabled=True but required companion flags are False: comparison_mode_enabled" (Rule 6) | cannot start | |

This also shows that a configuration given by path, with the sidebar `!include` paths relative to its own folder, validates and launches (the app accepts a path, `bootloader.py:292-307`).

### 6.4 The tests this makes possible

1. **Headless, exhaustive (cheap):** for all 32 combinations, the validator verdict and the capability set match a table written once from the decided rules; every shipped and test file is valid; no file has a capability on without its slot.
2. **Headless, structural:** no `is_enabled` of the three flags outside the resolver (a ratchet that counts the 17 sites down; it is also N5 of the architect review).
3. **Browser, per test configuration:** the presence and absence of each control of table 3.2 (the expected values come from the declared profile, not from a hand-written name set like `WITH_BLUEPRINT`).
4. **Browser, the science invariant:** in `test-static`, `test-preview` and `test-preview-export` try every control and check that the Result plot image is unchanged, nothing is written under `anchors/` and the export holds no filter (this is WP5's "plot identical before and after Apply", run per configuration). **Mutation check:** switch one gate on by mistake and see the test fail.

## 7. How this fits what is decided, and what it reconsiders

| Item | Status | Note |
|---|---|---|
| Hidden when not active; preview and audit are separate; test configurations; the demo is not a criterion | DECIDED by you today | section 1 |
| The target strip "Data: Raw \| Result", no "Plot to show", Exploration only without the audit flag | DECIDED (ADR-099) | section 3.2 |
| Comparison requires the audit flag; the audit flag requires the `audit_stack` slot | DECIDED (`home_audit_steps.md` 14, 16); not built | P4 |
| Flag names kept (`t3_sandbox_enabled` ...) | DECIDED (ADR-099 point 9) | G2 keeps them; G3 would not |
| Capability resolver (G2) | MINE | new module; replaces proxy and hand-written checks |
| Changing Rule 6 | MINE; reconsiders existing code that contradicts a decided text | section 5 |
| Test configurations outside the shipped folder; the capability profile in each file | MINE | section 6 |
| The interim (the old strip stays until audit mode exists) | DECIDED sequencing, but **OPEN** for the two features without the audit flag | Q7; this paper's G2 and `test-preview` are what make the early slice (forensics 3.7, option b) cheap and verifiable |

## 8. Questions for you (each with my recommendation; answer in the margin of this file)

| # | Question | Options | My recommendation |
|---|---|---|---|
| Q1 | "Hidden" = absent from the page when the configuration switches the capability off (not greyed)? | yes / greyed | yes (your answer, ADR-071) |
| Q2 | "Not active" also means: preview controls hidden while Audit mode is on? And does the "Exploration only" notice show in every Exploration, or only without the audit flag? | 3.3 a / b | a; show the notice only without the audit flag |
| Q3 | How to gate | G1 / G2 / G3 / G4 | G2 now, G4 later for independent controls |
| Q4 | The companion rule | R-a / R-b / R-c | R-c (warn, block only the technical) or R-b |
| Q5 | How to make test configurations | C1 / C2 / C3 / C4 | C4 |
| Q6 | Where the test files live | tests folder / `config/app_features/test-*` | tests folder |
| Q7 | The interim for the two features without the audit flag (forensics 3.7): keep the old strip until audit mode exists (a), or give them the final strip now (b)? Your answer "not active, hidden" fits (b); I did not want to decide it for you | a / b | b, together with G2 and `test-preview`, if you agree |
| Q8 | The wrong proxy (P2) and the wrong export text (P3) are small, verified defects in built code. Fix them now as separate small issues, or only with the gating work? | now / with G2 | with G2 (they disappear by construction); file the issues now so they are not lost |

## 9. Not verified (said plainly)

Whether audit steps are saved to disk without the sessions panel (section 5); that the control inventory of 3.2 is complete (I read the filter, strip, audit and export code, not every handler); how the two **shipped** features without the audit flag behave (I launched scratch files with the same flags, not the shipped files); the launch time of the test configurations in the test run (15 s each is the figure of the existing launch test, for shipped files); whether a configuration given by path works in the browser test fixture `create_app_fixture` (I launched them with my own server start, as `test_every_app_features_starts.py` does, not through the fixture).

## Appendix: one complete test configuration (`test-preview`, valid and launched; the others differ in the flags and in the right sidebar)

```yaml
name: "test-preview"
display_name: "test-preview"

flags:
  interactivity_enabled: true        # preview filters exist
  t3_sandbox_enabled: false          # no audit: nothing can change a plot, the data or an export
  comparison_mode_enabled: false
  session_management_enabled: false
  export_enabled: false
  gallery_enabled: false
  blueprint_enabled: false
  data_analysis_recipe_edit_enabled: false
  blueprint_agent_enabled: false
  test_lab_enabled: false
  import_helper_enabled: false
  metadata_ingestion_enabled: false
  data_ingestion_enabled: false
  show_app_features_badge: true

data_analysis_recipe_selector:
  visible: true                      # a test can pick the recipe, as with qa

testing_mode: true

automation:
  ghost_save:
    enabled: false                   # deterministic: no background saves during a test

workspaces:
  home:
    left_sidebar: !include ../../../config/ui/sidebars/home_standard_left.yaml
    right_sidebar: {visible: false, panels: []}     # the audit panel would go here
  blueprint: {left_sidebar: {visible: false, panels: []}, right_sidebar: {visible: false, panels: []}}
  gallery:   {left_sidebar: {visible: false, panels: []}, right_sidebar: {visible: false, panels: []}}
  test_lab:  {left_sidebar: {visible: false, panels: []}, right_sidebar: {visible: false, panels: []}}
```

The `!include` path is relative to the file: from a test folder it points at `config/ui/sidebars/`. The proposed capability profile (what the page must show) would be a comment block or a small key in each file, read by the tests.
