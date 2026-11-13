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
    "polars_fill_null", "polars_drop_nulls", "polars_select", "polars_drop", "polars_str_strip_chars", "modif_filter",
    "polars_rename", "polars_str_extract", "polars_cast", "polars_coalesce", "polars_with_columns", "polars_sort",
    "polars_join", "polars_unpivot", "polars_explode", "polars_group_by", "polars_unique", "step_top_n_other",
]

from utils.ui_schema import WIDGETS as _WIDGETS  # noqa: E402  (one vocabulary for the registries and the form)

VALID_WIDGETS = set(_WIDGETS)

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


# ── Semantic correctness ───────────────────────────────────────────────────────

class TestParamSignatureAlignment:

    def test_join_has_right_ingredient_and_join_keys(self):
        params = ACTION_SCHEMAS["polars_join"]["params"]
        for name in ("right_ingredient", "on", "left_on", "right_on", "how", "maintain_order"):
            assert name in params
        assert params["how"]["required"] and params["maintain_order"]["required"]

    def test_join_is_assembly_context_only(self):
        assert ACTION_SCHEMAS["polars_join"]["context"] == ["assembly"]

    def test_unpivot_in_t2_and_assembly(self):
        ctx = ACTION_SCHEMAS["polars_unpivot"]["context"]
        assert "t2" in ctx and "assembly" in ctx

    def test_explode_in_t2_not_t1(self):
        ctx = ACTION_SCHEMAS["polars_explode"]["context"]
        assert "t2" in ctx and "t1" not in ctx

    def test_cast_dtype_picker_options(self):
        dtype_param = ACTION_SCHEMAS["polars_cast"]["params"]["dtype"]
        assert dtype_param["widget"] == "dtype_picker"
        for expected in ("Int64", "Float64", "String", "Boolean", "Date", "Categorical"):
            assert expected in dtype_param["options"], f"cast dtype_picker missing option '{expected}'"

    def test_sort_has_by_and_the_order_rule_and_no_alias(self):
        params = ACTION_SCHEMAS["polars_sort"]["params"]
        assert "by" in params and params["maintain_order"]["required"]
        assert "columns" not in params

    def test_with_columns_has_named_exprs_and_no_column_alias(self):
        params = ACTION_SCHEMAS["polars_with_columns"]["params"]
        assert "named_exprs" in params and "column" not in params and "target_column" not in params

    def test_filter_has_one_vocabulary(self):
        params = ACTION_SCHEMAS["modif_filter"]["params"]
        assert {"column", "op", "value", "na", "closed"} <= set(params) and "columns" not in params
        assert params["na"]["required"]

    def test_coalesce_writes_its_target(self):
        params = ACTION_SCHEMAS["polars_coalesce"]["params"]
        assert "exprs" in params and params["target_column"]["required"]

    def test_rename_takes_a_mapping(self):
        assert ACTION_SCHEMAS["polars_rename"]["params"]["mapping"]["widget"] == "mapping"
