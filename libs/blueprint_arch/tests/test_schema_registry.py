"""
Automated tests for schema_registry.py (ADR-075).

Verifies that:
- Both catalogs load and are non-empty when transformer/viz_factory are installed
- All annotated actions/components from BP-SCHEMA-1 are present
- Every schema entry has required structural fields (label, category, context, params)
- Every param entry has required fields (widget, label, required)
- Widget types are from the declared vocabulary
- Context tags are from the declared vocabulary
- Filtering and search functions return correct subsets

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/blueprint_arch/tests/test_schema_registry.py -v
"""
import pytest

# Trigger decorator registrations in both libraries before testing catalog functions
import transformer.actions        # noqa: F401 — populates ACTION_SCHEMAS
import viz_factory                 # noqa: F401 — populates COMPONENT_SCHEMAS

# Import registries and inject into schema_registry
from transformer.actions.base import ACTION_SCHEMAS
from viz_factory.registry import COMPONENT_SCHEMAS
from blueprint_arch.schema_registry import (
    register,
    get_action_catalog,
    get_component_catalog,
    get_combined_catalog,
    get_actions_for_context,
    get_actions_by_category,
    get_components_for_context,
    search_actions,
)

# Inject the catalogs (required before catalog getters can return data)
register(ACTION_SCHEMAS, COMPONENT_SCHEMAS)

# ── Constants ──────────────────────────────────────────────────────────────────

REQUIRED_SCHEMA_KEYS = {"label", "category", "context", "params"}
REQUIRED_PARAM_KEYS = {"widget", "label", "required"}

VALID_CONTEXTS = {"t1", "t2", "assembly", "plot"}

VALID_WIDGETS = {
    "column_selector", "expression", "enum", "dtype_picker",
    "number", "string", "color", "column_or_literal", "bool",
}

# Actions annotated in BP-SCHEMA-1
ANNOTATED_ACTIONS = [
    "fill_nulls", "drop_nulls", "keep_columns", "drop_columns",
    "strip_whitespace", "filter_range", "add_constant", "filter_eq",
    "rename_columns", "regex_extract", "cast", "coalesce", "label_if",
    "mutate", "sort", "is_in", "join", "unpivot", "explode",
]

# Components annotated in BP-SCHEMA-1
ANNOTATED_COMPONENTS = [
    "geom_boxplot", "geom_point", "geom_line", "geom_bar",
    "geom_histogram", "geom_tile", "labs",
]


# ── Action catalog tests ───────────────────────────────────────────────────────

class TestActionCatalog:

    def test_catalog_loads_and_is_nonempty(self):
        catalog = get_action_catalog()
        assert isinstance(catalog, dict)
        assert len(catalog) >= 19, f"Expected >= 19 actions, got {len(catalog)}"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_annotated_action_present(self, action_name):
        assert action_name in get_action_catalog(), \
            f"'{action_name}' missing from ACTION_SCHEMAS"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_schema_has_required_top_level_keys(self, action_name):
        schema = get_action_catalog()[action_name]
        for key in REQUIRED_SCHEMA_KEYS:
            assert key in schema, f"Action '{action_name}' schema missing key '{key}'"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_context_is_non_empty_list(self, action_name):
        schema = get_action_catalog()[action_name]
        ctx = schema["context"]
        assert isinstance(ctx, list) and len(ctx) > 0, \
            f"Action '{action_name}' must have a non-empty context list"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_context_values_are_valid(self, action_name):
        for ctx in get_action_catalog()[action_name]["context"]:
            assert ctx in VALID_CONTEXTS, \
                f"Action '{action_name}' has unrecognised context '{ctx}'"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_params_is_dict(self, action_name):
        schema = get_action_catalog()[action_name]
        assert isinstance(schema["params"], dict)

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_each_param_has_required_keys(self, action_name):
        for pname, pdef in get_action_catalog()[action_name]["params"].items():
            for key in REQUIRED_PARAM_KEYS:
                assert key in pdef, \
                    f"Action '{action_name}', param '{pname}' missing key '{key}'"

    @pytest.mark.parametrize("action_name", ANNOTATED_ACTIONS)
    def test_each_param_widget_is_valid(self, action_name):
        for pname, pdef in get_action_catalog()[action_name]["params"].items():
            w = pdef.get("widget")
            assert w in VALID_WIDGETS, \
                f"Action '{action_name}', param '{pname}' has unrecognised widget '{w}'"


class TestActionSemanticRules:

    def test_join_is_assembly_context(self):
        schema = get_action_catalog()["join"]
        assert "assembly" in schema["context"]

    def test_explode_is_t2_not_t1(self):
        schema = get_action_catalog()["explode"]
        assert "t2" in schema["context"]
        assert "t1" not in schema["context"]

    def test_cast_dtype_picker_has_options(self):
        schema = get_action_catalog()["cast"]
        dtype_param = schema["params"]["dtype"]
        assert dtype_param["widget"] == "dtype_picker"
        assert "options" in dtype_param
        assert "Int64" in dtype_param["options"]

    def test_sort_has_both_by_and_columns_params(self):
        """sort accepts spec.get('by') or spec.get('columns') — both must appear."""
        params = get_action_catalog()["sort"]["params"]
        assert "by" in params
        assert "columns" in params

    def test_mutate_has_both_column_and_target_column(self):
        """mutate accepts spec.get('column', spec.get('target_column')) — both must appear."""
        params = get_action_catalog()["mutate"]["params"]
        assert "column" in params
        assert "target_column" in params

    def test_filter_eq_has_both_column_and_columns(self):
        """filter_eq tries column then columns[0] fallback — both must appear."""
        params = get_action_catalog()["filter_eq"]["params"]
        assert "column" in params
        assert "columns" in params


# ── Context filtering ──────────────────────────────────────────────────────────

class TestContextFiltering:

    def test_t1_actions_are_nonempty(self):
        t1 = get_actions_for_context("t1")
        assert len(t1) > 0

    def test_t1_actions_all_declare_t1(self):
        for name, schema in get_actions_for_context("t1").items():
            assert "t1" in schema["context"], f"'{name}' returned for t1 but lacks t1"

    def test_assembly_includes_join(self):
        assembly = get_actions_for_context("assembly")
        assert "join" in assembly

    def test_t2_includes_reshaping(self):
        t2 = get_actions_for_context("t2")
        assert "unpivot" in t2
        assert "explode" in t2


# ── Category filtering ─────────────────────────────────────────────────────────

class TestCategoryFiltering:

    def test_cleaning_category(self):
        cleaning = get_actions_by_category("cleaning")
        assert "fill_nulls" in cleaning
        assert "drop_nulls" in cleaning

    def test_filtering_category(self):
        filtering = get_actions_by_category("filtering")
        assert "filter_range" in filtering
        assert "filter_eq" in filtering

    def test_derivation_category(self):
        derivation = get_actions_by_category("derivation")
        assert "mutate" in derivation
        assert "label_if" in derivation
        assert "add_constant" in derivation

    def test_typing_category(self):
        assert "cast" in get_actions_by_category("typing")

    def test_relational_or_assembly_includes_join(self):
        all_names = set(get_action_catalog().keys())
        # join is in some category — just verify it appears somewhere
        assert "join" in all_names


# ── Search ─────────────────────────────────────────────────────────────────────

class TestSearch:

    def test_search_by_exact_name(self):
        assert "cast" in search_actions("cast")

    def test_search_by_tag(self):
        results = search_actions("null")
        assert "fill_nulls" in results
        assert "drop_nulls" in results

    def test_search_case_insensitive(self):
        lower = set(search_actions("regex").keys())
        upper = set(search_actions("REGEX").keys())
        assert lower == upper

    def test_search_empty_string_returns_everything(self):
        assert len(search_actions("")) == len(get_action_catalog())

    def test_search_no_match_returns_empty(self):
        results = search_actions("xyzzy_no_such_action")
        assert len(results) == 0


# ── Component catalog ──────────────────────────────────────────────────────────

class TestComponentCatalog:

    def test_catalog_loads_and_is_nonempty(self):
        catalog = get_component_catalog()
        assert isinstance(catalog, dict)
        assert len(catalog) >= 7

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_annotated_component_present(self, comp_name):
        assert comp_name in get_component_catalog(), \
            f"'{comp_name}' missing from COMPONENT_SCHEMAS"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_component_schema_has_required_keys(self, comp_name):
        schema = get_component_catalog()[comp_name]
        for key in REQUIRED_SCHEMA_KEYS:
            assert key in schema, f"Component '{comp_name}' schema missing key '{key}'"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_component_context_is_plot(self, comp_name):
        schema = get_component_catalog()[comp_name]
        assert "plot" in schema["context"], \
            f"Component '{comp_name}' must declare 'plot' context"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_component_has_allow_extra_params(self, comp_name):
        schema = get_component_catalog()[comp_name]
        assert schema.get("allow_extra_params") is True, \
            f"Component '{comp_name}' must have allow_extra_params: True"

    @pytest.mark.parametrize("comp_name", ANNOTATED_COMPONENTS)
    def test_component_has_wraps(self, comp_name):
        assert "wraps" in get_component_catalog()[comp_name], \
            f"Component '{comp_name}' missing 'wraps' field"

    def test_geom_categories_are_semantic(self):
        semantic = {
            "distribution", "correlation", "comparison", "evolution",
            "part-to-whole", "ranking", "annotation", "uncertainty",
        }
        for name in ANNOTATED_COMPONENTS:
            cat = get_component_catalog()[name].get("category")
            assert cat in semantic, \
                f"Component '{name}' has non-semantic category '{cat}'"

    def test_plot_context_filter(self):
        plot_comps = get_components_for_context("plot")
        for name in ANNOTATED_COMPONENTS:
            assert name in plot_comps


# ── Combined catalog ───────────────────────────────────────────────────────────

class TestCombinedCatalog:

    def test_combined_has_both_keys(self):
        combined = get_combined_catalog()
        assert "actions" in combined
        assert "components" in combined

    def test_combined_matches_individual_catalogs(self):
        combined = get_combined_catalog()
        assert combined["actions"] == get_action_catalog()
        assert combined["components"] == get_component_catalog()
