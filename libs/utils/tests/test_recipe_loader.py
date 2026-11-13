"""Reading a recipe file strictly (checks T01, T02, T07, T10, T11, F01) and `check_recipe_file`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_loader.py -q
"""
import textwrap

from utils.recipe_loader import check_recipe_file, load_recipe

MINIMAL = """
id: r
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info: {label: R, description: d, contact: c}
data_schemas:
  A:
    label: A
    description: One row per sample.
    source: {type: local_tsv, path: assets/test_data/a.tsv}
    null_values: []
    strip: true
    input_fields: %s
    wrangling: {tier1: []}
analysis_groups:
  g:
    label: G
    description: d
    plots:
      p:
        label: P
        description: d
        spec: {target_dataset: A, mapping: {x: id}, layers: [{name: geom_col}]}
"""
FIELDS_INLINE = "{id: {type: String, is_entity_key: true}}"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text))
    return path


def codes(problems):
    return [p.code for p in problems]


def test_a_clean_recipe_loads_without_problem(tmp_path):
    path = write(tmp_path / "r.yaml", MINIMAL % FIELDS_INLINE)
    raw, problems = load_recipe(path)
    assert problems == [] and raw["id"] == "r"


def test_a_clean_recipe_with_a_bare_fragment_passes_the_whole_check(tmp_path):
    write(tmp_path / "r" / "fields.yaml", "id: {type: String, is_entity_key: true}\n")
    path = write(tmp_path / "r.yaml", MINIMAL % "!include r/fields.yaml")
    assert check_recipe_file(path).problems == []


def test_invalid_yaml_is_t01_and_names_the_line(tmp_path):
    path = write(tmp_path / "r.yaml", "id: r\ninfo: {label: [unclosed\n")
    raw, problems = load_recipe(path)
    assert raw is None and codes(problems) == ["T01"]
    assert "line" in problems[0].message


def test_a_missing_file_is_t01(tmp_path):
    raw, problems = load_recipe(tmp_path / "nope.yaml")
    assert raw is None and codes(problems) == ["T01"]


def test_a_repeated_key_is_t10_and_names_both_lines(tmp_path):
    path = write(tmp_path / "r.yaml", "id: r\nid: s\n")
    raw, problems = load_recipe(path)
    assert codes(problems) == ["T10"]
    assert "line 1" in problems[0].message and "line 2" in problems[0].message


def test_a_repeated_key_deep_inside_a_mapping_is_found(tmp_path):
    path = write(tmp_path / "r.yaml", MINIMAL % "{id: {type: String}, id: {type: Int64}}")
    assert codes(load_recipe(path)[1]) == ["T10"]


def test_a_missing_include_is_t02(tmp_path):
    path = write(tmp_path / "r.yaml", MINIMAL % "!include r/missing.yaml")
    raw, problems = load_recipe(path)
    assert "T02" in codes(problems)
    assert problems[0].fix


def test_an_include_outside_the_project_is_t11(tmp_path):
    write(tmp_path / "outside.yaml", "id: {type: String}\n")
    path = write(tmp_path / "recipes" / "r.yaml", MINIMAL % "!include ../outside.yaml")
    assert "T11" in codes(load_recipe(path)[1])


def test_an_absolute_include_is_t11(tmp_path):
    target = write(tmp_path / "elsewhere" / "f.yaml", "id: {type: String}\n")
    path = write(tmp_path / "recipes" / "r.yaml", MINIMAL % f"!include {target}")
    assert "T11" in codes(load_recipe(path)[1])


def test_a_fragment_that_repeats_the_key_it_is_included_under_is_f01(tmp_path):
    write(tmp_path / "r" / "fields.yaml", "input_fields:\n  id: {type: String, is_entity_key: true}\n")
    path = write(tmp_path / "r.yaml", MINIMAL % "!include r/fields.yaml")
    raw, problems = load_recipe(path)
    assert codes(problems) == ["F01"]
    assert "remove" in problems[0].fix
    assert "input_fields" in problems[0].path


def test_the_wrapper_is_not_removed_silently(tmp_path):
    write(tmp_path / "r" / "fields.yaml", "input_fields:\n  id: {type: String}\n")
    path = write(tmp_path / "r.yaml", MINIMAL % "!include r/fields.yaml")
    raw, _ = load_recipe(path)
    assert raw["data_schemas"]["A"]["input_fields"] == {"input_fields": {"id": {"type": "String"}}}


def test_an_unquoted_on_is_t07_with_the_path(tmp_path):
    text = MINIMAL % FIELDS_INLINE + "joins:\n  J:\n    steps:\n      tier1:\n        - {action: polars_join, on: id}\n"
    raw, problems = load_recipe(write(tmp_path / "r.yaml", text))
    assert codes(problems) == ["T07"]
    assert "'on'" in problems[0].fix


def test_a_nested_include_uses_the_recipe_folder(tmp_path):
    write(tmp_path / "r" / "inner.yaml", "{type: String, is_entity_key: true}\n")
    write(tmp_path / "r" / "fields.yaml", "id: !include r/inner.yaml\n")
    path = write(tmp_path / "r.yaml", MINIMAL % "!include r/fields.yaml")
    assert check_recipe_file(path).problems == []


def test_check_recipe_file_merges_loader_and_checker_problems_and_names_the_file(tmp_path):
    path = write(tmp_path / "wrong_name.yaml", (MINIMAL % FIELDS_INLINE).replace("strip: true", "strip: true\n    extra: 1"))
    result = check_recipe_file(path)
    assert "T05" in result.codes() and "S01" in result.codes()


def test_check_recipe_file_stops_with_t01_when_the_file_cannot_be_read(tmp_path):
    result = check_recipe_file(write(tmp_path / "r.yaml", "a: [\n"))
    assert result.codes() == ["T01"]
