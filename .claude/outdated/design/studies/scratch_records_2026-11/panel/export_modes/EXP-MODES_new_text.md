# EXP-MODES: proposed new text (a PROPOSAL for Eve, nothing is changed)

Task EXP-MODES-TEXT-1. I changed nothing in the model, nothing in StarUML, no tracked file.
Her statement: ledger `D-0187` to `D-0193` (2026-11-16, her turns #2807, #2825, #2843).
Names used as she uses them: Publication (mode 1), Reproducibility (mode 2), `original_recipe`, `audit_recipe`.

How I read the diagram: with the StarUML bridge. The open project file is `docs/UML/app.mdj` (project info checked). I looked at the picture of `EXP-MODES` (id `AAAAAAGhwIL8VRe2olw=`) and read every element from the file (JSON). Both agree.

## 1. Element by element

"No change" = her words ask for none (`D-0190`: "I think we had described those use case and publication and reproducibility fits well. No need to rephrase so much").

| # | Element (id) | Text today | Text proposed | Why |
|---|---|---|---|---|
| 1 | Terminator `AAAAAAGhwIRbyxiMbI8=` | User clicks Export Bundle | no change | `D-0190`: "No need to rephrase so much" |
| 2 | Decision `AAAAAAGhwIRb5RiUJ0w=` | Mode selected? | no change (but see ADD 1: the first question comes before it, and "one box or three choices" is not decided) | `D-0190` |
| 3 | Process `AAAAAAGhwIRb+Ric0kk=` | Mode 1: Publication / the paper-facing facet | no change | `D-0190`: "publication and reproducibility fits well" |
| 4 | Process `AAAAAAGhwIRcDBikGjA=` | Both (recommended) / one zip - the two facets together | no change | `D-0190` |
| 5 | Process `AAAAAAGhwIRcIhisW8U=` | Mode 2: Reproducibility / the dig-in-and-rerun facet | no change | `D-0190` |
| 6 | Document `AAAAAAGhwIRcPhi0GnI=` | effective_run.yaml / E, D, R (+ file lists), AR, A, Rec, node keys (original and audit), file hashes + git_commit / + per-plot seeds + skipped list / ALWAYS written, identical content either way. Detail: DM-KEYS-EXPORT | no change | Nothing in her words touches it. `D-0187` says the audit case uses the recipe and the data "hashed": the hashes are already in this box |
| 7 | Document `AAAAAAGhwIRceRi8ZH0=` | report.qmd / plots + Methods prose (T3 why) / points to effective_run.yaml | no change now | `D-0193`: "We will need at one point to improve the report - but for now I just want the elemets that are important in place" |
| 8 | Data `AAAAAAGhwIRcoxjEDVA=` | plots/ | no change | Her words do not name plots |
| 9 | Document `AAAAAAGhwIRcwRjMCXA=` | README.txt / points to effective_run.yaml | no change | Her words do not name the README |
| 10 | Document `AAAAAAGhwIRc4xjUxF4=` | data_analysis_recipes_reproducibility/ / frozen recipe, T3 baked in as real steps | `data_analysis_recipes_reproducibility/` / `original_recipe` when the user only explored; `audit_recipe` (the recipe with the audit steps added, each reason as a `#` comment) when the user added audit steps | `D-0188`: "the mode 1 and mode 2 must export the original recipe"; `D-0187`: "use audit recipe and data hashed"; `D-0192`: "add the recipe to the reproducibility mode 2". The `#` reason is `D-0148` (not her words in this turn: it is in the ledger as decided). The word "frozen" and "baked in" can go: `audit_recipe` says it |
| 11 | Data `AAAAAAGhwIRdBRjc8Xs=` | data_reproducibility/ / actual data files, copied | `data_reproducibility/` / the data of the dataset the user worked with, copied | `D-0191`: "it will always be the dataset the user has actually worked with". Whether this means raw files or tables: not decided (open point 1) |
| 12 | Process `AAAAAAGhwIRdJxjkV9c=` | two SEPARATE exports: diff effective_run.yaml field by field (#48 per-leg verify) / recipe/data/T3 match, engine_fingerprint or git_commit differ / = a software change explains the difference, not the analysis | no change | Nothing in her words. (`D-0186`: "changing a recipe is" a failure, changing data not necessarily: this text already follows it) |
| 13 | Process `AAAAAAGhwLg4kRqNiN0=` | Import & Verify (#48) / upload a bundle, checks what it can against this machine | no change | Nothing in her words |
| 14 | Document `AAAAAAGhwLg4qRqV6Bc=` | Writes a NEW recipe + session / never into live app state (ADR-093) / selectable only after reload (F5) | no change | Nothing in her words |
| 15 | Data `AAAAAAGhwLg4txqd7dY=` | legs: engine, data, recipe, audit recipe, steps, record, and each part of every node key \| match / mismatch / not_checked - never blocks. Detail: DM-KEYS-EXPORT | no change | `D-0187` ("audit recipe and data hashed") is already a leg here |
| 16 | The 22 arrows (flows) | see the list in section 1b | change only the arrows named in section 2 | |

### 1b. The arrows today (all, by name)

- User clicks Export Bundle -> Mode selected?
- Mode selected? -> Mode 1 (label "Publication"); -> Mode 2 (label "Reproducibility"); -> Both (label "Both")
- Both -> Mode 1; Both -> Mode 2
- Mode 1 -> effective_run.yaml; Mode 1 -> report.qmd; Mode 1 -> plots/; Mode 1 -> README.txt
- Mode 2 -> effective_run.yaml; Mode 2 -> data_analysis_recipes_reproducibility/; Mode 2 -> data_reproducibility/
- effective_run.yaml -> "two SEPARATE exports" (label "diff field by field")
- data_analysis_recipes_reproducibility/ -> Import & Verify; data_reproducibility/ -> Import & Verify
- Import & Verify -> "Writes a NEW recipe + session"; Import & Verify -> "legs: ..."

## 2. To ADD (proposed; each needs her yes)

| # | New element | Text proposed | Why |
|---|---|---|---|
| ADD 1 | Decision, placed right after "User clicks Export Bundle" | "Did the user add audit steps?" Two arrows: "No: only explored" and "Yes: audit steps added". Both arrows then go on to "Mode selected?" | `D-0187`: "we have 2 cases : user mode exploration only and user with audit"; `D-0190`: "we have to distinguish when the user has worked with audit mode and added steps or if its only exploration" |
| ADD 2 | Document in Publication | "audit points file (short list of the audit steps, one line each with its reason). Only when audit steps were added. Not written when the user only explored." Arrow from Mode 1, labelled "only if steps added" | `D-0192`: "The audit points file that is separate from the recipe can stay in mode 1"; `D-0188`: "that does not make sense to have audit steps file exported" when only explored; `D-0193`: "The audit steps for the user (short and consise)" |
| ADD 3 | Document, optional | "audit history log (optional): the steps added and the steps deleted, for archive. Separate from the audit points file and from the recipe." Arrow labelled "optional". In which mode it goes: not decided (open point 8) | `D-0189`: "could be optional the full log of the audit added deleted ... for archive" |
| ADD 4 | Note on the recipe box (element 10) | "One source: the audit steps. The recipe has them for the computer, the audit points file for the user, the report Methods for the paper (see section 5)." | `D-0193`: "writing them from one source I totally agree - the only thing is that their purpose differ" |

I do NOT propose a box for the data tables in Publication (`D-0188` says both modes export "the data that was used (original tiers)", but what that means is open: point 1).

## 3. To REMOVE (propose only; needs her yes)

The model holds three leftover elements in the package `EXP-MODES`. They are on no diagram (no view).

| Element | Type | id |
|---|---|---|
| TEST A | FCTerminator | `AAAAAAGhwIMJnRhcBqw=` |
| TEST B | FCProcess | `AAAAAAGhwIMbpBhk09s=` |
| TEST C | FCProcess | `AAAAAAGhwIONlhhs3vw=` |

Arrows that must change if she says yes to the ADD points: the arrow "Mode 1 -> effective_run.yaml" stays; the arrow "Mode 2 -> data_analysis_recipes_reproducibility/" stays; nothing is removed from Publication on the picture today (the picture already has no recipe in Publication, which is what `D-0192` asks: "remove the recipe from the mode 1").

## 4. What each zip holds

Cases: E = the user only explored. A = the user added audit steps. P = Publication. R = Reproducibility.
A cell has a ledger number only when her words say it. "not decided (point n)" = see section 5. In the "Both" column a thing is in the zip when it is in P or in R.

| Row | E + P | E + R | A + P | A + R | Both |
|---|---|---|---|---|---|
| plots | not decided (point 7); the diagram has them in P | not decided (point 7); the diagram has none in R | not decided (point 7) | not decided (point 7) | not decided (point 7) |
| report (`report.qmd`) | not decided (point 7); diagram: in P; `D-0193`: improve later | not decided (point 7) | not decided (point 7); `D-0193`: keep only the important elements | not decided (point 7) | not decided (point 7) |
| README | not decided (point 7) | not decided (point 7) | not decided (point 7) | not decided (point 7) | not decided (point 7) |
| `effective_run.yaml` | kept as drawn, always written (`D-0190`) | kept as drawn (`D-0190`) | kept as drawn; names recipe and data by hash (`D-0187`) | kept as drawn; names recipe and data by hash (`D-0187`) | kept as drawn (`D-0190`) |
| the recipe (which one) | none: removed from mode 1 (`D-0192`) | `original_recipe` (`D-0188`, `D-0192`) | none: removed from mode 1 (`D-0192`) | `audit_recipe` (`D-0187`, `D-0192`) | `original_recipe` if E, `audit_recipe` if A, once, from the R side (`D-0192`); whole recipe or the plot's part in a scoped export: not decided (point 2) |
| the data used (copied) | "the data that was used (original tiers)" (`D-0188`); raw files or tables: not decided (point 1) | "the data that was used (original tiers)" (`D-0188`); raw files or tables: not decided (point 1) | "data hashed" (`D-0187`); copied or not in P: not decided (point 1) | "data hashed" (`D-0187`); copied: not decided (point 1, point 5) | not decided (point 1) |
| the audit points file | none (`D-0188`: "does not make sense to have audit steps file exported") | none (`D-0188`) | yes, stays in mode 1 (`D-0192`) | not decided (point 8): `D-0192` says only that it can stay in mode 1 | in the zip, from the P side (`D-0192`) |
| the audit history log | not asked: no steps (`D-0189` speaks of "audit mode") | not asked (`D-0189`) | optional (`D-0189`); in P: not decided (point 8) | optional (`D-0189`); in R: not decided (point 8) | optional (`D-0189`); where: not decided (point 8) |

Which dataset: always the one the user worked with (`D-0191`), in every cell; how the export knows it when one can be chosen: not decided (point 6).

## 5. Not decided, so not drawn

1. Publication and Reproducibility both export "the data that was used (original tiers)" (`D-0188`): it is not said if that means the tables after each tier (T1, T2, T3 of a plot), the raw files, or only their hashes (`D-0187` says "hashed" for the audit case).
2. In an export of one plot or one group, is the recipe in the zip the whole recipe or only the part that feeds that plot.
3. On the screen: one box ("also include ...", as today) or three choices (Publication, Reproducibility, Both, as the diagram).
4. A pinned seed (Reshuffle) counts as an audit step today in the code; it is not said if it puts the user in the audit case.
5. In the audit case, which tables are in the zip: only the audited ones, or the original and the audit tables labelled apart.
6. When one recipe is used with several datasets (`D-0191`), how the export knows which dataset the user chose.
7. Which of plots, report, README, lineage file each zip holds: her words do not list them; the diagram says plots, report and README in Publication.
8. Where the audit history log goes (Publication, Reproducibility, both), and whether the audit points file also goes in Reproducibility.

## 6. One source, three renderings (`D-0193`)

Source: the audit steps (the list of steps with their reasons and dates). Today:

| Rendering | For | What exists today | What would have to read the one source |
|---|---|---|---|
| Audit points file (short) | the user | `t3_steps.yaml`, written at `app/handlers/export_handlers.py:1294-1295` (`safe_dump` of `t3_steps_data`, each step with `reason`, `committed_at`); written when the plot has steps or a pinned seed (`:1263-1266`) | A short one-line-per-step writer. Today it is a dump of the step fields, not a short list. It would read the same steps as the other two |
| `#` reasons in the `audit_recipe` | the computer | Not built. The recipe is written with `yaml.safe_dump` (`export_handlers.py:1318`, which cannot write comments); the steps are put in as a forked join per plot by `translate_plot_steps` (`libs/blueprint_arch/src/blueprint_arch/t3_translator.py:158`; `translate_t3_node` `:91`); the fork comment names the step ids only (`_fork_comment` `:187`); the reasons are not in the recipe | A recipe writer that adds the steps in place and writes the reason as a `#` comment (`D-0148`, `D-0102`). Needs a writer that keeps comments |
| Methods prose of the report | the paper | `_build_methods_section` (`export_handlers.py:380`, "auto-generated Methods section"; the heading is written at `:479`; called at `:1629`) reads `t3_by_plot`. (The name `generate_methods_text` of the contract is not in the code today: I searched; the function is `_build_methods_section`.) | Already reads the same steps. Nothing new now (`D-0193`: improve the report later) |

Also: the audit history log (`D-0189`) has no code today (no event log of added and deleted steps).

## 7. What I could not read

Nothing of the diagram: picture and file both read. The recipe-comment writer and the audit points file's final form are not built, so section 6 describes the code as it is today (read, not run). Line numbers are those of the file today; the comparison file `export_modes_compare.md` quotes a few different numbers (for example `:1280` for the recipe write, now `:1318`).
