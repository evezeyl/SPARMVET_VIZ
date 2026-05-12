# Code Quality Standards (rules_code_quality.md)

**Authority:** @dasharch  
**Status:** Partially enforced — §1 (emoji ban) is active now. §2–3 (documentation tiers) are
deferred to the pre-deployment review sprint. See §4 for the implementation trigger.

---

## 1. Emoji Scope Rule (ACTIVE — enforced immediately)

**The guiding principle:** emojis belong in user-facing output and human-readable documents,
not in source logic or developer-level annotations.

### Forbidden in Python

| Location | Example violation | Replacement |
|---|---|---|
| Inline comments | `# ✅ done` | `# done` |
| Docstrings | `"""Returns ✅ if valid"""` | `"""Returns True if valid."""` |
| Exception / error messages (raised) | `raise ValueError("❌ missing key")` | `raise ValueError("Missing key: ...")` |
| Decorator arguments | `@register_action("cast 🔧")` | `@register_action("cast")` |
| Variable names, class names | `status_✅ = True` | (obviously forbidden) |

### Allowed in Python

| Location | Rationale |
|---|---|
| `print()` statements in debug/test scripts that report PASS/FAIL to the terminal | User-facing output — the emojis are the signal (`✅ PASS`, `❌ FAIL`) |
| `print()` progress banners in debug scripts (`🚀 LAYER 1 WRANGLER DEBUGGER`) | Developer-facing terminal UX — acceptable in test/debug scripts only |
| Production `print()` only if it is explicitly a status line shown to the user | Rare — most production output should use logging without emojis |

### Always allowed (not Python)

- YAML `label:` values in `analysis_groups`, `recipe_meta.md`, gallery bundles
- All `.md` files: tasks, changelogs, rules, README, handoffs
- Quarto `.qmd` documentation files
- `tasks.md` section headers and priority markers
- **`f.write()` / string literals that produce markdown content** — e.g., `f.write("## Section 📊\n")` in an export bundle generator that writes `.qmd` or `.md` output files. The emoji appears in the *output document*, not in source comments or error messages. Treat these the same as YAML `label:` values.

**The test/debug script exception is intentional.** Scripts like `debug_wrangler.py` and
`transformer_integrity_suite.py` produce terminal tables for developer review — the emoji
status icons (`✅`, `❌`, `🔴`, `🟢`) serve a functional role there and should be kept.

**Why the ban exists for source logic:** Emojis in docstrings and comments break grep,
reduce professionalism in shared code, and are invisible in some IDEs and CI logs.
They carry no information that words cannot express more precisely.

---

## 2. Comment Philosophy — Developer Level

When comments are written, they must meet **developer-level professional standard**:

### Write comments for the WHY, not the WHAT

```python
# Bad — describes what the code does (readable from the code itself):
# loop over all schemas and collect field names
for schema_id, schema in schemas.items():
    fields.update(schema.get("input_fields", {}).keys())

# Good — explains a non-obvious constraint or decision:
# output_fields may be absent if the schema uses identity passthrough (ADR-014)
for schema_id, schema in schemas.items():
    fields.update(schema.get("input_fields", schema.get("output_fields", {})).keys())
```

### Acceptable comment types

| Type | Example | When to write |
|---|---|---|
| Constraint note | `# 'on' is a YAML reserved word — must quote in manifests` | Non-obvious external constraint |
| ADR reference | `# ADR-045: renders must never call reactive.Value.set()` | Rule that a reader might be tempted to violate |
| Gotcha | `# Float64 → Int64 → String: direct cast gives "2022.0"` | Behaviour that surprises developers |
| WHY block | `# WHY: we write to tmpAI/ not tmp/ — tmp/ is reserved for @verify outputs` | Design decision not obvious from code |

### Never write these

- `# end of loop` / `# end of function`
- `# call the function` / `# return result`
- `# TODO` without a tasks.md entry (use tasks.md instead)
- Multi-paragraph docstrings that repeat the function name
- Commented-out code blocks (delete, use git history)

---

## 3. Documentation Tiers — Pre-Deployment Standard (DEFERRED)

**Implementation trigger:** Start with `libs/transformer/` and `libs/viz_factory/` when Eve
begins the pre-deployment code review. Do NOT implement across the whole codebase at once.

### Tier A — Module Intent Header (every .py file in libs/ and app/)

Every module gets a module-level docstring in plain English describing:
- What user space / workflow does this file serve?
- What are its inputs and what does it produce?
- What would break if this file were deleted?
- Which persona flag(s) gate this module (for app/ handlers)

```python
"""
Transformer wrangling actions — analytical operations.

Provides @register_action decorators for statistical and time-series
transformations: window aggregations, cumulative counts, date extraction,
z-scores, percentiles, and interpolation.

Consumed by: DataAssembler (data_assembler.py) via the action registry.
Persona gate: none — all personas can trigger these via manifests.
If deleted: manifests using any of these action names will silently skip those steps.
"""
```

### Tier B — Public Function Intent (all def not starting with _)

One-sentence docstring on every public function. Not "what" — "why it exists and
what contract it fulfills." Parameter and return types are in the signature; the
docstring adds the domain context.

```python
def classify_update(current: str, latest: str) -> str:
    """Return MAJOR/MINOR/PATCH for a semver bump — used to prioritise upgrade urgency."""
```

Not:
```python
def classify_update(current: str, latest: str) -> str:
    """Takes two version strings and returns a classification string."""
```

### Tier C — Registered Action / Component Docstrings

Every `@register_action` and `@register_plot_component` function gets a docstring
explaining the transformation in domain terms — what a scientist would need to know
to use it in a manifest:

```python
@register_action("cast")
def cast(lf: pl.LazyFrame, spec: dict) -> pl.LazyFrame:
    """Cast one or more columns to a new dtype.

    Use when a TSV-inferred numeric column (e.g. Year as Float64) needs to be
    a String for discrete plot axes, or when a join key has mismatched types.
    Two-step cast required for Float64 → String: cast to Int64 first to avoid
    '2022.0' output (see rules_manifest_structure.md §3-B).

    spec keys: columns (list[str]), dtype (str — Polars type name e.g. 'String', 'Int64')
    """
```

### Tier D — Shiny Reactive Handlers (app/handlers/)

Every `@render.*` and `@reactive.Effect` function that is not self-evident gets a
one-liner explaining its reactive dependencies and what it produces or side-effects:

```python
@output
@render.ui
def sidebar_filters():
    """Mounts the filter accordion shell. Reads only current_persona — stable shell pattern (ADR-045 §R4)."""
```

---

## 4. Implementation Plan (Deferred)

When Eve is ready to begin pre-deployment review:

1. **Start with `libs/transformer/`** — run `audit_code_quality.py --lib transformer` to get
   a list of all undocumented public functions and missing module headers
2. **Then `libs/viz_factory/`** — same process
3. **Then `app/handlers/`** — Shiny handler explanations (most valuable for Eve's review)
4. **Then `libs/ingestion/`, `libs/connector/`, `libs/blueprint_arch/`**
5. **Last: `app/src/`** — bootloader, server, ui (lowest user-review priority)

Each library is a standalone session: annotate, verify, commit, move on.

The audit script (`scripts/audit_code_quality.py`, not yet written) will:
- Flag all `.py` files missing Tier A module docstrings
- Flag all public functions missing Tier B docstrings
- Flag all `@register_action` / `@register_plot_component` missing Tier C docstrings
- Flag any emoji characters in `.py` files (Tier 0 — active now)
- Report coverage percentage per library so progress is visible

---

## 5. Audit Script (Deferred — write before implementation sprint)

The script will be `scripts/audit_code_quality.py` with flags:
- `--lib <name>` — single library
- `--tier <A|B|C|D>` — check only one tier
- `--emoji-only` — fast scan for emoji violations (active now)
- `--output` — markdown report

Add to `schedule_commands.md` as Routine 14 when ready to implement.

**Do not write this script until the implementation sprint begins** — no point auditing
absent docstrings before the session that adds them.
