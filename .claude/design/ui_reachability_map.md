# UI reachability map: where is a cross-cutting surface guaranteed to exist?

**Status:** new (2026-11-08). Prompted by a real miss: the panel now called "Processing Issues"
(originally "Pipeline Issues" — see the rename below) was built as a right-sidebar-only output,
but the right sidebar is structurally absent in two shipped app features files — so the panel
would have been unreachable there even before anyone noticed it was never mounted at all.

**Purpose:** before adding any UI surface meant to be seen regardless of which app features or
deployment is running — error/diagnostic panels, anything the project calls "always visible" —
check this table first. It answers one question only: *which structural containers exist in every
configuration, and which don't.* It does not replace `rules_app_features_flags.md` (the
authoritative flag matrix and cascade rules) or `ui_implementation_contract.md §11` (the sidebar
slot registry) — it is a derived quick-reference built from both, kept narrow on purpose.

**Does not duplicate:** `.claude/design/app_features_capability_matrix.md` and
`functionality_dependency_map.md` map *user functionality* (can the user filter? export? see T3?)
to flags. This map is one layer lower — it maps *structural containers* (is there a left sidebar
at all? a right sidebar?) to configurations, independent of which functionality is turned on
inside them. Both older docs are dated 2026-05-05 and predate ADR-073's slot registry; this file
does not attempt to refresh them, only to add the angle they don't cover.

---

## 1. First question, answered once: is a fully static (no server) deployment ever possible?

**No.** `.claude/rules/dasharch.md §4`: "**STRICT:** NO WASM/SHINYLIVE. Ensure standard
server-side execution compatibility." Every shipped `deployment_type` (`filesystem`, and per the
deployment template, `galaxy`/`irida`) runs a live Shiny server process. "`pipeline-static`" is an
app features *name* — it means most interactivity flags are off, not that the app is exported as
static HTML. There is no configuration, shipped or planned, where the page is pre-rendered and
served without a server. This matters here because it means every reachability question below is
about the app features's DOM, not about a genuinely static page with no reactive surface at all.

## 2. Structural containers, by presence

| Container | Present in every app features? | Absent in | Why |
|---|---|---|---|
| **Left sidebar** | **Yes, always** | — | Never excluded by any shipped app features file (`grep -rn "left_sidebar" config/app_features/ config/ui/sidebars/` finds no `visible: false`). Its *panel list* varies by the slot registry (`ui_implementation_contract.md §11`), but the container itself is unconditional. |
| **"Home" nav tab** | **Yes, always** | — | `sidebar_nav_ui` (`home_theater.py`) adds `ui.nav_panel("Home", ...)` with no flag check — the only nav item not gated. Blueprint/Test Lab/Gallery nav tabs are each gated on their own `*_enabled` flag. |
| **Right sidebar** | No | `pipeline-static`, `pipeline-exploration-simple` | `rules_app_features_flags.md` Group B: `workspaces.home.right_sidebar.visible` is `false` for these two — structural exclusion (the container is never created), not CSS-hidden. |
| **Native toast** (`ui.notification_show`, via `make_notifier()`) | **Yes, always** | — | Client-side Shiny mechanism, independent of DOM structure. Fires regardless of which sidebar exists. The transient part of every `_notify()` call always reaches the user; only the *persistent log* (see Alerts, below) depends on a sidebar existing to display it. |
| **Inline-on-content fallback** (e.g. "Data error: ..." drawn directly on the plot figure) | **Yes, always, for the specific surfaces that already do this** | — | Not a general mechanism — each render path has to build its own fallback. `_group_plot_handler`'s two `except` blocks already do this for data-materialization and VizFactory-render failures. Any *new* cross-cutting surface does not get this for free; it has to be written the same way, or placed in the left sidebar. |

## 3. What already uses which container, and whether that's a problem

| Surface | Lives in | Reachable everywhere? | Comment |
|---|---|---|---|
| Filters, Export, Session Management, Data Import panels | Left sidebar (gated per-panel by their own flag, per `ui_implementation_contract.md §11d`) | Reachable wherever their own flag is on | Correct pattern already — gated by *feature* flag, not by container absence. |
| Pipeline Audit / T3 audit stack | Right sidebar, gated `t3_sandbox_enabled` | No, by design | Correct: T3 audit genuinely doesn't exist as a concept in `pipeline-static`/`pipeline-exploration-simple` (no T3 sandbox there at all per the flag matrix), so the container absence matches the feature absence. Not a bug. |
| Alerts (`notification_log_panel_ui`) — persistent notification history | Right sidebar | Toasts: yes (native, see above). Persistent log: no, in `pipeline-static`/`pipeline-exploration-simple` | A real but narrower gap than it first looks: nothing is silently lost — the toast still fires everywhere — only the scroll-back history is unreachable in those two app features. Not evaluated further here; flagging it as the same shape of issue for awareness, not fixing it in this pass. |
| Processing Issues (`processing_issues_ui`, was "Pipeline Issues" / `pipeline_issues_ui` — renamed, F-26) | **Fixed, 2026-11-08: left sidebar**, new `processing_issues` panel type (`sidebar_registry.py`), `gate_flag: None`, added to the shared `home_standard_left.yaml` used by all 8 app features | **Yes, everywhere** — proven by `test_every_app_features_starts.py`'s per-app-features assertion, mutation-tested (removed the slot, confirmed `pipeline-static` fails, restored, confirmed it passes) | The finding that prompted this map. Previously built for the right sidebar and never mounted at all; also renamed throughout (code, UI label, ADRs, docs) to resolve the collision with `CTX-1`'s "Analysis pipeline" external actor. |

## 4. The rule to apply when building the next cross-cutting surface

1. **Does it need to be seen in every app features, including `pipeline-static`?** If yes: left
   sidebar, a native toast, or an inline-on-content fallback written for that specific render path.
   Never the right sidebar alone.
2. **Does it only make sense when a specific feature is on** (T3 audit, BLUEPRINT, Gallery)? Then
   it's correct for it to live wherever that feature's container already lives, including the
   right sidebar — its absence in other app features matches the feature's own absence, which is
   not a reachability bug, it's the feature being off.
3. When in doubt, check §2's container table first, then §3 for a worked example of the same
   shape of decision.

## 5. Open, not resolved here

- The Alerts persistent-log gap (§3) — same shape of issue, not evaluated for a fix in this pass.
- Whether `notification_log` (ADR-060) should itself move, or gain a left-sidebar fallback for the
  two app features that lack it. Left as a question for whoever picks it up next.
