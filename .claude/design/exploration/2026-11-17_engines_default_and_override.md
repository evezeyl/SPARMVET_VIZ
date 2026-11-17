Exploration report. Nothing in it is decided unless a ledger number is given. Status: Nothing is decided and nothing is built (as written in the report). Written: 2026-11-17. Source: tmpAI/panel/engines/REPORT_for_eve.md. Copied here on 2026-11-17.

Paths inside the body that point to tmpAI/ working files are local (not in git) and stay as written.

---

# A default engine that a tier or a plot may override; ggplot2 and dplyr from R

Written 2026-11-17 by the coordinator from a survey and four viewpoints (data scientist, software architect with security and deployment, developer, user). This is a report for planning. Nothing is decided and nothing is built.

Your questions are in the channel (M205, M206, M207). The files behind this report are in this folder: `scout_what_exists.md`, `viewpoint_scientist.md`, `viewpoint_architect.md`, `viewpoint_developer.md`, `viewpoint_user.md`.

## The short answer

- **A default theme for all plots: yes, it exists and works.** The built-in default is `theme_bw`; a recipe sets its own with `plot_defaults: theme:`; one plot overrides it with its own `theme:`.
- **An engine per plot: yes, this is a sound feature to plan.** All four viewpoints support it. Polars prepares and stores the table as today, the audit runs as today, and R only draws from the stored table.
- **An engine per tier or per table on the data side (dplyr): possible in principle, large, and risky for correctness.** Three viewpoints say not now; the fourth says only when a concrete use appears.
- **An engine per step: all four say no.**
- **What to settle now in the recipe format is small**: one sentence in the specification. See "What to decide now".

## Read this first: what would change a result silently

1. **The same step gives different rows in Polars and in R.** Run on this machine (Polars against base R):
   - "greater than 2" on a column with a not-a-number value: Polars keeps that row, R drops it.
   - Rounding 2.675 to two decimals: Polars gives 2.68, R gives 2.67.
   - Sorting text: a different order unless the locale is fixed (`_x`, capitals, digits).
   - A join on a missing key: R matches missing with missing, Polars does not.
   - A random sample with the same seed: different rows, always.
2. **dplyr's filter drops rows with a missing value without a message.** A sample could vanish and the audit would not show it.
3. **Ids above 2^53 collide in R** unless 64-bit integers are asked for: two samples become one.
4. **The order of categories changes.** R sorts factor levels by alphabet in the machine's locale; the axis of a plot can differ on another machine.
5. **An R script can end "successfully" while something went wrong.** A missing column read as `x$b` gives nothing and exit code 0. ggplot2 writes "removed N rows containing missing values" as a warning only. Both must reach the user.
6. **A silent fall-back** (R asked, plotnine draws) must never exist.
7. **Found today, not about R: four keys of `plot_defaults` are accepted and do nothing** (default font family, facet panel spacing, legend position, the optimisation switches). Four shipped recipes set a default font that has no effect. The architect: clean this before adding an engine on top.

Not run: anything with ggplot2, dplyr or arrow. R 4.5.3 is on your machine, but none of these packages is installed, and no agent installs anything on your machine. The Parquet hand-over to R, the real drawing time and the real pictures are therefore reasoned, not measured.

## What exists today

| Thing | State |
|---|---|
| `data_engine`, `plot_engine` | Required at the top of a recipe; one allowed value each (`python-polars`, `python-plotnine`). Decided by you (the engines are part of what a recipe means). |
| `plot_engine` in the code | Really checked: the plot factory refuses an engine it does not have. |
| `data_engine` in the code | Only checked by the recipe checker. Nothing switches on it. |
| An engine key inside a plot or a tier | Refused today as an unknown key. |
| A default that a block overrides | Exists for the theme, the palette and the random seed. |
| The export | Records the plotnine version. It does not record which engine drew a picture. |
| R, ggplot2, dplyr in your decisions | No ledger line. An exploration file (`.claude/design/feature_extension/r_backend.md`) proposes `Rscript` as a separate process with Arrow files, and is marked exploratory. |
| The app's container | Python only, no R. |

## Where could an override sit?

| Place | What it would mean | For | Against | Viewpoints |
|---|---|---|---|---|
| Per plot | One plot is drawn by R, the others by plotnine | The data stays Polars and audited. One-way boundary: a stored table goes in, a picture comes out. It reads like the theme: a default, one plot overrides. It covers the real use cases (trees with ggtree, maps, alluvial plots). | The picture will not look like its neighbours (fonts, sizes, jitter). Six places in the code draw plots and all must go through one dispatcher. R in the container. | All four: yes, this one. |
| Per table or per tier (T1, T2) | A table or a tier is computed by dplyr | dplyr work inside a recipe. The stored tiers are Parquet already, so a hand-over point exists. | The differences listed above apply. The checker cannot know dplyr's rules. The audit writes its steps in Polars ("remove from all tables"), so T3 could never be R. The cache keys would have to be per table. | Scientist, developer, user: not now. Architect: only when a concrete use appears. |
| Per step | One step in dplyr inside a Polars list | Maximum freedom. | A conversion and a silent-change point at every step. The name of the action already says the engine. | Nobody. |

What the user viewpoint proposes a recipe would look like:

```yaml
data_engine: python-polars
plot_engine: python-plotnine        # the default for every plot
...
plots:
  tree_by_source:
    plot_engine: r-ggplot2          # only this plot
    spec: ...                       # ggplot2's own component names
  st_by_source:
    spec: ...                       # plotnine components, as today
```

## ggplot2 as a second plot engine: how it would work

- **One spec is never drawn by two engines.** The scientist and the architect agree: a ggplot2 plot is its own kind of plot with ggplot2's own names (a `ggplot2_` family, parallel to `plotnine_`). No promise that a ggplot2 picture equals the plotnine picture. A translator from the plotnine spec to ggplot2 is what the exploration file itself warns against.
- **The checker refuses a mismatch**: a plot set to R that names a `plotnine_` component, or the reverse.
- **How R is called.** Three ways were compared:

| Way | For | Against |
|---|---|---|
| `Rscript` as a separate process per plot, the table as a Parquet file | Isolated; a crash of R does not take the app down; one fixed script; a timeout is easy | A start of R per plot: 0.26 s measured for bare R, plus the loading of ggplot2 (not measured, estimated 0.5 to 1.5 s) |
| One R process that stays open | Faster per plot | A second service to run and watch; users queue on one R |
| `rpy2` inside the app | Fastest | A crash of R kills the app; not safe with several users; the exploration file already says avoid |

  All viewpoints that judged it: the separate process.

- **The recipe stays data, never code.** The R side would be a list of allowed ggplot2 components with typed parameters, as for plotnine. The recipe gives a component name and values; a fixed script shipped with the app does the drawing. No R text from a recipe is ever run.
- **An "R snippet" in a recipe (write your own ggplot2 code): all four say no.** It would run with the app's rights (files, network), and the checker, Blueprint and the audit could not see into it. It would reverse your rule that no code is executed from recipe text.
- **What the HOME user sees**: a small label on the plot ("drawn by R, ggplot2"); a plain message when R or a package is missing on this deployment, with the remedies; the plot is not drawn, and never replaced by another engine.
- **The export** records, per picture: the engine, the R version, the package versions, the locale and time zone, the seed.
- **Deployment**: R and the packages are installed when the container is built, from pinned versions, never at run time (no network, your existing rule). The image grows by roughly 1 GB (estimated, not measured). At start the app says which engines this deployment has.
- **Effort** (the developer's estimate, a guess): 6 to 10 weeks for ggplot2 as a second plot engine. The largest pieces: today the code that draws a plot gives back a plotnine object, and the export, the gallery and HOME all use that object. An R plot gives back a file. That contract changes for every plot, not only for R plots. Then the list of ggplot2 components.

## dplyr and the tidyverse as a data engine

- The differences in "Read this first" are the core problem. For a result not to depend on the engine, each step would have to state its rule for missing values, for not-a-number, for missing join keys, the sort order and locale, and the rounding rule. A seeded random step can never be the same in two engines.
- The `polars_` actions are each proved equal to the direct Polars call by a test. Nothing like that exists for dplyr; it would have to be built first.
- The audit is Polars only. "Remove this sample from all tables" writes Polars steps.
- The developer: very large cost, small benefit, because Parquet already works as a bridge.
- **The lighter route** all viewpoints point to: prepare the table in your own R script outside the app and give the result to the recipe as a dataset. The honest limit: that step is then outside the recipe, so the audit and the export do not cover it. The recipe description should say so.
- `polars` for R exists as a package; it was not looked at further.

## What to decide now, before the recipe specification is completed

The architect found the point that matters for your planning:

- **As the specification is written today, adding an engine name later (`r-ggplot2`) or a new key (an engine on a plot) is a change of the recipe format.** It would mean format 2 and a mechanical migration of all recipes (50 today). The migration tooling exists, so this is work, not a break.
- **One sentence now avoids that for the engine names**: say in the specification that the engine names are an open list (as the gallery terms already are), so that a new engine value is not a format change.

| Option | What it means | For | Against |
|---|---|---|---|
| 1. Nothing now | The two keys stay as they are | No cost | Later: format 2 and a migration |
| 2. Write the principle now, build nothing | The specification says: the two keys are recipe defaults; engine names are an open list; a plot entry may name its own plot engine in a later version (still refused today, with a plain message); no engine per step; no data engine override for now | About 2 hours of specification text. Your planning is recorded. No break later for a new engine name. | A written plan that is not built. |
| 3. Reserve the key now (accepted by the checker, does nothing) | `plot_engine` allowed on a plot, only with the default value | The key exists already | A key that does nothing is the kind of half step you refuse. |

**Recommendation (the coordinator's, not a decision):** option 2. Then, when you plan the feature: the per-plot engine first, R called as a separate process, ggplot2 with its own names, no snippet, no fall-back. The data engine waits for a concrete need.

**One link to the rename that is about to be built.** The architect asks that the `plotnine_` prefix be built so that the prefix and the engine come from one field of the registry, not from a text written in many places. A `ggplot2_` family can then be added later without touching the plotnine code. This costs nothing extra now and I will put it in the rename brief unless you object.

## What you are asked

1. The recipe format now: option 2 (write the principle, build nothing)?
2. Engine names as an open list, so a new engine is not a format change?
3. For planning: per plot only, and no engine per step: do you agree? And the data side (dplyr): wait for a concrete use, with "prepare outside and give as a dataset" as the route until then?
4. An R snippet in a recipe: confirmed no?
5. The four `plot_defaults` keys that do nothing today: make them work, or refuse them until they do? (Your rule "no silent error" points to one of the two; which one is your choice.)
6. Do you want real numbers (drawing time, the hand-over of each column type, a first ggplot2 picture from a stored table)? Then ggplot2, arrow and svglite have to be installed in R on your machine. You install them, or you say an agent may.

## Not checked

- Anything that needs ggplot2, dplyr or arrow in R: the Parquet hand-over per column type, the drawing time, the pictures, reading ggplot2's parameters automatically.
- The size of a container with R.
- What Galaxy needs for an image with R.
- Every effort figure is an estimate.
- Claims about how ggplot2 changes its defaults between versions are from memory, not checked.
