"""
@deps
provides: function:define_server (HOME's opening of a recipe: build, store, draw once, progress; writes the shared shown_recipe), function:opening_waits, function:ProvenDrawings
consumes: app/modules/opening_build.py (build_plan, run_opening, draw_plot_proof, opening_signature, progress_text), app/src/bootloader.py (reject_after_opening, available_data_analysis_recipes, data_analysis_recipe_gate_version), app/modules/cache_keys.py (load_data_analysis_recipe), app/modules/data_change_notice.py (inputs_changed_during_build_notice); notify (the Alerts notifier) and shown_recipe (a reactive.Value of server.py, read by recipe_gate_handlers) are handed in
consumed_by: app/handlers/home_theater.py
doc: .claude/knowledge/decision_ledger.md (D-0326, D-0343, D-0335, D-0334, D-0336, D-0327), .claude/rules/ui_implementation_contract.md#14, .claude/rules/rules_data_analysis_recipe_structure.md#11
@end_deps

HOME opens a recipe (opening-build, D-0326): the first selection, a change of recipe, a restored session, a change of the data.

One effect, no render: it builds and stores every table, draws every plot once, shows a progress line while it works, and says what it found. A recipe that cannot be
built or drawn is refused through the load gate (`Bootloader.reject_after_opening`) with a plain reason, and HOME falls back as it does for a recipe that fails the gate.
Nothing here writes from a render (`ui_implementation_contract.md` section 14): the effect writes `opening_state` with an equality guard, and the theater reads it.

Rules this file keeps:
- the tables are built here and ONLY here (`dynamic_tabs` waits for the opening of the open recipe, then reads the stored tables);
- the keys are computed once per opening (`view_keys`, HOME's calc) and handed down;
- a later opening with equal keys builds nothing, and does not draw again what was drawn in this process for the same recipe files and data (`ProvenDrawings`);
- the opening blocks the session while it works, as every build in HOME does: the progress line is sent while it runs.
"""
from __future__ import annotations

import threading

from shiny import reactive, ui

from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.data_change_notice import inputs_changed_during_build_notice
from app.modules.opening_build import build_plan, draw_plot_proof, opening_signature, progress_text, run_opening


class ProvenDrawings:
    """The recipes whose plots were all drawn once in this process, by signature (recipe, its files, its data): a later opening with the same signature
    does not draw them again. In memory only: a restart proves again. Thread-safe (sessions run in one process).

    PROVISIONAL (D-0335 says "every plot is drawn once as the proof that it draws" and nothing about a second opening of the same recipe and data): the memory
    exists so that a second session or a second visit does not pay the drawing of every plot again. What it cannot see is a change of the plot code, of the
    palette file or of a library between two openings of the same process; these are fixed for a process, a restart proves again."""

    def __init__(self):
        self._lock = threading.Lock()
        self._signatures: set = set()

    def has(self, signature: tuple) -> bool:
        with self._lock:
            return signature in self._signatures

    def add(self, signature: tuple) -> None:
        with self._lock:
            self._signatures.add(signature)

    def clear(self) -> None:
        with self._lock:
            self._signatures.clear()


PROVEN = ProvenDrawings()


def opening_waits(state: dict, available, recipe_id, signature) -> bool:
    """True while the theater must wait for the opening of the open recipe: the recipe is one HOME can open and its opening has not finished for this
    signature. The ONE definition, read by the theater (`dynamic_tabs`) and by the effect, so they cannot disagree."""
    return bool(recipe_id) and recipe_id in available and (state or {}).get("signature") != signature


def define_server(input, output, session, *, bootloader, orchestrator, viz_factory, safe_input, view_keys, recipe_gate_version, opening_state,
                  notify, proven: ProvenDrawings | None = None, shown_recipe=None):
    """Registers the effect that opens the recipe HOME shows.

    `view_keys`: HOME's calc of the keys of the open recipe (computed once per project state). `recipe_gate_version`: server.py's shared value, read by
    `active_cfg`; it is moved here when a recipe is refused so that HOME falls back at once, not at the next poll of the gate. `opening_state`: a
    `reactive.Value({})` made by the caller and read by the theater; `notify(text, type=, duration=)`: the Alerts notifier. `shown_recipe`: the
    `reactive.Value` of the recipe HOME shows in this session (server.py); the effect writes the recipe it opens before it builds, so that the gate follower
    can name it when the opening refuses it on the first screen, when the selector value has not reached the server (the notice "no longer passes its checks")."""
    memory = proven if proven is not None else PROVEN

    @reactive.Effect
    def _open_recipe():
        recipe_gate_version.get()
        if safe_input(input, "sidebar_nav", "Home") != "Home":
            return
        recipe_id = safe_input(input, "data_analysis_recipe_id", bootloader.get_default_data_analysis_recipe_or_none())
        if not recipe_id or recipe_id not in bootloader.available_data_analysis_recipes:
            return
        try:
            keys = view_keys()
            loaded = load_data_analysis_recipe(orchestrator.data_analysis_recipes_dir / f"{recipe_id}.yaml")
        except Exception:
            return   # the theater shows the error of reading the recipe or its data; nothing is opened from it
        signature = opening_signature(recipe_id, keys)
        with reactive.isolate():
            if shown_recipe is not None and shown_recipe.get() != recipe_id:   # idempotent guard (section 14, R3)
                shown_recipe.set(recipe_id)
            if opening_state.get().get("signature") == signature:
                return
        status, result = "ready", None
        try:
            plan = build_plan(loaded.raw, keys)
            total = len(plan)
            already = memory.has(signature)
            with ui.Progress(min=0, max=max(total, 1)) as bar:
                def progress(tables_done, tables_total, plots_done, plots_total):
                    bar.set(tables_done + plots_done, message=progress_text(recipe_id, tables_done, tables_total, plots_done, plots_total))

                result = run_opening(
                    orchestrator, recipe_id, loaded.raw, keys, bootloader.get_location("user_data") / "anchors",
                    draw=(lambda plot_id, table: None) if already else (lambda plot_id, table: draw_plot_proof(viz_factory, loaded.raw, plot_id, table)),
                    progress=progress, plan=plan)
        except Exception as error:   # a fault of the opening itself, not of the recipe: HOME goes on and builds as it did, and says so
            # PROVISIONAL (no ledger line states what happens when the opening itself stops): HOME goes on, builds what it shows when it is asked, and the text and the
            # duration of the toast are the builder's.
            status = "error"
            notify(f"The opening of '{recipe_id}' stopped: {error}. HOME builds what it shows when it is asked.", type="error", duration=20)
        if result is not None:
            # PROVISIONAL: the texts and the durations (in seconds: 25 a warning, 12 a change of the inputs, 30 a refusal or a stop) of these toasts are the builder's;
            # no ledger line states them (D-0336 asks for a warning in plain words, D-0327 for a plain reason).
            for text in result.warnings:
                notify(text, type="warning", duration=25)
            for text in dict.fromkeys(result.inputs_changed):
                notify("⚠️ " + inputs_changed_during_build_notice(text), type="warning", duration=12)
            if result.problems:
                status = "refused"
                bootloader.reject_after_opening(recipe_id, result.problems, data_files=orchestrator.get_source_files(recipe_id).values())
                if recipe_gate_version.get() != bootloader.data_analysis_recipe_gate_version:   # idempotent guard (section 14, R3)
                    recipe_gate_version.set(bootloader.data_analysis_recipe_gate_version)
                notify(f"The data analysis recipe '{recipe_id}' could not be opened: {result.problems[0]}"
                       + (f" (and {len(result.problems) - 1} more)" if len(result.problems) > 1 else ""), type="error", duration=30)
            else:
                memory.add(signature)
        opening_state.set({"signature": signature, "status": status})
