"""Try an audit step before it is applied: the screen of FLOW-1 of the new Audit flow (ledger D-0650, D-0656, D-0662, D-0669, D-0671).

Two-Category Law (ADR-045): this module holds @render.* and @reactive.* only; the rules (where a step is tried, when a trial ends, the lines of the panel, the words) are in `app/modules/audit_try.py`,
the computation is the engine's (`app/modules/audit_trial.py`, `PlaceTrial`).

WHAT THE USER SEES (Audit mode only). A staged step is TRIED with the one button "Try" of the STEP BAR (`step_try`, drawn by `step_bar_handlers`; the switch `step_kind` says whether it is the staged condition or a column drop, one at a time). The step is written
at the place shown, plus the other places chosen in "Path of the data" when the place shown is among them (all of them, D-0669), and never at a place where the condition does not fit (that is told and
nothing is tried). While the engine counts, a line says so (`app/src/www/trial_counting.js` shows it at the click; the answer comes after). The answer is the fold-out of the bar
(`trial_panel_ui`, a `details` element that can be folded; not a pop-up): the condition, the rows the step removes at each place, each with the mark "User verified" (advice, D-0670), what the places reach (information, never ticks), the
summary "N of M places user verified", the field "Reason" (required), the button "Add to audit pipeline" (FLOW-2, D-0672) and "Discard".
The item shown shows the trial (`home_theater`: the preview, the band, the badge, the figure and Compare read it through the one reader, `audit_place_view`).

ADD (FLOW-2). "Add to audit pipeline" applies the step through `PlaceTrial.apply_trial` (the tables the trial computed are moved into the audit folder when their keys are the keys now wanted: never a second
computation path) and writes it at ALL the places of the trial, also those not marked (D-0669), as committed nodes (the list `audit_pipeline`), each with `user_verified` (and
`verified_at`). Then the trial ends, the staged condition (a condition trial) and the reason are cleared, the session is saved, and one notice says what was added. Anything that goes wrong leaves
NOTHING applied (`apply_trial` is all or nothing for a reader; the committed list and the session file are written only after it succeeded).

THE ONE WAY (FLOW-3, D-0662, D-0663, D-0672). This is the only way to create an audit step: show an item, stage the step, Try, (mark), reason, Add; one step at a time. A staged CONDITION is tried
with the button Try of the step bar when the switch says "Condition on rows"; a COLUMN DROP is tried with the same button when it says "Drop columns": the columns the chooser
does not select, at the Result data (T3) shown (PROVISIONAL, as the old drop was offered) and the other places chosen. Both give the same panel, marks, reason and Add; the panel says "drops N columns"
for a drop. The old entries (the pop-up of "Send to Audit", the button of the lineage panel, the small form of a table no plot reads, the staged cards and the separate Apply) are gone.

WHEN A TRIAL ENDS (`audit_try.end_cause`): her own Discard (no notice); or one plain notice for the first thing that changed: the condition, the places chosen, the mode, the recipe or the data, the applied
steps, a restored session. A drop trial is bound to the columns it was made for (a change of the column chooser or of the staged rows does not end it; the panel names the columns). The browser
session's end empties the trial folder.

NOTHING OF A TRIAL REACHES the session file, the export, the audit folder or a key of a stored audited table: the trial is held here as a reactive value (`trial_state`) that no saver reads, its tables are in
the trial's own folder (`<user data>/audit_trial/<token>`, `PlaceTrial`), and the tried nodes are never written to `home_state`.

R1 to R4 (ui_implementation_contract.md section 14): the Try runs in an effect on the click and writes `trial_state` (with an equality guard on the end); the panel only reads; the panel is an output of its
own, so a trial never draws the Filters form again (the typed value would be lost).

PROVISIONAL (the builder's words and choices; the owner reads them): the labels, the panel and its place, the notices; that the effect computes in the event loop (HOME does the same for a table); the order of
the causes; that a new Try resets the marks even with the same condition and places; that the reason typed is kept as a draft (not lost when a trial ends or is tried again) and cleared only by an Add.

Why the marks and the reason are inputs with the number of the Try in their id (`trial_verified_<serial>_<i>`, `trial_reason_<serial>`): Shiny keeps the last value of an input whose widget left the page; a
new trial with the same ids could read a mark ticked in an OLDER trial before the new widget reports its own value. A new id has no value yet, so a mark is never inherited.

# @deps
# provides: function:define_trial_server, output:trial_panel_ui, output:trial_marks_summary_ui, output:trial_add_ui, effect:_try_step (the one button Try of the step bar; it runs _try or _try_drop), effect:_discard, effect:_add, effect:_track_marks, effect:_track_reason, effect:_watch_the_world
# consumes: app/modules/t3_audit_engine.py (rows_built_elsewhere), app/modules/audit_try.py, app/modules/audit_add.py, app/modules/audit_trial.py (PlaceTrial through the callers' `get_trial`, TrialRefused, now_iso), app/modules/audit_places.py (nodes_signature), app/modules/notification_utils.py, libs/utils/src/utils/key_drop.py (DropGate: the refusal of a key drop by place at Try)
# consumed_by: app/handlers/home_theater.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/rules/ui_implementation_contract.md#14, .claude/knowledge/decision_ledger.md (D-0650, D-0656, D-0662, D-0669, D-0671)
# @end_deps
"""
from __future__ import annotations

import dataclasses
from typing import Callable, Optional

from shiny import reactive, render, ui

from app.modules.frame_widths import HOME as HOME_SPACE
from app.modules.audit_add import (ADD_LABEL, REASON_LABEL, REASON_PLACEHOLDER, VERIFIED_LABEL, VERIFIED_LEGEND, added_notice, can_add, marks_summary, stamp_marks)
from app.modules.audit_places import nodes_signature
from app.modules.audit_shown import request_to_show
from app.modules.audit_trial import TrialRefused, now_iso
from app.modules.step_bar import fold_summary, kind_of_input
from app.modules.audit_try import (DISCARD_LABEL, KIND_DROP, KIND_FILTER, NO_CONDITION, TrialRecord, condition_lines, drop_condition_lines, drop_fit_problem, drops_from_selection, end_cause, fit_problem, panel_model,
                                   trial_has_state, trial_places, tried_drop_nodes, tried_nodes, world_of)
from app.modules.notification_utils import make_notifier
from app.modules.plan_composer import PlanComposerBug
from app.modules.t3_audit_engine import BUILT_ELSEWHERE_LINE, rows_built_elsewhere
from utils import key_drop


def define_trial_server(input, output, session, *,
                        trial_state, trial_left_original, in_audit, home_state, pending_filters, safe_input,
                        recipe_id: Callable[[], str], recipe_keys: Callable[[], tuple], open_graph, lineage_calc, recipe_plans,
                        shown_place: Callable[[], Optional[str]], committed_nodes: Callable[[], list], columns_at, place_name: Callable[[str], str],
                        get_trial, shown_item=None, restored_steps=None, notification_log=None, current_view_key=None, save_session=None, recipe_raw=None):
    """Register the Try button's effect, the panel and the ends of a trial.

    Parameters (kwargs):
      trial_state           reactive.Value[TrialRecord | None]: the trial that exists (HOME's readers depend on it)
      trial_left_original   reactive.Value[bool]: Compare beside a trial shows the original on the left (reset when a trial ends)
      in_audit()            True in Audit mode (the one function of HOME)
      home_state            reactive.Value of the HOME state (the primary keys and the saved file of a restored session are read; nothing is written)
      pending_filters       reactive.Value[list]: the staged rows of the Filters panel (the condition)
      recipe_id()           the id of the open recipe (raises when none)
      recipe_keys()         (recipe hash, data hash) of the open recipe
      open_graph(), lineage_calc(), recipe_plans()   the recipe graph, the lineage `(Lineage | None, reason)` and the engine's plan book
      shown_place()         the place shown (the open plot's node when nothing was shown), or None
      committed_nodes()     the applied audit steps (the nodes of the audit copy HOME reads)
      columns_at(place)     the names and types of the table present at the place in the AUDITED state (no trial), or None
      place_name(node id)   the name of a place as the lineage panel writes it
      get_trial()           the `PlaceTrial` of this browser session
      shown_item            reactive.Value of the place shown (written by "Show" beside a place or a reached item of the panel)
      current_view_key()    the view key of the table shown (the rows a condition is stamped with): a condition built on another table is refused
      restored_steps        reactive.Value: the band's note of a restored session, cleared when the user shows something
      recipe_raw()          the resolved dictionary of the open recipe, for the rule of a key drop at Try (`utils.key_drop`); None: no drop is refused here (the engine still refuses it when it runs)
      save_session(state)   writes the session file as the old Apply writes it and returns a plain warning when it could not (None when saved or when ghost save is off); None: nothing is saved
    """
    _notify = make_notifier(notification_log)
    _counter = [0]                                      # the number of the last Try: the ids of the marks and of the reason of a trial carry it
    trial_marks = reactive.Value({})                    # {place: the time the mark "User verified" was set} of the trial that exists
    reason_text = reactive.Value("")                    # the reason typed so far (a draft kept across trials; cleared by an Add)
    reason_ok = reactive.Value(False)                   # whether the draft can be added (not empty): the button's state (an equality-guarded copy, R3)

    def _chosen() -> list:
        value = safe_input(input, "lineage_chosen", [])
        if isinstance(value, str):
            return [value]
        return [v for v in (value or []) if isinstance(v, str)]

    def _world_now(drop_of: Optional[TrialRecord] = None):
        """What a trial depends on, now. Reads the reactive values it names, so that the watcher below runs again when any of them changes. For the trial of a DROP (`drop_of`: its record) the
        condition is the columns it was made for: the staged rows of the Filters panel are another thing and a change of the column chooser does not end it (PROVISIONAL: the panel names the columns tried)."""
        try:
            rid = recipe_id()
        except Exception:
            rid = ""
        try:
            keys = tuple(recipe_keys())
        except Exception:
            keys = ("?", "?")
        state = home_state.get() if home_state is not None else {}
        world = world_of("audit" if in_audit() else "exploration", rid, keys, list(pending_filters.get()), _chosen(),
                         nodes_signature(committed_nodes()), str((state or {}).get("t3_ghost_file") or ""))
        return dataclasses.replace(world, rows=drop_of.world.rows) if drop_of is not None and drop_of.kind == KIND_DROP else world

    def _end(notice: Optional[str]) -> None:
        """End the trial (empty its folder, forget it) and say why when it was not the user's own Discard. Idempotent: no trial, no notice."""
        with reactive.isolate():
            if trial_state.get() is None:
                return
            try:
                get_trial().discard()
            finally:
                trial_state.set(None)
                trial_left_original.set(False)
                if trial_marks.get():
                    trial_marks.set({})
            if notice:
                _notify(notice, type="warning", duration=10)

    # ── Try ─────────────────────────────────────────────────────────────────────────────────────────────────────
    def _ready_to_try():
        """(graph, lineage) when the path of the data can be read, else None (one plain notice was shown)."""
        try:
            graph = open_graph()
            lineage, why = lineage_calc()
        except Exception as exc:
            _notify(f"The recipe cannot be read, so nothing was tried: {exc}", type="error", duration=10)
            return None
        if lineage is None:
            _notify(f"The path of the data cannot be drawn, so nothing was tried. {why}", type="warning", duration=10)
            return None
        return graph, lineage

    def _compute(kind: str, places, nodes, condition, world) -> None:
        """Run the engine on the tried nodes and keep the answer as THE trial. A failure of the engine is one plain notice and no trial."""
        try:
            result = get_trial().try_step(recipe_id(), committed_nodes(), nodes, recipe_plans())
        except Exception as exc:
            _end(None)
            _notify(f"The trial could not be computed, so nothing was tried: {exc}", type="error", duration=12)
            return
        trial_left_original.set(False)
        _counter[0] += 1
        if trial_marks.get():
            trial_marks.set({})                                         # a new Try never inherits a mark
        trial_state.set(TrialRecord(world, places, tuple(nodes), result, condition, _counter[0], kind))

    @reactive.Effect
    @reactive.event(input.step_try)
    def _try_step():
        """The one button Try of the step bar: the kind of step the switch names (a condition, or a column drop; one at a time, D-0672) is tried."""
        if not in_audit():
            return
        with reactive.isolate():
            kind = kind_of_input(safe_input(input, "step_kind", KIND_FILTER))
        if kind == KIND_DROP:
            _try_drop()
        else:
            _try()

    def _try():
        """Compute the effect of the staged condition at the places, without applying anything. Refusals are one plain sentence and leave the state as it was."""
        rows = list(pending_filters.get())
        if not rows:
            _notify(NO_CONDITION, type="warning", duration=6)
            return
        if current_view_key is not None and rows_built_elsewhere(rows, current_view_key()):
            _notify(BUILT_ELSEWHERE_LINE.format(done="tried"), type="warning", duration=10)
            return
        ready = _ready_to_try()
        if ready is None:
            return
        graph, lineage = ready
        places, problem = trial_places(shown_place(), _chosen(), graph, lineage)
        if problem:
            _notify(problem, type="warning", duration=10)
            return
        problem = fit_problem(rows, places, lineage, columns_at, place_name)
        if problem:
            _notify(problem, type="warning", duration=12)
            return
        state = home_state.get() if home_state is not None else {}
        nodes = tried_nodes(rows, places, (state or {}).get("primary_keys") or [])
        _compute(KIND_FILTER, places, nodes, condition_lines(rows), _world_now())

    def _try_drop():
        """FLOW-3: the column drop is tried like a condition (the one way to create a step). The columns to drop are the ones the column chooser of the table shown does NOT select; the drop is
        written at the places of the trial (the Result data (T3) of a plot is shown, as the drop was always offered; the other places chosen in Path of the data too, D-0669). A column a join
        step later reads as a key is refused BY PLACE (D-0358, D-0371: `utils.key_drop`), with the sentence of the rule, before anything is computed."""
        shown = shown_place()
        if not shown or not str(shown).startswith("T3:"):
            _notify("A column drop is tried on the Result data (T3) of a plot: show a plot's Result data in Path of the data first. Nothing was tried.", type="warning", duration=8)
            return
        names = [name for name, _ in (columns_at(shown) or ())]
        to_drop = drops_from_selection(names, safe_input(input, "preview_col_selector", None))
        if not to_drop:
            _notify("No column is deselected. Uncheck the columns to drop in the column chooser, then press Try. Nothing was tried.", type="warning", duration=6)
            return
        ready = _ready_to_try()
        if ready is None:
            return
        graph, lineage = ready
        places, problem = trial_places(shown, _chosen(), graph, lineage)
        if problem:
            _notify(problem, type="warning", duration=10)
            return
        problem = drop_fit_problem(to_drop, places, lineage, columns_at, place_name)
        if problem:
            _notify(problem, type="warning", duration=12)
            return
        if recipe_raw is not None:
            try:
                gate = key_drop.DropGate(recipe_raw(), recipe_plans())
            except PlanComposerBug:
                return                                                  # the plain notice was shown by `recipe_plans` (an error of the app): nothing is tried
            for place in places:
                refusal = gate.problem(place, to_drop)
                if refusal:
                    _notify(f"{refusal} Nothing was tried.", type="error", duration=10)
                    return
        nodes = tried_drop_nodes(to_drop, places)
        _compute(KIND_DROP, places, nodes, drop_condition_lines(to_drop), _world_now())
        if trial_state.get() is not None:
            _notify("The drop is tried: the answer is in the bar above the table (the effect at each place, the reason and Add to audit pipeline).", type="message", duration=8)

    # ── Discard (her own: no notice) ────────────────────────────────────────────────────────────────────────
    @reactive.Effect
    @reactive.event(input.trial_discard)
    def _discard():
        _end(None)

    # ── The trial ends when what it was made for changes ───────────────────────────────────────────────────────
    @reactive.Effect
    def _watch_the_world():
        # No trial, nothing to watch: in Exploration (and in Audit mode before any Try) `_world_now` is not computed at all. It hashes the data files of the recipe (`recipe_keys`) and
        # reads the whole HOME state, so computing it on every change of the staged rows, the mode or the state slowed every other output of the page. The effect reads `trial_state` first, so it
        # runs again when a trial begins and then watches.
        if trial_state.get() is None:
            return
        with reactive.isolate():
            record = trial_state.get()
        now = _world_now(record)
        with reactive.isolate():
            record = trial_state.get()
            if record is None:
                return
            cause = end_cause(record.world, now)
        if cause:
            _end(cause)

    # ── The end of the browser session empties the trial's folder ───────────────────────────────────────────────
    def _on_ended():
        try:
            get_trial().discard()
        except Exception:
            pass
    try:
        session.on_ended(_on_ended)
    except Exception:
        pass

    # ── "Show" beside a place or a reached item: look at what the trial does THERE without changing the places chosen (a change of the places ends the trial) ──────────────
    @reactive.Effect
    @reactive.event(input.trial_show)
    def _show():
        request = input.trial_show()
        place = request.get("place") if isinstance(request, dict) else None
        if not place or shown_item is None:
            return
        lineage, why = lineage_calc()
        if lineage is None:
            _notify(why or "The path of the data cannot be drawn, so nothing can be shown.", type="warning", duration=8)
            return
        outcome = request_to_show(place, [], open_graph(), lineage)
        if outcome.place is None:
            _notify(outcome.problem, type="warning", duration=8)
            return
        if shown_item.get() != outcome.place:
            shown_item.set(outcome.place)
        if restored_steps is not None and restored_steps.get():
            restored_steps.set(0)

    def _show_button(node: str):
        """A small "Show" beside a place or a reached item. The click goes to the server as an event with a time stamp (a button drawn again must still be heard, R4)."""
        return ui.tags.button("Show", type="button", class_="spv-lin-show ms-2", title="Show this item with the step you are trying",
                              onclick=f"Shiny.setInputValue('trial_show', {{place: {node!r}, t: Date.now()}}, {{priority: 'event'}})")

    # ── The marks "User verified" (advice, D-0670): one tick for each place of the trial ──────────────────────────────────────────────────────────────
    def _places_of(record) -> list:
        return [e.place for e in record.result.effects] if trial_has_state(record) else []

    def _marks_now(record, before: dict) -> dict:
        """{place: the time it was ticked} read from the ticks of THIS trial now (their ids carry its number, so no tick of an older trial is read: a new widget has no value yet, which is not ticked).
        The time of a mark that stays ticked is kept (`before`). Reads the inputs, so the caller decides whether that is a reactive dependency."""
        found: dict = {}
        for number, place in enumerate(_places_of(record)):
            if safe_input(input, f"trial_verified_{record.serial}_{number}", False):
                found[place] = before.get(place) or now_iso()
        return found

    @reactive.Effect
    def _track_marks():
        """Copy the ticks of the panel into `trial_marks` (the summary line reads it). Reads the trial (so it runs again when a trial begins) and the ticks of this trial."""
        record = trial_state.get()
        with reactive.isolate():
            before = dict(trial_marks.get())
        found = _marks_now(record, before) if record is not None else {}
        with reactive.isolate():
            if trial_marks.get() != found:
                trial_marks.set(found)

    _last_typed = {}                                    # {serial of the Try: the last raw value its box reported}

    @reactive.Effect
    def _track_reason():
        """Copy the reason typed into the draft and into `reason_ok` (equality-guarded, R3). The input of THIS trial only (its id carries the number of the Try); before its widget has reported a value the
        draft stands. A box that leaves the page (the user goes to another user space) is reported by Shiny as empty text, and that stale empty value is still there when the user comes back: only a raw value
        that CHANGED while the panel is on the page is the user's, so only that one is kept (the same rule as the reason boxes of the old way; D-0050: a text typed is never dropped silently)."""
        record = trial_state.get()
        if record is None:
            return
        typed = safe_input(input, f"trial_reason_{record.serial}", None)
        space = safe_input(input, "sidebar_nav", HOME_SPACE)
        with reactive.isolate():
            changed = _last_typed.get(record.serial) != typed
            _last_typed[record.serial] = typed
            on_page = space in (None, HOME_SPACE)
            text = reason_text.get() if (typed is None or not (changed and on_page)) else str(typed)
            if text != reason_text.get():
                reason_text.set(text)
            ok = can_add(text)[0]
            if ok != reason_ok.get():
                reason_ok.set(ok)

    # ── Add to audit pipeline (FLOW-2; D-0656, D-0669, D-0672) ────────────────────────────────────────────────────────────────────────────────────────
    @reactive.Effect(priority=1)       # before the trackers of the marks and the reason on purpose: Add reads the ticks and the reason itself, so it never depends on the order the effects run in
    @reactive.event(input.trial_add)
    def _add():
        """Apply the trial (the tables it computed are reused, `PlaceTrial.apply_trial`) and write the step at ALL the places of the trial as committed nodes, each with its mark. Everything is checked
        BEFORE anything is written; a failure leaves the committed list, the session file and the audit folder as they were (the engine's apply is all or nothing for a reader)."""
        if not in_audit():
            return
        record = trial_state.get()
        if record is None or not trial_has_state(record):
            return                                              # no trial (a second click after the first Add lands here: a step is added once)
        reason = str(safe_input(input, f"trial_reason_{record.serial}", "") or "").strip()
        ok, why = can_add(reason)
        if not ok:
            _notify(why, type="warning", duration=8)
            return
        cause = end_cause(record.world, _world_now(record))
        if cause:
            _end(cause)
            return
        applied = list(committed_nodes())
        marks = _marks_now(record, dict(trial_marks.get()))      # the ticks as they are NOW (read here, not from `trial_marks`: a tick and the click on Add can arrive in one flush, before the tracker has run)
        try:
            stored = get_trial().apply_trial(recipe_id(), applied, list(record.nodes), reason, recipe_plans())
        except TrialRefused as exc:
            _end(None)
            _notify(f"{exc}", type="warning", duration=12)
            return
        except Exception as exc:
            _end(None)
            _notify(f"The step could not be added: {exc}. Nothing was applied. Try the step again.", type="error", duration=12)
            return
        added = stamp_marks(stored[len(applied):], marks)
        _end(None)                                              # the trial's folder is empty already; the marks and the trial are forgotten
        state = home_state.get()
        steps = [dict(n) for n in ((state or {}).get("audit_pipeline") or [])] + added
        new_state = {**state, "audit_pipeline": steps, "audit_saves_count": int((state or {}).get("audit_saves_count", 0)) + 1}
        home_state.set(new_state)                               # the count is the saves of the session (the session panel reads it)
        if record.kind == KIND_FILTER:
            pending_filters.set([])                             # the condition was added: the staged rows go (a drop leaves them: they are another step)
        reason_text.set("")
        reason_ok.set(False)
        if save_session is not None:
            warning = save_session(new_state)
            if warning:
                _notify(warning, type="warning", duration=10)
        places = len({n.get("place") for n in added})
        verified = sum(1 for n in added if n.get("user_verified"))
        _notify(added_notice(places, verified), type="message", duration=8)

    # ── The panel ───────────────────────────────────────────────────────────────────────────────────────────────
    @output
    @render.ui
    def trial_panel_ui():
        """The answer of Try, the fold-out of the step bar: the three-state words, the condition, the rows the step removes at each place with its mark "User verified", what the places reach (information), the
        summary of the marks, the reason, "Add to audit pipeline" and Discard. It reads the trial only (R4): the ticks and the reason are inputs it mounts and never reads; the summary and the button are outputs
        of their own."""
        if not in_audit():
            return ui.div()
        safe_input(input, "sidebar_nav", HOME_SPACE)    # the user space: the panel is drawn again when the user comes back to HOME, so that its box holds the draft and its ticks stay (D-0050); never read by the widgets
        record = trial_state.get()
        if record is None:
            return ui.div()
        with reactive.isolate():
            marked = dict(trial_marks.get())
        model = panel_model(record.result, record.condition, place_name, record.kind)
        body = [ui.div(model.heading, class_="spv-trial-heading", role="status")]
        if model.condition:
            body.append(ui.div(*[ui.div(line, class_="spv-trial-line") for line in model.condition], class_="spv-trial-condition"))
        if model.error:
            body.append(ui.div(model.error, class_="spv-trial-error"))
        else:
            body.append(ui.tags.ul(*[ui.tags.li(line, _show_button(node), ui.div(ui.input_checkbox(f"trial_verified_{record.serial}_{number}", VERIFIED_LABEL, value=node in marked), class_="spv-trial-mark"))
                                     for number, (line, node) in enumerate(zip(model.effects, model.effect_nodes))], class_="spv-trial-effects"))
            body.append(ui.div(VERIFIED_LEGEND, class_="spv-trial-note"))
            body.append(ui.output_ui("trial_marks_summary_ui"))
            body.append(ui.div(model.reach_summary, class_="spv-trial-reach"))
            if model.reach_items:
                body.append(ui.tags.details(ui.tags.summary("Show what they reach"), ui.tags.ul(*[ui.tags.li(item, _show_button(node)) for item, node in zip(model.reach_items, model.reach_nodes)], class_="spv-trial-items")))
            with reactive.isolate():
                draft = reason_text.get()
            body.append(ui.input_text(f"trial_reason_{record.serial}", REASON_LABEL, value=draft, placeholder=REASON_PLACEHOLDER, width="100%"))
            body.append(ui.output_ui("trial_add_ui"))
        body.append(ui.input_action_button("trial_discard", DISCARD_LABEL, class_="btn-outline-secondary btn-sm"))
        # a `details` element: the user can fold the answer away to see the table under it; it is drawn open again by every new Try (PROVISIONAL)
        return ui.tags.details(ui.tags.summary(fold_summary(record.kind), class_="spv-trial-summary-line"), ui.div(*body, class_="spv-trial-body"), open=True, class_="spv-trial-panel")

    @output
    @render.ui
    def trial_marks_summary_ui():
        """"N of M places user verified" (D-0670). An output of its own: a tick redraws this line and never the panel (R4). Reads the marks and the trial."""
        record = trial_state.get()
        places = _places_of(record)
        if not places:
            return ui.div()
        marks = trial_marks.get()
        return ui.div(marks_summary(sum(1 for p in places if p in marks), len(places)), class_="spv-trial-summary", role="status")

    @output
    @render.ui
    def trial_add_ui():
        """The button "Add to audit pipeline": enabled only with a reason, and when it is not, one plain line says why (never a silent grey). An output of its own that reads `reason_ok` (an equality-guarded copy of
        "the reason is not empty"), so typing redraws it only when the answer changes, and never the field the user types in (R4)."""
        record = trial_state.get()
        if not in_audit() or not trial_has_state(record):
            return ui.div()
        ok, why = can_add("x" if reason_ok.get() else "")
        button = ui.input_action_button("trial_add", ADD_LABEL, class_="btn-primary btn-sm", disabled=not ok,
                                        title="Applies the step you tried (the tables it computed are reused) and writes it at every place of the trial, with your reason.")
        return ui.div(button, ui.div(why, class_="spv-trial-note", role="status") if why else ui.span(), class_="spv-trial-add")
