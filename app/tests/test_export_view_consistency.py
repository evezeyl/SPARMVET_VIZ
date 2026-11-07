"""What the user sees is what is exported (ADR-089, issue #10, EXPORT-KEYCHECK-1, EXPORT-T3-1).

Two parts, both headless:
- the key check: an export is refused when a data analysis recipe or data file changed after the view was opened;
- the T3 / My view build: T3 > T2 > T1, the same steps as the data preview in HOME.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_view_consistency.py -q
"""
import pytest

from app.handlers.export_handlers import blocked_export_notice, changed_since_view, audited_frame
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
    return w.orch.compute_recipe_keys("tiny")


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
    """T2 keeps A (s1, s2); a My view filter on top can only narrow T2, never bring s3 back."""
    rows = [{"column": "sample_id", "op": "ne", "value": "s1", "dtype": "Utf8"}]
    assert ids(audited_frame(base(world), rows, [])) == ["s2"]
    assert "s3" not in ids(audited_frame(base(world), [], []))


def test_my_view_builds_on_tier1_when_there_are_no_tier2_steps(world):
    world.write_data_analysis_recipe(steps_tier2=[])
    assert ids(audited_frame(base(world), [], [])) == ["s1", "s2", "s3"]


def test_my_view_applies_column_drops_and_ignores_unknown_ones(world):
    out = audited_frame(base(world), [], ["group", "no_such_column"]).collect()
    assert out.columns == ["sample_id"]


def test_my_view_with_a_filter_that_removes_every_row_is_empty_not_an_error(world):
    rows = [{"column": "sample_id", "op": "eq", "value": "nope", "dtype": "Utf8"}]
    assert ids(audited_frame(base(world), rows, [])) == []


def test_my_view_with_a_list_filter_uses_in(world):
    rows = [{"column": "sample_id", "op": "eq", "value": ["s1", "s3"], "dtype": "Utf8"}]
    assert ids(audited_frame(base(world), rows, [])) == ["s1"]    # s3 is not in T2


def test_my_view_without_changes_equals_the_result(world):
    assert ids(audited_frame(base(world), [], [])) == ids(base(world))


# -- what goes into an exported plot: the audited steps, never the exploration -----------------

from app.handlers.export_handlers import plot_content_rules

AUDITED = [{"column": "sample_id", "op": "ne", "value": "s2", "dtype": "Utf8"}]


def test_audited_rows_and_drops_are_exported():
    assert plot_content_rules(AUDITED, ["group"]) == (AUDITED, ["group"])


def test_nothing_audited_means_nothing_is_applied_to_the_export():
    assert plot_content_rules([], []) == ([], [])


def test_the_rule_has_no_way_to_let_exploration_in():
    """The function takes only audited input: exploration filters are not an argument at all."""
    import inspect
    assert list(inspect.signature(plot_content_rules).parameters) == ["audited_rows", "audited_drops"]


def test_the_audited_removal_really_removes_the_rows_from_the_data(world):
    """The user removed a poor quality sample with an audited step: it must not be in the export data."""
    out = audited_frame(base(world), plot_content_rules(AUDITED, [])[0], [])
    assert "s2" not in ids(out) and ids(out) == ["s1"]
