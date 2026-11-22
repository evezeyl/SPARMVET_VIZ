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


def group_by(by: Sequence[str], **aggs: str) -> dict:
    return {"action": "polars_group_by", "by": list(by), "named_aggs": dict(aggs)}


def fill_null(columns: Sequence[str], value: Any) -> dict:
    return {"action": "polars_fill_null", "columns": list(columns), "value": value}


def str_split(columns: Sequence[str], by: str) -> dict:
    return {"action": "polars_str_split", "columns": list(columns), "by": by}


def unpivot(on: Sequence[str], index: Sequence[str]) -> dict:
    return {"action": "polars_unpivot", "on": list(on), "index": list(index), "variable_name": "variable", "value_name": "value"}


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


def followed() -> List[Tuple[str, Recipe, Tables]]:
    """The recipes of LBFB steps 2 and 3: a column that changes name, type or values on the way (every start of every one is walked by the property tests).
    Text columns only where a mark is put (the marker proof), numbers where a cast or a compute step needs them."""
    ids = ["S1", "S2", "S3"]
    out: List[Tuple[str, Recipe, Tables]] = []
    out.append(("rename_across_tiers", recipe({"A": schema(["sample_id", "country", "lab"], [rename(country="origin")], [rename(origin="country")], keys=["sample_id"])},
                                              {}, {"P": plot("A"), "Q": plot("A", [keep("lab", "ne", "Z")])}),
                {"A": table(sample_id=ids, country=["NO", "SE", "NO"], lab=["X", "Y", "X"])}))
    out.append(("rename_back_in_one_tier", recipe({"A": schema(["sample_id", "country"], [rename(country="origin"), rename(origin="country")], keys=["sample_id"])}, {}, {"P": plot("A")}),
                {"A": table(sample_id=ids, country=["NO", "SE", "NO"])}))
    out.append(("swap", recipe({"A": schema(["sample_id", "a", "b"], [rename(a="b", b="a")], keys=["sample_id"])}, {}, {"P": plot("A")}),
                {"A": table(sample_id=ids, a=["x", "y", "z"], b=["u", "v", "w"])}))
    out.append(("join_other_key_and_suffix",
                recipe({"A": schema(["sample_id", "val", "lab"], keys=["sample_id"]), "B": schema(["isolate", "val", "lab", "note"])},
                       {"J": join(["A", "B"], [join_step("B", on=("sample_id", "isolate"), suffix="_b")], [keep("note", "ne", "Q")])}, {"P": plot("J"), "Pb": plot("B")}),
                {"A": table(sample_id=ids, val=["a1", "a2", "a3"], lab=["L1", "L2", "L3"]), "B": table(isolate=ids, val=["b1", "b2", "b3"], lab=["M1", "M2", "M3"], note=["n1", "n2", "n3"])}))
    out.append(("join_default_suffix_then_rename",
                recipe({"A": schema(["sample_id", "val"], keys=["sample_id"]), "B": schema(["sample_id", "val"], keys=["sample_id"])},
                       {"J": join(["A", "B"], [join_step("B"), rename(val_right="val_b")])}, {"P": plot("J")}),
                {"A": table(sample_id=ids, val=["a1", "a2", "a3"]), "B": table(sample_id=ids, val=["b1", "b2", "b3"])}))
    out.append(("cast_text", recipe({"A": schema(["sample_id", "year", "country"], [cast(["year"], "Categorical")], keys=["sample_id"]), "B": schema(["sample_id", "lab"], keys=["sample_id"])},
                                    {"J": join(["A", "B"], [join_step("B")])}, {"P": plot("J"), "Pa": plot("A")}),
                {"A": table(sample_id=ids, year=["2022", "2023", "2024"], country=["NO", "SE", "NO"]), "B": table(sample_id=ids, lab=["X", "Y", "Z"])}))
    out.append(("recompute_text", recipe({"A": schema(["sample_id", "country", "lab"], [with_columns(country="pl.col('country').str.to_lowercase()")], keys=["sample_id"])},
                                         {}, {"P": plot("A")}), {"A": table(sample_id=ids, country=["NO", "SE", "NO"], lab=["X", "Y", "X"])}))
    out.append(("group_by_text", recipe({"A": schema(["sample_id", "country", "lab"], [group_by(["country", "lab"], sample_id="pl.col('sample_id').first()")], keys=["sample_id"]),
                                         "B": schema(["country", "lab2"])},
                                        {"J": join(["A", "B"], [join_step("B", on="country")])}, {"P": plot("J"), "Pa": plot("A")}),
                {"A": table(sample_id=ids, country=["NO", "SE", "NO"], lab=["X", "Y", "X"]), "B": table(country=["NO", "SE"], lab2=["p", "q"])}))
    out.append(("semi_join_other_key_and_namesake",
                recipe({"A": schema(["sample_id", "val", "lab"], keys=["sample_id"]), "B": schema(["isolate", "val", "lab", "note"])},
                       {"J": join(["A", "B"], [join_step("B", on=("sample_id", "isolate"), how="semi")], [keep("lab", "ne", "Q")])}, {"P": plot("J"), "Pb": plot("B")}),
                {"A": table(sample_id=ids, val=["a1", "a2", "a3"], lab=["L1", "L2", "L3"]), "B": table(isolate=["S1", "S2", "S9"], val=["b1", "b2", "b3"], lab=["M1", "M2", "M3"], note=["n1", "n2", "n3"])}))
    out.append(("rename_in_tier1_cast_in_tier2", recipe({"A": schema(["sample_id", "year"], [rename(year="yr")], [cast(["yr"], "Categorical"), rename(yr="year")], keys=["sample_id"])},
                                                        {}, {"P": plot("A")}), {"A": table(sample_id=ids, year=["2022", "2023", "2024"])}))
    return out
