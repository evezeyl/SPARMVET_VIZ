# stat_function text block: builder report

Commit 0dc2e361 on task/function-text-block (from dev 32e09107). Not pushed, not merged.

Message (PROVISIONAL, one source: STAT_FUNCTION_TEXT_BLOCKED and STAT_FUNCTION_TEXT_SUGGESTION in libs/utils/src/utils/plot_text_check.py):
"A function curve written as text is blocked for now, because it would run text from the recipe as code. Suggestion: compute the values in a step of the recipe and draw them with a line layer."

What users see
- Recipe author at check: PS06 on layers[n].params.fun with that text. At draw: "Plot 'p', layer 2 (stat_function): <message>" (same sentence).
- Blueprint user: the picker still lists stat_function; its description says "BLOCKED FOR NOW in recipes ..." and the yaml_example is a comment saying blocked, then a geom_line layer. Blueprint code untouched. I did not run Blueprint; the picker reads the ui_schema description/yaml_example.
- stat_function with no `fun`: not blocked by us; plotnine itself refuses ("requires parameter 'fun' to be a function or any other callable") and the factory wraps it in the one error form. A real Python callable still draws (not a recipe value).

Removed: _function_from_string, function_string_namespace and the eval in geoms/core.py. No other user (grep). Left: formula_check.function_string_problems and its tables/tests (a checker, no evaluation; kept for the reopening, D-0275). Candidate for removal later: not used by the plot check any more. test_stat_function_names_drawn.py deleted (its purpose, check and drawing agree, no longer exists); replaced by the pins in test_stat_function_formula.py.

Tests: new/changed pins in libs/viz_factory/tests/test_stat_function_formula.py (message, plot and layer named, found by name, eval never called, helpers gone, help text), libs/utils/tests/test_plot_text_check.py, test_recipe_check.py (PS06 with message), test_stat_function_names.py, test_registry_audit_vs_plotnine.py (stat_function moved to a BLOCKED_TEXT group with its own test), test_formula_element_field.py (dead import removed). Full run of libs/viz_factory + libs/utils + app/tests/test_plot_text_gate.py before the last two fixes: 4125 passed, 2 failed (both fixed and rerun: 890 passed, 8 xfailed in the touched files). app import: OK.
Break once: disabled the stat_function branch in layer_text_problems: 7 tests failed; restored.

Suggestion trial: a computed column drawn with geom_line (mapping y to the computed column) draws. Limit: only at the data's own x values, not a smooth curve between them. Not put in the message.

No shipped recipe, gallery bundle or equality recipe uses a function text (grep config assets docs libs). Only docs/workflows/visualisation_factory.qmd (changed to say blocked) and the test recipe stat_function_test.yaml (description changed; its layer is still the refused one, pinned by tests, not used as a drawing test).
Listed, NOT changed: assets/scripts/debug_bootstrap_viz_yamls.py:123 writes geom_line with stat: stat_function and fun text; it is not the stat_function component, so no check refuses it, plotnine would fail on a text fun at draw. Eve/coordinator to decide.
PROVISIONAL: wording of the message; yaml_example form; keeping formula_check tables; dependency_index.md not regenerated (auto-generated).
