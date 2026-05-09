"""
Automated tests for transformer ACTION_SCHEMAS (ADR-075).

Verifies that @register_action(ui_schema=...) correctly populates ACTION_SCHEMAS,
and that the 19 annotated actions from BP-SCHEMA-1 have structurally valid schemas
with params that match their actual spec.get() call signatures.

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/transformer/tests/test_ui_schemas.py -v
"""
import pytest

# Importing transformer.actions runs its __init__.py, which triggers all
# @register_action decorators and populates ACTION_SCHEMAS.
import transformer.actions  # noqa: F401

from transformer.actions.base import ACTION_SCHEMAS

# ── Constants ──────────────────────────────────────────────────────────────────

ANNOTATED_ACTIONS = [
    "fill_nulls", "drop_nulls", "keep_columns", "drop_columns",
    "strip_whitespace", "filter_range", "add_constant", "filter_eq",
    "rename_columns", "regex_extract", "cast", "coalesce", "label_if",
    "mutate", "sort", "is_in", "join", "unpivot", "explode",
]

VALID_WIDGETS = {
    "column_selector", "expression", "enum", "dtype_picker",
    "number", "string", "color", "column_or_literal", "bool",
}

VALID_CONTEXTS = {"t1", "t2", "assembly"}


# ── Registration ───────────────────────────────────────────────────────────────

class TestRegistration:

    def test_action_schemas_registry_is_populated(self):
        assert isinstance(ACTION_SCHEMAS, dict)
        assert len(ACTION_SCHEMAS) >= 19, \
            f"Expected >= 19 annotated actions, got {len(ACTION_SCHEMAS)}"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_annotated_action_in_registry(self, action_name):
        assert action_name in ACTION_SCHEMAS, \
            f"'{action_name}' missing from ACTION_SCHEMAS; was ui_schema kwarg omitted?"


# ── Structure ──────────────────────────────────────────────────────────────────

class TestSchemaStructure:

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_has_label(self, action_name):
        schema = ACTION_SCHEMAS[action_name]
        assert "label" in schema and isinstance(schema["label"], str)

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_has_category(self, action_name):
        schema = ACTION_SCHEMAS[action_name]
        assert "category" in schema and isinstance(schema["category"], str)

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_has_context_list(self, action_name):
        schema = ACTION_SCHEMAS[action_name]
        ctx = schema.get("context")
        assert isinstance(ctx, list) and len(ctx) > 0, \
            f"'{action_name}' must have a non-empty context list"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_context_values_are_valid(self, action_name):
        for ctx in ACTION_SCHEMAS[action_name]["context"]:
            assert ctx in VALID_CONTEXTS, \
                f"'{action_name}' has unrecognised context tag '{ctx}'"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_has_params_dict(self, action_name):
        schema = ACTION_SCHEMAS[action_name]
        assert "params" in schema and isinstance(schema["params"], dict)

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_each_param_has_widget(self, action_name):
        for pname, pdef in ACTION_SCHEMAS[action_name]["params"].items():
            assert "widget" in pdef, \
                f"'{action_name}.{pname}' param missing 'widget' key"
            assert pdef["widget"] in VALID_WIDGETS, \
                f"'{action_name}.{pname}' has unrecognised widget '{pdef['widget']}'"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_each_param_has_label_and_required(self, action_name):
        for pname, pdef in ACTION_SCHEMAS[action_name]["params"].items():
            assert "label" in pdef, f"'{action_name}.{pname}' missing 'label'"
            assert "required" in pdef, f"'{action_name}.{pname}' missing 'required'"
            assert isinstance(pdef["required"], bool), \
                f"'{action_name}.{pname}' 'required' must be bool"


# ── Semantic correctness — params match function spec.get() calls ──────────────

class TestParamSignatureAlignment:

    def test_join_has_right_ingredient_and_join_keys(self):
        params = ACTION_SCHEMAS["join"]["params"]
        assert "right_ingredient" in params  # manifest-level param
        assert "on" in params
        assert "left_on" in params
        assert "right_on" in params
        assert "how" in params

    def test_join_is_assembly_context(self):
        assert "assembly" in ACTION_SCHEMAS["join"]["context"]

    def test_join_not_in_t1(self):
        assert "t1" not in ACTION_SCHEMAS["join"]["context"]

    def test_unpivot_in_t2_and_assembly(self):
        ctx = ACTION_SCHEMAS["unpivot"]["context"]
        assert "t2" in ctx
        assert "assembly" in ctx

    def test_explode_in_t2_not_t1(self):
        ctx = ACTION_SCHEMAS["explode"]["context"]
        assert "t2" in ctx
        assert "t1" not in ctx

    def test_cast_dtype_picker_options(self):
        dtype_param = ACTION_SCHEMAS["cast"]["params"]["dtype"]
        assert dtype_param["widget"] == "dtype_picker"
        for expected in ("Int64", "Float64", "String", "Boolean", "Date", "Categorical"):
            assert expected in dtype_param["options"], \
                f"cast dtype_picker missing option '{expected}'"

    def test_sort_has_both_by_and_columns_fallback(self):
        """sort: spec.get('by') or spec.get('columns') — both must appear."""
        params = ACTION_SCHEMAS["sort"]["params"]
        assert "by" in params
        assert "columns" in params

    def test_mutate_has_both_column_aliases(self):
        """mutate: spec.get('column', spec.get('target_column')) — both must appear."""
        params = ACTION_SCHEMAS["mutate"]["params"]
        assert "column" in params
        assert "target_column" in params

    def test_filter_eq_has_column_and_columns_fallback(self):
        """filter_eq: spec.get('column', spec.get('columns', ...)[0]) — both must appear."""
        params = ACTION_SCHEMAS["filter_eq"]["params"]
        assert "column" in params
        assert "columns" in params

    def test_label_if_has_all_conditional_params(self):
        params = ACTION_SCHEMAS["label_if"]["params"]
        for key in ("column", "new_column", "predicate", "value", "then", "otherwise"):
            assert key in params, f"label_if missing param '{key}'"

    def test_label_if_predicate_has_options(self):
        pred_param = ACTION_SCHEMAS["label_if"]["params"]["predicate"]
        assert pred_param["widget"] == "enum"
        assert "options" in pred_param
        for op in (">", ">=", "<", "<=", "==", "!="):
            assert op in pred_param["options"]

    def test_coalesce_has_min_items_hint(self):
        params = ACTION_SCHEMAS["coalesce"]["params"]
        assert "columns" in params
        assert params["columns"].get("min_items", 0) >= 2

    def test_filter_range_has_dtype_filter(self):
        col_param = ACTION_SCHEMAS["filter_range"]["params"]["columns"]
        assert col_param.get("dtype_filter") == ["numeric"] or \
               "numeric" in str(col_param.get("dtype_filter", ""))

    def test_rename_columns_has_mapping_and_list_form(self):
        params = ACTION_SCHEMAS["rename_columns"]["params"]
        assert "mapping" in params
        assert "columns" in params
        assert "new_names" in params

    def test_regex_extract_has_all_four_params(self):
        params = ACTION_SCHEMAS["regex_extract"]["params"]
        for key in ("source", "pattern", "target_column", "group"):
            assert key in params, f"regex_extract missing param '{key}'"
