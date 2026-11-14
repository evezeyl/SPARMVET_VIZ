"""Migration run D: the recipes take the strict form that `check_recipe` asks for (spec sections 5, 7, 12).

Runs A to C changed names, types and the contract. What is left is form: a label on every schema, join, group and plot
(the app made one up from the id or the description: a hidden rule), the old `info` blocks, the stray taxonomy keys in
plot specs, wrapper keys in fragments, removed keys. Run D writes what the app showed, so nothing changes on the screen,
and removes what nothing read. Text level: comments stay; a second run changes nothing.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_strict_form_migration.py -q
"""
import textwrap

import yaml

from utils.strict_form_migration import migrate_strict_form

BASE = textwrap.dedent("""\
    id: r
    spec_version: 1
    info:
      label: R
    data_schemas:
      My_Table:
        info:
          category: Quality Control
          sub_category: Reads   # which part
          comments: Filtered before delivery
        source: {type: local_tsv, path: a.tsv}
        null_values: []
        strip: false
        input_fields:
          sample_id:
            type: String
            role: primary_key
        wrangling: []
    joins:
      Big_Join:
        ingredients:
          - dataset_id: My_Table
        steps:
          tier1: []
    analysis_groups:
      Quality Control:
        description: QC of the reads
        plots:
          reads_bar_plot:
            info: Reads per sample.
            spec:
              target_dataset: Big_Join
              family: Distribution
              pattern: 1 Numeric, 1 Categorical
              difficulty: Simple
              description: Total reads, one bar per sample.
              mapping: {x: sample_id}
              layers:
                - name: geom_bar
                  params: {}
    """)


def write(tmp_path, text, name="r.yaml"):
    path = tmp_path / name
    path.write_text(text)
    return path


def load(path):
    return yaml.safe_load(path.read_text())


def migrated(tmp_path, text=BASE):
    path = write(tmp_path, text)
    report = migrate_strict_form(path, apply=True)
    return path, load(path), report


def test_a_dry_run_changes_nothing(tmp_path):
    path = write(tmp_path, BASE)
    report = migrate_strict_form(path, apply=False)
    assert path.read_text() == BASE and report.lines


def test_a_second_run_changes_nothing(tmp_path):
    path, _, _ = migrated(tmp_path)
    once = path.read_text()
    report = migrate_strict_form(path, apply=True)
    assert path.read_text() == once and report.changed_files == []


# -- labels: what the app showed is written ----------------------------------------------------------

def test_a_group_without_a_label_gets_its_description_as_label_like_the_app_showed(tmp_path):
    _, data, _ = migrated(tmp_path)
    assert data["analysis_groups"]["Quality Control"]["label"] == "QC of the reads"


def test_a_group_with_neither_gets_its_id(tmp_path):
    _, data, _ = migrated(tmp_path, BASE.replace("    description: QC of the reads\n", ""))
    assert data["analysis_groups"]["Quality Control"]["label"] == "Quality Control"


def test_a_plot_without_a_label_gets_the_title_cased_id_like_the_app_showed(tmp_path):
    _, data, _ = migrated(tmp_path)
    assert data["analysis_groups"]["Quality Control"]["plots"]["reads_bar_plot"]["label"] == "Reads Bar Plot"


def test_a_schema_and_a_join_get_their_id_with_spaces(tmp_path):
    _, data, _ = migrated(tmp_path)
    assert data["data_schemas"]["My_Table"]["label"] == "My Table" and data["joins"]["Big_Join"]["label"] == "Big Join"


def test_a_label_that_is_written_is_kept(tmp_path):
    text = BASE.replace("  Big_Join:\n", "  Big_Join:\n    label: The big one\n")
    _, data, _ = migrated(tmp_path, text)
    assert data["joins"]["Big_Join"]["label"] == "The big one"


# -- the old info blocks ---------------------------------------------------------------------------

def test_the_info_of_a_schema_becomes_description_and_comment(tmp_path):
    path, data, _ = migrated(tmp_path)
    schema = data["data_schemas"]["My_Table"]
    assert "info" not in schema
    assert schema["description"] == "Reads (Quality Control)" and schema["comment"] == "Filtered before delivery"


def test_the_info_of_a_plot_and_the_description_of_its_spec_become_one_description(tmp_path):
    _, data, _ = migrated(tmp_path)
    plot = data["analysis_groups"]["Quality Control"]["plots"]["reads_bar_plot"]
    assert "info" not in plot and plot["description"] == "Reads per sample. Total reads, one bar per sample."
    assert "description" not in plot["spec"]


# -- the stray keys of a plot spec -----------------------------------------------------------------

def test_the_taxonomy_keys_of_a_spec_move_to_the_plot_entry(tmp_path):
    _, data, _ = migrated(tmp_path)
    plot = data["analysis_groups"]["Quality Control"]["plots"]["reads_bar_plot"]
    assert plot["taxonomy"] == {"family": "Distribution", "pattern": "1 Numeric, 1 Categorical", "difficulty": "Simple"}
    assert set(plot["spec"]) == {"target_dataset", "mapping", "layers"}


def test_a_spec_in_a_fragment_is_cleaned_in_the_fragment_and_the_entry_gets_the_keys(tmp_path):
    (tmp_path / "p.yaml").write_text("spec:\n  target_dataset: Big_Join   # the join\n  family: Ranking\n  mapping: {x: sample_id}\n  layers:\n    - name: geom_bar\n      params: {}\n")
    text = BASE[:BASE.index("        spec:")] + "        spec: !include p.yaml\n"
    path = write(tmp_path, text)
    migrate_strict_form(path, apply=True)
    fragment = yaml.safe_load((tmp_path / "p.yaml").read_text())
    assert set(fragment) == {"target_dataset", "mapping", "layers"}          # unwrapped, the stray key gone
    assert "# the join" in (tmp_path / "p.yaml").read_text()
    entry = yaml.load(path.read_text(), Loader=yaml.BaseLoader)["analysis_groups"]["Quality Control"]["plots"]["reads_bar_plot"]
    assert entry["taxonomy"] == {"family": "Ranking"} and entry["label"] == "Reads Bar Plot"


# -- wrappers, removed keys, forms -----------------------------------------------------------------

def test_a_fragment_that_starts_with_the_key_it_is_included_under_is_unwrapped(tmp_path):
    (tmp_path / "w.yaml").write_text("# cleaning\nwrangling:\n  tier1:\n    - action: polars_unique   # one row\n      keep: first\n      maintain_order: true\n  tier2: []\n")
    path = write(tmp_path, BASE.replace("    wrangling: []\n", "    wrangling: !include w.yaml\n"))
    migrate_strict_form(path, apply=True)
    text = (tmp_path / "w.yaml").read_text()
    assert yaml.safe_load(text) == {"tier1": [{"action": "polars_unique", "keep": "first", "maintain_order": True}], "tier2": []}
    assert text.startswith("# cleaning\ntier1:\n") and "# one row" in text


def test_the_role_of_a_field_is_removed_and_reported(tmp_path):
    _, data, report = migrated(tmp_path)
    assert data["data_schemas"]["My_Table"]["input_fields"]["sample_id"] == {"type": "String"}
    assert any("role" in line for line in report.lines)


def test_an_empty_list_of_steps_becomes_the_tier_form(tmp_path):
    _, data, _ = migrated(tmp_path)
    assert data["data_schemas"]["My_Table"]["wrangling"] == {"tier1": []}


def test_a_schema_without_wrangling_gets_the_empty_tier_form(tmp_path):
    _, data, _ = migrated(tmp_path, BASE.replace("    wrangling: []\n", ""))
    assert data["data_schemas"]["My_Table"]["wrangling"] == {"tier1": []}


def test_the_output_fields_of_a_join_are_removed_and_reported(tmp_path):
    text = BASE.replace("    steps:\n      tier1: []\n", "    steps:\n      tier1: []\n    output_fields:\n      sample_id: {type: String}\n")
    _, data, report = migrated(tmp_path, text)
    assert "output_fields" not in data["joins"]["Big_Join"] and any("output_fields" in line for line in report.lines)


def test_the_comments_and_the_rest_of_the_file_stay(tmp_path):
    path, data, _ = migrated(tmp_path)
    assert "# which part" not in path.read_text()            # it was inside the info block that is replaced
    assert data["data_schemas"]["My_Table"]["source"] == {"type": "local_tsv", "path": "a.tsv"}
    assert data["analysis_groups"]["Quality Control"]["description"] == "QC of the reads"


def test_a_file_that_cannot_be_parsed_is_reported_and_not_touched(tmp_path):
    path = write(tmp_path, "id: r\n  bad: [\n")
    report = migrate_strict_form(path, apply=True)
    assert path.read_text() == "id: r\n  bad: [\n" and any("cannot be parsed" in line for line in report.lines)
