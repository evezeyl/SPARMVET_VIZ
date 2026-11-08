# Cross-cutting concepts

Rules and patterns that apply across the whole app, not to one user space. No diagram shows these
well; they are listed here with where they are decided and where they are enforced.

## Configuration resolution

Three independent files (deployment, app features, data analysis recipe), each with a resolution
order from a launch variable down to a default. See `DM-CONFIG`, ADR-091, ADR-092.

- Precedence: launch variable (`SPARMVET_DEPLOYMENT` / `SPARMVET_APP_FEATURES` /
  `SPARMVET_DATA_ANALYSIS_RECIPE`) > the deployment's default > nothing.
- A hidden data analysis recipe selector with no name given is a fatal startup error, not a silent
  fallback to the first recipe found.
- Old names (the renamed launch variables, deployment keys, app features flags, session keys) are
  refused with a message naming the new one — `app/modules/renamed_keys.py`,
  `libs/utils/src/utils/legacy_keys.py`. Never a silent alias (ADR-077).
- A deployment-level `app_features_override` can lock a flag regardless of the app features file
  (used for automated-pipeline deployments where data is always pushed, never uploaded).

## Fail-fast over silent suppression (ADR-077)

A configuration error that would produce a wrong result stops the app immediately, with a
`DeploymentError`: component, problem, location, fix, who should act, reference. No code path repairs
a bad configuration behind the user's back. Group B/C flag cascades (interactivity, import) are the
one exception: they are soft (forced false with a printed warning), because many existing templates
inherited inconsistencies there before the rule was written; Group D (Blueprint IDE, agent) cascades
are fatal.

## Error handling at runtime

Separate from startup configuration errors: a `PipelineError` carries what broke, where, the fix,
and who should apply it (ADR-078, ADR-079). It is built at all 7 production sites that can fail
mid-session — but every one of them used to throw the rich version away before it reached a
catcher, raising a plain `TransformationError`/`IngestionError`/`VisualizationError` with only a
message instead (`errors.py`; found 2026-11-08, ADR-095, while closing `PIPELINE-ERROR-WIRE-2`).
`SPARMVET_Error` now carries the original `PipelineError` through the raise (an optional
constructor kwarg, no breaking change to any existing catch site), and a shared `capture_entry()`
helper reads it back. As of 2026-11-08 this reaches the user at every production site that can
raise: HOME's "Pipeline Issues" panel (data materialization and VizFactory render, including the
Comparison Mode reference plot) shows `fix`/`who`, not just the problem; BLUEPRINT's three
recipe-load/YAML-parse failures show inline, right where the error happened; T3 Apply's
gatekeeper-blocked message and a failed session-ghost-save both now include the fix text (the
ghost-save one is a real, previously-silent gap: it used to fail with zero warning, meaning T3
state was lost on refresh without the user ever knowing); export bundle error stubs include the
fix too. Not done: the 4 `severity="warning"` constructions that never raise (`ingestor.py`,
`viz_factory.py`) still only print to the console — no exception to catch means a different
mechanism is needed (`PIPELINE-WARNING-SURFACE-1`). None of this ever calls `sys.exit` once the
app has started — that part has always held.

## Provenance

Every stored artifact that can be compared against another run carries the keys it was built from:
`data_analysis_recipe_sha256` (file set), `data_batch_hash` (content hash of the source files),
`tier1_key` / `tier2_key` (chained, ADR-089). These appear in the export bundle's README and
`report.qmd`, and are embedded in exported PNG/SVG metadata. The export's key check
(`REQ-VIZ-EXP-01`) exists because these keys can be compared cheaply before any heavy recomputation.

## Reactive write discipline (ADR-045 companion, `ui_implementation_contract.md` section 14)

Four rules, found the hard way from real bugs this session traced through `COM-REACTIVE`:

- **R1** A `@render.*` function never writes a reactive value — only reads.
- **R2** State writes live in a dedicated `@reactive.Effect`.
- **R3** An effect that writes a value it also reads must guard with an equality check, or it loops.
- **R4** Do not read an input inside the render that mounts it, or the widget destroys and rebuilds
  itself on every interaction, wiping transient state (the column-drop audit bug, Phase 22-I).

## Flag-driven gating, never a name comparison (ADR-053)

Every UI or logic decision reads `bootloader.is_enabled(flag)`. Comparing the app features name
against a string (`if app_features in ("developer", "qa")`) is a protocol violation: it makes a
custom combination of flags invisible to the app. Checked by grep in the audit routine registry; the
`flag` tag in the UML model is checked against the real flag names by `audit_uml_model.py`.

## The Two-Category Law (ADR-045)

Every file in `app/` and in `libs/` is either pure logic (importable headless, no Shiny) or Shiny
reactive wiring (`@render.*` / `@reactive.*`, never imported from a headless context). `PKG-TIERS`
and `C4-COMP-HOME` draw the boundary; mixing the two in one file is a protocol violation.

## Tier isolation (ADR-085)

T1 and T2 are permanently pure in every configuration: no exploration filter and no audit-committed
node ever renders there, regardless of flags. Only "My view" (T3) reflects either. Any new render
function that reads filter or audit state must apply the same gate (`tier_toggle.get() == "T3"`).

## Security (deferred — see risks)

Not designed yet beyond what deployment-time file permissions give. `eval()` runs data analysis
recipe text as Python with few limits, and the app has no login. Tracked as its own task,
`SECURITY-DEPLOY-1`, for before any shared or multi-user deployment — see
`risks_and_technical_debt.md`.
