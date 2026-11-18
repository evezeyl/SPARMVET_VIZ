"""The Blueprint navigator reads recipe format 1 as it is written now (D-0250, D-0252, D-0253): a tier is its own key
(`tier1`, `tier2`, each a mapping with `steps`), a plot entry is its own content (inline, or the whole entry in an included
file), there is no `wrangling`, `steps`, `spec`, `output_fields` or `pre_plot_wrangling` key.

The tests write a small recipe with the factory (`utils.recipe_factory`), with tier files, a fields file and a plot in its own file,
and read it with the functions the Blueprint handlers call.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/blueprint_arch/tests/test_navigator_new_shape.py -q
"""
import json
from pathlib import Path

import pytest

from utils.recipe_factory import Include, minimal_join, minimal_plot, minimal_recipe, minimal_schema, write_fragment, write_recipe
from utils.recipe_loader import check_recipe_file

from blueprint_arch.blueprint_mapper import BlueprintMapper
from blueprint_arch.data_analysis_recipe_navigator import (
    build_lineage_chain, build_plot_lineage, build_schema_registry, build_sibling_map, resolve_fields_for_schema)

STEP = {"action": "polars_select", "exprs": ["sample_id"]}


@pytest.fixture
def recipe_path(tmp_path):
    """samples: fields file, tier1 file, tier2 file (plotted directly by `direct`); reads: all inline; join C: tier1 file;
    `per_year` is written inline, `per_country` is a whole entry in its own file."""
    samples = minimal_schema("data/samples.tsv", {"sample_id": "String", "year": "Int64", "country": "String"},
                             entity_key="sample_id", label="Samples")
    reads = minimal_schema("data/reads.tsv", {"sample_id": "String", "reads": "Int64"}, label="Reads")
    samples["input_fields"] = Include("tiny/fields/samples.yaml")
    samples["tier1"] = Include("tiny/wrangling/samples_t1.yaml")
    samples["tier2"] = Include("tiny/wrangling/samples_t2.yaml")
    join = minimal_join(["samples", "reads"], [], label="Combined")
    join["tier1"] = Include("tiny/join/C_t1.yaml")
    plots = {
        "per_year": minimal_plot("C", {"x": "year"}, label="Per year"),
        "per_country": Include("tiny/plots/per_country.yaml"),
        "direct": minimal_plot("samples", {"x": "country"}, label="Direct"),
    }
    recipe = minimal_recipe("tiny", schemas={"samples": samples, "reads": reads}, joins={"C": join}, plots=plots)
    base = tmp_path / "tiny"
    write_fragment(base / "fields" / "samples.yaml", minimal_schema(
        "x", {"sample_id": "String", "year": "Int64", "country": "String"}, entity_key="sample_id")["input_fields"])
    write_fragment(base / "wrangling" / "samples_t1.yaml", {"steps": [dict(STEP)]})
    write_fragment(base / "wrangling" / "samples_t2.yaml", {"data_engine": "python-polars", "steps": [dict(STEP)]})
    write_fragment(base / "join" / "C_t1.yaml", {"steps": [dict(STEP)]})
    write_fragment(base / "plots" / "per_country.yaml", minimal_plot("C", {"x": "country"}, label="Per country"))
    return write_recipe(tmp_path / "tiny.yaml", recipe)


def test_the_recipe_of_the_tests_is_valid(recipe_path):
    assert check_recipe_file(recipe_path, "build").errors == []


# -- build_sibling_map

def test_a_tier_file_is_registered_with_its_tier(recipe_path):
    ctx = build_sibling_map(str(recipe_path))
    assert ctx["tiny/wrangling/samples_t1.yaml"]["role"] == "wrangling" and ctx["tiny/wrangling/samples_t1.yaml"]["tier"] == "tier1"
    assert ctx["tiny/wrangling/samples_t2.yaml"]["role"] == "wrangling" and ctx["tiny/wrangling/samples_t2.yaml"]["tier"] == "tier2"
    assert ctx["tiny/join/C_t1.yaml"]["role"] == "join" and ctx["tiny/join/C_t1.yaml"]["tier"] == "tier1"
    assert ctx["tiny/fields/samples.yaml"]["role"] == "input_fields"


def test_the_siblings_of_a_table_name_its_tiers_not_old_keys(recipe_path):
    entry = build_sibling_map(str(recipe_path))["tiny/wrangling/samples_t1.yaml"]
    assert entry["siblings"] == {"input_fields": "tiny/fields/samples.yaml", "tier1": "tiny/wrangling/samples_t1.yaml",
                                 "tier2": "tiny/wrangling/samples_t2.yaml"}


def test_a_table_written_inline_is_registered_by_its_id_with_the_inline_tier(recipe_path):
    entry = build_sibling_map(str(recipe_path))["reads"]
    assert entry["role"] == "wrangling" and entry["schema_type"] == "data_schemas"
    assert entry["siblings"]["tier1"] == {"inline": {"steps": []}}
    assert entry["siblings"]["tier2"] is None


def test_a_join_lists_its_ingredients(recipe_path):
    assert build_sibling_map(str(recipe_path))["tiny/join/C_t1.yaml"]["ingredients"] == ["samples", "reads"]


def test_a_plot_written_inline_is_navigable_by_its_id_and_a_plot_in_its_own_file_by_the_file(recipe_path):
    ctx = build_sibling_map(str(recipe_path))
    assert ctx["per_year"]["role"] == "plot_spec" and ctx["per_year"]["group_id"] == "main"
    assert ctx["tiny/plots/per_country.yaml"]["role"] == "plot_spec"
    assert ctx["tiny/plots/per_country.yaml"]["schema_id"] == "per_country"
    assert ctx["per_country"]["schema_id"] == "per_country"


def test_no_entry_has_an_output_fields_slot_or_a_plot_wrangling_role(recipe_path):
    ctx = build_sibling_map(str(recipe_path))
    for entry in ctx.values():
        assert "output_fields" not in entry["siblings"] and "wrangling" not in entry["siblings"]
        assert entry["role"] != "plot_wrangling"


def test_a_file_that_is_not_a_recipe_gives_an_empty_map(tmp_path):
    (tmp_path / "bad.yaml").write_text("- a\n- b\n", encoding="utf-8")
    assert build_sibling_map(str(tmp_path / "bad.yaml")) == {}
    assert build_sibling_map(str(tmp_path / "missing.yaml")) == {}


# -- build_schema_registry

def includes_of(recipe_path):
    return {rel: str(recipe_path.parent / rel) for rel in
            ("tiny/fields/samples.yaml", "tiny/wrangling/samples_t1.yaml", "tiny/plots/per_country.yaml")}


def test_the_registry_has_the_tiers_and_the_target_of_each_plot(recipe_path):
    reg = build_schema_registry(str(recipe_path), includes_of(recipe_path))
    assert reg["samples"]["tier1"] == "tiny/wrangling/samples_t1.yaml" and reg["samples"]["tier2"] == "tiny/wrangling/samples_t2.yaml"
    assert reg["reads"]["tier1"] == {"inline": {"steps": []}} and reg["reads"]["tier2"] is None
    assert reg["per_year"]["target_dataset"] == "C"
    assert reg["per_country"]["target_dataset"] == "C"          # read from the entry file
    assert reg["direct"]["target_dataset"] == "samples"
    assert reg["per_year"]["group_id"] == "main" and reg["per_year"]["schema_type"] == "plots"
    for entry in reg.values():
        assert not {"wrangling", "output_fields", "steps", "info"} & set(entry)


def test_a_plot_in_a_file_that_is_missing_has_no_target_and_no_error(recipe_path):
    (recipe_path.parent / "tiny" / "plots" / "per_country.yaml").unlink()
    reg = build_schema_registry(str(recipe_path), {})
    assert reg["per_country"]["target_dataset"] is None


# -- build_lineage_chain

def test_the_chain_of_a_tier_file_shows_the_fields_both_tiers_and_the_join(recipe_path):
    ctx = build_sibling_map(str(recipe_path))
    chain = build_lineage_chain("tiny/wrangling/samples_t1.yaml", ctx)
    # the join comes last, by its id (as before the tiers had files of their own)
    assert [n["rel"] for n in chain] == ["tiny/fields/samples.yaml", "tiny/wrangling/samples_t1.yaml",
                                         "tiny/wrangling/samples_t2.yaml", "C"]
    assert [n["is_active"] for n in chain] == [False, True, False, False]
    again = build_lineage_chain("tiny/wrangling/samples_t2.yaml", ctx)
    assert [n["is_active"] for n in again] == [False, False, True, False]
    # the two files of one table have one id: the rail says which is the tier 2
    assert [n["label"] for n in chain] == ["samples", "samples", "samples (tier 2)", "C"]


def test_the_chain_of_a_join_starts_with_the_tier_one_of_its_ingredients(recipe_path):
    chain = build_lineage_chain("tiny/join/C_t1.yaml", build_sibling_map(str(recipe_path)))
    # a table written with a file is listed by its file and by its id (as before); its tier 2 file is not listed
    assert [n["rel"] for n in chain] == ["tiny/wrangling/samples_t1.yaml", "samples", "reads", "tiny/join/C_t1.yaml"]
    assert chain[-1]["is_active"] is True
    assert "tiny/wrangling/samples_t2.yaml" not in [n["rel"] for n in chain]


def test_the_chain_of_a_plot_goes_back_to_its_table_when_the_target_is_given(recipe_path):
    ctx = build_sibling_map(str(recipe_path))
    chain = build_lineage_chain("tiny/plots/per_country.yaml", ctx, target_ds_override="C")
    assert chain[-1]["rel"] == "tiny/plots/per_country.yaml" and chain[-1]["is_active"] is True
    assert "tiny/join/C_t1.yaml" in [n["rel"] for n in chain]
    assert [n["rel"] for n in build_lineage_chain("tiny/plots/per_country.yaml", ctx)] == ["tiny/plots/per_country.yaml"]


def test_an_unknown_node_gives_an_empty_chain(recipe_path):
    assert build_lineage_chain("nothing", build_sibling_map(str(recipe_path))) == []


# -- resolve_fields_for_schema

def test_the_fields_of_a_table_come_from_its_fields_file_or_its_inline_fields(recipe_path):
    ctx = build_sibling_map(str(recipe_path))
    inc = includes_of(recipe_path)
    assert set(resolve_fields_for_schema("samples", ctx, inc)) == {"sample_id", "year", "country"}
    assert set(resolve_fields_for_schema("reads", ctx, inc)) == {"sample_id", "reads"}


def test_the_fields_of_a_join_are_the_fields_of_its_ingredients(recipe_path):
    ctx = build_sibling_map(str(recipe_path))
    assert set(resolve_fields_for_schema("C", ctx, includes_of(recipe_path))) == {"sample_id", "year", "country", "reads"}


def test_a_cycle_does_not_loop():
    ctx = {"a": {"schema_id": "a", "role": "join", "ingredients": ["b"], "siblings": {}},
           "b": {"schema_id": "b", "role": "join", "ingredients": ["a"], "siblings": {}}}
    assert resolve_fields_for_schema("a", ctx, {}) == {}


# -- the lineage of the export reads the same map

def test_the_lineage_of_a_plot_in_its_own_file_names_the_tier_one_files(recipe_path):
    steps = build_plot_lineage("per_country", str(recipe_path))
    assert [s["type"] for s in steps] == ["data_source", "wrangling", "data_source", "wrangling", "join", "plot_spec"]
    by_type = {(s["type"], s["schema_id"]): s["rel"] for s in steps}
    assert by_type[("wrangling", "samples")] == "tiny/wrangling/samples_t1.yaml"
    assert by_type[("join", "C")] == "tiny/join/C_t1.yaml"
    assert steps[-1]["label"] == "Per country"


def test_the_lineage_of_a_table_plotted_directly_says_it_has_a_tier_two(recipe_path):
    steps = build_plot_lineage("direct", str(recipe_path))
    assert [s["label"] for s in steps if s["type"] == "wrangling"] == ["samples / wrangling (tier 1; tier 2 only where samples is plotted directly)"]


# -- the map of the tubes

def elements(recipe_path):
    from utils.config_loader import ConfigManager
    return json.loads(BlueprintMapper(ConfigManager(str(recipe_path)).raw_config).generate_cy_elements())


def test_every_table_with_a_tier_written_has_a_wrangling_node_and_every_plot_a_node_fed_by_its_target(recipe_path):
    elems = elements(recipe_path)
    ids = {e["data"]["id"] for e in elems if "source" not in e["data"]}
    assert {"samples__wrn", "reads__wrn", "C__wrn"} <= ids
    assert {"per_year", "per_country", "direct"} <= ids
    edges = {(e["data"]["source"], e["data"]["target"]) for e in elems if "source" in e["data"]}
    assert ("C__wrn", "per_year") in edges and ("C__wrn", "per_country") in edges and ("samples__wrn", "direct") in edges


def test_a_table_without_any_tier_has_no_wrangling_node(tmp_path):
    recipe = minimal_recipe("tiny")
    del recipe["data_schemas"]["table"]["tier1"]
    elems = json.loads(BlueprintMapper(recipe).generate_cy_elements())
    assert "table__wrn" not in {e["data"]["id"] for e in elems if "source" not in e["data"]}


def test_a_plot_without_a_target_gets_the_warning_node():
    recipe = minimal_recipe("tiny", plots={"p": {"ui_label": "P", "mapping": {"x": "sample_id"}, "layers": []}})
    elems = json.loads(BlueprintMapper(recipe).generate_cy_elements())
    assert "INFO_p" in {e["data"]["id"] for e in elems if "source" not in e["data"]}


def test_the_lineage_names_the_tier_one_of_a_table_never_its_tier_two_file(tmp_path):
    """Tier 1 written in the recipe and tier 2 in a file: the file is the tier 2, so the lineage node of the table is its id."""
    table = minimal_schema("data/t.tsv", {"sample_id": "String", "year": "Int64"}, entity_key="sample_id", label="T")
    table["tier2"] = Include("tiny/t_t2.yaml")
    write_fragment(tmp_path / "tiny" / "t_t2.yaml", {"steps": [dict(STEP)]})
    recipe = minimal_recipe("tiny", schemas={"t": table}, plots={"p": minimal_plot("t", {"x": "year"}, label="P")})
    master = write_recipe(tmp_path / "tiny.yaml", recipe)
    steps = build_plot_lineage("p", str(master))
    assert [(s["type"], s["rel"]) for s in steps if s["type"] == "wrangling"] == [("wrangling", "t")]
    assert [s["label"] for s in steps if s["type"] == "wrangling"] == ["t / wrangling (tier 1; tier 2 only where t is plotted directly)"]
