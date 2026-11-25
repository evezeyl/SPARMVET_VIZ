# Panel: the widths of the three panels of the app frame (coordinator, 2026-11-20)

## The owner's words (2026-11-20)
"At 1100 px the plot is only 316 px wide, this will be horrible the side panel is too big - we need at least half of the px on the main panel (if not 2/3) - then the rest need to be split in the left and right panel - not necessarily equally but close I guess - so we need a solution for that ... so have the software design and user agents work together to propose good solutions here"

So the TARGET is hers: the main (centre) panel gets at least 1/2 of the window width, better 2/3; the rest is split between the left and right panel, close to equal. HOW is open. The panel recommends; she decides.

## Facts (scout, by reading; "wt" = worktree .claude/worktrees/home-walk-fixes)
DECIDED
- Gaps between sidebars, theater and cards are 10 px (rules_ui_dashboard.md:77; theme.css:393-394).
- Sidebars use collapsible accordions and high-density inputs (rules_ui_dashboard.md:78).
- When the right sidebar is excluded (app features without it), the centre takes the full width (ADR-044; ui.py:371-377).
- One slot registry for every sidebar (D-0011).
- ADR-029c text: "Sidebars must be 'Collapsible' (Open by default on Desktop) to allow the Theater to occupy 100% of the width during visualization." Its status line says PROPOSED: CONFIRM.
- ADR-062 (accepted): the sidebar toggle is positioned by bslib; `.collapse-toggle` only gets scale and z-index (theme.css:143-146).
- No CDN, all CSS in config/ui/theme.css, only colours/sizes of rules_css_style_spec.md.

AS BUILT
- One frame for all four user spaces: app/src/ui.py:348-399 (`ui.layout_sidebar`, nested). Left: `ui.sidebar(width="340px", id="nav_sidebar")` (ui.py:364). Right: `ui.sidebar(width="340px", id="audit_sidebar", position="right")` (ui.py:384). Fixed px, no min/max, no percent, no `open=` argument; bslib's default collapse toggle exists; no collapsed state is kept.
- The right sidebar is present or absent for ALL spaces from HOME's config only (ui.py:378).
- No `@media` rule in theme.css. The wt adds one container query for the header strip only (theme.css:365-371).
- Left content: accordion panels; `.shiny-input-container` keeps Shiny's 300 px default on purpose (theme.css:101-104); filter operator select `width="100px"` (filter_and_audit_handlers.py:399). Right content (HOME): audit cards, Apply button.
- Plot: `ui.output_plot(height="480px")`, width = the centre (home_theater.py:982). Compare: two panes `col_widths=[6, 6]`, height 440 px (home_theater.py:962-972).
- Measured by the builder in a browser (not by the scout): at 1100 px the theater is about 400 px wide, the plot image 316 px.
- Tests: test_shiny_smoke.py:238 (right sidebar absent in static); wt test_home_strip_narrow.py (strip at 1100/1300/1600 px). No test pins a sidebar or plot width.

NOT STATED anywhere
- A sidebar width, a minimum window width, a responsive rule, a resize rule, which panel yields first, whether the user may choose.

## What each viewpoint answers (one round, at most 250 words, plus a small table of options)
Propose 2 to 4 concrete options that reach her target (centre >= 1/2, better 2/3) at window widths 1100, 1366, 1600 and 1920 px, with the numbers each option gives for left / centre / right at those widths, with and without the right sidebar, and in Compare (two plots side by side in the centre). Consider at least: proportional widths with a floor and a ceiling (clamp); narrower fixed widths; a side panel that closes by itself under a window width (and opens over the content); user-resizable panels. Say what breaks inside the side panels at the narrow width each option gives (the 300 px input containers, the filter form, the audit cards). Say what the user sees and must do. State what needs a rule added to rules_css_style_spec.md. Name the pitfalls. Recommend one.
Scratch checks only under tmpAI/panel/panel_widths/. Do not edit the repository. Never read tmp.md.
