"""Exploration filters are cleared, with a notice, when the viewed table changes (D-0311, D-0178) - the REAL effect of the filter handlers.

D-0311: "exploration filters are cleared when the viewed tier changes; they are not kept, not checked and not carried silently". The effect
`_clear_filters_on_view_change` of `define_filter_audit_server` is run on the real HOME readers (`home_harness`). A change of the data
choice, of the source table, of the table the open plot reads (D-0505, D-0506), of the mode and of the recipe clears the staged and the applied rows and tells
the user; a change that leaves nothing to clear tells nothing (no notice for nothing); audited steps are never touched.

MUTATION C1 (the effect never clears): every clearing test fails. MUTATION C2 (the notice is told even for nothing): the quiet tests fail.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filters_cleared_on_view_change.py -q
"""
import pytest
from shiny import reactive

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.home_harness import Home, ViewWorld

AUDIT = ("interactivity_enabled", "t3_sandbox_enabled", "comparison_mode_enabled", "session_management_enabled", "export_enabled")
ROW = {"column": "score", "op": "ge", "value": 4, "dtype": "Int64", "na": "remove"}


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


class Run:
    """HOME with the real filter handlers; `step()` runs the clearing effect once (the first run records the view)."""

    def __init__(self, tmp_path, monkeypatch, **home_args):
        self.home = Home(ViewWorld(tmp_path), monkeypatch, flags=home_args.pop("flags", AUDIT), **home_args)
        self.effect = self.home.filter_handlers(monkeypatch)["_clear_filters_on_view_change"]
        self.step()

    def step(self):
        with reactive.isolate():
            self.effect()

    def stage(self, pending=1, applied=1):
        with reactive.isolate():
            self.home.filters_pending.set([dict(ROW) for _ in range(pending)])
            self.home.filters_applied.set([dict(ROW) for _ in range(applied)])

    def rows(self):
        with reactive.isolate():
            return len(self.home.filters_pending.get()), len(self.home.filters_applied.get())

    def notices(self):
        return [m for _, m in self.home.notes if "filters" in m.lower()]


@pytest.fixture
def run(tmp_path, monkeypatch):
    return Run(tmp_path, monkeypatch)


@pytest.mark.parametrize("change,word", [
    ({"view": "T1"}, "data you view"),
    ({"mode": "audit"}, "Audit mode"),
    ({"subtab": "subtab_p_steps"}, "another table"),    # J with its own tier-3 steps: not the table of p_join
    ({"subtab": "subtab_p_table"}, "another table"),    # T
])
def test_a_change_of_the_view_clears_the_staged_and_the_applied_filters_and_says_so(run, change, word):
    run.stage(pending=2, applied=1)
    run.home.set(**change)
    run.step()
    assert run.rows() == (0, 0), "staged rows not yet applied are cleared too"
    [text] = run.notices()
    assert word in text and "removed" in text and "Audited steps are kept" in text


def test_a_plot_on_the_same_table_keeps_the_staged_and_the_applied_filters_and_says_nothing(run):
    """D-0505, D-0506: the filter belongs to the table. p_join and p_jitter both read J: nothing is cleared, no notice. MUTATION K1 (the plot id
    back in the key): this fails."""
    run.stage(pending=2, applied=1)
    with reactive.isolate():
        before = run.home.readers["current_view_key"]()
    run.home.set(subtab="subtab_p_jitter")
    run.step()
    assert run.rows() == (2, 1) and run.notices() == []
    with reactive.isolate():
        assert run.home.readers["current_view_key"]() == before, "the rows built on p_join still belong to the view of p_jitter"
    run.home.set(subtab="subtab_p_table")
    run.step()
    assert run.rows() == (0, 0) and "reads another table" in run.notices()[0]


def test_on_t2_a_plot_with_its_own_tier_3_steps_still_shares_the_table_of_its_neighbour(run):
    run.home.set(view="T2")
    run.step()
    run.stage()
    run.home.set(subtab="subtab_p_steps")
    run.step()
    assert run.rows() == (1, 1) and run.notices() == []


def test_a_change_of_the_source_table_clears_them(tmp_path, monkeypatch):
    run = Run(tmp_path, monkeypatch, view="SRC", source="T")
    run.stage()
    run.home.set(source="M")
    run.step()
    assert run.rows() == (0, 0) and "source table" in run.notices()[0]


def test_a_change_of_the_source_table_while_not_viewing_the_source_changes_nothing(run):
    """The pick is part of the view only on Source: a pick made earlier does not make T3 another view."""
    run.stage()
    run.home.set(source="M")
    run.step()
    assert run.rows() == (1, 1) and run.notices() == []


def test_switching_back_to_exploration_clears_too(tmp_path, monkeypatch):
    run = Run(tmp_path, monkeypatch, mode="audit")
    run.stage(pending=1, applied=0)          # rows staged in Audit mode wait to be sent; the switch removes them
    run.home.set(mode="exploration")
    run.step()
    assert run.rows() == (0, 0) and "Exploration mode" in run.notices()[0]


def test_a_recipe_change_keeps_its_own_notice(run):
    run.stage()
    run.home.inputs["data_analysis_recipe_id"] = "other_recipe"
    run.step()
    assert run.rows() == (0, 0)
    assert run.notices() and "The filters of the previous recipe were removed" in run.notices()[0]


def test_no_notice_when_there_was_nothing_to_clear(run):
    for change in ({"view": "T1"}, {"mode": "audit"}, {"subtab": "subtab_p_steps"}, {"view": "T2"}):
        run.home.set(**change)
        run.step()
    assert run.notices() == [], "no notice for nothing"


def test_an_unchanged_view_clears_nothing_even_with_filters(run):
    run.stage()
    run.step()
    run.step()
    assert run.rows() == (1, 1) and run.notices() == []


def test_audited_steps_are_not_touched_by_a_view_change(tmp_path, monkeypatch):
    nodes = [{"id": "a", "node_type": "filter_row", "params": dict(ROW), "reason": "r"}]
    run = Run(tmp_path, monkeypatch, home_state={"t3_audit_steps_by_plot": {"subtab_p_join": nodes}})
    run.stage()
    run.home.set(view="T1")
    run.step()
    with reactive.isolate():
        assert run.home.home_state.get()["t3_audit_steps_by_plot"]["subtab_p_join"] == nodes


def test_the_first_view_is_not_a_change(tmp_path, monkeypatch):
    """The effect has run once in `Run.__init__` (it recorded the view); a Run with rows already staged keeps them on its first step."""
    home = Home(ViewWorld(tmp_path), monkeypatch, flags=AUDIT)
    effect = home.filter_handlers(monkeypatch)["_clear_filters_on_view_change"]
    with reactive.isolate():
        home.filters_pending.set([dict(ROW)])
        effect()
        assert len(home.filters_pending.get()) == 1


def test_apply_does_not_exist_in_audit_mode_even_if_called(tmp_path, monkeypatch):
    """P-B4: the form of Audit mode builds audit steps, not previews: `_filter_apply` refuses in Audit mode (the button is not drawn either)."""
    run = Run(tmp_path, monkeypatch, mode="audit")
    apply = run.home.filter_effects["_filter_apply"]
    run.stage(pending=1, applied=0)
    with reactive.isolate():
        apply()
        assert len(run.home.filters_applied.get()) == 0
    run.home.set(mode="exploration")
    run.step()
    run.stage(pending=1, applied=0)
    with reactive.isolate():
        apply()
        assert len(run.home.filters_applied.get()) == 1


def test_the_buttons_follow_the_mode_and_the_view(tmp_path, monkeypatch):
    """Exploration: Apply, no Send to Audit. Audit mode on T3: Send to Audit, no Apply. Audit mode on another view: neither, and one plain line."""
    def buttons(mode, view):
        run = Run(tmp_path / f"{mode}{view}", monkeypatch, mode=mode, view=view)
        with reactive.isolate():
            return str(run.home.outputs["filter_controls_ui"]())
    exploration = buttons("exploration", "T2")
    assert 'id="filter_apply"' in exploration and 'id="filter_send_to_audit"' not in exploration
    assert "never a plot" in exploration
    audit_t3 = buttons("audit", "T3")
    assert 'id="filter_send_to_audit"' in audit_t3 and 'id="filter_apply"' not in audit_t3
    audit_t2 = buttons("audit", "T2")
    assert 'id="filter_send_to_audit"' not in audit_t2 and 'id="filter_apply"' not in audit_t2 and "To create an audit step, view T3." in audit_t2


def test_one_function_says_whether_the_app_is_in_audit_mode(tmp_path, monkeypatch):
    """Review F4: HOME and the filter handlers share `home_theater._in_audit` (audit on AND interactive AND mode "audit"). With the audit flag on and
    interactivity off, a stale "audit" value is Exploration for both. MUTATION I1 (the handlers check the audit flag only): this fails."""
    run = Run(tmp_path, monkeypatch, mode="audit", view="T3", flags=("t3_sandbox_enabled",))
    with reactive.isolate():
        html = str(run.home.outputs["filter_controls_ui"]())
        assert 'id="filter_apply"' in html and 'id="filter_send_to_audit"' not in html
        assert run.home.readers["in_audit"]() is False
