# SPARMVET_VIZ — UI Panel Map & CSS Selector Reference (CURRENT STATE)
# Updated 2026-05-04 — moved to .claude/design/; added session delete buttons, inactive nav-pill color, fixed audit card header color

> Use this file to identify panels precisely when reporting visual issues and when filling in the persona capability matrix.
> **Companion files:**
> - `persona_capability_matrix.md` — which features are enabled per persona (use panel names below when adding comments)
> - `persona_scoping_guide.md` — flag definitions and group descriptions
> - `ui_panel_map.md` — original design-reference (superseded by this file)

## Vocabulary — panel names used in persona scoping

| Panel map term | CSS selector / ID | Used in persona scoping as |
|---|---|---|
| Banner | `.sparmvet-banner` | "top banner" |
| View title banner | `.view-title-banner` | "view-title banner" — Blueprint/Gallery/TestLab header strip |
| Theater header strip | `.theater-header-strip` | "tier toggle area" — contains T1/T2/T3 radio buttons |
| Nav pills strip | `#nav_sidebar .flex-column > .bg-white` | "navigation" — Home · Blueprint · Test Lab · Gallery pills |
| Left sidebar | `#nav_sidebar` | "left sidebar" |
| Right sidebar | `#audit_sidebar` | "right sidebar" / "audit sidebar" |
| Central theater | `.central-theater` | "central theater" |
| Groups pill nav | `#home_groups_nav` | "plot group nav" |
| Session Management accordion | accordion inside `#nav_sidebar` | "session panel" |
| Filters accordion | accordion inside `#nav_sidebar` | "filter panel" |
| Global Project Export accordion | accordion inside `#nav_sidebar` | "export panel" |
| Data Import accordion | accordion inside `#nav_sidebar` | "data import panel" |

**Proposed elements (not yet implemented — see persona_scoping_guide.md):**

| Proposed element | Controlled by | Notes |
|---|---|---|
| Sidebar project title | `[P] ui_branding.title` | Title shown in sidebar instead of (or above) manifest selector |
| Hide nav pills entirely | `[P] show_navigation: false` | Hides Home · Blueprint · etc. pill strip |
| T1/T2 toggle visibility | `[P] tier_toggle_enabled` | Theater header strip — hide the radio buttons |
| Default tier on load | `[P] default_tier` | T1 or T2 shown without user action |
| Ephemeral filter panel | `[P] passive_filter_enabled` | Filters accordion — view only, no audit, no T3 branch |

---

> **⚠️ Known dead CSS rules** (exist in `theme.css` but match no Python element):
> - `#central_theater_tabs` — §2 (line 76), §5 (line 137), §9 (lines 285–286) — ID removed from Python long ago

---

## Global Structure (all views)

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│  BANNER (optional, persona-driven)                          .sparmvet-banner       │
├──────────────────────┬────────────────────────────────┬───────────────────────────┤
│  LEFT SIDEBAR        │  CENTRAL THEATER               │  RIGHT SIDEBAR            │
│  #nav_sidebar        │  .central-theater              │  #audit_sidebar           │
│  (aside.sidebar)     │  output_ui("dynamic_tabs")     │  (persona-gated)          │
│  width: ~340px       │  → renders view-specific HTML  │  width: ~340px            │
└──────────────────────┴────────────────────────────────┴───────────────────────────┘
```

---

## VIEW 1 — Home

```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│  BANNER  .sparmvet-banner                                                                     │
├───────────────────────────┬───────────────────────────────────────────┬───────────────────────┤
│  LEFT SIDEBAR             │  CENTRAL THEATER                          │  RIGHT SIDEBAR        │
│  #nav_sidebar             │  div.theater-container-main               │  #audit_sidebar       │
│                           │                                           │                       │
│ ╔═══════════════════════╗ │ ┌───────────────────────────────────────┐ │ ┌───────────────────┐ │
│ ║  Nav Pills Strip      ║ │ │  Theater Header Strip                 │ │ │  Pipeline Audit   │ │
│ ║  Home · Blueprint ·   ║ │ │  div.theater-header-strip             │ │ │  card             │ │
│ ║  Test Lab · Gallery   ║ │ │  "Data to show:" + T1/T2/T3 toggle    │ │ │  #audit_sidebar   │ │
│ ║  #nav_sidebar .flex-  ║ │ └───────────────────────────────────────┘ │ │  .card            │ │
│ ║  column > .bg-white   ║ │                                           │ │                   │ │
│ ╚═══════════════════════╝ │ ┌───────────────────────────────────────┐ │ │  ── card-header ──│ │
│                           │ │  Groups Pill Nav (direct, no wrapper) │ │ │  "Pipeline Audit" │ │
│ ┌───────────────────────┐ │ │  div.spv-panel (padding 8px 10px 0)   │ │ │  .card-header     │ │
│ │  Manifest Choice      │ │ │  ui.navset_pill  #home_groups_nav     │ │ │                   │ │
│ │  accordion panel      │ │ │                                       │ │ │  ⏳ Pending       │ │
│ │  .accordion-button    │ │ │  ┌─────────────────────────────────┐  │ │ │  .recipe-pending- │ │
│ │  .accordion-body      │ │ │  │  Active Group Tab               │  │ │ │  badge            │ │
│ └───────────────────────┘ │ │  │  div.p-2                        │  │ │ │                   │ │
│                           │ │  │                                 │  │ │ │  Tier 2 — h6      │ │
│ ┌───────────────────────┐ │ │  │  ┌───────────────────────────┐  │  │ │ │  .audit-node-tier2│ │
│ │  Data Import          │ │ │  │  │  Plot Subtab Card         │  │  │ │ │  (repeats)        │ │
│ │  accordion panel      │ │ │  │  │  ui.navset_card_tab       │  │  │ │ │                   │ │
│ └───────────────────────┘ │ │  │  │  id=subtabs_{group_id}    │  │  │ │ │  ── hr ────────── │ │
│                           │ │  │  └───────────────────────────┘  │  │ │ │                   │ │
│ ┌───────────────────────┐ │ │  └─────────────────────────────────┘  │ │ │  Tier 3 — h6      │ │
│ │  Filters              │ │ └───────────────────────────────────────┘ │ │  .audit-node-tier3│ │
│ │  accordion panel      │ │                                           │ │  (repeats)        │ │
│ └───────────────────────┘ │ ┌───────────────────────────────────────┐ │ │                   │ │
│                           │ │  Data Preview                         │ │ │  ── bottom ────── │ │
│ ┌───────────────────────┐ │ │  div.spv-panel (overflow: visible)    │ │ │  [  Apply  ]      │ │
│ │  Global Project       │ │ │    ui.accordion  #acc_home_data       │ │ │  #btn_apply       │ │
│ │  Export               │ │ │    header: ui.tags.span               │ │ └───────────────────┘ │
│ │  accordion panel      │ │ │      "Data Preview"                   │ │                       │
│ └───────────────────────┘ │ │      (0.8em / #6c757d / fw-600)     │ │                       │
│                           │ │    body: column picker + data grid    │ │                       │
│ ┌───────────────────────┐ │ └───────────────────────────────────────┘ │                       │
│ │  Session Management   │ │                                           │                       │
│ │  accordion panel      │ │                                           │                       │
│ └───────────────────────┘ │                                           │                       │
└───────────────────────────┴───────────────────────────────────────────┴───────────────────────┘
```

### Home — CSS selectors per panel

| Panel label | CSS selector | Notes |
|---|---|---|
| Banner | `.sparmvet-banner` | Background + border |
| Nav pills strip | `#nav_sidebar .flex-column > .bg-white` | Home/Blueprint/… pill bar |
| Any sidebar accordion header | `#nav_sidebar .accordion-button` | bg `#a0a0a0`, 0.85rem/700 |
| Any sidebar accordion body | `#nav_sidebar .accordion-body` | bg `#c0c0c0` |
| Theater header strip | `.theater-header-strip` | "Data to show:" + tier toggle |
| Groups nav wrapper | `.theater-container-main .spv-panel` | `div.spv-panel` around pill nav |
| Groups pill nav | `#home_groups_nav` | `navset_pill` — group tab bar |
| Active group content | `#home_groups_nav .active` | Active group panel |
| Per-group plot card | `#subtabs_{group_id}` (dynamic) | `navset_card_tab` — plot tabs |
| Plot tab bar | `#subtabs_{group_id} .card-header` | Tabs row inside plot card |
| Plot content area | `#subtabs_{group_id} .card-body` | Image / table output |
| Data preview outer wrapper | `.theater-container-main .spv-panel:last-of-type` | `div.spv-panel` + `overflow:visible` |
| Data preview accordion | `#acc_home_data` | `bslib accordion` inside spv-panel |
| Data preview header | `#acc_home_data .accordion-button` | Styled by §16 (`0.85rem/700`) |
| Data preview body | `#acc_home_data .accordion-body` | `overflow:visible` (§11 — keeps dropdown unclipped) |
| Audit sidebar card | `#audit_sidebar .card` | Whole right card |
| Audit card header | `#audit_sidebar .card-header` | "Pipeline Audit" title bar, white bg, `#345beb` text |
| Audit card body | `#audit_sidebar .card .card-body` | Tier 2 / Tier 3 content |
| Tier 2 node | `.audit-node-tier2` | Blue tint bg `#eef0fb` |
| Tier 3 node | `.audit-node-tier3` | Teal tint bg `#e6f7f5` |
| Pending badge | `.recipe-pending-badge` | Amber chip |
| Apply button | `#btn_apply` | Bottom of audit sidebar |

---

## VIEW 2 — Blueprint Architect

```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│  BANNER  .sparmvet-banner                                                                     │
├───────────────────────────┬───────────────────────────────────────────┬───────────────────────┤
│  LEFT SIDEBAR             │  CENTRAL THEATER                          │  RIGHT SIDEBAR        │
│  #nav_sidebar             │  div.wrangle-studio-container             │  #audit_sidebar       │
│  (Wrangle Studio mode)    │                                           │  (Blueprint Surgeon)  │
│                           │                                           │                       │
│ ╔═══════════════════════╗ │ ┌───────────────────────────────────────┐ │ ┌───────────────────┐ │
│ ║  Nav Pills Strip      ║ │ │  VIEW TITLE BANNER                    │ │ │  Blueprint Surgeon│ │
│ ╚═══════════════════════╝ │ │  div.view-title-banner                │ │ │  card             │ │
│                           │ │  "👣 Blueprint Architect Flight Deck" │ │ │  ── card-header ──│ │
│ ┌───────────────────────┐ │ └───────────────────────────────────────┘ │ │  "Blueprint       │ │
│ │  Master Manifest      │ │ ┌───────────────────────────────────────┐ │ │   Surgeon"        │ │
│ │  accordion panel      │ │ │  TubeMap                              │ │ │                   │ │
│ │  #wrangle_sidebar_    │ │ │  div.spv-panel.mb-3 (outer wrapper)   │ │ │  🔬 Focused node  │ │
│ │  accordion            │ │ │    #blueprint_tubemap_accordion       │ │ │  info             │ │
│ └───────────────────────┘ │ │    (bslib accordion)                  │ │ │                   │ │
│ ┌───────────────────────┐ │ │    header: "🗺️ Project Lineage"       │ │ │  ── hr ────────── │ │
│ │  External Exchange    │ │ │    bg: #f8f9fa / text: #1a1a1a    │ │ │                   │ │
│ │  accordion panel      │ │ │    viewport: #tubemap_viewport 320px  │ │ │  Active Logic     │ │
│ └───────────────────────┘ │ └───────────────────────────────────────┘ │ │  Stack  h6        │ │
│                           │ ┌───────────────────────────────────────┐ │ │  .audit-node-tier3│ │
│                           │ │  Tri-tab Work Area (direct, no wrap)  │ │ │  (repeats)        │ │
│                           │ │  ui.navset_card_pill                  │ │ └───────────────────┘ │
│                           │ │  #architect_internal_tabs             │ │                       │
│                           │ │  1. Focus · 2. Interface · 3. YAML    │ │                       │
│                           │ └───────────────────────────────────────┘ │                       │
│                           │ ┌───────────────────────────────────────┐ │                       │
│                           │ │  Live Data Glimpse                    │ │                       │
│                           │ │  div.card.shadow-sm.mb-2              │ │                       │
│                           │ │  Bootstrap collapse toggle            │ │                       │
│                           │ │  → collapses #glimpse_body            │ │                       │
│                           │ │  btn: fw-semibold, bg #e9ecef       │ │                       │
│                           │ │  body: data table (max-h 280px)       │ │                       │
│                           │ └───────────────────────────────────────┘ │                       │
└───────────────────────────┴───────────────────────────────────────────┴───────────────────────┘
```

### Blueprint Architect — CSS selectors per panel

| Panel label | CSS selector | Notes |
|---|---|---|
| View title banner | `.view-title-banner` | White rounded panel, shared with Gallery/TestLab |
| TubeMap outer wrapper | `.wrangle-studio-container .spv-panel.mb-3` | Card shadow/radius provided by spv-panel |
| TubeMap accordion | `#blueprint_tubemap_accordion` | bslib accordion inside spv-panel |
| TubeMap header | `#blueprint_tubemap_accordion .accordion-button` | bg `#f8f9fa`, text `#345beb` (§9) |
| TubeMap viewport | `#tubemap_viewport` | height 320px, bg #fafafa |
| Tri-tab pill nav (whole card) | `#architect_internal_tabs` | `navset_card_pill` — direct child of container |
| Tri-tab pill bar | `#architect_internal_tabs .nav-pills` | Focus / Interface / YAML tabs |
| Left sidebar accordion | `#wrangle_sidebar_accordion` | Wrangle Studio left panels |
| Blueprint Surgeon card | `#audit_sidebar .card` | Right card |
| Blueprint Surgeon header | `#audit_sidebar .card-header` | Title bar |
| Blueprint Surgeon body | `#audit_sidebar .card .card-body` | Focused node info + logic stack |
| Live Data Glimpse card | `.wrangle-studio-container .card.shadow-sm` | Bootstrap collapse card |
| Glimpse header button | `.wrangle-studio-container .card-header .btn` | Styled by §18 (0.85rem / fw-bold / `#345beb`) |
| Glimpse collapse body | `#glimpse_body` | Table output, max-h 280px |
| Wrangle studio container | `.wrangle-studio-container` | All Blueprint central content |

> *§18 in `theme.css` sets `.wrangle-studio-container .card-header .btn` to `fw-bold / 0.85rem / #345beb`.
> The Python has `fw-semibold` + inline `background:#e9ecef` — the CSS wins on font-weight/size/color
> but the Python inline style wins on background color (`#e9ecef`).

---

## VIEW 3 — Test Lab

```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│  BANNER  .sparmvet-banner                                                                     │
├───────────────────────────┬───────────────────────────────────────────┬───────────────────────┤
│  LEFT SIDEBAR             │  CENTRAL THEATER                          │  RIGHT SIDEBAR        │
│  #nav_sidebar             │  div.theater-container-main               │  #audit_sidebar       │
│  (standard accordion)     │                                           │  (Dev Inspector)      │
│                           │                                           │                       │
│ ╔═══════════════════════╗ │ ┌───────────────────────────────────────┐ │ ┌───────────────────┐ │
│ ║  Nav Pills Strip      ║ │ │  VIEW TITLE BANNER                    │ │ │  Dev Inspector    │ │
│ ╚═══════════════════════╝ │ │  div.view-title-banner                │ │ │  card             │ │
│                           │ │  "Test Lab: Synthetic Engine"         │ │ └───────────────────┘ │
│ ┌───────────────────────┐ │ └───────────────────────────────────────┘ │                       │
│ │  Data Import          │ │ ┌───────────────────────────────────────┐ │                       │
│ │  accordion panel      │ │ │  Generation Configuration card        │ │                       │
│ └───────────────────────┘ │ │  + Environment Audit card             │ │                       │
│                           │ └───────────────────────────────────────┘ │                       │
└───────────────────────────┴───────────────────────────────────────────┴───────────────────────┘
```

### Test Lab — CSS selectors per panel

| Panel label | CSS selector | Notes |
|---|---|---|
| View title banner | `.view-title-banner` | Shared with Blueprint/Gallery |
| Left sidebar | same as Home view | Accordion panels shared |
| Dev Inspector card | `#audit_sidebar .card` | Right card |
| Dev Inspector header | `#audit_sidebar .card-header` | Title bar |

---

## VIEW 4 — Gallery

> ADR-057: Gallery filter sidebar is in persistent left `#nav_sidebar`. Main content is full-width.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│  BANNER  .sparmvet-banner                                                                     │
├───────────────────────────┬───────────────────────────────────────────┬───────────────────────┤
│  LEFT SIDEBAR             │  CENTRAL THEATER (full width)             │  RIGHT SIDEBAR        │
│  #nav_sidebar             │  div.theater-container-main               │  #audit_sidebar       │
│  (Gallery accordion)      │                                           │  (Gallery Explorer)   │
│                           │                                           │                       │
│ ╔═══════════════════════╗ │ ┌───────────────────────────────────────┐ │ ┌───────────────────┐ │
│ ║  Nav Pills Strip      ║ │ │  VIEW TITLE BANNER                    │ │ │  Gallery Explorer │ │
│ ╚═══════════════════════╝ │ │  div.view-title-banner                │ │ │  card             │ │
│                           │ │  "📚 Gallery Inspiration"             │ │ └───────────────────┘ │
│ ┌───────────────────────┐ │ └───────────────────────────────────────┘ │                       │
│ │  🖼️ Recipe            │ │ ┌───────────────────────────────────────┐ │                       │
│ │  accordion panel      │ │ │  Preview accordion                    │ │                       │
│ │  #gallery_sidebar_    │ │ │  #gallery_preview_accordion           │ │                       │
│ │  accordion            │ │ │  header bg: #f8f9fa                 │ │                       │
│ │  #gallery_recipe_     │ │ │  body (flush): #gallery_tech_tabs     │ │                       │
│ │  select + clone btn   │ │ │  Plot Preview / Data Sample / YAML    │ │                       │
│ └───────────────────────┘ │ └───────────────────────────────────────┘ │                       │
│ ┌───────────────────────┐ │ ┌───────────────────────────────────────┐ │                       │
│ │  🔍 Gallery Taxonomy  │ │ │  Guidance accordion                   │ │                       │
│ │  accordion panel      │ │ │  #gallery_guidance_accordion          │ │                       │
│ │  Family / Pattern /   │ │ │  "📖 Visual Cookbook: Guidance"       │ │                       │
│ │  Difficulty /         │ │ │  yellow note aesthetic (#fff9c4)      │ │                       │
│ │  Geom / Show /        │ │ │  .gallery-md-pane (md content)        │ │                       │
│ │  Sample Size filters  │ │ └───────────────────────────────────────┘ │                       │
│ │  .gallery-sidebar-    │ │                                           │                       │
│ │  group (×6)           │ │                                           │                       │
│ │  [▶ Apply]            │ │                                          │                       │
│ └───────────────────────┘ │                                           │                       │
└───────────────────────────┴───────────────────────────────────────────┴───────────────────────┘
```

### Gallery — CSS selectors per panel

| Panel label | CSS selector | Notes |
|---|---|---|
| Gallery sidebar accordion | `#gallery_sidebar_accordion` | Recipe + Taxonomy panels |
| Gallery taxonomy filters | `.gallery-sidebar-group` | ×6 filter groups (ADR-063: 6-axis taxonomy) |
| Gallery filter title | `.gallery-filter-title` | 0.85rem/700/uppercase labels |
| Recipe selector + clone | `#gallery_recipe_select`, `#btn_clone_gallery` | Inside sidebar accordion |
| View title banner | `.view-title-banner` | "📚 Gallery Inspiration" |
| Preview accordion | `#gallery_preview_accordion` | bslib accordion |
| Preview accordion header | `#gallery_preview_accordion .accordion-button` | bg `#f8f9fa`, §14 |
| Preview accordion body | `#gallery_preview_accordion .accordion-body` | `padding: 0` (flush) |
| Preview accordion item | `#gallery_preview_accordion .accordion-item` | `border: none`, radius 8px (§14) |
| Preview tabs | `#gallery_tech_tabs` | `navset_card_tab` inside preview body |
| Guidance accordion | `#gallery_guidance_accordion` | Yellow note aesthetic (§17) |
| Guidance header | `#gallery_guidance_accordion .accordion-button` | bg `#fff3c4`, text `#345beb` |
| Guidance body | `#gallery_guidance_accordion .accordion-body` | bg `#fff9c4` |
| Guidance content | `.gallery-md-pane` | Markdown render — images, headings, tables |
| Gallery Explorer card | `#audit_sidebar .card` | Right card (placeholder) |

---

## Quick Reference — Colors in use

| Role | Color | Selector(s) |
|---|---|---|
| Primary blue (buttons, active pills) | `#345beb` | `.btn-primary`, `.nav-pills .nav-link.active`, `#btn_apply` |
| Primary blue hover | `#2a4bc4` | `.btn-primary:hover` |
| Export / teal | `#10a395` | `#export_*`, `#btn_export`, `#filter_add_row`, upload buttons |
| Reset / amber | `#ffc107` | `#filter_reset`, `.recipe-pending-badge` |
| Sidebar accordion header | `#a0a0a0` | `#nav_sidebar .accordion-button` |
| Audit card header bg / text | `#ffffff` bg / `#345beb` text | `#audit_sidebar .card-header` — **was #a0a0a0, fixed 2026-05-03** |
| Inactive nav-pill links | `#345beb` | `#nav_sidebar .nav-pills .nav-link:not(.active)`, theater pill/tab links |
| Session delete buttons | `#ffc107` amber | `[id^="session_delete_"]` — matches Pending badge amber |
| Sidebar body bg | `#c0c0c0` | `--bslib-sidebar-bg` |
| Page background | `#d1d1d1` | `body` |
| Theater header / spv-panel | `#ffffff` | `.theater-header-strip`, `.spv-panel`, `.view-title-banner` |
| Theater accordion (collapsed hdr) | `#f8f9fa` | `.theater-container-main .accordion-button` (§18) |
| Theater accordion (expanded hdr) | `#ffffff` | `.theater-container-main .accordion-button:not(.collapsed)` (§18) |
| Blueprint Glimpse header (inline) | `#e9ecef` | Python inline style — overrides §18 bg |
| TubeMap accordion header | `#f8f9fa` bg / `#345beb` text | `#blueprint_tubemap_accordion .accordion-button` (§9) |
| Audit node T2 | `#eef0fb` (blue tint) | `.audit-node-tier2` |
| Audit node T3 | `#e6f7f5` (teal tint) | `.audit-node-tier3` |
| Gallery guidance bg | `#fff9c4` (yellow) | `#gallery_guidance_accordion .accordion-body` |
| Checked radio/checkbox | `#345beb` | `#nav_sidebar .radio input:checked`, `.theater-header-strip .form-check-input:checked` |

---

## Typography scale

| Tier | Size | Weight | Used for |
|---|---|---|---|
| Primary | `0.85rem` | `700` | Accordion buttons, section headings, badges |
| Secondary | `0.80rem` | `400–600` | Body content, form labels, filter choices |
| Micro | `0.65rem` | `400` | Helper text, dtype labels, meta |

---

## Known dead CSS rules (safe to clean up later)

| Selector | File location | Why dead |
|---|---|---|
| `#central_theater_tabs.card.navset-card-tab` | `theme.css` §2 line 76, §9 lines 285–286 | ID removed from Python (pre-existing) |
| `#central_theater_tabs > .card-header .nav-tabs` | `theme.css` §5 line 137 | Same |

---

## CSS sections reference

| § | Title | Key targets |
|---|---|---|
| 1 | Layout & Backgrounds | `body`, `#main_layout_*`, `.central-theater`, `.spv-panel` |
| 2 | Panel Token | `.spv-panel`, `.theater-container-main .card`, `.audit-node-*` |
| 3 | High-Density Nav Sidebar | `#nav_sidebar` — all accordion + form elements |
| 4 | Sidebar Toggle | `.collapse-toggle` |
| 5 | Global Card & Theatre Polish | `.central-theater .card-header`, `#audit_sidebar` |
| 6 | Button Harmonization | `.btn-primary`, `#btn_apply`, teal export buttons, amber reset |
| 7 | Ingest & Upload UI | `.upload-row`, `#nav_sidebar .input-group` |
| 8 | Header Controls | `.active-view-btn`, `.control-btn`, `.ultra-small` |
| 9 | Wrangle Studio | `#architect_internal_tabs`, `#blueprint_tubemap_accordion` |
| 10 | Comparison Theater | `.reference-pane`, `.active-pane` |
| 11 | Column Picker | `.column-picker-container`, `#acc_home_data .accordion-body` |
| 12 | Structural Gaps & Layout | `.bslib-sidebar-layout`, `.theater-container-main`, `.theater-header-strip`, `.view-title-banner` |
| 13 | Gallery Sidebar & Filter UI | `.gallery-filter-title`, `.gallery-sidebar-group`, `#gallery_taxonomy_sub_accordion` |
| 14 | Gallery Theater accordions | `#gallery_preview_accordion`, `#gallery_guidance_accordion` header/item rules |
| 15 | Scientific Table | `table`, `th`, `td`, zebra rows |
| 16 | Theater & Audit Typography | `#audit_sidebar` headings, `.audit-node-*`, `#acc_home_data .accordion-button` |
| 17 | Guidance Pane Content | `.gallery-md-pane` — headings, blockquote, tables, images |
| 18 | Accordion normalization | `.theater-container-main` + `.wrangle-studio-container` accordion global rules; Bootstrap collapse cards in Blueprint |
