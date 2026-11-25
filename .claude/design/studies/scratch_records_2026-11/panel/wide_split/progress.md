# Progress: step_split_wide design note (builder-opus, 2026-11-18)

Done: read the decisions and sources; ran 8 prototype scripts (01 to 08, outputs *.out next to them; proto_step.py is the
scratch prototype). Writing `.claude/design/exploration/2026-11-18_step_split_wide_design.md`.
Done: the design note is written (not committed). Next: none (report sent).
Findings: no polars_list_to_struct and the formula check refuses list.to_struct; too_few error stops the demo genotype
(33 of 42 cells); no carrier for a step note; fill_null(0) on text gives "0"; strategy forward copies the row above;
width from data is not lazy; step_top_n_other equals a chain of 4 with_columns + drop (200/200).
