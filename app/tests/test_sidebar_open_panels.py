"""Which left panels are open after the app's own redraw (D-0502): the user's choice is kept (pure logic)."""
from app.modules.sidebar_open_panels import open_panels_after_redraw as f

ALL = ["Info", "Choice", "Filters", "Export"]


def test_first_draw_uses_the_fixed_list():
    assert f(["Choice"], ALL, None, None) == ["Choice"]


def test_answer_not_there_yet_uses_the_fixed_list():
    assert f(["Choice"], ALL, ALL, None) == ["Choice"]


def test_user_opened_a_panel_it_stays_open():
    assert f(["Choice"], ALL, ALL, ["Choice", "Export"]) == ["Choice", "Export"]


def test_user_closed_a_fixed_panel_it_stays_closed():
    assert f(["Choice"], ALL, ALL, []) == []


def test_everything_closed_by_user_is_not_reopened():
    assert f(["Choice", "Info"], ALL, ALL, []) == []


def test_removed_panel_is_not_there():
    assert f(["Choice"], ["Info", "Export"], ALL, ["Choice", "Export"]) == ["Export"]


def test_new_panel_follows_the_fixed_list():
    assert f(["Choice", "Filters"], ["Info", "Choice", "Filters"], ["Info", "Choice"], []) == ["Filters"]


def test_new_panel_not_in_fixed_list_starts_closed():
    assert f(["Choice"], ["Info", "Choice", "Export"], ["Info", "Choice"], ["Choice"]) == ["Choice"]


def test_order_is_the_order_of_the_existing_panels():
    assert f([], ALL, ALL, ["Export", "Info"]) == ["Info", "Export"]


def test_nothing_exists():
    assert f(["Choice"], [], ALL, ["Choice"]) == []
