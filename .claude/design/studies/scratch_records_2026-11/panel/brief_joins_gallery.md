# Panel brief: joins and gallery (2026-11-14)

You recommend; Eve decides. Principles: `.claude/workflows/agent_principles.md`. Scratch checks only under `tmpAI/panel/`.
Tags: DECIDED (a dated decision, an ADR, a DEC row) / CONFIRM (written, awaiting Eve) / OPEN.

## Theme 1: joins
DECIDED (tasks.md:181, Eve 2026-11-14): a join keeps the declared key types; the hidden cast to String is removed; the build fails on differing types.
- J-a (N1, CONFIRM): the join key rule lives in three places: the build `data_assembler.py:52` (`_check_join_key_types`), the Blueprint preview `join_designer.py:29` (`check_join_keys`), the recipe checker `recipe_check.py:539` (`join_key_problems`). Kept equal by parity tests only. Options: A keep three copies with the parity tests; B one pure rule in `libs/utils`, called by all three (`transformer` and `blueprint_arch` may import `utils`; they may not import each other).
- J-b (N5, CONFIRM): the checker refuses at load a join key that is not declared in `input_fields` (J10, `recipe_check.py:581`). Options: A confirm; B make it advice, not a refusal; C remove.
- J-c (older point 3, CONFIRM): a first assembly step that joins the base table with itself is skipped silently (`data_assembler.py:221-223`). Options: A keep the silent skip; B fail with a plain message (recorded recommendation); C skip with a visible warning.
- J-d (TEMPLATE-KEY-TYPE-1, OPEN): the shipped template declares `sample_id` as Float64 on both sides (`config/data_analysis_recipes/templates/complex_template/metadata_input.yaml:1-3`, `genomics_input.yaml:1-3`). The join runs (same type on both sides). Options: A leave; B change the template to a text type (the rule files say a primary key is categorical); C also make the checker advise against a float join key.

## Theme 2: gallery
DECIDED: DEC48 (the gallery check runs at rebuild, at app start, in tests). `recipe_format_spec.md:515` (D4, "DECIDED as recommended", no date): an example that fails is left out "with the reason shown". `rules_gallery_standards.md:91-94`: the index is the only source of the UI; failing bundles are excluded from it.
- G-a (N3, CONFIRM): when the gallery folder is read-only, the start check cannot rewrite the index (status `not_writable`, `gallery_manager.py:141-161`), so a failing example listed in the old index is still shown; only a console line says so. Options: A keep; B leave failing examples out in memory at start (`bootloader.rejected_gallery_examples` exists, `bootloader.py:201-208`); C stop the gallery with a message.
- G-b (N4): "with the reason shown" is decided but not built: nothing in `app/` reads `rejected_gallery_examples`. Options for WHERE the user reads it: A a short list under the gallery filters ("N examples are not shown", each with its reason), as HOME does for rejected recipes (ADR-094); B only the alert log; C the console only (today).
- G-c (N15, OPEN): `GalleryManager.submit_example` (`gallery_manager.py:163-203`) has no caller outside its tests; ADR-093 made the gallery a static browser; `recipe_format_spec.md:190` (Q3) says "Eve's call"; `recipe_format_spec.md:831` names it as a test target. Options: A keep as a library function (documented as not used by the app); B delete it and its tests; C wire it to a command-line script for maintainers.

## Your answer
At most 100 words per point (7 points). For each: the option you recommend, its main pro and con, evidence class (RUN / READ / INFERRED). Flag first anything that changes a result silently, hides something from the user, or reconsiders a decision already taken.
