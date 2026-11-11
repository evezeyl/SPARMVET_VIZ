# UML model of SPARMVET_VIZ: plan (TOOLS-UML-3)

**Status:** in use (Eve, 2026-11-07). The UML is for the app.
**Model file:** `docs/UML/app.mdj` (StarUML). **Tool:** `OBSWORK/_bin/staruml/` (usage: `OBSWORK/_HELP/7_StarUML_Modeling_Workflow.md`).
**Findings:** `.claude/tasks/uml_findings.md`.

## 1. Scope (Eve, 2026-11-07)

The model describes the app, on one machine today; Galaxy, IRIDA and a container are shown as not implemented yet. It goes from wide to narrow: the whole app first, then each user space, HOME first, then GALLERY, BLUEPRINT and TEST_LAB.

## 1b. Goals, for now

1. Understand the key points: how the app is built and what a user does on HOME.
2. Find discrepancies between code, rules and documents, so the fixes are the right ones.

Documentation is a side effect, not the aim. A diagram exists only if it answers a question in section 3. No diagram of every function, no code generation. Eve does not review each diagram: she sees the findings that need a decision.

## 2. Decisions

- **D1. All diagrams are in StarUML, built as native elements; the model file is the single source of truth.** One element appears in many diagrams and is renamed once; for example the lifelines of the sequence diagrams point to the elements of the architecture diagrams. The Mermaid importer is not used, because it makes separate copies. The file is JSON, so a script can read it without StarUML. No Mermaid: the existing Mermaid diagrams in 8 `docs/` pages render badly and are replaced by StarUML images later (TOOLS-UML-4, after the licence, because of the trial watermark).
- **D2. The model shows what the app does today and what it is supposed to do, with a status. No history.** Every element has a `status` tag: `implemented`, `partial` or `planned`. Anything not `implemented` is grey in the diagrams and says so. No superseded ADRs and no old designs: the ADR log keeps the history as text.
- **D3. Elements carry tags that a script can check:** `status`, `code` (file and symbol), `adr` (only the ADR that governs it today), `rule`, `test`, `flag`. Names are the code's names. Views hide the tags, so diagrams stay readable. Vocabulary follows `CLAUDE.md` section 1.
- **D4. Requirements only where they prevent a wrong result.** Drafted from current ADRs and rules, each naming its source. Eve is asked only when sources conflict or none exists.

## 3. Diagrams, first set

Order is wide to narrow, and the table is in working order: context and containers, then how it is
built and run, then the parts, then the key flows. Code level is left out.

**Reordered 2026-11-08 (Eve: make the order human-navigable, not just complete)** — both the table
below and the live model (`docs/UML/app.mdj`) now follow the same logic: general functioning first
(Architecture — nothing user-space-specific belongs here), then one block per user space, each
internally ordered **what the user does → the screen → how it works**: use case, then wireframe,
then the component/reactive/sequence/state diagrams that explain the mechanism behind what was
just shown. The live StarUML project previously grouped diagrams by *diagram type* (every C4
diagram under one "Shiny app" folder, every wireframe under one "Wireframe1" folder, every
flowchart under one "Flowchart1" folder, every sequence under its own single-diagram folder) —
structurally accurate but not how a person looks for "everything about HOME." Each space's
diagrams are now reparented into that space's own top-level package in the model (`HOME`,
`GALLERY`, `BLUEPRINT`, `TEST_LAB`), so opening one node in the Model Explorer shows everything
about that space together. Diagram content, tags and exported filenames are unchanged — confirmed
diagram-by-diagram after reparenting (render check) and via `audit_uml_model.py` (0 violations)
after saving.

**Status column:** ✅ built and in `docs/UML/app.mdj` today (verified against the live project,
2026-11-08 — every diagram listed below exists; `GALLERY`/`BLUEPRINT`/`TEST_LAB` use case and
component diagrams and their `COM-REACTIVE-*` counterparts were added 2026-11-07/08, after this
table was first drafted, and are included here even though they weren't in the original row set).
⬜ not built — none currently; the table only lists diagrams that answer a question from this
section, so a planned-but-not-built diagram would show here, not in the "Later" prose below.

| ID | Question | Type | View | Status |
|---|---|---|---|---|
| **Architecture** | | | | |
| CTX-1 | Who and what does the app talk to? | C4 context | scenarios, logical | ✅ |
| C4-CONT | What runs, and which files and folders does it use? | C4 container | logical, physical | ✅ |
| PKG-TIERS | Which library may import which? | Package | development | ✅ |
| DEP-APP | How does the app run on one machine: process, folders, launch variables? | Deployment | physical | ✅ |
| C4-COMP-APP | Inside the Shiny app: which handler and module serves which user space? | C4 component | logical | ✅ |
| **HOME** — what the user does, then the screen, then how it works | | | | |
| UC-HOME | What can a user do, under which flag? | Use case | scenarios | ✅ |
| UI-HOME | What is on the screen, what is each panel called in the code, and which flag shows it? | Wireframe | scenarios, for users and developers | ✅ |
| C4-COMP-HOME | Which handler and module owns what on HOME? | C4 component | logical | ✅ |
| COM-REACTIVE | Which output reads which reactive value? (cause of the blank page and the sidebar bug). Direct reads found by a scan of the code | Flowchart | process | ✅ |
| SEQ-LAUNCH | How are deployment, app features and data analysis recipe resolved, and what stops the app? | Sequence | process | ✅ |
| SEQ-OPEN | Data analysis recipe to Raw stage, Result stage, plot, with the fingerprint checks — plain language, redrawn 2026-11-08 | Sequence | process, for users | ✅ |
| SEQ-AUDIT | Exploration filter against Send to Audit and Apply, current ADR-085/086 naming ("My view") — plain language, redrawn 2026-11-08 | Sequence | process, for users | ✅ |
| SEQ-EXPORT | From click to bundle, with the key check | Sequence | process | ✅ |
| STM-STAGE | When is a stored stage valid, rebuilt or removed? | State machine | process | ✅ |
| **GALLERY** — what the user does, then the screen, then how it works | | | | |
| UC-GALLERY | What can a user do, under which flag? | Use case | scenarios | ✅ |
| UI-GALLERY | What is on the screen, same detail as UI-HOME | Wireframe | scenarios, for users and developers | ✅ |
| C4-COMP-GALLERY | Which handler and module owns what, same detail as C4-COMP-HOME | C4 component | logical | ✅ |
| COM-REACTIVE-GALLERY | Which output reads which reactive value, in GALLERY? | Flowchart | process | ✅ |
| **BLUEPRINT** — what the user does, then the screen, then how it works | | | | |
| UC-BLUEPRINT | What can a user do, under which flag? Includes branching (ADR-082 §Q3), added 2026-11-08 | Use case | scenarios | ✅ |
| UI-BLUEPRINT | What is on the screen, in plain language — redrawn 2026-11-08 for users, unlike UI-HOME it carries no code/flag tags | Wireframe | scenarios, for users | ✅ |
| C4-COMP-BLUEPRINT | Which handler and module owns what, same detail as C4-COMP-HOME | C4 component | logical | ✅ |
| COM-REACTIVE-BLUEPRINT | Which output reads which reactive value, in BLUEPRINT? | Flowchart | process | ✅ |
| **TEST_LAB** — what the user does, then the screen, then how it works | | | | |
| UC-TESTLAB | What can a user do, under which flag? | Use case | scenarios | ✅ |
| UI-TESTLAB | What is on the screen, same detail as UI-HOME | Wireframe | scenarios, for users and developers | ✅ |
| C4-COMP-TESTLAB | Which handler and module owns what, same detail as C4-COMP-HOME | C4 component | logical | ✅ |
| COM-REACTIVE-TESTLAB | Which output reads which reactive value, in TEST_LAB? | Flowchart | process | ✅ |
| **Data** — cross-cutting, not tied to one space | | | | |
| DM-CONFIG | Deployment, app features, launch variables, precedence | Class | logical | ✅ |
| DM-RECIPE | The data analysis recipe's own data model — Data schema, Join, Analysis group, Plot, Wrangling step | Class | logical | ✅ |
| REQ-CORE | Quality goals and the requirements that protect a correct result | SysML requirement | all | ✅ |

**Later, not yet in this table** (from §3's original prose, still open): class diagrams of "the
core" and of other platforms (Galaxy/IRIDA) — deferred when UI-HOME's wireframe pattern was
worked out, not picked up since. Not rows here yet because no concrete question has been drafted
for either; add the row only once one is.

**Written (2026-11-07):** three text pages that go with the diagrams, because no diagram shows them
well, in `docs/UML/`: [`quality_goals.md`](quality_goals.md) (correct science and reproducibility
first, each goal backed by a `REQ-CORE` requirement), [`cross_cutting_concepts.md`](cross_cutting_concepts.md)
(configuration resolution, fail-fast, error handling, provenance, reactive write discipline,
flag-driven gating, the Two-Category Law, tier isolation, security deferred) and
[`risks_and_technical_debt.md`](risks_and_technical_debt.md) (the findings register, sorted by cost).

**Written (2026-11-08):** a fourth text page, written for the scientist running an analysis rather
than a developer: [`data_contract_and_failures.md`](data_contract_and_failures.md) — the two
different checks (recipe structure vs. data-vs-contract), where to run them, and plainly, what the
engine does with a mismatched column when nobody runs the check (silent skip). Prompted by Eve
asking for the "process of failures" to be explained from the user's perspective; writing it
surfaced that `validate_data_analysis_recipe_data()` (the data-vs-contract check) was built and
tested but called from nowhere in the running app — fixed the same day (`VALIDATE-UI-1`). Backed
by a new `REQ-VIZ-DATA-02` in `REQ-CORE`.

**Extended (2026-11-08, ADR-094):** Eve's follow-up clarified HOME and BLUEPRINT need opposite
failure behaviour (HOME automatic/blocking, BLUEPRINT manual/advisory) and surfaced a real gap —
no deployment had anywhere to declare a contact for a HOME user who hits a broken recipe with no
BLUEPRINT available. `data_contract_and_failures.md` rewritten to describe the final state;
`quality_goals.md`'s `REQ-VIZ-DATA-02` wording unchanged (already generic enough); `SEQ-LAUNCH`'s
`_resolve_default_data_analysis_recipe` message renamed to name the new discover+validate step
(the gate itself has no dedicated diagram — `data_contract_and_failures.md`'s prose covers it
better than a sequence diagram would, same reasoning as D1/D3's "no diagram shows this well" cases).
While wiring ADR-079 alongside this, found its own implementation was further along than its
status line or `tasks.md` said: `session_processing_issues` capture and the `report.qmd` "Pipeline
Issues During Session" section already existed (one catch point, VizFactory render failures) —
corrected both the ADR-079 status line and the stale `PIPELINE-ERROR-WIRE-1` task description
rather than re-building what was already there.

**Extended again (2026-11-08, same day):** Eve asked specifically about BLUEPRINT's own error
display ("are errors reported in blueprint... the detection and guidance text need to reach the
screen") — found all 3 BLUEPRINT catch points built a full `PipelineError` (problem + fix + who)
but only printed it server-side; the user only ever saw a generic toast. Wired `render_blueprint_inline()`
to actually render, and extended that renderer itself to include the fix text (it previously showed
only the problem). `UI-BLUEPRINT` gets two new panels (`bp_import_error_ui`, the YAML-hatch inline
error block) so the wireframe keeps matching the real screen; `COM-REACTIVE-BLUEPRINT` gets the new
`wrangle_studio.inline_errors` state and its two read edges. `cross_cutting_concepts.md`'s "Error
handling at runtime" section and `project_conventions.md`'s `pipeline_error.py` row were both still
describing the pre-ADR-094 (and in cross_cutting_concepts.md's case, pre-dating even that — it had
never been accurate) state — corrected both to name exactly which of the 7 raise points are wired
and which 4 remain open under `PIPELINE-ERROR-WIRE-2`.

**Done (2026-11-07):** GALLERY, BLUEPRINT, TEST_LAB use case diagrams (UC-GALLERY, UC-BLUEPRINT,
UC-TESTLAB) and C4 component diagrams (C4-COMP-GALLERY, C4-COMP-BLUEPRINT, C4-COMP-TESTLAB),
same level of detail as C4-COMP-HOME.

**Done (2026-11-08):** COM-REACTIVE for the other three spaces, same purpose as COM-REACTIVE-HOME
(which output reads which reactive value, by direct code scan). COM-REACTIVE-GALLERY (18 nodes,
small — one Calc, four render outputs, the clone-to-T3 handoff shown as two arrows into/out of
`home_state`). COM-REACTIVE-BLUEPRINT (46 nodes, grouped by concern — 2800-line handler, so
individual buttons/handlers inside each concern area are counted in the node label rather than
drawn one-by-one; `wrangle_studio` state is the visible hairball, every concern reads or writes
it, which is the honest picture of that file). COM-REACTIVE-TESTLAB (17 nodes) — confirms by the
total *absence* of edges between its five tool clusters that `rules_test_lab.md §1`'s stateless
tool principle holds in the real wiring, not just in the rule text. Building COM-REACTIVE-GALLERY
surfaced F-23 (`.claude/tasks/uml_findings.md`) — open, needs Eve.

**Done (2026-11-08):** wireframes UI-GALLERY (9 panels), UI-TESTLAB (8 panels), UI-BLUEPRINT (19
panels, the 3-column layout of `ui_implementation_contract.md §7` — left sidebar / central
theater / right sidebar, with the L1-L4 layer labels), same purpose as UI-HOME ("what is on the
screen, what is each panel called in the code, and which flag shows it"). The earlier blocker is
solved: `app.factory.createViewOf` on an existing model still throws the same
`getViewType`/`wireframe-factory.js:58` error headlessly, but a single
`app.factory.createModelAndView` call does not — use that, not the two-step
create-model-then-create-view pattern, for any wireframe element. Second gotcha: the `x`/`y`/
`width`/`height` options passed to `createModelAndView` are silently ignored for `WFPanel`/
`WFText` (they land at `0,0`, size `16x16`, `containerView: null`, all stacked on top of each
other) — position them in a second pass after creation by mutating `view.left`/`.top`/`.width`/
`.height`/`.containerView` directly on the view objects, then re-render; no `staruml_layout_diagram`
call (its generic auto-layout pulls wireframe children out of their frame entirely — tried once on
UI-GALLERY, `app.repository.undo()` reverted it). UI-HOME's existing structure confirmed the
pattern to replicate: one `WFPanel` (tagged `status`/`code`/`flag`) per UI region, with one
untagged `WFText` child carrying the same name as the visible label. **Later:** class diagrams of
the core and of other platforms (DM-RECIPE, the data analysis recipe data model, done 2026-11-08
below).

**Diagram export:** all 30 diagrams exported to `docs/UML/diagrams/*.png` via
`staruml_export_diagrams` (re-run after any diagram change; PNGs are not auto-synced).

**Done (2026-11-08, issue #33):** moved UI-HOME's "Alerts" panel+text from the right sidebar
(x=1170) to the left (x=20,y=690) — it had drifted: the actual code fix (notification_log moved
left) happened earlier the same session but the wireframe was never updated, which is exactly
what the new UML & ADR Sync Law (`workspace_standard.md §3`) now exists to catch. Added a new
"Alerts" `WFPanel`/`WFText` pair to UI-GALLERY, UI-BLUEPRINT, and UI-TESTLAB's left sidebars
(same `code`/`status` tags as Home's). Updated UI-TESTLAB's Info panel text to describe the new
`test_lab_info` placeholder, not the shared recipe-info panel. `audit_uml_model.py` clean
(0 violations) after each save.

**Tagging gotcha (new):** `app.engine.addItem(model, "tags", tag)` alone silently no-ops for a
tag created via `new type.Tag()` on an element created in the same script session — it never
registers the new object in the repository, so the push is lost on the next read even though no
error is raised. Fix: build the operation explicitly — `const ob = app.repository.getOperationBuilder(); ob.begin(...); ob.insert(tag); ob.fieldInsert(model, "tags", tag); ob.end(); app.repository.doOperation(ob.getOperation());` — `ob.insert(tag)` is what actually registers the
new element; `fieldInsert` alone only pushes a reference StarUML can't resolve later.

**Export gotcha (worked around, not fixed):** `staruml_export_diagrams` reliably fails to
refresh a diagram's PNG after a same-session edit — confirmed across 4 separate export calls on
4 diagrams, always returning the exact pre-edit file (same byte size, same mtime). The `.mdj`
model itself is correct (confirmed by direct script introspection and a clean
`audit_uml_model.py` run) — this is a stale-bitmap/caching bug in the export path, not a
model-data bug. Workaround: call `staruml_diagram_image` (returns a live render as a tool-result
image, bypassing whatever cache `staruml_export_diagrams` reads from) and copy that blob over the
stale PNG in `docs/UML/diagrams/` by hand.

**Position-vs-label desync gotcha (new, real bug this session):** when reflowing `WFPanelView`
positions in bulk (shifting several panels down to make room for an inserted one), the loop that
locates each panel's companion `WFTextView` (the visible label — see the "one `WFPanel` ... with
one untagged `WFText` child" line above) matched on `v.left === 20`, but the text views sit
*inset* from their panel (`panel.left + 6`, i.e. `26`, not `20`). Every text match silently
missed, so the panel rectangles moved to their new positions but every visible label stayed
exactly where it was — Eve caught this immediately ("the alerts are at the wrong place... nice
if visually it looks like the app, because for us it's how we detect"). Fix: match
panel-to-text pairs by `model.name` (unique per diagram here), not by `left`, and re-snap each
text to `panel.left+6, panel.top+6, panel.width-12, panel.height-12` after any bulk reposition —
don't try to preserve each panel's original bespoke inset, just standardize on 6px.

UI-HOME uses StarUML's wireframe diagrams (panels, buttons, tabs as model elements). Each widget carries its Shiny id in `code` and its gate in `flag`, so the script can check it. It replaces the hand-drawn picture in `ui_panel_map_current.md`, which is already out of date (it still shows a T1/T2/T3 toggle).

**Done (2026-11-08):** DM-RECIPE, the "Later" class diagram this section had deferred (data
analysis recipe data model — Eve asked, when picking the next task, whether this and REQ-CORE
were actually finished; both were, but this specific "Later" item was not). Five new classes
(Data schema, Join, Analysis group, Plot, Wrangling step) plus the existing "Data analysis
recipe" class reused from DM-CONFIG (D1 — one element, renamed once, shown on both diagrams).
Code tags point at the real class that owns each shape (`ConfigManager` for data_schemas and the
analysis_groups→plots flatten, `DataAssembler` for joins, `DataWrangler` for the canonical
`action:` step format, `VizFactory` for plot specs); `adr` tags needed a detour first — ADR-041,
ADR-012, ADR-024 all resolved, but trying `adr: ADR-014`/`ADR-013`/`ADR-024` on early drafts
would have failed `audit_uml_model.py`'s own check: ADR-001 through ADR-034 were all headed
`## ADR NNN:` (space) instead of `## ADR-NNN:` (hyphen), the only 34 headings in the whole file
not matching the hyphenated convention every citation elsewhere already uses. Fixed first (F-25,
pure rename, confirmed nothing parses the old form), then built DM-RECIPE on top of working
citations.

**Gotcha (2026-11-08):** a freshly created `UMLClassView` defaults `showProperty: true`, which
renders every tag as a visible `{code="...", adr="...", status="..."}` line under the class name
— directly contradicting D3 ("views hide the tags, so diagrams stay readable"). DM-CONFIG's
existing classes don't show this only because someone (or an earlier session) had already set
`showProperty: false` on each view; it is a per-view property, not a model-level or diagram-level
default, and is not touched by `createModelAndView`'s other options. Any new `UMLClass` added to
any diagram needs `app.engine.setProperty(classView, "showProperty", false)` as a follow-up step,
or it silently breaks D3 for that one element. Diagnosed by comparing `nameCompartment.subViews`
between a known-good DM-CONFIG view and a new one — the fourth `LabelView` (the tag line) existed
identically in both, differing only in `visible`, which turned out to be computed from
`showProperty`, not independently settable.

## 4. Outside check of this plan

Compared with arc42 (12 sections), the C4 model, and Kruchten's 4+1 views with ISO 42010 (each view states who it is for and what concern it answers):

- Starting with architecture, then HOME, is what C4 practice advises: context and containers first, dynamic diagrams for key flows, components selectively, code level optional. My first plan started from one export slice and drew class diagrams too broadly. Changed.
- The first plan was missing, against arc42: quality goals, constraints, cross-cutting concepts and risks. Added above. Security was missing entirely and already gave a finding (F-13).
- All four 4+1 views are covered by the set above; scenarios are UC-HOME and CTX-1.

**Fixed (2026-11-08, ADR-095, no new diagram nodes):** continuing `PIPELINE-ERROR-WIRE-2`
("keep going please") found the root cause the previous round's 2-of-7 count was built on: every
library raise site built a full `PipelineError` and then discarded it, raising a message-only
`SPARMVET_Error` instead — so the 5 remaining catch sites had nothing structured to show even if
wired. Fixed at the library contract (`SPARMVET_Error` now carries the original `PipelineError`
through the raise; `capture_entry()` reads it back), not by re-wiring symptoms. All 7 raise points
now surface fix/who: VizFactory render (both the normal and Comparison Mode paths — the latter was
found missing capture entirely, not just using an old pattern), T3 Apply's gatekeeper message and
a session-ghost-save failure that used to fail silently, and the export bundle's error stub. This
is exception plumbing inside handlers already drawn in `COM-REACTIVE-HOME`/`COM-REACTIVE-BLUEPRINT`
— no new reactive wiring topology, so no diagram edits this round. `cross_cutting_concepts.md` and
`project_conventions.md`'s `pipeline_error.py` row corrected again to the closed state;
`PIPELINE-ERROR-WIRE-2` closed, `PIPELINE-WARNING-SURFACE-1` opened for the 4 non-raising
`severity="warning"` sites (console-only, needs a different mechanism — not started).

## 5. Discrepancy checks

**Built (2026-11-07):** `assets/scripts/audit_uml_model.py`. Run manually (`./.venv/bin/python assets/scripts/audit_uml_model.py --project-root .`) and from `scripts/run_audits.sh ondemand`. No StarUML needed: it reads `docs/UML/app.mdj` as JSON. Each check below was proven with a planted error (one mutation per check: break a code/test reference, an ADR id, a flag name, a status value) and confirmed it fails, then confirmed it recovers once the model is restored. Its first real run against the finished model caught F-21 (a 4-file citation of an ADR, "ADR-037", that was never actually written).

| Check | Finds |
|---|---|
| Every `code` tag resolves (file and symbol via `ast`, or a string literal for a Shiny widget id) | Renamed or deleted code |
| Every `test` tag resolves | A claim of proof with nothing behind it |
| Every `adr` tag exists and is not marked historical/removed/superseded | Model built on an old or missing decision |
| Every `rule` tag's file exists under `.claude/rules/` (anchor not verified — formats vary too much) | A renamed or deleted rule file |
| Every `flag` tag is a real flag or field in a shipped app features file | UI promises a flag does not gate |
| Every `status` tag is `implemented`, `partial` or `planned` | A typo in the model's own status convention |

| Every `UMLDependency` edge in PKG-TIERS matches a live `from X import` / `import X` scan of the directory its `code` tag names, in both directions | A stale arrow (import since removed) or a missing arrow (real import never drawn) |

**Built (2026-11-08):** the PKG-TIERS check above, closing the gap this section itself had
flagged as "not yet checked". First real run found F-24 (`.claude/tasks/uml_findings.md`): one
stale edge (`test_lab -> id_reconciliation`, drawn but no longer imported — matches
`rules_test_lab.md §8`'s own claim the permission is unused) and two missing edges (`app ->
viz_gallery`, `assets/scripts -> app`, both real imports never drawn). Mutation-tested on a
synthetic two-package project before trusting it against the real repo: planted a stale edge and
a missing edge, confirmed both caught, confirmed clean after restoring. Fixed all three edges in
the live model via the StarUML bridge, re-ran — 0 violations.

**Built (2026-11-08):** the `rule` tag check above. Scoped intentionally to file existence only —
a `rule` value like `rules_test_lab.md §8` or `rules_runtime_environment.md#4` mixes `§N` and
`#N` anchor conventions across rule files inconsistently, so verifying the anchor itself would
need per-file heuristics; checking the filename catches the same class of bug the `adr` check
catches (a citation surviving a rename or deletion) without that fragility. First real run against
the live model: 0 violations (all 12 existing `rule` tags resolve).

Not yet checked (left for a later pass if it turns out to matter): widget ids in `UI-HOME` beyond
what a `code` tag already names — scoping this one needs a decision first, see the open question
below.

**Open question (2026-11-08):** the UI-HOME widget-coverage check would need to pick what counts
as "coverage" for a *wireframe*, which is deliberately not exhaustive — it draws panels, not every
micro-widget (a filter row's individual input, for instance). A real scan of `home_theater.py` and
its sibling handlers (`filter_and_audit_handlers.py`, `audit_stack.py`, `session_handlers.py`,
`export_handlers.py`, `data_import_handlers.py`) for every `ui.input_*`/`ui.output_*`/
`ui.nav_panel`/`ui.accordion_panel` id, diffed against what UI-HOME's `code` tags already name,
would likely be noisy — most individual inputs were never meant to be drawn. Needs a decision on
scope (panel-level ids only? nav/accordion structure only?) before building it, so it isn't done.

It checks names and links. It does not prove that the code runs in the order a sequence diagram shows; the tests do that.

## 6. Working rules

- StarUML holds the model in memory. Save before `git commit`. After a `git checkout` or `git pull` that changes the file, reopen it, otherwise the old copy overwrites the new one on the next save.
- Commit the model file by name after each diagram.
- Every difference found goes into the findings register. Findings that need work become issues.
- Tags: `[opus/high]` for this plan and the architecture diagrams, `[sonnet/high]` for the HOME diagrams read from code, `[sonnet/medium]` for the script.

### 6a. Embedding a diagram in the Quarto book (ADR-096, 2026-11-08)

No live fetch exists or is planned — StarUML has no headless/CLI export; the bridge needs the GUI
app running. The workflow is manual, same as any other diagram change: export via
`staruml_export_diagrams` after a model change (already routine, §3's "Diagram export" note),
commit the PNG to `docs/UML/diagrams/`, then reference it from the `.qmd` page with:

```markdown
::: {.lightbox}
![<diagram id>: <one-line question it answers>. Source: `docs/UML/app.mdj`, package `<space>`
(ADR-096 — StarUML trial mode watermarks this image; a clean re-export follows once
licensed).](../UML/diagrams/<filename>.png)
:::
```

The `::: {.lightbox}` wrapper matches the project's existing Mermaid convention
(`rules_documentation_aesthetics.md §5`) so the image gets the same click-to-zoom. Used this way
2026-11-08 to replace all 4 Mermaid blocks across 3 `.qmd` pages — Mermaid was not merely
"rendering poorly" as first reported, it was not rendering at all in this Quarto book config (0
SVGs produced, raw `graph TD` source dumped as visible text; confirmed by inspecting the rendered
HTML directly). One block (BLUEPRINT's lineage-branching diagram) had no 1:1 UML match and became
a plain table instead of a forced-fit diagram.

## Sources

[arc42 sections](https://examples.arc42.org/sections/), [C4 model](https://c4model.com/), [C4 modelling guide](https://barkingiguana.com/writing/the-workshop-c4-modelling/), [Kruchten 4+1](https://arxiv.org/pdf/2006.04975), [views and viewpoints](https://btabok.iasaglobal.org/btabok_3/capability-descriptions/views-and-viewpoints/).

**Added 2026-11-11 (HOME filters, issue #56):** `HOME-FILTER-FLOW` (as built: staged and applied
filters, what each consumer does, audit and export) and `HOME-FILTER-SCOPING` (concept: lineage cases
L1 T1=T2=T3, L2 T1=T2 with T3 different, L3 all different; red nodes = scope decisions still open).
Both are flowcharts in the HOME package. Concept text: `.claude/design/home_filter_scoping_concept.md`.
Still to draw: the lineage object diagram of `1_test_data_ST22_dummy` and the cross-dataset sequence.
