"""What the user sees is what is exported (ADR-089, issue #10, EXPORT-KEYCHECK-1, EXPORT-T3-1).

Two parts, both headless:
- the key check: an export is refused when a data analysis recipe or data file changed after the view was opened;
- the T3 build (the audited table): T3 > T2 > T1, the same steps as the data preview in HOME.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_view_consistency.py -q
"""
import pytest

from app.handlers.export_handlers import blocked_export_notice, changed_since_view
from app.tests.audit_nodes import audited_lf as audited_frame, filter_nodes
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_cache_chain import FILTER_A, FILTER_B
from app.tests.test_tier2_store import Tier2World


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


@pytest.fixture
def world(tmp_path):
    w = Tier2World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])           # T2 keeps group A: s1, s2
    w.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\n")
    return w


def keys(w):
    return w.orch.compute_data_analysis_recipe_keys("tiny")


def base(w):
    return w.orch.materialize_tier2("tiny", "C", w.anchor, keys=keys(w))


def ids(lf):
    return sorted(lf.collect()["sample_id"].to_list())


# -- key check -----------------------------------------------------------------------------

def test_nothing_changed_since_the_view_gives_no_change(world):
    assert changed_since_view(keys(world), keys(world)) == []


def test_no_view_keys_means_no_check():
    assert changed_since_view(None, None) == []


def test_a_data_change_after_the_view_is_reported(world):
    view = keys(world)
    world.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n")
    assert changed_since_view(view, keys(world)) == ["the data files"]


def test_a_change_in_an_included_file_after_the_view_is_reported(world):
    view = keys(world)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_B])
    changes = changed_since_view(view, keys(world))
    assert len(changes) == 1 and changes[0].startswith("the data analysis recipe")


def test_data_analysis_recipe_and_data_changes_are_both_named(world):
    view = keys(world)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_B])
    world.write_data("sample_id\tgroup\ns1\tA\n")
    assert len(changed_since_view(view, keys(world))) == 2


def test_the_refusal_text_explains_what_it_means_and_what_to_do(world):
    view = keys(world)
    world.write_data("sample_id\tgroup\ns1\tA\n")
    now = keys(world)
    text = blocked_export_notice(changed_since_view(view, now), view, now)
    assert "EXPORT NOT CREATED" in text and "the data files" in text
    assert "Reload the page" in text and "never happen silently" in text
    assert view.data_batch_hash in text and now.data_batch_hash in text


# -- T3 > T2 > T1 --------------------------------------------------------------------------

def test_my_view_builds_on_tier2_when_there_are_tier2_steps(world):
    """T2 keeps A (s1, s2); an audited filter on top can only narrow T2, never bring s3 back."""
    rows = [{"column": "sample_id", "op": "ne", "value": "s1", "dtype": "Utf8"}]
    assert ids(audited_frame(base(world), filter_nodes(rows))) == ["s2"]
    assert "s3" not in ids(audited_frame(base(world), []))


def test_my_view_builds_on_tier1_when_there_are_no_tier2_steps(world):
    world.write_data_analysis_recipe(steps_tier2=[])
    assert ids(audited_frame(base(world), [])) == ["s1", "s2", "s3"]


def test_my_view_applies_column_drops_and_refuses_unknown_ones(world):
    """PLOT-TABLE-ORDER-1: a drop of a column that is not in the table is an error (the exported recipe's re-run stops on it too),
    never ignored; the columns that are there are dropped."""
    out = audited_frame(base(world), filter_nodes([], ["group"])).collect()
    assert out.columns == ["sample_id", "not_in_original_data"]   # the marker column of the completion of the ids is a normal column of the table
    with pytest.raises(Exception, match="no_such_column"):
        audited_frame(base(world), filter_nodes([], ["group", "no_such_column"])).collect()


def test_my_view_with_a_filter_that_removes_every_row_is_empty_not_an_error(world):
    rows = [{"column": "sample_id", "op": "eq", "value": "nope", "dtype": "Utf8"}]
    assert ids(audited_frame(base(world), filter_nodes(rows))) == []


def test_my_view_with_a_list_filter_uses_in(world):
    rows = [{"column": "sample_id", "op": "eq", "value": ["s1", "s3"], "dtype": "Utf8"}]
    assert ids(audited_frame(base(world), filter_nodes(rows))) == ["s1"]    # s3 is not in T2


def test_my_view_without_changes_equals_the_result(world):
    assert ids(audited_frame(base(world), [])) == ids(base(world))


# -- what goes into an exported plot: the audited steps, never the exploration -----------------

AUDITED = [{"column": "sample_id", "op": "ne", "value": "s2", "dtype": "Utf8"}]


def test_the_rule_has_no_way_to_let_exploration_in(world):
    """Production code, not a test helper: an exploration filter (the shape `applied_filters` holds: column, op, value, dtype, no node type and no place) cannot reach the
    audited table or the export. The only list the export and HOME read is `place_nodes` of the committed audit steps; a row of that shape is not in it, and the audit copy
    refuses it in plain words instead of running it (so a filter tried in Exploration can never change a plot or an exported table)."""
    from app.modules.audit_places import PLACES_BUCKET, audit_copy_for, place_nodes
    from app.modules.cache_keys import load_data_analysis_recipe
    from utils.audit_copy import AuditCopyError

    exploration_row = {"column": "sample_id", "op": "ne", "value": "s1", "dtype": "Utf8", "na": "remove"}
    by_plot = {PLACES_BUCKET: [exploration_row], "subtab_p": [exploration_row]}
    assert place_nodes(by_plot) == [], "an exploration row is not an audit step: it has no place"
    raw = load_data_analysis_recipe(world.orch.data_analysis_recipes_dir / "tiny.yaml").raw
    with pytest.raises(AuditCopyError, match="refused"):
        audit_copy_for(raw, [exploration_row])
    # and the audited table of the original stays what the recipe builds: nothing was filtered
    assert ids(base(world)) == ["s1", "s2"]


def test_the_audited_removal_really_removes_the_rows_from_the_data(world):
    """The user removed a poor quality sample with an audited step: it must not be in the export data."""
    out = audited_frame(base(world), filter_nodes(AUDITED))
    assert "s2" not in ids(out) and ids(out) == ["s1"]


def test_an_export_whose_audit_steps_cannot_run_is_refused_with_the_reason(world):
    """PLOT-TABLE-ORDER-1: the text of EXPORT_NOT_CREATED.txt gives the reason the audit copy names (the step, its place, the engine's words)
    and the plot whose table showed it; the steps themselves refuse to run on the table (the filter on a column the drop removed)."""
    from app.handlers.export_handlers import blocked_audit_notice
    from app.modules.audit_run import AuditRunError

    nodes = filter_nodes([{"column": "sample_id", "op": "ne", "value": "s2", "dtype": "Utf8"}], ["group"])
    nodes += filter_nodes([{"column": "group", "op": "eq", "value": "A", "dtype": "Utf8"}])
    with pytest.raises(Exception, match="group"):
        audited_frame(base(world), nodes).collect()
    error = AuditRunError("The audit step audit_1a2b3c4d_3 at T3:the_plot cannot be applied: column 'group' is not in the table", "audit_1a2b3c4d_3", "T3:the_plot")
    text = blocked_audit_notice([("the_plot", error)])
    assert text.startswith("EXPORT NOT CREATED") and "'the_plot'" in text
    assert "audit_1a2b3c4d_3" in text and "T3:the_plot" in text and "group" in text and "nothing was exported" in text
