# @deps
# provides: class:GalleryViewer, function:build_sidebar_ui, function:render_explorer_ui
# consumes: app/src/bootloader.py (bootloader singleton)
# consumed_by: app/handlers/gallery_handlers.py, app/src/server.py, app/handlers/home_theater.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-033, .claude/knowledge/architecture_decisions.md#ADR-057
# @end_deps
from shiny import ui, reactive, render
import yaml
from pathlib import Path
from app.src.bootloader import bootloader


class GalleryViewer:
    """
    GalleryViewer (gallery_viewer.py)
    Architectural context: ADR-033 Split-Pane Gallery and Submission Gate.
    """

    def __init__(self):
        pass

    def submission_modal_ui(self):
        """
        Renders the Submission Gate Modal with mandatory checklist.
        ADR-033: Enforce MD file presence before submission.
        """
        return ui.modal(
            ui.h4("Public Gallery: Quality Submission Gate"),
            ui.div(
                ui.p(
                    "Your analysis is ready for sharing. Please verify the documentation triplet:"),
                ui.div(
                    ui.input_checkbox(
                        "check_yaml", "✅ Recipe Logic (.yaml)", value=True),
                    ui.input_checkbox(
                        "check_tsv", "✅ Reference Data (.tsv)", value=True),
                    ui.input_checkbox(
                        "check_png", "✅ Plot Evidence (.png)", value=True),
                    ui.input_checkbox(
                        "check_md", "📄 Educational Metadata (.md)", value=False),
                    ui.input_checkbox(
                        "check_supp", "🖼️ Supplemental Illustrations (optional)", value=False),
                    class_="p-3 border rounded bg-light mb-3"
                ),
                ui.div(
                    ui.p("Educational metadata is MANDATORY for all Gallery submissions.",
                         class_="text-warning small"),
                    ui.input_action_button(
                        "btn_autofill_meta", "📝 Autofill template from Audit Stack", class_="btn-sm btn-outline-info w-100"),
                    class_="mb-3"
                )
            ),
            ui.div(
                ui.input_action_button(
                    "btn_confirm_submission", "🚀 Confirm & Upload", class_="btn-primary"),
                ui.modal_button("Cancel"),
                class_="d-flex justify-content-end gap-2"
            ),
            title="Gallery Submission",
            size="l",
            easy_close=True
        )

    def split_viewer_layout(self, recipe_id="active"):
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
                        ui.nav_panel("YAML Recipe",
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

    def _load_pivot(self) -> dict:
        """Read taxonomy pivot from gallery_index.json. Returns {} on any failure."""
        import json
        index_path = bootloader.get_location("gallery") / "gallery_index.json"
        if not index_path.exists():
            return {}
        try:
            with open(index_path) as f:
                return json.load(f).get("pivot", {})
        except Exception:
            return {}

    @staticmethod
    def _filter_panel(label, input_id, all_id, choices, value):
        """One collapsible taxonomy filter panel (label + select-all + checkboxes)."""
        return ui.accordion_panel(
            label,
            ui.div(
                ui.div(
                    ui.div(
                        ui.span("Select all", class_="text-muted",
                                style="font-size:0.78em; white-space:nowrap; margin-right:4px;"),
                        ui.input_checkbox(all_id, "", value=True),
                        class_="gallery-select-all-row",
                        style="display:flex; align-items:center; margin-left:auto;",
                    ),
                    style="display:flex; margin-bottom:0;",
                ),
                ui.input_checkbox_group(input_id, label=None,
                                        choices=choices, selected=choices),
                class_="gallery-sidebar-group"
            ),
            value=value,
        )

    def build_sidebar_ui(self):
        """
        Gallery filter + recipe selector UI for the left nav_sidebar.
        ADR-057: moved from internal layout_sidebar to persistent nav_sidebar accordion.
        Choices are read dynamically from gallery_index.json pivot so new recipe
        families/patterns appear automatically without code changes.
        """
        pivot = self._load_pivot()

        _diff_order    = {"Simple": 0, "Intermediate": 1, "Advanced": 2}
        _ss_order      = {"any": 0, "individual points": 1, "medium+": 2, "large": 3}
        _def_families  = ["Comparison", "Correlation", "Distribution",
                          "Evolution", "Part-to-Whole", "Ranking"]
        _def_patterns  = ["1 Numeric", "1 Numeric, 1 Categorical",
                          "1 Numeric, 2 Categorical", "1 Numeric, 2 Categorical (Faceted)",
                          "2 Numeric", "2 Numeric, 1 Categorical (Faceted)", "Numeric-Numeric"]
        _def_diff      = ["Simple", "Intermediate", "Advanced"]
        _def_geoms     = ["geom_area", "geom_bar", "geom_bin_2d", "geom_boxplot",
                          "geom_col", "geom_density", "geom_freqpoly", "geom_histogram",
                          "geom_jitter", "geom_line", "geom_path", "geom_point",
                          "geom_pointrange", "geom_qq", "geom_segment", "geom_sina",
                          "geom_step", "geom_tile", "geom_violin", "stat_ecdf"]
        _def_show      = ["change", "distribution", "frequency", "normality",
                          "proportion", "ranking", "relationship", "trend", "uncertainty"]
        _def_ss        = ["any", "individual points", "medium+", "large"]

        family_choices = sorted(pivot.get("by_family", {}).keys()) or _def_families
        pattern_choices = sorted(pivot.get("by_pattern", {}).keys()) or _def_patterns
        difficulty_choices = sorted(
            pivot.get("by_difficulty", {}).keys() or _def_diff,
            key=lambda x: _diff_order.get(x, 99),
        )
        geom_choices = sorted(pivot.get("by_geom", {}).keys()) or _def_geoms
        show_choices = sorted(pivot.get("by_show", {}).keys()) or _def_show
        ss_choices = sorted(
            pivot.get("by_sample_size", {}).keys() or _def_ss,
            key=lambda x: _ss_order.get(x, 99),
        )

        return ui.accordion(
            ui.accordion_panel(
                "👨‍🍳 Recipe",
                ui.input_select(
                    "gallery_recipe_select",
                    ui.span("Select a Recipe", class_="fw-bold"),
                    choices={}
                ),
                ui.input_action_button(
                    "btn_clone_gallery",
                    ui.HTML('<i class="bi bi-copy"></i> Clone to Sandbox'),
                    class_="btn-primary w-100 mt-2"
                ),
                value="gallery_recipe_panel",
            ),
            ui.accordion_panel(
                "🔍 Gallery Taxonomy",
                ui.accordion(
                    self._filter_panel(
                        "📊 Family (Purpose)",
                        "gallery_filter_family", "gallery_all_family",
                        family_choices, "tax_family",
                    ),
                    self._filter_panel(
                        "🔢 Data Pattern",
                        "gallery_filter_pattern", "gallery_all_pattern",
                        pattern_choices, "tax_pattern",
                    ),
                    self._filter_panel(
                        "📈 Difficulty",
                        "gallery_filter_difficulty", "gallery_all_difficulty",
                        difficulty_choices, "tax_difficulty",
                    ),
                    self._filter_panel(
                        "⚙️ Primary Geom",
                        "gallery_filter_geom", "gallery_all_geom",
                        geom_choices, "tax_geom",
                    ),
                    self._filter_panel(
                        "🎯 What it Shows",
                        "gallery_filter_show", "gallery_all_show",
                        show_choices, "tax_show",
                    ),
                    self._filter_panel(
                        "📏 Sample Size",
                        "gallery_filter_sample_size", "gallery_all_sample_size",
                        ss_choices, "tax_sample_size",
                    ),
                    id="gallery_taxonomy_sub_accordion",
                    multiple=True,
                    open=False,
                ),
                ui.input_action_button(
                    "btn_apply_gallery_filters",
                    ui.HTML('<i class="bi bi-play-fill"></i> Apply'),
                    class_="btn-success w-100 mt-2"
                ),
                value="gallery_taxonomy_panel",
            ),
            id="gallery_sidebar_accordion",
            multiple=True,
            open=["gallery_recipe_panel", "gallery_taxonomy_panel"],
        )

    def render_explorer_ui(self):
        """
        Renders the Gallery main content area (full-width, no internal sidebar).
        ADR-057: filter sidebar moved to nav_sidebar via build_sidebar_ui().
        """
        return ui.div(
            ui.div(
                ui.span("📚 Gallery Inspiration", class_="banner-title"),
                ui.span(
                    "Browse visual recipes for inspiration. "
                    "Did you see a nice figure? Send us a request for recipe implementation.",
                    class_="banner-subtitle"
                ),
                class_="view-title-banner"
            ),
            ui.output_ui("gallery_browser_anchor"),
            self.split_viewer_layout(),
            class_="d-flex flex-column"
        )

    def autofill_meta_from_audit(self, audit_stack, persona="Standard User"):
        """
        Helper to generate the mandatory Markdown headers from session audit data.
        ADR-033/035: Axis-Based Taxonomy (Purpose/Pattern/Difficulty).
        """
        headers = [
            "![Final Visualization](preview_plot.png)",
            "",
            "# Recipe Meta: Autofilled from Session Audit",
            "## Family (Purpose): [Distribution | Correlation | Comparison | Ranking]",
            "## Data Pattern: [1 Numeric | 2 Numeric | 1 Numeric, 1 Categorical]",
            "## Difficulty: [Simple | Intermediate | Advanced]",
            "",
            "## Author & License",
            f"- **Author**: {persona}",
            f"- **License**: Creative Commons Attribution 4.0 International (CC-BY 4.0)",
            "",
            "## 1. Suitability (When to Use)",
            "- [x] Derived from specific session transformations.",
            "",
            "## 2. Data Schema (Tier 1 Requirements)",
            "- Columns required for visualization mappings.",
            "",
            "## 3. Transformation Logic (Tier 2 Logic)",
            "The following logic nodes were utilized in this recipe:"
        ]

        for i, node in enumerate(audit_stack):
            action = node.get("action", "unknown")
            comment = node.get("comment", "No justification provided.")
            headers.append(f"- **Step {i+1} ({action})**: {comment}")

        headers.extend([
            "",
            "## 4. Interpretations & Assumptions",
            "- Standard SPARMVET interpretation applies.",
            "",
            "## 5. Inspiration & Resources",
            "- [Link to community resource or R Graph Gallery](https://r-graph-gallery.com/)"
        ])

        return "\n".join(headers)


# Singleton for import
gallery_viewer = GalleryViewer()
