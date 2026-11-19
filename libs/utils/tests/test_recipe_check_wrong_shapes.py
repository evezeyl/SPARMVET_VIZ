"""The recipe checker reports a value of the wrong SHAPE with a code; it never raises (D-0029, D-0102).

A recipe whose value has the wrong shape (a list where a text is expected, a mapping where a list is expected) is read by the checker as a problem
with the code of the element it sits in. Before this file the checker raised a Python error on some of them (TypeError: unhashable type), and the
gate of the app turned that into one line that said nothing about the recipe. Each test below breaks one place and asserts the code AND that the
check ends; the last test runs a seeded fuzz of shape corruptions of a shipped recipe.

Mutation index (each seen failing): W1 the guard of `ingredients` is removed; W2 the guard of `join_steps` (right_ingredient); W3 the guard of
`plot_content` (target and theme); W4 the guard of `sum_advices`; W5 the guard of `steps` (action in tier 2); W6 the guard of `check_engine_of`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_wrong_shapes.py -q
"""
import copy
import random

import pytest

from app.modules.data_analysis_recipe_validator import _graph_of, checker_catalogs
from utils.recipe_check import check_recipe
from utils.recipe_loader import load_recipe

ROOT = "config/data_analysis_recipes/pipelines/"
SHAPES = [[], {}, 7, None, True, [[1]], [{"a": 1}], {"a": [1]}, [None], ["x"]]


@pytest.fixture(scope="module")
def catalogs():
    return checker_catalogs()


@pytest.fixture(scope="module")
def raw():
    return load_recipe(ROOT + "2_test_data_ST22_dummy.yaml")[0]


def check(raw, catalogs, graph=False, profile="build"):
    return check_recipe(raw, profile, catalogs=catalogs, graph=_graph_of(raw) if graph else None)


def broken(raw, path, value):
    """A copy of the recipe with `value` written at `path` (a tuple of keys and positions)."""
    out = copy.deepcopy(raw)
    node = out
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    return out


JOIN = ("joins", "AMR_Profile_Joint")
JOIN_STEP = JOIN + ("tier1", "steps", 1)       # the polars_join step
PLOT = ("analysis_groups", "Group_1", "plots")


def first_plot_path(raw):
    group = next(iter(raw["analysis_groups"]))
    plot = next(iter(raw["analysis_groups"][group]["plots"]))
    return ("analysis_groups", group, "plots", plot)


@pytest.mark.parametrize("shape", [[], {"a": 1}, [[1]], 7])
def test_an_ingredient_whose_dataset_id_is_not_text_is_J04(raw, catalogs, shape):
    """MUTATION W1."""
    result = check(broken(raw, JOIN + ("ingredients", 0, "dataset_id"), shape), catalogs)
    assert "J04" in result.codes()
    assert not result.ok


@pytest.mark.parametrize("shape", [[], {"a": 1}, [[1]], 7])
def test_a_join_step_whose_right_ingredient_is_not_text_is_J05_with_and_without_the_graph(raw, catalogs, shape):
    """MUTATION W2: the key checks compare tables by id and raised on a list."""
    for graph in (False, True):
        result = check(broken(raw, JOIN_STEP + ("right_ingredient",), shape), catalogs, graph)
        assert "J05" in result.codes() and not result.ok


def test_an_earlier_join_step_with_a_wrong_right_ingredient_does_not_stop_the_check_of_the_next(raw, catalogs):
    """The left table of a later join is made of the tables joined before: with one that has no text id, the checks that need it are silent and J05 speaks."""
    mutated = copy.deepcopy(raw)
    steps = mutated["joins"]["AMR_Profile_Joint"]["tier1"]["steps"]
    first = next(i for i, s in enumerate(steps) if isinstance(s, dict) and "right_ingredient" in s)
    steps.insert(first, {**steps[first], "right_ingredient": ["x"]})   # a join step with a wrong id, then the real one
    result = check(mutated, catalogs, True)
    assert "J05" in result.codes() and not result.ok


def test_a_step_whose_action_is_not_text_is_ST01_also_without_catalogs_and_in_tier_2(raw, catalogs):
    """MUTATION W5."""
    schema = ("data_schemas", "amr_data", "tier1", "steps", 0, "action")
    for catalog in (catalogs, None):
        result = check_recipe(broken(raw, schema, ["polars_filter"]), "build", catalogs=catalog)
        assert "ST01" in result.codes() and not result.ok
    mutated = copy.deepcopy(raw)
    mutated["data_schemas"]["amr_data"]["tier2"] = {"steps": [{"action": {"a": 1}}]}
    assert "ST01" in check(mutated, catalogs).codes()
    result = check(broken(raw, JOIN_STEP + ("action",), ["polars_join"]), catalogs, True)
    assert "ST01" in result.codes()


def test_a_join_step_whose_how_is_not_text_ends_with_a_result_and_is_refused(raw, catalogs):
    """The self-join advice (J12) reads `how` as a dictionary key; the step is refused by the parameter check."""
    for graph in (False, True):
        result = check(broken(raw, JOIN_STEP + ("how",), ["inner"]), catalogs, graph)
        assert not result.ok


def test_a_plot_target_that_is_not_text_is_PS02(raw, catalogs):
    """MUTATION W3."""
    for shape in ([], ["AMR_Profile_Joint"], {"a": 1}, 7):
        result = check(broken(raw, first_plot_path(raw) + ("target_dataset",), shape), catalogs)
        assert "PS02" in result.codes() and not result.ok


def test_a_theme_that_is_not_text_is_PS05(raw, catalogs):
    """MUTATION W3."""
    for shape in ([], ["theme_light"], {"a": 1}, 7):
        result = check(broken(raw, first_plot_path(raw) + ("theme",), shape), catalogs)
        assert "PS05" in result.codes() and not result.ok


def test_a_block_engine_that_is_not_text_is_T06(raw, catalogs):
    """MUTATION W6: the engine check of a step read the engine as a set element."""
    for shape in ([], ["python-polars"], {"a": 1}):
        result = check(broken(raw, ("data_schemas", "amr_data", "tier1", "data_engine"), shape), catalogs)
        assert "T06" in result.codes() and not result.ok


NAME_SHAPES = [[["identity"]], [{"a": 1}], ["identity", ["x"]], [5], [None], [True]]
CAST = {"action": "polars_cast", "columns": None, "dtype": "Int32"}
CUM = {"action": "polars_cum_sum", "columns": None}


def put_step(raw, place, step):
    out = copy.deepcopy(raw)
    if place == "table_tier1":
        out["data_schemas"]["amr_data"]["tier1"]["steps"].insert(0, step)
    elif place == "join_tier1":
        out["joins"]["AMR_Profile_Joint"]["tier1"]["steps"].insert(0, step)
    elif place == "tier2":
        out["data_schemas"]["amr_data"]["tier2"] = {"steps": [step]}
    elif place == "metadata_tier1":
        out["metadata_schema"]["tier1"]["steps"].insert(0, step)
    else:
        plot = out
        for key in first_plot_path(out):
            plot = plot[key]
        plot.setdefault("tier3", {"steps": []})["steps"].insert(0, step)
    return out


@pytest.mark.parametrize("place", ["table_tier1", "join_tier1", "tier2", "plot_tier3", "metadata_tier1"])
@pytest.mark.parametrize("shape", NAME_SHAPES, ids=repr)
@pytest.mark.parametrize("template", [CAST, CUM], ids=["cast", "cum_sum"])
def test_a_cast_or_cumulative_sum_with_columns_that_are_not_text_is_refused(raw, catalogs, template, shape, place):
    """MUTATION W7: the element check of a list of names is removed from `step_problems`."""
    step = dict(template, columns=copy.deepcopy(shape))
    result = check(put_step(raw, place, step), catalogs, graph=place == "join_tier1")
    assert not result.ok
    assert any(p.code == "ST10" and "column name" in p.text() for p in result.problems), result.problems


def _name_list_parameters(catalogs):
    return [(action, name) for action, schema in sorted(catalogs["actions"].items())
            for name, definition in schema.get("params", {}).items()
            if definition.get("widget") == "column_selector" and definition.get("multi")]


def test_every_list_of_names_parameter_of_every_action_refuses_a_non_text_element(catalogs):
    """Every registered action, every parameter declared as a list of column names: the five wrong elements are ST10, a list of text is sound."""
    from utils.ui_schema import step_problems
    found = _name_list_parameters(catalogs)
    assert len(found) >= 40
    for action, name in found:
        schema = catalogs["actions"][action]
        for bad in ([["x"]], [{"a": 1}], [5], [None], [True], ["a", ["b"]]):
            problems = step_problems(action, {"action": action, name: bad}, schema)
            assert any(p.code == "ST10" and p.param == name and "column name" in p.text() for p in problems), (action, name, bad)
        good = step_problems(action, {"action": action, name: ["a", "b"]}, schema)
        assert not [p for p in good if p.param == name], (action, name, good)


@pytest.mark.parametrize("value", [[1, 2], ["a"], [1.5, True]])
def test_the_values_of_a_filter_stay_a_list_of_any_kind(catalogs, value):
    """`value` of modif_filter is not a list of names: numbers and text stay accepted."""
    from utils.ui_schema import step_problems
    step = {"action": "modif_filter", "column": "x", "op": "in", "value": value, "na": "remove"}
    problems = step_problems("modif_filter", step, catalogs["actions"]["modif_filter"])
    assert not [p for p in problems if p.param == "value"], problems


def test_a_plot_target_that_is_not_text_does_not_count_as_a_read_table(raw, catalogs):
    """`plot_targets` (utils.recipe_tiers) kept the target as a set element."""
    from utils import recipe_tiers
    mutated = copy.deepcopy(raw)
    for group in mutated["analysis_groups"].values():
        for plot in group["plots"].values():
            plot["target_dataset"] = ["AMR_Profile_Joint"]
    assert recipe_tiers.plot_targets(mutated) == set()
    assert "PS02" in check(mutated, catalogs).codes()


def test_a_seeded_fuzz_of_300_shape_corruptions_never_raises(raw, catalogs):
    """Two or three random places of the recipe get a wrong shape; the checker (with and without the graph, profiles build and run) ends with a result."""
    rng = random.Random(20261119)

    def paths(node, prefix=()):
        yield prefix
        if isinstance(node, dict):
            for key, value in node.items():
                yield from paths(value, prefix + (key,))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                yield from paths(value, prefix + (index,))

    places = [p for p in paths(raw) if p]
    for _ in range(300):
        mutated = copy.deepcopy(raw)
        for _ in range(rng.choice([1, 2, 3])):
            try:
                node = mutated
                place = rng.choice(places)
                for key in place[:-1]:
                    node = node[key]
                node[place[-1]] = copy.deepcopy(rng.choice(SHAPES))
            except (KeyError, IndexError, TypeError):
                pass
        for profile, graph in (("build", False), ("build", True), ("run", True)):
            check_recipe(mutated, profile, catalogs=catalogs, graph=_graph_of(mutated) if graph else None)


@pytest.mark.parametrize("item, example", [(2022, '"2022"'), (True, '"True"'), (None, '"None"'), (1.5, '"1.5"')])
def test_a_non_text_scalar_in_a_list_of_names_gets_the_quote_hint(catalogs, item, example):
    """A bare 2022, yes or null is not text in YAML: the fix says to write such a column name in quotes, with the item as the example."""
    from utils.ui_schema import step_problems
    action, name = next(_name_list_parameters(catalogs).__iter__())
    problems = step_problems(action, {"action": action, name: [item]}, catalogs["actions"][action])
    texts = [p.text() for p in problems if p.code == "ST10" and p.param == name]
    assert texts and all("in quotes" in t and example in t for t in texts), texts


@pytest.mark.parametrize("item", [["a"], {"a": 1}])
def test_a_nested_list_or_mapping_in_a_list_of_names_has_no_quote_hint(catalogs, item):
    from utils.ui_schema import step_problems
    action, name = next(_name_list_parameters(catalogs).__iter__())
    problems = step_problems(action, {"action": action, name: [item]}, catalogs["actions"][action])
    texts = [p.text() for p in problems if p.code == "ST10" and p.param == name]
    assert texts and not any("quotes" in t for t in texts), texts
