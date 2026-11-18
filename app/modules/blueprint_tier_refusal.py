# @deps
# provides: function:other_tier_refusal
# consumes: none (pure text, no Shiny, no recipe reading: the caller hands over the tier files it knows)
# consumed_by: app/handlers/blueprint_handlers.py, app/tests/test_blueprint_tier_refusal.py
# doc: .claude/design/recipe_format_spec.md (tier files, D-0250)
# @end_deps
"""The message of Blueprint's Save when a step was made for another tier than the file that is open (PROVISIONAL).

PROVISIONAL (D-0308): the refusal itself and its wording are not chosen by the owner yet; they go to her with the texts to approve.
Until then the message says only what is true today: which step, which tier it was made for, which file is open, that nothing
was saved, which file of that tier the table has (if any) and what the user can really do. It names no control that does not
exist: Blueprint has no button that removes one step and no button that creates a tier file.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

_TIER_WORDS = {"tier1": "tier 1", "tier2": "tier 2"}


def tier_word(tier: str) -> str:
    """`tier2` as a user reads it: `tier 2`."""
    return _TIER_WORDS.get(tier, tier)


def other_tier_refusal(action: str, step_tier: str, file_tier: str, file_name: str, siblings: Optional[dict]) -> str:
    """Why nothing was saved, and what the user can do now.

    `siblings` is what the lineage map knows of the table: for each tier the path of its file (a string), `{"inline": ...}` when the
    tier is written inside the recipe, or nothing when the table has no such tier.
    """
    step_word = tier_word(step_tier)
    where = (siblings or {}).get(step_tier)
    text = (f"The step '{action}' was made for {step_word}, but the file that is open ({file_name}) is {tier_word(file_tier)}: "
            "nothing was saved. ")
    if isinstance(where, str) and where:
        text += (f"This table has a {step_word} file, {Path(where).name}: open it from the lineage rail and add the step there. ")
    elif where:
        text += (f"This table writes its {step_word} inside the recipe, not in a file, and Blueprint saves into files only: "
                 f"change it in the recipe by hand. ")
    else:
        text += (f"This table has no {step_word} file yet. Blueprint cannot create one: add `{step_tier}:` with its file to the "
                 "table in the recipe by hand. ")
    text += "To drop the unsaved step from this screen, click the table node again: the steps of the open file are loaded again."
    return text
