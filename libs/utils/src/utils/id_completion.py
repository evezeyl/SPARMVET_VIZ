# engine: python-polars (reads the id column of a table and adds the missing lines with Polars frames)
"""The completion of the ids: before anything else, every table that names the entity gets a line for each entity id it lacks.

D-0572 to D-0599, D-0613 (her decisions, quoted in the ledger). The purpose, in her words (D-0584): "so that the data can always use left joints to
join with the metadata - limiting lineages problems". What it does, and nothing else:

- The set of ids is the union of the entity ids of the metadata table (when the recipe has one) and of every table of `data_schemas` that declares an
  entity id (`is_entity_id`). Each table of that set is taken AS READ from its file (strip, missing-value words and declared type applied, no recipe step).
- Each such table gets a line for each id of the union it lacks: the id, every other value missing, and a yes/no column (its `marker`) that is true on
  the added lines and false on its own. The metadata table is completed in the same way, with its own marker. Only lines are added; nothing is removed or
  changed (D-0597: "changes or removes nothing from the user's data").
- A line with no usable id (missing, empty, or only spaces) is not an id: it stays where it is, is not completed and is not part of the union. The report lists it.
- A table under `additional_datasets_schemas` (a look-up, a database) is never completed.
- The recipe says what an added line means (`completion: {marker, meaning}` on every table that takes part, D-0574, D-0586); the recipe never records how
  many lines were added (D-0574).
- Nothing blocks. The three checks of the ids are warnings (D-0581): the ids of a table that the metadata lacks, the ids of the metadata that a table
  lacks, and, after the completion, the equality of all the sets (a difference there is a bug of the app, D-0590).

The marker is not a zero (D-0573): an added line carries no value, only the marker. What a count, a sum or a stamp of the recipe does with it is the recipe's
choice, which is why the recipe must say what the lines mean. The marker column is kept (D-0586); a step that lists a fixed set of columns after it is the
recipe maker's to extend.

PROVISIONAL (an agent's choices, D-0613: small open points are built with the agents' lean and listed): the name `completion` and its two keys; the list of
meanings; the marker is a Boolean column appended as the last column; the added lines are appended after the table's own lines, in the order of the ids; the
id is compared as text; a table that declares several entity ids is completed on the first one written.

Consumed by: `app/modules/orchestrator.py` (`_read_source`, `id_report`), `libs/utils/src/utils/recipe_check.py` (E04 to E07), `app/modules/cache_keys.py`.
If deleted: the ids of the tables are never made equal.

# @deps
# provides: function:participants, function:completion_problems, function:read_ids, function:complete_table, function:union_of, function:build_report, class:Participant, class:TableIds, class:IdReport, class:TableReport
# consumes: libs/utils/src/utils/recipe_spec.yaml (completion), libs/utils/src/utils/errors.py
# consumed_by: app/modules/orchestrator.py, libs/utils/src/utils/recipe_check.py, libs/utils/src/utils/id_log.py, app/modules/cache_keys.py
# doc: .claude/design/recipe_format_spec.md (7.3, E04 to E07), .claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md
# @end_deps
"""
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import polars as pl

from utils.errors import DataAnalysisRecipeError

COMPLETION = "completion"
MARKER = "marker"
MEANING = "meaning"
DATA = "data"
METADATA = "metadata"
METADATA_ID = "metadata_schema"

# How many lines with no usable id a report lists by number (the count is always whole). PROVISIONAL.
LISTED_NO_ID_LINES = 100


# ---------------------------------------------------------------------------
# What the recipe says
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Participant:
    """A table that takes part in the completion: `kind` is `data` or `metadata`; `id_column` is the first field it declares `is_entity_id`;
    `marker` is the name of the yes/no column the completion adds; `meaning` is what an added line means (a word of the list of the specification)."""
    table: str
    kind: str
    id_column: str
    marker: str
    meaning: str


def declared_id_columns(schema: Any) -> List[str]:
    """The columns a schema declares `is_entity_id: true`, in the order written."""
    fields = schema.get("input_fields") if isinstance(schema, dict) else None
    if not isinstance(fields, dict):
        return []
    return [name for name, field in fields.items() if isinstance(field, dict) and field.get("is_entity_id") is True]


def candidate_tables(raw: dict) -> List[Tuple[str, str, dict]]:
    """(table id, kind, schema) of every table that could take part: the metadata table, then each table of `data_schemas`, when it declares an entity id.
    The tables of `additional_datasets_schemas` are never candidates (D-0613, her definition: look-ups and databases, not results about the entities)."""
    found: List[Tuple[str, str, dict]] = []
    meta = raw.get(METADATA_ID) if isinstance(raw, dict) else None
    if isinstance(meta, dict) and declared_id_columns(meta):
        found.append((METADATA_ID, METADATA, meta))
    data = raw.get("data_schemas") if isinstance(raw, dict) else None
    if isinstance(data, dict):
        for table, schema in data.items():
            if isinstance(schema, dict) and declared_id_columns(schema):
                found.append((str(table), DATA, schema))
    return found


def allowed_meanings(spec: dict) -> Dict[str, List[str]]:
    """The words that say what an added line means, per kind (`data` or `metadata`), from the specification."""
    return {kind: list(words) for kind, words in spec["completion"]["meanings"].items()}


def block_problems(table: str, kind: str, schema: dict, spec: dict, path: str) -> List[Tuple[str, str, str, str]]:
    """(code, path, message, fix) of what is wrong with the `completion` block of one table that declares an entity id.

    E04: no block. E05: the block is not a mapping, has an unknown or a missing key, or a meaning that is not on the list. E06: the marker is not a column
    name of the form the specification gives, or is already a column of the table (and, for the whole recipe, a marker that two tables share)."""
    cspec = spec["completion"]
    meanings = allowed_meanings(spec)[kind]
    example = f"completion: {{{MARKER}: {cspec['default_markers'][kind]}, {MEANING}: {meanings[0]}}}"
    block = schema.get(COMPLETION)
    place = f"{path}.{COMPLETION}"
    if block is None:
        return [("E04", place, f"the table {table!r} declares an entity id and has no {COMPLETION} block, so the recipe does not say what a line added "
                 "for an entity that the table lacks means",
                 f"write {example}; the meaning is one of: {', '.join(meanings)}")]
    if not isinstance(block, dict):
        return [("E05", place, f"{COMPLETION} of {table!r} is not a mapping", f"write {example}")]
    out: List[Tuple[str, str, str, str]] = []
    known = set(cspec["keys"])
    for key in block:
        if key not in known:
            out.append(("E05", f"{place}.{key}", f"{key} is not a key of {COMPLETION}", f"the keys are {', '.join(cspec['keys'])}"))
    for key in cspec["keys"]:
        if key not in block:
            out.append(("E05", place, f"{COMPLETION} of {table!r} has no {key}", f"write {example}"))
    marker = block.get(MARKER)
    if MARKER in block:
        if not isinstance(marker, str) or not re.fullmatch(cspec["marker_pattern"], marker):
            out.append(("E06", f"{place}.{MARKER}", f"the marker {marker!r} is not a column name",
                        f"write a name of letters, digits and underscores that starts with a letter, for example {cspec['default_markers'][kind]}"))
        elif marker in (schema.get("input_fields") or {}):
            out.append(("E06", f"{place}.{MARKER}", f"the marker {marker!r} is already a field of the table {table!r}",
                        "write another name: the marker is a new column that the completion adds"))
    meaning = block.get(MEANING)
    if MEANING in block and meaning not in meanings:
        out.append(("E05", f"{place}.{MEANING}", f"the meaning {meaning!r} is not one the check knows for {kind} tables",
                    f"write one of: {', '.join(meanings)}"))
    return out


def completion_problems(raw: dict, spec: dict) -> List[Tuple[str, str, str, str]]:
    """(code, path, message, fix) for the whole recipe: the blocks of the tables that declare an entity id (E04, E05, E06; E06 also when two tables share a marker), a block on a table that cannot take
    part (E07). Nothing is read from disk."""
    problems: List[Tuple[str, str, str, str]] = []
    taking_part = {table for table, _, _ in candidate_tables(raw)}
    for table, kind, schema in candidate_tables(raw):
        path = METADATA_ID if kind == METADATA else f"data_schemas.{table}"
        problems += block_problems(table, kind, schema, spec, path)
    # a block where the table takes no part: an additional table (never completed), or a table that declares no entity id
    additional = raw.get("additional_datasets_schemas")
    for table, schema in (additional.items() if isinstance(additional, dict) else []):
        if isinstance(schema, dict) and COMPLETION in schema:
            problems.append(("E07", f"additional_datasets_schemas.{table}.{COMPLETION}",
                             f"{COMPLETION} on {table!r}, which is a look-up or a database: it is never completed", f"remove {COMPLETION}"))
    data = raw.get("data_schemas")
    for table, schema in (data.items() if isinstance(data, dict) else []):
        if isinstance(schema, dict) and COMPLETION in schema and str(table) not in taking_part:
            problems.append(("E07", f"data_schemas.{table}.{COMPLETION}", f"{COMPLETION} on {table!r}, which declares no entity id, so nothing is completed",
                             f"remove {COMPLETION}, or write is_entity_id: true on the column that identifies the entity"))
    seen: Dict[str, str] = {}
    for table, kind, schema in candidate_tables(raw):
        block = schema.get(COMPLETION)
        name = block.get(MARKER) if isinstance(block, dict) else None
        if isinstance(name, str):
            if name in seen:
                path = METADATA_ID if kind == METADATA else f"data_schemas.{table}"
                problems.append(("E06", f"{path}.{COMPLETION}.{MARKER}", f"the marker {name!r} of {table!r} is also the marker of {seen[name]!r}",
                                 f"write a different marker for each table, for example {table}_{name}: a join of the two tables would otherwise hold two columns of one name"))
            seen.setdefault(name, table)
    meta = raw.get(METADATA_ID)
    if isinstance(meta, dict) and COMPLETION in meta and METADATA_ID not in taking_part:
        problems.append(("E07", f"{METADATA_ID}.{COMPLETION}", f"{COMPLETION} on the metadata, which declares no entity id, so nothing is completed",
                         f"remove {COMPLETION}, or write is_entity_id: true on the column that identifies the entity"))
    return problems


def participants(raw: dict, spec: Optional[dict] = None) -> List[Participant]:
    """The tables that take part in the completion of this recipe, the metadata first, then the data tables in the order written.

    Raises `DataAnalysisRecipeError` (plain words, with the table and what to write) when a table declares an entity id and its `completion` block is missing or
    wrong: the recipe check refuses such a recipe (E04 to E06), and the engine does not run it either (never a default that hides the missing words)."""
    if spec is None:
        from utils.recipe_check import spec as load_spec
        spec = load_spec()
    problems = [p for p in completion_problems(raw, spec) if p[0] != "E07"]
    if problems:
        code, path, message, fix = problems[0]
        more = f" (and {len(problems) - 1} more problem(s) of the same kind)" if len(problems) > 1 else ""
        raise DataAnalysisRecipeError(f"The completion of the ids cannot run: {message} [{code} at {path}]{more}.", tip=fix[:1].upper() + fix[1:] + ".")
    out = []
    for table, kind, schema in candidate_tables(raw):
        block = schema[COMPLETION]
        out.append(Participant(table, kind, declared_id_columns(schema)[0], block[MARKER], block[MEANING]))
    return out


def participant_of(raw: dict, table: str, spec: Optional[dict] = None) -> Optional[Participant]:
    """The participant that is `table`, or None when the table does not take part (a look-up, a table that declares no entity id)."""
    for participant in participants(raw, spec):
        if participant.table == table:
            return participant
    return None


def plan_material(raw: dict) -> dict:
    """What the completion reads of the recipe, as plain data: for each table that takes part, what decides the ids it holds (its id column, its declared
    type, its `strip` and `null_values`, its source, its `completion` block). The key of a stored table that reads a participant holds it, so that a change in
    any participant, or a table that starts to declare an entity id, moves the key (cache_keys.py). Empty when no table takes part. Never raises: a recipe
    with a wrong block is refused elsewhere, and the material then holds what is written."""
    out = {}
    for table, kind, schema in candidate_tables(raw):
        columns = declared_id_columns(schema)
        fields = schema.get("input_fields") or {}
        out[table] = {"kind": kind, "id_columns": columns, "id_fields": {c: fields[c] for c in columns}, "null_values": schema.get("null_values"),
                      "strip": schema.get("strip"), "source": schema.get("source"), COMPLETION: schema.get(COMPLETION)}
    return out


# ---------------------------------------------------------------------------
# What the data says
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TableIds:
    """The ids of one table as it was read (or as it is after the completion): `ids` are the distinct usable ids as text, sorted; `no_id_lines` are the
    numbers of the data lines (the first line after the header is 1) with no usable id; `rows` is the number of lines of the table."""
    table: str
    kind: str
    id_column: str
    rows: int
    ids: Tuple[str, ...]
    no_id_lines: Tuple[int, ...]


def read_ids(lf: pl.LazyFrame, participant: Participant) -> TableIds:
    """The ids of a table as it is read. An id is usable when it is not missing and is not an empty text or a text of only spaces; it is compared as text, as written."""
    column = participant.id_column
    frame = lf.select(pl.col(column).cast(pl.String).alias("id")).with_row_index("n", offset=1).collect()
    usable = pl.col("id").is_not_null() & (pl.col("id").str.strip_chars() != "")
    ids = sorted(set(frame.filter(usable)["id"].to_list()))
    no_id = tuple(frame.filter(~usable)["n"].to_list())
    return TableIds(participant.table, participant.kind, column, frame.height, tuple(ids), no_id)


def union_of(read: Iterable[TableIds]) -> Tuple[str, ...]:
    """The union of the usable ids of all the tables that take part, sorted: the one set every table is completed to."""
    found: set = set()
    for table in read:
        found.update(table.ids)
    return tuple(sorted(found))


def complete_table(lf: pl.LazyFrame, participant: Participant, union: Sequence[str], own_ids: Iterable[str]) -> pl.LazyFrame:
    """The table with the marker column (false on every own line) and a line for each id of `union` that `own_ids` lacks (true), appended after the own lines in
    the order of the ids. Every other value of an added line is missing. Nothing is removed or changed."""
    schema = lf.collect_schema()
    if participant.marker in schema.names():
        raise DataAnalysisRecipeError(
            f"The completion of '{participant.table}' adds the column '{participant.marker}', and the table already has a column of that name.",
            tip="Write another marker in the completion block of the table.")
    own = set(own_ids)
    added = [i for i in union if i not in own]
    marked = lf.with_columns(pl.lit(False).alias(participant.marker))
    if not added:
        return marked
    columns: Dict[str, pl.Series] = {name: pl.Series(name, [None] * len(added), dtype=dtype) for name, dtype in schema.items()}
    try:
        columns[participant.id_column] = pl.Series(participant.id_column, added, dtype=pl.String).cast(schema[participant.id_column])
    except Exception as exc:  # noqa: BLE001 - a Polars error names no table: say which table and which id column
        raise DataAnalysisRecipeError(
            f"The ids that '{participant.table}' lacks cannot be written in its id column '{participant.id_column}', declared {schema[participant.id_column]}: {str(exc)[:160]}",
            tip="Declare the id column as String (or Categorical), the types an id keeps its written form in.") from exc
    columns[participant.marker] = pl.Series(participant.marker, [True] * len(added), dtype=pl.Boolean)
    return pl.concat([marked, pl.DataFrame(columns).lazy()], how="vertical")


# ---------------------------------------------------------------------------
# The three checks and what they say
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TableReport:
    """What the checks found for one table. `not_in_metadata` (check 1) and `missing_from_table` (check 2) are None when the recipe has no metadata.
    `added` are the ids the completion adds to this table. `after_difference` (check 3) are the ids that the table does not hold, or holds beyond the
    union, after the completion: empty when the completion did its work."""
    table: str
    kind: str
    id_column: str
    marker: str
    meaning: str
    rows: int
    distinct_ids: int
    no_id_lines: int
    no_id_line_numbers: Tuple[int, ...]
    not_in_metadata: Optional[Tuple[str, ...]]
    missing_from_table: Optional[Tuple[str, ...]]
    added: Tuple[str, ...]
    after_difference: Tuple[str, ...]


@dataclass(frozen=True)
class IdReport:
    """The report of the checks of the ids of one recipe: one `TableReport` per table that takes part, the metadata first. `completed` says whether check 3
    was made (it needs the tables after the completion)."""
    has_metadata: bool
    union_count: int
    tables: Tuple[TableReport, ...]
    completed: bool

    @property
    def check3_ok(self) -> bool:
        """True when, after the completion, every table holds exactly the union of the ids (her third check, D-0590). False means a bug of the app."""
        return all(not t.after_difference for t in self.tables)

    @property
    def differs(self) -> bool:
        """True when the ids of the tables were not equal before the completion: something was added or one line has no usable id."""
        return any(t.added or t.no_id_lines for t in self.tables)

    def as_dict(self) -> dict:
        """Plain data for the log (YAML) and the export."""
        def table(t: TableReport) -> dict:
            out = {"table": t.table, "kind": t.kind, "id_column": t.id_column, "marker": t.marker, "meaning": t.meaning, "rows": t.rows,
                   "distinct_ids": t.distinct_ids, "lines_with_no_usable_id": t.no_id_lines,
                   "ids_added": {"count": len(t.added), "ids": list(t.added)}}
            if t.no_id_lines:
                out["lines_with_no_usable_id_numbers"] = list(t.no_id_line_numbers)
                if t.no_id_lines > len(t.no_id_line_numbers):
                    out["lines_with_no_usable_id_numbers_shown"] = len(t.no_id_line_numbers)
            if t.not_in_metadata is not None:
                out["check_1_ids_not_in_the_metadata"] = {"count": len(t.not_in_metadata), "ids": list(t.not_in_metadata)}
            if t.missing_from_table is not None:
                out["check_2_metadata_ids_not_in_this_table"] = {"count": len(t.missing_from_table), "ids": list(t.missing_from_table)}
            if self.completed:
                out["check_3_difference_after_the_completion"] = {"count": len(t.after_difference), "ids": list(t.after_difference)}
            return out
        return {"has_metadata": self.has_metadata, "ids_in_the_union": self.union_count,
                "check_3": ("not made" if not self.completed else "passed" if self.check3_ok else "FAILED: a bug of the app"),
                "tables": [table(t) for t in self.tables]}


def build_report(parts: Sequence[Participant], read: Sequence[TableIds], completed: Optional[Sequence[TableIds]] = None) -> IdReport:
    """The report of the three checks. `read` are the tables as read (before the completion); `completed` are the same tables after it, or None when check 3
    is not asked for. Check 1 and check 2 compare each data table with the metadata, when the recipe has one."""
    by_table = {t.table: t for t in read}
    after = {t.table: t for t in completed} if completed is not None else {}
    union = union_of(read)
    metadata = by_table.get(METADATA_ID)
    meta_ids = set(metadata.ids) if metadata is not None else None
    reports = []
    for p in parts:
        t = by_table[p.table]
        own = set(t.ids)
        not_in_metadata = missing_from_table = None
        if meta_ids is not None and p.kind == DATA:
            not_in_metadata = tuple(i for i in t.ids if i not in meta_ids)
            missing_from_table = tuple(sorted(meta_ids - own))
        difference: Tuple[str, ...] = ()
        if completed is not None:
            now = set(after[p.table].ids)
            difference = tuple(sorted(now.symmetric_difference(union)))
        reports.append(TableReport(
            p.table, p.kind, p.id_column, p.marker, p.meaning, t.rows, len(t.ids), len(t.no_id_lines), t.no_id_lines[:LISTED_NO_ID_LINES],
            not_in_metadata, missing_from_table, tuple(i for i in union if i not in own), difference))
    return IdReport(metadata is not None, len(union), tuple(reports), completed is not None)


def _shown(ids: Sequence[str], limit: int = 12) -> str:
    """Up to `limit` ids, then how many more."""
    head = ", ".join(ids[:limit])
    return head + (f", and {len(ids) - limit} more" if len(ids) > limit else "")


def report_lines(report: IdReport) -> List[str]:
    """The report in plain words, one line per finding, nothing when the ids are equal everywhere. PROVISIONAL wording (the owner reads it).

    A finding is a warning: the recipe is never refused for it (D-0581). The meaning of a line added to a table is the one the recipe states."""
    lines: List[str] = []
    for t in report.tables:
        if t.no_id_lines:
            lines.append(f"In {t.table}: {t.no_id_lines} line(s) have no usable id (line numbers {_shown([str(n) for n in t.no_id_line_numbers])}); they stay as they are "
                         "and are not completed.")
        if t.not_in_metadata:
            lines.append(f"In {t.table}: {len(t.not_in_metadata)} id(s) are not in the metadata: {_shown(t.not_in_metadata)}.")
        if t.missing_from_table:
            lines.append(f"In {t.table}: {len(t.missing_from_table)} id(s) of the metadata are not in this table: {_shown(t.missing_from_table)}.")
        if t.added:
            lines.append(f"In {t.table}: {len(t.added)} line(s) were added for ids it lacks ({_shown(t.added)}), marked in the column {t.marker}; "
                         f"the recipe says they mean: {t.meaning}.")
        if t.after_difference:
            lines.append(f"BUG OF THE APP: after the completion {t.table} does not hold the same ids as the other tables ({_shown(t.after_difference)}). Report it.")
    return lines
