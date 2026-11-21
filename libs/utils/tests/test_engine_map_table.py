"""The table of counts in the engine map page equals the output of the script that generates it from the list (stage 0, D-0458).

The page `.claude/design/engine_boundary_map.md` holds the table between two marker lines. The script `assets/scripts/engine_map_table.py`
prints it from `utils.engine_boundary.PLACES`. A page that was edited by hand, or a list that changed without the page, fails here.

# @deps
# consumes: assets/scripts/engine_map_table.py, .claude/design/engine_boundary_map.md, libs/utils/src/utils/engine_boundary.py
# doc: .claude/knowledge/decision_ledger.md (D-0458)
# @end_deps
"""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PAGE = REPO / ".claude" / "design" / "engine_boundary_map.md"
SCRIPT = REPO / "assets" / "scripts" / "engine_map_table.py"
START, END = "<!-- engine-table:start -->", "<!-- engine-table:end -->"


def script_lines():
    spec = importlib.util.spec_from_file_location("engine_map_table", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.table_lines()


def page_lines(text: str):
    assert text.count(START) == 1 and text.count(END) == 1, "the page needs exactly one pair of table markers"
    inside = text.split(START, 1)[1].split(END, 1)[0]
    return [line for line in inside.strip().splitlines()]


def test_the_table_in_the_page_equals_the_script_output():
    assert page_lines(PAGE.read_text(encoding="utf-8")) == script_lines()


def test_a_changed_count_in_the_page_is_found():
    text = PAGE.read_text(encoding="utf-8")
    first = script_lines()[-1].split("|")[2].strip()   # the first count of the totals row, whatever it is today
    broken = text.replace(f"| All | {first} |", f"| All | {int(first) + 1} |", 1)
    assert broken != text
    assert page_lines(broken) != script_lines()


def test_the_total_is_the_number_of_places():
    from utils.engine_boundary import PLACES
    assert script_lines()[-1].rstrip(" |").split("|")[-1].strip() == str(len(PLACES))
