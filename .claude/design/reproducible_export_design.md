# Reproducible export & import — design discussion (2026-11-09)

**Status:** DISCUSSION — nothing in this document is implemented yet. Written to capture a
chat discussion that grew from issue #39 into five/six separable pieces of work, so none of
it is lost before filing issues. Decided by Eve, with @dasharch.

**Originating issue:** [#39](https://github.com/evezeyl/SPARMVET_VIZ/issues/39) — "Export
records what was actually used: the seed in effect and the data files." The discussion below
grew out of answering #39's own open questions.

---

## 1. What already exists (grounding — read this before building anything here)

Checked directly in code before any of the design below was proposed.

### 1a. Provenance/hash machinery — already substantially built

`app/handlers/export_handlers.py` (the function building the export's provenance dict, around
line 90-152) already computes, every export:

- `data_source_paths` — the actual file(s) used per dataset (via
  `orchestrator.get_source_files`), not the recipe's declared default `source.path`. Already
  correct for `data_lookup: by_dataset_id` and for Data-Import-replaced files.
- `decision_hashes` — per-dataset `tier1_key` (ADR-089 chained content hash), from the stage
  keys the export itself used, or from stored Parquet metadata.
- `data_analysis_recipe_sha256` — file-set hash of the recipe + every `!include`d file
  (independently verifiable with `sha256sum`).
- `data_batch_hash` — content hash of the source data files.
- `git_commit`, `release_version`, `software_versions` — already captured.

**So the "data actually used, with hashes" half of #39 is largely done already.** The real
gap in #39 itself is narrower than it first read: the **seed**, plus pulling what already
exists into one consolidated, human-checkable record.

### 1b. Human-readable T3 description — already built, for Mode 1

`export_handlers.py`'s Methods-section generator (the function starting "Return QMD lines for
the auto-generated Methods section", ~line 290) already turns every T3 node into a plain
sentence: `"Rows were filtered where **column** is at least "value"."`, with the node's
`reason` appended (`ui_implementation_contract.md §12f`). This already satisfies "a simple
description of the T3 steps, readable for a paper" — nothing new needed for that half of
chunk D below. What's missing is the *machine-executable* counterpart (§4D).

### 1c. The random seed — not recordable today (the actual gap in #39)

`libs/viz_factory/src/viz_factory/viz_factory.py`: `DEFAULT_RANDOM_STATE = 0`,
`_generator(seed)`, `_seed_random_components(...)`. `random_state: random` (or `null`) means
"use numpy's global RNG" — genuinely un-recoverable after the render. Nothing records which
number was drawn. This is the real content of #39.

### 1d. T3 is session-only — no engine-level replay mechanism exists

T3 filter/drop application (`app/modules/t3_audit_engine.py`'s `_apply_filter_rows`, the
per-plot audit application in `home_theater.py`) runs *inside the running Shiny session*,
reading `home_state`. `ConfigManager`/`DataAssembler` (the headless engine `debug_assembler.py`
runs) has never heard of a T3 node — it only understands registered wrangling actions
(`filter_range`, `filter_eq`, `drop_columns`, ...) declared in a recipe's `wrangling:` block.
**There is no path today from "a recipe file + a T3 step list" to "the T3-adjusted data"
without a live Shiny session.** This is the gap chunk D (§4D) closes.

### 1e. The Plot Style panel is built but deliberately unmounted

`ui_implementation_contract.md §12g.9`: the UI that authors `aesthetic_override` nodes exists
in code but is not mounted in HOME — a prior attempt broke the plot (fork issue #15). Relevant
to the reshuffle-button idea (§4F): any new button touching `aesthetic_override` needs its own
narrow UI, not a revival of that panel.

### 1f. TEST_LAB is the wrong home for bundle verification

`rules_test_lab.md` — TEST_LAB is gated by `test_lab_enabled`, built for people *preparing*
recipes/analyses (ID Reconciliation, AquaSynthesizer, scaffolding). The audience for "verify a
reproducibility bundle" may have none of that — may not even have `blueprint_enabled`. It needs
to live wherever Export already lives (`export_enabled`), as an **Import**, not a TEST_LAB tool
(§4E).

### 1g. Export scope today

Three-way `export_scope`: `global` / `group` (active analysis group) / `plot` (active plot
sub-tab) — `ui_implementation_contract.md §7.2`. Relevant to §4B: a reproducibility export
can't be partial, so it forces `global`.

---

## 2. The two export purposes, named

The discussion surfaced that "export" today conflates two genuinely different jobs:

| | **Mode 1 — Publication** (today's export, mostly unchanged) | **Mode 2 — Reproducibility / reimport** (new) |
|---|---|---|
| **For whom** | Someone writing a paper from the plots | Someone (possibly the same person, possibly someone else, possibly on a different computer) who needs to reconstruct and verify the result |
| **Scope** | Existing 3-way (global/group/plot) — a paper only needs the plots that are in it | Forced **global** — you cannot partially reconstruct a recipe |
| **T3 content** | Human prose in the Methods section (§1b, unchanged) — *why* a step was taken, for the reader of the paper | The actual replayable actions (§4D) — *what* must run to reproduce the data, for the engine |
| **Recipe copy** | **Open question** — kept as a lightweight reference, or dropped now that Mode 2 exists to carry it? | Yes, always — plus the data, the hashes, the seed record, the git commit |
| **Data** | Not needed | Needed — open question whether copied into the bundle or referenced+hashed (§4B) |

**Combined option, confirmed:** a single export action can also produce *both* bundles at
once inside one zip — "when you finish a project," per Eve. Not strictly either/or.

---

## 3. Sensitive data

Confirmed: this is a **documentation-level** mitigation, not a code-enforced one — the app
cannot know what counts as sensitive in a given dataset. Two things needed:

1. An in-app, non-blocking notification when building a Mode 2 (reproducibility/reimport)
   bundle, naming that the data will be copied/fully included and that this bundle is meant to
   be shared or moved to another computer.
2. A new section in the user guide / guidelines (`docs/user_guide/` — exact page TBD):
   recommend anonymising sensitive data *before* loading it into the app, and keeping any
   de-anonymisation key/mapping file **outside** the app entirely, as better practice than
   relying on the app to protect it.

---

## 4. The decomposition — six chunks

### 4A. Seed-in-effect recording (#39's core — narrowed)

- Per-plot seed (confirmed: not per-recipe — a recipe can have several independently-seeded
  plots).
- `random_state` added to the `aesthetic_override` **data shape** (T3 cascade L5) — the
  existing per-plot, session-level, no-recipe-edit, already-exported mechanism (`fill_color`,
  `alpha`, `shape`, ... already live there). This gives a pin/override path "for free."
- Automatic bookkeeping: for the default case (`random_state: random`, no explicit user
  override), a lightweight **non-audited** session value remembers the last seed actually
  drawn per plot, so Export reads back whatever is currently on screen rather than drawing a
  fresh (different) number at export time.
- Multi-jitter layers in one plot: keep today's behaviour (one shared seed per plot) — simplest,
  matches the per-plot granularity decision, correlated jitter between layers is cosmetic, not
  a correctness concern.
- Non-blocking warning notification when exporting with `random_state: random` still in effect
  and no user-pinned override — the export is still fully reproducible via the recorded draw,
  this is just a nudge toward pinning for a final/publication export.
- Consolidate into one small record (not a second full recipe) — `effective_run.yaml` (or
  similar name) listing: seed-in-effect per plot, and the already-existing provenance fields
  from §1a assembled in one place, plus `engine_fingerprint()` (polars/transformer versions +
  cache-version constant, `cache_keys.py` — needed as the third leg of hash verification, see
  §4E) and the git commit (already captured, §1a).

**Scope boundary:** no new UI. The capability (pin/override a seed) exists via the data shape;
whether/when a button appears is §4F, deliberately separate.

### 4B. Export mode split

- Two export actions (or one action with a mode choice) producing Mode 1 and/or Mode 2
  bundles, confirmed combinable into one zip.
- Mode 2 forces `export_scope: global`, with an explanation shown in the UI (why reimport
  needs everything).
- **Open:** does Mode 2 copy the actual data files into the bundle, or reference + hash them
  (today's behaviour)? Copying is needed for genuine portability to another computer; hashing
  only is needed for size/sensitivity. Possibly both, user's choice, with the sensitive-data
  notification (§3) shown when copying is chosen.
- **Open:** does Mode 1 keep a lightweight recipe reference now that Mode 2 exists, or drop it
  as redundant/"overkill" (Eve's word)?

### 4C. Sensitive-data warning + docs

See §3. Small, mostly documentation; the in-app half is one notification call at Mode-2
export time.

### 4D. T3 → recipe-action translator (the engine-facing piece)

The real new engineering work. Per §1d, T3 state is session-only; for Mode 2 to be genuinely
reproducible without a running Shiny session, each plot's committed T3 nodes need to become
real, registered wrangling actions appended into the frozen recipe copy — not just carried
along as an auxiliary YAML a human reads.

Confirmed requirements from this discussion:
- **Per-plot, dataset/join-aware**: T3 nodes are already scoped per plot
  (`t3_audit_steps_by_plot`); translated actions must attach to the correct dataset/join in the
  frozen recipe, not a single global block.
- **T2-may-be-absent edge case** (Eve: "T3 might exist while no T2"): per
  `rules_data_engine.md §1`, an empty `tier2` means T2 ≡ T1 — no tier2 block is materialized.
  The translator needs a rule for where translated actions go when the target dataset's join
  has no existing `tier2:` list to append to (create one in the frozen copy only, never in the
  live recipe on disk).
- **Mapping**: `exclusion_row`/`filter_row` → `filter_eq`/`filter_range`/etc. (the existing
  registered actions, `rules_agent_role_bioscientist.md §8` has the full list); `drop_column` →
  `drop_columns`; `aesthetic_override` is cosmetic, not translated (doesn't affect data);
  `developer_raw_yaml` is already a recipe fragment — closest to a direct copy.
- **Two outputs from one translation step, reusing what exists**: the human prose (§1b,
  already built, reuse as-is for Mode 1) and the new machine-executable actions (new, for Mode
  2's frozen recipe copy).
- **Read-back / provenance marking** (Eve: "read again... we do not read T3"): today there is
  no mechanism to even recognise, on reading a recipe back, which steps originated from a T3
  session versus which the recipe's author wrote directly. The frozen copy needs some marker
  convention (a YAML comment banner, similar in spirit to the project's existing
  `rules_legacy_management.md` DEPRECATED/HISTORICAL banners) so a human — or Blueprint, if a
  frozen copy is ever re-opened there — can tell translated-from-T3 steps apart from native
  recipe steps. Exact convention: **undecided, needs its own pass.**

This chunk is the most open-ended of the six and should probably be scoped and estimated on
its own before any of the others that depend on it (§4B's "Mode 2 recipe copy" and §4E's
"Import" both assume this translator exists and works).

### 4E. Import (paired with Mode 2 export)

- Lives near Export / Session Management (confirmed: not TEST_LAB, §1f) — exact placement
  (a new Session Management action, or its own small panel) still open.
- Reads a Mode 2 bundle; reconstructs what it can; **verification is part of import, not a
  separate step** — compares the bundle's recorded hashes against what's actually on this
  machine right now:
  - recipe file-set hash (`sha256sum` equivalent, already computed, §1a)
  - data content hash per dataset (`data_batch_hash`/`decision_hashes`, already computed, §1a)
  - engine fingerprint (polars/transformer versions + cache version, `engine_fingerprint()`,
    §4A) — the third leg; without it, a recipe+data hash match still wouldn't guarantee an
    identical re-render if the library versions differ.
- Reports match/mismatch per leg, not just "ok"/"fail" — a mismatch should say *which* of the
  three changed.

### 4F. Reshuffle control — deferred, separate from this decomposition

Already flagged mid-discussion: needs conditional visibility (only on plots with a
jitter-capable layer, and only when a seed override is actually meaningful — e.g. not shown at
all for a plot with no random component). Depends on §4A's `aesthetic_override.random_state`
existing first. Not a sub-issue of this tracking issue — stays its own small, later discussion.

### 4G. Session Management: labels + multi-dataset distinction — separate, linked issue

A different problem: not reproducibility for someone else, but a user's own ability to tell
apart multiple in-progress sessions of the same recipe against different data batches, and to
describe what each one is (a free-text label/comment per session). Cross-referenced here
because sloppy session hygiene undermines reproducible work in its own way, but it is not a
sub-issue of the Mode 2 / Import work above — it's Session Management's own backlog.

---

## 5. Suggested issue structure

- **One parent tracking issue** ("Reproducible export & import — tracking") linking this
  design doc, with **sub-issues** (GitHub's native sub-issue relation, confirmed available on
  this repo via `gh api repos/{owner}/{repo}/issues/{number}/sub_issues`) for 4A–4E.
- #39 itself becomes 4A (re-scoped, not closed-and-reopened — same issue, narrowed body).
- 4F (reshuffle) and 4G (session labels) referenced from the tracking issue but filed as their
  own independent issues, not sub-issues, since neither blocks nor is blocked by 4A–4E.

Filed as #44 (tracking), #39 (4A, re-scoped), #45 (4B), #46 (4C), #47 (4D), #48 (4E), #49 (4F,
deferred), #50 (4G).

---

## 6. Audit findings (2026-11-09) — before any of #39/#45–#48 start building

Two parallel investigations (one tracing the design against the real codebase and this
project's own ADRs, one researching external reproducibility-bundling practice) were run
after the issues above were filed, specifically to catch logic flaws before implementation —
not a survey, a check for things that would break. Findings below, with the corrections made
during discussion.

### 6a. #47's "T3 → recipe actions" is not an ADR-082/ADR-093 boundary violation — corrected

First pass over-read the ADRs: ADR-082 §4 forbids **BLUEPRINT** from writing T3 (Blueprint
authoring/injecting T3 state) — #47 does the opposite direction, HOME's own T3 (which HOME
legitimately owns, per Eve: *"T3 belongs to HOME"*) flowing *out* into an export artifact.
ADR-093 removed a *third*, different direction (Gallery content flowing *into* T3). Neither
ADR is actually in #47's path. **Not a blocker. No superseding ADR needed.**

The real question #47 raises is narrower and purely technical, not an ADR question:
**Tier 2 is shared across every plot using a given join** (`rules_data_engine.md`'s
Bifurcation Point Rule), but T3 steps are **per-plot** (`t3_audit_steps_by_plot`). Baking one
plot's T3 steps directly into that join's shared `tier2:` list would wrongly apply that one
plot's filters to every other plot sharing the same branch — a correctness bug.

**Two solution options for #47 to choose between (not decided here):**

- **(A) A genuine per-plot "tier3" concept in the recipe.** Architecturally the most honest —
  T3 steps get their own, truly per-plot, recipe section. Requires teaching the headless engine
  (`DataAssembler`) a new concept it doesn't have today: real new engine work, not just an
  export-time YAML change.
- **(B) Fork the join per affected plot.** For each plot carrying T3 steps, duplicate just that
  join's branch under a new id used only by that plot (mechanically the existing Bifurcation
  Point Rule / Tier 2 "Branch" concept, applied at export time), append the translated actions
  to the fork, repoint only that plot's `target_dataset` at it. Zero new engine code —
  `debug_assembler.py` needs no changes. Downside: more near-duplicate join blocks in the
  frozen copy when several plots each carry their own T3 steps.

(B) is lower-risk and faster for a first version; (A) is the more architecturally proper
long-term shape. #47's body should record this as an open decision, not resolve it by default.

### 6b. #48 (Import) must commit to file-based-only — ADR-093 does apply here

ADR-093's stated principle: *"every cross-space handoff is file-based... no space writes into
another space's state at runtime, ever."* #48's original body said "reconstructs what it can"
with no committed mechanism — that is the actual gap. **Import must write a new recipe file +
a new session under `_sessions/`, then let the user open it through the existing
selector/restore entry points — never inject parsed bundle content directly into a live
`wrangle_studio`/`home_state` object.** This is a hard rule, not a UX choice.

**Verification-mismatch handling, resolved:** non-blocking. Import always proceeds; each leg
reports pass/fail; a mismatch is a loud, hard-to-miss warning, never a refusal to open — matches
the project's existing non-blocking-warning pattern (e.g. the `random_state: random` export
warning, §4A).

### 6c. #39's automatic seed bookkeeping must not violate Reactive Write Discipline R1

`ui_implementation_contract.md §14` R1: a `@render.*` must never call `.set()` on a reactive
value. The natural-looking place to capture "which seed did this render actually draw" is
inside the `@render.plot` that calls `viz_factory.render()` — which R1 forbids outright (this
project has hit the resulting bugs before: outputs stuck "recalculating", stale renders). Fix
is already this project's own pattern (R2/R3, §14): draw the seed via a separate
`@reactive.Calc`, persist it via a separate, idempotency-guarded `@reactive.Effect` — the
render reads the Calc, never writes state itself. Also: the value holding the last-drawn seed
must be an ordinary **per-session** `reactive.Value`, not the bootloader's process-wide asset
cache (used for `tier1_anchor`) — reusing that cache would leak one user's drawn seed into
every other session rendering the same recipe.

### 6d. #39/#48 are missing a fourth hash leg: the T3 steps themselves — new finding

Confirmed by reading the code, not assumed: `export_handlers.py`'s provenance dict has never
had a `t3_audit_steps_sha256` field — `grep -n "t3_audit_steps_sha256" app/handlers/export_handlers.py`
returns nothing, even though the *original* design spec's own example front-matter
(`ui_implementation_contract.md §12f`) already specified one: `t3_audit_steps_sha256: "b7c1..."
# SHA256 of the serialized audit steps`. Designed once, never wired up.

The same gap exists on ordinary session reopen, not just reproducibility export/import:
`app/handlers/session_handlers.py` (~line 324-325) restores a T3 ghost and warns on a
`data_analysis_recipe_sha256` or `data_batch_hash` mismatch — but never checks whether the T3
steps themselves changed, even though they affect the data just as much as the recipe or the
data batch do.

**Fold-in:**
- **#39**: compute and include `t3_audit_steps_sha256` (per the content already serialized for
  export) in the consolidated provenance record.
- **#48**: verify it as a fourth leg (recipe / data / engine / **T3 steps**), same pass/fail
  reporting, same non-blocking-mismatch rule as §6b.
- **#50** (Session Management, separate from the export/import flow): extend the existing
  restore-mismatch warning to also check T3-steps content — this is ordinary session-reopen
  integrity, not new export surface, so it belongs with Session Management's own work, not #39
  or #48.

### 6e. Import vs. existing Session Management — distinct, confirmed, but must be stated

Confirmed by reading `session_manager.py`: `export_session_zip`/`import_session_zip` only ever
zip the `_sessions/{key}/` ghost directory (metadata + *paths* to source files, never the
recipe or the data itself) — so #48 is a genuinely different capability, not a duplicate. #48's
body should explicitly state whether Import extends `SessionManager`'s existing machinery or
builds a parallel importer, rather than leaving that unstated.

### 6f. External research — two items worth folding in, three checked as not applicable

- **Align field vocabulary with [RO-Crate's Provenance Run Crate profile](https://arxiv.org/abs/2312.07852)**
  (W3C-PROV-aligned, formalizes exactly our prospective/retrospective split) when naming fields
  in `effective_run.yaml` (#39) — not full adoption, just reusing established names where they
  overlap, and **documenting the source inline** (a comment citing the spec) so a future move
  to full adoption has a clear starting point, per Eve.
- **The "engine fingerprint" (library version strings) is weaker than established practice**
  (Code Ocean-style tools snapshot the whole environment). Plan for later, not blocking #47/#48:
  also snapshot the dependency lock (`uv.lock`) into the Mode 2 bundle, and note the project's
  existing container path (`assets/containers/Dockerfile`) as a stronger future option.
- Checked, not applicable: GPU/BLAS nondeterminism (VizFactory's jitter is CPU-only
  `numpy.random.RandomState`, already deterministic, ADR-090); row-order false-hash-match
  (SPARMVET hashes raw file bytes, not computed dataframes); ACM artifact-badging checklist
  (already substantially matched — commit hash, README — only gap is no license field, low
  priority for an internal tool).
