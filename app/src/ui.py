# @deps
# provides: app_ui (Shiny UI definition, page_fillable layout)
# consumes: pathlib, shiny, app.src.bootloader, base64, mimetypes
# consumes: app/src/www/bp_expr_editor.js (BP-EXPR-EDITOR-1, included via ui.tags.script)
# consumes: app/src/www/export_ready.js (D-0270, included via ui.tags.script)
# consumes: app/src/www/gallery_select_all.js (GALLERY-CHECK-1, included via ui.tags.script, only with gallery_enabled)
# consumes: app/src/www/audit_places_path.js (the places of the audit dialog as a path), app/src/www/lineage_view.js (the lineage panel of HOME's Audit mode), app/src/www/trial_counting.js (the line of the count at the click on Try), app/src/www/preview_switch.js (the "All rows" switch of the data preview does not fold the data panel)
# consumes: app/src/www/panel_widths.js (D-0381, D-0382, D-0384: the drag of the side panels), app/modules/frame_widths.py (the widths)
# consumed_by: app.src.main
# doc: ADR-027, ADR-029a, ADR-030, ADR-039, ADR-052
# @end_deps
# app/src/ui.py
from pathlib import Path
from shiny import ui
from app.src.bootloader import bootloader
from app.modules import frame_widths

print("--- LOADING UI VERSION V5.1 (Aggressive Centering) ---")
# 1. System Aesthetics (ADR-027, ADR-030)
# Base theme is always injected first.  If the app features points to a different
# CSS file it is injected as a second <style> block so it only needs overrides
# — no @import required (which wouldn't resolve when injected as a string).
_BASE_THEME = Path("config/ui/theme.css")
_base_css = _BASE_THEME.read_text(encoding="utf-8")
_app_features_theme_path = bootloader.get_theme_css_path()
_app_features_extra_css = (
    _app_features_theme_path.read_text(encoding="utf-8")
    if _app_features_theme_path.resolve() != _BASE_THEME.resolve()
    else ""
)


_WWW_DIR = Path(__file__).parent / "www"


def _versioned(served_path: str) -> str:
    """Append ?v=<mtime> to a /-rooted static asset path served from app/src/www/.

    Issue #37 (Eve): an edited first-party or vendored script kept running the
    old version after a hard refresh — Shiny's static_assets mount serves the current
    file from disk every request, but the browser can still treat the URL itself as
    cacheable. Appending the file's own mtime makes the URL change whenever the file
    does, forcing a real fetch — no cache-busting needed when nothing changed either.
    Falls back to the bare path if the file can't be stat'd (e.g. missing at import
    time) rather than raising — a missing script is a 404 either way.
    """
    local_path = _WWW_DIR / served_path.lstrip("/")
    try:
        mtime = int(local_path.stat().st_mtime)
    except OSError:
        return served_path
    sep = "&" if "?" in served_path else "?"
    return f"{served_path}{sep}v={mtime}"


def _resolve_logo_src(logo_url: str) -> str:
    """Return a usable <img src> value for logo_url from app features config.

    Remote URLs (http/https) are returned as-is.
    Local paths are read from disk and returned as a base64 data URI so no
    static file serving setup is required — the image is embedded in the page.
    Returns empty string if the path is empty or the file is not found.
    """
    if not logo_url:
        return ""
    if logo_url.startswith("http://") or logo_url.startswith("https://"):
        return logo_url
    import base64, mimetypes
    p = Path(logo_url)
    if not p.exists():
        print(f"[ui] WARNING: logo_url '{logo_url}' not found — banner logo skipped.")
        return ""
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"

def export_ready_script_tags() -> list:
    """The script of the Export button, only where the Export panel can exist (ADR-071 rule 2: positive inclusion).

    The script reads the panel that export_enabled gates; loading it elsewhere would put code on a page that has no
    such panel.
    """
    if not bootloader.is_enabled("export_enabled"):
        return []
    return [ui.tags.script(src=_versioned("/export_ready.js"))]


def panel_widths_script_tags() -> list:
    """The drag of the side panels: limit, keep and restore the widths in the browser (D-0381, D-0382, D-0384). The numbers come from
    `app/modules/frame_widths.py` as data attributes of a hidden element, never from a string built into a style."""
    return [ui.tags.script(src=_versioned("/panel_widths.js"))]


def panel_widths_data() -> object:
    """The hidden element that carries the numbers of `panel_widths_script_tags` (in the body: a head cannot hold a div)."""
    return ui.div(id="spv_frame_widths", hidden=True, **frame_widths.data_attributes())


def gallery_script_tags() -> list:
    """The script of the Gallery filter groups, only where the Gallery can exist (ADR-071 rule 2: positive inclusion)."""
    if not bootloader.is_enabled("gallery_enabled"):
        return []
    return [ui.tags.script(src=_versioned("/gallery_select_all.js"))]


app_ui = ui.page_fillable(
    ui.head_content(
        ui.tags.style(_base_css),
        *([ui.tags.style(_app_features_extra_css)] if _app_features_extra_css else []),
        # Vendored locally — air-gap / restricted-network safe (DEPLOY-CDN-1).
        # Source: app/src/www/vendor/ — pinned versions, no CDN dependency.
        ui.tags.link(
            rel="stylesheet", href=_versioned("/vendor/bootstrap-icons.css")),
        # [BP-EXPR-EDITOR-1] Expression widget column autocomplete — vanilla JS, no CDN.
        # Cache-busted by mtime (issue #37) so an edit during development is always
        # picked up on reload, without needing "Disable cache" in DevTools.
        ui.tags.script(src=_versioned("/bp_expr_editor.js")),
        # [D-0270] Export button is ready only when the server holds the values on the screen — vanilla JS, no CDN.
        *export_ready_script_tags(),
        # [GALLERY-CHECK-1] "Select all" of a Gallery filter group is done in the page, not by a server answer that can arrive late.
        *gallery_script_tags(),
        *panel_widths_script_tags(),
        # the "All rows" switch of the data preview sits in a panel header: its click must not fold the panel
        ui.tags.script(src=_versioned("/preview_switch.js")),
        # the places of the audit dialog as the path of the lineage; the places that follow from a ticked place are derived (greyed)
        ui.tags.script(src=_versioned("/audit_places_path.js")),
        # the lineage panel of HOME in Audit mode: the list and the map of dots to choose the place of an audit step (D-0629, D-0634)
        ui.tags.script(src=_versioned("/lineage_view.js")),
        # the line "Counting the rows each place loses..." at the click on Try (FLOW-1): the server cannot show a line while it works
        ui.tags.script(src=_versioned("/trial_counting.js")),
        # [ADR-039] Cytoscape.js Tube-Map Integration (replaces Mermaid + svg-pan-zoom)
        # Cytoscape core + dagre layout plugin for ranked-LR hierarchical DAG.
        ui.tags.script(src=_versioned("/vendor/cytoscape.min.js")),
        ui.tags.script(src=_versioned("/vendor/dagre.min.js")),
        ui.tags.script(src=_versioned("/vendor/cytoscape-dagre.js")),
        ui.tags.script("""
// ── [ADR-039] Cytoscape TubeMap Bridge ──────────────────────────────────────
//
// Global instance — one Cytoscape graph per page (the TubeMap is a singleton).
window._cyInstance = null;

// Called by wrangle_studio.py blueprint_tubemap_ui render with the JSON elements string.
function initCyTubeMap(elementsJson, containerId) {
    var container = document.getElementById(containerId || 'cy_tubemap');
    if (!container) return;

    // Destroy previous instance if Shiny replaced the DOM
    if (window._cyInstance) {
        try { window._cyInstance.destroy(); } catch(e) {}
        window._cyInstance = null;
    }

    var elements;
    try { elements = JSON.parse(elementsJson); }
    catch(e) { console.error('TubeMap: bad JSON', e); return; }

    // ── Colour palette (mirrors _CY_COLOURS in blueprint_mapper.py) ──────────
    var palette = {
        trunk:   { bg: '#345beb', border: '#2a4bc4', text: '#ffffff' },
        add:     { bg: '#6c757d', border: '#495057', text: '#ffffff' },
        meta:    { bg: '#fd7e14', border: '#dc6a0d', text: '#ffffff' },
        wrangle: { bg: '#ffc107', border: '#e0a800', text: '#212529' },
        branch:  { bg: '#9c27b0', border: '#7b1fa2', text: '#ffffff' },
        plot:    { bg: '#10a395', border: '#0d8a7e', text: '#ffffff' },
        info:    { bg: '#eef0fb', border: '#345beb', text: '#1a1a1a' },
    };

    function styleFor(role) {
        return palette[role] || { bg: '#adb5bd', border: '#6c757d', text: '#000' };
    }

    // ── Node shape per role ────────────────────────────────────────────────────
    var shapes = {
        trunk:   'ellipse',
        add:     'ellipse',
        meta:    'ellipse',
        wrangle: 'round-rectangle',
        branch:  'diamond',
        plot:    'round-rectangle',
        info:    'round-rectangle',
    };

    // Build per-role stylesheet entries
    var roleStyles = [];
    Object.keys(palette).forEach(function(role) {
        var c = palette[role];
        roleStyles.push({
            selector: 'node.' + role,
            style: {
                'background-color': c.bg,
                'border-color':     c.border,
                'color':            c.text,
                'shape':            shapes[role] || 'ellipse',
            }
        });
    });

    var cy = cytoscape({
        container: container,
        elements:  elements,

        layout: {
            name:       'dagre',
            rankDir:    'LR',          // left → right pipeline flow
            nodeSep:    12,            // vertical gap between nodes in same tier (tighter rail)
            rankSep:    65,            // horizontal gap between tiers (tighter tube)
            edgeSep:    6,
            ranker:     'tight-tree',  // compact assignment — prevents gaps
            animate:    false,
        },

        style: [
            // ── Base node ────────────────────────────────────────────────────
            {
                selector: 'node',
                style: {
                    'label':              'data(label)',
                    'text-wrap':          'wrap',
                    'text-max-width':     '80px',
                    'font-size':          '9px',
                    'font-family':        'system-ui, sans-serif',
                    'text-valign':        'center',
                    'text-halign':        'center',
                    'width':              'label',
                    'height':             'label',
                    'padding':            '4px',
                    'border-width':       '1.5px',
                    'border-style':       'solid',
                    'cursor':             'pointer',
                    'transition-property':'border-width border-color',
                    'transition-duration':'0.15s',
                }
            },
            // ── Per-role colours (generated above) ──────────────────────────
            ...roleStyles,
            // ── Active / selected node ───────────────────────────────────────
            {
                selector: 'node.active',
                style: {
                    'border-width':       '3px',
                    'border-color':       '#212529',
                    'border-style':       'dashed',
                    'overlay-opacity':    0,
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width':       '3px',
                    'border-color':       '#212529',
                    'border-style':       'solid',
                }
            },
            // ── Hover ────────────────────────────────────────────────────────
            {
                selector: 'node:active',
                style: { 'overlay-opacity': 0.1, 'overlay-color': '#000' }
            },
            // ── Edges ────────────────────────────────────────────────────────
            {
                selector: 'edge',
                style: {
                    'width':              1.5,
                    'line-color':         '#9e9e9e',
                    'target-arrow-color': '#9e9e9e',
                    'target-arrow-shape':'triangle',
                    'arrow-scale':        0.7,
                    'curve-style':        'bezier',
                }
            },
            // ── Highlighted edge (connected to active node) ──────────────────
            {
                selector: 'edge.highlighted',
                style: {
                    'width':              2.5,
                    'line-color':         '#212529',
                    'target-arrow-color': '#212529',
                    'z-index':            10,
                }
            },
        ],

        userZoomingEnabled:   true,
        userPanningEnabled:   true,
        boxSelectionEnabled:  false,
        autounselectify:      false,
        minZoom:              0.1,
        maxZoom:              8,
    });

    // ── Click → Shiny bridge ─────────────────────────────────────────────────
    cy.on('tap', 'node', function(evt) {
        var node = evt.target;
        var schemaId = node.data('schema_id');
        if (!schemaId) return;
        console.log('TubeMap node clicked: ' + schemaId);
        Shiny.setInputValue('blueprint_node_clicked', schemaId, {priority: 'event'});

        // Highlight connected edges
        cy.edges().removeClass('highlighted');
        node.connectedEdges().addClass('highlighted');
    });

    // ── Tooltip on hover ─────────────────────────────────────────────────────
    cy.on('mouseover', 'node', function(evt) {
        var node = evt.target;
        var tip = document.getElementById('cy_tooltip');
        if (!tip) return;
        var label = node.data('label') || '';
        var role  = node.data('role')  || '';
        var grp   = node.data('group') || '';
        tip.textContent = label.replace(/\\n/g,' ') + ' [' + role + (grp ? ' · ' + grp : '') + ']';
        tip.style.display = 'block';
    });
    cy.on('mouseout', 'node', function() {
        var tip = document.getElementById('cy_tooltip');
        if (tip) tip.style.display = 'none';
    });

    cy.fit(undefined, 20);
    window._cyInstance = cy;
}
window.initCyTubeMap = initCyTubeMap;

// ── Highlight active node (called from server after component load) ───────────
function cyHighlightNode(schemaId) {
    var cy = window._cyInstance;
    if (!cy) return;
    cy.nodes().removeClass('active');
    cy.edges().removeClass('highlighted');
    var matches = cy.nodes().filter(function(n) {
        return n.data('schema_id') === schemaId;
    });
    matches.addClass('active');
    matches.connectedEdges().addClass('highlighted');
    if (matches.length > 0) {
        cy.animate({ fit: { eles: matches, padding: 60 } }, { duration: 250 });
    }
}
window.cyHighlightNode = cyHighlightNode;

// ── Toolbar helpers ──────────────────────────────────────────────────────────
function cyZoomIn()  { if (window._cyInstance) window._cyInstance.zoom(window._cyInstance.zoom() * 1.3); }
function cyZoomOut() { if (window._cyInstance) window._cyInstance.zoom(window._cyInstance.zoom() * 0.77); }
function cyFit()     { if (window._cyInstance) window._cyInstance.fit(undefined, 20); }
window.cyZoomIn  = cyZoomIn;
window.cyZoomOut = cyZoomOut;
window.cyFit     = cyFit;
        """)
    ),

    # Optional deployment banner: logo, ui_label and description from branding.banner of the deployment file
    *([ui.div(
        *([ui.tags.img(
            src=_resolve_logo_src(bootloader.get_ui_banner().get("logo_url", "")),
            class_="sparmvet-banner-logo",
            alt="Logo",
        )] if _resolve_logo_src(bootloader.get_ui_banner().get("logo_url", "")) else []),
        *([ui.tags.span(
            bootloader.get_ui_banner()["ui_label"],
            class_="sparmvet-banner-title",
        )] if bootloader.get_ui_banner().get("ui_label") else []),
        *([ui.tags.span(
            bootloader.get_ui_banner()["description"],
            class_="sparmvet-banner-subtitle",
        )] if bootloader.get_ui_banner().get("description") else []),
        class_="sparmvet-banner",
    )] if bootloader.get_ui_banner() else []),

    panel_widths_data(),

    # 3-Zone Shell (ADR-029a)
    ui.layout_sidebar(
        # 1. Navigation Panel (Left)
        ui.sidebar(
            ui.div(
                # Persistent Global Navigation (Always Visible)
                ui.div(
                    ui.output_ui("sidebar_nav_ui"),
                    class_="px-3 py-2 border-bottom bg-white mb-2"
                ),
                ui.div(
                    ui.output_ui("sidebar_tools_ui"),
                    class_="flex-grow-1 overflow-auto"
                ),
                class_="h-100 w-100 d-flex flex-column"
            ),
            class_="sidebar-content p-0",
            width=frame_widths.css_width(frame_widths.LEFT),
            id="nav_sidebar"
        ),
        # 3. Right sidebar — excluded from DOM when not visible (ADR-073).
        # Structural exclusion (not CSS hide) so the center column fills full width.
        # Visibility is driven by workspaces.home.right_sidebar.visible in app features file;
        # replacing the prior t3_sandbox_enabled flag check (ADR-053 violation, task 25-O).
        (
            ui.div(
                # The warning of the ids (D-0582): above the tabs, in every app features file; empty when the checks found nothing (id_warning_handlers.py).
                ui.output_ui("id_warning_ui"),
                ui.output_ui("dynamic_tabs"),
                class_="central-theater p-0 bg-transparent h-100",
                id="main_layout_inner",
                style="height:100%; flex:1;"
            )
            if not bootloader.get_sidebar_config("home", "right").visible
            else ui.layout_sidebar(
                ui.sidebar(
                    ui.output_ui("right_sidebar_content_ui"),
                    id="audit_sidebar",
                    bg="#c0c0c0",
                    width=frame_widths.css_width(frame_widths.RIGHT),
                    position="right",
                    # HOME starts in Exploration: closed; the server opens it with the mode (D-0375, D-0385)
                    open="closed"
                ),
                # 2. Central Theater (Center)
                ui.div(
                    ui.output_ui("id_warning_ui"),
                    ui.output_ui("dynamic_tabs"),
                    class_="central-theater p-0 bg-transparent h-100"
                ),
                id="main_layout_inner",
                fillable=True,
                border=False
            )
        ),
        id="main_layout_outer",
        fillable=True,
        border=False
    ),
    fillable=True
)
