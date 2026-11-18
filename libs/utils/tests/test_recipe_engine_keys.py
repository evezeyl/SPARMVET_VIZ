"""The recipe shape of the engine-keys change (D-0250, D-0237, D-0252, D-0253, D-0242, D-0220, D-0251).

New shape: a tier is written as its own key (`tier1`, `tier2` in a table and in a join, `tier3` in a plot entry), holding a mapping
with an optional `data_engine` and `steps`; a plot entry has no `spec:` (its content is written in the entry, or the whole entry is in
an included file); `ui_label` and `ui_title` name a group or a plot; the four dead `plot_defaults` keys are refused. Every old
shape is refused with the key, where to write it now, and the rewrite tool by name.

Each rule has an accepted case and a refused case. The refused ones were made to fail once by breaking the rule (see the report).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_engine_keys.py -q
"""
import copy
import textwrap

import pytest

from utils.recipe_check import check_recipe, spec
from utils.recipe_loader import check_recipe_file, load_recipe

TOOL = "assets/scripts/migrate_recipe_engine_keys.py"
ACTIONS = {
    "polars_filter_demo": {"context": ["t1", "t2"], "params": {
        "columns": {"widget": "column_selector", "multi": True, "required": True},
        "na": {"widget": "enum", "options": ["keep", "remove"], "required": True}}},
    "polars_join": {"context": ["assembly"], "params": {
        "right_ingredient": {"widget": "string", "required": True},
        "how": {"widget": "enum", "options": ["left", "inner"], "required": True},
        "on": {"widget": "string", "required": False}}},
}
CATALOGS = {"actions": ACTIONS, "components": {"geom_col", "geom_point", "theme_bw"},
            "component_arguments": {"geom_col": {"fill"}, "geom_point": None, "theme_bw": None},
            "themes": {"theme_bw"}}
FILTER = {"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}


def valid():
    """A small recipe in the new shape."""
    return {
        "id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine",
        "info": {"label": "R", "description": "What it answers", "contact": "me"},
        "data_schemas": {
            "A": {"label": "A", "description": "One row per sample.",
                  "source": {"type": "local_tsv", "path": "assets/test_data/a.tsv"}, "null_values": [], "strip": True,
                  "input_fields": {"id": {"type": "String", "is_entity_key": True, "label": "Id"}, "v": {"type": "Float64"}},
                  "tier1": {"steps": []}},
            "B": {"label": "B", "description": "One row per sample.",
                  "source": {"type": "local_tsv", "path": "assets/test_data/b.tsv"}, "null_values": [], "strip": False,
                  "input_fields": {"id": {"type": "String", "is_entity_key": True}, "w": {"type": "Int64"}},
                  "tier1": {"steps": []}},
        },
        "joins": {"AB": {"label": "AB", "description": "One row per sample, A with B.",
                         "ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}],
                         "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}]}}},
        "analysis_groups": {"g": {"ui_label": "G", "description": "Question.", "plots": {
            "p": {"ui_label": "P", "description": "Drawn.", "target_dataset": "AB", "mapping": {"x": "id", "y": "v"},
                  "layers": [{"name": "geom_col"}]}}}},
    }


def mutated(change):
    raw = copy.deepcopy(valid())
    change(raw)
    return raw


def check(raw, profile="run", **kw):
    kw.setdefault("catalogs", CATALOGS)
    kw.setdefault("file_stem", "r")
    return check_recipe(raw, profile, **kw)


def found(raw, code, **kw):
    return [p for p in check(raw, **kw).problems if p.code == code]


def test_the_new_shape_is_accepted_without_any_problem():
    assert check(valid()).problems == []


def test_every_tier_form_is_accepted_with_and_without_data_engine():
    plot = lambda r: r["analysis_groups"]["g"]["plots"]["p"]
    on_join = mutated(lambda r: (r["data_schemas"]["A"].update(tier1={"data_engine": "python-polars", "steps": [FILTER]}),
                                 r["joins"]["AB"].update(tier2={"data_engine": "python-polars", "steps": []}),
                                 plot(r).update(tier3={"data_engine": "python-polars", "steps": []})))
    assert check(on_join).problems == []
    # tier2 of a table applies when a plot reads the table directly
    on_table = mutated(lambda r: (r["data_schemas"]["A"].update(tier2={"steps": [FILTER]}), plot(r).update(target_dataset="A")))
    assert check(on_table).problems == []


# -- the old shapes are refused, naming the key, where to write it now and the tool ---------------------------------------------

OLD_SHAPES = [
    ("wrangling in a table", lambda r: r["data_schemas"]["A"].update(wrangling={"tier1": {"steps": []}}), "S06", "data_schemas.A.wrangling", "wrangling"),
    ("steps container in a join", lambda r: r["joins"]["AB"].update(steps={"tier1": {"steps": []}}), "J07", "joins.AB.steps", "steps"),
    ("steps container in a plot", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(steps={"tier3": {"steps": []}}), "P04",
     "analysis_groups.g.plots.p.steps", "tier3"),
    ("spec in a plot", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(spec={"target_dataset": "AB"}), "P01",
     "analysis_groups.g.plots.p.spec", "directly in the plot entry"),
    ("a tier written as a list in a table", lambda r: r["data_schemas"]["A"].update(tier1=[]), "S06", "data_schemas.A.tier1", "steps"),
    ("a tier written as a list in a join", lambda r: r["joins"]["AB"].update(tier1=[FILTER]), "J07", "joins.AB.tier1", "steps"),
    ("tier3 written as a list in a plot", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(tier3=[]), "P04",
     "analysis_groups.g.plots.p.tier3", "steps"),
]


@pytest.mark.parametrize("name, change, code, path, words", OLD_SHAPES, ids=[o[0] for o in OLD_SHAPES])
def test_an_old_shape_is_refused_with_the_key_the_new_form_and_the_tool(name, change, code, path, words):
    problems = found(mutated(change), code)
    assert problems, f"{code} not found for {name}"
    problem = problems[0]
    assert problem.severity == "E" and problem.path == path
    text = problem.text("my_recipe.yaml")
    assert text.startswith(f"my_recipe.yaml : {path} :")  # the file and the key
    assert words in text and TOOL in text


def test_a_recipe_in_the_old_shape_is_refused_as_a_whole_with_the_tool_named_each_time():
    old = valid()
    old["data_schemas"]["A"]["wrangling"] = {"tier1": []}
    del old["data_schemas"]["A"]["tier1"]
    old["joins"]["AB"]["steps"] = {"tier1": []}
    del old["joins"]["AB"]["tier1"]
    plot = old["analysis_groups"]["g"]["plots"]["p"]
    old["analysis_groups"]["g"]["plots"]["p"] = {"ui_label": "P", "description": "d", "spec": {k: plot[k] for k in ("target_dataset", "mapping", "layers")}}
    result = check(old)
    assert not result.ok
    assert all(TOOL in p.text() for p in result.errors if p.code in ("S06", "J07", "P01", "P04"))
    assert {p.path for p in result.errors} >= {"data_schemas.A.wrangling", "joins.AB.steps", "analysis_groups.g.plots.p.spec"}


# -- the tier mapping ---------------------------------------------------------------------------------------------------------

TIER_CASES = [
    ("table, no steps", lambda r: r["data_schemas"]["A"].update(tier1={"data_engine": "python-polars"}), "S06", "steps"),
    ("table, steps not a list", lambda r: r["data_schemas"]["A"].update(tier1={"steps": "x"}), "S06", "list"),
    ("table, a key that is not a tier key", lambda r: r["data_schemas"]["A"].update(tier1={"steps": [], "label": "x"}), "S06", "label"),
    ("table, no tier1", lambda r: r["data_schemas"]["A"].pop("tier1"), "S06", "tier1"),
    ("join, no tier1", lambda r: r["joins"]["AB"].pop("tier1"), "J07", "tier1"),
    ("join, a tier inside a tier (an old fragment)", lambda r: r["joins"]["AB"].update(tier1={"tier1": {"steps": []}}), "J07", "tier1"),
    ("plot, tier3 without steps", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(tier3={}), "P04", "steps"),
]


@pytest.mark.parametrize("name, change, code, words", TIER_CASES, ids=[c[0] for c in TIER_CASES])
def test_a_wrong_tier_mapping_is_refused(name, change, code, words):
    problems = found(mutated(change), code)
    assert problems and problems[0].fix and words in problems[0].text()


def test_tier2_of_a_table_and_of_a_join_is_optional_but_a_step_in_it_is_judged():
    raw = mutated(lambda r: r["data_schemas"]["A"].update(tier2={"steps": [{"action": "polars_filter_demo", "columns": ["v"]}]}))
    assert "ST04" in check(raw).codes()  # the step "na" is required: judged in tier2 steps too, with the path of the new shape
    assert [p.path for p in found(raw, "ST04")] == ["data_schemas.A.tier2.steps[1].na"]


def test_the_path_of_a_step_follows_the_new_shape():
    raw = mutated(lambda r: r["joins"]["AB"]["tier1"]["steps"].append({"action": "polars_nope"}))
    assert [p.path for p in found(raw, "ST02")] == ["joins.AB.tier1.steps[2].action"]


def test_tier_one_only_actions_are_refused_in_tier2_and_tier3(monkeypatch):
    catalogs = dict(CATALOGS, tier1_only={"polars_filter_demo"})
    raw = mutated(lambda r: r["data_schemas"]["A"].update(tier2={"steps": [FILTER]}))
    assert [p.path for p in found(raw, "ST05", catalogs=catalogs)] == ["data_schemas.A.tier2.steps[1]"]


def test_an_empty_tier_and_empty_steps_are_refused_not_read_as_nothing():
    raw = mutated(lambda r: r["data_schemas"]["A"].update(tier1=None))
    assert [p.path for p in found(raw, "S06")] == ["data_schemas.A.tier1"]
    assert "empty value" in found(raw, "S06")[0].message and TOOL in found(raw, "S06")[0].text()
    raw = mutated(lambda r: r["joins"]["AB"]["tier1"].update(steps=None))
    assert [p.path for p in found(raw, "J07")] == ["joins.AB.tier1.steps"]


def test_the_steps_of_one_tier_and_of_another_stay_separate():
    """An error in tier1 does not hide one in tier2, and each is reported at its own path."""
    bad = {"action": "polars_filter_demo", "columns": ["v"]}
    raw = mutated(lambda r: (r["data_schemas"]["A"]["tier1"].update(steps=[bad]), r["data_schemas"]["A"].update(tier2={"steps": [bad]}),
                             r["analysis_groups"]["g"]["plots"]["p"].update(target_dataset="A")))
    assert [p.path for p in found(raw, "ST04")] == ["data_schemas.A.tier1.steps[1].na", "data_schemas.A.tier2.steps[1].na"]


# -- engines at every level ---------------------------------------------------------------------------------------------------

ENGINE_PLACES = [
    ("top data_engine", lambda r, v: r.update(data_engine=v), "data_engine"),
    ("top plot_engine", lambda r, v: r.update(plot_engine=v), "plot_engine"),
    ("tier1 of a table", lambda r, v: r["data_schemas"]["A"]["tier1"].update(data_engine=v), "data_schemas.A.tier1.data_engine"),
    ("tier2 of a table", lambda r, v: r["data_schemas"]["A"].update(tier2={"data_engine": v, "steps": []}), "data_schemas.A.tier2.data_engine"),
    ("tier1 of a join", lambda r, v: r["joins"]["AB"]["tier1"].update(data_engine=v), "joins.AB.tier1.data_engine"),
    ("tier2 of a join", lambda r, v: r["joins"]["AB"].update(tier2={"data_engine": v, "steps": []}), "joins.AB.tier2.data_engine"),
    ("tier3 of a plot", lambda r, v: r["analysis_groups"]["g"]["plots"]["p"].update(tier3={"data_engine": v, "steps": []}),
     "analysis_groups.g.plots.p.tier3.data_engine"),
    ("a plot", lambda r, v: r["analysis_groups"]["g"]["plots"]["p"].update(plot_engine=v), "analysis_groups.g.plots.p.plot_engine"),
]


@pytest.mark.parametrize("name, put, path", ENGINE_PLACES, ids=[e[0] for e in ENGINE_PLACES])
def test_an_unknown_engine_value_is_refused_at_each_level(name, put, path):
    wrong = "python-pandas" if "plot" not in name else "python-ggplot2"
    problems = found(mutated(lambda r: put(r, wrong)), "T06")
    assert [p.path for p in problems] == [path]
    assert "no library for this engine in this app" in problems[0].message and problems[0].fix.startswith("write one of ")


def test_the_engine_values_the_app_builds_are_accepted_at_each_level():
    right = {"data_engine": "python-polars", "plot_engine": "python-plotnine"}
    for name, put, path in ENGINE_PLACES:
        key = "plot_engine" if "plot" in name and "tier3" not in name else "data_engine"
        assert found(mutated(lambda r: put(r, right[key])), "T06") == [], name


def test_the_engine_written_in_one_tier_does_not_reach_the_next_tier():
    engines = {**ENGINE_OF, "action_engines": {**ENGINE_OF["action_engines"], "polars_filter_demo": "python-other"}}
    raw = mutated(lambda r: (r["data_schemas"]["A"]["tier1"].update(data_engine="python-other", steps=[FILTER]),
                             r["data_schemas"]["A"].update(tier2={"steps": [FILTER]}),
                             r["analysis_groups"]["g"]["plots"]["p"].update(target_dataset="A")))
    problems = found(raw, "EN02", catalogs={**CATALOGS, **engines})
    assert [p.path for p in problems] == ["data_schemas.A.tier2.steps[1]"]


def test_a_data_engine_is_not_a_plot_engine():
    assert found(mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(plot_engine="python-polars")), "T06")
    assert found(mutated(lambda r: r["data_schemas"]["A"]["tier1"].update(data_engine="python-plotnine")), "T06")


# -- the engine of a step or a component (the registry field, D-0238) -------------------------------------------------------------

ENGINE_OF = {"action_engines": {"polars_filter_demo": "python-polars", "polars_join": "python-polars"},
             "component_engines": {"geom_col": "python-plotnine", "geom_point": "python-plotnine", "theme_bw": "python-plotnine"}}


def test_without_engine_information_the_check_says_so_in_its_coverage():
    assert "engines" not in check(valid()).coverage
    assert "engines" not in check(valid(), catalogs={"actions": ACTIONS}).coverage
    assert {"structure", "actions", "components"} <= check(valid()).coverage


def test_with_engine_information_the_check_is_covered_and_a_step_of_the_right_engine_passes():
    result = check(valid(), catalogs={**CATALOGS, **ENGINE_OF})
    assert "engines" in result.coverage and result.problems == []


def test_a_step_that_belongs_to_another_engine_is_refused_with_the_names():
    engines = {**ENGINE_OF, "action_engines": {**ENGINE_OF["action_engines"], "polars_filter_demo": "python-other"}}
    raw = mutated(lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append(FILTER))
    problems = found(raw, "EN02", catalogs={**CATALOGS, **engines})
    assert [p.path for p in problems] == ["data_schemas.A.tier1.steps[1]"]
    assert "python-other" in problems[0].message and "python-polars" in problems[0].message and "polars_filter_demo" in problems[0].message


def test_the_engine_of_a_tier_is_its_own_value_else_the_recipes():
    engines = {**ENGINE_OF, "action_engines": {**ENGINE_OF["action_engines"], "polars_filter_demo": "python-other"}}
    catalogs = {**CATALOGS, **engines}
    # a tier that names the other engine accepts the step (only the engine value itself is judged by T06)
    raw = mutated(lambda r: r["data_schemas"]["A"]["tier1"].update(data_engine="python-other", steps=[FILTER]))
    assert found(raw, "EN02", catalogs=catalogs) == []
    # a tier that names no engine uses the recipe's
    raw = mutated(lambda r: r["data_schemas"]["A"]["tier1"].update(steps=[FILTER]))
    assert found(raw, "EN02", catalogs=catalogs)


def test_a_layer_of_another_plot_engine_is_refused_and_the_plot_engine_of_the_entry_decides():
    engines = {**ENGINE_OF, "component_engines": {**ENGINE_OF["component_engines"], "geom_col": "python-other"}}
    catalogs = {**CATALOGS, **engines}
    raw = mutated(lambda r: None)
    problems = found(raw, "EN02", catalogs=catalogs)
    assert [p.path for p in problems] == ["analysis_groups.g.plots.p.layers[1]"]
    raw = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(plot_engine="python-other"))
    assert found(raw, "EN02", catalogs=catalogs) == []


def test_tier3_steps_are_judged_against_the_data_engine():
    engines = {**ENGINE_OF, "action_engines": {**ENGINE_OF["action_engines"], "polars_filter_demo": "python-other"}}
    raw = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(tier3={"steps": [FILTER]}))
    assert [p.path for p in found(raw, "EN02", catalogs={**CATALOGS, **engines})] == ["analysis_groups.g.plots.p.tier3.steps[1]"]


def test_a_registered_name_without_an_engine_in_the_registry_is_a_fault_not_a_silent_pass():
    engines = {**ENGINE_OF, "action_engines": {"polars_join": "python-polars"}}  # polars_filter_demo has no engine
    raw = mutated(lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append(FILTER))
    problems = found(raw, "EN03", catalogs={**CATALOGS, **engines})
    assert problems and "polars_filter_demo" in problems[0].message and "fault of the app" in problems[0].message


# -- the plot entry: no spec, the names, the title -----------------------------------------------------------------------------------

def test_the_plot_content_is_judged_where_it_is_now_with_the_old_codes():
    p = lambda r: r["analysis_groups"]["g"]["plots"]["p"]
    assert found(mutated(lambda r: p(r).update(target_dataset="nope")), "PS02")
    assert found(mutated(lambda r: p(r).pop("layers")), "PS03")
    assert found(mutated(lambda r: p(r).update(layers=[{"name": "geom_nope"}])), "PS04")
    assert found(mutated(lambda r: p(r).update(theme="theme_nope")), "PS05")
    assert [x.path for x in found(mutated(lambda r: p(r).update(theme="theme_nope")), "PS05")] == ["analysis_groups.g.plots.p.theme"]
    assert found(mutated(lambda r: p(r).update(unknown_key=1)), "P01")


def test_a_title_in_the_plot_is_refused_with_where_to_write_the_two_names():
    raw = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(title="Old title"))
    problem = found(raw, "P01")[0]
    assert problem.path == "analysis_groups.g.plots.p.title"
    for words in ("labs", "ui_title", TOOL):
        assert words in problem.text()
    assert "Old title" not in raw["analysis_groups"]["g"]["plots"]["p"].get("ui_title", "")


def test_the_ui_names_are_accepted_and_label_is_refused_as_renamed_at_group_and_plot():
    ok = mutated(lambda r: (r["analysis_groups"]["g"].update(ui_title="Long group name"), r["analysis_groups"]["g"]["plots"]["p"].update(ui_title="Long plot name", plot_engine="python-plotnine")))
    assert check(ok).problems == []
    group = mutated(lambda r: r["analysis_groups"]["g"].update(label="G"))
    problem = found(group, "G01")[0]
    assert problem.path == "analysis_groups.g.label" and "ui_label" in problem.text() and "renamed" in problem.text()
    plot = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(label="P"))
    problem = found(plot, "P01")[0]
    assert problem.path == "analysis_groups.g.plots.p.label" and "ui_label" in problem.text() and "renamed" in problem.text()


def test_ui_label_is_required_at_group_and_plot():
    assert found(mutated(lambda r: r["analysis_groups"]["g"].pop("ui_label")), "G01")
    assert found(mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("ui_label")), "P01")


def test_a_group_or_plot_with_only_the_old_label_is_told_the_rename_once_not_also_that_ui_label_is_missing():
    raw = mutated(lambda r: (r["analysis_groups"]["g"].update(label=r["analysis_groups"]["g"].pop("ui_label")),
                             r["analysis_groups"]["g"]["plots"]["p"].update(label=r["analysis_groups"]["g"]["plots"]["p"].pop("ui_label"))))
    texts = [p.text() for p in check(raw).errors]
    assert len(texts) == 2 and all("renamed" in t for t in texts)


# -- the three places that keep `label` until Eve answers (M271), in one table ----------------------------------------------------

def test_the_three_pending_places_still_use_label_and_the_table_names_them():
    assert spec()["label_keys"] == {"info": "label", "schema": "label", "join": "label", "field": "label"}
    # accepted as written today
    assert check(valid()).problems == []
    # refused when missing, with the key the table names
    assert found(mutated(lambda r: r["info"].pop("label")), "I01")
    assert found(mutated(lambda r: r["data_schemas"]["A"].pop("label")), "S03")
    assert found(mutated(lambda r: r["joins"]["AB"].pop("label")), "J02")
    # ui_label is NOT yet a key of these places
    assert found(mutated(lambda r: r["data_schemas"]["A"].update(ui_label="A")), "S01")
    assert found(mutated(lambda r: r["joins"]["AB"].update(ui_label="A")), "J01")
    assert found(mutated(lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(ui_label="V")), "FD01")


def test_changing_the_table_changes_the_three_places_in_one_line(monkeypatch):
    """The answer of Eve is one line per place in recipe_spec.yaml (`label_keys`): the checker follows the table."""
    import utils.recipe_check as module
    changed = copy.deepcopy(spec())
    changed["label_keys"] = {"info": "ui_label", "schema": "ui_label", "join": "ui_label", "field": "ui_label"}
    monkeypatch.setattr(module, "spec", lambda: changed)
    raw = mutated(lambda r: (r["info"].update(ui_label=r["info"].pop("label")),
                             [t.update(ui_label=t.pop("label")) for t in (r["data_schemas"]["A"], r["data_schemas"]["B"], r["joins"]["AB"])],
                             r["data_schemas"]["A"]["input_fields"]["id"].update(ui_label=r["data_schemas"]["A"]["input_fields"]["id"].pop("label"))))
    assert check(raw).problems == []
    # and the old key is then the unknown one
    assert found(mutated(lambda r: None), "S01") and found(mutated(lambda r: None), "J01")


# -- plot_defaults: the four dead keys are tombstones, the live ones stay -----------------------------------------------------------

DEAD = {"default_font_family": "Liberation Sans", "facet_panel_spacing": 0.1, "legend_position": "right", "optimisation": {"auto_axis_text": True}}


@pytest.mark.parametrize("key", sorted(DEAD))
def test_a_dead_plot_defaults_key_is_refused_with_a_tombstone(key):
    problems = found(mutated(lambda r: r.update(plot_defaults={"theme": "theme_bw", key: DEAD[key]})), "PD02")
    assert [p.path for p in problems] == [f"plot_defaults.{key}"]
    text = problems[0].text("r.yaml")
    for words in ("REMOVED", "D-0242", "2026-11-17", TOOL, "Tombstone expires", "the key did nothing"):
        assert words in text, (key, words)
    assert found(mutated(lambda r: r.update(plot_defaults={key: DEAD[key]})), "PD01") == []  # not also "unknown key"


def test_the_live_plot_defaults_keys_are_still_accepted():
    raw = mutated(lambda r: r.update(plot_defaults={"palette": "p", "theme": "theme_bw", "random_state": 3, "layers": [{"name": "theme_bw"}]}))
    assert check(raw).problems == []


def test_plot_defaults_without_the_dead_keys_is_empty_of_tombstones_and_a_truly_unknown_key_is_still_pd01():
    assert found(mutated(lambda r: r.update(plot_defaults={"theme": "theme_bw"})), "PD02") == []
    assert found(mutated(lambda r: r.update(plot_defaults={"colour_wheel": 1})), "PD01")


# -- the gallery profile reads the entry without spec ------------------------------------------------------------------------------

TAXONOMY = {"family": "Distribution", "pattern": "1 Numeric", "difficulty": "Simple", "show": "frequency", "sample_size": "medium+"}


def gallery_raw():
    raw = valid()
    raw["analysis_groups"]["g"]["plots"]["p"]["taxonomy"] = dict(TAXONOMY)
    raw["data_schemas"] = {"A": {**raw["data_schemas"]["A"], "source": {"type": "local_tsv", "path": "./assets/gallery_data/r/example_data.tsv"}}}
    raw.pop("joins")
    raw["analysis_groups"]["g"]["plots"]["p"]["target_dataset"] = "A"
    return raw


def test_a_gallery_example_in_the_new_shape_passes_the_gallery_profile():
    result = check(gallery_raw(), "gallery", file_stem="r")
    assert [p.code for p in result.errors if p.code.startswith("GP")] == []


def test_gallery_checks_read_the_taxonomy_of_the_entry():
    raw = gallery_raw()
    del raw["analysis_groups"]["g"]["plots"]["p"]["taxonomy"]
    assert [p.code for p in check(raw, "gallery", file_stem="r").errors if p.code.startswith("GP")] == ["GP02"]
    raw = gallery_raw()
    raw["analysis_groups"]["g"]["plots"]["p"]["taxonomy"]["family"] = "Nope"
    assert [p.code for p in check(raw, "gallery", file_stem="r").errors if p.code.startswith("GP")] == ["GP03"]
    raw = gallery_raw()
    raw["analysis_groups"]["g2"] = copy.deepcopy(raw["analysis_groups"]["g"])
    assert "GP01" in check(raw, "gallery", file_stem="r").codes()


def test_a_gallery_example_in_the_old_shape_is_refused_by_the_same_checker():
    raw = gallery_raw()
    plot = raw["analysis_groups"]["g"]["plots"]["p"]
    raw["analysis_groups"]["g"]["plots"]["p"] = {"label": "P", "taxonomy": plot["taxonomy"],
                                                 "spec": {k: plot[k] for k in ("target_dataset", "mapping", "layers")}}
    codes = check(raw, "gallery", file_stem="r").codes()
    assert "P01" in codes


# -- the include forms, read from files (loader rule F01 and the checker) -----------------------------------------------------------

RECIPE = """
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
    input_fields: {id: {type: String, is_entity_key: true}, v: {type: Float64}}
%(tier)s
analysis_groups:
  g:
    ui_label: G
    description: d
    plots:
%(plot)s
"""
INLINE_TIER = "    tier1:\n      steps: []\n"
INLINE_PLOT = "      p:\n        ui_label: P\n        description: d\n        target_dataset: A\n        mapping: {x: id}\n        layers: [{name: geom_col}]\n"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text) if text.startswith("\n") else text)
    return path


def recipe_file(tmp_path, tier=INLINE_TIER, plot=INLINE_PLOT):
    return write(tmp_path / "r.yaml", RECIPE % {"tier": tier.rstrip("\n"), "plot": plot.rstrip("\n")})


def test_an_inline_tier_and_an_inline_plot_pass_the_whole_check(tmp_path):
    assert check_recipe_file(recipe_file(tmp_path), catalogs=CATALOGS).problems == []


def test_a_tier_in_an_included_file_passes_and_the_file_root_is_the_tiers_own_content(tmp_path):
    write(tmp_path / "r" / "A_tier1.yaml", "data_engine: python-polars\nsteps:\n  - {action: polars_filter_demo, columns: [v], na: keep}\n")
    path = recipe_file(tmp_path, tier="    tier1: !include r/A_tier1.yaml\n")
    assert check_recipe_file(path, catalogs=CATALOGS).problems == []
    raw, _ = load_recipe(path)
    assert raw["data_schemas"]["A"]["tier1"]["steps"][0]["action"] == "polars_filter_demo"


def test_a_whole_plot_entry_in_its_own_file_passes_and_the_include_sits_at_the_entry(tmp_path):
    write(tmp_path / "r" / "plots" / "p.yaml", "ui_label: P\ndescription: d\ntarget_dataset: A\nmapping: {x: id}\nlayers: [{name: geom_col}]\n")
    path = recipe_file(tmp_path, plot="      p: !include r/plots/p.yaml\n")
    assert check_recipe_file(path, catalogs=CATALOGS).problems == []


def test_an_included_tier_whose_file_repeats_the_tier_key_is_a_wrapper_f01(tmp_path):
    write(tmp_path / "r" / "A_tier1.yaml", "tier1:\n  steps: []\n")
    path = recipe_file(tmp_path, tier="    tier1: !include r/A_tier1.yaml\n")
    assert [p.code for p in load_recipe(path)[1]] == ["F01"]
    assert "tier1" in load_recipe(path)[1][0].path and "remove" in load_recipe(path)[1][0].fix


def test_an_included_plot_entry_whose_file_repeats_the_plot_id_is_a_wrapper_f01(tmp_path):
    write(tmp_path / "r" / "plots" / "p.yaml", "p:\n  ui_label: P\n  target_dataset: A\n  mapping: {x: id}\n  layers: [{name: geom_col}]\n")
    path = recipe_file(tmp_path, plot="      p: !include r/plots/p.yaml\n")
    assert [p.code for p in load_recipe(path)[1]] == ["F01"]


def test_an_old_fragment_that_holds_both_tiers_included_under_one_tier_is_refused_by_the_check(tmp_path):
    write(tmp_path / "r" / "A_wrangling.yaml", "tier1:\n  steps: []\ntier2:\n  steps: []\n")
    path = recipe_file(tmp_path, tier="    tier1: !include r/A_wrangling.yaml\n")
    result = check_recipe_file(path, catalogs=CATALOGS)
    assert [p.path for p in result.errors] == ["data_schemas.A.tier1.tier1", "data_schemas.A.tier1.tier2", "data_schemas.A.tier1"]
    assert TOOL in result.errors[0].text() and "its own table, join or plot entry" in result.errors[0].message


def test_an_old_fragment_included_at_wrangling_and_a_spec_include_are_refused_with_the_tool(tmp_path):
    write(tmp_path / "r" / "A_wrangling.yaml", "tier1: []\n")
    write(tmp_path / "r" / "plots" / "p.yaml", "target_dataset: A\nmapping: {x: id}\nlayers: [{name: geom_col}]\n")
    text = RECIPE % {"tier": "    wrangling: !include r/A_wrangling.yaml", "plot": "      p:\n        ui_label: P\n        spec: !include r/plots/p.yaml"}
    result = check_recipe_file(write(tmp_path / "r.yaml", text), catalogs=CATALOGS)
    texts = [p.text("r.yaml") for p in result.errors]
    assert any("data_schemas.A.wrangling" in t and TOOL in t for t in texts)
    assert any("analysis_groups.g.plots.p.spec" in t and TOOL in t for t in texts)
