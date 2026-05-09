---
trigger: always_on
deps:
  provides: [rule:css_design_tokens, rule:typography_scale, rule:color_palette, rule:button_catalog]
  documents: [config/ui/theme.css]
  consumed_by: [.claude/rules/rules_ui_dashboard.md, .claude/rules/ui_implementation_contract.md]
---

# SPARMVET CSS Style Specification (rules_css_style_spec.md)

**Authority:** @dasharch  
**Status:** ACTIVE — enforced immediately.  
**Source of truth:** `config/ui/theme.css` — read this file; this spec documents WHY each token exists.

**Agent rule:** Before writing a single CSS rule, check this file. If a color, size, or shape you need is not listed here, HALT and ask Eve before inventing one.

---

## 1. Color Palette

### 1a. Background & Surface

| What it looks like | Hex | Where used | Rule |
|---|---|---|---|
| Medium grey page background | `#d1d1d1` | Body, outer layout | Page wash — never override on individual panels |
| Darker grey for sidebars | `#c0c0c0` | Left + right sidebars (`--bslib-sidebar-bg`) | Sidebars are visually recessed vs body |
| White card surface | `#ffffff` | Cards, panels, expanded accordions, theater elements | All content lives on white |
| Near-white neutral | `#f8f9fa` | Collapsed accordion headers, reference pane, blueprint tubemap bg | Not white, not grey — "inactive surface" |
| Very light neutral | `#fafafa` | `.spv-info-bg` utility | Barely-visible inner panel tint |

### 1b. Borders

| Description | Hex | Where used |
|---|---|---|
| Card / panel / theater header border | `#e9ecef` | All `.spv-panel`, `.theater-header-strip`, nav pill strip |
| Table / comparison pane border | `#dee2e6` | Tables, comparison theater pane, input borders in chat panel |
| Sidebar accordion item border | `#d0d0d0` | `#nav_sidebar .accordion-item` |
| Sidebar accordion button underline | `#909090` | Collapsed accordion button bottom border in nav sidebar |

### 1c. Brand / Action Colors

| Color | Hex | Hover Hex | Category | Used for |
|---|---|---|---|---|
| **SPARMVET Blue** | `#345beb` | `#2a4bc4` | Primary action | Buttons, active tabs, headings in cards, focus rings |
| **SPARMVET Teal** | `#10a395` | `#0d8a7e` | Export / upload | Export bundle, upload, filter "+ Add row" |
| **SPARMVET Amber** | `#ffc107` | `#e0a800` | Discard / pending | Reset, session delete, pending badge, "send to audit" |
| **SPARMVET Error Red** | `#d62828` | `#b91c1c` | Error / destructive | Error banners, danger-delete modal, critical alerts |

**FORBIDDEN Bootstrap defaults:** `#0d6efd` (Bootstrap primary), `#198754` (success), `#dc3545` (danger). If Bootstrap injects any of these, override with the palette above using `!important`.

### 1d. Text Colors

| Description | Hex | Where used |
|---|---|---|
| Main dark text | `#1a1a1a` | Sidebar labels, accordion button text, most body text |
| Sidebar form label | `#333` | `#nav_sidebar label` rules |
| Brand blue as text | `#345beb` | Card headers, gallery accordion button text, active link text |
| Muted / helper text | `#6c757d` | `.ultra-small`, subtitles, dtype labels, `.banner-subtitle` |
| Text on white buttons (amber) | `#000` | Amber buttons — black for contrast |
| Text on colored buttons (blue/teal) | `#ffffff` | Primary and teal buttons |

### 1e. Status / Semantic Colors

These are the ONLY allowed values for informational banners (connected/error/busy states).
**NEVER use Bootstrap green `#d4edda`/`#155724` or Bootstrap red `#f8d7da`/`#721c24`.**

| State | Background | Text | Rationale |
|---|---|---|---|
| OK / connected | `#d5efec` | `#0b6358` | Teal 10% tint — stays in brand palette |
| Busy / loading | `#fff3cd` | `#856404` | Amber tint — same family as pending/warning |
| Error / disconnected | `#ffe0e0` | `#d62828` | Error red 20% tint with error red text — distinct from warning/pending |

**Error red:** `#d62828` is now the dedicated error color in the SPARMVET palette. Use it for error banners, danger-delete modals, and critical alerts that require clear distinction from the amber warning/pending state.

### 1f. Component-Specific Colors (do not reuse in other contexts)

| Token | Hex | Only used for |
|---|---|---|
| Audit Tier 2 node bg (Violet) | `#eef0fb` | T2 inherited nodes in audit stack; user messages in chat panels |
| Audit Tier 3 node bg (Teal-tint) | `#e6f7f5` | T3 user nodes in audit stack |
| Gallery guidance note (yellow) | `#fff9c4` | `#gallery_guidance_accordion` pane only |
| Gallery guidance border | `#f0e68c` | Same pane border |
| Gallery guidance text | `#5f5a3a` | Text inside guidance pane |
| Gallery note header bg | `#fff3c4` | Guidance accordion button collapsed |
| Comparison reference badge | `#fff3cd` bg / `#856404` text / `#ffbc00` border | "REFERENCE" label chip in comparison theater |
| Reference pane bg | `#f8f9fa` | Comparison reference column background |
| Scientific table border | `#cbd5e1` | `.central-theater` table/td/th borders (Slate-300 — stable since §15) |
| Scientific table header bg | `#f1f5f9` | `th` inside central theater tables (Slate-100) |
| Scientific table even-row bg | `#f8fafc` | Even rows in `.central-theater` table (Slate-50) |
| Gallery guidance table border | `#c8b96a` | Tables inside `.gallery-md-pane` (golden, matches note theme) |
| Gallery guidance blockquote border | `#c8b86a` | Left-border accent in guidance blockquote |
| Gallery guidance h2 color | `#3b3620` | Dark olive — recipe title in guidance pane |
| Gallery guidance even-row | `#fffde7` | Even rows in guidance table |
| Gallery guidance row hover | `#fff8a0` | Row hover in guidance table |
| PK-warn badge border | `#ffeeba` | `.spv-badge-pk-warn` border |
| Propagation badge (pending fix) | `#cfe2ff` bg / `#0a3678` text | `.spv-badge-propagation` — **Bootstrap info colors, added today (§20). Should be migrated to `#eef0fb` bg / `#345beb` text in next session.** |

---

## 2. Typography Scale

All text in the application follows exactly this scale. **No other sizes are permitted.**

| Level | `rem` | `weight` | Named uses |
|---|---|---|---|
| **Primary** | `0.85rem` | 700 | Accordion buttons, card headers, gallery filter titles, section headings |
| **Secondary** | `0.80rem` | 400/600 | Body text, form content, input labels, filter rows |
| **Sub-secondary** | `0.78rem` | 400 | Gallery blockquotes, small labels |
| **Small** | `0.75rem` | 400 | Badges, `.spv-text-xs`, recipe-pending-badge text in audit sidebar |
| **Micro** | `0.65rem` | 400 | `.ultra-small`, dtype labels, helper/meta annotations |

Special cases (allowed and documented):
- `1.0rem` / 700 — gallery h1/h2 recipe titles, `.banner-title` in view-title-banner
- `0.9rem` — **FORBIDDEN** (outside scale; was introduced in today's agent error — already fixed)

**Font weight:** Only 400 (regular), 600 (medium), 700 (bold). Never 500, 800, 900.  
**Text-transform uppercase:** Only on gallery filter titles and comparison "REFERENCE" badge. Never on accordion buttons or form labels.

---

## 3. Shape & Sizing

### 3a. Border Radius

| Shape | Value | Where used |
|---|---|---|
| Panel / card | `8px` | `.spv-panel`, theater `.card`, view-title-banner, `.bp-agent-container` |
| Accordion item (theater) | `8px` | `#acc_home_data .accordion-item`, gallery accordions |
| Accordion item (sidebar) | `6px` | `#nav_sidebar .accordion-item` |
| Buttons | `6px` | All action buttons (primary, teal, amber) |
| Small components (badges, inputs) | `3px`–`4px` | Sidebar inputs (`3px`), chat input (`4px`), small badges (`3px`) |
| Round spinner | `50%` | `.bp-agent-status-banner .spinner` |

### 3b. Height (Vertical Size)

| Component | Height | Where |
|---|---|---|
| Primary action buttons | `32px` | `#btn_apply`, `#filter_add_row`, export buttons, etc. |
| Control buttons (compact) | `28px` | `.control-btn` header area |
| Sidebar form inputs / selects | `26px` | `#nav_sidebar .form-select`, `.form-control` |
| Theater header strip | `44px` min | `.theater-header-strip` |
| Nav pill strip | `44px` min | `#nav_sidebar .flex-column > .bg-white` |

### 3c. Gap & Spacing

| Property | Value | Context |
|---|---|---|
| Layout gap (sidebars ↔ theater) | `10px` | `--bslib-sidebar-gap`, `.bslib-grid gap` |
| Theater internal padding | `10px` | `.theater-container-main` |
| Card shadow | `0 1px 4px rgba(0,0,0,0.08)` | All `.spv-panel`, `.theater-header-strip` |
| Sidebar label bottom margin | `5px` | `#nav_sidebar label` |
| Sidebar input bottom margin | `4px` | `#nav_sidebar .shiny-input-container` |

---

## 4. Button Catalog

Every button in the application belongs to exactly one of five types.
Add new buttons by finding the right type — never invent a new color.

### Type 1 — Primary Action (Blue)

> Default for "do something meaningful." Blue = committed, safe, forward-moving action.

- **Color:** `#345beb` bg, `#2a4bc4` hover, white text
- **Size:** `height: 32px`, `border-radius: 6px`, `font-weight: 600`
- **IDs:** `#btn_apply` (base state), `#btn_revert_sync`, `#btn_ingest`, `#restore_session`, `#btn_save_internal`, `#btn_autofill_meta`, `#btn_generate_data`, `#btn_apply_gallery_filters`

### Type 2 — Export / Upload / Ingest (Teal)

> Actions that produce output or bring data in. Teal = data flows across a boundary.

- **Color:** `#10a395` bg, `#0d8a7e` hover, white text
- **Size:** `height: 32px`, `border-radius: 6px`, `font-weight: 600`
- **IDs:** `#export_bundle_download`, `#filter_add_row`, `#btn_export`, `#btn_upload_replace`, `#btn_upload_append`, `#btn_import_manifest`, `#session_export_active`

### Type 3 — Discard / Delete / Reset (Amber)

> Destructive or state-clearing actions. Amber = stop and think, not irreversibly dangerous.

- **Color:** `#ffc107` bg, `#e0a800` hover, **black text** (`#000`)
- **Size:** `height: 32px`, `border-radius: 6px`, `font-weight: 700`
- **IDs:** `#filter_reset`, `[id^="session_delete_"]`

### Type 4 — Pending / Audit Action (Amber Badge)

> The apply button or "send to audit" state when changes are staged. Visually identical to
> Type 3 amber but rendered as a badge-like element with a specific class.

- **Color:** `#ffc107` bg, `#e0a800` border, black text
- **Class:** `.recipe-pending-badge`
- **Usage:** Replaces or accompanies `#btn_apply` when `recipe_pending == True`. The badge
  signals "there are uncommitted changes — press to apply."

### Type 5 — Disabled / Inactive (Grey)

> Button is present but not actionable (e.g. `#btn_apply` with missing audit comments).

- **Color:** Bootstrap default disabled grey (`#b0b0b0` bg equivalent), cursor not-allowed
- **Applied via:** `disabled` HTML attribute on the button element — CSS handles it natively.
  Do not override disabled styles with custom colors.

---

## 5. Chat / Conversational Panel Pattern

When building any panel that shows a message history (e.g. Blueprint Agent chat):

```css
/* Container */
.my-panel-container {
    background-color: #ffffff;
    border-radius: 8px;             /* panel radius */
    overflow: hidden;
}

/* Message log */
.my-panel-messages {
    background-color: #f8f9fa;      /* surface-neutral */
    font-size: 0.85rem;             /* Primary scale */
}

/* User message bubble */
.my-panel-message.user {
    background-color: #eef0fb;      /* audit-tier2-bg — in-palette */
    color: #1a1a1a;                 /* text-primary-dark */
}

/* System/agent message bubble */
.my-panel-message.agent {
    background-color: #f5f5f5;
    color: #1a1a1a;
}

/* Input field */
.my-panel-input-area input {
    border: 1px solid #dee2e6;      /* border-table */
    font-size: 0.8rem;              /* Secondary scale */
}

/* Send button → always Type 1 Primary */
.my-panel-input-area button {
    background-color: #345beb;
    color: #ffffff;
    font-size: 0.85rem;
    font-weight: 600;
}
.my-panel-input-area button:hover {
    background-color: #2a4bc4;      /* primary-hover — NOT #2643c7 */
}
```

---

## 6. Accordion Header Pattern

| Context | Collapsed bg | Expanded bg | Text color | Shadow on expand |
|---|---|---|---|---|
| `#nav_sidebar` | `#a0a0a0` | same | `#1a1a1a` | none |
| Theater / WrangleStudio main | `#f8f9fa` | `#ffffff` | `#1a1a1a` | `none !important` |
| Gallery Preview | `#f8f9fa` | `#ffffff` | `#345beb` | `none !important` |
| Gallery Guidance note | `#fff3c4` | `#fff9c4` | `#345beb` | `none !important` |
| Blueprint TubeMap | `#f8f9fa` | `#ffffff` | `#345beb` | `none !important` |
| Data preview (`#acc_home_data`) | `#f8f9fa` | `#ffffff` | `#345beb` | — |

All accordion buttons: `font-size: 0.85rem !important`, `font-weight: 700 !important`.  
Always add `box-shadow: none !important` on `:not(.collapsed)` to remove Bootstrap's inset shadow.

---

## 7. Status / Info Banner Pattern

For any banner that shows adapter state, connection status, or informational messages:

```css
.my-banner { font-size: 0.8rem; border-radius: 4px; padding: 8px 10px; }
.my-banner.ok    { background-color: #d5efec; color: #0b6358; }  /* teal tint */
.my-banner.error { background-color: #fff3cd; color: #7a4100; }  /* amber, dark text */
.my-banner.busy  { background-color: #fff3cd; color: #856404; }  /* amber */
```

Do NOT use `#d4edda`/`#155724` (Bootstrap success) or `#f8d7da`/`#721c24` (Bootstrap danger).

---

## 8. Common Violations

Agents frequently introduce these — all are FORBIDDEN:

| What an agent wrote | Why it's wrong | Correct value |
|---|---|---|
| `font-size: 0.9rem` | Outside typography scale | `0.85rem` |
| `color: #0d47a1` | Material Design Blue — not SPARMVET | `#1a1a1a` or `#345beb` |
| `background-color: #e3f2fd` | Material Design Blue 50 | `#eef0fb` |
| `background-color: #d4edda` | Bootstrap success green | `#d5efec` |
| `color: #155724` | Bootstrap success dark | `#0b6358` |
| `background-color: #f8d7da` | Bootstrap danger red | `#fff3cd` |
| `color: #721c24` | Bootstrap danger dark | `#7a4100` |
| `background-color: #0d6efd` | Bootstrap primary blue | `#345beb` |
| Button hover `#2643c7` | Inconsistent — off by one blue | `#2a4bc4` |
| Border `#d0d0d0` or `#e0e0e0` | Off-palette border | `#dee2e6` |
| Missing `!important` on button styles | Python `style=` overrides CSS | Add `!important` |

---

## 9. Panel & Surface Catalog

Every distinct "container" in the app maps to one of these named surfaces. When you add a new
panel in Python (Shiny), decide which surface type it is before writing any CSS.

### 9a. spv-panel (Standard Content Card)

The default white card for any content area. Add `class="spv-panel"` to the wrapping div.

```
bg: #ffffff | border: 1px solid #e9ecef | radius: 8px | shadow: 0 1px 4px rgba(0,0,0,0.08)
```

All `.card` and `.accordion-item` inside `.theater-container-main` inherit this look automatically.

### 9b. Theater Header Strip

The white pill bar at the top of the Home Theater (holds tier toggle radio buttons).

```
bg: #ffffff | border: 1px solid #e9ecef | radius: 8px | shadow: 0 1px 4px rgba(0,0,0,0.08)
min-height: 44px | padding: 6px 14px | margin-bottom: 10px
```

Class: `.theater-header-strip`

### 9c. View Title Banner

Heading card used at the top of Blueprint, Gallery, Test Lab workspaces.

```
bg: #ffffff | border: 1px solid #e9ecef | radius: 10px | shadow: 0 1px 4px rgba(0,0,0,0.08)
padding: 10px 18px | margin-bottom: 12px
.banner-title:  font-size 1.0rem / weight 700 / color #345beb
.banner-subtitle: font-size 0.78rem / weight 400 / color #6c757d
```

Class: `.view-title-banner`

### 9d. Comparison Panes

Two side-by-side panels in comparison mode.

| Pane | bg | border | radius | padding |
|---|---|---|---|---|
| Reference (left, read-only) | `#f8f9fa` | `1px solid #dee2e6` | `6px` | `6px` |
| Active (right, T3 sandbox) | `#ffffff` | `1px solid #dee2e6` | `6px` | `6px` |

Reference pane has subtle inset shadow: `box-shadow: inset 0 0 10px rgba(0,0,0,0.02)`.

Classes: `.reference-pane`, `.active-pane`

### 9e. Audit Nodes (T2 / T3)

Small tag-like blocks inside the audit stack.

| Node type | bg | radius | padding | font-size |
|---|---|---|---|---|
| T2 inherited (Violet) | `#eef0fb` | `4px` | `2px 6px` | `0.8rem` / weight 400 |
| T3 user (Teal-tint) | `#e6f7f5` | `4px` | `2px 6px` | `0.8rem` / weight 400 |

Classes: `.audit-node-tier2`, `.audit-node-tier3`

### 9f. Gallery Guidance Pane (Note aesthetic)

Soft yellow "note" look to signal educational/guidance content.

```
bg: #fff9c4 | border: 1px solid #f0e68c | radius: 7px
text: #5f5a3a | header bg: #fff3c4
```

ID: `#gallery_guidance_accordion`

---

## 10. Tab & Navigation Patterns

### 10a. Nav Pills (workspace switcher + group tabs)

Active pill: `bg #345beb`, white text, same border-color.  
Inactive pill: text `#345beb`, transparent bg.

Applied to: workspace nav in `#nav_sidebar`, Home analysis group tabs (`.theater-container-main`).

### 10b. Nav Tabs / Underline Tabs (plot sub-tabs)

All nav-tab links in theater: text `#345beb`, no special bg.  
Active tab is handled by Bootstrap (underline or highlight) — do not override the active indicator.

Applied to: plot sub-tabs within each analysis group accordion.

### 10c. Navset Card Tab (Blueprint / WrangleStudio)

`#central_theater_tabs.card.navset-card-tab` — borderless, full-height, fills viewport.

```
border: none | radius: 0 | box-shadow: none | height: calc(100vh - 4px)
```

The `card-body` inside is `overflow-y: auto` to allow scrolling within the theater.

---

## 11. Adding a New CSS Section

When adding a new `/* ── N. Section Name ── */` block to `config/ui/theme.css`:

1. Use only colors from §1 of this spec. New colors require user confirmation.
2. Use only font sizes from §2. `0.9rem` is forbidden.
3. Use border-radius from §3a. Default for new panels: `8px`.
4. For any button: classify into the five types in §4. No sixth type without user confirmation.
5. Update the `Sections` comment block at the top of `theme.css` (lines 9–27).
6. Write a one-line comment explaining which UI element the rules target.
7. Run the hex audit:
   ```bash
   grep -oE '#[0-9a-fA-F]{6}' config/ui/theme.css | sort -u
   ```
   Compare output against §1. Any unlisted hex is a candidate violation.
