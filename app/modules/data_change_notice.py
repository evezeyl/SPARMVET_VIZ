"""
@deps
provides: function:data_files_changed_notice, function:notice_after_data_change, function:inputs_changed_during_build_notice
consumed_by: app/handlers/home_theater.py, app/tests/test_data_change_notice.py
doc: .claude/knowledge/architecture_decisions.md#adr-089
@end_deps

The sentence HOME shows when a source data file changed on disk (STALE-KEY-STORE-1). Pure text, no Shiny.

Before, it said "re-assembling". Nothing re-assembled: HOME computes the keys of its view once and keeps them, so the
tables on screen still come from the earlier files, and the export is refused until the page is reloaded
(`export_handlers.changed_since_view`). The two cases below say what really happens.
"""


def data_files_changed_notice(view_follows_the_data: bool) -> str:
    """What happened, then what the user can do (`Suggestion: ...`).

    view_follows_the_data: True when the keys of the view already describe the files now on disk, which is the case after
    a Data Import in this session (the import raises the refresh that recomputes them); False when the file changed by
    another way (an editor, a pipeline, another session) and the view still holds the keys of the earlier files.
    """
    if view_follows_the_data:
        return ("A source data file of this project changed. The tables and plots are rebuilt from the new files. "
                "Suggestion: check the new values in the data table.")
    return ("A source data file of this project changed after this page was loaded. The tables and plots on screen can "
            "still come from the earlier file, and the export is refused until the page is reloaded. "
            "Suggestion: reload the page (F5) to read the current files.")


def notice_after_data_change(view_data_batch_hash: str | None, new_data_batch_hash: str) -> str:
    """The sentence for a data file that changed: does the view already follow the data on disk?

    `view_data_batch_hash` is the data hash of the keys the view holds (None when they could not be read: then the view is
    taken as behind, the careful answer). The view follows when its keys describe the files now on disk, which is the case
    after a Data Import of this session.
    """
    return data_files_changed_notice(view_data_batch_hash is not None and view_data_batch_hash == new_data_batch_hash)


def inputs_changed_during_build_notice(what_changed: str, suggestion: str = "reload the page (F5) to read the current files") -> str:
    """The sentence for a table that was built while its inputs changed (STALE-KEY-STORE-1): what happened, then a Suggestion.

    `what_changed` is the clause the orchestrator gives (`InputsChanged.text`), for example "the data files changed" or
    "the data analysis recipe can no longer be read (...)". The table was returned but not stored: it can mix the files
    from before and after the change. Nothing is re-read by itself and nothing is blocked. `suggestion` is for a caller
    that is not a page (the gallery previews are drawn by a command).
    """
    return (f"While a table was being built, {what_changed}, so what is shown may not match the files on disk. "
            f"Suggestion: {suggestion}.")
