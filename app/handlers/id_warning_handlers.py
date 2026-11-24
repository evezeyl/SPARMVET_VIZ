"""
@deps
provides: function:define_server (the red warning of the ids at the top of HOME, its button "I have read this", the one line of the Export panel), output:id_warning_ui, output:export_id_warning_ui
consumes: app/modules/id_warning.py (warning_lines, read_status, mark_read, quiet_line, log_place_text), app/modules/id_check_run.py (IdCheckRun, through the state the opening writes); id_run_state (a reactive.Value of home_theater.py, written by opening_handlers.py) and safe_input are handed in
consumed_by: app/handlers/home_theater.py
doc: .claude/knowledge/decision_ledger.md (D-0582, D-0585, D-0613), .claude/rules/ui_implementation_contract.md#14, .claude/rules/rules_css_style_spec.md
@end_deps

HOME shows what the checks of the ids found (D-0582): a red warning above the tabs, in every app features file (no flag gates a warning), and a button "I have read
this" that blocks nothing. A click is written in the log of the ids (`utils.id_log.record_read`) and the warning shrinks to one quiet line that can be opened again.

Rules this file keeps (`ui_implementation_contract.md` section 14):
- the two outputs only read: they never write a reactive value (R1); the opening effect writes `id_run_state` with an equality guard;
- the outputs are small and of their own: the warning never draws HOME's tabs or the Export panel's fields again (R4); the Export panel only mounts the slot;
- the buttons set an input with priority `event` and a time stamp, so that a click is always a new value even when the output was drawn again (a plain action
  button that is drawn again starts again at its old count and a second recipe's first click would not be seen).
"""
from __future__ import annotations

from shiny import reactive, render, ui

from app.modules.id_warning import log_place_text, mark_read, quiet_line, read_status, warning_lines

WARNING_ID = "id_warning_ui"
EXPORT_SLOT_ID = "export_id_warning_ui"
TITLE = "Check the ids before you use these results."
READ_BUTTON = "I have read this"


def _click(input_id: str) -> str:
    return f"Shiny.setInputValue('{input_id}', Date.now(), {{priority: 'event'}});"


def define_server(input, output, session, *, bootloader, safe_input, id_run_state):
    """Registers the two outputs and the three clicks. `id_run_state`: HOME's `reactive.Value`, None or a dict
    {signature, recipe_id, recipe_sha256, data_batch_hash, folder, run} written by the opening of a recipe."""
    read_version = reactive.Value(0)        # moves when a click was written, so the outputs read the log again
    reopened_for = reactive.Value(None)     # the signature whose warning the user opened again from the quiet line
    click_problem = reactive.Value(None)    # (signature, text) of a click that could not be written

    def _open_recipe_state():
        """The state of the recipe HOME shows now, or None (nothing opened yet, or the state belongs to another recipe)."""
        state = id_run_state.get()
        if not state:
            return None
        current = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe_or_none())
        return state if state["recipe_id"] == current else None

    def _status(state):
        read_version.get()
        return read_status(state["folder"], state["recipe_id"], state["recipe_sha256"], state["data_batch_hash"])

    @output
    @render.ui
    def id_warning_ui():
        """The warning of the ids at the top of HOME. Reads the opening's state, the read state (the log file) and the open user space; writes nothing."""
        if safe_input(input, "sidebar_nav", "Home") != "Home":
            return ui.div()
        state = _open_recipe_state()
        if state is None:
            return ui.div()
        run = state["run"]
        lines = warning_lines(run)
        if not lines:
            return ui.div()
        status = _status(state)
        signature = state["signature"]
        opened = reopened_for.get() == signature
        if status.read and not opened:
            return ui.div(
                ui.tags.span(quiet_line(status) + " ", class_="spv-id-quiet-text"),
                ui.tags.a("Show again", href="#", class_="spv-id-link", onclick=_click("id_warning_show") + " return false;"),
                class_="spv-id-quiet", role="status")
        problem = click_problem.get()
        problem_text = problem[1] if problem and problem[0] == signature else (
            "The log of the ids cannot be written, so your click cannot be kept." if run.outcome is not None and not run.outcome.written else None)
        action = (ui.tags.a("Hide", href="#", class_="spv-id-link", onclick=_click("id_warning_hide") + " return false;") if status.read else
                  ui.tags.button(READ_BUTTON, type="button", id="id_warning_read", class_="btn btn-primary spv-id-button", onclick=_click("id_warning_read")))
        return ui.div(
            ui.div(TITLE, class_="spv-id-title"),
            ui.tags.ul(*[ui.tags.li(line) for line in lines], class_="spv-id-lines"),
            ui.div(log_place_text(run), class_="spv-id-place"),
            ui.tags.details(ui.tags.summary("Show the log of the ids"), ui.tags.pre(run.log_text or "", class_="spv-id-log"), class_="spv-id-detail",
                            open=opened or None),
            ui.div(problem_text, class_="spv-id-problem") if problem_text else ui.div(),
            ui.div(f"Read on {status.when.split('T')[0]}.", class_="spv-id-place") if status.read else ui.div(),
            ui.div(action, class_="spv-id-actions"),
            class_="spv-id-warning", role="alert")

    @output
    @render.ui
    def export_id_warning_ui():
        """The one line of the Export panel: the bundle holds the log of the ids. Red until the warning was read."""
        if not bootloader.is_enabled("export_enabled"):
            return ui.div()
        state = _open_recipe_state()
        if state is None:
            return ui.div()
        lines = warning_lines(state["run"])
        if not lines:
            return ui.div()
        status = _status(state)
        text = f"This export includes the log of the ids: {len(lines)} warning(s)."
        if status.read:
            return ui.tags.small(f"{text} Read on {status.when.split('T')[0]}.", class_="text-muted d-block mb-1", style="font-size:0.7em;")
        return ui.div(f"{text} Not read yet: see the warning at the top of HOME.", class_="spv-id-export-line")

    @reactive.Effect
    @reactive.event(input.id_warning_read)
    def _on_read():
        state = id_run_state.get()
        if not state:
            return
        outcome = mark_read(state["folder"], state["recipe_id"], state["recipe_sha256"], state["data_batch_hash"])
        if outcome.written:
            click_problem.set(None)
            read_version.set(read_version.get() + 1)
        else:
            click_problem.set((state["signature"], f"Your click could not be kept: {outcome.problem}"))

    @reactive.Effect
    @reactive.event(input.id_warning_show)
    def _on_show():
        state = id_run_state.get()
        if state and reopened_for.get() != state["signature"]:
            reopened_for.set(state["signature"])

    @reactive.Effect
    @reactive.event(input.id_warning_hide)
    def _on_hide():
        if reopened_for.get() is not None:
            reopened_for.set(None)
