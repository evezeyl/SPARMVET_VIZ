"""
Joint Designer pure logic — key-match computation and canonical join-step (de)serialisation.

Serves the BLUEPRINT Joint Designer pane (ADR-082 Q5, BP-JOINT-1). Pure and stdlib-only:
the caller (app/handlers/blueprint_handlers.py) materialises each ingredient via the
orchestrator, extracts the join-key columns with polars (String-cast, mirroring how the
assembler joins), and passes plain Python rows here. Importable headless — no Shiny, no polars.

Consumed by: app/handlers/blueprint_handlers.py (Joint Designer wiring).
Produces: canonical `join` recipe steps consumed by the transformer `join` action.
If deleted: the Joint Designer pane loses its overlap stats and step (de)serialisation.
"""
from __future__ import annotations

# @deps
# provides: join_designer:compute_key_match, join_designer:build_join_step, join_designer:parse_join_step
# consumes: —
# consumed_by: app/handlers/blueprint_handlers.py, libs/blueprint_arch/tests/test_join_designer.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-082 (Q5), .claude/rules/rules_manifest_structure.md#7
# @end_deps

# Join strategies offered by the Designer — mirrors the `how` enum declared in the
# transformer join action ui_schema (libs/transformer/.../relational/joins.py).
JOIN_HOW_OPTIONS = ["inner", "left", "outer", "semi", "anti", "cross"]


def _normalise_dtype_family(dtype: str) -> str:
    """Map a polars dtype name to a coarse family for an advisory compatibility check.

    The assembler casts join keys to String before joining (the safe common denominator),
    so cross-family joins technically run; this family check is an honest *advisory* about
    whether raw values are likely to align (e.g. Float64 vs Int64 produces '2022.0' vs
    '2022' and silently fails to match), not a hard gate.
    """
    d = (dtype or "").lower()
    if any(t in d for t in ("utf8", "str", "cat")):
        return "text"
    if "bool" in d:
        return "bool"
    if "date" in d or "time" in d:
        return "temporal"
    if "float" in d or "decimal" in d:
        return "float"
    if "int" in d:
        return "int"
    return d or "unknown"


def compute_key_match(left_rows, right_rows, left_dtypes, right_dtypes, sample_n=8):
    """Compute real key-overlap statistics between two ingredients' join-key columns.

    left_rows / right_rows: list of key tuples — one tuple per distinct key value (for a
        single key, 1-tuples). The caller extracts these via
        `lf.select([pl.col(k).cast(pl.String) for k in keys]).unique().collect().rows()`
        so the overlap reflects exactly what the assembler will join on.
    left_dtypes / right_dtypes: original polars dtype-name strings, key-aligned (for the
        advisory dtype panel — independent of the String-cast overlap above).
    sample_n: number of unmatched key tuples to surface in each *_only_sample list.

    Returns a stats dict (see keys below). Never raises on data shape — an arity mismatch
    is reported via arity_ok=False rather than an exception.
    """
    left_keys_n = len(left_dtypes)
    right_keys_n = len(right_dtypes)
    arity_ok = left_keys_n == right_keys_n and left_keys_n > 0

    dtype_pairs = []
    for i in range(min(left_keys_n, right_keys_n)):
        lf_fam = _normalise_dtype_family(left_dtypes[i])
        rf_fam = _normalise_dtype_family(right_dtypes[i])
        dtype_pairs.append({
            "left_key_dtype": left_dtypes[i],
            "right_key_dtype": right_dtypes[i],
            "family_match": lf_fam == rf_fam,
        })
    dtype_compatible = bool(dtype_pairs) and all(p["family_match"] for p in dtype_pairs)

    if not arity_ok:
        return {
            "arity_ok": False,
            "left_total": len(set(left_rows)),
            "right_total": len(set(right_rows)),
            "matched": 0,
            "left_only": 0,
            "right_only": 0,
            "match_rate": 0.0,
            "dtype_pairs": dtype_pairs,
            "dtype_compatible": dtype_compatible,
            "left_only_sample": [],
            "right_only_sample": [],
        }

    left_set = {tuple(r) for r in left_rows}
    right_set = {tuple(r) for r in right_rows}
    matched_set = left_set & right_set
    left_only_set = left_set - right_set
    right_only_set = right_set - left_set

    left_total = len(left_set)
    matched = len(matched_set)
    match_rate = (matched / left_total) if left_total else 0.0

    return {
        "arity_ok": True,
        "left_total": left_total,
        "right_total": len(right_set),
        "matched": matched,
        "left_only": len(left_only_set),
        "right_only": len(right_only_set),
        "match_rate": match_rate,
        "dtype_pairs": dtype_pairs,
        "dtype_compatible": dtype_compatible,
        "left_only_sample": sorted(left_only_set)[:sample_n],
        "right_only_sample": sorted(right_only_set)[:sample_n],
    }


def build_join_step(right_ingredient, left_keys, right_keys, how="inner", comment=""):
    """Emit a canonical `join` recipe step from Joint Designer selections.

    left_keys / right_keys: aligned, non-empty lists of column names (the left side refers
        to the accumulating assembly base; the right side to `right_ingredient`'s columns).
    Symmetric keys (left == right) emit `on`; differing keys emit `left_on` / `right_on`.
    A single key emits a scalar; composite keys emit a list.

    NOTE on the YAML boolean trap: the emitted symmetric key is the string "on". When this
    step is serialised the writer MUST quote it (`'on':`) — unquoted `on:` reloads as the
    boolean True (rules_manifest_structure.md §7). DataAssembler defensively recovers via
    step.get("on") or step.get(True) (data_assembler.py:182-185), but the saved manifest
    will be malformed. The Designer save path must handle quoting.
    """
    left_keys = list(left_keys)
    right_keys = list(right_keys)
    if not left_keys or not right_keys:
        raise ValueError("build_join_step requires at least one key on each side.")
    if len(left_keys) != len(right_keys):
        raise ValueError(
            f"Key arity mismatch: {len(left_keys)} left key(s) vs {len(right_keys)} right key(s).")

    step = {"action": "join", "right_ingredient": right_ingredient}

    def _scalar_or_list(keys):
        return keys[0] if len(keys) == 1 else keys

    if left_keys == right_keys:
        step["on"] = _scalar_or_list(left_keys)
    else:
        step["left_on"] = _scalar_or_list(left_keys)
        step["right_on"] = _scalar_or_list(right_keys)

    step["how"] = how
    if comment:
        step["comment"] = comment
    return step


def parse_join_step(step):
    """Inverse of build_join_step — extract Designer fields from a canonical join step.

    Defensive against the YAML boolean trap: an unquoted `on:` in a hand-authored manifest
    reloads as the boolean key True, so we look up both "on" and True.
    Returns {right_ingredient, left_keys, right_keys, how, comment}. `how` falls back to
    "left" when absent (the transformer join action's default), so an edit faithfully
    represents the step's current runtime behaviour.
    """
    if not isinstance(step, dict):
        return {"right_ingredient": None, "left_keys": [], "right_keys": [],
                "how": "left", "comment": ""}

    def _as_list(v):
        if v is None:
            return []
        return list(v) if isinstance(v, (list, tuple)) else [v]

    on = step.get("on", step.get(True))
    if on is not None:
        left_keys = _as_list(on)
        right_keys = list(left_keys)
    else:
        left_keys = _as_list(step.get("left_on"))
        right_keys = _as_list(step.get("right_on"))

    return {
        "right_ingredient": step.get("right_ingredient"),
        "left_keys": left_keys,
        "right_keys": right_keys,
        "how": step.get("how", "left"),
        "comment": step.get("comment", ""),
    }
