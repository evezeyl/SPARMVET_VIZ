ARCHITECT / SECURITY-DEPLOYMENT VIEWPOINT, engines round. Recommendation only; nothing decided or built. Labels: V-read, V-run, R-reasoned. Tags: DECIDED / CONFIRM / OPEN / MINE. Scratch: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/engines/architect/probe.R

## 1. Present state (five sentences)
1. `data_engine` and `plot_engine` are required top-level keys (DEC05, recipe_format_spec.md:92, :226-227; D-0029, D-0033 DECIDED). Each has exactly one legal value (libs/utils/src/utils/engines.py:21-25). Both are checked at load (recipe_check.py:218-221, T06). `plot_engine` alone is read at draw time, where it only refuses an unbuilt engine (viz_factory.py:113-126, V8). `data_engine` is read by writers and the checker only, so Polars is not switched by the key (V-read, scout plus my grep).
2. Both keys already sit in the Tier 1 cache material, because only info, analysis_groups, plot_defaults and plots are excluded (cache_keys.py:51, :80-85). That contradicts the spec's "fingerprint later" (spec :226). `engine_fingerprint()` holds only the cache version, polars and transformer, with no plotnine (cache_keys.py:70-72, V-read).
3. Yes, there is a default theme: `theme_bw` (plot_config_resolver.py:47; viz_factory.py:135), and `plot_defaults.theme` overrides it. A plot's own `theme` and `palette` beat `plot_defaults` (resolver:617-620, :644-647). So "a default overridden per plot" already exists for theme and palette.
4. `plot_defaults` keys `default_font_family`, `facet_panel_spacing`, `legend_position` and `optimisation` are accepted, but nothing reads them. They appear only in the allowed-key lists (resolver.py:68-69) and an error message (viz_factory.py:279). `default_font_family` is set in shipped recipes (V-run grep). This is a silent no-effect and conflicts with P1 "executed, displayed, or refused".
5. R 4.5.3 exists on this machine, but ggplot2, dplyr, arrow, jsonlite, svglite and ragg are all absent (V-run). Bare `Rscript` starts in 0.27 s (V-run). `assets/containers/Dockerfile:32-51` has no R (V-read). No ledger line mentions R (scout). The only record of the idea is agent text: home_observations_and_future.md:37-38, 46-60 and r_backend.md, both EXPLORATORY.

## 2. The design: a default plus an override per block
The override is itself a pattern Eve decided for theme and palette (point 3 above). The question is which blocks may carry it.

| Place | Looks like | Checker must know | Keys / fingerprint | Engine boundary | What breaks |
|---|---|---|---|---|---|
| A. Plot entry | `tree_1: {data: isolates, plot_engine: r-ggplot2, spec: ...}` | allowed values per scope; all components in the spec carry that engine's prefix; the engine can read the table; `plot_defaults` meaning for that engine | the plot is drawn from the T3 frame, not cached. Fingerprint needs the R and package versions (only when used) | one-way: Parquet in, image out. Dispatch in `app/` (Tier 3), engine library by id | six `render` call sites (below); plot_defaults is plotnine-shaped; the cascade is in viz_factory |
| B. Schema or join (collection) | `wrangling: {data_engine: r-dplyr, tier1: [...]}` | the steps in that list all belong to that engine; audit steps may not enter | tier1_key is one key for the whole recipe (home_observations:29), so a per-collection engine needs per-collection keys | two-way handover through anchors (anchor.py:88-161) | dtype round trip; the audit's "remove from all tables" steps are `modif_filter` (Polars) |
| C. Tier list (T1, T2, T3) | `steps: {tier2: {engine: ..., list}}` | same as B; T3 is written by the audit, so Polars only | tier2_key already chains from tier1_key | the anchor files `<name>__T2.parquet` already exist (orchestrator.py:26-29) | T3 cannot be R |
| D. Join | a join is a collection with its own tier lists (7.6) | same as B | same | same | a join between two engines' outputs needs a stated handover |
| E. Step | `- {action: dplyr_filter, engine: ...}` | prefix equals key (redundant) | per-step keys do not exist | a conversion at every step | see "not allow" below |

Plot call sites that must all go through one dispatcher: home_theater.py:522 and :594, export_handlers.py:1171, wrangle_studio.py:707, gallery_examples.py:119, assets/scripts/golden_baseline.py:117 (V-run grep). The "one code path" claim breaks if even one stays hard-wired to `VizFactory`. HOME would show R while the export draws plotnine. A test must fail if any call site bypasses the dispatcher.

Clear Lines (rules_runtime_environment.md section 4): a second plot library cannot import `viz_factory`, so the cascade and `plot_defaults` logic would be duplicated or moved to `utils`. `utils.engines` may hold names, roles and prefixes only, no R import. There is already a clean seam: the checker receives its catalogs injected from `app/` (data_analysis_recipe_validator.py:120-123), so each engine library can supply its own catalog (MINE, reasoned).

## 3. Naming
- The prefix is the engine for actions. D-0036 says "an action that is not Polars must be seen by its name". `modif_` and `step_` name no engine today; they mean "Polars idea" (DEC31). With R they become ambiguous, and `modif_filter` is the audit's own action (DEC39).
- My reading: the registry field `engine` is the truth. The block's engine key is the check that the prefix matches, and a test already exists in this spirit for plot components (ADR-106 note). An engine key per step would be redundant.
- Family names (OPEN, Eve): `dplyr_` and `ggplot2_`, parallel to `polars_` and `plotnine_` (library name), versus an `r_` family. The value format `language-library` (`r-ggplot2`) is already DEC05's shape.
- `modif_` and `step_` need one decision: either they carry the engine (`modif_dplyr_filter`), or they stay and the registry field names the engine. I would not leave the prefix to guess.
- Plot rename (D-0091, D-0210 to D-0214): build `plotnine_` so the prefix and the engine come from one registry field, not a hard-coded string in about 20 places. D-0214 says names written as values (`geom: geom_area`) stay plotnine's names. For ggplot2 they differ in places (`geom_bin2d` and `geom_bin_2d`, D-0213), so those values are per engine. Do not let one spec be drawn by two engines. A transpiler is the dual-renderer divergence that r_backend.md Option B warns about.

## 4. How R is called (security first)
Rule check: "the recipe is data, never code" is today an allow-list, not "no eval". Formulas are parsed with `ast` and then run by `eval` with empty builtins (formula_check.py:289, :322). The known limit was accepted (ADR-100 point 10, D22/D23 M86). DEC42 and DEC44 forbid recipe-chosen paths and recipe-run code.

| Way | For | Against | Failure / time |
|---|---|---|---|
| `Rscript --vanilla` subprocess plus Parquet | process isolation, no shared R state, survives a crash, one fixed script, easy timeout and no-network | spawn per call; needs R and packages in the deployment | 0.27 s bare start (V-run); ggplot2 and arrow load time not measured, packages absent |
| rpy2 in-process | fast | R is single-threaded with global state inside Shiny's async server; a segfault kills the app; the R code path is wider | not installed; reject (r_backend.md:51) |
| small service (plumber) | warm process | a second service, a port, auth, monitoring | later only if latency demands |

- For R, keep the rule by a registry of allowed R functions with typed parameters. The recipe supplies only a component name and JSON literals, never R text. The fixed script ships in the repo and is hashed. Arguments arrive as a JSON file read with `jsonlite`. Functions are fetched by name (`getExportedValue`) only after an allow-list check. File paths are made by the app (DEC42 spirit). No `eval(parse())` on recipe text.
- R mappings must be column names only. R expressions (`dplyr_mutate`, `summarise`) would need an R expression allow-list, which is the genuinely hard part. My suggestion: in a first version only verbs with typed parameters (select, rename, filter by `column op value`, arrange, distinct, joins).
- An "R snippet" escape hatch (r_backend.md Option C) breaks the rule outright: arbitrary file, network and `system()` access with the app's rights. It also makes the plot opaque to the checker, Blueprint, the audit and the equality tests. It would reconsider DEC44 and the "recipe is data" principle. ADR-071's second layer (who may deposit recipes) does not make it safe. I would not allow it.
- Sandbox of the subprocess: `--vanilla`, a temp working dir, a pinned `R_LIBS`, a timeout, a memory limit, no network, stderr captured.
- Deployment: Dockerfile is Python 3.12 slim with TeX and Quarto, no R. R needs a pinned R plus packages installed at build time from a dated snapshot or lockfile, never at run time (ADR-071 rule 1, air-gap). Galaxy interactive tools mean a container, so a second or larger image. The checker needs a capability probe ("this recipe needs r-ggplot2, this deployment has none") at the load gate, in the same one-error form (V7, "what, which plot, how to fix").
- Errors back to the user: capture stderr, exit code and a missing output file, and map them into one `plot_failure` message with the raw R text as detail.
- Traps in the R path that exit 0: R warns "removed N rows containing missing values" on stderr, so it must reach the user (nothing silent). Fonts and devices differ from matplotlib. Seeds: the same recipe seed gives different jitter and sample in R than in numpy (D-0052 "seed fixed holds" means a different picture per engine).

## 5. Export and reproducibility bundle
- Per engine used: id, library versions (R, ggplot2, dplyr, arrow), the container image digest (the real pin; home_observations:31 point g), the lockfile or `sessionInfo()`.
- Plotnine today: export_handlers.py:104 and :203 record plotnine only. Export line for `plot_engine` is OPEN (tasks.md:365).
- The input Parquet hash, and the exact R code or parameters run.
- OPEN (MINE): a generated R script that is also the run (one path, but quoting must be fuzz-tested with hostile strings), versus JSON read by a fixed script plus a separate generated script (safer, but two paths that can disagree). A03 (ledger :244) is the recipe-to-code research, still not decided.
- The data the plot received must equal the exported T3 table. A dtype round trip (Polars to Arrow to R) needs a test per dtype (Enum, Categorical, Datetime tz, Decimal). Not run: no `arrow` in R here.

## 6. Decide now and what can wait
Now (cheap, avoids a break):
1. Keep the two keys as recipe defaults. DECIDED (DEC05); no change.
2. Key fact for Eve: spec 4.1 (recipe_format_spec.md:243) says a key added or an engine name added changes `spec_version`. So an override key or `r-ggplot2` later means format 2 plus a migration of 50 recipes (16 + 34). The machinery exists (DEC43), and the change is mechanical.
3. Alternatively Eve could classify engine names as an "open vocabulary" (like gallery terms, 4.1): then adding an engine value is not a format change. This is a one-line change to DEC05 and 4.1.
4. Reserved-but-refused key now: DEC02 already refuses unknown keys, so reserving adds a key that executes nothing, which is a half step by P1. I would write the planned places in the spec as a note instead.
5. State plainly: the plot override is the small, safe case; the data-engine override is a different, bigger feature.

Can wait: the registry table (home_observations:46-60), `modif_` / `step_` engine naming, R expressions, the snippet question.

Rows and ADR points that would change: spec DEC05, 4.1, section 4 rows :226-227 and plot-entry keys in 7.7 and 7.8 (`plot_defaults` meaning); ADR-100 point 1; ADR-106 V8 and the V1-B note; ADR-071 (R in the container); D-0091 and D-0214 (prefix and values).

Would NOT allow: an engine per step (conversion at every step; Polars's lazy plan and optimiser are lost; the step list is the audit record and cannot be previewed; the prefix already says it); R in tier 3; an R snippet; rpy2; one spec drawn by two engines.

## 7. Traps, honestly
- The six `render` call sites above (single dispatcher; a test must fail on a bypass).
- The audit is Polars-only. An R data engine and "remove sample from all tables" conflict in the lineage.
- `plot_defaults` is plotnine-shaped, and the four no-effect keys already show the format promises more than it delivers. Do not add an engine on top before that is cleaned (P1).
- Fingerprint: put R versions in only when R is used, otherwise every existing cache key changes (the `ENGINE_CACHE_VERSION` bump rule).
- Version drift: ggplot2 majors change defaults, so only the container pin makes a picture reproducible (R-reasoned, my recollection, not checked).
- What an audit or test would not catch: the font and RNG differences, a stderr warning at exit 0, and R package versions drifting inside an unpinned image.
- Testable without a browser: the registry, the checker, the dispatcher (with a stub engine that writes a fixed PNG), the quoting of the JSON, the capability probe. The dtype round trip and real renders need R plus packages, so they must be environment-gated tests.

## 8. Options (my recommendation is labelled)

| Option | For | Against | Effort | Risk | Evidence |
|---|---|---|---|---|---|
| 1. Do nothing now, keep two keys | zero cost; format 1 untouched | later format 2 plus migration; the question stays open | none | low | spec :243 |
| 2. Decide the principle and vocabulary class now, build nothing | no break later; planning for Eve | an unbuilt promise; the keys stay silent in `plot_defaults` | small (spec text) | low | spec 4.1, DEC05 |
| 3. Plot-entry override first, later | one-way boundary, no audit conflict; natural for ggplot2 | six call sites; dispatcher; R in the container | medium | medium | call sites, viz_factory.py:113-126 |
| 4. Data engine per collection or tier | dplyr possible | dtype round trip; audit conflict; per-collection keys | high | high | anchor.py, home_observations:29 |
| 5. Snippet escape hatch | fastest to "run my R" | breaks DEC44 and recipe-is-data | low | very high | r_backend.md Option C |

MY RECOMMENDATION (label: MINE): option 2 now, then option 3 later. The plot engine override at the plot entry only, with the rename (D-0091 and D-0210 to D-0214) built so that the prefix and the engine come from one registry field. Option 4 only when a concrete use appears. Options 5 and per-step engine: no.

What Eve needs to be told to choose well:
- An engine name or a new key is a format change under 4.1 as written, and what that costs (a bump to format 2 plus a mechanical migration of 50 recipes).
- Plot override and data override are different sizes.
- R in the deployment needs a pinned image, and the picture can differ between engines (fonts, seeds).
- The R snippet breaks the "recipe is data" rule.
- The four `plot_defaults` keys that do nothing today.

## Not checked
- Time to load ggplot2 and arrow (packages not installed).
- Polars to Arrow to R dtype round trip.
- Galaxy interactive-tool requirements.
- ggplot2 version-change claims (recollection only).
- Ledger lines omitted by the scout's tool output.
- Whether DEC02 refuses an unknown key on a plot entry in every profile (checked only at viz_factory.py:218-225).
- No tests were run.
