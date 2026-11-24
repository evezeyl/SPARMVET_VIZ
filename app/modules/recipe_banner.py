"""The recipe banner of HOME: what its title says and when it is shown (names pass, D-0410, D-0470, D-0474, D-0482).

Pure module (no Shiny, no I/O), so that the rule is tested without starting the app.

Consumed by: `app/handlers/home_theater.py` (the banner above the theater).
If deleted: HOME has no banner rule and each reader would write its own.
"""

# @deps
# provides: module:recipe_banner
# consumes: -
# consumed_by: app/handlers/home_theater.py, app/tests/test_recipe_banner.py
# doc: .claude/knowledge/decision_ledger.md (D-0410, D-0470, D-0474, D-0482)
# @end_deps
from typing import Any, Optional


def recipe_banner_title(info: Any, recipe_id: str, show: bool = True) -> Optional[str]:
    """The text of HOME's recipe banner, or None when no banner is shown.

    The banner shows `info.ui_label`, the one name of the recipe (D-0410); it shows nothing else: `info.subtitle` is a free key of `info`
    that the banner does not read (D-0482). A recipe with no `ui_label` is named by its file name, which is its id (D-0470, ADR-092).
    `show` is `branding.show_recipe_name` of the deployment file, true when the key is absent (D-0474): false means no banner.
    """
    if not show:
        return None
    label = info.get("ui_label") if isinstance(info, dict) else None
    text = str(label).strip() if label else ""
    return text or (recipe_id or None)
