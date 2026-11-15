"""
@deps
provides: function:export_refusal, function:unavailable_export_text (GATE-GAP-1)
consumes: app/modules/data_analysis_recipe_validator.py (rejected_recipe_text)
consumed_by: app/handlers/export_handlers.py (export_bundle_download), app/tests/test_export_refusal.py
doc: .claude/rules/ui_implementation_contract.md#7.2, .claude/knowledge/architecture_decisions.md#ADR-094
@end_deps

The export of a recipe that is not available (GATE-GAP-1): nothing is exported, the user is told plainly why, and gets the same
`EXPORT_NOT_CREATED.txt` as the key check (ui_implementation_contract.md section 7.2, rule 1), never a failed download.

Not available means: the recipe failed the load gate (ADR-094) after its files changed, or it can no longer be read at all (a
missing include, a YAML syntax error) in the moment before the next gate check.
"""
import io
import zipfile

from app.modules.data_analysis_recipe_validator import rejected_recipe_text


def unavailable_export_text(recipe_id: str, error, record: dict | None) -> str:
    """The text of EXPORT_NOT_CREATED.txt for a recipe that is not available: what, why, what to do."""
    why = rejected_recipe_text(recipe_id, record) if record else (
        f"The data analysis recipe '{recipe_id}' cannot be read any more: {error}")
    return (f"The export was not created: the data analysis recipe '{recipe_id}' is not available, so nothing was exported.\n\n"
            f"{why}\n\n"
            "What to do: open the recipe in Blueprint, fix it, and save; when it passes its checks HOME uses it again "
            "and the export works.\n")


def export_refusal(bootloader, recipe_id: str, error, notify) -> bytes | None:
    """The zip (only EXPORT_NOT_CREATED.txt) to hand to the user when the recipe is not available, else None.

    `error` is what reading the recipe raised (None when it read fine); `notify` shows the error notification."""
    record = bootloader.rejected_data_analysis_recipes.get(recipe_id)
    if record is None and error is None:
        return None
    text = unavailable_export_text(recipe_id, error, record)
    notify(f"Export not created: the data analysis recipe '{recipe_id}' is not available (it failed its checks). "
           "Fix it in Blueprint, then export again.", type="error", duration=None)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        archive.writestr("EXPORT_NOT_CREATED.txt", text)
    return buffer.getvalue()
