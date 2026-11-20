# @deps
# provides: class:GalleryViewer, function:build_sidebar_ui, function:render_explorer_ui
# consumes: app/src/www/gallery_select_all.js (the "Clear all ticks" button, id gallery_clear_ticks), app/src/bootloader.py (bootloader singleton), app/modules/gallery_listing.py, libs/viz_gallery/src/viz_gallery/taxonomy.py (filter_panels)
# consumed_by: app/handlers/gallery_handlers.py, app/src/server.py, app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-033, .claude/knowledge/architecture_decisions.md#ADR-057, .claude/design/recipe_format_spec.md (section 9, G1)
# @end_deps
from shiny import ui, reactive, render
import yaml
from pathlib import Path
from app.src.bootloader import bootloader
from app.modules.gallery_listing import APPLY_RULE_TEXT, matching_examples, read_listing
from viz_gallery.taxonomy import filter_panels


class GalleryViewer:
    """
    GalleryViewer (gallery_viewer.py)
    Architectural context: ADR-033 Split-Pane Gallery (the submission modal was removed, D-0046).
    """

    def __init__(self):
        pass

    def split_viewer_layout(self, example_id="active"):
        """
        Implements the ADR-033 Vertical Stack UI for Maximized Previews.
        Top: Technical (Full Width) / Bottom: Educational (Guidance Underneath).
        Both panes are collapsible via accordion (open by default).
        """
        return ui.div(
            # Technical Top Pane — collapsible
            ui.accordion(
                ui.accordion_panel(
                    "📊 Preview",
                    ui.navset_card_tab(
                        ui.nav_panel("Plot Preview",
                                     ui.output_ui("gallery_preview_img")),
                        ui.nav_panel("Data Sample",
                                     ui.div(ui.output_ui("gallery_static_data"),
                                            style="max-height: 650px; overflow: auto;")),
                        ui.nav_panel("YAML Example",
                                     ui.output_text_verbatim("gallery_yaml_preview")),
                        id="gallery_tech_tabs"
                    ),
                    value="gallery_preview_panel",
                ),
                id="gallery_preview_accordion",
                open=True,
            ),
            # Educational Bottom Pane — collapsible, soft-note aesthetic
            ui.accordion(
                ui.accordion_panel(
                    "📖 Visual Cookbook: Guidance",
                    ui.div(
                        ui.output_ui("gallery_md_content"),
                        class_="mx-auto px-4 gallery-md-pane",
                    ),
                    value="gallery_guidance_panel",
                ),
                id="gallery_guidance_accordion",
                open=True,
            ),
            class_="d-flex flex-column gap-2"
        )

    def _load_listing(self):
        """The examples that pass the check and their taxonomy pivot (gallery_listing); empty when there is no index."""
        return read_listing(bootloader.get_location("gallery"), bootloader.rejected_gallery_examples,
                            bootloader.gallery_index_status)

    @staticmethod
    def _filter_panel(label, input_id, all_id, choices, value, selected=None, all_value=True):
        """One collapsible taxonomy filter panel (label + select-all + checkboxes)."""
        return ui.accordion_panel(
            label,
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Select all", class_="text-muted",
                                style="font-size:0.78em; white-space:nowrap; margin-right:4px;"),
                        ui.input_checkbox(all_id, "", value=all_value),
                        class_="gallery-select-all-row",
                        style="display:flex; align-items:center; margin-left:auto;",
                    ),
                    style="display:flex; margin-bottom:0;",
                ),
                ui.input_checkbox_group(input_id, label=None,
                                        choices=choices, selected=choices if selected is None else selected),
                class_="gallery-sidebar-group"
            ),
            value=value,
        )

    def build_sidebar_ui(self, state=None):
        """
        Gallery filter + example selector UI for the left nav_sidebar.

        `state` is what the user left (ticked terms, applied filters, selected example, ui_implementation_contract.md
        section 13: a panel's state survives a switch of space). The shell is rebuilt on every switch of space, so the
        inputs are built from it: they come back as they were left, and the dropdown holds the applied list from the
        first paint (no empty select filled a moment later). Without a state, everything is ticked and listed.
        ADR-057: moved from internal layout_sidebar to persistent nav_sidebar accordion.
        The six filter panels (label, icon, order of the axes and of their terms) come from the
        specification data through viz_gallery.taxonomy.filter_panels; a panel offers the terms that
        at least one indexed example uses. No list of terms is kept in this file (spec section 9, G1).
        """
        state = state or {}
        listing = self._load_listing()
        panels = filter_panels(listing.pivot)
        applied = state.get("applied")
        choices = matching_examples(listing, applied)
        label = (ui.span(f"Visual Gallery ({len(choices)} matched)", style="font-weight:700;color:#345beb;")
                 if applied is not None else ui.span("Select an Example", class_="fw-bold"))
        chosen = state.get("selected")

        accordion = ui.accordion(
            ui.accordion_panel(
                "👨‍🍳 Example",
                ui.input_select(
                    "gallery_example_select",
                    label,
                    choices=choices,
                    selected=chosen if chosen in choices else None,
                ),
                value="gallery_example_panel",
            ),
            ui.accordion_panel(
                "🔍 Gallery Taxonomy",
                ui.accordion(
                    *[
                        self._filter_panel(
                            panel["label"],
                            f"gallery_filter_{panel['axis']}", f"gallery_all_{panel['axis']}",
                            panel["choices"], f"tax_{panel['axis']}",
                            selected=state.get("ticked", {}).get(panel["axis"]),
                            all_value=state.get("all", {}).get(panel["axis"], True),
                        )
                        for panel in panels
                    ],
                    id="gallery_taxonomy_sub_accordion",
                    multiple=True,
                    open=False,
                ),
                ui.div(APPLY_RULE_TEXT, class_="text-muted gallery-apply-rule",
                       style="font-size:0.75rem; margin-top:6px;"),
                # Plain button handled in the page (app/src/www/gallery_select_all.js): it only unticks; the list
                # changes after Apply (PROVISIONAL label, D-0379). Amber discard/reset type (rules_css_style_spec.md 4).
                ui.tags.button("Clear all ticks", type="button", id="gallery_clear_ticks",
                               class_="btn w-100 mt-2"),
                ui.input_action_button(
                    "btn_apply_gallery_filters",
                    ui.HTML('<i class="bi bi-play-fill"></i> Apply'),
                    class_="btn-success w-100 mt-2"
                ),
                value="gallery_taxonomy_panel",
            ),
            id="gallery_sidebar_accordion",
            multiple=True,
            open=["gallery_example_panel", "gallery_taxonomy_panel"],
        )
        # Under the filters: why examples are left out (absent when none failed the check). It stays inside this one
        # freestanding block, so the sidebar registry needs no new panel type.
        return ui.TagList(accordion, ui.output_ui("gallery_left_out_notice"))

    def render_explorer_ui(self):
        """
        Renders the Gallery main content area (full-width, no internal sidebar).
        ADR-057: filter sidebar moved to nav_sidebar via build_sidebar_ui().
        """
        return ui.div(
            ui.div(
                ui.span("📚 Gallery Inspiration", class_="banner-title"),
                ui.span(
                    "Browse visual examples for inspiration. "
                    "Missing an example? Open an issue with the GitHub button under the workspace tabs on the left.",
                    class_="banner-subtitle"
                ),
                class_="view-title-banner"
            ),
            ui.output_ui("gallery_browser_anchor"),
            self.split_viewer_layout(),
            class_="d-flex flex-column"
        )


# Singleton for import
gallery_viewer = GalleryViewer()
