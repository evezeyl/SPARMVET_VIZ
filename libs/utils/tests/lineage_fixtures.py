"""The small recipes and tables of the lineage walk tests (LBFB step 0a): built in the tests, nothing shipped changes.

Each function returns `(recipe, tables)`: the recipe as the resolved dictionary the graph is built from, and the source tables as Polars
frames. The oracle (`lineage_oracle`) turns them into the engine's plan and into expected tables; the tests state the expected lines by hand.

FX-CHAIN  the smallest recipe with a join, a table read by a plot and by a join, an empty tier 2 and an empty tier 3.
FX-TIERS  the structure kitchen of DESIGN.md 3.1: a source with tier 2 steps read by a plot and by two joins, a source read by a plot and two
          joins with no tier 2, a join with tier 2 steps and three plots (one with its own tier 3 steps), a join no plot reads, a source
          nothing reads.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import polars as pl

Recipe = Dict[str, Any]
Tables = Dict[str, pl.DataFrame]


def keep(column: str, op: str, value: Any, na: str = "keep") -> dict:
    return {"action": "modif_filter", "column": column, "op": op, "value": value, "na": na}


def join_step(right: str, on: Any = "sample_id", how: str = "left", **extra: Any) -> dict:
    step = {"action": "polars_join", "right_ingredient": right, "how": how, **extra}
    if isinstance(on, tuple):
        step["left_on"], step["right_on"] = on
    else:
        step["on"] = on
    return step


def rename(**mapping: str) -> dict:
    return {"action": "polars_rename", "mapping": dict(mapping)}


def drop(*columns: str) -> dict:
    return {"action": "polars_drop", "columns": list(columns)}


def select(*columns: str) -> dict:
    return {"action": "polars_select", "exprs": list(columns)}


def with_columns(**formulas: str) -> dict:
    return {"action": "polars_with_columns", "named_exprs": dict(formulas)}


def cast(columns: Sequence[str], dtype: str) -> dict:
    return {"action": "polars_cast", "columns": list(columns), "dtype": dtype}


def schema(columns: Sequence[str], tier1: Sequence[dict] = (), tier2: Optional[Sequence[dict]] = None, keys: Sequence[str] = ()) -> dict:
    fields = {c: ({"type": "String", "is_entity_key": True} if c in keys else {"type": "String"}) for c in columns}
    body: dict = {"source": {"type": "local_tsv", "path": "x.tsv"}, "input_fields": fields, "tier1": {"steps": list(tier1)}}
    if tier2 is not None:
        body["tier2"] = {"steps": list(tier2)}
    return body


def join(ingredients: Sequence[str], tier1: Sequence[dict] = (), tier2: Optional[Sequence[dict]] = None) -> dict:
    body: dict = {"ingredients": [{"dataset_id": i} for i in ingredients], "tier1": {"steps": list(tier1)}}
    if tier2 is not None:
        body["tier2"] = {"steps": list(tier2)}
    return body


def plot(target: str, tier3: Optional[Sequence[dict]] = None) -> dict:
    entry: dict = {"target_dataset": target, "mapping": {"x": "sample_id"}, "layers": [{"name": "geom_col"}]}
    if tier3 is not None:
        entry["tier3"] = {"steps": list(tier3)}
    return entry


def recipe(schemas: Dict[str, dict], joins: Optional[Dict[str, dict]] = None, plots: Optional[Dict[str, dict]] = None) -> Recipe:
    return {"data_schemas": dict(schemas), "joins": dict(joins or {}), "analysis_groups": {"g": {"plots": dict(plots or {})}}}


def table(**columns: List[Any]) -> pl.DataFrame:
    return pl.DataFrame(columns)


IDS = ["S1", "S2", "S3", "S4", "S5"]


def chain(a_steps: Sequence[dict] = (), b_steps: Sequence[dict] = (), j_steps: Optional[Sequence[dict]] = None, extra_plots: Optional[Dict[str, dict]] = None,
          keys: Sequence[str] = ("sample_id",)) -> Tuple[Recipe, Tables]:
    """FX-CHAIN: A(sample_id, country, year, val) with one filter, B(sample_id, lab), J = A left join B on sample_id; P1 reads J, P2 reads A."""
    tables = {"A": table(sample_id=IDS, country=["NO", "SE", "NO", "SE", "NO"], year=[2022, 2023, 2023, 2024, 2024], val=[1.0, 2.0, 3.0, 4.0, -5.0]),
              "B": table(sample_id=["S1", "S2", "S3", "S4"], lab=["X", "X", "Y", "Y"])}
    a_steps = list(a_steps) or [keep("val", "gt", 0.0)]
    steps = [join_step("B")] if j_steps is None else list(j_steps)
    return recipe({"A": schema(["sample_id", "country", "year", "val"], a_steps, keys=keys), "B": schema(["sample_id", "lab"], b_steps, keys=keys)},
                  {"J": join(["A", "B"], steps)}, {"P1": plot("J"), "P2": plot("A"), **(extra_plots or {})}), tables


def tiers(u_declares_key: bool = False, u_plot: bool = False) -> Tuple[Recipe, Tables]:
    """FX-TIERS (DESIGN 3.1): S(T1 one step, T2 two steps; plot Ps; ingredient of J1 and J2), E(no steps; plot Pe; ingredient of J1 and JU), M(no steps),
    U(no steps; nothing reads it; its key is declared only when asked); J1 = S, E, M (two join steps, one tier 2 step; plots Pa, Pb, Pc with Pc
    holding two own steps), J2 = S, M (one join step; plot Pd), JU = E, M (no plot). Every table has `sample_id`, a declared key (except U)."""
    ids = ["S1", "S2", "S3", "S4"]
    tables = {"S": table(sample_id=ids, country=["NO", "SE", "NO", "SE"], val=[1.0, 2.0, 3.0, 4.0]),
              "E": table(sample_id=ids, gene=["g1", "g2", "g3", "g4"]),
              "M": table(sample_id=ids, year=[2022, 2023, 2024, 2024]),
              "U": table(sample_id=ids, junk=["a", "b", "c", "d"])}
    schemas = {"S": schema(["sample_id", "country", "val"], [keep("val", "gt", 0.0)], [keep("val", "lt", 9.0), keep("country", "ne", "XX")], keys=["sample_id"]),
               "E": schema(["sample_id", "gene"], keys=["sample_id"]),
               "M": schema(["sample_id", "year"], keys=["sample_id"]),
               "U": schema(["sample_id", "junk"], keys=["sample_id"] if u_declares_key else [])}
    joins = {"J1": join(["S", "E", "M"], [join_step("E"), join_step("M")], [keep("year", "gt", 2000)]),
             "J2": join(["S", "M"], [join_step("M")]),
             "JU": join(["E", "M"], [join_step("M")])}
    plots = {"Ps": plot("S"), "Pe": plot("E"), "Pa": plot("J1"), "Pb": plot("J1"), "Pc": plot("J1", [keep("val", "gt", 0.0), keep("gene", "ne", "g9")]), "Pd": plot("J2")}
    if u_plot:
        plots["Pu"] = plot("U")
    return recipe(schemas, joins, plots), tables
