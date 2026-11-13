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
        "sample_id": "String", "reads": "Float64", "year": "Int64", "day": "Date", "ok": "Boolean", "note": "String"}


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
    assert load(new) == {"sample_id": {"type": "String", "is_entity_key": True}, "reads": {"type": "Float64"}}


def test_a_wrapped_fragment_is_unwrapped_and_dedented():
    fragment = "# my note\ninput_fields:\n  sample_id:\n    type: categorical   # keep\n"
    new, report = migrate_text(fragment, role="input_fields")
    assert new == "# my note\nsample_id:\n  type: String   # keep\n"
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
    assert yaml.safe_load((tmp_path / "r" / "fields.yaml").read_text()) == {"id": {"type": "String"}}
    again = migrate_recipe_file(main, apply=True)
    assert again.changed_files == []
