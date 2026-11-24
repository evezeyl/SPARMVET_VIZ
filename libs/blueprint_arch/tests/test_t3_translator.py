"""
Automated tests for t3_translator.py (ADR-097 decision 4, REPRO-TRANSLATOR-1, issue #47).

Verifies:
- translate_t3_node: eq/ne/gt/ge/lt/le/in/not_in happy paths (all eight T3 filter ops —
  #52 closed the gap that used to leave ne/gt/lt/not_in untranslatable), the eq/ne+list
  auto-promotion mirroring viz_factory's own render-time rule, drop_column,
  and that a genuinely unrecognised op
  still raises UntranslatableNode rather than approximate (defensive — every real T3 op
  is translatable today, `ui_implementation_contract.md §8`).

What is NOT here any more (demo step 7, the third tier went through the audit copy): `translate_plot_steps` and `build_mode2_recipe` (the fork of a join per plot, its
dedup, its `skipped` dict and its `_t3_origin`-style comment) are gone; the steps of every tier are written at their place (`app/modules/audit_places.py`:
`audit_copy_for`, `bake_place_steps`) and those are tested in `app/tests/test_audit_places.py`, `test_audit_places_export.py`, `test_step_order.py` (order, re-run equals the
audit table) and `test_writers_emit_format_one.py` (the baked recipe is a format 1 recipe that loads and runs).

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/blueprint_arch/tests/test_t3_translator.py -v
"""
import copy

import pytest
import yaml

from blueprint_arch.t3_translator import (
    UntranslatableNode,
    translate_t3_node,
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
