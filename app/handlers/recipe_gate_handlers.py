"""
@deps
provides: function:define_server (HOME's load gate follower, GATE-GAP-1), function:tell_tables_rebuilt, function:follow_gate, function:gate_notes
consumes: the shared reactive.Value shown_recipe (made by server.py, also written by app/handlers/opening_handlers.py), app/src/bootloader.py (take_stored_tables_notice: the one-time notice of the cache version, recheck_changed_data_analysis_recipes, data_analysis_recipe_gate_version, available/rejected recipes), app/modules/data_analysis_recipe_validator.py (home_advice_entries)
consumed_by: app/src/server.py
doc: .claude/rules/rules_data_analysis_recipe_structure.md#11, .claude/knowledge/architecture_decisions.md#ADR-094, .claude/rules/ui_implementation_contract.md#14
@end_deps

HOME follows the load gate while the app runs (GATE-GAP-1).

The gate (ADR-094) is re-run for a recipe whose files changed (`Bootloader.recheck_changed_data_analysis_recipes`). This handler
polls it for the session, publishes the gate version (`recipe_gate_version`, read by `active_cfg` and the theater), keeps the
recipe selector in step with it and draws the notes under the selector (what is unavailable and why, advices).

The selector is updated, never rebuilt (`ui_implementation_contract.md` section 14, R4): rebuilding a widget the user is using
wipes what the user just did.
"""
from types import SimpleNamespace

from shiny import reactive, render, ui

from app.modules.data_analysis_recipe_validator import home_advice_entries
from app.modules.notification_utils import make_notifier

POLL_SECONDS = 2


def follow_gate(available, current, remembered):
    """What the recipe selector becomes when the gate changed: (choices, selected, switched).

    `current` is the value of the selector now (None when it is not on the page), `remembered` the last value it had. When
    the recipe that was open is no longer available the selector moves to the first one that is, and `switched` is
    (the recipe that was open, the one shown instead) so that HOME says so; otherwise `switched` is None.
    """
    choices = list(available)
    previous = current or remembered
    if current in choices:
        return choices, current, None
    selected = choices[0] if choices else None
    switched = (previous, selected) if previous and previous not in choices and selected else None
    return choices, selected, switched


def follow_step(available, current, remembered, notice):
    """One poll of the gate: (choices, selected, notice, announce).

    `notice` is (the recipe that was left, the recipe shown instead) or None. It is set when the gate drops the open recipe and
    it stays, over any number of later polls, until the recipe passes its checks again, a newer replacement takes its place, or
    the user picks a recipe (`notice_after_pick`): the user is informed and never silently switched (ADR-104). `announce` is True
    when the notice is new, so that it is written once to the Alerts log."""
    choices, selected, switched = follow_gate(available, current, remembered)
    if switched:
        return choices, selected, switched, switched != notice
    if notice and notice[0] in choices:
        notice = None
    return choices, selected, notice, False


def notice_after_pick(notice, previous, value, available):
    """(notice, announce) after the recipe selector changed from `previous` to `value` (None: off the page).

    Three kinds of change:
    - the recipe the selector held was dropped by the gate and the selector now holds another (the sidebar was built again
      from the new list before the poll saw the change, for example on the way back from Blueprint): that is a replacement
      nobody announced yet, so it becomes the notice (and is announced) unless it already is;
    - the change the app makes itself (to the replacement), or a selector built again: the notice stays and, if the selector
      came back on another recipe, names the one that is open now;
    - a change away from the replacement: the user's own pick, the notice goes."""
    if value is None:
        return notice, False
    if previous is not None and previous != value and previous not in available:
        new = (previous, value)
        return new, new != notice
    if not notice or value == notice[1]:
        return notice, False
    if previous == notice[1]:
        return None, False
    return (notice[0], value), False


def gate_notes_text(switched):
    """The sentence of the notice: the recipe that was left and the one now open."""
    return f"'{switched[0]}' was open and no longer passes its checks: HOME shows '{switched[1]}' instead."


def gate_notes(rejected, advices, switched):
    """The notes under the selector: the recipe that was replaced, the recipes that are unavailable and why, the advices."""
    blocks = []
    if switched:
        blocks.append(ui.tags.small(
            gate_notes_text(switched),
            class_="d-block fw-bold", style="font-size: 0.72rem; color: #d62828;"))
    if rejected:
        blocks.append(ui.div(
            ui.tags.small(f"{len(rejected)} recipe(s) unavailable — failed data or structure check:",
                          class_="text-muted d-block mt-2 mb-1", style="font-size: 0.68rem;"),
            *[ui.div(
                ui.tags.div(name, style="font-size: 0.72rem; font-weight: 600; color: #d62828;"),
                ui.tags.div("; ".join(r["problems"][:2]) + (" ..." if len(r["problems"]) > 2 else ""),
                            style="font-size: 0.68rem;"),
                ui.tags.div(f"Contact: {r['contact']}" if r.get("contact") else "Contact: not configured for this deployment",
                            style="font-size: 0.68rem; color: #6c757d;"),
                style="margin: 2px 0 6px 0; padding: 4px 6px; background: #ffe0e0; border-radius: 3px;")
              for name, r in sorted(rejected.items())],
        ))
    entries = home_advice_entries(advices)
    if entries:
        blocks.append(ui.div(
            ui.tags.small("Advice (these recipes load and run):", class_="text-muted d-block mt-2 mb-1",
                          style="font-size: 0.68rem;"),
            *[ui.div(
                ui.tags.div(name, style="font-size: 0.72rem; font-weight: 600;"),
                *[ui.tags.div(text, style="font-size: 0.68rem;") for text in texts],
                style="margin: 2px 0 6px 0; padding: 4px 6px; background: #fff3cd; border-radius: 3px;")
              for name, texts in entries],
        ))
    return ui.div(*blocks)


def usable_config(bootloader, recipe_id, load):
    """The parsed recipe for HOME's readers (`active_cfg`), or an empty stand-in when the recipe is not usable.

    Not usable: it failed the load gate, or it is broken on disk since the last check (the next poll rejects it). Nothing is
    computed from a failing recipe: every reader of `active_cfg` only reads `.raw_config` and shows its own empty state."""
    if not recipe_id or recipe_id not in bootloader.available_data_analysis_recipes:
        return SimpleNamespace(raw_config={})
    try:
        return load(bootloader.get_location("data_analysis_recipes") / f"{recipe_id}.yaml").config
    except ValueError:
        return SimpleNamespace(raw_config={})


def tell_tables_rebuilt(bootloader, notify) -> bool:
    """Tell the user, once, that the stored tables are rebuilt (D-0240); True when it was told.

    The bootloader gives the sentence to the first session that asks after a start that removed stored tables of another cache
    version, and to nobody after or when nothing was removed. The wording is PROVISIONAL (`cache_keys.STORED_TABLES_REBUILT_NOTICE`).
    """
    text = bootloader.take_stored_tables_notice()
    if text:
        notify(text, type="message", duration=20)
    return bool(text)


def define_server(input, output, session, *, bootloader, safe_input, recipe_gate_version, notification_log=None, shown_recipe=None):
    """Registers the poll of the gate, the selector follower and the notes output. `recipe_gate_version` is a reactive.Value
    created by server.py (shared state read by `active_cfg`); `notification_log` is the Alerts log. `shown_recipe` is the
    `reactive.Value` that holds the recipe HOME shows in this session (server.py): the selector writes it here, and the opening
    of a recipe writes it too (`opening_handlers`), because on the first screen the selector value has not reached the server
    when the opening refuses the recipe, and the notice still has to name the recipe that was left."""
    _notify = make_notifier(notification_log)

    @reactive.poll(lambda: (bootloader.recheck_changed_data_analysis_recipes(),
                            bootloader.data_analysis_recipe_gate_version)[1], POLL_SECONDS)
    def _version():
        return bootloader.data_analysis_recipe_gate_version

    @reactive.Effect
    def _tell_tables_rebuilt():
        """Runs once when the session starts: it reads no input."""
        tell_tables_rebuilt(bootloader, _notify)

    _remembered = shown_recipe if shown_recipe is not None else reactive.Value(None)   # the last recipe HOME showed (the selector is off the page while Blueprint is open)
    _switched = reactive.Value(None)     # (recipe that was open, recipe shown instead) after the gate dropped the open one

    @reactive.Effect
    def _remember_choice():
        v = safe_input(input, "data_analysis_recipe_id", None)
        if v is not None and v in bootloader.available_data_analysis_recipes:
            _remembered.set(v)

    @reactive.Effect
    def _publish_version():
        v = _version()
        if recipe_gate_version.get() != v:   # idempotent guard (ui_implementation_contract.md section 14, R3)
            recipe_gate_version.set(v)

    _last_value = [None]                 # the selector's value at the previous change (plain state, not reactive)

    @reactive.Effect
    @reactive.event(recipe_gate_version, ignore_init=True)
    def _follow():
        current = safe_input(input, "data_analysis_recipe_id", None)
        with reactive.isolate():
            remembered = _remembered.get()
            notice = _switched.get()
        choices, selected, new_notice, announce = follow_step(bootloader.available_data_analysis_recipes, current, remembered,
                                                              notice)
        if new_notice != notice:
            _switched.set(new_notice)
        if announce:
            _notify(gate_notes_text(new_notice), type="warning", duration=10)
        ui.update_select("data_analysis_recipe_id", choices=choices, selected=selected)

    @reactive.Effect
    def _user_picks():
        """The notice goes when the user picks a recipe by hand (the selector changes away from the replacement)."""
        value = safe_input(input, "data_analysis_recipe_id", None)
        previous, _last_value[0] = _last_value[0], value
        with reactive.isolate():
            notice = _switched.get()
        after, announce = notice_after_pick(notice, previous, value, bootloader.available_data_analysis_recipes)
        if after != notice:
            _switched.set(after)
        if announce:
            _notify(gate_notes_text(after), type="warning", duration=10)

    @output
    @render.ui
    def recipe_gate_notes_ui():
        """Reads only the gate version and the switched notice (never the selector it sits under: R4)."""
        recipe_gate_version.get()
        return gate_notes(bootloader.rejected_data_analysis_recipes,
                          getattr(bootloader, "data_analysis_recipe_advices", {}), _switched.get())
