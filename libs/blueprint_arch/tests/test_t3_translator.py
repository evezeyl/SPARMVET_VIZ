"""
Automated tests for t3_translator.py (ADR-097 decision 4, REPRO-TRANSLATOR-1, issue #47).

Verifies:
- translate_t3_node: eq/ne/gt/ge/lt/le/in/not_in happy paths (all eight T3 filter ops —
  #52 closed the gap that used to leave ne/gt/lt/not_in untranslatable), the eq/ne+list
  auto-promotion mirroring viz_factory's own render-time rule, drop_column,
  and that a genuinely unrecognised op
  still raises UntranslatableNode rather than approximate (defensive — every real T3 op
  is translatable today, `ui_implementation_contract.md §8`).
- translate_plot_steps: ordering, aesthetic_override skipped, one bad node fails the
  whole plot (no partial result).
- build_mode2_recipe: forking mechanics (T2-then-T3 ordering, empty-tier2 case),
  per-plot correctness under propagation (shared fork only when sequences are
  byte-identical, different forks when they diverge), the origin of a fork written
  in its `comment` (recipe format 1 has no `_t3_origin` key), the
  skipped dict for untranslatable/bare-schema/missing-spec plots, and that the
  original raw_config is never mutated.
- The forked recipe of a format 1 recipe is a format 1 recipe: it passes `check_recipe`.

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/blueprint_arch/tests/test_t3_translator.py -v
"""
import copy

import pytest
import yaml

from utils import action_names
from utils.recipe_check import check_recipe, spec
from utils.recipe_factory import minimal_join, minimal_plot, minimal_recipe, minimal_schema, recipe_text

from blueprint_arch.t3_translator import (
    UntranslatableNode,
    translate_t3_node,
    translate_plot_steps,
    build_mode2_recipe,
)


def node(node_type, params, node_id=None, reason=""):
    n = {"node_type": node_type, "params": params, "reason": reason}
    if node_id:
        n["id"] = node_id
    return n


# ── translate_t3_node ────────────────────────────────────────────────────────

class TestTranslateNodeFilterOps:
    def test_eq(self):
        actions = translate_t3_node(node("filter_row", {"column": "country", "op": "eq", "value": "Norway"}))
        assert actions == [{"action": "modif_filter", "column": "country", "op": "eq", "value": "Norway", "na": "remove"}]

    def test_ne(self):
        actions = translate_t3_node(node("filter_row", {"column": "species", "op": "ne", "value": "cat"}))
        assert actions == [{"action": "modif_filter", "column": "species", "op": "ne", "value": "cat", "na": "remove"}]

    def test_gt(self):
        actions = translate_t3_node(node("filter_row", {"column": "identity", "op": "gt", "value": 90}))
        assert actions == [{"action": "modif_filter", "column": "identity", "op": "gt", "value": 90, "na": "remove"}]

    def test_ge(self):
        actions = translate_t3_node(node("filter_row", {"column": "year", "op": "ge", "value": 2024}))
        assert actions == [{"action": "modif_filter", "column": "year", "op": "ge", "value": 2024, "na": "remove"}]

    def test_lt(self):
        actions = translate_t3_node(node("filter_row", {"column": "identity", "op": "lt", "value": 100}))
        assert actions == [{"action": "modif_filter", "column": "identity", "op": "lt", "value": 100, "na": "remove"}]

    def test_le(self):
        actions = translate_t3_node(node("filter_row", {"column": "year", "op": "le", "value": 2024}))
        assert actions == [{"action": "modif_filter", "column": "year", "op": "le", "value": 2024, "na": "remove"}]

    def test_in(self):
        actions = translate_t3_node(
            node("filter_row", {"column": "country", "op": "in", "value": ["Norway", "Sweden"]})
        )
        assert actions == [{"action": "modif_filter", "column": "country", "op": "in", "value": ["Norway", "Sweden"], "na": "remove"}]

    def test_not_in(self):
        actions = translate_t3_node(
            node("filter_row", {"column": "country", "op": "not_in", "value": ["Norway", "Sweden"]})
        )
        assert actions == [{"action": "modif_filter", "column": "country", "op": "not_in", "value": ["Norway", "Sweden"], "na": "remove"}]

    def test_exclusion_row_uses_the_op_literally_no_flip(self):
        """AUDIT-1 (ui_implementation_contract.md §12g.3): the operator is the truth —
        exclusion_row does not get eq flipped to ne."""
        actions = translate_t3_node(node("exclusion_row", {"column": "sample_id", "op": "eq", "value": "S2"}))
        assert actions == [{"action": "modif_filter", "column": "sample_id", "op": "eq", "value": "S2", "na": "remove"}]

    def test_an_unrecognised_op_raises_not_approximate(self):
        """Defensive — every real T3 op (ui_implementation_contract.md §8) is
        translatable today (#52), but a genuinely unknown op must still raise, never
        silently approximate."""
        with pytest.raises(UntranslatableNode):
            translate_t3_node(node("filter_row", {"column": "year", "op": "regex", "value": "2024"}))

    def test_eq_with_list_value_promotes_to_in(self):
        """Mirrors viz_factory.render()'s own render-time auto-promotion — a stored
        node can carry op='eq' with a list value and only be promoted at render time."""
        actions = translate_t3_node(node("filter_row", {"column": "country", "op": "eq", "value": ["Norway", "Sweden"]}))
        assert actions == [{"action": "modif_filter", "column": "country", "op": "in", "value": ["Norway", "Sweden"], "na": "remove"}]

    def test_ne_with_list_value_promotes_to_not_in(self):
        """Same auto-promotion rule, the other direction — ne/list -> not_in."""
        actions = translate_t3_node(node("filter_row", {"column": "country", "op": "ne", "value": ["Norway", "Sweden"]}))
        assert actions == [{"action": "modif_filter", "column": "country", "op": "not_in", "value": ["Norway", "Sweden"], "na": "remove"}]

    def test_missing_column_raises(self):
        with pytest.raises(UntranslatableNode):
            translate_t3_node(node("filter_row", {"op": "eq", "value": "x"}))


class TestTranslateNodeTypesTheValueFromTheDtype:
    """ADR-104 point 7: a step an older panel stored with the value as text is typed at export from the dtype it carries.
    A value that cannot be read is reported, never guessed; a step with no dtype is left as written."""

    @staticmethod
    def step(params):
        return translate_t3_node(node("filter_row", params))[0]

    @pytest.mark.parametrize("dtype, op, value, expected", [
        ("Int64", "ge", "90", 90), ("Int64", "gt", "90.5", 90.5), ("Float64", "lt", "90", 90.0), ("Int64", "eq", 90, 90),
        ("Int64", "in", ["89", "91"], [89, 91]), ("Float64", "not_in", ["89.5"], [89.5]), ("Int64", "between", ["89", "91"], [89, 91]),
        ("Boolean", "in", ["True"], [True]), ("Boolean", "eq", "False", False), ("Boolean", "in", [True], [True]),
        ("String", "eq", "90", "90"), ("String", "in", ["a", "b"], ["a", "b"]),
    ])
    def test_value_is_typed(self, dtype, op, value, expected):
        got = self.step({"column": "c", "op": op, "value": value, "dtype": dtype})["value"]
        assert got == expected and type(got) is type(expected)
        if isinstance(expected, list):
            assert [type(v) for v in got] == [type(v) for v in expected]

    def test_a_date_is_typed_as_a_date(self):
        import datetime
        got = self.step({"column": "d", "op": "in", "value": ["2020-01-02"], "dtype": "Date"})["value"]
        assert got == [datetime.date(2020, 1, 2)]

    def test_the_typed_step_dumps_to_yaml_and_loads_back_the_same(self):
        got = self.step({"column": "d", "op": "in", "value": ["2020-01-02"], "dtype": "Date"})
        assert yaml.safe_load(yaml.safe_dump(got)) == got

    def test_a_step_without_dtype_is_left_as_written(self):
        assert self.step({"column": "c", "op": "ge", "value": "90"})["value"] == "90"

    @pytest.mark.parametrize("dtype, value", [("Int64", "abc"), ("Float64", ""), ("Boolean", "maybe"), ("Date", "31/01/2020")])
    def test_an_unreadable_value_is_reported_in_plain_words(self, dtype, value):
        with pytest.raises(UntranslatableNode) as exc:
            self.step({"column": "year", "op": "eq", "value": value, "dtype": dtype})
        text = str(exc.value)
        assert "year" in text and repr(value) in text and "ComputeError" not in text

    def test_the_dtype_is_not_written_into_the_step(self):
        assert "dtype" not in self.step({"column": "c", "op": "eq", "value": 1, "dtype": "Int64"})


class TestTranslateNodeDropColumn:
    def test_drop_column(self):
        actions = translate_t3_node(node("drop_column", {"column": "notes"}))
        assert actions == [{"action": "polars_drop", "columns": ["notes"]}]

    def test_missing_column_raises(self):
        with pytest.raises(UntranslatableNode):
            translate_t3_node(node("drop_column", {}))


class TestTranslateNodeRemovedType:
    def test_a_removed_step_type_is_not_translatable_and_nothing_special_is_known_about_it(self):
        """AUDIT-RAWYAML-REMOVE-1: the translator has no branch for the removed type; it is an unknown node type like any other."""
        removed = "developer_" + "raw_yaml"
        with pytest.raises(UntranslatableNode, match="not translatable"):
            translate_t3_node(node(removed, {"yaml_fragment": "- action: cast\n  columns: [Year]\n  dtype: String\n"}))


class TestTranslateNodeUnknownType:
    def test_aesthetic_override_raises_if_reached_directly(self):
        """Cosmetic nodes must be filtered by the caller (translate_plot_steps does
        this) — calling translate_t3_node directly on one is a caller error, not a
        silently-ignored no-op."""
        with pytest.raises(UntranslatableNode):
            translate_t3_node(node("aesthetic_override", {"fill_color": "#ff0000"}))

    def test_unknown_node_type_raises(self):
        with pytest.raises(UntranslatableNode):
            translate_t3_node(node("some_future_node_type", {}))


# ── translate_plot_steps ─────────────────────────────────────────────────────

class TestTranslatePlotSteps:
    def test_order_preserved(self):
        nodes = [
            node("filter_row", {"column": "year", "op": "ge", "value": 2023}),
            node("filter_row", {"column": "year", "op": "le", "value": 2025}),
        ]
        actions = translate_plot_steps(nodes)
        assert actions == [
            {"action": "modif_filter", "column": "year", "op": "ge", "value": 2023, "na": "remove"},
            {"action": "modif_filter", "column": "year", "op": "le", "value": 2025, "na": "remove"},
        ]

    def test_aesthetic_override_skipped_not_raised(self):
        nodes = [
            node("aesthetic_override", {"fill_color": "#ff0000"}),
            node("filter_row", {"column": "year", "op": "eq", "value": 2024}),
        ]
        actions = translate_plot_steps(nodes)
        assert actions == [{"action": "modif_filter", "column": "year", "op": "eq", "value": 2024, "na": "remove"}]

    def test_one_bad_node_fails_the_whole_plot(self):
        """Never a partial, silently-incomplete result."""
        nodes = [
            node("filter_row", {"column": "year", "op": "eq", "value": 2024}),
            node("filter_row", {"column": "species", "op": "regex", "value": "cat"}),
        ]
        with pytest.raises(UntranslatableNode):
            translate_plot_steps(nodes)

    def test_empty_list(self):
        assert translate_plot_steps([]) == []


# ── build_mode2_recipe ───────────────────────────────────────────────────────

def _recipe_with_one_join():
    return {
        "analysis_groups": {
            "g1": {"plots": {"p1": {"ui_label": "P1", "target_dataset": "J1"},
                              "p2": {"ui_label": "P2", "target_dataset": "J1"}}}
        },
        "joins": {
            "J1": {"tier1": {"steps": [{"action": "join", "right_ingredient": "x", "on": "id"}]}},
        },
    }


class TestBuildMode2RecipeForking:
    def test_fork_created_and_plot_repointed(self):
        raw = _recipe_with_one_join()
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        new_cfg, skipped = build_mode2_recipe(raw, t3)
        assert skipped == {}
        fork_id = new_cfg["analysis_groups"]["g1"]["plots"]["p1"]["target_dataset"]
        assert fork_id == "J1__t3_p1"
        assert fork_id in new_cfg["joins"]
        # p2 (no T3 steps) keeps the original join untouched
        assert new_cfg["analysis_groups"]["g1"]["plots"]["p2"]["target_dataset"] == "J1"

    def test_t2_then_t3_ordering_appended_after_existing_tier2(self):
        raw = _recipe_with_one_join()
        raw["joins"]["J1"]["tier2"] = {"steps": [{"action": "sort", "columns": ["id"]}]}
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        new_cfg, _ = build_mode2_recipe(raw, t3)
        fork_tier2 = new_cfg["joins"]["J1__t3_p1"]["tier2"]["steps"]
        assert fork_tier2 == [
            {"action": "sort", "columns": ["id"]},
            {"action": "modif_filter", "column": "year", "op": "eq", "value": 2024, "na": "remove"},
        ]

    def test_the_engine_written_in_the_tier2_of_the_join_is_kept_in_the_fork(self):
        raw = _recipe_with_one_join()
        raw["joins"]["J1"]["tier2"] = {"data_engine": "python-polars", "steps": [{"action": "sort", "columns": ["id"]}]}
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        new_cfg, _ = build_mode2_recipe(raw, t3)
        fork_tier2 = new_cfg["joins"]["J1__t3_p1"]["tier2"]
        assert list(fork_tier2) == ["data_engine", "steps"] and fork_tier2["data_engine"] == "python-polars"
        assert [s["action"] for s in fork_tier2["steps"]] == ["sort", "modif_filter"]
        assert raw["joins"]["J1"]["tier2"]["steps"] == [{"action": "sort", "columns": ["id"]}], "the original is not changed"

    def test_empty_original_tier2_fork_is_just_the_translated_actions(self):
        raw = _recipe_with_one_join()   # no tier2 at all on J1
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        new_cfg, _ = build_mode2_recipe(raw, t3)
        assert new_cfg["joins"]["J1__t3_p1"]["tier2"]["steps"] == [
            {"action": "modif_filter", "column": "year", "op": "eq", "value": 2024, "na": "remove"}
        ]
        # tier1 (the shared trunk) is untouched, byte-identical to the original
        assert new_cfg["joins"]["J1__t3_p1"]["tier1"]["steps"] == raw["joins"]["J1"]["tier1"]["steps"]

    def test_the_fork_says_where_it_comes_from_in_its_comment(self):
        raw = _recipe_with_one_join()
        raw["joins"]["J1"]["comment"] = "the note of the author"
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1"),
                     node("drop_column", {"column": "notes"}, node_id="n2")]}
        new_cfg, _ = build_mode2_recipe(raw, t3)
        comment = new_cfg["joins"]["J1__t3_p1"]["comment"]
        assert isinstance(comment, str)
        for part in ("J1", "p1", "n1", "n2", "tier2"):
            assert part in comment
        # the note of the author stays on the join it was written for
        assert new_cfg["joins"]["J1"]["comment"] == "the note of the author"
        assert "the note of the author" not in comment

    def test_a_fork_shared_by_two_plots_names_both(self):
        raw = _recipe_with_one_join()
        shared = node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="shared")
        new_cfg, _ = build_mode2_recipe(raw, {"p1": [dict(shared)], "p2": [dict(shared)]})
        comment = new_cfg["joins"]["J1__t3_p1"]["comment"]
        assert "p1" in comment and "p2" in comment
        assert comment.count("shared") == 1

    def test_a_node_without_an_id_is_not_invented_in_the_comment(self):
        raw = _recipe_with_one_join()
        new_cfg, _ = build_mode2_recipe(raw, {"p1": [node("drop_column", {"column": "notes"})]})
        comment = new_cfg["joins"]["J1__t3_p1"]["comment"]
        assert "J1" in comment and "p1" in comment and "None" not in comment

    def test_the_fork_has_no_key_outside_the_recipe_format(self):
        """`_t3_origin` was an unknown key of a join: recipe format 1 refuses it (check J01)."""
        raw = _recipe_with_one_join()
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        new_cfg, _ = build_mode2_recipe(raw, t3)
        join_keys = spec()["elements"]["join"]
        assert set(new_cfg["joins"]["J1__t3_p1"]) <= set(join_keys["required"]) | set(join_keys["optional"])

    def test_original_raw_config_never_mutated(self):
        raw = _recipe_with_one_join()
        original = copy.deepcopy(raw)
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        build_mode2_recipe(raw, t3)
        assert raw == original

    def test_only_aesthetic_override_nodes_no_fork_needed(self):
        raw = _recipe_with_one_join()
        t3 = {"p1": [node("aesthetic_override", {"fill_color": "#ff0000"})]}
        new_cfg, skipped = build_mode2_recipe(raw, t3)
        assert skipped == {}
        assert new_cfg["analysis_groups"]["g1"]["plots"]["p1"]["target_dataset"] == "J1"
        assert "J1__t3_p1" not in new_cfg["joins"]


class TestBuildMode2RecipeMultiPlotPropagation:
    """ADR-097 decision 4: the fork must be keyed by each plot's own fully-resolved,
    ordered action sequence — never by "which plots received a given shared node"."""

    def test_two_plots_sharing_an_identical_sequence_share_one_fork(self):
        raw = _recipe_with_one_join()
        shared_node = node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="shared")
        t3 = {"p1": [dict(shared_node)], "p2": [dict(shared_node)]}
        new_cfg, skipped = build_mode2_recipe(raw, t3)
        assert skipped == {}
        fork_p1 = new_cfg["analysis_groups"]["g1"]["plots"]["p1"]["target_dataset"]
        fork_p2 = new_cfg["analysis_groups"]["g1"]["plots"]["p2"]["target_dataset"]
        assert fork_p1 == fork_p2
        assert len(new_cfg["joins"]) == 2   # original J1 + exactly one fork, not two

    def test_a_plot_with_an_extra_node_on_top_gets_its_own_fork(self):
        """A shared node plus one plot's own additional node must NOT collapse into
        the shared fork — the resulting sequences genuinely differ."""
        raw = _recipe_with_one_join()
        shared_node = node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="shared")
        extra_node = node("drop_column", {"column": "notes"}, node_id="extra")
        t3 = {"p1": [dict(shared_node)], "p2": [dict(shared_node), extra_node]}
        new_cfg, skipped = build_mode2_recipe(raw, t3)
        assert skipped == {}
        fork_p1 = new_cfg["analysis_groups"]["g1"]["plots"]["p1"]["target_dataset"]
        fork_p2 = new_cfg["analysis_groups"]["g1"]["plots"]["p2"]["target_dataset"]
        assert fork_p1 != fork_p2
        assert len(new_cfg["joins"]) == 3   # original J1 + two distinct forks

    def test_shared_node_across_different_joins_forks_separately(self):
        """A node propagated to 'all plots' spanning different joins must become
        translated actions in multiple different forks, one per join it touches."""
        raw = _recipe_with_one_join()
        raw["joins"]["J2"] = {"tier1": {"steps": [{"action": "join", "right_ingredient": "y", "on": "id"}]}}
        raw["analysis_groups"]["g1"]["plots"]["p2"]["target_dataset"] = "J2"
        shared_node = node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="shared")
        t3 = {"p1": [dict(shared_node)], "p2": [dict(shared_node)]}
        new_cfg, skipped = build_mode2_recipe(raw, t3)
        assert skipped == {}
        fork_p1 = new_cfg["analysis_groups"]["g1"]["plots"]["p1"]["target_dataset"]
        fork_p2 = new_cfg["analysis_groups"]["g1"]["plots"]["p2"]["target_dataset"]
        assert fork_p1 == "J1__t3_p1" and fork_p2 == "J2__t3_p2"
        assert fork_p1 != fork_p2


class TestBuildMode2RecipeSkipped:
    def test_untranslatable_op_is_skipped_not_raised(self):
        raw = _recipe_with_one_join()
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "regex", "value": "2024"}, node_id="n1")]}
        new_cfg, skipped = build_mode2_recipe(raw, t3)
        assert "p1" in skipped
        # Original target_dataset is left completely untouched — never partially forked.
        assert new_cfg["analysis_groups"]["g1"]["plots"]["p1"]["target_dataset"] == "J1"
        assert "J1__t3_p1" not in new_cfg["joins"]

    def test_bare_schema_plot_is_skipped(self):
        raw = _recipe_with_one_join()
        raw["analysis_groups"]["g1"]["plots"]["p1"].pop("target_dataset")  # no target_dataset
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        _, skipped = build_mode2_recipe(raw, t3)
        assert "p1" in skipped
        assert "target_dataset" in skipped["p1"]

    def test_unknown_plot_id_is_skipped(self):
        raw = _recipe_with_one_join()
        t3 = {"does_not_exist": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        _, skipped = build_mode2_recipe(raw, t3)
        assert "does_not_exist" in skipped

    def test_target_dataset_pointing_at_a_bare_schema_not_a_join_is_skipped(self):
        raw = _recipe_with_one_join()
        raw["analysis_groups"]["g1"]["plots"]["p1"]["target_dataset"] = "some_bare_schema"
        t3 = {"p1": [node("filter_row", {"column": "year", "op": "eq", "value": 2024}, node_id="n1")]}
        _, skipped = build_mode2_recipe(raw, t3)
        assert "p1" in skipped

    def test_empty_t3_by_plot(self):
        raw = _recipe_with_one_join()
        new_cfg, skipped = build_mode2_recipe(raw, {})
        assert skipped == {}
        assert new_cfg == raw


class TestBuildMode2RecipeStripsConfigManagerInternals:
    """ConfigManager injects a root-level `plots:` key into raw_config as an internal
    convenience mirror of analysis_groups (config_loader.py comment: "engine detail
    only"). Confirmed live (not a hypothetical): a recipe dumped with this key present
    fails to reload — it trips LEGACY-FLAT-PLOTS-1's fatal check on a root `plots:` key.
    build_mode2_recipe must strip it so its output is always safe to dump and reload."""

    def test_root_plots_key_is_stripped(self):
        raw = _recipe_with_one_join()
        raw["plots"] = {"p1": {"target_dataset": "J1"}}   # ConfigManager-style mirror
        new_cfg, _ = build_mode2_recipe(raw, {})
        assert "plots" not in new_cfg

    def test_stripped_even_with_no_t3_content_at_all(self):
        raw = _recipe_with_one_join()
        raw["plots"] = {}
        new_cfg, _ = build_mode2_recipe(raw, {})
        assert "plots" not in new_cfg


# ── the forked recipe is a recipe in format 1 ────────────────────────────────

# The parameters the translator writes, as the registry declares them (the real registry is checked in
# app/tests/test_writers_emit_format_one.py; this library may not import `transformer`).
_ACTIONS = {
    action_names.FILTER: {
        "params": {
            "column": {"widget": "string", "required": True},
            "op": {"widget": "enum", "options": ["eq", "ne", "gt", "ge", "lt", "le", "in", "not_in", "between"], "required": True},
            "value": {"widget": "any", "required": True},
            "na": {"widget": "enum", "options": ["keep", "remove"], "required": True},
        },
        "rules": [{"when": {"op": ["in", "not_in"]}, "shape": {"value": "list"}},
                  {"when": {"op": ["eq", "ne", "gt", "ge", "lt", "le"]}, "shape": {"value": "scalar"}}],
    },
    action_names.DROP: {"params": {"columns": {"widget": "column_selector", "multi": True, "required": True}}},
}


def _format_one_recipe():
    schemas = {"samples": minimal_schema("data/samples.tsv", {"sample_id": "String", "year": "Int64", "notes": "String"},
                                         entity_key="sample_id")}
    plots = {"per_year": minimal_plot("C", {"x": "year"}), "per_sample": minimal_plot("C", {"x": "sample_id"})}
    return minimal_recipe("tiny", schemas=schemas, joins={"C": minimal_join(["samples"], [])}, plots=plots)


class TestTheForkedRecipeIsFormatOne:
    T3 = {"per_year": [node("filter_row", {"column": "year", "op": "ge", "value": 2023}, node_id="n1", reason="recent years"),
                       node("exclusion_row", {"column": "sample_id", "op": "not_in", "value": ["s2"]}, node_id="n2"),
                       node("drop_column", {"column": "notes"}, node_id="n3")]}

    def test_the_starting_recipe_is_valid(self):
        assert check_recipe(_format_one_recipe(), "run", file_stem="tiny", catalogs={"actions": _ACTIONS}).errors == []

    def test_the_forked_recipe_passes_the_checker(self):
        new_cfg, skipped = build_mode2_recipe(_format_one_recipe(), self.T3)
        assert skipped == {}
        result = check_recipe(new_cfg, "run", file_stem="tiny", catalogs={"actions": _ACTIONS})
        assert result.errors == [] and "actions" in result.coverage

    def test_the_forked_recipe_passes_the_checker_after_it_was_written_and_read(self):
        """The export writes the dictionary as YAML text; the text read back is the same recipe."""
        new_cfg, _ = build_mode2_recipe(_format_one_recipe(), self.T3)
        read_back = yaml.safe_load(recipe_text(new_cfg))
        assert read_back == new_cfg
        assert check_recipe(read_back, "run", file_stem="tiny", catalogs={"actions": _ACTIONS}).errors == []

    def test_the_format_keys_of_the_original_are_kept_in_their_order(self):
        original = _format_one_recipe()
        new_cfg, _ = build_mode2_recipe(original, self.T3)
        assert list(new_cfg) == list(original)
        assert new_cfg["spec_version"] == 1 and new_cfg["id"] == "tiny"
        assert list(new_cfg["analysis_groups"]["main"]["plots"]) == ["per_year", "per_sample"]

    def test_no_removed_key_is_written(self):
        new_cfg, _ = build_mode2_recipe(_format_one_recipe(), self.T3)
        text = recipe_text(new_cfg)
        for old in ("_t3_origin", "final_contract", "output_fields"):
            assert old not in text

    def test_the_mirror_of_the_loader_does_not_reach_the_forked_recipe(self):
        """ConfigManager adds a root-level `plots` to what it loaded; the format refuses that key (T08)."""
        loaded = _format_one_recipe()
        loaded["plots"] = {"per_year": dict(loaded["analysis_groups"]["main"]["plots"]["per_year"])}
        new_cfg, _ = build_mode2_recipe(loaded, self.T3)
        assert check_recipe(new_cfg, "run", file_stem="tiny", catalogs={"actions": _ACTIONS}).errors == []
