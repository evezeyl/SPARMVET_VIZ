# @deps
# provides: app_ui (Shiny UI definition, page_fillable layout)
# consumes: pathlib, shiny, app.src.bootloader, base64, mimetypes
# consumed_by: app.src.main
# doc: ADR-027, ADR-029a, ADR-030, ADR-039, ADR-052
# @end_deps
# app/src/ui.py
from pathlib import Path
from shiny import ui
from app.src.bootloader import bootloader

print("--- LOADING UI VERSION V5.1 (Aggressive Centering) ---")
# 1. System Aesthetics (ADR-027, ADR-030)
# Base theme is always injected first.  If the persona points to a different
# CSS file it is injected as a second <style> block so it only needs overrides
# — no @import required (which wouldn't resolve when injected as a string).
_BASE_THEME = Path("config/ui/theme.css")
_base_css = _BASE_THEME.read_text(encoding="utf-8")
_persona_theme_path = bootloader.get_theme_css_path()
_persona_extra_css = (
    _persona_theme_path.read_text(encoding="utf-8")
    if _persona_theme_path.resolve() != _BASE_THEME.resolve()
    else ""
)


def _resolve_logo_src(logo_url: str) -> str:
    """Return a usable <img src> value for logo_url from persona config.

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

app_ui = ui.page_fillable(
    ui.head_content(
        ui.tags.style(_base_css),
        *([ui.tags.style(_persona_extra_css)] if _persona_extra_css else []),
        # Vendored locally — air-gap / restricted-network safe (DEPLOY-CDN-1).
        # Source: app/src/www/vendor/ — pinned versions, no CDN dependency.
        ui.tags.link(
            rel="stylesheet", href="/vendor/bootstrap-icons.css"),
        # [ADR-039] Cytoscape.js Tube-Map Integration (replaces Mermaid + svg-pan-zoom)
        # Cytoscape core + dagre layout plugin for ranked-LR hierarchical DAG.
        ui.tags.script(src="/vendor/cytoscape.min.js"),
        ui.tags.script(src="/vendor/dagre.min.js"),
        ui.tags.script(src="/vendor/cytoscape-dagre.js"),
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
        trunk:   { bg: '#0d6efd', border: '#0a58ca', text: '#ffffff' },
        ref:     { bg: '#6c757d', border: '#495057', text: '#ffffff' },
        meta:    { bg: '#fd7e14', border: '#dc6a0d', text: '#ffffff' },
        wrangle: { bg: '#ffc107', border: '#e0a800', text: '#212529' },
        branch:  { bg: '#9c27b0', border: '#7b1fa2', text: '#ffffff' },
        plot:    { bg: '#198754', border: '#146c43', text: '#ffffff' },
        info:    { bg: '#e3f2fd', border: '#1976d2', text: '#1a1a1a' },
    };

    function styleFor(role) {
        return palette[role] || { bg: '#adb5bd', border: '#6c757d', text: '#000' };
    }

    // ── Node shape per role ────────────────────────────────────────────────────
    var shapes = {
        trunk:   'ellipse',
        ref:     'ellipse',
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
            nodeSep:    18,            // vertical gap between nodes in same tier
            rankSep:    90,            // horizontal gap between tiers
            edgeSep:    8,
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
                    'padding':            '6px',
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
                    'arrow-scale':        0.8,
                    'curve-style':        'unbundled-bezier',
                    'control-point-distances': [20],
                    'control-point-weights':   [0.5],
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

    # Optional persona banner — logo + title injected from ui_banner key in persona template
    *([ui.div(
        *([ui.tags.img(
            src=_resolve_logo_src(bootloader.get_ui_banner().get("logo_url", "")),
            class_="sparmvet-banner-logo",
            alt="Logo",
        )] if _resolve_logo_src(bootloader.get_ui_banner().get("logo_url", "")) else []),
        *([ui.tags.span(
            bootloader.get_ui_banner()["title"],
            class_="sparmvet-banner-title",
        )] if bootloader.get_ui_banner().get("title") else []),
        *([ui.tags.span(
            bootloader.get_ui_banner()["subtitle"],
            class_="sparmvet-banner-subtitle",
        )] if bootloader.get_ui_banner().get("subtitle") else []),
        class_="sparmvet-banner",
    )] if bootloader.get_ui_banner() else []),

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
            width="340px",
            id="nav_sidebar"
        ),
        # 3. Right sidebar — excluded from DOM when not visible (ADR-073).
        # Structural exclusion (not CSS hide) so the center column fills full width.
        # Visibility is driven by workspaces.home.right_sidebar.visible in persona template;
        # replacing the prior t3_sandbox_enabled flag check (ADR-053 violation, task 25-O).
        (
            ui.div(
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
                    width="340px",
                    position="right"
                ),
                # 2. Central Theater (Center)
                ui.div(
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
