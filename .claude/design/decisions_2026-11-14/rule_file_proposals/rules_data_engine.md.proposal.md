# Proposal: `.claude/rules/rules_data_engine.md`

Status: PROPOSAL for Eve's double confirmation. No rule file was edited.
Checked against: ADR-100 (points 4 to 7), ADR-101, ADR-090 (and its proposed new wording in `.claude/design/adr_100_recipe_format_1_draft.md:145-159`), ADR-106 last line,
`recipe_format_spec.md` DEC23, DEC24, DEC31 to DEC36, DEC41; the registry (68 actions); `libs/transformer/tests/test_action_recipe_pairs.py` (the 1:1:1 law enforced);
`libs/transformer/tests/debug_wrangler.py` and `debug_assembler.py` (both RUN or `--help` run on 2026-11-15: they work on format 1).
Each change: FACT or CHANGES A RULE.

---

## 1. Front matter, line 4 (FACT)

Today: `  provides: [rule:3tier_lifecycle, rule:wrangling_block_structure, rule:decorator_standards, rule:polars_parity]`
Proposed: `  provides: [rule:3tier_lifecycle, rule:wrangling_block_structure, rule:decorator_standards, rule:polars_actions]`
Why: follows change 8 (the parity mandate is replaced). Run `build_dep_graph.py` after the edit: `rules_agent_role_bioscientist.md` and the dependency index list `rule:polars_parity`.

## 2. Lines 21 and 27, cache keys (FACT, pending a build)

Today (line 21): `- **Cache key:** the Tier 1 parquet is valid only while its \`tier1_key\` matches (resolved data analysis recipe minus downstream-only parts, plus data hash and engine version; ADR-089). Never reuse an anchor by file name alone.`
Proposed: keep the text and add at its end: ` **[Decided 2026-11-12, NOT BUILT: ADR-101 replaces the key formula of ADR-089 by a series of labelled parts per node (task KEYS-NODE-1). Until it is built, this paragraph describes the code.]**`
Today (line 27): the same reference `(ADR-089)` in the Tier 2 bullet.
Proposed: the same marker added at the end of the sentence `keyed by the chained \`tier2_key\` (ADR-089)`.
Why: ADR-101 header ("Supersedes: ADR-089 decision points 1 and 2 ...", "NOT BUILT (task KEYS-NODE-1)"). The rule says "Never reuse an anchor by file name alone" stays true under ADR-101 (point 2: the key is stored and compared on read).

## 3. Lines 38-40, decorator standards: add naming and prefixes (CHANGES A RULE)

Today (lines 38-40): "Homogeneity", "Signature", "Atomicity".
Proposed: keep the three bullets and add after line 40:
```
- **Names (ADR-100 point 6, DEC31, DEC35):** an action name has a prefix: `polars_<name>` (a Polars call), `modif_<name>` (a Polars idea with a documented change) or `step_<name>` (several Polars calls in one step). No unprefixed name and no alias remains; there is one action for one Polars method.
- **A `polars_` action is exactly Polars (DEC32):** the Polars name, all Polars parameters with the Polars names and defaults. A test compares it with the direct Polars call (`libs/transformer/tests/test_polars_actions_equal_polars.py`). A special need is a separate `modif_` action, or is written in the recipe.
- **No hidden choice (DEC33):** a parameter that changes the result is required, or its default is the Polars default. For `modif_` and `step_` actions a default is allowed only when the parameter is "off when absent".
- **No silent no-op (DEC36):** an action that gets a missing parameter, a missing column or an empty list or mapping that would do nothing fails and names the step (`libs/transformer/tests/test_actions_must_act.py`). 40 of the 68 actions refuse an empty list or mapping (`min_items.py`, merged `b91a9fd5`).
```
CHANGES A RULE (new rules; they are decided in ADR-100 and already enforced by the tests named).
Why: ADR-100 point 6; DEC31 to DEC36 (`recipe_format_spec.md:133-138`). Commits `d0108338`, `4659a4bc` (empty list refused).

## 4. Line 41, Determinism (CHANGES A RULE)

Today (line 41): `- **Determinism (ADR-090):** the same input gives the same rows in the same order. An action that can reorder rows (grouping, deduplication, joins, sorting, sampling) states its order rule in its description and has a test of that rule (\`libs/transformer/tests/test_deterministic_order.py\`). Polars promises no row order unless asked: use \`maintain_order\`, \`keep="first"\`, \`maintain_order="left_right"\` for joins, and a fixed default \`seed\` for anything random.`

Proposed:
```
- **Determinism (ADR-090, amended by ADR-100 DEC34):** the same input gives the same rows in the same order. The order rule is written in the recipe, as a required parameter with the Polars name; the action adds no default of its own. An action that can reorder rows (grouping, deduplication, joins, sorting, sampling) requires: `polars_group_by` and `polars_sort` `maintain_order`; `polars_join` `how` and `maintain_order` (`left_right` for the order of ADR-090); `polars_unique` `keep` and `maintain_order`; `polars_sample` `seed` and `n` or `fraction`. Each rule has a test on data large enough to expose a random order (`libs/transformer/tests/test_deterministic_order.py`).
```
CHANGES A RULE (from "a default in the action" to "a required parameter in the recipe").
Why: `adr_100_recipe_format_1_draft.md:145-159` ("ADR-090, proposed new wording", DEC34); shipped steps carry `maintain_order` (`2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml`). The new wording of ADR-090 is a draft: it is in the ADR log as a proposed text, not yet as an edited ADR-090 (see `adr_sync_changes.md`); Eve confirms both together.

## 5. Line 42, 1:1:1 Naming Law (FACT)

Today (line 42): `- **1:1:1 Naming Law:** Logic: \`@register_action("name")\` -> Data analysis recipe: \`name_data_analysis_recipe.yaml\` -> Data: \`name_test.tsv\`.`
Proposed: `- **1:1:1 Naming Law (enforced by test):** Logic: \`@register_action("name")\` -> recipe \`libs/transformer/tests/data/name_data_analysis_recipe.yaml\` (format 1, \`id\` equal to the action name) -> data \`libs/transformer/tests/data/name_test.tsv\`. A new action without its pair, or a pair of a removed action, fails \`libs/transformer/tests/test_action_recipe_pairs.py\`. A join action has two data files (\`name_test.tsv\` and \`name_test_right.tsv\`).`
Why: the module docstring of `test_action_recipe_pairs.py:1-22` (ACTION-RECIPES-1). The old text had no path and no mention of the test.

## 6. Line 43, Documentation Standard (FACT, small)

Today (line 43, last sentence): `For 1:1 Polars wrappers, \`wraps\` MUST also be populated ...`
Proposed: add ` and the registry field \`polars\` (\`exact\`, \`wrapper\`, \`modified\` or \`composite\`, DEC31) says how the action relates to Polars`.
Why: `polars_calls.py:228-229` sets both `polars` and `wraps`.

## 7. Lines 60-62, Flat List Rejection (FACT)

Today (line 62): `The engine rejects flat \`wrangling:\` lists with a \`DataAnalysisRecipeError\`. ...`
Proposed: `The checker refuses a \`wrangling\` that is not a mapping of \`tier1\` (and optionally \`tier2\`) (check S06), before the run; HOME's gate does not load such a recipe.`
Why: `recipe_check.py:297-299` (S06). I did not verify that the engine still raises `DataAnalysisRecipeError` itself; the checker is the gate (ADR-100 point 3), so the checker is named.

## 8. Section 4, lines 64-74 (CHANGES A RULE)

Today (lines 64-74): heading "The Data analysis recipe Data Contract (ADR-013 & Identity Logic)"; three required items (`input_fields`, `wrangling`, `output_fields`); "Identity Transformations (ADR-014)": if `output_fields` is omitted all `input_fields` are retained.

Proposed (replaces section 4):
```
## 4. The Recipe Data Contract (ADR-100)

> **SUPERSEDED (ADR-013 and ADR-014, by ADR-100 DEC23, DEC24, DEC45, 2026-11-14):** the schema `output_fields` block and the "identity when `output_fields` is omitted" rule are gone. The published columns are the columns left by the last tier-1 step.

A schema of a format-1 recipe MUST contain:

1. `input_fields`: the raw incoming schema, a mapping `column: {type: <Polars dtype>, ...}`. Reading is strict: only declared fields are read, and a declared column missing from the file fails (DEC24).
2. `wrangling`: `tier1` (required, even if empty) and optionally `tier2`; each a sequential list of actions.
3. `null_values` and `strip`: always stated, no default (DEC28).

- **Published columns:** the columns a schema or a join publishes are those left by its last tier-1 step. To publish a chosen list, end the step list with `polars_select` or `polars_drop` (DEC37). With no such step every column is published.
- **Identity:** if a tier is omitted or empty, the data passes through unchanged.
```
CHANGES A RULE.
Why: ADR-100 "Supersedes: ADR-013 and ADR-014 (DEC23, DEC24, DEC45)"; point 4 (strict import, DEC24, DEC28); point 5; `recipe_spec.yaml` `elements.schema.required` = `label, source, null_values, strip, input_fields, wrangling`.

## 9. Section 5, lines 76-82, Polars Parity Mandate (CHANGES A RULE; Eve to confirm: ADR-106 last line)

Today (lines 76-82): heading `## 5. The Polars Parity Mandate (ADR-035)`; "the Transformer library MUST strive for 1:1 Functional Parity with the Polars core library"; "Every significant high-level transformation ... should have a corresponding `@register_action`"; "Maintenance: Upon major Polars releases, the agent MUST perform an inventory audit"; "Goal".

Proposed (replaces section 5):
```
## 5. Polars Actions (replaces the Polars Parity Mandate)

> **QUALIFIED (ADR-100 DEC32, DEC41; ADR-106, 2026-11-14):** the heading "Polars Parity Mandate (ADR-035)" is retired. ADR-035 is the gallery taxonomy and holds no parity decision (ADR-106 "Corrects a citation"). The parity text existed only in this rule file (commit `342f7980`, 2026-04-17).

- **What is registered is exact.** A `polars_` action behaves exactly as the Polars call of that name (DEC32); the equality is proved by a test for each. A `modif_` action states its change; a `step_` action is a composite. The registry field `polars` says which (DEC31).
- **What is missing is listed.** Polars methods that have no action yet are tracked in `.claude/tasks/tasks.md` (Eve, 2026-11-14, channel M77 point 4: start them now, each as a `polars_` action under the rules of section 2). The agent does not claim parity; it keeps that list true.
- **Maintenance.** At a major Polars release the agent compares the Polars methods with the registry and adds the gaps to the list.
- **Goal.** A user can write the Polars transformations that have an action in a recipe, without Python code.
```
CHANGES A RULE (a "MUST strive for parity" becomes "what is registered is exact, what is missing is listed").
Why: ADR-106 "Replaces" line, "Corrects a citation" line and last paragraph: "Whether the mandate is withdrawn like V9 is not recorded: Eve to confirm in the rule file". ADR-100 point 6 note (M77 point 4). The same change for plotnine is in `rules_viz_factory.md.proposal.md`.
Not recorded: whether Eve wants the Polars side replaced the same way as the plotnine side (V9 was approved; this one was not). Eve decides; the old text may also be kept with only the citation corrected ("ADR-035" becomes "this file, commit `342f7980`").

## 10. Section 6, lines 84-87 (FACT, no change needed)

Checked: `debug_wrangler.py` (format-1 recipe, `--tier tier1|tier2|all`, `--output`) and `debug_assembler.py` (run on `2_test_data_ST22_dummy.yaml`: "ALL ASSEMBLY STEPS COMPLETE") both work. No change.

## 11. Section 7, line 90 (FACT)

Today: `They should only be dropped at the final assembly contract.`
Proposed: `They should only be dropped by the last \`polars_select\`/\`polars_drop\` step of the join.`
Why: ADR-100 point 5.

---

## Not settled

1. Change 9: whether the Polars parity mandate is withdrawn like the plotnine one (ADR-106 says it is not recorded).
2. Change 2: a later edit is needed when KEYS-NODE-1 is built; this proposal only marks it.
3. Section 1, Tier 3 (lines 30-34): says the leaf is "transient, on-the-fly ... exclusively via predicate pushdown from user UI inputs". ADR-099/105 (audit steps at T3 of a plot) and ADR-100 point 9 (`steps: {tier3: [...]}` on the plot entry; the reader is NOT BUILT) make this incomplete. What the rule should say before the engine reads `tier3` is not decided; no text proposed.
4. Whether the engine still raises `DataAnalysisRecipeError` for a flat `wrangling` list (change 7).
