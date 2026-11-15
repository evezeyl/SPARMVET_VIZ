"""
@deps
provides: function:define_server (HOME's load gate follower, GATE-GAP-1), function:follow_gate, function:gate_notes
consumes: app/src/bootloader.py (recheck_changed_data_analysis_recipes, data_analysis_recipe_gate_version, available/rejected recipes), app/modules/data_analysis_recipe_validator.py (home_advice_entries)
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


def gate_notes(rejected, advices, switched):
    """The notes under the selector: the recipe that was replaced, the recipes that are unavailable and why, the advices."""
    blocks = []
    if switched:
        blocks.append(ui.tags.small(
            f"'{switched[0]}' was open and no longer passes its checks: HOME shows '{switched[1]}' instead.",
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


def define_server(input, output, session, *, bootloader, safe_input, recipe_gate_version):
    """Registers the poll of the gate, the selector follower and the notes output. `recipe_gate_version` is a reactive.Value
    created by server.py (shared state read by `active_cfg`)."""

    @reactive.poll(lambda: (bootloader.recheck_changed_data_analysis_recipes(),
                            bootloader.data_analysis_recipe_gate_version)[1], POLL_SECONDS)
    def _version():
        return bootloader.data_analysis_recipe_gate_version

    _remembered = reactive.Value(None)   # the last recipe the selector had (it is off the page while Blueprint is open)
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

    @reactive.Effect
    @reactive.event(recipe_gate_version, ignore_init=True)
    def _follow():
        current = safe_input(input, "data_analysis_recipe_id", None)
        with reactive.isolate():
            remembered = _remembered.get()
        choices, selected, switched = follow_gate(bootloader.available_data_analysis_recipes, current, remembered)
        if switched:
            _switched.set(switched)
        elif current in choices:
            _switched.set(None)
        ui.update_select("data_analysis_recipe_id", choices=choices, selected=selected)

    @output
    @render.ui
    def recipe_gate_notes_ui():
        """Reads only the gate version and the switched notice (never the selector it sits under: R4)."""
        recipe_gate_version.get()
        return gate_notes(bootloader.rejected_data_analysis_recipes,
                          getattr(bootloader, "data_analysis_recipe_advices", {}), _switched.get())
