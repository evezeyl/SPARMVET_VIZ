DEVELOPER VIEWPOINT, engines question. Labels: measured (run), read (file read), estimated (my judgement).

RECOMMENDATION
Do not build R now. Reserve the door with the smallest recipe-format change (item 6). Only one of her wishes, ggplot2 as a plot engine, is a clean fit. dplyr as a data engine is not (item 5).

1. THIS MACHINE (measured)
- Rscript 4.5.3.
- ggplot2, arrow, dplyr, jsonlite, svglite, ragg, nanoparquet and polars (R) are all FALSE. Nothing is installed.
- No spike was possible: there is no Parquet reader and no ggplot2. I installed nothing.
- Floor for `Rscript -e '1'`: 0.256 s wall (one run).
- Error text and exit code, from the bare R I could run:
  - A missing package returns "Error in library(ggplot2) : there is no package called ...", then "Execution halted", exit 1.
  - `stop("col missing")` returns "Error: col missing", exit 1.
  - A missing column read with `x$b` gives NULL and exit 0. This is a silent failure. R must check columns itself, and the wrapper must read stderr and the exit code.
- Not measured: package-load time (ggplot2 plus arrow costs roughly 0.5 to 1.5 s, estimated), file sizes, the real error for a missing column in ggplot2.

2. THREE WAYS TO CALL R

| Way | Build (estimated) | Container | Shiny with several users | CI | Failure modes |
|---|---|---|---|---|---|
| Subprocess per plot | 3-5 days | r-base plus ggplot2, arrow, svglite. About +0.8 to 1.5 GB (not measured). The Dockerfile is python:3.12-slim with no R (read). | Isolated. Each plot costs one spawn, at least 0.26 s plus package load. Needs a timeout and a concurrency cap. | Needs an R job, or tests skipped when no Rscript. | Silent exit 0, a hung process, stderr that must be translated, temp files. |
| Long-lived R process | 8-12 days | Same, plus plumber | One shared R is single-threaded, so users queue. Needs a pool. | Harder: needs a service in CI | Crash and restart, state leaking between users, a second service to watch. |
| rpy2 | 4-6 days, plus unknown debugging | Same, plus a matching R and Python build | Not thread-safe. The existing notes in r_backend.md say avoid it. | Fragile | Segfaults take the whole app down. |

Lean: the subprocess. The other two cost more and fail worse.

3. ggplot2 AS A SECOND PLOT ENGINE: PIECES IN BUILD ORDER
Today `render` returns a plotnine object, and callers use `.save` and `.draw` on it. I read this at export_handlers.py:1176 and :1195, gallery_examples.py:121 and checked_plot.py:200. An R plot gives a file, not an object. The caller contract therefore has to change (piece 3).

| # | Piece | Size | Depends on | Tests |
|---|---|---|---|---|
| 1 | Engine override per plot: key in the plot spec, resolver, checker (T06 only reads the top level), cache and export keys. 25 .py files mention plot_engine, 17 of them tests (read). | medium | none | Checker cases: unknown engine, per plot, default overridden. Cache key differs. |
| 2 | Engine registry in `utils.engines`: allowed values per scope, and a refusal for a missing R. | small | 1 | Refusal text, missing Rscript |
| 3 | Return contract: an image artefact instead of a plotnine object. Touches export, gallery, HOME, qmd. | large | 2 | Export, gallery and HOME for both engines |
| 4 | Data hand-over: Parquet is already on disk (anchor.py). An R script reads it. Type checks needed (dates, categoricals, NA). | medium | 3 | A round-trip table of dtypes |
| 5 | R runner (subprocess), plus a spec-to-ggplot2 translator | large | 4 | Needs R in CI |
| 6 | Component registry for ggplot2 | large | 5 | One test per name |
| 7 | Golden baseline: a pixel match is not stable across engines, so a new baseline is needed. | medium | 5 | |
| 8 | Blueprint forms and docs | medium | 6 | |

- Piece 6: PLOT_COMPONENTS holds 191 components (measured). Each needs a ggplot2 name.
- ggplot2 parameter names can be read in R with `formals()`, but I did not run it because ggplot2 is missing.
- Parallel: 1 and 2 can run in a worktree of their own. 4 and 5 can start once 3 is fixed. 6 and 7 can run in parallel after 5. 8 comes last.
- Total estimate: about 6 to 10 weeks, including the translator for the existing recipes.

4. dplyr AS A DATA ENGINE
- Read: no code reads data_engine, so Polars is not selected by that key.
- Everything that knows Polars would have to know dplyr:
  - the transformer, with its 70 tests (read)
  - Parquet tiers (anchor.py)
  - cache keys
  - T3 audit filters (these run in Polars today)
  - the step names with the polars_ prefix
- My honest view: the cost is very large and the benefit is small. Parquet already works as the bridge, so R can read a tier and produce another Parquet file if the user wants it. A dplyr step would need its own step registry and a second audit path, so the same data and recipe could give a different result per engine.
- If it is ever built, make it a separate tier-step type, not a switch of the data engine.

5. COST OF KEEPING THE DOOR OPEN NOW (estimated)
- Smallest change: the recipe format says that `plot_engine` and `data_engine` are defaults, and that an entry may name its own engine later. The checker refuses an engine key inside a plot or Tx today. That refusal is the reservation, so it costs about 2 hours, and it only covers the spec text.
- If nothing is reserved: the later change touches every shipped recipe (48 files with 100 or more lines, read) and the migration tool, at about 1 to 2 days.

6. RISKS, RANKED
1. Silent differences between engines: the same recipe gives a different picture, and the export does not say which engine drew it.
2. An R error with exit 0, or a missing column returned as NULL.
3. Return contract (piece 3) breaking export and gallery.
4. CI and container size.
5. Dependence on an unsettled design (r_backend.md is EXPLORATORY).
I would NOT do: rpy2; dplyr as a data engine; raw ggplot2 snippets (they cannot be checked); building R before the return contract is decided.

WHAT THE USER MUST BE TOLD
- ggplot2 from R changes the return type of every plot call, not only the engine name.
- The export must record the engine per plot, and a plot drawn by R cannot be compared with the golden baseline.
- Needs a decision: the R-in-container cost (around 1 GB, not measured), versus a lighter route where she writes R outside the app and the app only reads the Parquet.

NOT CHECKED
- Real R timing and file sizes (no ggplot2).
- Image size.
- formals() reading of ggplot2.
- Parquet types in R.
- Shiny load.
- Every piece estimate is a guess.

Scratch folder only: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/engines/developer (empty).
