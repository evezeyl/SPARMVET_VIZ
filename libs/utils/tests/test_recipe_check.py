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
                "tier1": {"steps": []},
            },
            "B": {
                "label": "B", "description": "One row per sample.",
                "source": {"type": "local_tsv", "path": "assets/test_data/b.tsv"},
                "null_values": ["NA"], "strip": False,
                "input_fields": {"id": {"type": "String", "is_entity_key": True}, "w": {"type": "Int64"}},
                "tier1": {"steps": []},
            },
        },
        "joins": {
            "AB": {
                "label": "AB", "description": "One row per sample, A with B.",
                "ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}],
                "tier1": {"steps": [{"action": "polars_join", "right_ingredient": "B", "on": "id", "how": "left"}]},
                "labels": {"v": "Value"},
            }
        },
        "analysis_groups": {
            "g": {"ui_label": "G", "description": "Question.", "plots": {
                "p": {"ui_label": "P", "description": "Drawn.",
                      "target_dataset": "AB", "mapping": {"x": "id", "y": "v"}, "layers": [{"name": "geom_col"}]}}}
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
    ("E03", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["id"].update(type="Int64"), "run"),
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
    ("S06", "E", lambda r: r["data_schemas"]["A"].update(tier1=[]), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"].update(tier1=[{"action": "x"}]), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"].pop("tier1"), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"]["tier1"].update(tier2=[]), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"]["tier1"].pop("steps"), "run"),
    ("S06", "E", lambda r: r["data_schemas"]["A"].update(wrangling={"tier1": []}), "run"),
    ("S01", "E", lambda r: r["data_schemas"]["A"].update(tier9={"steps": []}), "run"),
    ("S07", "E", lambda r: r["data_schemas"]["A"].update(tier2={"steps": [{"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}]}), "run"),
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
    ("ST01", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"columns": ["v"]}), "run"),
    ("ST01", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append("polars_filter_demo"), "run"),
    ("ST02", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "filter_range"}), "run"),
    ("ST02", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "nope"}), "run"),
    ("ST03", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "polars_filter_demo", "columns": ["v"], "na": "keep", "column": "v"}), "run"),
    ("ST04", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "polars_filter_demo", "columns": ["v"]}), "run"),
    ("ST05", "E", lambda r: (r["data_schemas"]["A"].update(tier2={"steps": [{"action": "polars_join", "right_ingredient": "B", "how": "left", "on": "id"}]}),
                             r["analysis_groups"]["g"]["plots"]["p"].update(target_dataset="A")), "run"),
    ("ST06", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "polars_with_columns", "exprs": {"x": "__import__('os')"}}), "run"),
    ("ST06", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "polars_with_columns", "exprs": {"x": "pl.col('v').shuffle(seed=1)"}}), "run"),
    ("ST07", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "polars_filter_demo", "columns": "v", "na": "keep"}), "run"),
    ("ST08", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"id": "mine", "action": "polars_filter_demo", "columns": ["v"], "na": "keep"}), "run"),
    ("ST08", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"id": "audit_1a2b3c4d_1", "action": "polars_filter_demo", "columns": ["v"], "na": "keep"}), "build"),
    ("ST09", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "polars_filter_demo", "columns": ["v"], "na": "keep", "__metadata__": {}}), "run"),
    ("ST10", "E", lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "polars_filter_demo", "columns": ["v"], "na": "maybe"}), "run"),
    ("J01", "E", lambda r: r["joins"]["AB"].update(output_fields={}), "run"),
    ("J01", "E", lambda r: r["joins"]["AB"].update(final_contract={"id": {}}), "run"),
    ("J01", "E", lambda r: r["joins"]["AB"].update(info="s"), "run"),
    ("J02", "E", lambda r: r["joins"]["AB"].pop("label"), "run"),
    ("J03", "A", lambda r: r["joins"]["AB"].pop("description"), "run"),
    ("D01", "A", lambda r: r["joins"]["AB"].update(description="One row per sample (issue"), "run"),
    ("J04", "E", lambda r: r["joins"]["AB"].update(ingredients=["A", "B"]), "run"),
    ("J04", "E", lambda r: r["joins"]["AB"].update(ingredients=[]), "run"),
    ("J04", "E", lambda r: r["joins"]["AB"]["ingredients"].append({"dataset_id": "Ghost"}), "run"),
    ("J04", "E", lambda r: r["joins"]["AB"]["ingredients"].append({"dataset_id": "A"}), "run"),
    ("J05", "E", lambda r: r["joins"]["AB"]["tier1"]["steps"][0].update(right_ingredient="Ghost"), "run"),
    ("J05", "E", lambda r: r["joins"]["AB"]["tier1"]["steps"][0].pop("on"), "run"),
    ("J05", "E", lambda r: r["joins"]["AB"]["tier1"]["steps"][0].update(left_on="id", right_on="id"), "run"),
    ("J06", "E", lambda r: r["joins"]["AB"].update(labels=["v"]), "run"),
    ("J07", "E", lambda r: r["joins"]["AB"].update(tier1=[{"action": "polars_join"}]), "run"),
    ("J07", "E", lambda r: r["joins"]["AB"].update(steps={"tier1": []}), "run"),
    ("J14", "E", lambda r: (r["joins"]["AB"].update(tier2={"steps": [{"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}]}),
                            r["analysis_groups"]["g"]["plots"]["p"].update(target_dataset="A")), "run"),
    ("J07", "E", lambda r: r["joins"]["AB"].pop("tier1"), "run"),
    ("X1", "E", lambda r: r["joins"].update(A=copy.deepcopy(r["joins"]["AB"])), "run"),
    ("G01", "E", lambda r: r["analysis_groups"]["g"].pop("ui_label"), "run"),
    ("G01", "E", lambda r: r["analysis_groups"]["g"].update(label="G"), "run"),
    ("G01", "E", lambda r: r["analysis_groups"]["g"].update(unknown=1), "run"),
    ("G02", "A", lambda r: r["analysis_groups"]["g"].pop("description"), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("ui_label"), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(label="P"), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(spec={"target_dataset": "AB"}), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(title="T"), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(info="a sentence"), "run"),
    ("P02", "A", lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("description"), "run"),
    ("P03", "E", lambda r: r["analysis_groups"]["g"]["plots"].update({"Bad Id": copy.deepcopy(r["analysis_groups"]["g"]["plots"]["p"])}), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(tier1={"steps": []}), "run"),
    ("P04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(tier3=[]), "run"),
    ("P04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(steps={"tier3": {"steps": []}}), "run"),
    ("P06", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(filters=[{"column": "v"}]), "run"),
    ("P07", "E", lambda r: r["analysis_groups"].update(h=copy.deepcopy(r["analysis_groups"]["g"])), "run"),
    ("ST04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(tier3={"steps": [{"action": "polars_filter_demo", "columns": ["v"]}]}), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(family="Ranking"), "run"),
    ("P01", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(labs={}), "run"),
    ("PS02", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(target_dataset="Ghost"), "run"),
    ("PS02", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("target_dataset"), "run"),
    ("PS03", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].pop("layers"), "run"),
    ("PS03", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(layers=[{"name": "theme_bw"}]), "run"),
    ("PS04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["layers"].append({"params": {}}), "run"),
    ("PS04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["layers"].append({"name": "geom_colum"}), "run"),
    ("PS04", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["layers"][0].update(params={"colour_": 1}), "run"),
    ("PS05", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(theme="theme_nope"), "run"),
    ("PS06", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["layers"].append(
        {"name": "geom_smooth", "params": {"method": "lm", "formula": "y ~ I(__import__('os').getcwd())"}}), "run"),
    ("PS06", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["layers"].append(
        {"name": "stat_smooth", "params": {"formula": "y ~ np.load('/etc/passwd')"}}), "run"),
    ("PS06", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["layers"].append(
        {"name": "facet_wrap", "params": {"facets": "__import__('os').getcwd()"}}), "run"),
    ("PS06", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["layers"].append(
        {"name": "facet_grid", "params": {"rows": "g", "cols": ["h", "len(open('/x').read())"]}}), "run"),
    ("PS06", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["mapping"].update(facet_by="f(a + b)"), "run"),
    ("PS06", "E", lambda r: r["analysis_groups"]["g"]["plots"]["p"]["layers"].append(
        {"name": "stat_function", "params": {"fun": "__import__('os').getcwd()"}}), "run"),
    ("PD01", "E", lambda r: r.update(plot_defaults={"height": 3}), "run"),
    ("PD02", "E", lambda r: r.update(plot_defaults={"default_font_family": "Liberation Sans"}), "run"),
    ("PD02", "E", lambda r: r.update(plot_defaults={"facet_panel_spacing": 0.1}), "run"),
    ("PD02", "E", lambda r: r.update(plot_defaults={"legend_position": "top"}), "run"),
    ("PD02", "E", lambda r: r.update(plot_defaults={"optimisation": {"auto_axis_text": True}}), "run"),
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


def test_a_join_tier2_that_a_plot_reads_is_not_refused():
    raw = mutated(lambda r: r["joins"]["AB"].update(tier2={"steps": [{"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}]}))
    assert "J14" not in check(raw, file_stem="r").codes()


def test_a_problem_reads_as_recipe_path_what_and_fix():
    result = check(mutated(lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="numeric")), file_stem="r")
    text = result.problems[0].text("my_recipe")
    assert text.startswith("my_recipe : data_schemas.A.input_fields.v.type :")
    assert "Float64" in text and "Fix:" in text


def test_old_categorical_is_refused_with_the_three_suggestions():
    """Eve 2026-11-15: String for a category with no order, Enum for an order, Categorical also accepted.

    The order drawn for each was verified on a plot: String alphabetical, Enum as written, Categorical as the rows come.
    """
    problem = check(mutated(lambda r: r["data_schemas"]["A"]["input_fields"]["v"].update(type="categorical"))).problems[0]
    assert "no longer read" in problem.message
    assert "write `String` for a category with no order" in problem.fix and "alphabetical order" in problem.fix
    assert "write `Enum` with `categories:`" in problem.fix
    assert "`Categorical` is also accepted" in problem.fix and "order of the rows" in problem.fix
    assert not problem.fix.startswith("write Categorical")


def test_build_profile_accepts_placeholders_that_run_refuses():
    raw = valid()
    raw["analysis_groups"] = {}
    assert "T09" in check(raw, "run").codes()
    assert check(raw, "build").problems == []


AUDIT_CODES = ("ST08", "AU01", "AU02", "AU03")
AUDIT_STEP = {"id": "audit_1a2b3c4d_1", "action": "modif_filter", "column": "v", "op": "gt", "value": 1, "na": "keep", "audit_comment": "why"}


def audit_codes(raw, profile):
    return [code for code in check(raw, profile).codes() if code in AUDIT_CODES]


def test_an_audit_step_id_is_accepted_only_in_the_audit_list_of_the_audit_profile_and_must_be_well_formed():
    """D-0332: the audit id and the reason live in `audit_steps`; in the author's `steps` an id is refused in every profile, the audit profile included."""
    raw = mutated(lambda r: r["data_schemas"]["A"]["tier1"].update(audit_steps=[dict(AUDIT_STEP)]))
    assert audit_codes(raw, "audit") == []
    for profile in ("run", "build", "gallery"):
        assert audit_codes(raw, profile) == ["AU01"], profile
    raw["data_schemas"]["A"]["tier1"]["audit_steps"][0]["id"] = "audit_zz"
    assert audit_codes(raw, "audit") == ["AU03"]
    among_authors = mutated(lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append(
        {"id": "audit_1a2b3c4d_1", "action": "polars_filter_demo", "columns": ["v"], "na": "keep"}))
    for profile in ("run", "build", "audit"):
        assert "ST08" in audit_codes(among_authors, profile), profile


def test_the_same_audit_id_twice_is_refused():
    raw = mutated(lambda r: r["data_schemas"]["A"]["tier1"].update(audit_steps=[dict(AUDIT_STEP), dict(AUDIT_STEP)]))
    assert audit_codes(raw, "audit") == ["AU03"]


def test_a_step_may_carry_a_comment():
    raw = mutated(lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append(
        {"action": "polars_filter_demo", "columns": ["v"], "na": "keep", "comment": "why"}))
    assert check(raw).problems == []


def test_the_formula_of_a_mapping_step_is_checked():
    ok = mutated(lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append(
        {"action": "polars_with_columns", "exprs": {"x": "pl.col('v') * 2"}}))
    assert check(ok).problems == []


def test_an_empty_tier3_step_list_is_fine():
    raw = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(tier3={"steps": []}))
    assert check(raw).problems == []


def test_a_tier3_step_is_judged_like_any_step_because_the_engine_reads_it():
    """The engine reads `tier3` (DataOrchestrator.materialize_tier3): a non-empty list is no longer refused (P05 is retired), its steps
    are judged like the steps of any tier, and `filters` of a plot entry are refused (P06): they are written as tier3 steps."""
    assert "P05" not in {p.code for p in check(mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(
        tier3={"steps": [{"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}]}))).problems}
    good = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(
        tier3={"steps": [{"action": "polars_filter_demo", "columns": ["v"], "na": "keep"}]}))
    assert check(good).problems == []
    bad = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(
        tier3={"steps": [{"action": "polars_filter_demo", "columns": ["v"]}]}))
    assert "ST04" in check(bad).codes()
    with_filters = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(filters=[{"column": "v"}]))
    assert "P06" in check(with_filters).codes()


def test_a_wrong_form_names_the_old_action_replacement():
    raw = mutated(lambda r: r["data_schemas"]["A"]["tier1"]["steps"].append({"action": "filter_range"}))
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
    raw["analysis_groups"]["g"]["plots"]["p"]["target_dataset"] = "A"
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


# -- what a plot component is to plotnine, shown with a wrong argument (ADR-106 V1) ----------------

KINDS = {"geom_col": "exact", "geom_point": "modified", "theme_bw": "own"}


def _wrong_argument_message(component, kinds):
    def put_wrong_argument(r):
        r["analysis_groups"]["g"]["plots"]["p"]["layers"][0].update(name=component, params={"colr_": 1})
    catalogs = {**CATALOGS, "component_arguments": {**CATALOGS["component_arguments"], component: {"fill"}}}
    if kinds is not None:
        catalogs["component_kinds"] = kinds
    result = check(mutated(put_wrong_argument), catalogs=catalogs, file_stem="r")
    return next(p.message for p in result.problems if p.code == "PS04" and "colr_" in p.message)


def test_a_wrong_argument_says_what_the_component_is_to_plotnine():
    assert "exactly plotnine's geom_col" in _wrong_argument_message("geom_col", KINDS)
    assert "changes plotnine's geom_point" in _wrong_argument_message("geom_point", KINDS)
    assert "is not in plotnine" in _wrong_argument_message("theme_bw", KINDS)


def test_without_the_kinds_the_message_is_as_before():
    message = _wrong_argument_message("geom_col", None)
    assert message == "colr_ is not an argument of geom_col"


# -- random_state: accepted on a random layer and only on a random layer (SEED-HOLDS-1) --------------------------------

RANDOM_CATALOGS = {**CATALOGS, "components": CATALOGS["components"] | {"geom_sina", "geom_pointrange", "geom_bar"},
                   "component_arguments": {**CATALOGS["component_arguments"], "geom_point": {"position", "alpha", "stat"}, "geom_sina": {"random_state", "scale"},
                                           "geom_pointrange": {"stat", "fun_data", "color"}, "geom_bar": {"fill", "stat"}}}


def _seed_problems(name, params):
    def put(r):
        r["analysis_groups"]["g"]["plots"]["p"]["layers"][0].update(name=name, params=params)
    result = check(mutated(put), catalogs=RANDOM_CATALOGS, file_stem="r")
    return [p for p in result.problems if p.code == "PS04" and "random_state" in p.message]


@pytest.mark.parametrize("name, params", [
    ("geom_sina", {"random_state": 0}),
    ("geom_point", {"position": "jitter", "random_state": 0}),
    ("geom_point", {"position": "jitterdodge", "random_state": 3}),
    ("geom_pointrange", {"stat": "summary", "fun_data": "mean_cl_boot", "random_state": 0}),
    ("geom_pointrange", {"stat": "summary", "random_state": 0}),
    ("geom_point", {"stat": "sina", "random_state": 0}),
    ("geom_bar", {"stat": "sina", "random_state": 0}),
    ("geom_point", {"position": "position_jitter", "random_state": 0}),
    ("geom_point", {"position": "position_jitterdodge", "random_state": 0}),
    ("geom_point", {"stat": "stat_sina", "random_state": 0}),
    ("geom_pointrange", {"stat": "stat_summary", "random_state": 0}),
])
def test_a_seed_is_accepted_on_a_random_layer(name, params):
    assert _seed_problems(name, params) == []


@pytest.mark.parametrize("name, params", [
    ("geom_point", {"random_state": 0}),
    ("geom_point", {"position": "dodge", "random_state": 0}),
    ("geom_bar", {"random_state": 0}),
    ("geom_pointrange", {"random_state": 0}),
    ("geom_pointrange", {"stat": "summary", "fun_data": "mean_se", "random_state": 0}),
    ("geom_point", {"position": "position_dodge", "random_state": 0}),
])
def test_a_seed_is_refused_on_a_layer_that_is_not_random(name, params):
    assert len(_seed_problems(name, params)) == 1


@pytest.mark.parametrize("written", [None, "random", " RANDOM ", "abc", "1.5", 2.5, True])
@pytest.mark.parametrize("name, params", [
    ("geom_sina", {}),
    ("geom_point", {"position": "jitter"}),
    ("geom_pointrange", {"stat": "summary", "fun_data": "mean_cl_boot"}),
])
def test_null_or_random_as_a_seed_is_refused_with_the_fix(name, params, written):
    """PROVISIONAL (S1): a seed is a number; the checker names the fix."""
    def put(r):
        r["analysis_groups"]["g"]["plots"]["p"]["layers"][0].update(name=name, params={**params, "random_state": written})
    result = check(mutated(put), catalogs=RANDOM_CATALOGS, file_stem="r")
    found = [p for p in result.problems if p.code == "PS04" and "random_state" in p.message]
    assert len(found) == 1 and "random_state: 0" in found[0].fix and "number" in found[0].message


@pytest.mark.parametrize("written", [0, 7, "5"])
def test_a_number_as_a_seed_is_not_refused_by_s1(written):
    def put(r):
        r["analysis_groups"]["g"]["plots"]["p"]["layers"][0].update(name="geom_sina", params={"random_state": written})
    result = check(mutated(put), catalogs=RANDOM_CATALOGS, file_stem="r")
    assert not [p for p in result.problems if p.code == "PS04" and "random_state" in p.message]


# -- PROVISIONAL (S3): plot_defaults.random_state is the one seed of the whole recipe --------------------------------

def _with_plot_defaults(value):
    def put(r):
        r["plot_defaults"] = {"random_state": value}
    return check(mutated(put), file_stem="r")


@pytest.mark.parametrize("value", [0, 7, 123456, "7"])
def test_the_checker_knows_the_recipe_seed_key(value):
    assert [p for p in _with_plot_defaults(value).problems if p.path.startswith("plot_defaults")] == []


@pytest.mark.parametrize("value", [None, "random", "abc", True, 1.5, [1]])
def test_the_recipe_seed_is_a_whole_number(value):
    found = [p for p in _with_plot_defaults(value).problems if p.path.startswith("plot_defaults")]
    assert len(found) == 1 and found[0].code == "PD01" and "random_state: 0" in found[0].fix


# -- PS06: a text of a layer that plotnine evaluates as Python (PLOT-TEXT-RUNS-CODE-1) --------------------------------------

def _layer_problems(params, name="geom_smooth", catalogs=CATALOGS):
    def put(r):
        r["analysis_groups"]["g"]["plots"]["p"]["layers"].append({"name": name, "params": params})
    return [p for p in check(mutated(put), catalogs=catalogs, file_stem="r").problems if p.code == "PS06"]


def test_ps06_is_found_without_any_catalogue_and_names_the_layer_and_the_text():
    def put(r):
        r["analysis_groups"]["g"]["plots"]["p"]["layers"].append(
            {"name": "geom_smooth", "params": {"formula": "y ~ I(eval(x))"}})
    found = [p for p in check_recipe(mutated(put)).problems if p.code == "PS06"]
    assert len(found) == 1
    assert found[0].path.endswith("layers[2].params.formula")
    assert "'y ~ I(eval(x))'" in found[0].message and "'eval'" in found[0].message
    assert found[0].fix.startswith("Suggestion: ")


@pytest.mark.parametrize("name, params", [
    ("geom_smooth", {"method": "lm", "formula": "y ~ x + I(x**2)"}),
    ("geom_smooth", {"method": "lm", "formula": "y ~ np.log(x)"}),
    ("stat_smooth", {"formula": "y ~ bs(x, df=4)"}),
    ("facet_wrap", {"facets": "~ metric"}),
    ("facet_wrap", {"facets": "country"}),
    ("facet_grid", {"facets": "row_group ~ col_group"}),
    ("facet_grid", {"rows": "a", "cols": "b"}),
])
def test_ps06_leaves_what_a_scientist_writes_alone(name, params):
    assert _layer_problems(params, name) == []


def test_ps06_refuses_a_function_text_of_stat_function_with_the_message_when_the_recipe_is_checked():
    from utils.plot_text_check import STAT_FUNCTION_TEXT_BLOCKED
    found = _layer_problems({"fun": "lambda x: x ** 2"}, "stat_function")
    assert len(found) == 1 and STAT_FUNCTION_TEXT_BLOCKED in found[0].message


def test_ps06_facet_by_in_the_mapping_is_a_plain_column_name():
    ok = mutated(lambda r: r["analysis_groups"]["g"]["plots"]["p"]["mapping"].update(facet_by="country"))
    assert "PS06" not in check(ok, file_stem="r").codes()


def test_a_closed_bracket_description_gets_no_cut_advice_and_every_element_is_looked_at():
    assert "D01" not in check(valid()).codes()
    for where, change in {
        "info": lambda r: r["info"].update(description="What it answers (issue"),
        "schema": lambda r: r["data_schemas"]["A"].update(description="One row per sample (issue"),
        "group": lambda r: r["analysis_groups"]["g"].update(description="Which (issue"),
        "plot": lambda r: r["analysis_groups"]["g"]["plots"]["p"].update(description="Bars (issue"),
    }.items():
        assert "D01" in check(mutated(change)).codes(), where


# -- the layers of plot_defaults go through the same layer checks as the layers of a plot (D-0050)
def _with_defaults_layers(layers):
    def put(raw):
        raw["plot_defaults"] = {"layers": layers}
    return mutated(put)


def test_defaults_layers_unknown_component_is_reported():
    result = check(_with_defaults_layers([{"name": "theme_bww"}]), file_stem="r")
    found = [p for p in result.problems if p.code == "PS04" and p.path.startswith("plot_defaults.layers[1]")]
    assert found and "theme_bww" in found[0].message and "theme_bw" in found[0].fix


def test_defaults_layers_unknown_argument_is_reported():
    result = check(_with_defaults_layers([{"name": "geom_col", "params": {"colr_": 1}}]), file_stem="r")
    assert [p for p in result.problems if p.code == "PS04" and "colr_" in p.message and p.path.startswith("plot_defaults.layers")]


def test_defaults_layers_valid_block_is_accepted_and_needs_no_geom():
    result = check(_with_defaults_layers([{"name": "theme_bw"}]), file_stem="r")
    assert result.problems == []


def test_defaults_layers_that_is_not_a_list_is_reported():
    result = check(_with_defaults_layers({"name": "theme_bw"}), file_stem="r")
    assert [p for p in result.problems if p.path == "plot_defaults.layers"]


# --- P07: a plot id written in two groups of one recipe (RESULT-ID-TWICE-NOT-REFUSED, D-0050) ---------

def _second_group(raw, name="h", plot_id="p"):
    group = copy.deepcopy(raw["analysis_groups"]["g"])
    group["plots"] = {plot_id: group["plots"].pop("p")} if plot_id != "p" else group["plots"]
    raw["analysis_groups"][name] = group


def test_p07_names_the_id_and_both_groups_in_one_line():
    found = [p for p in check(mutated(_second_group), file_stem="r").problems if p.code == "P07"]
    assert len(found) == 1
    text = found[0].message
    assert "'p'" in text and "'g'" in text and "'h'" in text
    assert found[0].path == "analysis_groups.h.plots.p" and found[0].fix


def test_p07_three_groups_give_one_line_per_extra_entry_each_naming_the_first_group():
    def change(raw):
        _second_group(raw, "h")
        _second_group(raw, "k")
    found = [p for p in check(mutated(change), file_stem="r").problems if p.code == "P07"]
    assert [p.path for p in found] == ["analysis_groups.h.plots.p", "analysis_groups.k.plots.p"]
    assert all("'g'" in p.message for p in found)


def test_p07_does_not_fire_when_the_ids_differ_and_the_recipe_is_unchanged():
    assert check(mutated(lambda r: _second_group(r, "h", "q")), file_stem="r").problems == []
    assert check(valid(), file_stem="r").problems == []


def test_p07_ids_that_differ_only_by_case_are_different_ids_here_and_p03_refuses_the_capital():
    codes = check(mutated(lambda r: _second_group(r, "h", "P")), file_stem="r").codes()
    assert "P07" not in codes and "P03" in codes


def test_p07_the_loader_refuses_a_plot_id_twice_in_one_group(tmp_path):
    from utils.strict_yaml import DuplicateKeyError, load_strict
    text = "plots:\n  p: {a: 1}\n  p: {a: 2}\n"
    with pytest.raises(DuplicateKeyError):
        load_strict(text)
