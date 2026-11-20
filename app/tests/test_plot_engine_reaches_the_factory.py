"""Every place of the app that builds the recipe dictionary for `VizFactory.render` hands over the recipe's `plot_engine`
(ADR-106 V8). The plots of HOME and of Blueprint are rendered from a small dictionary built in the handler, not from the
recipe itself, so a handler that forgets the key would draw with the implemented engine whatever the recipe says.

HOME no longer builds the dictionary itself: HOME's plot, its comparison pane and the opening's proof of drawing all call
`opening_build.plot_render_recipe` (the one place, D-0326), so that function is the builder listed here, and a second test
checks that HOME builds no dictionary of its own and calls it in both places.

The export (`app/handlers/export_handlers.py`) builds the same dictionary and is listed here too. The dictionary carries the
recipe's default engine (`utils.engines.plot_engine_slot`); the plot's own engine travels in its entry under `plots`, and
`PlotEngines.render` alone chooses between the two (D-0237). `test_plot_own_engine_over_recipe.py` holds that choice.

# @deps
# consumes: app/modules/opening_build.py (plot_render_recipe), app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/wrangle_studio.py, libs/viz_factory/src/viz_factory/viz_factory.py
# doc: .claude/knowledge/architecture_decisions.md (ADR-106 V8)
# @end_deps
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDERS = {
    "app/modules/opening_build.py": "return {",   # `plot_render_recipe`: the dictionary of HOME's plot, its comparison pane and the opening's proof of drawing
    "app/handlers/export_handlers.py": "synthetic_data_analysis_recipe = {",
    "app/modules/wrangle_studio.py": "render_data_analysis_recipe = {",
}


def _blocks(text: str, opening: str):
    for match in re.finditer(re.escape(opening), text):
        depth, i = 1, match.end()
        while depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        yield text[match.start():i]


def test_every_recipe_dictionary_built_for_the_factory_carries_the_plot_engine():
    for relative, opening in BUILDERS.items():
        blocks = list(_blocks((ROOT / relative).read_text(encoding="utf-8"), opening))
        assert blocks, f"{relative}: no recipe dictionary found, update this test"
        without = [b for b in blocks if '"plot_engine"' not in b and "plot_engine_slot(" not in b]
        assert without == [], f"{relative}: a recipe dictionary for VizFactory.render has no plot_engine"


def test_home_builds_no_recipe_dictionary_of_its_own_and_hands_the_plot_engine_through_the_one_builder():
    """HOME must call `plot_render_recipe` in the two places it draws a plot (plot and comparison pane) and must not build the dictionary itself:
    a handler that builds its own dictionary escapes the check above."""
    source = (ROOT / "app/handlers/home_theater.py").read_text(encoding="utf-8")
    assert "synthetic_data_analysis_recipe = {" not in source, "HOME builds its own recipe dictionary: use opening_build.plot_render_recipe"
    calls = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "plot_render_recipe"]
    assert len(calls) == 2, "HOME draws a plot in two places (plot and comparison); each must call plot_render_recipe"
    opening = (ROOT / "app/modules/opening_build.py").read_text(encoding="utf-8")
    assert list(_blocks(opening, "return {")) and all("plot_engine_slot(" in b for b in _blocks(opening, "return {")), \
        "plot_render_recipe must hand over the recipe's plot engine"
