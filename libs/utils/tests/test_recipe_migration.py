"""Migration run A, the part that does not depend on the action names: keys, field types, spec_version, engines and the
explicit missing-value setting (spec 4.1, decision DEC43). Text-level: every `#` comment and the layout stay.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_migration.py -q
"""
import textwrap

import yaml

from utils.recipe_migration import SANITISER_TEXTS, migrate_recipe_file, migrate_text

OLD = textwrap.dedent("""\
    id: old_recipe
    info:
      display_name: Old recipe   # the name
      description: What it answers.
    # the schemas
    data_schemas:
      A:
        source:
          type: local_tsv
          path: assets/test_data/a.tsv
        input_fields:
          sample_id:
            type: categorical        # a group
            is_primary_key: true
            source_name: Sample ID
          reads: {type: numeric, label: Reads}
          year: {type: integer}
          day: {type: date}
          ok: {type: boolean}
          note: {type: utf8}
        wrangling:
          tier1: []
    analysis_groups: {}
    """)


def load(text):
    return yaml.safe_load(text)


def test_spec_version_and_engines_are_added_after_the_id():
    new, report = migrate_text(OLD, role="recipe")
    assert new.startswith("id: old_recipe\nspec_version: 1\ndata_engine: python-polars\nplot_engine: python-plotnine\ninfo:")
    assert any("spec_version" in line for line in report)


def test_a_key_that_is_already_there_is_not_added_again():
    once, _ = migrate_text(OLD, role="recipe")
    twice, report = migrate_text(once, role="recipe")
    assert twice == once and report == []


def test_the_field_types_become_polars_names():
    new, _ = migrate_text(OLD, role="recipe")
    fields = load(new)["data_schemas"]["A"]["input_fields"]
    assert {k: v["type"] for k, v in fields.items()} == {
        "sample_id": "Categorical", "reads": "Float64", "year": "Int64", "day": "Date", "ok": "Boolean", "note": "String"}


def test_the_field_keys_are_renamed():
    fields = load(migrate_text(OLD, role="recipe")[0])["data_schemas"]["A"]["input_fields"]["sample_id"]
    assert fields["is_entity_key"] is True and fields["original_name"] == "Sample ID"
    assert "is_primary_key" not in fields and "source_name" not in fields


def test_display_name_becomes_label():
    assert load(migrate_text(OLD, role="recipe")[0])["info"]["label"] == "Old recipe"


def test_each_schema_gets_the_old_sanitiser_as_explicit_settings():
    schema = load(migrate_text(OLD, role="recipe")[0])["data_schemas"]["A"]
    assert schema["strip"] is True
    assert schema["null_values"] == list(SANITISER_TEXTS) and len(SANITISER_TEXTS) == 14


def test_a_schema_that_states_its_settings_keeps_them():
    text = OLD.replace("    input_fields:", "    null_values: [NA]\n    strip: false\n    input_fields:", 1)
    schema = load(migrate_text(text, role="recipe")[0])["data_schemas"]["A"]
    assert schema["null_values"] == ["NA"] and schema["strip"] is False


def test_comments_and_layout_survive():
    new, _ = migrate_text(OLD, role="recipe")
    for comment in ("# the name", "# the schemas", "# a group"):
        assert comment in new
    assert "reads: {type: Float64, label: Reads}" in new


def test_the_result_is_the_same_recipe_otherwise():
    before, after = load(OLD), load(migrate_text(OLD, role="recipe")[0])
    assert after["data_schemas"]["A"]["source"] == before["data_schemas"]["A"]["source"]
    assert after["data_schemas"]["A"]["wrangling"] == before["data_schemas"]["A"]["wrangling"]


def test_an_input_fields_fragment_is_migrated_by_its_role():
    fragment = "sample_id:\n  type: categorical\n  is_primary_key: true\nreads: {type: numeric}\n"
    new, _ = migrate_text(fragment, role="input_fields")
    assert load(new) == {"sample_id": {"type": "Categorical", "is_entity_key": True}, "reads": {"type": "Float64"}}


def test_a_wrapped_fragment_is_unwrapped_and_dedented():
    fragment = "# my note\ninput_fields:\n  sample_id:\n    type: categorical   # keep\n"
    new, report = migrate_text(fragment, role="input_fields")
    assert new == "# my note\nsample_id:\n  type: Categorical   # keep\n"
    assert any("wrapper" in line for line in report)


def test_a_type_with_no_known_replacement_is_reported_not_guessed():
    new, report = migrate_text("x: {type: weird}\n", role="input_fields")
    assert new == "x: {type: weird}\n" and any("weird" in line for line in report)


def test_a_file_is_migrated_with_its_fragments(tmp_path):
    (tmp_path / "r").mkdir()
    (tmp_path / "r" / "fields.yaml").write_text("input_fields:\n  id: {type: categorical}\n")
    main = tmp_path / "old.yaml"
    main.write_text(textwrap.dedent("""\
        id: old
        data_schemas:
          A:
            source: {type: local_tsv, path: a.tsv}
            input_fields: !include r/fields.yaml
            wrangling: {tier1: []}
        """))
    dry = migrate_recipe_file(main, apply=False)
    assert main.read_text().startswith("id: old\ndata_schemas")      # nothing written
    assert dry.changed_files == [main, tmp_path / "r" / "fields.yaml"]
    migrate_recipe_file(main, apply=True)
    assert yaml.safe_load((tmp_path / "r" / "fields.yaml").read_text()) == {"id": {"type": "Categorical"}}
    again = migrate_recipe_file(main, apply=True)
    assert again.changed_files == []


# -- the steps (run A, part 2) ------------------------------------------------------------------------------------

STEPS_TEXT = """\
# fragment of tier lists
tier1:
  # first the cleaning
  - action: strip_whitespace   # a note on this step
    columns: [name]

  - action: "join"
    right_ingredient: "R"
    "on": "id"
    how: "left"

  # then the filter
  - action: filter_range
    columns: [identity]
    min: 90
tier2: []
"""


def test_steps_are_converted_in_place_and_every_comment_stays():
    from utils.recipe_migration import migrate_steps_text
    new, lines = migrate_steps_text(STEPS_TEXT)
    assert "# fragment of tier lists" in new and "# first the cleaning" in new and "# then the filter" in new
    assert "# a note on this step" in new
    assert "polars_str_strip_chars" in new and "polars_join" in new and "modif_filter" in new
    assert "strip_whitespace" not in new and "filter_range" not in new
    assert len(lines) == 3


def test_the_converted_steps_are_valid_yaml_with_the_right_content():
    import yaml
    from utils.recipe_migration import migrate_steps_text
    new, _ = migrate_steps_text(STEPS_TEXT)
    data = yaml.safe_load(new)
    assert [s["action"] for s in data["tier1"]] == ["polars_str_strip_chars", "polars_join", "modif_filter"]
    assert data["tier1"][1]["on"] == ["id"] and data["tier1"][1]["maintain_order"] == "left_right"
    assert data["tier1"][2] == {"action": "modif_filter", "column": "identity", "op": "ge", "value": 90, "na": "remove"}
    assert data["tier2"] == []


def test_a_second_run_changes_nothing():
    from utils.recipe_migration import migrate_steps_text
    once, _ = migrate_steps_text(STEPS_TEXT)
    twice, lines = migrate_steps_text(once)
    assert twice == once and lines == []


def test_a_step_that_needs_a_person_stays_and_is_reported():
    from utils.recipe_migration import migrate_steps_text
    text = "tier1:\n  - action: percentile\n    column: x\n  - action: sort\n    columns: [a]\n"
    new, lines = migrate_steps_text(text)
    assert "- action: percentile" in new and "polars_sort" in new
    assert any("percentile" in line and "removed" in line for line in lines)


def test_one_step_can_become_several_with_the_dashes_aligned():
    import yaml
    from utils.recipe_migration import migrate_steps_text
    text = "tier1:\n    - action: split_column\n      columns: [p]\n      new_columns: [a, b]\n      delimiter: _\n"
    new, _ = migrate_steps_text(text)
    data = yaml.safe_load(new)
    assert [s["action"] for s in data["tier1"]] == ["polars_str_splitn", "polars_unnest", "polars_rename"]
    assert all(line.startswith("    - ") or line.startswith("      ") for line in new.splitlines()[1:])


def test_strip_whitespace_without_columns_takes_the_text_fields_of_its_schema(tmp_path):
    import yaml
    from utils.recipe_migration import migrate_recipe_file
    recipe = tmp_path / "r.yaml"
    recipe.write_text("id: r\ndata_schemas:\n  T:\n    input_fields:\n      a: {type: categorical}\n      n: {type: numeric}\n      b: {type: utf8}\n"
                      "    wrangling:\n      tier1:\n        - action: strip_whitespace\n", encoding="utf-8")
    migrate_recipe_file(recipe, apply=True)
    step = yaml.safe_load(recipe.read_text(encoding="utf-8"))["data_schemas"]["T"]["wrangling"]["tier1"][0]
    assert step["action"] == "polars_str_strip_chars" and step["columns"] == ["b"]   # a categorical field was cast before the step, so it was not a String column
