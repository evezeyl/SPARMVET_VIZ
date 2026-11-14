"""`generate_branch_plan` writes recipe text: what it writes is recipe format 1 (work order W8).

A branch adds a schema, a join or a plot to a recipe file by inserting text, so the comments of the author stay.
The tests write a small valid recipe, apply the plan the way Blueprint does (the new files, then the recipe file),
and judge the result with the recipe checker and with the loader of the app.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/blueprint_arch/tests/test_branch_plan.py -q
"""
from pathlib import Path

import pytest
import yaml

from utils.config_loader import ConfigManager
from utils.recipe_factory import (Include, minimal_join, minimal_plot, minimal_recipe, minimal_schema, recipe_text,
                                  write_fragment)
from utils.recipe_loader import check_recipe_file, load_recipe

from blueprint_arch.data_analysis_recipe_navigator import generate_branch_plan

COMMENT_TOP = "# Why this recipe exists: a note of the author that a branch must keep."
COMMENT_INLINE = "# the reads file of the sequencing run"


def write_master(folder: Path, recipe: dict) -> Path:
    """The recipe as text with comments of the author: one at the top, and one after each key a branch looks for."""
    text = recipe_text(recipe)
    text = text.replace("data_schemas:\n", f"data_schemas:  {COMMENT_INLINE}\n", 1)
    text = text.replace("  main:\n", "  main:  # the only tab\n", 1)
    text = text.replace("    plots:\n", "    plots:  # the sub-tabs, in this order\n", 1)
    path = folder / f"{recipe['id']}.yaml"
    path.write_text(f"{COMMENT_TOP}\n{text}", encoding="utf-8")
    return path


def recipe_with_a_join() -> dict:
    schemas = {
        "samples": minimal_schema("data/samples.tsv", {"sample_id": "String", "year": "Int64"}, entity_key="sample_id",
                                  label="Samples", null_values=["", "NA"], strip=True),
        "reads": minimal_schema("data/reads.tsv", {"sample_id": "String", "reads": "Int64"}, label="Reads"),
    }
    plots = {"per_year": minimal_plot("C", {"x": "year"}, label="Samples per year")}
    return minimal_recipe("tiny", schemas=schemas, joins={"C": minimal_join(["samples", "reads"], [], label="Combined")}, plots=plots)


def apply_plan(master: Path, plan: dict) -> None:
    """What Blueprint does with a plan: refuse to replace a file, write the new files, then the recipe file."""
    assert plan["ok"], plan["error"]
    for fragment in plan["fragments"]:
        target = Path(fragment["abs_path"])
        assert not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(fragment["content"], encoding="utf-8")
    master.write_text(plan["new_master_text"], encoding="utf-8")


def lines_in_order(needles, haystack) -> bool:
    position = 0
    for needle in needles:
        position = haystack.find(needle, position)
        if position < 0:
            return False
        position += len(needle)
    return True


@pytest.fixture
def master(tmp_path):
    return write_master(tmp_path, recipe_with_a_join())


def test_the_starting_recipe_is_valid(master):
    assert check_recipe_file(master).errors == []


# -- a schema

@pytest.mark.parametrize("role", ["wrangling", "input_fields", "output_fields"])
def test_a_schema_branch_gives_a_valid_recipe_that_loads(master, role):
    """The node role `output_fields` still selects a schema; the KEY `output_fields` is not written any more."""
    plan = generate_branch_plan(str(master), "samples", role, "samples_b")
    apply_plan(master, plan)
    assert check_recipe_file(master).errors == []
    loaded = ConfigManager(str(master)).raw_config
    assert set(loaded["data_schemas"]) == {"samples", "reads", "samples_b"}
    assert loaded["data_schemas"]["samples_b"]["wrangling"] == {"tier1": [], "tier2": []}


def test_a_schema_branch_writes_no_output_fields_key_and_no_file_for_it(master):
    plan = generate_branch_plan(str(master), "samples", "wrangling", "samples_b")
    assert "output_fields" not in plan["new_master_text"]
    assert [f["rel_include"] for f in plan["fragments"]] == ["tiny/wrangling/samples_b_wrangling.yaml"]
    assert "output_fields" not in plan["summary"]


def test_a_schema_branch_reads_the_same_file_in_the_same_way(master):
    """The branch shares what is upstream: the file, the fields, and how missing values are read."""
    apply_plan(master, generate_branch_plan(str(master), "samples", "wrangling", "samples_b"))
    raw, problems = load_recipe(master)
    assert problems == []
    source, branch = raw["data_schemas"]["samples"], raw["data_schemas"]["samples_b"]
    for key in ("source", "null_values", "strip", "input_fields"):
        assert branch[key] == source[key]
    assert branch["null_values"] == ["", "NA"] and branch["strip"] is True
    assert branch["label"] == "Samples (branch)"
    assert list(branch) == ["label", "source", "null_values", "strip", "input_fields", "wrangling"]


def test_a_schema_branch_reuses_an_included_fields_file(tmp_path):
    recipe = recipe_with_a_join()
    write_fragment(tmp_path / "tiny" / "samples_fields.yaml", recipe["data_schemas"]["samples"]["input_fields"])
    recipe["data_schemas"]["samples"]["input_fields"] = Include("tiny/samples_fields.yaml")
    master = write_master(tmp_path, recipe)
    plan = generate_branch_plan(str(master), "samples", "input_fields", "samples_b")
    assert plan["new_master_text"].count("input_fields: !include 'tiny/samples_fields.yaml'") == 2
    apply_plan(master, plan)
    assert check_recipe_file(master).errors == []


def test_a_key_the_source_schema_does_not_have_is_not_invented(tmp_path):
    """A recipe that does not say how missing values are read is not format 1; the branch does not choose for the author."""
    recipe = recipe_with_a_join()
    del recipe["data_schemas"]["samples"]["null_values"]
    del recipe["data_schemas"]["samples"]["strip"]
    master = write_master(tmp_path, recipe)
    apply_plan(master, generate_branch_plan(str(master), "samples", "wrangling", "samples_b"))
    raw, _ = load_recipe(master)
    assert "null_values" not in raw["data_schemas"]["samples_b"] and "strip" not in raw["data_schemas"]["samples_b"]


def test_every_line_of_the_author_is_kept_in_its_order(master):
    before = master.read_text(encoding="utf-8")
    plan = generate_branch_plan(str(master), "samples", "wrangling", "samples_b")
    after = plan["new_master_text"]
    assert COMMENT_TOP in after and COMMENT_INLINE in after
    assert lines_in_order(before.split("\n"), after)
    assert len(after.split("\n")) > len(before.split("\n"))


# -- a join

def test_a_join_branch_gives_a_valid_recipe_that_loads(master):
    plan = generate_branch_plan(str(master), "C", "join", "C_b")
    assert "output_fields" not in plan["new_master_text"] and "output_fields" not in plan["summary"]
    assert [f["rel_include"] for f in plan["fragments"]] == ["tiny/assembly/C_b_assembly.yaml"]
    apply_plan(master, plan)
    assert check_recipe_file(master).errors == []
    branch = ConfigManager(str(master)).raw_config["joins"]["C_b"]
    assert branch["label"] == "Combined (branch)"
    assert branch["ingredients"] == [{"dataset_id": "samples"}, {"dataset_id": "reads"}]
    assert branch["steps"] == {"tier1": [], "tier2": []}
    assert list(branch) == ["label", "ingredients", "steps"]


def test_the_steps_file_of_a_join_branch_is_tiered_not_a_flat_list(master):
    """`steps` is `{tier1: [...]}`; a flat list is refused by the format and by the engine."""
    plan = generate_branch_plan(str(master), "C", "join", "C_b")
    (fragment,) = plan["fragments"]
    assert yaml.safe_load(fragment["content"]) == {"tier1": [], "tier2": []}


def test_a_join_branch_keeps_the_comments(master):
    before = master.read_text(encoding="utf-8")
    after = generate_branch_plan(str(master), "C", "join", "C_b")["new_master_text"]
    assert lines_in_order(before.split("\n"), after)


# -- a plot

def test_a_plot_branch_of_an_inline_spec_writes_the_spec_itself_without_a_wrapper(master):
    plan = generate_branch_plan(str(master), "per_year", "plot_spec", "per_year_b")
    (fragment,) = plan["fragments"]
    assert yaml.safe_load(fragment["content"]) == recipe_with_a_join()["analysis_groups"]["main"]["plots"]["per_year"]["spec"]
    apply_plan(master, plan)
    result = check_recipe_file(master)
    assert result.errors == []
    plots = ConfigManager(str(master)).raw_config["analysis_groups"]["main"]["plots"]
    assert plots["per_year_b"]["label"] == "Samples per year (branch)"
    assert plots["per_year_b"]["spec"] == plots["per_year"]["spec"]


def test_a_plot_branch_of_an_included_spec_copies_the_file_with_its_comments(tmp_path):
    recipe = recipe_with_a_join()
    spec_text = "# drawn as bars because the years are few\n" + recipe_text(recipe["analysis_groups"]["main"]["plots"]["per_year"]["spec"])
    (tmp_path / "tiny" / "plots").mkdir(parents=True)
    (tmp_path / "tiny" / "plots" / "per_year.yaml").write_text(spec_text, encoding="utf-8")
    recipe["analysis_groups"]["main"]["plots"]["per_year"]["spec"] = Include("tiny/plots/per_year.yaml")
    master = write_master(tmp_path, recipe)
    plan = generate_branch_plan(str(master), "per_year", "plot_spec", "per_year_b")
    (fragment,) = plan["fragments"]
    assert fragment["content"] == spec_text
    apply_plan(master, plan)
    assert check_recipe_file(master).errors == []


def test_a_label_with_a_quote_and_a_colon_stays_valid_text(tmp_path):
    recipe = recipe_with_a_join()
    recipe["analysis_groups"]["main"]["plots"]["per_year"]["label"] = 'Samples: the "good" ones'
    recipe["data_schemas"]["samples"]["label"] = 'Samples: the "good" ones'
    master = write_master(tmp_path, recipe)
    apply_plan(master, generate_branch_plan(str(master), "per_year", "plot_spec", "per_year_b"))
    apply_plan(master, generate_branch_plan(str(master), "samples", "wrangling", "samples_b"))
    raw, problems = load_recipe(master)
    assert problems == []
    assert raw["analysis_groups"]["main"]["plots"]["per_year_b"]["label"] == 'Samples: the "good" ones (branch)'
    assert raw["data_schemas"]["samples_b"]["label"] == 'Samples: the "good" ones (branch)'


# -- what is refused

@pytest.mark.parametrize("schema_id, role, new_id, word", [
    ("samples", "wrangling", "reads", "already exists"),
    ("C", "join", "C", "already exists"),
    ("per_year", "plot_spec", "per_year", "already exists"),
    ("nothing", "wrangling", "x", "not found"),
    ("samples", "wrangling", "not an id", "snake_case"),
    ("samples", "wrangling", "", "snake_case"),
    ("samples", "something_else", "x", "not branchable"),
])
def test_a_refused_branch_writes_nothing(master, schema_id, role, new_id, word):
    plan = generate_branch_plan(str(master), schema_id, role, new_id)
    assert plan["ok"] is False and word in plan["error"]
    assert plan["new_master_text"] == "" and plan["fragments"] == []


def test_a_missing_recipe_file_is_refused(tmp_path):
    plan = generate_branch_plan(str(tmp_path / "none.yaml"), "samples", "wrangling", "x")
    assert plan["ok"] is False and plan["fragments"] == []
