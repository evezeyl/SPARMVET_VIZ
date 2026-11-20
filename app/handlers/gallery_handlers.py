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
# consumes: app/src/bootloader.py (rejected_gallery_examples, gallery_index_status), app/modules/gallery_listing.py, libs/viz_gallery/src/viz_gallery/taxonomy.py (display_axes, filter_panels)
# consumed_by: app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-037, .claude/knowledge/architecture_decisions.md#ADR-045, .claude/rules/rules_ui_dashboard.md#5
# @end_deps

import base64
from pathlib import Path

import polars as pl
from shiny import reactive, render, ui

from app.modules.gallery_listing import (FILTER_AXES, NO_MATCH_TEXT, NOTE_LINES, GalleryListing,
                                         external_links_new_tab, matching_examples, read_listing)


def define_server(input, output, session, *,
                  bootloader, safe_input):
    """Register all Gallery reactive handlers.

    Parameters
    ----------
    bootloader : Bootloader
        Path Authority instance (ADR-031).
    safe_input : callable
        Shared utility: safe_input(input_obj, key, default) → value.
    """

    def _listing() -> GalleryListing:
        """What the gallery lists: the stored index minus the examples that failed the check (flags G-a, G-b)."""
        return read_listing(bootloader.get_location("gallery"),
                            bootloader.rejected_gallery_examples, bootloader.gallery_index_status)

    # 'Select all' of a filter group is done in the page (app/src/www/gallery_select_all.js), never by a server
    # answer: an answer that arrives after the user ticked one term wipes that tick (GALLERY-CHECK-1 finding 9).

    # The examples the last Apply left in the list; None before the first Apply. Written only by the Apply effect.
    _applied_choices = reactive.Value(None)
    # (name of the example an Apply removed from the list, the example shown instead), for a note; None otherwise.
    # The note is shown only while that replacement is the example on screen. Written only by the Apply effect.
    _dropped = reactive.Value(None)

    @reactive.Calc
    def _visible():
        """{id: name} of the examples in the dropdown: the whole list until the first Apply."""
        applied = _applied_choices.get()
        return applied if applied is not None else matching_examples(_listing(), None)

    @reactive.Calc
    def _current_rid():
        """The example shown: the dropdown's value when it is in the list; the first of the list while the dropdown
        has no value yet; nothing for a value that is not in the list (an example that failed the check is never opened).

        The dropdown is built with the same list (gallery_viewer), so its first option and the panes agree from the
        first paint, before the input value has reached the server.
        """
        visible = _visible()
        chosen = safe_input(input, "gallery_example_select", None)
        if chosen is None:
            return next(iter(visible), None)
        return chosen if chosen in visible else None

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
        dropped_pair = _dropped.get()
        dropped = dropped_pair[0] if dropped_pair and dropped_pair[1] == _current_rid() else None
        if not meta:
            if _applied_choices.get() is not None and not _visible():
                return ui.div(NO_MATCH_TEXT, class_="p-5 text-muted gallery-no-match")
            return ui.div("Select an example to view preview.", class_="p-5 text-muted")
        note = (ui.div(f'"{dropped}" does not match the ticked filters, so it is not shown. '
                       "Showing the first example that matches instead.", class_="alert alert-warning m-3 gallery-dropped")
                if dropped else None)

        path_str = meta.get("path")
        if not path_str:
            return ui.div("Path missing in index.", class_="text-danger")

        img_path = Path(path_str).parent / "preview_plot.png"
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
        path_str = meta.get("path")
        if not path_str:
            return None

        data_path = Path(path_str).parent / "example_data.tsv"
        if data_path.exists():
            try:
                # Polars maintains high-density left alignment by default in Shiny's render.table
                return pl.read_csv(data_path, separator="\t")
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
        path_str = meta.get("path")
        if not path_str:
            return "Data analysis recipe path not found"

        if Path(path_str).exists():
            with open(path_str, "r") as f:
                return f.read()
        return "Source YAML not found"

    @output
    @render.ui
    def gallery_md_content():
        meta = _gallery_active_metadata()
        if not meta:
            return ui.div("Select an entry to view guidance.", class_="p-4 text-center text-muted")

        path_str = meta.get("path")
        if not path_str:
            return ui.div("Metadata path not found", class_="text-danger")

        md_path = Path(path_str).parent / "example_meta.md"
        if md_path.exists():
            with open(md_path, "r") as f:
                return ui.div(ui.HTML(external_links_new_tab(str(ui.markdown(f.read())))), class_="gallery-guidance-styled")
        return ui.div("Educational metadata (example_meta.md) missing.", class_="alert alert-warning")

    @reactive.Effect
    @reactive.event(input.btn_apply_gallery_filters, input.sidebar_nav)
    def _update_gallery_options():
        """
        High-Performance Filtering Gate (ADR-037).
        TRIGGERED BY: 'Apply' button OR Tab switch to Gallery.
        """
        # 1. Check if we are actually in the Gallery (don't recalc if switching away)
        if input.sidebar_nav() != "Gallery":
            return
        listing = _listing()
        if not listing.registry:
            ui.notification_show("Indexer not found or no example passed the check.", type="error")
            return

        # 2. Collect Filter Inputs; a group with nothing ticked does not filter (matching_examples)
        applied = {axis: list(safe_input(input, f"gallery_filter_{axis}", []) or []) for axis in FILTER_AXES}
        ui.notification_show("Filtering examples...", duration=1, type="message")

        # 3. Pivot-Set Intersection across all 6 axes
        choices = matching_examples(listing, applied)
        # Keep the example the user is looking at when it still matches (Eve, 2026-11-20: "This is a bug fix");
        # else the first match, and say so on screen.
        with reactive.isolate():
            before = _current_rid()
        shown = before if before in choices else next(iter(choices), None)
        _dropped.set((listing.registry[before]["name"], shown) if (before and shown and shown != before) else None)
        _applied_choices.set(choices)

        # 4. Push Update to UI
        ui.update_select("gallery_example_select",
                         label=ui.span(
                             f"Visual Gallery ({len(choices)} matched)", style="font-weight:700;color:#345beb;"),
                         choices=choices,
                         selected=shown)

        if not choices:
            ui.notification_show(
                "No matches found for these filters.", type="warning")

    @output
    @render.ui
    def gallery_left_out_notice():
        """Why examples are not shown: the same kind of block as the rejected recipes of HOME. Absent when none failed.

        Reads only bootloader data fixed at start; it does not read the inputs it sits next to (ui_implementation_contract.md section 14).
        """
        notice = _listing().notice
        if not notice:
            return None
        # The title line exists only when examples were rejected; a lone note (failed check) has none.
        header, rest = (notice[0], notice[1:]) if notice[0] not in NOTE_LINES else (None, notice)
        return ui.div(
            *([ui.div(header, class_="gallery-left-out-title")] if header else []),
            *[ui.div(line, class_="gallery-left-out-line" + (" gallery-left-out-note" if line in NOTE_LINES else ""))
              for line in rest],
            class_="gallery-left-out",
        )

    @output
    @render.ui
    def gallery_browser_anchor():
        """Placeholder for any additional anchor logic if needed."""
        return None
