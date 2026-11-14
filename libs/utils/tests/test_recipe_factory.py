"""`utils.recipe_factory`: a minimal valid recipe in format 1 as a dictionary, and the writers of recipe text (W8).

The factory is the shared helper of the tests and of every program that writes a recipe, so what it returns must pass
the checker and load through the app's loader, and what it writes must keep the order of the keys.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_factory.py -q
"""
import pytest
import yaml

from utils.config_loader import ConfigManager
from utils.recipe_check import check_recipe, spec
from utils.recipe_factory import (Include, minimal_join, minimal_plot, minimal_recipe, minimal_schema, recipe_text,
                                  write_fragment, write_recipe)
from utils.recipe_loader import check_recipe_file, load_recipe
from utils.strict_yaml import load_strict

TOP_ORDER = ["id", "spec_version", "data_engine", "plot_engine", "info", "data_schemas", "analysis_groups"]


def codes(result):
    return [p.code for p in result.errors]


# -- the dictionary

def test_the_default_recipe_has_no_error_in_profile_run():
    result = check_recipe(minimal_recipe("tiny"), "run", file_stem="tiny")
    assert result.errors == []


def test_the_top_level_keys_come_in_the_order_of_the_specification():
    assert list(minimal_recipe("tiny")) == TOP_ORDER


def test_the_version_and_the_engines_are_read_from_the_specification_data():
    recipe = minimal_recipe("tiny")
    assert recipe["spec_version"] == spec()["format_version"]
    assert recipe["data_engine"] in spec()["engines"]["data_engine"]
    assert recipe["plot_engine"] in spec()["engines"]["plot_engine"]


def test_the_label_is_the_id_unless_given():
    assert minimal_recipe("tiny")["info"] == {"label": "tiny"}
    assert minimal_recipe("tiny", label="Tiny recipe")["info"] == {"label": "Tiny recipe"}


def test_no_old_key_is_written():
    recipe = minimal_recipe("tiny", joins={"C": minimal_join(["table"], [])})
    text = recipe_text(recipe)
    for old in ("output_fields", "final_contract", "display_name", "is_primary_key", "source_name"):
        assert old not in text
    assert "name" not in recipe["info"]


def test_two_calls_share_no_object():
    first, second = minimal_recipe("tiny"), minimal_recipe("tiny")
    first["data_schemas"]["table"]["input_fields"]["sample_id"]["type"] = "Int64"
    assert second["data_schemas"]["table"]["input_fields"]["sample_id"]["type"] == "String"


def test_the_arguments_are_not_changed_by_the_call():
    schemas = {"a": minimal_schema("data/a.tsv", {"x": "String"})}
    plots = {"p": minimal_plot("a", {"x": "x"})}
    recipe = minimal_recipe("tiny", schemas=schemas, steps=[{"action": "anything"}], plots=plots)
    recipe["analysis_groups"]["main"]["plots"]["p"]["label"] = "changed"
    assert schemas["a"]["wrangling"] == {"tier1": []}
    assert plots["p"]["label"] == "Plot of a"


def test_given_schemas_and_plots_are_used_as_they_are():
    schemas = {"reads": minimal_schema("data/reads.tsv", {"sample_id": "String", "reads": "Int64"}, entity_key="sample_id")}
    plots = {"reads_per_sample": minimal_plot("reads", {"x": "sample_id", "y": "reads"}, [{"name": "geom_col"}])}
    recipe = minimal_recipe("tiny", schemas=schemas, plots=plots)
    assert check_recipe(recipe, "run", file_stem="tiny").errors == []
    assert list(recipe["data_schemas"]) == ["reads"]
    assert recipe["data_schemas"]["reads"]["input_fields"]["sample_id"] == {"type": "String", "is_entity_key": True}
    assert recipe["data_schemas"]["reads"]["input_fields"]["reads"] == {"type": "Int64"}
    assert recipe["analysis_groups"]["main"]["plots"]["reads_per_sample"]["spec"]["layers"] == [{"name": "geom_col"}]


def test_the_default_plot_draws_the_first_column_of_the_first_schema():
    schemas = {"reads": minimal_schema("data/reads.tsv", {"country": "String", "reads": "Int64"})}
    recipe = minimal_recipe("tiny", schemas=schemas)
    (plot_id, plot), = recipe["analysis_groups"]["main"]["plots"].items()
    assert plot_id == "tiny_plot"
    assert plot["spec"]["target_dataset"] == "reads" and plot["spec"]["mapping"] == {"x": "country"}


def test_the_default_plot_draws_the_first_join_when_there_is_one():
    recipe = minimal_recipe("tiny", joins={"C": minimal_join(["table"], [])})
    assert check_recipe(recipe, "run", file_stem="tiny").errors == []
    assert list(recipe) == TOP_ORDER[:6] + ["joins", "analysis_groups"]
    (plot,) = recipe["analysis_groups"]["main"]["plots"].values()
    assert plot["spec"]["target_dataset"] == "C"
    assert recipe["joins"]["C"]["ingredients"] == [{"dataset_id": "table"}]
    assert recipe["joins"]["C"]["steps"] == {"tier1": []}


def test_without_plots_the_recipe_is_a_draft_valid_in_profile_build_only():
    draft = minimal_recipe("tiny", plots={})
    assert draft["analysis_groups"] == {}
    assert check_recipe(draft, "build", file_stem="tiny").errors == []
    assert codes(check_recipe(draft, "run", file_stem="tiny")) == ["T09"]


def test_steps_go_to_tier1_of_the_only_schema_in_the_given_order():
    steps = [{"action": "b_second_in_the_alphabet", "columns": ["value"]}, {"action": "a_first_in_the_alphabet"}]
    recipe = minimal_recipe("tiny", steps=steps)
    assert recipe["data_schemas"]["table"]["wrangling"] == {"tier1": steps}


def test_steps_with_several_schemas_are_refused_because_the_place_is_not_said():
    schemas = {"a": minimal_schema("data/a.tsv", {"x": "String"}), "b": minimal_schema("data/b.tsv", {"x": "String"})}
    with pytest.raises(ValueError, match="minimal_schema"):
        minimal_recipe("tiny", schemas=schemas, steps=[{"action": "anything"}])


def test_a_schema_without_columns_is_refused_by_the_default_plot_with_a_plain_message():
    with pytest.raises(ValueError, match="no column"):
        minimal_recipe("tiny", schemas={"empty": minimal_schema("data/e.tsv", {})})


def test_a_schema_without_columns_is_accepted_when_the_plots_are_given():
    schemas = {"empty": minimal_schema("data/e.tsv", {})}
    assert check_recipe(minimal_recipe("tiny", schemas=schemas, plots={}), "build", file_stem="tiny").errors == []


def test_the_schema_states_how_missing_values_are_read():
    schema = minimal_schema("data/a.tsv", {"x": "String"})
    assert schema["null_values"] == [] and schema["strip"] is False
    schema = minimal_schema("data/a.tsv", {"x": "String"}, null_values=["NA"], strip=True, tier2=[{"action": "s"}])
    assert schema["null_values"] == ["NA"] and schema["strip"] is True
    assert schema["wrangling"] == {"tier1": [], "tier2": [{"action": "s"}]}


def test_a_field_can_be_given_as_a_full_mapping():
    schema = minimal_schema("data/a.tsv", {"level": {"type": "Enum", "categories": ["low", "high"]}})
    assert schema["input_fields"]["level"] == {"type": "Enum", "categories": ["low", "high"]}


def test_an_entity_key_that_is_not_a_column_is_refused():
    with pytest.raises(ValueError, match="sample_id"):
        minimal_schema("data/a.tsv", {"x": "String"}, entity_key="sample_id")


def test_a_plot_can_carry_its_tier3_steps():
    plot = minimal_plot("table", {"x": "sample_id"}, tier3=[])
    assert plot["steps"] == {"tier3": []}
    assert "steps" not in minimal_plot("table", {"x": "sample_id"})


# -- the text

def test_the_written_recipe_passes_the_checker_and_loads_through_the_loader_of_the_app(tmp_path):
    path = write_recipe(tmp_path / "tiny.yaml", minimal_recipe("tiny"))
    assert check_recipe_file(path).errors == []
    loaded = ConfigManager(str(path)).raw_config
    assert loaded["id"] == "tiny" and loaded["spec_version"] == 1
    assert list(loaded["data_schemas"]["table"]["input_fields"]) == ["sample_id", "value"]


def test_the_written_text_keeps_the_order_of_the_keys(tmp_path):
    """The order of the groups is the order of the tabs: a writer that sorts would put `a_last` first."""
    recipe = minimal_recipe("tiny")
    main = recipe["analysis_groups"].pop("main")
    recipe["analysis_groups"] = {"z_first": main, "a_last": {"label": "Last", "plots": {}}}
    path = write_recipe(tmp_path / "tiny.yaml", recipe)
    text = path.read_text(encoding="utf-8")
    assert [text.index(f"\n{key}:") for key in TOP_ORDER[1:]] == sorted(text.index(f"\n{key}:") for key in TOP_ORDER[1:])
    assert text.startswith("id: tiny\n")
    assert text.index("z_first:") < text.index("a_last:")
    raw, problems = load_recipe(path)
    assert problems == [] and list(raw["analysis_groups"]) == ["z_first", "a_last"]


def test_a_recipe_whose_id_is_not_the_file_name_is_not_written(tmp_path):
    with pytest.raises(ValueError, match="other"):
        write_recipe(tmp_path / "other.yaml", minimal_recipe("tiny"))
    assert not (tmp_path / "other.yaml").exists()


def test_nothing_to_write_is_refused(tmp_path):
    with pytest.raises(ValueError):
        write_recipe(tmp_path / "tiny.yaml", {})
    assert not (tmp_path / "tiny.yaml").exists()


def test_the_join_key_on_is_written_quoted(tmp_path):
    """An unquoted `on` is read back as the boolean true (check T07)."""
    schemas = {"a": minimal_schema("data/a.tsv", {"sample_id": "String"}), "b": minimal_schema("data/b.tsv", {"sample_id": "String"})}
    join = minimal_join(["a", "b"], [{"action": "some_join", "right_ingredient": "b", "on": "sample_id", "how": "left"}])
    path = write_recipe(tmp_path / "tiny.yaml", minimal_recipe("tiny", schemas=schemas, joins={"C": join}))
    assert "'on': sample_id" in path.read_text(encoding="utf-8")
    raw, problems = load_recipe(path)
    assert problems == [] and raw["joins"]["C"]["steps"]["tier1"][0]["on"] == "sample_id"


def test_one_object_used_twice_is_written_twice_not_as_an_anchor(tmp_path):
    fields = {"sample_id": "String"}
    shared = minimal_schema("data/a.tsv", fields)["input_fields"]
    recipe = minimal_recipe("tiny", schemas={"a": minimal_schema("data/a.tsv", fields), "b": minimal_schema("data/b.tsv", fields)})
    recipe["data_schemas"]["a"]["input_fields"] = shared
    recipe["data_schemas"]["b"]["input_fields"] = shared
    text = recipe_text(recipe)
    assert "&id" not in text and "*id" not in text
    assert text.count("sample_id:") == 2


def test_text_outside_ascii_is_kept_readable(tmp_path):
    path = write_recipe(tmp_path / "tiny.yaml", minimal_recipe("tiny", label="Prøver fra Tromsø"))
    assert "Prøver fra Tromsø" in path.read_text(encoding="utf-8")


def test_an_include_is_written_as_a_tag_and_the_fragment_is_read_back(tmp_path):
    recipe = minimal_recipe("tiny")
    fields = recipe["data_schemas"]["table"]["input_fields"]
    recipe["data_schemas"]["table"]["input_fields"] = Include("tiny/table_input_fields.yaml")
    write_fragment(tmp_path / "tiny" / "table_input_fields.yaml", fields)
    path = write_recipe(tmp_path / "tiny.yaml", recipe)
    assert "input_fields: !include 'tiny/table_input_fields.yaml'\n" in path.read_text(encoding="utf-8")
    assert check_recipe_file(path).errors == []
    assert ConfigManager(str(path)).raw_config["data_schemas"]["table"]["input_fields"] == fields


def test_a_fragment_keeps_its_comment_lines_and_holds_the_value_itself(tmp_path):
    path = write_fragment(tmp_path / "f" / "steps.yaml", {"tier1": []}, comment="Candidate key: sample_id\nWrite the steps here")
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Candidate key: sample_id\n# Write the steps here\n")
    assert load_strict(text) == {"tier1": []}


def test_an_empty_fragment_is_written_as_an_empty_mapping_or_list(tmp_path):
    assert load_strict(write_fragment(tmp_path / "a.yaml", {}).read_text()) == {}
    assert load_strict(write_fragment(tmp_path / "b.yaml", []).read_text()) == []


def test_a_fragment_that_is_not_a_mapping_or_a_list_is_refused(tmp_path):
    with pytest.raises(ValueError):
        write_fragment(tmp_path / "a.yaml", None)
    assert not (tmp_path / "a.yaml").exists()


def test_the_text_is_plain_yaml_for_any_reader():
    assert yaml.safe_load(recipe_text(minimal_recipe("tiny"))) == minimal_recipe("tiny")
