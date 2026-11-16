"""The comparisons that differ today (see FINDINGS.md). A case listed here runs in `test_findings_open.py`, not in
`test_recipe_equals_hand_written.py`. Remove a case from this set the day the difference is resolved.

F1 (a missing phenotype was counted as a resistance class) was corrected in the shipped recipe on 2026-11-16 and left this list.
F2: `null_values: []` does not make an empty cell a text: the engine reads it as missing.
"""
OPEN_FINDINGS: set[str] = {
    # F2
    "dirty_no_null_text-refused-metadata_schema",
    "dirty_no_null_text-refused-amr_data",
    "dirty_no_null_text-refused-plasmid_data",
    "dirty_no_null_text-refused-AMR_Profile_Joint",
    "dirty_no_null_text-refused-Plasmid_Profile_Joint",
}
