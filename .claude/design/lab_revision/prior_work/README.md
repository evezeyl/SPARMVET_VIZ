# Prior work on the Test Lab (copied from tmpAI/, unchanged except for one header line)

These files are sources, not decisions. They were in git-ignored scratch folders (`tmpAI/`); they are kept here so that a cleaning of `tmpAI/` loses nothing the guide cites. Each file's first line says where it was copied from and its date. Copied on 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396).

| File | Source | Date | What it is |
|---|---|---|---|
| `step4c_report.md` | main tree `tmpAI/engine_keys/step4c_report.md` | 2026-11-18 | The (partial) report of step 4c of the big recipe change, which rewrote the Test Lab writers (bootstrapper, scaffolder) for recipe format 1; lists its provisional choices (choice 7 keeps an absolute data path that the checker refuses) and what it did not fix (`anonymiser.build_deanon_steps` still writes the old action name `join`) |
| `test_lab_review_2026-11-18/run1.py` | main tree `tmpAI/panel/test_lab_review/run1.py` | 2026-11-18 | The scaffold run of the earlier review (`../../exploration/2026-11-18_test_lab_review.md`): two uploads named as Shiny names them, ids `007...`, join key `sample_id` and `Sample ID`. It writes its own input files |
| `test_lab_review_2026-11-18/run2.py` | main tree `tmpAI/panel/test_lab_review/run2.py` | 2026-11-18 | The checker run on the two scaffolds of `run1.py` (profile `run`) |
| `probes_2026-11-21/probe.py` | worktree `.claude/worktrees/lab-review/tmpAI/run/probe.py` | 2026-11-21 | Step 1 probe of this review, cases A to F (`../02_planned_vs_existing.md`, "The runs") |
| `probes_2026-11-21/probe2.py` | worktree `.claude/worktrees/lab-review/tmpAI/run/probe2.py` | 2026-11-21 | Step 1 probe, case G (text ids, then the checker and the engine's own load) |

**Not copied, and why.**
- The main tree folder `tmpAI/panel/test_lab_review/` holds no `.md` file. Its input files (`up/*.tsv`, `up/real.csv`, `ref/t.tsv`) and its outputs (`out_sample_id/`, `out_Sample_ID/`) were left out: `run1.py` writes its own inputs again; the other inputs are small invented tables used by runs that were not saved as scripts; the outputs are scaffolds of the shape before step 4c (out of date, see `../02_planned_vs_existing.md` section L).
- The probes' outputs (`tmpAI/run/out_A`, `out_B`, `out_G`, `uploads/` of the worktree): written again by the probes.

**Personal data check (2026-11-21).** No file holds an e-mail address, a token or a recipe's contact field (grep). `step4c_report.md` names the owner twice by her first name ("for Eve", "pending Eve"), as the tracked records do (`tasks.md`, the ledger) and as the files of `../../blueprint_revision/prior_work/` do; it was copied unchanged.

Where these files differ from `../02_planned_vs_existing.md`, that file is the newer reading.
