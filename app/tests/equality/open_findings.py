"""The comparisons that differ today (see FINDINGS.md). A case listed here runs in `test_findings_open.py`, not in
`test_recipe_equals_hand_written.py`. Remove a case from this set the day the difference is resolved.

F1: a missing phenotype is counted as a resistance class (`Multiresistant`); the four AMR plot cases follow from it.
F2: `null_values: []` does not make an empty cell a text: the engine reads it as missing.
"""
OPEN_FINDINGS: set[str] = {
    # F1
    "dirty-t1-AMR_Profile_Joint",
    "dirty-t2-AMR_Profile_Joint",
    "dirty-plot_data-multi_resistance_by_country",
    "dirty-plot_built-multi_resistance_by_country",
    "dirty-plot_data-multi_resistance_by_source",
    "dirty-plot_built-multi_resistance_by_source",
    # F2
    "dirty_no_null_text-refused-metadata_schema",
    "dirty_no_null_text-refused-amr_data",
    "dirty_no_null_text-refused-plasmid_data",
    "dirty_no_null_text-refused-AMR_Profile_Joint",
    "dirty_no_null_text-refused-Plasmid_Profile_Joint",
}
