"""The comparisons of the equality check, shared by the passing tests and the open findings (EQUALITY-CHECK-1)."""
from dataclasses import dataclass

import pandas as pd
import polars as pl
from polars.testing import assert_frame_equal

from app.tests.equality import reference_2_test_data_ST22_dummy as reference
from app.tests.equality import scenarios
from app.tests.equality.engine_black_box import built

# Tables whose row order the recipe does not state: the three data schemas (the file order is never written down; a
# filter keeps it only by the way Polars works). They are compared as a set of rows, and `order` cases ask in
# addition whether the order is the file's. The two joins end in `polars_sort ... maintain_order: true`: stated.
UNSTATED_ORDER = {"metadata_schema", "amr_data", "plasmid_data"}

# The scenarios where every table must equal the hand-written one, and where some must be refused by both sides.
EQUAL_SCENARIOS = ("clean", "dirty", "emptied")
REFUSED = {
    # a Year of 2023.5 cannot become the text "2023": the two joins are refused, the schemas are read
    "fractional_year": ("AMR_Profile_Joint", "Plasmid_Profile_Joint"),
    # the shipped recipe says null_values [] (no text means missing) and the data has empty number cells
    "dirty_no_null_text": tuple(scenarios.ALL_TABLES),
}


@dataclass(frozen=True)
class Case:
    scenario: str
    kind: str  # t1 | t2 | order | plot_data | plot_built | plot_isolated | refused
    name: str

    @property
    def id(self) -> str:
        return f"{self.scenario}-{self.kind}-{self.name}"


def all_cases() -> list[Case]:
    cases = []
    for scenario in EQUAL_SCENARIOS:
        for name in scenarios.ALL_TABLES:
            cases.append(Case(scenario, "t1", name))
            cases.append(Case(scenario, "t2", name))
        for name in sorted(UNSTATED_ORDER):
            cases.append(Case(scenario, "order", name))
        for plot_id in scenarios.PLOTS:
            cases.append(Case(scenario, "plot_data", plot_id))
            cases.append(Case(scenario, "plot_built", plot_id))
            cases.append(Case(scenario, "plot_isolated", plot_id))
    for scenario, names in REFUSED.items():
        for name in scenarios.ALL_TABLES:
            cases.append(Case(scenario, "refused" if name in names else "t1", name))
    return cases


def _sorted_set(frame: pl.DataFrame) -> pl.DataFrame:
    return frame.sort(frame.columns, nulls_last=True)


def _describe(outcome) -> str:
    return f"{type(outcome).__name__}: {str(outcome)[:160]}" if isinstance(outcome, BaseException) else "built"


def check(case: Case) -> None:
    engine = scenarios.engine_result(case.scenario)
    if case.kind == "refused":
        # the hand-written side refuses (the recipe's meaning cannot be applied) and so must the engine
        try:
            hand = scenarios.hand_table(case.scenario, case.name)
        except Exception:  # noqa: BLE001 - the refusal is what is expected of the hand side
            hand = None
        assert hand is None, f"the hand-written side built {case.name}: the scenario does not test a refusal"
        got = engine.t1[case.name]
        assert isinstance(got, BaseException), (
            f"the hand-written side refuses {case.name} but the engine built it: {got.height} rows")
        return
    if case.kind in ("t1", "t2", "order"):
        hand = scenarios.hand_table(case.scenario, case.name)
        got = (engine.t2 if case.kind == "t2" else engine.t1)[case.name]
        if isinstance(got, BaseException):
            raise AssertionError(f"engine failed on {case.name} {case.kind}: {_describe(got)}")
        if case.name in UNSTATED_ORDER and case.kind != "order":
            assert_frame_equal(_sorted_set(got), _sorted_set(hand))
        else:
            assert_frame_equal(got, hand)
        return
    plot = engine.plots[case.name]
    target = scenarios.PLOTS[case.name]
    if case.kind == "plot_data":
        hand = scenarios.hand_table(case.scenario, target)
        if isinstance(plot, BaseException):
            raise AssertionError(f"engine has no plot {case.name}: {_describe(plot)}")
        # compared as pandas frames: that is what plotnine receives, and an empty frame keeps its column types
        pd.testing.assert_frame_equal(plot.data.reset_index(drop=True), hand.to_pandas())
        return
    if case.kind == "plot_isolated":
        # the hand-written plot is fed with the very table the engine's plot received: only the drawing is compared
        if isinstance(plot, BaseException):
            raise AssertionError(f"engine has no plot {case.name}: {_describe(plot)}")
        source = pl.from_pandas(plot.data.reset_index(drop=True))
    else:
        source = scenarios.hand_table(case.scenario, target)
    hand_outcome = _hand_built(case.name, source)
    engine_outcome = _engine_built(plot)
    if isinstance(hand_outcome, BaseException) or isinstance(engine_outcome, BaseException):
        assert isinstance(hand_outcome, BaseException) and isinstance(engine_outcome, BaseException), (
            f"hand-written plot: {_describe(hand_outcome)}; engine plot: {_describe(engine_outcome)}")
        return
    assert engine_outcome["labels"] == hand_outcome["labels"]
    assert engine_outcome["geoms"] == hand_outcome["geoms"]
    assert len(engine_outcome["layers"]) == len(hand_outcome["layers"])
    for got, want in zip(engine_outcome["layers"], hand_outcome["layers"]):
        assert_frame_equal(got, want)
    assert_frame_equal(engine_outcome["panels"], hand_outcome["panels"])


def _hand_built(plot_id: str, table: pl.DataFrame):
    try:
        return built(reference.reference_plot(plot_id, table))
    except Exception as exc:  # noqa: BLE001 - a plot that plotnine cannot draw is a result
        return exc


def _engine_built(plot):
    if isinstance(plot, BaseException):
        return plot
    try:
        return built(plot)
    except Exception as exc:  # noqa: BLE001
        return exc
