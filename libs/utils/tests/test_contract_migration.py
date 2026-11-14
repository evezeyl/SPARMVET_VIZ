"""Migration run C: `final_contract` and the schema `output_fields` are removed (DEC23, DEC43; Eve 2026-11-14 "next step").

The published columns of a join become the last step of its tier 1, a plain `polars_select` in the order of the old
contract; the display texts of the contract become `labels`. The old engine applied `final_contract` only when it was a
dictionary (a list was skipped silently), so a list form is removed WITHOUT a select (the result stays identical) and
the migration says so. Text level: every comment stays; a second run changes nothing.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_contract_migration.py -q
"""
import textwrap

import yaml

from utils.contract_migration import migrate_contracts

BASE = textwrap.dedent("""\
    id: r
    spec_version: 1
    data_schemas:
      A:
        source: {type: local_tsv, path: a.tsv}
        null_values: []
        strip: false
        input_fields:
          sample_id: {type: String}
        wrangling: {tier1: []}
    joins:
      J:
        ingredients:
          - dataset_id: A
        steps:
          tier1:
            - action: polars_unique   # keep one row per sample
              keep: first
              maintain_order: true
          tier2: []
        final_contract:
          sample_id: categorical
          Year:
            type: integer
            label: Collection year
    analysis_groups: {}
    """)


def write(tmp_path, text, name="r.yaml"):
    path = tmp_path / name
    path.write_text(text)
    return path


def load(path):
    return yaml.safe_load(path.read_text())


def test_a_dry_run_changes_nothing(tmp_path):
    path = write(tmp_path, BASE)
    report = migrate_contracts(path, apply=False)
    assert path.read_text() == BASE and any("polars_select" in line for line in report.lines)


def test_an_inline_contract_becomes_the_last_step_of_tier1_in_the_same_column_order(tmp_path):
    path = write(tmp_path, BASE)
    migrate_contracts(path, apply=True)
    join = load(path)["joins"]["J"]
    assert join["steps"]["tier1"][-1] == {"action": "polars_select", "exprs": ["sample_id", "Year"]}
    assert len(join["steps"]["tier1"]) == 2 and "final_contract" not in join


def test_the_labels_of_the_contract_become_labels_and_other_comments_stay(tmp_path):
    path = write(tmp_path, BASE)
    migrate_contracts(path, apply=True)
    assert load(path)["joins"]["J"]["labels"] == {"Year": "Collection year"}
    assert "# keep one row per sample" in path.read_text()


def test_a_second_run_changes_nothing(tmp_path):
    path = write(tmp_path, BASE)
    migrate_contracts(path, apply=True)
    once = path.read_text()
    report = migrate_contracts(path, apply=True)
    assert path.read_text() == once and report.changed_files == []


def test_a_contract_in_a_fragment_with_a_wrapper_key_is_read_and_the_fragment_is_deleted(tmp_path):
    (tmp_path / "frag.yaml").write_text("output_fields:\n  sample_id:\n    type: categorical\n    label: Sample\n  Year:\n    type: integer\n")
    path = write(tmp_path, BASE[:BASE.index("    final_contract:")] + "    final_contract: !include frag.yaml\nanalysis_groups: {}\n")
    report = migrate_contracts(path, apply=True)
    join = load(path)["joins"]["J"]
    assert join["steps"]["tier1"][-1]["exprs"] == ["sample_id", "Year"] and join["labels"] == {"sample_id": "Sample"}
    assert not (tmp_path / "frag.yaml").exists() and any("frag.yaml" in line for line in report.lines)


def test_a_fragment_that_another_recipe_still_includes_is_kept_until_the_last_one_is_migrated(tmp_path):
    (tmp_path / "frag.yaml").write_text("sample_id: categorical\n")
    head = BASE[:BASE.index("    final_contract:")]
    first = write(tmp_path, head + "    final_contract: !include frag.yaml\nanalysis_groups: {}\n", "first.yaml")
    second = write(tmp_path, head.replace("id: r", "id: s") + "    final_contract: !include frag.yaml\nanalysis_groups: {}\n", "second.yaml")
    migrate_contracts(first, apply=True)
    assert (tmp_path / "frag.yaml").exists()          # second.yaml still includes it
    migrate_contracts(second, apply=True)
    assert not (tmp_path / "frag.yaml").exists()
    assert load(second)["joins"]["J"]["steps"]["tier1"][-1]["exprs"] == ["sample_id"]


def test_the_steps_in_a_fragment_get_the_select_in_the_fragment(tmp_path):
    (tmp_path / "steps.yaml").write_text("tier1:\n  - action: polars_unique\n    keep: first\n    maintain_order: true\ntier2: []\n")
    text = BASE.replace(BASE[BASE.index("    steps:"):BASE.index("    final_contract:")], "    steps: !include steps.yaml\n")
    path = write(tmp_path, text)
    migrate_contracts(path, apply=True)
    frag = yaml.safe_load((tmp_path / "steps.yaml").read_text())
    assert frag["tier1"][-1] == {"action": "polars_select", "exprs": ["sample_id", "Year"]} and frag["tier2"] == []


def test_an_empty_tier1_gets_a_list_with_the_select(tmp_path):
    text = BASE.replace(BASE[BASE.index("    steps:"):BASE.index("    final_contract:")], "    steps: {tier1: [], tier2: []}\n")
    path = write(tmp_path, text)
    migrate_contracts(path, apply=True)
    assert load(path)["joins"]["J"]["steps"]["tier1"] == [{"action": "polars_select", "exprs": ["sample_id", "Year"]}]


def test_a_contract_in_list_form_never_acted_so_it_is_removed_without_a_select_and_reported(tmp_path):
    text = BASE.replace(BASE[BASE.index("    final_contract:"):BASE.index("analysis_groups")], "    final_contract:\n      - sample_id:\n          type: categorical\n      - Year:\n          type: integer\n")
    path = write(tmp_path, text)
    report = migrate_contracts(path, apply=True)
    join = load(path)["joins"]["J"]
    assert "final_contract" not in join and len(join["steps"]["tier1"]) == 1
    assert any("list" in line and "never" in line for line in report.lines)


def test_the_schema_output_fields_are_removed_and_reported(tmp_path):
    text = BASE.replace("    wrangling: {tier1: []}\n", "    wrangling: {tier1: []}\n    output_fields:\n      sample_id: {type: categorical, label: Sample}\n")
    path = write(tmp_path, text)
    report = migrate_contracts(path, apply=True)
    assert "output_fields" not in load(path)["data_schemas"]["A"] and any("output_fields" in line for line in report.lines)


def test_a_join_without_a_contract_is_left_alone(tmp_path):
    text = BASE.replace(BASE[BASE.index("    final_contract:"):BASE.index("analysis_groups")], "")
    path = write(tmp_path, text)
    report = migrate_contracts(path, apply=True)
    assert path.read_text() == text and report.changed_files == []


def test_a_file_that_cannot_be_parsed_is_reported_and_not_touched(tmp_path):
    path = write(tmp_path, "id: r\n  bad: [\n")
    report = migrate_contracts(path, apply=True)
    assert path.read_text() == "id: r\n  bad: [\n" and any("cannot be parsed" in line for line in report.lines)


def test_the_next_join_and_the_comments_around_the_removed_key_are_not_swallowed(tmp_path):
    """Found on the shipped recipes: the end of a block mapping lies at the next key, so a naive removal ate its first line."""
    text = BASE.replace("analysis_groups: {}\n", "  K:\n    ingredients:\n      - dataset_id: A\n    steps: {tier1: []}\n    final_contract:\n      sample_id: categorical\n\n# about the groups\nanalysis_groups: {}\n")
    path = write(tmp_path, text)
    migrate_contracts(path, apply=True)
    data = load(path)
    assert set(data["joins"]) == {"J", "K"} and data["joins"]["K"]["steps"]["tier1"][-1]["exprs"] == ["sample_id"]
    assert data["joins"]["J"]["ingredients"] == [{"dataset_id": "A"}] and "# about the groups" in path.read_text()
