"""`check_recipe`: one test per row of the catalogue (spec section 11). A small valid recipe, one change per case.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check.py -q
"""
import copy

import pytest

from utils.recipe_check import Problem, check_recipe, check_recipe_set, spec

ACTIONS = {
    "polars_filter_demo": {
        "context": ["t1", "t2"],
        "params": {
            "columns": {"widget": "column_selector", "multi": True, "required": True},
            "na": {"widget": "enum", "options": ["keep", "remove"], "required": True},
        },
    },
    "polars_with_columns": {
        "context": ["t1", "t2"],
        "params": {"exprs": {"widget": "mapping", "value_widget": "expression", "required": True}},
    },
    "polars_join": {
        "context": ["assembly"],
        "params": {
            "right_ingredient": {"widget": "string", "required": True},
            "how": {"widget": "enum", "options": ["left", "inner"], "required": True},
            "on": {"widget": "string", "required": False},
            "left_on": {"widget": "string", "required": False},
            "right_on": {"widget": "string", "required": False},
        },
    },
}
CATALOGS = {
    "actions": ACTIONS,
    "components": {"geom_col", "geom_point", "theme_bw"},
    "component_arguments": {"geom_col": {"fill", "color"}, "geom_point": None, "theme_bw": None},
    "themes": {"theme_bw", "theme_light"},
    "old_action_names": {"filter_range": "polars_filter_demo"},
}


def valid():
    return {
        "id": "r", "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine",
        "info": {"label": "R", "description": "What it answers", "contact": "me"},
        "data_schemas": {
            "A": {
                "label": "A", "description": "One row per sample.",
                "source": {"type": "local_tsv", "path": "assets/test_data/a.tsv"},
                "null_values": [], "strip": True,
                "input_fields": {"id": {"type": "String", "is_entity_key": True}, "v": {"type": "Float64"}},
                "wrangling": {"tier1": []},
            },
            "B": {
                "label": "B", "description": "One row per sample.",
                "source": {"type": "local_tsv", "path": "assets/test_data/b.tsv"},
                "null_values": ["NA"], "strip": False,
                "input_fields": {"id": {"type": "String", "is_entity_key": True}, "w": {"type": "Int64"}},
                "wrangling": {"tier1": []},
            },
        },
        "joins": {
            "AB": {
                "label": "AB", "description": "One row per sample, A with B.",
                "ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}],
                "steps": {"tier1": [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}]},
                "labels": {"v": "Value"},
            }
        },
        "analysis_groups": {
            "g": {"label": "G", "description": "Question.", "plots": {
                "p": {"label": "P", "description": "Drawn.",
                      "spec": {"target_dataset": "AB", "mapping": {"x": "id", "y": "v"}, "layers": [{"name": "geom_col"}]}}}}
        },
    }


def check(raw, profile="run", **kw):
    kw.setdefault("catalogs", CATALOGS)
    return check_recipe(raw, profile, **kw)


def mutated(change):
    raw = valid()
    change(raw)
    return raw


def test_a_valid_recipe_has_no_problem_and_full_coverage():
    result = check(valid(), file_stem="r")
    assert result.problems == []
    assert {"structure", "actions", "components"} <= result.coverage


def test_without_catalogs_the_coverage_says_so():
    result = check_recipe(valid())
    assert result.problems == [] and result.coverage == {"structure"}


def test_the_specification_is_data_and_has_the_format_version():
    assert spec()["format_version"] == 1


# (code, severity, mutation, profile)
CASES = [
    ("T01", "E", None, "run"),
    ("T03", "E", lambda r: r.update(foo=1), "run"),
    ("T03", "E", lambda r: r.update(name="x"), "run"),
    ("T03", "E", lambda r: r.update(final_contract={}), "run"),
    ("T08", "E", lambda r: r.update(plots={}), "run"),
    ("T04", "E", lambda r: r.pop("info"), "run"),
    ("T04", "E", lambda r: r.pop("data_schemas"), "run"),
    ("T04", "E", lambda r: r.pop("analysis_groups"), "run"),
    ("T04", "E", lambda r: r.pop("data_engine"), "run"),
    ("T05", "E", lambda r: r.update(id="other"), "run"),
    ("V01", "E", lambda r: r.pop("spec_version"), "run"),
    ("V02", "E", lambda r: r.update(spec_version=0), "run"),
    ("V03", "E", lambda r: r.update(spec_version=2), "run"),
    ("V04", "E", lambda r: r.update(spec_version="1"), "run"),
    ("V04", "E", lambda r: r.update(spec_version=1.0), "run"),
    ("V04", "E", lambda r: r.update(spec_version=True), "run"),
    ("T06", "E", lambda r: r.update(data_engine="pandas"), "run"),
    ("T06", "E", lambda r: r.update(plot_engine="python-polars"), "run"),
    ("T09", "E", lambda r: r.update(analysis_groups={}), "run"),
    ("I01", "E", lambda r: r.update(info="text"), "run"),
    ("I01", "E", lambda r: r["info"].pop("label"), "run"),
    ("I02", "A", lambda r: r["info"].pop("description"), "run"),
    ("I02", "A", lambda r: r["info"].pop("contact"), "run"),
    ("I03", "E", lambda r: r["info"].update(display_name="x"), "run"),
    ("E01", "E", lambda r: r.update(entity={"noun": "s", "plural": "ss", "population": "A", "x": 1}), "run"),
    ("E01", "E", lambda r: r.update(entity={"noun": "s"}), "run"),
    ("E02", "E", lambda r: r.update(entity={"noun": "s", "plural": "ss", "population": "Nope"}), "run"),
    ("E02", "E", lambda r: (r.update(entity={"noun": "s", "plural": "ss", "population": "A"}),
                            r["data_schemas"]["A"]["input_fields"]["id"].pop("is_entity_key")), "run"),
    ("S01", "E", lambda r: r["data_schemas"]["A"].update(info={"x": 1}), "run"),
    ("S01", "E", lambda r: r["data_schemas"]["A"].update(output_fields={}), "run"),
    ("S01", "E", lambda r: r["data_schemas"]["A"].update(fields={}), "run"),
    ("S02", "E", lambda r: r.update(additional_datasets_schemas={"A": copy.deepcopy(r["data_schemas"]["A"])}), "run"),
    ("S02", "E", lambda r: r["data_schemas"].update(metadata_schema=copy.deepcopy(r["data_schemas"]["A"])), "run"),
    ("S03", "E", lambda r: r["data_schemas"]["A"].pop("label"), "run"),
    ("S04", "A", lambda r: r["data_schemas"]["A"].pop("description"), "run"),
    ("S05", "E", lambda r: r["data_schemas"]["A"].pop("source"), "run"),
    ("S05", "E", lambda r: r["data_schemas"]["A"]["source"].update(type="remote"), "run"),
    ("S05", "E", lambda r: r["data_schemas"]["A"]["source"].pop("path"), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"].update(wrangling=[]), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"].update(wrangling=[{"action": "x"}]), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"].update(wrangling={"tier2": []}), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"].update(wrangling={"tier1": [], "tier9": []}), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"].update(wrangling={"tier1": {}}), "run"),
    ("S07", "E", lambda r: r["data_schemas"]["A"]["wrangling"].update(tier2=[{"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}]), "run"),
    ("S08", "E", lambda r: r["data_schemas"]["A"].update(input_fields=["id"]), "run"),
    ("S09", "E", lambda r: r["data_schemas"]["A"].pop("null_values"), "run"),
    ("S09", "E", lambda r: r["data_schemas"]["A"].pop("strip"), "run"),
    ("S09", "E", lambda r: r["data_schemas"]["A"].update(strip="yes"), "run"),
    ("S09", "E", lambda r: r["data_schemas"]["A"].update(null_values="NA"), "run"),
    ("S09", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(null_values=3), "run"),
    ("FD01", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(colour="x"), "run"),
    ("FD02", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].pop("type"), "run"),
    ("FD02", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="categorical"), "run"),
    ("FD02", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="numeric"), "run"),
    ("FD02", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="Binary"), "run"),
    ("FD02", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="Utf8"), "run"),
    ("FD03", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["id"].update(is_primary_key=True), "run"),
    ("FD04", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(source_name="V"), "run"),
    ("FD05", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["id"].update(is_entity_key="yes"), "run"),
    ("FD05", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="Enum"), "run"),
    ("FD05", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(categories=["a"]), "run"),
    ("FD05", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(precision=5), "run"),
    ("FD06", "E", lambda r: r["data_schemas"]["A"]["input_fields"].update(v="Float64"), "run"),
    ("ST01", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"columns": ["v"]}), "run"),
    ("ST01", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append("polars_filter_demo"), "run"),
    ("ST02", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "filter_range"}), "run"),
    ("ST02", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "nope"}), "run"),
    ("ST03", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "polars_filter_demo", "columns": ["v"], "na": "keep", "column": "v"}), "run"),
    ("ST04", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "polars_filter_demo", "columns": ["v"]}), "run"),
    ("ST05", "E", lambda r: (r["data_schemas"]["A"]["wrangling"].update(tier2=[{"action": "polars_join", "right_ingredient": "B", "how": "left", "on": "id"}]),
                             r["analysis_groups"]["g"]["plots"]["p"]["spec"].update(target_dataset="A")), "run"),
    ("ST06", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "polars_with_columns", "exprs": {"x": "__import__('os')"}}), "run"),
    ("ST07", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "polars_filter_demo", "columns": "v", "na": "keep"}), "run"),
    ("ST08", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"id": "mine", "action": "polars_filter_demo", "columns": ["v"], "na": "keep"}), "run"),
    ("ST08", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"id": "audit_1a2b3c4d_1", "action": "polars_filter_demo", "columns": ["v"], "na": "keep"}), "build"),
    ("ST09", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "polars_filter_demo", "columns": ["v"], "na": "keep", "__metadata__": {}}), "run"),
    ("ST10", "E", lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "polars_filter_demo", "columns": ["v"], "na": "maybe"}), "run"),
    ("J01", "E", lambda r: r["joins"]["AB"].update(output_fields={}), "run"),
    ("J01", "E", lambda r: r["joins"]["AB"].update(final_contract={"id": {}}), "run"),
    ("J01", "E", lambda r: r["joins"]["AB"].update(info="s"), "run"),
    ("J02", "E", lambda r: r["joins"]["AB"].pop("label"), "run"),
    ("J03", "A", lambda r: r["joins"]["AB"].pop("description"), "run"),
    ("J04", "E", lambda r: r["joins"]["AB"].update(ingredients=["A", "B"]), "run"),
    ("J04", "E", lambda r: r["joins"]["AB"].update(ingredients=[]), "run"),
    ("J04", "E", lambda r: r["joins"]["AB"]["ingredients"].append({"dataset_id": "Ghost"}), "run"),
    ("J04", "E", lambda r: r["joins"]["AB"]["ingredients"].append({"dataset_id": "A"}), "run"),
    ("J05", "E", lambda r: r["joins"]["AB"]["steps"]["tier1"][0].update(right_ingredient="Ghost"), "run"),
    ("J05", "E", lambda r: r["joins"]["AB"]["steps"]["tier1"][0].pop("on"), "run"),
    ("J05", "E", lambda r: r["joins"]["AB"]["steps"]["tier1"][0].update(left_on="id", right_on="id"), "run"),
    ("J06", "E", lambda r: r["joins"]["AB"].update(labels=["v"]), "run"),
    ("J07", "E", lambda r: r["joins"]["AB"].update(steps=[{"action": "polars_join"}]), "run"),
    ("J07", "E", lambda r: r["joins"]["AB"].update(steps={"tier2": []}), "run"),
    ("X1", "E", lambda r: r["joins"].update(A=copy.deepcopy(r["joins"]["AB"])), "run"),
    ("G01", "E", lambda r: r["analysis_groups"]["g"].pop("label"), "run"),
    ("G01", "E", lambda r: r["analysis_groups"]["g"].update(unknown=1), "run"),
    ("G02", "A", lambda r: r["analysis_groups"]["g"].pop("description"), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("label"), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(info="a sentence"), "run"),
    ("P02", "A", lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("description"), "run"),
    ("P03", "E", lambda r: r["analysis_groups"]["g"]["plots"].update({"Bad Id": copy.deepcopy(r["analysis_groups"]["g"]["plots"]["p"])}), "run"),
    ("P04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(steps={"tier1": []}), "run"),
    ("P04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(steps=[]), "run"),
    ("P05", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(steps={"tier3": [{"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}]}), "run"),
    ("PS01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"].update(family="Ranking"), "run"),
    ("PS01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"].update(labs={}), "run"),
    ("PS02", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"].update(target_dataset="Ghost"), "run"),
    ("PS02", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"].pop("target_dataset"), "run"),
    ("PS03", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"].pop("layers"), "run"),
    ("PS03", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"].update(layers=[{"name": "theme_bw"}]), "run"),
    ("PS04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"]["layers"].append({"params": {}}), "run"),
    ("PS04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"]["layers"].append({"name": "geom_colum"}), "run"),
    ("PS04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"]["layers"][0].update(params={"colour_": 1}), "run"),
    ("PS05", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"].update(theme="theme_nope"), "run"),
    ("PD01", "E", lambda r: r.update(plot_defaults={"height": 3}), "run"),
    ("CM01", "E", lambda r: r["data_schemas"]["A"].update(comment=3), "run"),
    ("CM01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(comment=["x"]), "run"),
    ("PA01", "E", lambda r: r["data_schemas"]["A"]["source"].update(path="/etc/passwd"), "run"),
    ("PA01", "E", lambda r: r["data_schemas"]["A"]["source"].update(path="../x.tsv"), "run"),
]


@pytest.mark.parametrize("code, severity, change, profile", CASES, ids=[f"{c[0]}-{i}" for i, c in enumerate(CASES)])
def test_each_row_of_the_catalogue_is_found_with_the_fix(code, severity, change, profile):
    raw = "not a mapping" if change is None else mutated(change)
    result = check(raw, profile, file_stem="r")
    found = [p for p in result.problems if p.code == code]
    assert found, f"{code} not found; got {result.codes()}"
    assert found[0].severity == severity
    assert all(isinstance(p, Problem) for p in result.problems)
    if severity == "E" and code not in ("ST08",):
        assert found[0].fix or code in ("T01",), f"{code} names no fix"


def test_a_problem_reads_as_recipe_path_what_and_fix():
    result = check(mutated(lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="numeric")), file_stem="r")
    text = result.problems[0].text("my_recipe")
    assert text.startswith("my_recipe : data_schemas.A.input_fields.v.type :")
    assert "Float64" in text and "Fix:" in text


def test_categorical_is_refused_with_this_was_string():
    result = check(mutated(lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="categorical")))
    assert "String" in result.problems[0].fix


def test_build_profile_accepts_placeholders_that_run_refuses():
    raw = valid()
    raw["analysis_groups"] = {}
    assert "T09" in check(raw, "run").codes()
    assert check(raw, "build").problems == []


def test_an_audit_step_id_is_accepted_only_in_the_audit_profile_and_must_be_well_formed():
    raw = mutated(lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append(
        {"id": "audit_1a2b3c4d_1", "action": "polars_filter_demo", "columns": ["v"], "na": "keep"}))
    assert "ST08" in check(raw, "run").codes()
    assert "ST08" not in check(raw, "audit").codes()
    raw["data_schemas"]["A"]["wrangling"]["tier1"][0]["id"] = "audit_zz"
    assert "ST08" in check(raw, "audit").codes()


def test_the_same_audit_id_twice_is_refused():
    step = {"id": "audit_1a2b3c4d_1", "action": "polars_filter_demo", "columns": ["v"], "na": "keep"}
    raw = mutated(lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].extend([dict(step), dict(step)]))
    assert "ST08" in check(raw, "audit").codes()


def test_a_step_may_carry_a_comment():
    raw = mutated(lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append(
        {"action": "polars_filter_demo", "columns": ["v"], "na": "keep", "comment": "why"}))
    assert check(raw).problems == []


def test_the_formula_of_a_mapping_step_is_checked():
    ok = mutated(lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append(
        {"action": "polars_with_columns", "exprs": {"x": "pl.col('v') * 2"}}))
    assert check(ok).problems == []


def test_a_tier3_step_list_is_refused_until_the_engine_reads_it_and_an_empty_one_is_fine():
    raw = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(steps={"tier3": []}))
    assert check(raw).problems == []


def test_a_tier3_step_is_judged_like_any_step_once_the_engine_reads_it(monkeypatch):
    import utils.recipe_check as module
    monkeypatch.setattr(module, "TIER3_READ_BY_ENGINE", True)
    good = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(
        steps={"tier3": [{"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}]}))
    assert check(good).problems == []
    bad = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(
        steps={"tier3": [{"action": "polars_filter_demo", "columns": ["v"]}]}))
    assert "ST04" in check(bad).codes()
    with_filters = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"]["spec"].update(filters=[{"column": "v"}]))
    assert "P06" in check(with_filters).codes()


def test_a_wrong_form_names_the_old_action_replacement():
    raw = mutated(lambda r: r["data_schemas"]["A"]["wrangling"]["tier1"].append({"action": "filter_range"}))
    st02 = next(p for p in check(raw).problems if p.code == "ST02")
    assert "polars_filter_demo" in st02.fix


# ---- paths (PA02), the recipe graph (J08), the gallery profile, the set -----------------------------------------

def test_a_development_path_outside_the_allowed_roots_is_refused(tmp_path):
    (tmp_path / "assets" / "test_data").mkdir(parents=True)
    (tmp_path / "elsewhere").mkdir()
    raw = valid()
    assert check(raw, roots=[tmp_path / "assets" / "test_data"], base=tmp_path).problems == []
    raw["data_schemas"]["A"]["source"]["path"] = "elsewhere/a.tsv"
    assert "PA02" in check(raw, roots=[tmp_path / "assets" / "test_data"], base=tmp_path).codes()


class Graph:
    def __init__(self, columns):
        self.columns = columns

    def columns_of(self, dataset_id):
        return self.columns.get(dataset_id)


def test_a_column_in_both_ingredients_that_is_not_a_key_is_j08():
    graph = Graph({"A": ["id", "v", "total"], "B": ["id", "total"]})
    result = check(valid(), graph=graph)
    j08 = [p for p in result.problems if p.code == "J08"]
    assert j08 and "total" in j08[0].message and j08[0].fix
    assert "columns" in result.coverage


def test_the_join_key_in_both_ingredients_is_fine():
    graph = Graph({"A": ["id", "v"], "B": ["id", "w"]})
    assert check(valid(), graph=graph).problems == []


def test_the_same_plot_id_in_two_recipes_is_x5():
    one, two = valid(), valid()
    problems = check_recipe_set({"one": one, "two": two})
    assert problems and problems[0].code == "X5"
    two["analysis_groups"]["g"]["plots"] = {"q": two["analysis_groups"]["g"]["plots"]["p"]}
    assert check_recipe_set({"one": one, "two": two}) == []


def gallery_recipe():
    raw = valid()
    raw["id"] = "bar_simple"
    raw["joins"] = {}
    del raw["data_schemas"]["B"]
    raw["data_schemas"]["A"]["source"]["path"] = "./assets/gallery_data/bar_simple/example_data.tsv"
    raw["analysis_groups"]["g"]["plots"]["p"]["spec"]["target_dataset"] = "A"
    raw["analysis_groups"]["g"]["plots"]["p"]["taxonomy"] = {
        "family": "Ranking", "pattern": "1 Numeric, 1 Categorical", "difficulty": "Simple", "show": "ranking", "sample_size": "any"}
    return raw


def test_a_good_gallery_example_passes_the_gallery_profile():
    assert check(gallery_recipe(), "gallery", file_stem="bar_simple").problems == []


@pytest.mark.parametrize("code, change", [
    ("GP01", lambda r: r["analysis_groups"].update(h=copy.deepcopy(r["analysis_groups"]["g"]))),
    ("GP02", lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("taxonomy")),
    ("GP02", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["taxonomy"].pop("show")),
    ("GP03", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["taxonomy"].update(family="Nonsense")),
    ("GP04", lambda r: r.update(id="other")),
    ("GP06", lambda r: r["data_schemas"]["A"]["source"].update(path="./assets/test_data/a.tsv")),
])
def test_each_gallery_rule_is_found(code, change):
    raw = gallery_recipe()
    change(raw)
    assert code in check(raw, "gallery", file_stem="bar_simple").codes()


def test_a_missing_companion_file_is_gp05(tmp_path):
    (tmp_path / "example_data.tsv").write_text("x")
    result = check(gallery_recipe(), "gallery", file_stem="bar_simple", bundle_dir=tmp_path)
    assert [p.path for p in result.problems if p.code == "GP05"] == ["example_meta.md", "preview_plot.png"]


def test_an_unknown_profile_is_a_programming_error():
    with pytest.raises(ValueError):
        check_recipe(valid(), "other")
