"""The recipe shape of the engine-keys change (D-0250, D-0237, D-0252, D-0253, D-0242, D-0220, D-0251).

New shape: a tier is written as its own key (`tier1`, `tier2` in a table and in a join, `tier3` in a plot entry), holding a mapping
with an optional `data_engine` and `steps`; a plot entry has no `spec:` (its content is written in the entry, or the whole entry is in
an included file); `ui_label` names a group or a plot; the four dead `plot_defaults` keys are refused. Every old
shape is refused with the key, where to write it now, and the rewrite tool by name.

Each rule has an accepted case and a refused case. The refused ones were made to fail once by breaking the rule (see the report).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_engine_keys.py -q
"""
import copy
import textwrap

import pytest

from utils.recipe_check import check_recipe, plot_keys, spec
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
        "info": {"ui_label": "R", "description": "What it answers", "contact": "me"},
        "data_schemas": {
            "A": {"ui_label": "A", "description": "One row per sample.",
                  "source": {"type": "local_tsv", "path": "assets/test_data/a.tsv"}, "null_values": [], "strip": True,
                  "input_fields": {"id": {"type": "String", "is_entity_id": True, "ui_label": "Id"}, "v": {"type": "Float64"}},
                  "tier1": {"steps": []}},
            "B": {"ui_label": "B", "description": "One row per sample.",
                  "source": {"type": "local_tsv", "path": "assets/test_data/b.tsv"}, "null_values": [], "strip": False,
                  "input_fields": {"id": {"type": "String", "is_entity_id": True}, "w": {"type": "Int64"}},
                  "tier1": {"steps": []}},
        },
        "joins": {"AB": {"ui_label": "AB", "description": "One row per sample, A with B.",
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
    ("table, a key that is not a tier key", lambda r: r["data_schemas"]["A"].update(tier1={"steps": [], "ui_label": "x"}), "S06", "ui_label"),
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


def test_a_title_in_the_plot_is_refused_with_where_to_write_the_figure_title_and_the_name():
    raw = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(title="Old title"))
    problem = found(raw, "P01")[0]
    assert problem.path == "analysis_groups.g.plots.p.title"
    for words in ("labs", "ui_label", TOOL):
        assert words in problem.text()
    assert "ui_title" not in problem.text()                 # the key is removed (D-0409)


def test_ui_label_is_accepted_and_label_and_ui_title_are_refused_as_renamed_or_removed_at_group_and_plot():
    ok = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(plot_engine="python-plotnine"))
    assert check(ok).problems == []
    for code, change in (("G01", lambda r: r["analysis_groups"]["g"].update(ui_title="x")),
                         ("P01", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(ui_title="x"))):
        problem = found(mutated(change), code)
        assert problem and "ui_label" in problem[0].text() and "removed" in problem[0].text(), problem
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


# -- the other places that are named: info, a table, a join and an input field use ui_label too (D-0410, D-0468) --------------------------

def test_the_names_of_info_a_table_a_join_and_a_field_are_ui_label_and_the_old_label_is_refused_with_it():
    assert "label_keys" not in spec()                       # the table that held the pending answer is gone
    assert check(valid()).problems == []
    assert found(mutated(lambda r: r["data_schemas"]["A"].pop("ui_label")), "S03")
    assert found(mutated(lambda r: r["joins"]["AB"].pop("ui_label")), "J02")
    assert found(mutated(lambda r: r["data_schemas"]["A"].update(label="A")), "S01")
    assert found(mutated(lambda r: r["joins"]["AB"].update(label="A")), "J01")
    assert found(mutated(lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(label="V")), "FD01")
    assert found(mutated(lambda r: r["info"].update(label="R")), "I03")


def test_the_entry_keys_and_the_content_keys_split_the_keys_the_checker_accepts():
    entry, content = plot_keys()
    plot = spec()["elements"]["plot"]
    assert set(entry) | set(content) == set(plot["required"]) | set(plot["optional"])
    assert not set(entry) & set(content)
    assert set(entry) == {"plot_engine", "ui_label", "description", "comment", "taxonomy", "tier3"}
    assert {"target_dataset", "mapping", "layers", "theme", "palette", "facet_by", "labels", "guides", "filters"} == set(content)


def test_title_is_in_neither_list_of_a_plot_entry():
    entry, content = plot_keys()
    assert "title" not in entry and "title" not in content


def test_every_entry_key_is_a_key_the_checker_accepts_in_a_plot():
    plot = spec()["elements"]["plot"]
    assert set(plot["entry_keys"]) <= set(plot["required"]) | set(plot["optional"])


# -- an engine the app has no library for gives one message, not one per step (PROVISIONAL, follows the plain-message rule) ----------

def many_steps(raw):
    """Several steps and layers under the blocks, so that one EN02 per step would show."""
    raw["data_schemas"]["A"]["tier1"]["steps"] = [FILTER, FILTER, FILTER]
    raw["data_schemas"]["B"]["tier1"]["steps"] = [FILTER, FILTER]
    raw["analysis_groups"]["g"]["plots"]["p"]["layers"] = [{"name": "geom_col"}, {"name": "geom_point"}, {"name": "theme_bw"}]


def counts(raw):
    problems = check(raw, catalogs={**CATALOGS, **ENGINE_OF}).problems
    return {code: len([p for p in problems if p.code == code]) for code in ("T06", "EN02", "EN03")}


def test_an_unknown_engine_at_the_top_of_the_recipe_gives_one_t06_and_no_en02():
    assert counts(mutated(lambda r: (many_steps(r), r.update(data_engine="python-pandas")))) == {"T06": 1, "EN02": 0, "EN03": 0}
    assert counts(mutated(lambda r: (many_steps(r), r.update(plot_engine="r-ggplot2")))) == {"T06": 1, "EN02": 0, "EN03": 0}


def test_an_unknown_engine_on_one_tier_gives_one_t06_and_no_en02_for_its_steps():
    raw = mutated(lambda r: (many_steps(r), r["data_schemas"]["A"]["tier1"].update(data_engine="python-pandas")))
    assert counts(raw) == {"T06": 1, "EN02": 0, "EN03": 0}


def test_an_unknown_engine_on_a_plot_gives_one_t06_and_no_en02_for_its_layers():
    raw = mutated(lambda r: (many_steps(r), r["analysis_groups"]["g"]["plots"]["p"].update(plot_engine="r-ggplot2")))
    assert counts(raw) == {"T06": 1, "EN02": 0, "EN03": 0}


def test_a_known_engine_and_steps_of_another_library_still_give_one_en02_per_step_and_layer():
    # the real case: python-polars is an engine of the app, the steps belong to another library; the plot likewise
    engines = {"action_engines": {"polars_filter_demo": "python-other", "polars_join": "python-polars"},
               "component_engines": {"geom_col": "python-other", "geom_point": "python-other", "theme_bw": "python-plotnine"}}
    raw = mutated(many_steps)
    problems = check(raw, catalogs={**CATALOGS, **engines}).problems
    assert len([p for p in problems if p.code == "EN02"]) == 5 + 2, "three steps of A, two of B, and the two layers of the other library"
    assert [p for p in problems if p.code == "T06"] == []
