**Part 1 (data scientist)**

Correction to the brief: the assembler does NOT cast join keys to String. `data_assembler.py:68-120` (`_check_join_key_types`) fails the build when key types differ ("the engine does not change the type of a join key for you"). The old line `data_analysis_recipe_data_contract_rules.md:518` ("String is the safe common denominator") still describes the cast. Verified by reading.

**Legitimate non-string keys in other fields (external knowledge, not checked here).** Time series keyed by date. Events keyed by timestamp. A boolean flag as a group key. Integer ids and composite keys, for example (date, station).

**Runs** (`/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/key_types/k.py`):
- **Date vs Datetime:** the join raises SchemaError, so it is loud and not silent.
- **Date vs String:** Date compared to a string raises InvalidOperationError. An audit row filter whose value is typed by the user, as text in the YAML or JSON session, would fail or need a parse step per type.
- **Date to String:** `2026-01-02`. A Datetime gives `2026-01-02 00:00:00.000000`. A tz-aware Datetime gives `+02:00`. Two sources in different formats (`02/01/2026` vs `2026-1-3`) only join after an explicit parse; the engine does none.
- **Boolean:** a null key joined to itself matched 2 rows (null handling, in effect). It prints as `true` and `false`. As a key it carries almost no identity.
- **Float:** `0.1+0.2` is not `0.3`. It casts to `1e+16` or `0.30000000000000004`. It is unsafe as a key.
- **Integer:** `007` and `7` become one key (`007` parses to 7), and `7.0` fails to parse. This is the E03 reason.
- **Ambiguous DST time with a zone:** the parse fails, which is loud.

**Reasoned only:** session files (no date object, so text must be re-parsed), export, and display of the key in the audit "remove from all tables".

**Recommendation: A, strict String or Categorical.** A date key is only safe as a canonical ISO text, and then it is a String. The user can still join by date after an explicit cast step.

**Part 2: places that treat "sample id" as the only key**

Rule files:
- `.claude/rules/rules_data_analysis_recipe_structure.md:206`: "Default for identifiers... (`sample_id`, `taxon`...)". It uses the old vocabulary `categorical` and `utf8` as recipe types, with the load and output contract columns. Lines 207-212 also carry the tombstone about `string`/`character`.
- `rules_data_analysis_recipe_structure.md:211`: "REMOVED... replace `type: string` with `type: categorical`... or `utf8`". Old vocabulary.
- `rules_data_analysis_recipe_structure.md:214`: "**Primary key rule:** the sample id is a string or a categorical, never a number". It says "Primary key" and "sample id".
- `.claude/rules/rules_test_lab.md:14` and `:136`: "Single-key only (`on: sample_id`)" and "Candidate PK: sample_id".
- `.claude/rules/rules_agent_role_bioscientist.md:89`, `:196`, `:204`: "identity columns (sample_id, gene, accession)" and `sample_id: string`. The last one is the lowercase `string`, the removed type name.
- `.claude/rules/ui_implementation_contract.md:684-692`, `:704`, `:733`: "true primary keys (`sample_id`)", "`sample_id == S2` is a select". The vocabulary is "PK", "primary key", "primary_key_warning".

`.claude/knowledge/data_analysis_recipe_data_contract_rules.md`:
- `:76`: `sample_id: {original_name: sample_id, type: categorical, is_primary_key: true}`. Old lowercase `categorical` and `is_primary_key` (FD03 refuses it now).
- `:105-113`:
  - `:107`: `type: categorical # categorical | numeric | string | boolean | date`, an old type list that includes the removed `string`.
  - `:108`: `label: Sample ID`.
  - `:109`: `is_primary_key: true # marks join key`.
- `:107` and `:113` are the two known lines. `:113`: "Legacy (deprecated): `sample_id: categorical` (flat string)". It is still a `categorical` flat string, which is the bare-string form FD06 rejects.
- `:474-477`: "4 use `Categorical` for `sample_id` and 1 uses `String` will raise".
- `:518`: the "String is the safe common denominator" cast claim, which is wrong now (see the correction above).

`.claude/design/recipe_format_spec.md`:
- `:43`, `:56`: `{type: String, is_entity_key: true}`. This is the current vocabulary.
- `:276`, `:300`: the old shorthand `sample_id: categorical`, listed as removed.
- `:305`: "`sample_id` is in the `input_fields` of every table".
- `:608`: the E03 row says "(the sample id)".

`libs/utils/src/utils/recipe_check.py`:
- `:364`: "the declared entity key (the sample id) is a String or a Categorical".
- `:375`: f"The sample id {slug!r} of the table {table!r} is declared ... a number". This is the user-visible message. It also says "loses leading zeros", which only applies to integers. It would be wrong for a Date or a Boolean key if those were refused under a wider E03.
- `libs/utils/build/lib/utils/recipe_check.py:364` and `:375` are the same text. `build/lib/utils/recipe_factory.py:33`, `:139` and `:148` are a stale build copy.

UI and code texts:
- `app/modules/session_manager.py:124`: "true PKs (sample_id) and secondary/accessory keys".
- `app/handlers/test_lab_handlers.py:340-341`: default value `sample_id` and placeholder "e.g. sample_id" for the join key. `:422` and `:424`: the fallback join key `"sample_id"`. `:550`: the placeholder "sample_id, species, year, country". These are user-visible, and the `:422` and `:424` fallback is a silent default key.
- `libs/utils/src/utils/recipe_factory.py:33`, `:139` and `:148`: the default column `sample_id` ("the entity key").
- `libs/transformer/src/transformer/actions/polars_calls.py:260-340`: help examples using `sample_id`. These are only examples.

Docs `.qmd` (80 hits in total; the key-as-primary-key ones):
- `docs/user_guide/audit_pipeline.qmd:121`: "In a typical SPARMVET project the primary key is `sample_id`".
- `docs/user_guide/audit_pipeline.qmd:127`: "You can't add a `drop_column` node for `sample_id`".
- `docs/user_guide/audit_pipeline.qmd:129`: "Column `sample_id` is a join key — cannot be dropped...".
- `docs/user_guide/audit_pipeline.qmd:135`: "filter on a primary-key column — for example `sample_id == "S2"`".
- `docs/appendix/Terminology.qmd:12`: "not necessarily `sample_id`". This one already says the key is not always `sample_id`.
- `docs/appendix/data_types_philosophy.qmd:27` and `:59`: the "identifier and join key" comment. `:27` is correct about no automatic cast.
- `docs/user_guide/data_literacy.qmd:47`: "joining on a strictly unique ID".
- `docs/user_guide/glossary_and_feedback.qmd:24`: "Key: the column that identifies the entity". This one is already close to "entity key".
- `docs/foundations/data_contracts_adr.qmd:137` and `:228`, `docs/appendix/FAQ.qmd:134`, `docs/appendix/running_helper_scripts.qmd:31` (`--primary_key_data sample_id`).
- Other qmd hits: `docs/appendix/test_lab_rationale.qmd`, `audit_benchmarks_st22.qmd`, `Standards_yaml.qmd`, `data_lifecycle_theater.qmd`, `transformer_actions.qmd`, `docs/workflows/wrangling.qmd`, `docs/reference/wrangling_guide.qmd`, `development_rules.qmd`, `decorator_testing.qmd`, `docs/troubleshooting/index.qmd`.
- The worktree copies under `.claude/worktrees/recipe-plots/docs/` repeat these.

I did not list the test files under `app/tests/`, where `sample_id` is a column of a test dataset. Their paths come from grep, and the qmd list is a filtered subset of the 80 hits.

**Anything silent:**
- `app/handlers/test_lab_handlers.py:422` and `:424` fall back to `sample_id` when the join key field is empty.
- The `ui_implementation_contract.md` audit key set comes from join keys (`session_manager.py:124-150`), not from `is_entity_key`. So the key concept is split across two mechanisms.

**To tell Eve before she decides** (the wording is mine):
- The strict rule would refuse legitimate time-series keys. With A, those users must declare a String key and parse it themselves.
- Under B or C, the E03 message must change per type.
- Under B or C, the audit filter values need type-aware parsing.
