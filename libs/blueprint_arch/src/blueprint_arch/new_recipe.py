"""The recipe that Blueprint's "new recipe" form creates (BP-NEW-1, ADR-082 Q2): a draft in recipe format 1.

Pure (no Shiny): the handler reads the form, this function builds the recipe, `utils.recipe_factory.write_recipe`
writes it. A new recipe has no table and no plot yet, so it is valid in profile `build` only (spec section 3); the
author adds the tables, the joins and the plots in Blueprint.

# @deps
# provides: function:new_recipe_draft
# consumes: libs/utils/src/utils/recipe_factory.py (minimal_recipe)
# consumed_by: app/handlers/blueprint_handlers.py (_handle_new_data_analysis_recipe_submit), libs/blueprint_arch/tests/test_new_recipe.py
# doc: .claude/design/recipe_format_spec.md (sections 3, 4, 7.1), .claude/design/recipe_format_work_order.md (W8)
# @end_deps
"""
from utils.recipe_factory import minimal_recipe

FIRST_VERSION = "1.0.0"


def new_recipe_draft(recipe_id: str, label: str, *, description: str, author: str, created: str) -> dict:
    """A recipe with no table, no join and no plot yet; `recipe_id` is also the name of its file.

    `label` is the short name shown to the user (`info.label`; it was `info.name`) and is required by the format.
    `description`, `author` and `created` (a date as text) are written as given, also when empty.
    """
    if not label or not label.strip():
        raise ValueError("a recipe needs a label (its short name): give one, for example the recipe id")
    recipe = minimal_recipe(recipe_id, label=label.strip(), schemas={}, joins={}, plots={})
    recipe["info"].update({
        "description": description,
        "author": author,
        "version": FIRST_VERSION,
        "created": created,
        "tags": [],
    })
    return recipe
