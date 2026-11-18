"""Every place of the app that builds the recipe dictionary for `VizFactory.render` hands over the recipe's `plot_engine`
(ADR-106 V8). The plots of HOME and of Blueprint are rendered from a small dictionary built in the handler, not from the
recipe itself, so a handler that forgets the key would draw with the implemented engine whatever the recipe says.

The export (`app/handlers/export_handlers.py`) builds the same dictionary and is listed here too. The engine is the plot's own
(`plot_engine` of the plot entry, D-0237), else the recipe's: `utils.engines.plot_engine_slot` gives the one to hand over.

# @deps
# consumes: app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/wrangle_studio.py, libs/viz_factory/src/viz_factory/viz_factory.py
# doc: .claude/knowledge/architecture_decisions.md (ADR-106 V8)
# @end_deps
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDERS = {
    "app/handlers/home_theater.py": "synthetic_data_analysis_recipe = {",
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
