"""The engine's plan of every place of a recipe, in the form the lineage walk receives it (LBFB step 0a, D-0325).

A plan is the ordered list of (column name, engine type) a table has after k steps. The plan book holds one plan for
every (node id, k) of the recipe graph: k = 0 is the table at the start of the node (a source table; the end of the table
before, for a tier or a join's first ingredient), k = n is the table after the n-th step of the node (n = number of steps
of the node, author steps then audit steps). A failure of the engine at a place is a VALUE of the book (`PlanFailure`,
with the engine's own sentence), never an exception lost on the way: the walk greys what depends on it and lists it.

The book is built by the caller that may ask the engine (the app layer composes the lazy plan of every step without
storing anything). This module holds only the types: pure, no Polars, no file, no engine. A type is whatever the engine
prints (`str(dtype)`); the walk compares types as text and never converts.

A caller must give an entry for EVERY (node, k) of the graph, and a `PlanFailure` for every place below a failure: a
missing entry is a bug of the caller and raises `PlanBookIncomplete` naming the place, so that absence is never read as
failure.

Consumed by: libs/utils/src/utils/lineage_walk.py, libs/utils/src/utils/step_effects.py.
If deleted: the walk has no input.

# @deps
# provides: class:Plan, class:PlanFailure, class:PlanBook, class:PlanBookIncomplete
# consumed_by: libs/utils/src/utils/lineage_walk.py, libs/utils/src/utils/step_effects.py, libs/utils/src/utils/declared_plans.py, libs/utils/src/utils/key_drop.py, libs/utils/tests/lineage_oracle.py
# doc: .claude/knowledge/decision_ledger.md (D-0325, D-0342), .claude/design/home_stage2_mechanism_spec.md
# @end_deps
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Tuple, Union


@dataclass(frozen=True)
class Plan:
    """The columns of a table at one place: (name, engine type) pairs in the engine's order. Names are exact (case sensitive)."""
    columns: Tuple[Tuple[str, str], ...]

    @staticmethod
    def of(pairs: Iterable[Tuple[str, str]]) -> "Plan":
        return Plan(tuple((str(name), str(kind)) for name, kind in pairs))

    @property
    def names(self) -> Tuple[str, ...]:
        return tuple(name for name, _ in self.columns)

    def has(self, name: str) -> bool:
        return any(n == name for n, _ in self.columns)

    def type_of(self, name: str) -> Optional[str]:
        return next((kind for n, kind in self.columns if n == name), None)


@dataclass(frozen=True)
class PlanFailure:
    """The engine could not give the plan here. `sentence` is the engine's own sentence, carried as data and never reworded;
    `node` and `step` name where the engine failed first (None when the caller does not know)."""
    sentence: str
    node: Optional[str] = None
    step: Optional[int] = None


class PlanBookIncomplete(KeyError):
    """The caller gave no plan (and no failure) for a place the walk needs: a bug of the caller, never read as a failure."""

    def __init__(self, node: str, step: int) -> None:
        self.node, self.step = node, step
        super().__init__(f"the plan book has no entry for {node!r} after {step} step(s): the caller must give a plan or a PlanFailure for every place")


class PlanBook:
    """A read-only mapping (node id, k) -> `Plan` or `PlanFailure`. The mapping given is held, not copied (a test may hand a
    counting mapping); nothing here writes to it."""

    def __init__(self, entries: Mapping[Tuple[str, int], Union[Plan, PlanFailure]]) -> None:
        self._entries = entries

    @staticmethod
    def of(raw: Mapping[Tuple[str, int], object]) -> "PlanBook":
        """A book from plain literals: a list of (name, type) pairs is a plan, a string is a failure sentence, a `Plan` or a `PlanFailure` stays."""
        built: Dict[Tuple[str, int], Union[Plan, PlanFailure]] = {}
        for key, value in raw.items():
            if isinstance(value, (Plan, PlanFailure)):
                built[key] = value
            elif isinstance(value, str):
                built[key] = PlanFailure(value, key[0], key[1])
            else:
                built[key] = Plan.of(value)  # type: ignore[arg-type]
        return PlanBook(built)

    def get(self, node: str, step: int) -> Union[Plan, PlanFailure]:
        try:
            return self._entries[(node, step)]
        except KeyError:
            raise PlanBookIncomplete(node, step) from None

    def has(self, node: str, step: int) -> bool:
        return (node, step) in self._entries
