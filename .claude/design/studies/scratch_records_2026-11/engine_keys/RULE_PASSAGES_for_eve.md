# Four rule passages that wait for Eve (written 2026-11-18, before the worker put them back)

Commit `724c83ce` (branch `task/engine-keys`) changed these passages. D-0249 allows only: the cache-key rule with the engine argument, the removal of the four dead keys, the open engine names, the `spec:` change and the tier mapping, the theme rule. The review (point 6) judged the four items below to be outside that list. On the branch they are put back to the wording of `dev`, except for the parts D-0249 does allow in the same sentence (named per item). If you say yes to an item, the "proposed" text can be applied as it stands.

## Item 1. Visible labels (`.claude/rules/rules_data_analysis_recipe_structure.md`, section "Visible labels"), and the "no `title:` key" comments

Rests on D-0253 (the key `ui_label`, `ui_title`), a decision that does not name this rule file.

Text on `dev`:
- chain: "1. `label:` field if set (recommended — explicit and concise)"
- "All three preserve any unicode, including emoji and CJK. Data Analysis Recipe authors can use any icons in `label:` to make the UI friendly."
- "Reserve `description:` for longer prose; use `label:` for short emoji-rich tab text."
- no comment on the `labs` layer in the plot examples.

Text the builder proposed:
- chain: "1. `ui_label:` field if set (recommended — explicit and concise)"; "... any icons in `ui_label:` ..."
- "Reserve `description:` for longer prose; use `ui_label:` for short emoji-rich tab text; `ui_title:` (optional) is a longer name that the report uses."
- comment on the `labs` layer: "(there is no `title:` key)" in the plot example of that file and of `rules_agent_role_bioscientist.md`.

Why it is true today: the checker reads `ui_label` / `ui_title` and refuses `label:` and a plot `title:` (`libs/utils/src/utils/recipe_check.py`; `libs/viz_factory/src/viz_factory/viz_factory.py:219-230` refuses an unknown plot key, `title` named).

Put back on the branch: the chain, the "All three" sentence, the "Reserve" sentence (to `label:`, no `ui_title` sentence), and both "(there is no `title:` key)" comments are removed. Kept (allowed, the `spec:` change): the example in that section without `spec:`.
Consequence you should know: the rule text now says `label:` while the examples in the same file (and the checker) use `ui_label:`. The `ui_title:` line in the plot example of the same file ("Optional — the longer name the report uses") was not in the list and was left as built; it is a fifth passage of the same kind (D-0253).

## Item 2. Section 10 of the same file: who may override

Text on `dev`: "Individual plot specs may override any key."
Text proposed: "Individual plot entries may override `palette` and `theme`."
Why true today: the plot entry takes `palette`, `theme` and `layers` (the entry also adds `layers`, so the proposed sentence is itself incomplete); the cascade is in `libs/viz_factory/src/viz_factory/plot_config_resolver.py` (`resolve_plot_config`). Decision: none named.
Put back on the branch: the `dev` sentence. Kept (allowed, the `spec:` change): "L4 plot entry" in the next sentence of the cascade.

## Item 3. Unknown key in `plot_defaults`: warning or refusal (`rules_data_analysis_recipe_structure.md` 10a; `rules_viz_factory.md` 6b and 7)

Text on `dev`: "Unknown key warning: keys not in the list above emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)`. Non-fatal — experimental keys are allowed — but the warning prevents silent typos." (6b and 7 carry the same sentence, 7 "per ADR-079. Non-fatal.")
Text proposed: "A key not in the list is refused by the data analysis recipe checker (PD01); each of the four removed keys is refused with a tombstone text (PD02)."
Why true today: the checker refuses it (`recipe_check.py:1104`, PD01; PD02 for the four keys). The plot library still only warns at run time (`viz_factory.py:277-291`). So both sentences are true, of two different places. Decision: none named (it is a behaviour rule: warning became refusal).
Put back on the branch: the `dev` warning sentence, then one added sentence that D-0249 allows: the four removed keys are refused with a tombstone text (PD02).

## Item 4. L3, what the optimisation may do (`rules_viz_factory.md` section 7)

Text on `dev`: "Allowed: axis text rotation/size, panel spacing, density-aware positions."
Text proposed: "Allowed: axis text rotation/size (built). Panel spacing and density-aware positions are designed, not built, and have no switch (the `optimisation` key was removed)."
Why true today: only the axis-text adjustment is built (`libs/viz_factory/src/viz_factory/plot_config_resolver.py:482-484`); the `optimisation` key is removed (D-0242, allowed). Decision: none for the status claim.
Put back on the branch: the `dev` sentence; the fact that the `optimisation` key was removed stays in section 10a (allowed).
