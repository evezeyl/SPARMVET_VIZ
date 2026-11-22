# engine: python-polars (compares two collected Polars tables: counted whole-row diff, key check and paired view)
"""The comparison of an ORIGINAL result and an AUDITED result of the same entry, both at the last stage (the owner's baseline, D-0485, D-0488, D-0489).

What the owner wants to know is "that our changes worked and what is affected" (D-0488). This module answers with facts, as plain data: three
layers, each true by itself.

Layer 1, the counts (always computed, never refuses): rows and columns before and after; the columns only in the original (dropped), only in the
audited table (added), and the common columns whose TYPE differs, named with both types; whether the two tables are equal as they stand; whether
the order of the rows that both tables hold is the same (a table with the same rows in another order is a different result: this is said apart from
a difference of content).

Layer 2, the whole-row diff with no key (on request of the caller): on the columns both tables hold with the SAME type, rows are compared as a counted
set. A row present twice in one table and once in the other gives one row "only in" the first. The two lists come in the order of their own table (the
original's rows in the original's order, the audited table's in its own): a rule that cannot fail on any column type and gives the same output for the
same inputs. A list may be cut by `limit`; the record then holds the first rows AND the total count AND a flag that it was cut, never a silent cut.

Layer 3, the paired view (only with a VERIFIED key): `key_candidates` is an ordered list of column tuples that the CALLER gives (it reads them from the
recipe; this module knows nothing of recipes). A candidate is usable only when every key column exists in both tables, has the same type in both, is not
a nested type, has no missing value and no NaN in either table (a NaN key is refused, never paired or guessed) and is unique in EACH table. The first usable candidate is used; every candidate that fails is
returned with the plain reason and a count. No usable candidate: no pairing, and layers 1 and 2 are still returned. The module never searches for a key,
never pairs by position and never pairs rows that "differ in one column" (the trials' S5 did, wrongly on a constructed case: it is not built).

How values are compared: EXACTLY (`Comparison.exact` is True; no tolerance, a change of the smallest step of a decimal number is a change; a tolerance is
not decided). A missing value equals a missing value and NaN equals NaN for this purpose (`null_equals_null`, `nan_equals_nan`); two numbers are equal as
Polars compares them. A column whose type differs between the tables is NOT compared by value (it is named in `type_changes`); columns that only one table
holds are named in `columns_only_in_original` and `columns_only_in_audited`, so that a dropped column can never read as "0 rows differ" without the drop
being stated.

Sizes: the tables are eager (the caller collects). `max_cells` is a guard: when rows times columns of either table is above it, layers 2 and 3 are NOT
computed and the record says so (`not_computed`); layer 1's counts are still returned. The default is "no limit": the caller must choose, and the
number is not decided (D-0489 asks it of the owner). The same for `limit`, the length of a list: no default is chosen for the app.

What this module cannot catch is in `CANNOT_CATCH`, in plain sentences, each shown by a test (the owner: "we just also need to be clear in the documentation of the cases it cannot catch").
The words on screen are not here (not decided): the record is facts as data; the `reason` texts of a rejected key and the sentences of `CANNOT_CATCH`
are PROVISIONAL wording.

Consumed by: libs/utils/tests/test_table_compare.py. A later slice makes `app/modules/audit_run.py`, HOME and the export read this one record.
If deleted: nothing uses it yet; the three places above would each compare two tables their own way.

# @deps
# provides: function:compare, class:Comparison, class:RowList, class:TypeChange, class:NotComputed, class:KeyRejection, class:CellChange, class:CellChanges, class:ColumnChange, class:PairedView, class:Limitation, constant:CANNOT_CATCH
# consumed_by: libs/utils/tests/test_table_compare.py
# doc: .claude/knowledge/decision_ledger.md (D-0485, D-0488, D-0489), .claude/rules/rules_runtime_environment.md (engine marks)
# @end_deps
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Sequence, Tuple, Union

import polars as pl

# Why layers 2 and 3 were not computed.
NOT_COMPUTED_SIZE = "size"
NOT_COMPUTED_NO_COLUMNS = "no_comparable_columns"
# The state of the key: used, none of the candidates is usable, no candidate was given, or layer 3 was not computed.
KEY_USED = "used"
KEY_NONE_USABLE = "none_usable"
KEY_NO_CANDIDATES = "no_candidates"
KEY_NOT_COMPUTED = "not_computed"
# Which check a candidate key failed.
CHECK_EMPTY = "empty"
CHECK_DUPLICATED_COLUMN = "duplicated_column"
CHECK_MISSING = "missing"
CHECK_TYPE_DIFFERS = "type_differs"
CHECK_NESTED = "nested_type"
CHECK_HAS_NULL = "has_null"
CHECK_NOT_UNIQUE = "not_unique"
CHECK_HAS_NAN = "has_nan"


@dataclass(frozen=True)
class TypeChange:
    """A column both tables hold whose type differs: its name and the two types as text (for example `Int64`, `Float64`)."""
    column: str
    original: str
    audited: str


@dataclass(frozen=True)
class RowList:
    """Rows as plain values. `columns` names them; `rows` holds at most `limit` rows, each a tuple of Python values (a list or a dict for a nested
    column); `total` is the true number of rows; `cut` is True when `rows` holds fewer than `total` because of the limit."""
    columns: Tuple[str, ...]
    rows: Tuple[Tuple[Any, ...], ...]
    total: int
    cut: bool


@dataclass(frozen=True)
class NotComputed:
    """Layers 2 and 3 were not computed. `reason` is NOT_COMPUTED_SIZE (`cells` is the larger of rows times columns of the two tables, above `max_cells`) or
    NOT_COMPUTED_NO_COLUMNS (no column with the same name and type in both tables)."""
    reason: str
    cells: Optional[int] = None
    max_cells: Optional[int] = None


@dataclass(frozen=True)
class KeyRejection:
    """A candidate key that failed. `check` is one of the CHECK_ constants; `table` is `original`, `audited` or `both`; `count` is a number that
    says how bad (rows with a missing key, rows that share a key value, missing columns; for `both` the larger of the two counts); `reason` is one plain
    sentence (PROVISIONAL wording)."""
    columns: Tuple[str, ...]
    check: str
    table: str
    count: Optional[int]
    reason: str


@dataclass(frozen=True)
class CellChange:
    """One value that differs between two paired rows: the key values of the row, the column, the value before (original) and after (audited)."""
    key: Tuple[Any, ...]
    column: str
    before: Any
    after: Any


@dataclass(frozen=True)
class CellChanges:
    """The changed cells, by row of the original and then by column order. `cells` holds at most `limit` of them; `total` is the true number; `cut` says
    when `cells` is shorter than `total`."""
    key_columns: Tuple[str, ...]
    cells: Tuple[CellChange, ...]
    total: int
    cut: bool


@dataclass(frozen=True)
class ColumnChange:
    """For one non-key compared column: how many of the `n_paired` rows changed in it, and, for a numeric column, the smallest and largest change
    (audited minus original). A whole-number column is computed exactly in whole numbers (never through a decimal number) and returns Python ints, so
    `2**62 -> 2**62 + 1` is 1; a decimal column returns floats. The range covers the changes where both values are present and finite. It is None when no
    change has a range, when the column is not numeric, and for the 128-bit whole-number types (the range could overflow: a missing range is better than a
    wrong one). `n_to_or_from_null` counts changed rows where either value is missing; `n_to_or_from_non_finite` counts the changed rows of a decimal column
    where either value is NaN or infinite and neither is missing (the two counts do not overlap), so `n_changed` is explained: for a numeric column
    n_changed = rows with a range + n_to_or_from_null + n_to_or_from_non_finite."""
    column: str
    n_changed: int
    n_paired: int
    smallest_change: Optional[Union[int, float]]
    largest_change: Optional[Union[int, float]]
    n_to_or_from_null: int = 0
    n_to_or_from_non_finite: int = 0


@dataclass(frozen=True)
class PairedView:
    """Layer 3 with a verified key. `removed`: the whole original rows whose key is not in the audited table (original columns); `added`: the whole audited
    rows whose key is not in the original (audited columns); `n_paired` rows have the key in both; `n_rows_changed` of them differ in at least one
    compared column; `changed_cells` lists the cells; `columns` has one entry per compared non-key column, in the original's column order."""
    key: Tuple[str, ...]
    n_paired: int
    n_rows_changed: int
    removed: RowList
    added: RowList
    changed_cells: CellChanges
    columns: Tuple[ColumnChange, ...]


@dataclass(frozen=True)
class Comparison:
    """The record of one comparison; plain data, no Polars objects.

    Layer 1 (always): `n_rows_original`, `n_rows_audited`, `n_columns_original`, `n_columns_audited`; `columns_only_in_original` (dropped),
    `columns_only_in_audited` (added); `common_columns`; `type_changes`; `compared_columns` (the common columns with the same type: the ones whose values
    are compared); `equal` (the same columns in the same order with the same types and the same rows in the same order); `column_order_same` (the columns both
    tables hold are in the same order in both). When only the column order differs, `equal` and `column_order_same` are False and nothing else
    differs. Whether a changed column order counts as a difference of the RESULT is NOT decided: the record states it and decides nothing.
    Layer 2 (None when `not_computed` is set): `row_order_same` (the rows both tables hold, in the same order in both?), `only_in_original`,
    `only_in_audited` (a RowList each, on `compared_columns`; their `total` is the number of rows only in one table).
    Layer 3: `key_status` (KEY_USED, KEY_NONE_USABLE, KEY_NO_CANDIDATES, KEY_NOT_COMPUTED), `key_used`, `key_rejections` (every failed candidate before the
    one used, or all when none is usable), `paired` (the PairedView when a key is used).
    How values were compared: `exact` (True: no tolerance), `null_equals_null`, `nan_equals_nan` (True: they match for this purpose).
    `not_computed`: why layers 2 and 3 are missing, or None."""
    n_rows_original: int
    n_rows_audited: int
    n_columns_original: int
    n_columns_audited: int
    columns_only_in_original: Tuple[str, ...]
    columns_only_in_audited: Tuple[str, ...]
    common_columns: Tuple[str, ...]
    type_changes: Tuple[TypeChange, ...]
    compared_columns: Tuple[str, ...]
    equal: bool
    column_order_same: bool
    row_order_same: Optional[bool]
    only_in_original: Optional[RowList]
    only_in_audited: Optional[RowList]
    key_status: str
    key_used: Optional[Tuple[str, ...]]
    key_rejections: Tuple[KeyRejection, ...]
    paired: Optional[PairedView]
    not_computed: Optional[NotComputed]
    exact: bool = True
    null_equals_null: bool = True
    nan_equals_nan: bool = True


@dataclass(frozen=True)
class Limitation:
    """One case the comparison cannot catch: a short code (the test `test_limit_<code>` shows it) and a plain sentence (PROVISIONAL wording)."""
    code: str
    sentence: str


CANNOT_CATCH: Tuple[Limitation, ...] = (
    Limitation("why_a_value_moved",
               "The comparison does not say why a value moved. When the count of a group goes from 19 to 18 because a sample was removed upstream, the record shows "
               "the group and the two numbers, and nothing in it shows that a sample was removed: that sample is not a row of this table."),
    Limitation("a_value_over_all_samples_moves_every_row",
               "A value computed over all samples (a z-score, a mean of all samples) changes in every row when one sample is removed, so the whole-row diff lists "
               "every row of both tables and the removed sample is one line among them."),
    Limitation("a_unique_key_may_pair_rows_that_do_not_mean_the_same",
               "A key that is verified as unique may still pair rows that do not mean the same thing, for example a unique column of computed means: the paired "
               "view then reads the change of a group as the change of one cell. Uniqueness shows that rows can be paired, not that they are the same entity."),
    Limitation("the_comparison_is_exact",
               "The comparison is exact: a change of the smallest step of a decimal number counts as a change, and no tolerance is applied."),
    Limitation("it_compares_two_tables_and_knows_nothing_of_the_steps",
               "It compares two tables and knows nothing of the steps between them: a step that removed a row and a later step that put the same row back leave no "
               "trace, and it cannot tell which audit step changed what."),
    Limitation("a_column_whose_type_changed_is_not_compared_by_value",
               "A column whose type changed (a whole number that became a decimal number, a number that became text) is named, but its values are not compared, "
               "so a value that changed inside it is not listed."),
    Limitation("zero_and_negative_zero_are_equal",
               "The comparison is exact to the value, not to the bit: 0.0 and -0.0 are equal, so a change of the sign of zero leaves no trace."),
    Limitation("a_change_to_a_non_finite_value_has_no_size",
               "A change to or from NaN or infinity is counted in its column but has no size: the smallest and largest change cover finite changes only."),
    Limitation("a_renamed_column_is_a_drop_and_an_add",
               "A renamed column is shown as a dropped column and an added column; the comparison does not link the two."),
)


def _fresh(taken: Iterable[str], base: str) -> str:
    """A column name that no table uses: `base` with underscores put before it until it is free."""
    used = set(taken)
    name = base
    while name in used:
        name = "_" + name
    return name


def _rowlist(frame: pl.DataFrame, limit: Optional[int]) -> RowList:
    total = frame.height
    shown = frame if limit is None else frame.head(limit)
    return RowList(tuple(frame.columns), tuple(shown.iter_rows()), total, limit is not None and total > limit)


def _row_diff(original: pl.DataFrame, audited: pl.DataFrame, cols: Sequence[str], limit: Optional[int]) -> Tuple[bool, RowList, RowList]:
    """Layer 2 on `cols` (not empty): the counted whole-row diff and the order check. The occurrence number of a row inside its own table makes a duplicate
    a row of its own, so a row twice in one table and once in the other leaves one row on the side that has more."""
    taken = list(original.columns) + list(audited.columns)
    pos_o, pos_a, occ = _fresh(taken, "__cmp_pos_o"), _fresh(taken, "__cmp_pos_a"), _fresh(taken, "__cmp_occ")
    cols = list(cols)
    left = original.select(cols).with_row_index(pos_o).with_columns(pl.int_range(pl.len()).over(cols).alias(occ))
    right = audited.select(cols).with_row_index(pos_a).with_columns(pl.int_range(pl.len()).over(cols).alias(occ))
    on = cols + [occ]
    only_o = left.join(right.select(on), on=on, how="anti", nulls_equal=True).sort(pos_o).select(cols)
    only_a = right.join(left.select(on), on=on, how="anti", nulls_equal=True).sort(pos_a).select(cols)
    matched = left.join(right.select(on + [pos_a]), on=on, how="inner", nulls_equal=True).sort(pos_o)
    return bool(matched[pos_a].is_sorted()), _rowlist(only_o, limit), _rowlist(only_a, limit)


def _key_problem(original: pl.DataFrame, audited: pl.DataFrame, key: Tuple[str, ...]) -> Optional[KeyRejection]:
    """None when the candidate passes every check, else the first check it fails (the order: empty, missing, type, nested, missing values, unique)."""
    if not key:
        return KeyRejection(key, CHECK_EMPTY, "both", None, "The candidate names no column.")
    if len(set(key)) != len(key):
        repeated = sorted({c for c in key if key.count(c) > 1})
        return KeyRejection(key, CHECK_DUPLICATED_COLUMN, "both", len(repeated), f"The candidate names the column(s) {repeated} more than once.")
    missing_o = [c for c in key if c not in original.columns]
    missing_a = [c for c in key if c not in audited.columns]
    if missing_o or missing_a:
        table = "both" if missing_o and missing_a else ("original" if missing_o else "audited")
        names = sorted(set(missing_o) | set(missing_a))
        return KeyRejection(key, CHECK_MISSING, table, len(names), f"The key column(s) {names} are not in the {table} table.")
    for c in key:
        if original.schema[c] != audited.schema[c]:
            return KeyRejection(key, CHECK_TYPE_DIFFERS, "both", 1, f"The key column {c!r} is {original.schema[c]} in the original and {audited.schema[c]} in the audited table.")
        if original.schema[c].is_nested():
            return KeyRejection(key, CHECK_NESTED, "both", 1, f"The key column {c!r} holds lists or groups of values ({original.schema[c]}) and cannot identify a row.")
    floats = [c for c in key if original.schema[c].is_float()]
    nan_rows = lambda df: int(df.select(pl.any_horizontal([pl.col(c).is_nan() for c in floats]).sum()).item()) if floats else 0
    # NaN is a value that equals itself here, so a NaN key passes the null and unique checks, but a lone NaN row pairs with nothing in the joins and a real
    # change would be hidden: a key with NaN is refused, never guessed (D-0050). Pairing NaN with NaN is the owner's choice and is not built.
    for check, text, count_of in (
        (CHECK_HAS_NULL, "rows have a missing value in the key", lambda df: int(df.select(pl.any_horizontal(pl.col(list(key)).is_null()).sum()).item())),
        (CHECK_NOT_UNIQUE, "rows share a key value with another row", lambda df: int(df.select(list(key)).is_duplicated().sum())),
        (CHECK_HAS_NAN, "rows have NaN (not a number) in the key", nan_rows),
    ):
        n_o, n_a = count_of(original), count_of(audited)
        if n_o or n_a:
            table = "both" if n_o and n_a else ("original" if n_o else "audited")
            count = max(n_o, n_a)
            where = {"both": "In both tables", "original": "In the original table", "audited": "In the audited table"}[table]
            return KeyRejection(key, check, table, count, f"{where}, {count} {text}.")
    return None


def _paired_view(original: pl.DataFrame, audited: pl.DataFrame, key: Tuple[str, ...], compared: Sequence[str], limit: Optional[int]) -> PairedView:
    taken = list(original.columns) + list(audited.columns)
    pos = _fresh(taken, "__cmp_pos")
    suffix = "__audited"
    while any(c + suffix in taken for c in taken):
        suffix = "_" + suffix
    keycols = list(key)
    nonkey = [c for c in compared if c not in key]
    with_pos = original.with_row_index(pos)
    removed = with_pos.join(audited.select(keycols), on=keycols, how="anti", nulls_equal=True).sort(pos).drop(pos)
    added = audited.with_row_index(pos).join(original.select(keycols), on=keycols, how="anti", nulls_equal=True).sort(pos).drop(pos)
    both = with_pos.select([pos] + keycols + nonkey).join(audited.select(keycols + nonkey), on=keycols, how="inner", suffix=suffix, nulls_equal=True).sort(pos)
    differs = {c: ~pl.col(c).eq_missing(pl.col(c + suffix)) for c in nonkey}

    n_rows_changed = int(both.select(pl.any_horizontal(list(differs.values())).sum()).item()) if nonkey and both.height else 0
    columns: List[ColumnChange] = []
    cells: List[Tuple[int, int, CellChange]] = []
    total_cells = 0
    for index, c in enumerate(nonkey):
        changed = both.filter(differs[c])
        n_changed = changed.height
        total_cells += n_changed
        smallest = largest = None
        n_null = n_nonfinite = 0
        if n_changed:
            dtype = original.schema[c]
            old, new = pl.col(c), pl.col(c + suffix)
            either_null = old.is_null() | new.is_null()
            n_null = int(changed.select(either_null.sum()).item())
            if dtype.is_float():
                n_nonfinite = int(changed.select((~either_null & (~old.is_finite() | ~new.is_finite())).sum()).item())
                sized = changed.filter(~either_null & old.is_finite() & new.is_finite())
                if sized.height:
                    smallest, largest = sized.select((new - old).min().alias("lo"), (new - old).max().alias("hi")).row(0)
            elif dtype.is_integer() and dtype not in (pl.Int128, pl.UInt128):
                # in a wider whole-number type, so that no change wraps or loses a digit: Int128 holds the difference of any two 64-bit values
                sized = changed.filter(~either_null)
                if sized.height:
                    diff = new.cast(pl.Int128) - old.cast(pl.Int128)
                    smallest, largest = sized.select(diff.min().alias("lo"), diff.max().alias("hi")).row(0)
            elif dtype.is_numeric() and dtype not in (pl.Int128, pl.UInt128):
                sized = changed.filter(~either_null)                  # Decimal: the difference in the column's own type
                if sized.height:
                    smallest, largest = sized.select((new - old).min().alias("lo"), (new - old).max().alias("hi")).row(0)
        columns.append(ColumnChange(c, n_changed, both.height, smallest, largest, n_null, n_nonfinite))
        shown = changed if limit is None else changed.head(limit)
        for row in shown.select([pos] + keycols + [c, c + suffix]).iter_rows():
            cells.append((row[0], index, CellChange(tuple(row[1:1 + len(keycols)]), c, row[-2], row[-1])))
    cells.sort(key=lambda item: (item[0], item[1]))
    kept = cells if limit is None else cells[:limit]
    changes = CellChanges(key, tuple(item[2] for item in kept), total_cells, limit is not None and total_cells > limit)
    return PairedView(key, both.height, n_rows_changed, _rowlist(removed, limit), _rowlist(added, limit), changes, tuple(columns))


def compare(original: pl.DataFrame, audited: pl.DataFrame, key_candidates: Sequence[Sequence[str]] = (), *,
            limit: Optional[int] = None, max_cells: Optional[int] = None) -> Comparison:
    """Compare the ORIGINAL result with the AUDITED result of the same entry, both at the last stage (see the module text for the three layers).

    `key_candidates`: ordered column tuples, verified here on the data; none is ever invented. `limit`: the most rows or cells a list holds (None: all; the
    app has not chosen a number). `max_cells`: rows times columns of either table above which layers 2 and 3 are not computed (None: no guard; not decided).
    ValueError for a negative `limit` or `max_cells`."""
    if limit is not None and limit < 0:
        raise ValueError(f"limit must not be negative, got {limit}")
    if max_cells is not None and max_cells < 0:
        raise ValueError(f"max_cells must not be negative, got {max_cells}")
    o_cols, a_cols = list(original.columns), list(audited.columns)
    only_o_cols = tuple(c for c in o_cols if c not in a_cols)
    only_a_cols = tuple(c for c in a_cols if c not in o_cols)
    common = tuple(c for c in o_cols if c in a_cols)
    type_changes = tuple(TypeChange(c, str(original.schema[c]), str(audited.schema[c])) for c in common if original.schema[c] != audited.schema[c])
    compared = tuple(c for c in common if original.schema[c] == audited.schema[c])
    same_shape_of_columns = o_cols == a_cols and not type_changes
    column_order_same = common == tuple(c for c in a_cols if c in o_cols)

    cells = max(original.height * original.width, audited.height * audited.width)
    not_computed: Optional[NotComputed] = None
    if not compared:
        not_computed = NotComputed(NOT_COMPUTED_NO_COLUMNS)
    elif max_cells is not None and cells > max_cells:
        not_computed = NotComputed(NOT_COMPUTED_SIZE, cells, max_cells)

    row_order_same: Optional[bool] = None
    only_in_original: Optional[RowList] = None
    only_in_audited: Optional[RowList] = None
    key_status = KEY_NOT_COMPUTED
    key_used: Optional[Tuple[str, ...]] = None
    rejections: List[KeyRejection] = []
    paired: Optional[PairedView] = None
    if not_computed is None:
        row_order_same, only_in_original, only_in_audited = _row_diff(original, audited, compared, limit)
        candidates = [tuple(c) for c in key_candidates]
        key_status = KEY_NO_CANDIDATES if not candidates else KEY_NONE_USABLE
        for candidate in candidates:
            problem = _key_problem(original, audited, candidate)
            if problem is not None:
                rejections.append(problem)
                continue
            key_status, key_used = KEY_USED, candidate
            paired = _paired_view(original, audited, candidate, compared, limit)
            break
        equal = same_shape_of_columns and row_order_same and only_in_original.total == 0 and only_in_audited.total == 0
    else:
        equal = same_shape_of_columns and original.equals(audited)         # not computed: the cheap whole-table test is the only one left

    return Comparison(
        n_rows_original=original.height, n_rows_audited=audited.height, n_columns_original=original.width, n_columns_audited=audited.width,
        columns_only_in_original=only_o_cols, columns_only_in_audited=only_a_cols, common_columns=common, type_changes=type_changes,
        compared_columns=compared, equal=bool(equal), column_order_same=column_order_same, row_order_same=row_order_same, only_in_original=only_in_original, only_in_audited=only_in_audited,
        key_status=key_status, key_used=key_used, key_rejections=tuple(rejections), paired=paired, not_computed=not_computed)
