# NA rule (#63): gap between Eve's decision (M65, 2026-11-14) and the code. Checked 2026-11-14, Polars 1.40.1.
Probe: `tmpAI/panel/na_rule/probe.py`, `probe2.py` (RUN). Frame x=[1,2,3,null,NaN,2], s=["a","b","c",null,"NA","b"], threshold 2 / "b".
Read: M65 (agent_channel.md:70), tasks.md:38 (already rewritten), home_audit_steps.md:587-591 (already rewritten, "SUPERSEDED in part").

## (a) Behaviour today (RUN). Decision: every comparison removes null; NaN is a number above all; na keep adds `| is_null()`
| op | modif_filter na=remove | modif_filter na=keep | HOME table `_apply_filter_rows` | plot loop `VizFactory.render` | translator writes | = decision? |
|---|---|---|---|---|---|---|
| eq, in, gt, ge, lt, le, between | null out; NaN: only gt/ge keep it | null in | null out, same rows as engine | null out, same | `na: remove` | yes (all three) |
| ne, not_in | null out; NaN kept | null in | null out; NaN kept | null out; NaN kept | `na: remove` | yes |
| user wants "keep" | possible | | NOT possible (no `na` read) | NOT possible | cannot write keep | no: only gap |
Null and NaN are identical across the three places on both columns (float, text) for scalar ops: the engine already follows the decision.
Not NA but found (RUN, probe2): plot `in/not_in` casts to text: `in [2]` on Float64 gives [] in the plot, [1,5] in HOME; `not_in [NaN]` keeps the NaN row (text "nan"/"NaN" differs). Same cause as FILTER-DTYPES-1 / xfails below.

## Dialog, step, session, checker (READ unless marked)
- Filter row built at `filter_and_audit_handlers.py:418` = {column, op, value, dtype}(+closed): no `na`, no count, no "no value in" text anywhere (grep, RUN: zero hits in app/libs).
- Audit step: params copied at `:481-483` (column, op, value, dtype); `make_audit_step` stores `params` as is (`session_manager.py:81-90`): an extra `na` key would be stored and saved in the ghost, nothing else needed. Propagation copies `dict(params)` (`:830`).
- Display/report: `describe_filter` (`t3_audit_engine.py:53`) and report prose (`export_handlers.py:373-380`) say nothing about missing values.
- Checker (RUN `step_problems`): `na` missing -> "na is required by modif_filter"; `maybe` -> refused; keep/remove accepted. No count, no warning for ne/not_in on a column with nulls (no data access there).
- Translator `t3_translator.py:127`: always writes `na: remove`, so a "keep" tick could not be exported. FROZEN.
- Plot path: `home_theater.py:482-490` copies every row key except `dtype`, so an `na` field would reach VizFactory (ignored there today).

## Tests that pin today (RUN: 230 passed, 19 xfailed in those 6 files)
- `app/tests/test_filter_defects.py:107,112,123`: three strict xfails that name #63 and encode the WITHDRAWN rule (`!=`/not_in keep null; NaN as null). With the decision they are wrong and must be deleted/rewritten (the engine already does what the decision says). Docstring lines 12-14 also wrong. `:137` pins "no count": to be replaced.
- `test_modif_filter_vs_home_filter.py:73` pins "HOME has no way to keep the missing rows"; `:44-54` pins HOME = modif(remove).
- `test_modif_filter_verify.py` and `libs/transformer/tests/test_modif_filter.py` already pin na keep/remove and NaN untouched (the decision's engine part, built).
- `libs/blueprint_arch/tests/test_t3_translator.py:53-104` pin `na: remove` (frozen file).
- `test_filter_int_equivalence.py`: 4 plot in/not_in xfails ("91.0 is not 91") and 12 translator-text xfails (EXPORT-FILTER-VALUE-1, frozen); none names #63.

## (b) Changes, grouped (G1..G6 independent unless noted)
G1 ENGINE `modified.py`: none for the rule (done). Only: description (`:45-47`) to add "keep adds rows Polars would drop" and the Polars equivalents (`ne_missing`, `is_in(nulls_equal=True)`). Not frozen. Needs no undecided point. [sonnet/low]
G2 HOME table + plot: read `na` from the row (`t3_audit_engine.py:104-170`, `viz_factory.py:166-218`, plus `home_theater.py:482-490,1346` plumbing): add `| is_null()` when keep; default when `na` absent = remove (today) or required? VizFactory in libs/viz_factory is not on the frozen list. Not frozen; depends on FILTER-UNIFY-1 (one implementation vs two copies): doing it twice is the cost if unify comes later.
G3 DIALOG + messages `filter_and_audit_handlers.py:150-290` (form), `:418` (row), `:481` (params), `:125-135` (list text): add tick preselected by operator (ne/not_in keep, others remove), count "N rows have no value in <column>: they are kept / removed" and separate "N rows have a failed calculation" (NaN) using the active frame; write `na` into the audit params. Not frozen (`audit_stack.py` display of `na` in the audit card is frozen: only if the card must show it). Depends on G2 for the effect, on the stage-2 spec only for the audit_counts/`audit_counts.py` (not built).
G4 EXPORT TRANSLATOR `t3_translator.py:127` + `test_t3_translator.py`: write the step's `na` instead of the constant. FROZEN (needs Eve's yes); also `export_handlers.py:373-380` report sentence and `audited_frame:220` (frozen). Depends on G3 (the field exists) and on FILTER-UNIFY-1 not at all. Until done a "keep" exported as "remove": a result that changes silently, so G3 must not ship a keep tick before G4.
G5 CHECKER + BLUEPRINT: counts and the warning for ne/not_in need data: the checker (`libs/utils/src/utils/recipe_check.py`, `ui_schema.step_problems`) is static, no frames. A data-aware function (pure, in libs/utils or app/modules, e.g. count_missing_nan(lf, column)) shared with G3, then shown in the Blueprint form of `modif_filter` (generated from ui_schema, `wrangle_studio.py`/`blueprint_handlers.py`) and in the data check (`data_analysis_recipe_validator.py`, validate_..._data). Not frozen. Depends on: where Blueprint shows a step with data (stage-2 spec `audit_counts.py` is not built).
G6 DOCS + tests: help text/user doc (`docs/appendix/transformer_actions.qmd:198`, `wrangling.qmd:172`, `Standards_yaml.qmd:126`, `blueprint_data_analysis_recipe_authoring.qmd:101-104` already explain null/NaN/no `NA`; add text "NA", equivalents, keep-adds-rows); fix `home_audit_steps.md:523` (old "kept by !=" wording in flaw 2, check), `home_preview_filters.md:72` (old "NA (missing)" value); rewrite the 3 xfails of G-tests above; add edge cases (all-null column, NaN-only, empty list, keep + not_in). Not frozen.

## (c) Not covered by the decision (questions)
1. `home_preview_filters.md:72` (decided 2026-11-12): "NA (missing)" as a selectable value in every value list. Kept, or replaced by the `na` tick? They overlap.
2. HOME rows with no `na` (old sessions, old ghosts, T1/T2 exploration filters): default remove (today's behaviour), or refuse? Same for an old audit step re-run.
3. Does the tick apply to exploration filters (applied_filters) too, or only to audit steps? (exploration never exported.)
4. `na: keep` with `in`/`eq` on a text value list: is "keep" also offered for `>`/`<`/between (Polars has no switch, we add `|is_null`)? M65 says "all options offered": confirm for comparisons.
5. Text "NA": is turned to null at ingestion by recipe `null_values` (spec 7.3); a column read with "NA" as text is not missing. The count must say which; no decision on a warning when the text "NA" or "" remains in a text column.
6. NaN in the plot path/`in` lists: decision silent; the text-cast of plot in/not_in (FILTER-DTYPES-1) decides it.
7. Per-plot reach: the count shown for the filter is on which frame (T2 of that plot, the whole join)? Needed for the sentence.
8. Frozen files: translator + report + audit card need Eve's yes before keep can be exported.
