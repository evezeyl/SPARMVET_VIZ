"""app/handlers/gallery_handlers.py
Gallery Shiny wiring (ADR-037 / ADR-045).

Entry point:
    define_server(input, output, session, *,
                  bootloader, safe_input)

Concern: Gallery filtering and preview rendering only. GALLERY is a static
reference browser (rules_ui_dashboard.md §5, "Gallery Isolation Boundary") —
it has no interactive handoff into any other user space. A prior clone-to-T3
feature was removed 2026-11-08 (F-23/F-22, uml_findings.md): T3 is HOME-only,
audited modifications to a user's own running analysis, never a place to
import recipe content from. GALLERY serves inspiration; a builder who wants
to reuse a recipe fragment copies the YAML by hand into a text file or
BLUEPRINT, same as any other file-based handoff (developer_workflow.md §7).
Two-Category Law (ADR-045): This file contains @render.* and @reactive.* decorators
only. It MUST NOT be imported by non-Shiny contexts.
"""

from __future__ import annotations

# @deps
# provides: function:define_server (gallery_handlers)
# consumes: app/src/bootloader.py (rejected_gallery_examples, gallery_index_status, stale_gallery_pictures), app/modules/gallery_examples.py (example_sample), app/modules/gallery_listing.py, libs/viz_gallery/src/viz_gallery/taxonomy.py (display_axes, filter_panels)
# consumed_by: app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-037, .claude/knowledge/architecture_decisions.md#ADR-045, .claude/rules/rules_ui_dashboard.md#5
# @end_deps

import base64
from pathlib import Path

import polars as pl
from shiny import reactive, render, ui

from app.modules.gallery_examples import example_sample
from app.modules.gallery_listing import (FILTER_AXES, NO_MATCH_TEXT, NOTE_LINES, GalleryListing,
                                         external_links_new_tab, matching_examples, read_listing)
from viz_gallery.taxonomy import display_axes


def define_server(input, output, session, *,
                  bootloader, safe_input, gallery_state):
    """Register all Gallery reactive handlers.

    Parameters
    ----------
    bootloader : Bootloader
        Path Authority instance (ADR-031).
    safe_input : callable
        Shared utility: safe_input(input_obj, key, default) → value.
    gallery_state : reactive.Value[dict]
        What the user left in the Gallery: `ticked` (axis -> terms), `all` (axis -> the Select all box), `applied`
        (axis -> terms, None before the first Apply), `selected` (example id), `dropped` (name of the example an Apply
        removed from the list). It outlives the sidebar shell, which is rebuilt on every switch of space, and the
        shell is built from it (gallery_viewer.build_sidebar_ui). Written only by the effects below, never by a render
        (ui_implementation_contract.md section 14).
    """

    def _listing() -> GalleryListing:
        """What the gallery lists: the stored index minus the examples that failed the check (flags G-a, G-b)."""
        return read_listing(bootloader.get_location("gallery"),
                            bootloader.rejected_gallery_examples, bootloader.gallery_index_status,
                            bootloader.stale_gallery_pictures)

    def _remember(**changes):
        """Merge changes into the Gallery state; idempotent (rule R3), and reads without taking a dependency."""
        with reactive.isolate():
            current = gallery_state.get()
            merged = {**current, **changes}
            if merged != current:
                gallery_state.set(merged)

    # --- Gallery Taxonomy 'Select All' Logic ---

    def _make_select_all_tracker(axis: str):
        """One effect per taxonomy axis; the axes come from the specification data.

        The 'Select all' box ticks or clears its group in the page (app/src/www/gallery_select_all.js), never by a
        server answer: an answer that arrives after the user ticked one term wipes that tick (finding 9). The server
        only remembers the box, so that the rebuilt shell shows it as it was left.
        """
        @reactive.Effect
        def _track_all():
            v = safe_input(input, f"gallery_all_{axis}", None)
            if v is None:
                return
            with reactive.isolate():
                known = gallery_state.get().get("all", {})
            if bool(v) != known.get(axis, True):
                _remember(all={**known, axis: bool(v)})
        return _track_all

    _select_all_trackers = [_make_select_all_tracker(item["axis"]) for item in display_axes()]

    def _make_tick_tracker(axis: str):
        """Keep the ticked terms of one group in the state (so a return to the Gallery shows them again)."""
        @reactive.Effect
        def _track_ticks():
            v = safe_input(input, f"gallery_filter_{axis}", None)
            if v is None:
                return
            with reactive.isolate():
                ticked = gallery_state.get().get("ticked", {})
            if list(v) != ticked.get(axis):
                _remember(ticked={**ticked, axis: list(v)})
        return _track_ticks

    _tick_trackers = [_make_tick_tracker(item["axis"]) for item in display_axes()]

    # --- Gallery Content Resolution (ADR-037) ---
    @reactive.Calc
    def _visible():
        """{id: name} of the examples that match the applied filters (all of them before the first Apply)."""
        return matching_examples(_listing(), gallery_state.get().get("applied"))

    @reactive.Calc
    def _current_rid():
        """The example shown: the dropdown's value when it is in the list, else the one the state holds, else the first.

        The same rule fills the dropdown's first paint (gallery_viewer builds it from the state), so the dropdown and
        every pane agree before the input value has reached the server.
        """
        visible = _visible()
        chosen = safe_input(input, "gallery_example_select", None)
        if chosen in visible:
            return chosen
        if chosen and chosen not in _listing().registry:
            return None  # an example that failed the check, or an unknown id, is never opened
        kept = gallery_state.get().get("selected")
        if kept in visible:
            return kept
        return next(iter(visible), None)

    @reactive.Effect
    def _track_selection():
        """Remember the example the user picked; a pick ends the note about a dropped example."""
        chosen = safe_input(input, "gallery_example_select", None)
        with reactive.isolate():
            if chosen not in _visible() or chosen == gallery_state.get().get("selected"):
                return
        _remember(selected=chosen, dropped=None)

    def _example_dir():
        """The folder of the example shown: the gallery folder of the deployment plus its id. The index holds no path that
        depends on where the gallery sits, so the folder is never read from it."""
        return Path(bootloader.get_location("gallery")) / _current_rid()

    @reactive.Calc
    def _gallery_active_metadata():
        rid = _current_rid()
        if not rid:
            return None
        return _listing().registry.get(rid)

    @output
    @render.ui
    def gallery_preview_img():
        meta = _gallery_active_metadata()
        if not meta:
            if gallery_state.get().get("applied") is not None and not _visible():
                return ui.div(NO_MATCH_TEXT, class_="p-5 text-muted gallery-no-match")
            return ui.div("Select an example to view preview.", class_="p-5 text-muted")
        dropped = gallery_state.get().get("dropped")
        note = (ui.div(f'"{dropped}" does not match the ticked filters, so it is not shown. '
                       "Showing the first example that matches instead.", class_="alert alert-warning m-3 gallery-dropped")
                if dropped else None)

        img_path = _example_dir() / "preview_plot.png"
        if img_path.exists():
            try:
                with open(img_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                return ui.div(
                    note,
                    ui.div(
                        ui.img(src=f"data:image/png;base64,{encoded}",
                               style="max-width: 100%; border: 1px solid #dee2e6; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"),
                        class_="p-3 text-center"
                    ),
                )
            except Exception as e:
                return ui.div(f"Error loading preview: {e}", class_="text-danger")
        return ui.div("No preview image found (.png)", class_="p-5 text-muted")

    @output
    @render.table(index=False)
    def gallery_static_data():
        """Render a clean, left-aligned table without row numbers (ADR-033)."""
        meta = _gallery_active_metadata()
        if not meta:
            return None
        example_dir = _example_dir()
        if (example_dir / "example_data.tsv").exists():
            try:
                # the table the plot is drawn from, read through the declared types (one reader with the picture)
                return example_sample(example_dir)
            except Exception as e:
                # Fallback to an empty DF with error message for debugging
                return pl.DataFrame({"Error": [f"Could not load data: {e}"]})
        return None

    @output
    @render.text
    def gallery_yaml_preview():
        meta = _gallery_active_metadata()
        if not meta:
            return "Select an example"
        recipe_path = _example_dir() / "data_analysis_recipe.yaml"
        if recipe_path.exists():
            with open(recipe_path, "r") as f:
                return f.read()
        return "Source YAML not found"

    @output
    @render.ui
    def gallery_md_content():
        meta = _gallery_active_metadata()
        if not meta:
            return ui.div("Select an entry to view guidance.", class_="p-4 text-center text-muted")

        md_path = _example_dir() / "example_meta.md"
        if md_path.exists():
            with open(md_path, "r") as f:
                return ui.div(ui.HTML(external_links_new_tab(str(ui.markdown(f.read())))), class_="gallery-guidance-styled")
        return ui.div("Educational metadata (example_meta.md) missing.", class_="alert alert-warning")

    @reactive.Effect
    @reactive.event(input.btn_apply_gallery_filters)
    def _update_gallery_options():
        """
        High-Performance Filtering Gate (ADR-037).
        TRIGGERED BY: the 'Apply' button only. The shell is built from the state, so a switch of space needs no refresh.
        """
        listing = _listing()
        if not listing.registry:
            ui.notification_show("Indexer not found or no example passed the check.", type="error")
            return

        # Pivot-Set Intersection across all 6 axes; a group with nothing ticked does not filter (matching_examples).
        applied = {axis: list(safe_input(input, f"gallery_filter_{axis}", []) or []) for axis in FILTER_AXES}
        choices = matching_examples(listing, applied)

        # Keep the example the user is looking at when it still matches; else the first match, and say so on screen.
        with reactive.isolate():
            before = _current_rid()
        if before in choices:
            shown, dropped = before, None
        else:
            shown = next(iter(choices), None)
            dropped = listing.registry[before]["name"] if (before and shown) else None
        _remember(applied=applied, selected=shown, dropped=dropped)

        ui.update_select("gallery_example_select",
                         label=ui.span(
                             f"Visual Gallery ({len(choices)} matched)", style="font-weight:700;color:#345beb;"),
                         choices=choices,
                         selected=shown)

        if not choices:
            ui.notification_show("No matches found for these filters.", type="warning")

    @output
    @render.ui
    def gallery_left_out_notice():
        """Why examples are not shown: the same kind of block as the rejected recipes of HOME. Absent when none failed.

        Reads only bootloader data fixed at start; it does not read the inputs it sits next to (ui_implementation_contract.md section 14).
        """
        blocks = _listing().blocks
        if not blocks:
            return None
        # The title of a block is marked by the listing (`(title, lines)`), not guessed from the text of a line.
        children = []
        for title, lines in blocks:
            if title:
                children.append(ui.div(title, class_="gallery-left-out-title"))
            children.extend(ui.div(line, class_="gallery-left-out-line" + (" gallery-left-out-note" if line in NOTE_LINES else ""))
                            for line in lines)
        return ui.div(*children, class_="gallery-left-out")

    @output
    @render.ui
    def gallery_browser_anchor():
        """Placeholder for any additional anchor logic if needed."""
        return None
