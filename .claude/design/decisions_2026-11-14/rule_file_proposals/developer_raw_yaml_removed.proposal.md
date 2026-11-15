# Proposal: the audit step type `developer_raw_yaml` is removed, and `audited_frame` moved (AUDIT-RAWYAML-REMOVE-1, PLOT-TABLE-ORDER-1, 2026-11-15)

Status: PROPOSAL for Eve's double confirmation. No file under `.claude/rules/` was edited. Decided by Eve 2026-11-12 (O3, task AUDIT-RAWYAML-REMOVE-1): the type is removed, nothing creates it. Done in code 2026-11-15: no code path knows the name but the one refusal table (`app/modules/renamed_keys.py`, `REMOVED_AUDIT_STEP_TYPES`, a tombstone that expires with Phase 40); a session file, an imported session zip, the `t3_steps.yaml` of an imported bundle and an audit list that holds one are refused with a message that names the step (never ignored, never applied in one place only). Before: HOME's table, plot and bundle ignored such a step and the exported recipe applied it (42 rows against 22, silently).

Line numbers are those of 2026-11-15 (this branch).

## `.claude/rules/ui_implementation_contract.md`

1. Line 203 (section 7.2 export rule 3), old: `... plus the plot's filter rows and column drops, built by \`export_handlers.audited_frame\`, the same steps and order as the HOME data preview.`
   New: `... plus the plot's audit steps (filters and column drops), built by \`audited_frame\` in \`app/modules/t3_audit_engine.py\`, in the order they were recorded: the same function and the same order as the HOME table and the HOME plot (ADR-105 note of 2026-11-15, S2-1). A step that cannot run is an error that names the plot, the step and the fix; the export checks every plot first and refuses with \`EXPORT_NOT_CREATED.txt\`.` (FACT + the S2-1 decision)
2. Line 204 (rule 4), old: `The pure rule is \`export_handlers.plot_content_rules(audited_rows, audited_drops)\`: exploration is not even an argument.`
   New: `The pure rule is \`audited_frame(lf, nodes, plot_id)\`: it takes the audit steps of the plot only, so exploration is not even an argument.` (FACT: \`plot_content_rules\` is gone.)
3. Line 458 (table of node types), old: `| \`developer_raw_yaml\` | Escape hatch: arbitrary data analysis recipe fragment (>= ... ) | **Mandatory** |`
   New: delete the row. Section 12a opening sentence ("locked to five node types") then reads "four node types".
4. Line 462 (Gatekeeper rule), old: `... \`filter_row\`, \`exclusion_row\`, \`drop_column\`, or \`developer_raw_yaml\` node has an empty \`reason\` field.`
   New: `... \`filter_row\`, \`exclusion_row\` or \`drop_column\` node has an empty \`reason\` field.`
5. Line 473 (12b example comment), old: `# filter_row | exclusion_row | drop_column | aesthetic_override | developer_raw_yaml`
   New: `# filter_row | exclusion_row | drop_column | aesthetic_override`
6. Line 484, old: `... For \`developer_raw_yaml\`, \`params\` carries \`{yaml_fragment: "..."}\`.`
   New: delete the second sentence.
7. Lines 610 and 614 (the REMOVED block of 12e, history of the Gallery clone): keep as history, add after "kept only so a reader ... understands what it meant": `The type \`developer_raw_yaml\` itself was removed on 2026-11-15 (AUDIT-RAWYAML-REMOVE-1).`
8. Line 641 (12f Methods prose), old: `   - \`developer_raw_yaml\`: *"A custom data analysis recipe fragment was applied to [plot_scope]. Reason: [reason]."*`
   New: delete the line.
9. Line 822 (section 13 state comment), old: `# audit steps (wrangling nodes - filter, exclusion, drop_column, developer_raw_yaml)`
   New: `# audit steps (wrangling nodes - filter, exclusion, drop_column)`
10. Section 8 (filter builder), add after the state model: `In My view the filter dialog acts on the table after the plot's audited steps (\`dialog_frame\`): a column that an earlier audit step dropped is not offered (Eve, 2026-11-15, S2-1). Steps still pending are not applied, so a list that cannot run can still be recorded; the table, the plot and the export then show the plain error.` (CHANGES A RULE: decided by Eve 2026-11-15)

## `.claude/rules/rules_ui_dashboard.md`

11. Line 13 (section 1, T3 scope), old: `... aesthetic overrides, and BLUEPRINT's own YAML escape hatch (\`developer_raw_yaml\`, written only via \`data_analysis_recipe_edit_enabled\` - never from any other source, see ADR-093).`
    New: `... and aesthetic overrides.` (the escape hatch no longer writes a T3 step; ADR-093 stays for the Gallery rule)
12. Line 203 (section 7, YAML escape hatch), old: `An editable escape hatch emits a \`developer_raw_yaml\` T3 node on save.`
    New: delete the sentence. (OPEN for Eve: what the editable escape hatch does on save, if anything; no code emits a step today.)

## `.claude/rules/rules_app_features_flags.md`

13. Line 111 (Group D, `data_analysis_recipe_edit_enabled`), old: `When \`true\`, the YAML panel becomes an editable textarea that emits a \`developer_raw_yaml\` T3 node on save.`
    New: `When \`true\`, the YAML panel becomes an editable textarea.` (same OPEN point as 12)

## Not settled

- Points 12 and 13: no code creates the step today (checked: grep over `app/` and `libs/`), so the rule text described a feature that does not exist. Eve decides what the editable escape hatch should do, if anything.
- `.claude/knowledge/architecture_decisions.md` (ADR-093 history and ADR-099 point 16 mention the name): left as history, they are dated records.
