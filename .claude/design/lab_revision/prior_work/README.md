# Prior work on the Test Lab (copied from tmpAI/, unchanged except for one header line)

These files are sources, not decisions. They were in git-ignored scratch folders (`tmpAI/`); they are kept here so that a cleaning of `tmpAI/` loses nothing the guide cites. Each file's first line says where it was copied from and its date. Copied on 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396).

| File | Source | Date | What it is |
|---|---|---|---|
| `step4c_report.md` | main tree `.claude/design/studies/scratch_records_2026-11/engine_keys/step4c_report.md` | 2026-11-18 | The (partial) report of step 4c of the big recipe change, which rewrote the Test Lab writers (bootstrapper, scaffolder) for recipe format 1; lists its provisional choices (choice 7 keeps an absolute data path that the checker refuses) and what it did not fix (`anonymiser.build_deanon_steps` still writes the old action name `join`) |
| `test_lab_review_2026-11-18/run1.py` | main tree `tmpAI/panel/test_lab_review/run1.py` | 2026-11-18 | The scaffold run of the earlier review (`../../exploration/2026-11-18_test_lab_review.md`): two uploads named as Shiny names them, ids `007...`, join key `sample_id` and `Sample ID`. It writes its own input files |
| `test_lab_review_2026-11-18/run2.py` | main tree `tmpAI/panel/test_lab_review/run2.py` | 2026-11-18 | The checker run on the two scaffolds of `run1.py` (profile `run`) |
| `probes_2026-11-21/probe.py` | worktree `.claude/worktrees/lab-review/tmpAI/run/probe.py` | 2026-11-21 | Step 1 probe of this review, cases A to F (`../02_planned_vs_existing.md`, "The runs") |
| `probes_2026-11-21/probe2.py` | worktree `.claude/worktrees/lab-review/tmpAI/run/probe2.py` | 2026-11-21 | Step 1 probe, case G (text ids, then the checker and the engine's own load) |
| `probes_step4_2026-11-21/sci_probe.py` | main tree `tmpAI/panel/lab_step4/sci_probe.py` | 2026-11-21 night | Scientist viewpoint of step 4: anonymiser hash collisions in 200,000 ids, reversal of a hashed id by guessing, sequential ids depending on row order, case and space variants (`../06_proposal_scientist.md` R1 to R4) |
| `probes_step4_2026-11-21/sci_probe2.py` | main tree `tmpAI/panel/lab_step4/sci_probe2.py` | 2026-11-21 night | Scientist: one colliding pair through `Anonymiser.anonymise`; the synthetic generator's seed and the process-wide random state (R1, R7) |
| `probes_step4_2026-11-21/sci_probe3.py` | main tree `tmpAI/panel/lab_step4/sci_probe3.py` | 2026-11-21 night | Scientist: id reconciliation on messy ids (`ISO-1` to `ISO-10` and others), zero rows, a missing id (R5, R6) |
| `probes_step4_2026-11-21/arch_check1.py` | main tree `tmpAI/panel/lab_step4/arch_check1.py` | 2026-11-21 night | Architect: synthetic generator with and without a seed, the global random state, a planted wrong type refused at ingestion (`../06_proposal_architect.md` 1.2) |
| `probes_step4_2026-11-21/arch_check2.py` | main tree `tmpAI/panel/lab_step4/arch_check2.py` | 2026-11-21 night | Architect: hash of the TSV bytes of a seeded synthetic table (run twice, in two processes) |
| `probes_step4_2026-11-21/arch_check3.py` | main tree `tmpAI/panel/lab_step4/arch_check3.py` | 2026-11-21 night | Architect: headless reading of a recipe with `utils.recipe_loader.load_recipe` (1.4) |
| `probes_step4_2026-11-21/arch_check4.py` | main tree `tmpAI/panel/lab_step4/arch_check4.py` | 2026-11-21 night | Architect: HOME's Data Import check on the file the recipe itself reads (first form of 1.1) |
| `probes_step4_2026-11-21/arch_check5.py` | main tree `tmpAI/panel/lab_step4/arch_check5.py` | 2026-11-21 night | Architect: HOME's Data Import check against the engine's strict import, two header spellings, recipe `simple_template.yaml` (1.1) |
| `probes_step4_2026-11-21/simple_data.tsv` | main tree `tmpAI/panel/lab_step4/simple_data.tsv` | 2026-11-21 night | The two-row input of `arch_check4.py` (headers `ID`, `Measurement`, `Group`). Copied with NO header line: a line added on top would change the data the script reads |

The `.py` probes of step 4 read paths relative to the main tree root (`config/...`, `tmpAI/panel/lab_step4/simple_data.tsv`); run from here they need that path changed. The four viewpoints' texts are in `../06_proposal_*.md` and their brief in `../06_panel_brief.md`.

**Not copied, and why.**
- The main tree folder `tmpAI/panel/test_lab_review/` holds no `.md` file. Its input files (`up/*.tsv`, `up/real.csv`, `ref/t.tsv`) and its outputs (`out_sample_id/`, `out_Sample_ID/`) were left out: `run1.py` writes its own inputs again; the other inputs are small invented tables used by runs that were not saved as scripts; the outputs are scaffolds of the shape before step 4c (out of date, see `../02_planned_vs_existing.md` section L).
- The probes' outputs (`tmpAI/run/out_A`, `out_B`, `out_G`, `uploads/` of the worktree): written again by the probes.

**Personal data check (2026-11-21).** No file holds an e-mail address, a token or a recipe's contact field (grep). `step4c_report.md` names the owner twice by her first name ("for Eve", "pending Eve"), as the tracked records do (`tasks.md`, the ledger) and as the files of `../../blueprint_revision/prior_work/` do; it was copied unchanged.

Where these files differ from `../02_planned_vs_existing.md`, that file is the newer reading.
