"""
Joint Designer pure logic — key-match computation and canonical join-step (de)serialisation.

Serves the BLUEPRINT Joint Designer pane (ADR-082 Q5, BP-JOINT-1). Pure and stdlib-only:
the caller (app/handlers/blueprint_handlers.py) materialises each ingredient via the
orchestrator, reads the schemas and the join-key columns with polars (as they are, no cast: the
assembler does not cast either), and passes plain Python values here. Importable headless — no Shiny, no polars.

Consumed by: app/handlers/blueprint_handlers.py (Joint Designer wiring).
Produces: canonical `join` steps consumed by the transformer `join` action.
If deleted: the Joint Designer pane loses its overlap stats and step (de)serialisation.
"""
from __future__ import annotations

from utils import action_names

# @deps
# provides: join_designer:check_join_keys, join_designer:compute_key_match, join_designer:build_join_step, join_designer:parse_join_step
# consumes: libs/utils/src/utils/action_names.py
# consumed_by: app/handlers/blueprint_handlers.py, app/modules/wrangle_studio.py, libs/blueprint_arch/tests/test_join_designer.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-082 (Q5), .claude/rules/rules_data_analysis_recipe_structure.md#7
# @end_deps

# Join strategies offered by the Designer — mirrors the `how` enum declared in the
# transformer join action ui_schema (libs/transformer/.../relational/joins.py).
JOIN_HOW_OPTIONS = ["inner", "left", "outer", "semi", "anti", "cross"]


def check_join_keys(left_schema, right_schema, left_keys, right_keys, right_id="the right table"):
    """Say whether a join on these keys can be built, with the same rule as the assembler.

    The build (DataAssembler, JOIN-KEY-TYPES-1, 2026-11-14) keeps the declared type of every key and fails when
    the two lists of keys differ in length, when a key column is missing, or when the types of a pair differ.
    This function gives the same verdict for the same pair, so the preview never says "compatible" for a join
    that the build refuses. The rule is written three times on purpose: the build (data_assembler.py:52), this preview and the
    checker (libs/utils/src/utils/recipe_check.py:539); a domain library may not import another one
    (rules_runtime_environment.md section 4); the parity test in app/tests compares them.

    left_schema / right_schema: {column name: dtype name} of the two tables (dtype names as strings).
    left_keys / right_keys: key column names, paired by position.

    Returns {"ok": bool, "kind": None | "length" | "missing" | "type", "problem": str, "fix": str,
    "type_pairs": [{"left_column", "right_column", "left_type", "right_type", "same"}]}.
    """
    left_keys = list(left_keys)
    right_keys = list(right_keys)
    fail = {"ok": False, "type_pairs": []}

    if len(left_keys) != len(right_keys) or not left_keys:
        return {**fail, "kind": "length",
                "problem": (f"The key lists differ in length: left has {len(left_keys)} column(s) {left_keys} "
                            f"and right has {len(right_keys)} column(s) {right_keys}."),
                "fix": ("Pick the same number of key columns on each side, paired by position "
                        "(the first of the left with the first of the right).")}

    missing_left = [c for c in left_keys if c not in left_schema]
    missing_right = [c for c in right_keys if c not in right_schema]
    if missing_left or missing_right:
        lacks = []
        if missing_left:
            lacks.append(f"key column(s) {missing_left} missing in the left table (its columns: {list(left_schema)})")
        if missing_right:
            lacks.append(f"key column(s) {missing_right} missing in '{right_id}' (its columns: {list(right_schema)})")
        return {**fail, "kind": "missing",
                "problem": "A join key column does not exist: " + "; ".join(lacks) + ".",
                "fix": ("Pick key columns that exist in each table. The left table is the table at this step: a column of "
                        "a table joined later is not in it yet, and a step before the join may have renamed or dropped it.")}

    pairs = []
    for left_col, right_col in zip(left_keys, right_keys):
        left_type, right_type = str(left_schema[left_col]), str(right_schema[right_col])
        pairs.append({"left_column": left_col, "right_column": right_col,
                      "left_type": left_type, "right_type": right_type, "same": left_type == right_type})
    differing = [p for p in pairs if not p["same"]]
    if differing:
        described = "; ".join(
            (f"column '{p['left_column']}'" if p["left_column"] == p["right_column"]
             else f"column '{p['left_column']}' (left) and '{p['right_column']}' (right)")
            + f" is {p['left_type']} in the left table and {p['right_type']} in '{right_id}'"
            for p in differing)
        return {"ok": False, "kind": "type", "type_pairs": pairs,
                "problem": f"The join key types differ: {described}.",
                "fix": (f"Declare the same type for this field in input_fields of both tables. A cast step before the join "
                        f"changes only the left table (the table at this step); the type of '{right_id}' is changed in its "
                        "own input_fields or in its own wrangling. The engine does not change the type of a join key for you.")}
    return {"ok": True, "kind": None, "problem": "", "fix": "", "type_pairs": pairs}


def compute_key_match(left_rows, right_rows, sample_n=8):
    """Compute real key-overlap statistics between two ingredients' join-key columns.

    Call it only when check_join_keys says the join can be built. The overlap is computed on the keys as they
    are, with no cast (the build does not cast either).

    left_rows / right_rows: list of key tuples, one tuple per distinct key value (1-tuples for a single key),
        as the tables hold them: `lf.select(keys).unique().collect().rows()`.
    sample_n: number of unmatched key tuples to surface in each *_only_sample list.
    """
    left_set = {tuple(r) for r in left_rows}
    right_set = {tuple(r) for r in right_rows}
    matched_set = left_set & right_set
    left_only_set = left_set - right_set
    right_only_set = right_set - left_set

    left_total = len(left_set)
    matched = len(matched_set)
    return {
        "left_total": left_total,
        "right_total": len(right_set),
        "matched": matched,
        "left_only": len(left_only_set),
        "right_only": len(right_only_set),
        "match_rate": (matched / left_total) if left_total else 0.0,
        "left_only_sample": sorted(left_only_set, key=str)[:sample_n],
        "right_only_sample": sorted(right_only_set, key=str)[:sample_n],
    }


def build_join_step(right_ingredient, left_keys, right_keys, how="inner", comment=""):
    """Emit a canonical `join` step from Joint Designer selections.

    left_keys / right_keys: aligned, non-empty lists of column names (the left side refers
        to the accumulating assembly base; the right side to `right_ingredient`'s columns).
    Symmetric keys (left == right) emit `on`; differing keys emit `left_on` / `right_on`.
    Keys are always written as a list (a single key is a list of one).

    NOTE on the YAML boolean trap: the emitted symmetric key is the string "on". When this
    step is serialised the writer MUST quote it (`'on':`) — unquoted `on:` reloads as the
    boolean True (rules_data_analysis_recipe_structure.md §7). DataAssembler defensively recovers via
    step.get("on") or step.get(True) (data_assembler.py:182-185), but the saved data analysis recipe
    will be malformed. The Designer save path must handle quoting.
    """
    left_keys = list(left_keys)
    right_keys = list(right_keys)
    if not left_keys or not right_keys:
        raise ValueError("build_join_step requires at least one key on each side.")
    if len(left_keys) != len(right_keys):
        raise ValueError(
            f"Key arity mismatch: {len(left_keys)} left key(s) vs {len(right_keys)} right key(s).")

    step = {"action": action_names.JOIN, "right_ingredient": right_ingredient}

    # Polars takes a list of keys (format 1): a single key is a list of one, so the form never changes with the arity
    if left_keys == right_keys:
        step["on"] = left_keys
    else:
        step["left_on"] = left_keys
        step["right_on"] = right_keys

    step["how"] = how
    # The order rule is written in the step (no default): left order, right order of the matches; a right join keeps the right table's.
    step["maintain_order"] = "right_left" if how == "right" else "left_right"
    if comment:
        step["comment"] = comment
    return step


def parse_join_step(step):
    """Inverse of build_join_step — extract Designer fields from a canonical join step.

    Defensive against the YAML boolean trap: an unquoted `on:` in a hand-authored data analysis recipe
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
