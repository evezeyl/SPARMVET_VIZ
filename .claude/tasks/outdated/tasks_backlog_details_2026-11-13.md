> **OUTDATED (2026-11-13): original text of the backlog tasks that were shortened, merged or removed in the triage of 2026-11-13.** Each entry says what happened to the task. Nothing here is an instruction.

### UNDO-WIRE-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **UNDO-WIRE-1** `[sonnet/medium]`: wire `app/handlers/blueprint_handlers.py`'s `_undo()` to a real "Undo" button in the BLUEPRINT IDE (found while resolving `DEAD-CODE-REVIEW-1`). The capture/persist side (20-step deque, draft save/restore) already works; only the trigger is missing. Needs Eve's call on where the button goes (toolbar? keyboard shortcut?) and whether it should also need the standard audit/reason gate or not (it reverts `logic_stack`, not T3 audit nodes, so probably not).

### PIPELINE-WARNING-SURFACE-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **PIPELINE-WARNING-SURFACE-1** `[sonnet/medium]`: the 4 `severity="warning"` `PipelineError` constructions that never raise (`ingestor.py` ×2 incl. the documented "Silent Skip Warning", `viz_factory.py` ×2) print to console and nowhere else — found while closing `PIPELINE-ERROR-WIRE-2` (ADR-095 §7, deliberately scoped out). No exception to catch, so `capture_entry()`'s pattern doesn't apply; needs `DataIngestor.ingest()`/`VizFactory.render()` to return or collect warnings instead, then a caller to surface them (likely `data_import_panel` / `notification` surfaces per their own `surface=` field). Needs a design pass on the return-value shape before implementing — not a quick fix.

### TEST-INGESTION-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **TEST-INGESTION-1** `[sonnet/medium]`: `libs/ingestion/tests/` has zero pytest-discoverable tests — only `debug_ingestor.py` (an argparse CLI debugger, not pytest-named) and `ingestion_integrity_suite.py`. `pytest libs` silently runs nothing for this library; every other lib has real `test_*.py` files (found while resolving finding F-11, `.claude/tasks/uml_findings.md`). Needs a design pass on what `IngestorFactory`/`ConfigManager` test coverage should look like before writing it — not a quick fix.

### BP-VALIDATE-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **BP-VALIDATE-1** `[sonnet/low]` (narrowed 2026-11-08, bookkeeping check while verifying independent tasks — the original scope is done via `VALIDATE-UI-1`: the "Validate data analysis recipe" button exists, runs both `validate_data_analysis_recipe` (structure) and `validate_data_analysis_recipe_data` (data vs contract)). **Still open:** `_handle_upload_replace`/`_handle_upload_append` in `blueprint_handlers.py` (~line 1051/1066) parse the uploaded file's wrangling nodes with zero validation — neither check runs on upload, only when the user later clicks Validate by hand. Wire the same two headless checks into both upload handlers before the nodes are added to `logic_stack`.

### EXPORT-CHECK-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **EXPORT-CHECK-1** `[sonnet/medium]`: Export test by hand in the app. Automated since 2026-11-06 (`app/tests/test_export_download.py`, real download in the qa app features): keys recorded in README (points 3), data files exist, no `_ERROR.txt`, no My view content on Result (7 partly), export refused after a data change. Still by hand: points 1, 2 (compare with the screen), 4-6, 8, 9. What to look for, with the data analysis recipe and a data analysis recipe with a `tier2` step:
  1. Plot in the bundle equals the plot in HOME "Result (T2)": same rows, same picture. With a `tier2` step the bundle plot must NOT look like T1.
  2. `data/<ds>/T1_data.tsv` equals the Raw view; `T2_data.tsv` exists only when the join has `tier2` steps and equals the Result view (row count, columns).
  3. README and `report.qmd` show: data analysis recipe SHA256 (file set), data batch hash, `tier1_key` and `tier2_key` per dataset ("none (T2 equals T1)" when no tier2). The PNG metadata has `sparmvet:tier1_key` / `tier2_key`.
  4. Same keys as the stored parquet files (`sparmvet_tier1_key`, `sparmvet_tier2_key` in the metadata of `anchors/*.parquet`).
  5. Change one thing and export again: a Tier 2 step (only tier2_key changes, plot changes), an included file (tier1_key and data analysis recipe hash change), a data file (data hash and tier1_key change). Nothing exported may come from before the change.
  6. Move a step from tier2 to tier1, export: no `T2_data.tsv`, no `anchors/<ds>__T2.parquet` left.
  7. Exploration filters (Apply, not sent to audit): never in the bundle, from any view; audited steps: always (see RT-15 to RT-17).
  8. App features without `interactivity_enabled` (pipeline-static): export works and shows the Result.
  9. Edge: join with no tier2 steps; data analysis recipe with two datasets (each its own keys); a failing plot writes an `_ERROR.txt` and the other plots are still exported.

### DEPS-REVIEW-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **DEPS-REVIEW-1** (issue evezeyl/SPARMVET_VIZ#35) `[opus/medium]`: 61 outdated packages, 11 major (polars 1.40 to 2.1, pyarrow 24 to 26, pillow 12 to 13 ...) from `audit_package_deps.py`. Polars 2 first: ADR-035 parity audit of `libs/transformer/src/transformer/actions/`, run the full suites on a branch, then the others.

### BLUEPRINT-AGENT-API-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **[@user] BLUEPRINT-AGENT-API-1** (reminder set 2026-11-07, revisit around 2026-11-14 when Claude API credits are available): Set up the `claude_api` backend for the BLUEPRINT AI agent (ADR-076). Today only `claude_cli` and `disabled` are implemented — `make_adapter()` in `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:399-402` degrades any other backend (including `claude_api`) to `DisabledAdapter` with "not implemented in Phase 1". Once credits are available: implement the `claude_api` adapter path (uses `ANTHROPIC_API_KEY`, see `rules_app_features_flags.md` consequences table), so `developer`/`qa` app features can choose `claude_cli` (uses the subscription, via the installed Claude Code CLI) or `claude_api` (uses metered credits) depending on which is cheaper/available at the time.

### HELP-FROM-DOCS-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **HELP-FROM-DOCS-1** `[sonnet/medium]`: later (Eve, 2026-11-07). The help is not built yet; it is to be built from the documentation (there was an earlier discussion, find it first). `app/modules/help_registry.py` is imported by nothing today (finding F-20): wire it in or remove it as part of this.

### DOC-TIER-PROSE-REFRESH-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **DOC-TIER-PROSE-REFRESH-1** `[haiku/low]` `[doc-sync]` (found 2026-11-08, ADR-096 work — replacing the 4 broken Mermaid diagrams with UML embeds surfaced this, didn't fix it): the **prose** around `docs/foundations/data_tiering_adr.qmd` and `docs/appendix/data_lifecycle_theater.qmd` is stale independent of their (now-fixed) diagrams — module names like `Summarizer (performance/aggregation.py)` and `Anchor (persistence/anchor.py)` don't match current code (`DataOrchestrator`/`DataAssembler`), and `data_lifecycle_theater.qmd`'s own "Tier 3 / Active Pane" terms predate ADR-085/086's "My view" naming. The two pages also substantially duplicate each other (same 3-tier concept, two different cooking-metaphor write-ups) — `rules_documentation_aesthetics.md`'s DRY rule says pick one. Rewrite the prose, and decide whether to merge the two pages or keep them distinct with a clear reason why.

### DEMO-USERS-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **DEMO-USERS-1** `[sonnet/medium]`: functionality demo for users, most of them not developers (Eve, 2026-11-07; work on it after the fixes). Show the interface and what they can do: get the graphs, filter data, navigate the plots of one data analysis recipe, select another data analysis recipe and see the UI build itself. Briefly show what can be switched on and off: (1) fully static with a custom logo (`pipeline-static` plus a deployment with branding), (2) possibly a pipeline with some data exploration (`pipeline-exploration-simple`), (3) everything else, audit and so on, with the full configuration Eve uses for development (`developer`). A separate short demo for interested developers is possible. Check first that each of the three starts with the logo and data wanted.

### TOOLS-UML-0: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **[@user] TOOLS-UML-0** (after live app testing; first step of the TOOLS / UML chain): Decide the StarUML licence before TOOLS-UML-1. Check: (a) official StarUML price and edition (a third-party site listed Professional at about 199 USD per user, VAT excluded; unverified); (b) whether the StarUML MCP server works on the free trial or needs the paid licence (not found in docs, unverified); (c) the 30-day trial may NOT have started yet (Eve has not opened the app; notes in `my-mentoring` say 2026-10-08, probably wrong); start it only when ready to do TOOLS-UML-1; (d) install StarUML >= 7.0.0 and confirm Node >= 22. Eve decided in principle to buy, because the MCP lets the agent and Eve draw diagrams together.

### UML-FAQ-DIAGRAMS-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **UML-FAQ-DIAGRAMS-1** `[opus/medium]` (Eve, conversation preserved from `issue-drafts/tmp.md`, 2026-11-08): wants a new UML section — a "FAQ"-style set of diagrams, more human-oriented than the existing packages, for explaining the app to colleagues. First candidate: a simple bubble-style diagram answering "what does maximizing efficiency actually mean" — light Shiny (keep reactivity thin), send computation to Polars not the UI layer, don't recompute when nothing changed (the fingerprint/cache-key check). If possible, link it to the real architecture diagrams (SEQ-OPEN already covers the mechanism precisely but reads as too technical/developer-facing for this purpose, per Eve: "a bit outside of the architecture and more for me to explain to my colleagues"). Needs a design pass: where does this package live in `app.mdj` (new top-level package, e.g. "FAQ" or "Explainers", separate from HOME/GALLERY/BLUEPRINT/TEST_LAB/Structure/Requirements/Behaviour/Data and configuration/Architecture), what diagram type fits a "bubble" visual (UML doesn't have a native bubble/mindmap type — closest options are a heavily-simplified Use Case diagram reusing ellipses non-technically, or a plain image/graphic embedded as a diagram asset), and how it links back to the technical diagrams (StarUML hyperlink tag, or just a caption cross-reference in the Quarto embed).

### UML-MAIN-EMPTY-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **UML-MAIN-EMPTY-1** `[haiku/low]`: the top-level `Model` package's own diagram ("Main", `UMLClassDiagram`) has zero elements — it has been empty since the project was first inspected this session (confirmed again 2026-11-08). Eve asked: "should it contain something?" Needs her decision: delete the diagram (if `Model` is just a container with no content of its own, which matches the current structure — HOME/GALLERY/BLUEPRINT/TEST_LAB/Structure/etc. are themselves top-level packages, not children of `Model`), or give it a real purpose (e.g. a project-wide index/legend diagram, a C4 System Context pointer, or move it under `UML-FAQ-DIAGRAMS-1`'s new package as a landing page).

### RESEARCH-HELP-1: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **RESEARCH-HELP-1** `[sonnet/medium]`: Gallery keyword enrichment + AND/OR search. **Design settled (2026-05-22):** add `keywords: [list]` to `info:` block in each `data_analysis_recipe.yaml` (35 examples); update `refresh_gallery.py` to include keywords in `gallery_index.json` pivot entries; add a text search input to the Gallery UI (split on spaces → AND-intersect tokens across keywords + existing taxonomy fields). Three keyword layers: (1) statistical/methodological synonyms (`median`, `quartile`, `IQR`, `spread`, `beeswarm`, `ridge`, `dumbbell`, `before after`, `cumulative`, `paired`, `stacked`, `proportional`, `small multiples`, `faceted`, `overlay`, `individual points`, `raw data`, `regression`, `fit`, `confidence interval`…); (2) data/use-case terms (`time series`, `temporal`, `longitudinal`, `rate`, `prevalence`, `incidence`, `frequency`, `quality control`, `normality`, `heterogeneity`, `exploration`…); (3) domain terms (`AMR`, `antimicrobial`, `resistance`, `MIC`, `susceptibility`, `surveillance`, `epidemiology`, `pathogen`, `species comparison`…). No fuzzy matching needed — AND/OR on exact tokens is sufficient for this gallery size. Step 1: enrich all 35 example `info:` blocks. Step 2: one-line `refresh_gallery.py` change. Step 3: gallery UI search widget.

### UX-CSS-DEMO: shortened (kept; details that the rebuild makes wrong are not repeated)

- [ ] **[@user] UX-CSS-DEMO**: Review `assets/demo/demo_vetinst.css` after default theme is finalised.

### CONFIG-AGENT-BACKENDS-1: removed: merged into BLUEPRINT-AGENT-API-1

- [ ] **CONFIG-AGENT-BACKENDS-1** `[opus/medium]`: implement the `claude_api` and `local` backends of the BLUEPRINT agent (ADR-076 phase 2); until then `blueprint_agent.model`, `.endpoint`, `.api_key_env`, `.gallery_awareness` stay in the templates marked "reserved, not implemented".

### DEPS-UPGRADE-1: removed: merged into DEPS-REVIEW-1

- [ ] **DEPS-UPGRADE-1** `[sonnet/low]` `[deferred - monitor only, decided by Eve 2026-11-05]`: Dependency upgrades are frozen until the app is at a more advanced stage (no minor-version change before then). Monitor, do not apply. Known: plotnine 0.15.4 installed, 0.15.9 available (patch releases within the allowed range `>=0.15.4,<0.16.0`; still no pie or polar coordinates, see fork issue #19); matplotlib 3.10.9 -> 3.11.2 and mizani 0.14.4 -> 0.14.6 also available. When the freeze ends: upgrade one library at a time, run the full test suite and the plot render test (`app/tests/test_render_every_plot.py`), and compare the images. Open point: there is no lockfile for the main app, so a fresh install may already pick a newer patch version than the one tested (a lockfile, for example `uv.lock`, would pin it; packaging is Eve's to do by hand).

### HELP-CONTENT-REFRESH-1: removed: done: gallery, blueprint and test_lab help were rewritten (commit 1964c9c, re-verified 2026-11-13); `home.md` is covered by HOME-EXPLORE-6 (P12)

- [ ] **HELP-CONTENT-REFRESH-1** `[haiku/low]` `[doc-sync]` (found live by Eve, 2026-11-08, HOM-55 in `test_plan_home_2026-11.md`): all 4 of `app/src/help/*.md` (the `? Help` modal's quick-reference content, HELP-INLINE-1 — separate, simpler mechanism from `HELP-FROM-DOCS-1` above) are stale. `home.md` describes the pre-ADR-086 tier toggle (superseded by HOM-45's Plot-to-show/Data-to-show strip, months ago). `gallery.md` actively describes **"Send to Blueprint,"** removed this session (ADR-093) — actively misleading, not just outdated. `blueprint.md`/`test_lab.md` use pre-rename "pipeline" vocabulary; `test_lab.md` lists only 4 of the 8 real tools (missing Reformatter, ID Reconciliation, Scaffolding, Anonymiser). Rewrite all 4 to match current reality.

### TOOLS-UML-2: removed: merged into UML-DOCS-1

- [ ] **TOOLS-UML-2** (decided in `.claude/design/uml_model_plan.md` D1: all in StarUML, `docs/UML/app.mdj`; write it into the rules with TOOLS-UML-4) `[sonnet/low]`: Diagram location policy. Decide and write into `rules_documentation_aesthetics.md`: `.staruml` source files and exports (SVG, PNG) under `docs/` (suggest `docs/diagrams/`), exports referenced from the `.qmd` docs so GitHub shows them (GitHub does not render `.staruml`); Mermaid stays for small inline diagrams (existing `::: {.lightbox}` rule). Add `.staruml` handling to `.gitignore`/`.aiignore` only if needed.

### TOOLS-UML-3: removed: done: the UML model exists (about 30 diagrams in `docs/UML/app.mdj`, exports in `docs/UML/diagrams/`); further diagrams are UML-HOME-REDRAW-1 and UML-FAQ-DIAGRAMS-1

- [ ] **TOOLS-UML-3** (plan: `.claude/design/uml_model_plan.md`, findings: `.claude/tasks/uml_findings.md`; plan accepted, in progress) `[opus/high]` then `[sonnet/high]`: First diagrams of SPARMVET_VIZ with StarUML MCP, one at a time, Eve reviews each: (1) C4 context + container, (2) activity diagram of the yes/no decision logic, (3) sequence (user click -> filter -> plot), (4) SysML requirement diagram linked to requirement IDs. Export to `docs/diagrams/`, reference in docs. Reference: `OBSWORK/60_ME/CAREER_TRANSITION/00_context/Learning_UML_for_SPARMVET_VIZ.md` (read only if Eve grants access).

### TOOLS-UML-4: removed: merged into UML-DOCS-1

- [ ] **TOOLS-UML-4** `[sonnet/medium]`: replace the Mermaid diagrams in the 8 `docs/` pages by StarUML images, and change the Mermaid line of `rules_documentation_aesthetics.md`. After the licence is bought (the trial puts a watermark on images). Decided by Eve 2026-11-07.

### _user_Taxonomy_Data_Audit_Verify_: removed: merged into GALLERY-RECIPES-1 (the checker verifies the taxonomy terms against the specification)

- [ ] **[@user] Taxonomy Data Audit**: Verify/correct tags in `assets/gallery_data/*/data_analysis_recipe.yaml` against `assets/gallery_data/TAXONOMY_CHEATSHEET.md`.

### Discuss_Aesthetics_automation_visual: removed: merged into UX-PLOTSTYLE-1

- [ ] Discuss - Aesthetics / automation visuals -> capture and adding to T3 audit ? possibilities ? Consequences ? Gating ?  

### _FEATURE_Label_x_y_axis_adjustment_: removed: merged into UX-PLOTSTYLE-1

- [ ] **[FEATURE]** Label x/y axis adjustment module — edit title, policy change, color changes, points display — registered in audit. Large feature, grant-exploration candidate.

### _TO_DISCUSS_Lab_script_Extract_pil: removed: merged into TESTLAB-IDEAS-1

- [ ] **[TO DISCUSS]** Lab script: Extract pilot data analysis recipe (reconstitution of lineage) — improve reusability.

### _TO_DISCUSS_Lab_script_Create_tool: removed: merged into TESTLAB-IDEAS-1

- [ ] **[TO DISCUSS]** Lab script: Create tool-specific data analysis recipe (e.g. single-sheet variant).

### _TO_DISCUSS_Lab_script_Combine_dat: removed: merged into TESTLAB-IDEAS-1

- [ ] **[TO DISCUSS]** Lab script: Combine data analysis recipes — format detection, common datasets, branching.

### UX-PLOTSTYLE-1: kept, with two ideas merged into it

- [ ] **UX-PLOTSTYLE-1** `[sonnet/medium]` `[deferred — eventual enhancement]`: The **Plot Style** panel (T3 `aesthetic_override`, `audit_stack.py` `aesthetic_style_panel_ui`, added 2026-05-11) is **not mounted** in HOME since 2026-11-05 (fork issue #15): letting users change in HOME what the data analysis recipe defines is too much for now, and using it broke the plot (test plan HOM-47). Code kept, unused, with a pointer comment at the mount point (`home_theater.py`). Later: find why it broke the plot, then decide whether to bring it back. Plot style that belongs to the data analysis recipe is authored in BLUEPRINT (separate). ADR-082 unchanged.
