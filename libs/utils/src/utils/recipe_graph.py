# engine: python-polars (reads the Polars select and drop actions to know the columns of a table)
"""The recipe graph: one model of a data analysis recipe, built once from the resolved recipe (ADR-099 point 16(d), 16(i); ADR-101 point 3).

It serves HOME's audit (where does a field exist, which plots read a table), Blueprint's lineage, the checker (J08, X7)
and the cache keys (the precise parts of a table's key). The recipe is read once, here; everything else is a query.

Input: the resolved recipe, a dictionary (the loader has merged every `!include`). No file is read, no data frame is
built, no registry is asked. Output: a `RecipeGraph`.

Nodes (the ids of `home_stage2_mechanism_spec.md` section 2):
- `DS:<schema>`  the source table of a data schema, as declared (`input_fields`);
- `T1:<table>`   the table after its tier 1; a table is a schema or a join;
- `T2:<table>`   the table after its tier 2 (the same table when the list is empty or absent);
- `T3:<plot>`    what a plot reads: the T2 of its target after the plot's own tier 3 (the same when the list is empty).
Edges: `DS:S` to `T1:S`; `T1:I` to `T1:J` for every ingredient `I` of a join `J` (a join reads the tier 1 of its
ingredients, `recipe_tiers`); `T1:C` to `T2:C`; `T2:C` to `T3:p` for a plot `p` that targets `C`. Every table has T1, T2
and T3 with or without a join, and T2 and T3 may be empty (Eve, 2026-11-12). An ingredient that names a join is drawn too
(a chain of tier-1 nodes), although the engine and the checker take schema ids only today.

The steps of a node are the steps its tier RUNS: the author's `steps`, then the `audit_steps` of an audit recipe (D-0332, `recipe_tiers.step_list`).
So a filter audit step keeps the columns and a drop audit step removes the column it names, exactly as the same steps do when an author writes them
(a step number in a message counts the audit steps after the author's; the path names `steps`, which for an audit step is the list `audit_steps` of the same tier).

Order: every list this module returns is in graph order. It is a topological order (a node after all its parents); among
nodes that are free to come next the recipe order decides: schemas (`data_schemas`, `additional_datasets_schemas`,
`metadata_schema`), then joins, then plots in the order of the groups. Plots always come last, in the order of the recipe.
`parents(n)` is the exception: the order the recipe writes the ingredients in (the first ingredient is the base).

Columns: a node's columns are never guessed. `column_info(n)` says what is known and how:
- `declared`: the `input_fields` of the schema, kept through steps that only choose or order rows (`join_keys.ROW_STEPS`);
- `select`: the last step is a `polars_select` of plain column names (DEC23, DEC37): the columns are exactly those, in the
  order written, whatever came before;
- `drop`: a `polars_drop` of plain names after known columns;
- `provider`: where the recipe cannot say, the caller's `columns_provider(node_id)` (a dry run on column names, a stored
  schema; `recipe_format_spec.md` R10, not built) said so;
- `unknown`: nothing says. `names` is then None and `reason` names the step or the missing declaration. Any other step
  (a join, a rename, `polars_with_columns`, an unpivot, ...) leaves the columns unknown, because the recipe does not
  declare what such a step does to them.

Order of columns: for a table whose columns come from the declared fields, the SET of columns is known and the ORDER is not:
the engine returns the columns in the order of the FILE, not of `input_fields` (`ingestor.py`). `ColumnInfo.order_known` says
it: True only after a `polars_select` (the order written), kept by steps that choose or order rows and by a `polars_drop`;
False for `declared`, for a `provider` answer and for `unknown`. A caller must not rely on the order when it is False.

Provisional choices of the builder, not decided by the owner:
- a join that names a join as ingredient is drawn (a chain of tier-1 nodes), although the engine and the checker accept source
  tables only today;
- the signature `build_graph(raw, *, columns_provider=None)` differs from the one on the mechanism page;
- the build is strict: it raises `RecipeGraphError` on a broken recipe instead of returning a partial graph;
- the rule of what a step does to the column list (only row steps, a plain `polars_select` and a plain `polars_drop` are
  understood; every other step makes the columns unknown);
- the key-family rule: the `by` columns of an as-of join link families too, and families are by column name for the whole
  recipe (not per table).

Raises `RecipeGraphError` for what makes a graph impossible (a join that names an unknown ingredient, a join step whose `right_ingredient` is not one of the join's ingredients, a cycle of joins, a
plot whose target does not exist, one id for two things); the error lists every problem with the place in the recipe.
The checker (`recipe_check`) still judges the recipe; this module does not repeat its advice.

Consumed by: libs/utils/tests/test_recipe_graph.py. The checker takes the graph as its `graph` argument
(`columns_of(dataset_id)`). Blueprint's navigator, the tube map, the export lineage and the J08 call are rebuilt on it next.
If deleted: nothing runs yet; the rebuild of those callers needs it.

# @deps
# provides: function:build_graph, function:source_tables_of_plot, function:source_tables_of_table, class:RecipeGraph, class:RecipeGraphError, class:GraphProblem, class:Node, class:ColumnInfo, method:RecipeGraph.declared_entity_keys
# consumes: libs/utils/src/utils/recipe_tiers.py, libs/utils/src/utils/join_keys.py, libs/utils/src/utils/action_names.py
# consumed_by: libs/utils/tests/test_recipe_graph.py, libs/utils/src/utils/lineage_walk.py (declared_entity_keys, key_family_of, lineage_forward, plot_columns), libs/utils/src/utils/declared_plans.py (column_info, parents), libs/utils/src/utils/key_drop.py (build_graph), app/tests/test_read_source.py (source_tables_of_plot: the source tables that feed a plot, for the Source view of HOME, D-0310)
# doc: .claude/knowledge/architecture_decisions.md#adr-099, .claude/knowledge/architecture_decisions.md#adr-101, .claude/design/home_stage2_mechanism_spec.md (sections 1 to 3, P3), .claude/design/home_audit_steps.md (D1, 5a points 3, 8, 18)
# @end_deps
"""
import heapq
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from utils import action_names, join_keys, recipe_tiers, ui_schema

ColumnsProvider = Callable[[str], Optional[Sequence[str]]]


@dataclass(frozen=True)
class GraphProblem:
    """One thing that makes the graph impossible: the place in the recipe and what is wrong."""
    path: str
    message: str


class RecipeGraphError(ValueError):
    """The recipe cannot be drawn as a graph; `problems` lists every reason, each with its place in the recipe."""

    def __init__(self, problems: Iterable[GraphProblem]) -> None:
        self.problems: Tuple[GraphProblem, ...] = tuple(problems)
        super().__init__("the recipe cannot be drawn as a graph:\n" + "\n".join(f"  {p.path}: {p.message}" for p in self.problems))


@dataclass(frozen=True)
class Node:
    """One node. `steps` is a read-only tuple of the recipe's own step dictionaries (not copied; do not change them).

    kind: DS, T1, T2 or T3. name: the schema, table or plot id. path: the recipe element the node belongs to
    (`data_schemas.A`, `joins.J`, `analysis_groups.g.plots.p`). steps_path: where its step list is written (empty for DS).
    collection_kind: `schema` or `join` for DS, T1 and T2, None for T3. read_by_plot: for T2, whether a plot reads the table
    (a tier-2 list that no plot reads is run nowhere, check S07, J14); False for the other kinds."""
    id: str
    kind: str
    name: str
    path: str
    steps_path: str
    steps: Tuple[Any, ...]
    collection_kind: Optional[str] = None
    read_by_plot: bool = False


@dataclass(frozen=True)
class ColumnInfo:
    """What is known of the columns of a node. `names` is None when they are not known; `how` says why they are known
    (`declared`, `select`, `drop`, `provider`) or `unknown`; `reason` says in words what stops the knowledge (empty when known).
    `order_known`: True only when the ORDER of `names` is the order of the table (after a `polars_select`); False when only the set
    of columns is known (the engine returns the file's order for a source table, not the order of `input_fields`)."""
    names: Optional[Tuple[str, ...]]
    how: str
    reason: str = ""
    order_known: bool = False


_PLAIN_NAME = re.compile(r"[^\s.()]+")


def _is_plain_name(text: str) -> bool:
    return bool(_PLAIN_NAME.fullmatch(text)) and not text.startswith("pl.")


def _plain_names(value: Any) -> Optional[Tuple[str, ...]]:
    """A list of plain column names, or None. `*` and a `^...$` pattern are selections by pattern, not names."""
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    if any(item == "*" or (item.startswith("^") and item.endswith("$")) for item in value):
        return None
    return tuple(value)


def _as_names(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value]
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


class RecipeGraph:
    """The graph of one recipe. Built by `build_graph`; read-only."""

    def __init__(self, nodes: Dict[str, Node], parents: Dict[str, List[str]], bodies: Dict[str, Any],
                 plot_entries: Dict[str, Any], columns_provider: Optional[ColumnsProvider]) -> None:
        self._nodes = nodes                                   # in graph order
        self._index = {nid: i for i, nid in enumerate(nodes)}
        self._parents = parents
        self._children: Dict[str, List[str]] = {nid: [] for nid in nodes}
        for nid in nodes:
            for parent in parents[nid]:
                self._children[parent].append(nid)
        for nid in nodes:
            self._children[nid].sort(key=self._index.__getitem__)
        self._bodies = bodies                                 # collection id -> its schema or join body
        self._plot_entries = plot_entries
        self._provider = columns_provider
        self._info: Dict[str, ColumnInfo] = {}

    # ------------------------------------------------------------------ structure
    def nodes(self) -> List[str]:
        """Every node id, in graph order."""
        return list(self._nodes)

    def has_node(self, node_id: str) -> bool:
        """True when the recipe has a node of this id (`DS:`, `T1:`, `T2:` or `T3:` and a name); a bare table id is not a node."""
        return node_id in self._nodes

    def node(self, node_id: str) -> Node:
        """The node of an id; KeyError with a plain message when the recipe has none."""
        if node_id not in self._nodes:
            raise KeyError(f"no node {node_id!r} in the recipe graph")
        return self._nodes[node_id]

    def edges(self) -> List[Tuple[str, str]]:
        """Every edge (parent, child), by the graph order of the parent, then of the child."""
        found = [(parent, nid) for nid in self._nodes for parent in dict.fromkeys(self._parents[nid])]
        return sorted(found, key=lambda edge: (self._index[edge[0]], self._index[edge[1]]))

    def parents(self, node_id: str) -> List[str]:
        """The nodes a node reads directly, in the order the recipe gives them (the ingredients in written order)."""
        self.node(node_id)
        return list(dict.fromkeys(self._parents[node_id]))

    def children(self, node_id: str) -> List[str]:
        """The nodes that read a node directly, in graph order."""
        self.node(node_id)
        return list(self._children[node_id])

    def lineage_back(self, node_id: str) -> List[str]:
        """Every node a node depends on (not itself), in graph order."""
        return self._reach(node_id, self._parents)

    def lineage_forward(self, node_id: str) -> List[str]:
        """Every node that depends on a node (not itself), in graph order."""
        return self._reach(node_id, self._children)

    def _reach(self, node_id: str, links: Dict[str, List[str]]) -> List[str]:
        self.node(node_id)
        seen: Set[str] = set()
        stack = list(links[node_id])
        while stack:
            current = stack.pop()
            if current not in seen:
                seen.add(current)
                stack.extend(links[current])
        return sorted(seen, key=self._index.__getitem__)

    def collections(self) -> List[str]:
        """The ids of the tables (schemas, then joins), in graph order."""
        return [node.name for node in self._nodes.values() if node.kind == "T1"]

    def plots(self) -> List[str]:
        """The plot ids, in the order of the recipe."""
        return [node.name for node in self._nodes.values() if node.kind == "T3"]

    def plot_target(self, plot_id: str) -> str:
        """The table a plot reads (its `target_dataset`)."""
        parents = self.parents(f"T3:{plot_id}")
        return self._nodes[parents[0]].name

    def plots_reading(self, node_id: str) -> List[str]:
        """The plots that depend on a node (a plot node gives itself), in the order of the recipe."""
        node = self.node(node_id)
        if node.kind == "T3":
            return [node.name]
        return [self._nodes[n].name for n in self.lineage_forward(node_id) if self._nodes[n].kind == "T3"]

    def source_tables(self, node_id: str) -> List[str]:
        """The source tables (DS nodes) a node depends on, itself included when it is one, in graph order."""
        node = self.node(node_id)
        found = [n for n in self.lineage_back(node_id) if self._nodes[n].kind == "DS"]
        return ([node_id] if node.kind == "DS" else []) + found

    def same_t1_definition(self, table_a: str, table_b: str) -> bool:
        """True when two tables have the same definition up to their tier 1, as the TEXT of the recipe: for schemas the same source,
        null values, strip, `input_fields` and tier 1; for joins the same ingredients in the same order and the same tier 1. A schema
        and a join are never the same. Labels, descriptions, comments and the tier 2 are not part of it. KeyError for an id that is not
        a table.

        Two DIFFERENT schema ids are the same only when both carry an explicit source path (`source` with a type and a `path`) and the
        paths are equal: the engine often finds the file by the table id, so equal text without a path may read two files.
        The answer is about the recipe text only. It says nothing about the content of the files, and it must never be used alone to
        share a stored table: the data hash decides that (D-0025)."""
        for table in (table_a, table_b):
            if table not in self._bodies:
                raise KeyError(f"no table {table!r} in the recipe")
        if table_a != table_b and self._nodes[f"T1:{table_a}"].collection_kind == "schema" == self._nodes[f"T1:{table_b}"].collection_kind:
            path_a, path_b = self._explicit_path(table_a), self._explicit_path(table_b)
            if path_a is None or path_a != path_b:
                return False
        return self._definition(table_a) == self._definition(table_b)

    def _explicit_path(self, table: str) -> Optional[str]:
        source = self._bodies[table].get("source")
        if isinstance(source, dict) and source.get("type") and isinstance(source.get("path"), str) and source["path"]:
            return source["path"]
        return None

    def _definition(self, table: str) -> Tuple[Any, ...]:
        body = self._bodies[table]
        if self._nodes[f"T1:{table}"].collection_kind == "join":
            ingredients = tuple(self._nodes[p].name for p in self._parents[f"T1:{table}"])
            return ("join", ingredients, body.get("tier1"))
        return ("schema", body.get("source"), body.get("null_values"), body.get("strip"), body.get("input_fields"), body.get("tier1"))

    # ------------------------------------------------------------------ columns
    def _resolve(self, node_or_table: str) -> Optional[str]:
        if node_or_table in self._nodes:
            return node_or_table
        if f"T1:{node_or_table}" in self._nodes:
            return f"T1:{node_or_table}"
        return None

    def column_info(self, node_or_table: str) -> ColumnInfo:
        """What is known of a node's columns and why; a table id means its tier 1. `order_known` says whether the order of `names` is a
        fact or only the order the recipe lists them in. KeyError for an id the recipe does not have."""
        node_id = self._resolve(node_or_table)
        if node_id is None:
            raise KeyError(f"no node or table {node_or_table!r} in the recipe graph")
        if node_id not in self._info:
            info = self._derive(node_id)
            if info.names is None and self._provider is not None:
                given = self._provider(node_id)
                if given is not None:
                    info = ColumnInfo(tuple(given), "provider", order_known=False)
            self._info[node_id] = info
        return self._info[node_id]

    def columns_of(self, node_or_table: str) -> Optional[Tuple[str, ...]]:
        """The columns of a node, or of a table after its tier 1 (the checker's call); None when not known.

        The SET is what is known. The order is the order of the table only when `column_info(...).order_known` is True (after a
        `polars_select`); for a table whose columns come from the declared fields it is the order of `input_fields`, which the
        engine does not promise (it returns the file's order).

        None is also the answer for an id the recipe does not have: `has_node` tells the two apart."""
        if self._resolve(node_or_table) is None:
            return None
        return self.column_info(node_or_table).names

    def _derive(self, node_id: str) -> ColumnInfo:
        node = self._nodes[node_id]
        if node.kind == "DS":
            fields = self._bodies[node.name].get("input_fields")
            if not isinstance(fields, dict):
                return ColumnInfo(None, "unknown", f"{node.path}.input_fields is not a mapping of column names")
            if not fields:
                return ColumnInfo(None, "unknown", f"{node.path}.input_fields is empty, so the table keeps every column of its file and the recipe does not list them")
            if not all(isinstance(name, str) for name in fields):
                return ColumnInfo(None, "unknown", f"{node.path}.input_fields has a name that is not text")
            return ColumnInfo(tuple(fields), "declared", order_known=False)
        parents = self._parents[node_id]
        if not parents:
            return ColumnInfo(None, "unknown", f"{node.path} has no table to start from")
        start = self.column_info(parents[0])           # a join starts from its first ingredient: the base table
        return self._flow(start, node.steps, node.steps_path)

    @staticmethod
    def _flow(start: ColumnInfo, steps: Sequence[Any], steps_path: str) -> ColumnInfo:
        names, how, reason, ordered = start.names, start.how, start.reason, start.order_known
        for number, step in enumerate(steps, start=1):
            where = f"{steps_path}[{number}]"
            action = step.get("action") if isinstance(step, dict) else None
            if action in join_keys.ROW_STEPS:
                continue
            if action == action_names.SELECT:
                chosen = _plain_names(step.get("exprs"))
                extra = sorted(str(key) for key in step if key != "exprs" and key not in ui_schema.STEP_KEYS)
                if chosen is not None and not extra and all(_is_plain_name(name) for name in chosen):
                    names, how, reason, ordered = chosen, "select", "", True
                    continue
                why = (f"{where} ({action}): the step has the key(s) {extra}, which the engine does not expose" if extra else
                       f"{where} ({action}): `exprs` is not a list of plain column names")
            elif action == action_names.DROP and names is not None:
                dropped = _plain_names(step.get("columns"))
                if dropped is not None:
                    names, how = tuple(n for n in names if n not in set(dropped)), "drop"
                    continue
                why = f"{where} ({action}): `columns` is not a list of plain column names"
            else:
                why = f"{where} ({action}): the recipe does not declare what this step does to the columns"
            if names is not None:
                names, how, reason, ordered = None, "unknown", why, False
        return ColumnInfo(names, how, reason, ordered if names is not None else False)

    def column_presence(self, column: str) -> Dict[str, str]:
        """For every node, in graph order: `yes` (the column is certainly there), `no` (the columns are known and it is not) or `unknown`."""
        found: Dict[str, str] = {}
        for node_id in self._nodes:
            names = self.column_info(node_id).names
            found[node_id] = "unknown" if names is None else ("yes" if column in names else "no")
        return found

    def nodes_with_column(self, column: str) -> List[str]:
        """The nodes that certainly have the column, in graph order. A node whose columns are unknown is not listed:
        `nodes_with_unknown_columns` lists those, so nothing is hidden."""
        return [n for n, state in self.column_presence(column).items() if state == "yes"]

    def nodes_with_unknown_columns(self) -> List[str]:
        """The nodes whose columns are not known, in graph order."""
        return [n for n in self._nodes if self.column_info(n).names is None]

    def shared_columns(self, node_a: str, node_b: str) -> Optional[Tuple[str, ...]]:
        """The columns two nodes (or two tables, at their tier 1) both have, in the order of the first; None when either side is unknown.

        A set: the order is a fact only when `column_info` of the first node says `order_known`."""
        first, second = self.columns_of(node_a), self.columns_of(node_b)
        if first is None or second is None:
            return None
        return tuple(name for name in first if name in set(second))

    def plot_columns(self, plot_id: str) -> Tuple[str, ...]:
        """The columns the plot entry names: the values of `mapping`, `facet_by` and the columns of `filters`, once each, in that order.

        Columns named inside a layer's own parameters are not read."""
        entry = self._plot_entries[plot_id]
        names: List[str] = []
        mapping = entry.get("mapping")
        if isinstance(mapping, dict):
            names.extend(value for value in mapping.values() if isinstance(value, str))
        names.extend(_as_names(entry.get("facet_by")))
        filters = entry.get("filters")
        for item in filters if isinstance(filters, list) else []:
            if isinstance(item, dict) and isinstance(item.get("column"), str):
                names.append(item["column"])
        return tuple(dict.fromkeys(names))

    # ------------------------------------------------------------------ key families
    def key_families(self) -> List[Tuple[str, ...]]:
        """The key families: the columns declared `is_entity_key` in any schema, joined into one family when a join equates them
        (`on`, or `left_on` with `right_on`). Never found from equal column names alone. A family is a sorted tuple of column
        names; the list is sorted. A join on columns that no schema declares as a key makes no family (`home_audit_steps.md` 5a points 3, 13)."""
        declared = {name for body in self._schema_bodies() if isinstance(body.get("input_fields"), dict)
                    for name, field in body["input_fields"].items() if isinstance(field, dict) and field.get("is_entity_key") is True}
        parent: Dict[str, str] = {}

        def find(name: str) -> str:
            parent.setdefault(name, name)
            while parent[name] != name:
                parent[name] = parent[parent[name]]
                name = parent[name]
            return name

        for name in declared:
            find(name)
        for table in self.collections():
            if self._nodes[f"T1:{table}"].collection_kind != "join":
                continue
            for step in self._nodes[f"T1:{table}"].steps:
                if isinstance(step, dict) and step.get("action") in join_keys.JOIN_ACTIONS:
                    left, right = join_keys.key_columns(step)
                    for left_name, right_name in zip(left, right):
                        parent[find(left_name)] = find(right_name)
        groups: Dict[str, List[str]] = {}
        for name in list(parent):
            groups.setdefault(find(name), []).append(name)
        families = [tuple(sorted(group)) for group in groups.values() if declared & set(group)]
        return sorted(families)

    def declared_entity_keys(self, table_id: str) -> Tuple[str, ...]:
        """The columns a schema declares `is_entity_key` in its `input_fields`, in the order written; empty for a join or for a schema
        that declares none. KeyError for an id that is not a table of the recipe. The declaration only: the name is never guessed."""
        if table_id not in self._bodies:
            raise KeyError(f"no table {table_id!r} in the recipe graph")
        if self._nodes[f"T1:{table_id}"].collection_kind != "schema":
            return ()
        fields = self._bodies[table_id].get("input_fields")
        return tuple(name for name, field in fields.items() if isinstance(field, dict) and field.get("is_entity_key") is True) if isinstance(fields, dict) else ()

    def key_family_of(self, column: str) -> Optional[Tuple[str, ...]]:
        """The key family a column belongs to, or None."""
        return next((family for family in self.key_families() if column in family), None)

    def _schema_bodies(self) -> List[dict]:
        return [self._bodies[t] for t in self.collections() if self._nodes[f"T1:{t}"].collection_kind == "schema"]


# ---------------------------------------------------------------------- building

# PROVISIONAL names (the coordinator's, owner's question P-B7): source_tables_of_plot, source_tables_of_table. It lives here, with the graph, because it is a pure query of the map (no data,
# no file, no engine); the orchestrator reads the tables it names (`DataOrchestrator.read_source`).
def source_tables_of_plot(graph: "RecipeGraph", plot_id: str) -> List[str]:
    """The ids of the source tables (data schemas, metadata, additional datasets) that feed a plot, each once, in graph order.
    The order is the graph order (a table after those it depends on; among free ones the order of the recipe: schemas as declared), not the order
    the ingredients of a join are written in. KeyError ("The recipe has no plot 'x'.") for a plot id the recipe does not have: KeyError is the
    type `RecipeGraph.node` and `plot_key` already raise, so callers of the graph handle it. A plot that reads a table directly lists that table's source;
    a plot on a join lists the source of every ingredient."""
    if not graph.has_node(f"T3:{plot_id}"):
        raise KeyError(f"The recipe has no plot '{plot_id}'.")
    return [graph.node(n).name for n in graph.source_tables(f"T3:{plot_id}")]


def source_tables_of_table(graph: "RecipeGraph", table_id: str) -> List[str]:
    """The same for a table (a schema or a join): the source tables its tier 1 reads, each once, in graph order.
    The order is the graph order, as for a plot. KeyError ("The recipe has no table or join 'x'.") for an id that is not a table of the recipe."""
    if not graph.has_node(f"T1:{table_id}"):
        raise KeyError(f"The recipe has no table or join '{table_id}'.")
    return [graph.node(n).name for n in graph.source_tables(f"T1:{table_id}")]


def build_graph(raw: Any, *, columns_provider: Optional[ColumnsProvider] = None) -> RecipeGraph:
    """The graph of a resolved recipe.

    columns_provider: optional `f(node_id) -> columns or None`, asked only for a node whose columns the recipe cannot say.
    Raises `RecipeGraphError` listing every reason when the graph cannot be drawn."""
    if not isinstance(raw, dict):
        raise RecipeGraphError([GraphProblem("", "the recipe is not a mapping")])
    problems: List[GraphProblem] = []
    schemas = _schemas(raw, problems)
    joins = _joins(raw, schemas, problems)
    ingredients = _ingredients(joins, schemas, problems)
    _join_steps(joins, ingredients, problems)
    plots = _plots(raw, set(schemas) | set(joins), problems)
    cycle = _cycle({jid: [i for i in ids if i in joins] for jid, ids in ingredients.items()})
    if cycle:
        first = cycle[0]
        problems.append(GraphProblem(f"joins.{first}.ingredients", "the joins form a cycle: " + " -> ".join(cycle + [first])
                                     + "; a join reads the tier 1 of its ingredients, so none of them can read it back"))
    if problems:
        raise RecipeGraphError(problems)

    read = {target for _, _, target, _ in plots}
    nodes: Dict[str, Node] = {}
    parents: Dict[str, List[str]] = {}
    bodies: Dict[str, Any] = {}
    for sid, (path, body) in schemas.items():
        bodies[sid] = body
        nodes[f"DS:{sid}"] = Node(f"DS:{sid}", "DS", sid, path, "", (), "schema")
        parents[f"DS:{sid}"] = []
        _collection_nodes(nodes, parents, sid, path, body, "schema", sid in read, [f"DS:{sid}"])
    for jid, (path, body) in joins.items():
        bodies[jid] = body
        _collection_nodes(nodes, parents, jid, path, body, "join", jid in read, [f"T1:{i}" for i in ingredients[jid]])
    plot_entries: Dict[str, Any] = {}
    for pid, path, target, entry in plots:
        plot_entries[pid] = entry
        steps = tuple(recipe_tiers.step_list(entry, "tier3"))
        nodes[f"T3:{pid}"] = Node(f"T3:{pid}", "T3", pid, path, f"{path}.tier3.steps", steps)
        parents[f"T3:{pid}"] = [f"T2:{target}"]
    ordered = _graph_order(nodes, parents)
    return RecipeGraph({nid: nodes[nid] for nid in ordered}, parents, bodies, plot_entries, columns_provider)


def _collection_nodes(nodes: Dict[str, Node], parents: Dict[str, List[str]], cid: str, path: str, body: Any, kind: str,
                      read_by_plot: bool, t1_parents: List[str]) -> None:
    t1_steps = tuple(recipe_tiers.step_list(body, "tier1"))
    t2_steps = tuple(recipe_tiers.step_list(body, "tier2"))
    nodes[f"T1:{cid}"] = Node(f"T1:{cid}", "T1", cid, path, f"{path}.tier1.steps", t1_steps, kind)
    parents[f"T1:{cid}"] = t1_parents
    nodes[f"T2:{cid}"] = Node(f"T2:{cid}", "T2", cid, path, f"{path}.tier2.steps", t2_steps, kind, read_by_plot)
    parents[f"T2:{cid}"] = [f"T1:{cid}"]


def _schemas(raw: dict, problems: List[GraphProblem]) -> Dict[str, Tuple[str, Any]]:
    found: Dict[str, Tuple[str, Any]] = {}

    def add(sid: Any, path: str, body: Any) -> None:
        if not isinstance(body, dict):
            problems.append(GraphProblem(path, "a schema is a mapping"))
        elif sid in found:
            problems.append(GraphProblem(path, f"the schema id {sid!r} is also written at {found[sid][0]}; an id names one table"))
        else:
            found[sid] = (path, body)

    for section in recipe_tiers.SCHEMA_SECTIONS:
        held = raw.get(section)
        if held is None:
            continue
        if not isinstance(held, dict):
            problems.append(GraphProblem(section, "a section of schemas is a mapping of id to schema"))
            continue
        for sid, body in held.items():
            add(sid, f"{section}.{sid}", body)
    if recipe_tiers.METADATA_SCHEMA in raw:
        add(recipe_tiers.METADATA_SCHEMA, recipe_tiers.METADATA_SCHEMA, raw[recipe_tiers.METADATA_SCHEMA])
    return found


def _joins(raw: dict, schemas: Dict[str, Tuple[str, Any]], problems: List[GraphProblem]) -> Dict[str, Tuple[str, Any]]:
    held = raw.get("joins")
    found: Dict[str, Tuple[str, Any]] = {}
    if held is None:
        return found
    if not isinstance(held, dict):
        problems.append(GraphProblem("joins", "joins is a mapping of id to join"))
        return found
    for jid, body in held.items():
        path = f"joins.{jid}"
        if not isinstance(body, dict):
            problems.append(GraphProblem(path, "a join is a mapping"))
        elif jid in schemas:
            problems.append(GraphProblem(path, f"the id {jid!r} names a schema ({schemas[jid][0]}) and a join; a plot's target must name one table"))
        else:
            found[jid] = (path, body)
    return found


def _ingredients(joins: Dict[str, Tuple[str, Any]], schemas: Dict[str, Tuple[str, Any]], problems: List[GraphProblem]) -> Dict[str, List[str]]:
    found: Dict[str, List[str]] = {}
    for jid, (path, body) in joins.items():
        ids: List[str] = []
        listed = body.get("ingredients")
        for number, item in enumerate(listed if isinstance(listed, list) else [], start=1):
            where = f"{path}.ingredients[{number}]"
            name = item.get("dataset_id") if isinstance(item, dict) else None
            if not isinstance(name, str):
                problems.append(GraphProblem(where, "an ingredient is {dataset_id: <table id>}"))
            elif name not in schemas and name not in joins:
                problems.append(GraphProblem(where, f"names {name!r}, which is not a schema or a join of this recipe"))
            elif name not in ids:
                ids.append(name)
        found[jid] = ids
    return found


def _join_steps(joins: Dict[str, Tuple[str, Any]], ingredients: Dict[str, List[str]], problems: List[GraphProblem]) -> None:
    """A tier-1 step of a join that names a `right_ingredient` the join does not list would be a missing edge (checker J05)."""
    for jid, (path, body) in joins.items():
        for number, step in enumerate(recipe_tiers.step_list(body, "tier1"), start=1):
            name = step.get("right_ingredient") if isinstance(step, dict) else None
            if isinstance(name, str) and name not in ingredients[jid]:
                problems.append(GraphProblem(f"{path}.tier1.steps[{number}]",
                                             f"the step names right_ingredient {name!r}, which is not an ingredient of join {jid!r}; list it in ingredients"))


def _plots(raw: dict, tables: Set[str], problems: List[GraphProblem]) -> List[Tuple[str, str, str, dict]]:
    """[(plot id, path, target table, entry)] in the order of the recipe."""
    groups = raw.get("analysis_groups")
    found: List[Tuple[str, str, str, dict]] = []
    if groups is None:
        return found
    if not isinstance(groups, dict):
        problems.append(GraphProblem("analysis_groups", "analysis_groups is a mapping of id to group"))
        return found
    seen: Dict[str, str] = {}
    for gid, group in groups.items():
        plots = group.get("plots") if isinstance(group, dict) else None
        if not isinstance(plots, dict):
            problems.append(GraphProblem(f"analysis_groups.{gid}", "a group is a mapping with a `plots` mapping"))
            continue
        for pid, entry in plots.items():
            path = f"analysis_groups.{gid}.plots.{pid}"
            if not isinstance(entry, dict):
                problems.append(GraphProblem(path, "a plot is a mapping"))
                continue
            if pid in seen:
                problems.append(GraphProblem(path, f"the plot id {pid!r} is also written at {seen[pid]}; it is written twice and a plot id names one plot"))
                continue
            seen[pid] = path
            target = entry.get("target_dataset")
            if not isinstance(target, str):
                problems.append(GraphProblem(path, "the plot has no target_dataset, so no table to read"))
            elif target not in tables:
                problems.append(GraphProblem(f"{path}.target_dataset", f"names {target!r}, which is not a schema or a join of this recipe"))
            else:
                found.append((pid, path, target, entry))
    return found


def _cycle(reads: Dict[str, List[str]]) -> List[str]:
    """One cycle of joins (a list of ids, each reading the next, the last reading the first), or an empty list."""
    state: Dict[str, int] = {}
    trail: List[str] = []

    def visit(jid: str) -> List[str]:
        state[jid] = 1
        trail.append(jid)
        for other in reads.get(jid, []):
            if state.get(other) == 1:
                return trail[trail.index(other):]
            if state.get(other) is None:
                inner = visit(other)
                if inner:
                    return inner
        trail.pop()
        state[jid] = 2
        return []

    for jid in reads:
        if state.get(jid) is None:
            found = visit(jid)
            if found:
                return found
    return []


def _graph_order(nodes: Dict[str, Node], parents: Dict[str, List[str]]) -> List[str]:
    """A topological order; the node written earlier in the recipe comes first when several are free."""
    construction = {nid: i for i, nid in enumerate(nodes)}
    waiting = {nid: len(set(parents[nid])) for nid in nodes}
    children: Dict[str, List[str]] = {nid: [] for nid in nodes}
    for nid in nodes:
        for parent in set(parents[nid]):
            children[parent].append(nid)
    ready = [construction[nid] for nid, count in waiting.items() if count == 0]
    heapq.heapify(ready)
    names = list(nodes)
    order: List[str] = []
    while ready:
        nid = names[heapq.heappop(ready)]
        order.append(nid)
        for child in children[nid]:
            waiting[child] -= 1
            if waiting[child] == 0:
                heapq.heappush(ready, construction[child])
    return order
