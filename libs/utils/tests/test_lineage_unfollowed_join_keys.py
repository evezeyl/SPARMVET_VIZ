"""The key columns of a join the app cannot YET follow are linked by an uncertain link, so no table is silently absent (D-0460, D-0454, D-0452, D-0486).

The gap this file closes (review of the branch `task/lineage-unfollowed-join-red`): behind an anti, right, full or self-join the walk linked the first table's key
to the joined table and nothing else, so the key column of the OTHER table was not linked to the first table's key at all. A sample could stay in a table and no
line told the user: a walk from `T1:A sample_id` listed no line for `T1:B`, and "remove from all the data" with the key declared only at one of the two tables put
the other table in `not_reached` with the code `same_name_not_linked`, which is not in `may_stay`.

The rule (D-0460: a place the app cannot trace is shown, red, not tickable; never silently absent): for a join NOT YET followed, the first table's key and the
second table's key (by `on`, or by `left_on` and `right_on`) are linked by an UNCERTAIN link that carries the reason `join_not_yet_followed` and the join's facts. The
other table is then a red line in the walk, in either direction, and a table in `may_stay` with the full sentence (YET in capitals) in "remove from all the data".

Also here: the sentence is true for every kind (anti, right, full, cross, an unknown word, a self-join); the lists of kinds are ONE partition (every kind the engine's
join action accepts is followed or not yet followed, never both, never neither); and "remove from all the data" tells the user about EVERY table that holds a column of
the key's name (written, may stay, or a listed reason), also a table that shares only the name (`same_name_not_linked`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_lineage_unfollowed_join_keys.py -q
"""
import re
from pathlib import Path

import lineage_fixtures as F
import lineage_oracle as O
import pytest
from lineage_support import run

from utils import action_names, audit_copy, lineage_sentences, remove_from_all as rfa, step_effects as fx
from utils.declared_plans import declared_plan_book
from utils.lineage_records import JOIN_NOT_YET_FOLLOWED, Reason
from utils.lineage_walk import LineageIndex
from utils.recipe_graph import build_graph
from utils.recipe_loader import load_recipe

NOT_YET = ["anti", "right", "full"]
ROOT = Path(__file__).resolve().parents[3]
AUD = "1a2b3c4d"


def line(walk, place):
    return next((x for x in walk.lines if x.place == place), None)


def keyed(how, declared="AB", other_name="sample_id", **extra):
    """A(sample_id, country) and B(<other_name>, lab); J = A with B (kind `how`); a plot P reads J. The entity key is declared where `declared` says ("A", "B" or "AB").
    `other_name` is the name of B's key: the same as A's, or another (then the join writes left_on and right_on)."""
    on = "sample_id" if other_name == "sample_id" else ("sample_id", other_name)
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"] if "A" in declared else []),
                       "B": F.schema([other_name, "lab"], keys=[other_name] if "B" in declared else [])},
                      {"J": F.join(["A", "B"], [F.join_step("B", on=on, how=how, **extra)])}, {"P": F.plot("J")})
    tables = {"A": F.table(sample_id=["S1", "S2", "S3"], country=["NO", "SE", "NO"]), "B": F.table(**{other_name: ["S1", "S2", "S4"], "lab": ["X", "Y", "Z"]})}
    return recipe, tables


def described(recipe, tables, column="sample_id"):
    return rfa.describe(recipe, column, plans=O.replay(recipe, tables).plans)


# ----------------------------------------------------------------------------------------------------------------------------- the walk: both tables are listed

@pytest.mark.parametrize("other_name", ["sample_id", "isolate"])
@pytest.mark.parametrize("how", NOT_YET)
def test_a_walk_from_the_key_of_one_table_lists_the_other_table_as_red_with_the_join_as_the_reason(how, other_name):
    recipe, tables = keyed(how, other_name=other_name)
    from_a = run(recipe, tables, "T1:A", "sample_id")
    other = line(from_a, "T1:B")
    assert other is not None, "T1:B is silently absent from the walk"                    # the reviewer's failing case: no line at all
    assert other.state == "grey" and other.reason.code == JOIN_NOT_YET_FOLLOWED
    assert (other.reason.get("kind"), other.reason.get("node"), other.reason.get("step"), other.reason.get("right")) == (how, "T1:J", 1, "B")
    from_b = run(recipe, tables, "T1:B", other_name)
    first = line(from_b, "T1:A")
    assert first is not None and first.state == "grey" and first.reason.code == JOIN_NOT_YET_FOLLOWED
    assert line(from_b, "T1:B").state == "tick" and line(from_a, "T1:A").state == "tick"


@pytest.mark.parametrize("how", ["left", "inner", "semi"])
def test_the_key_of_the_second_table_stays_a_certain_line_behind_a_followed_join(how):
    recipe, tables = keyed(how)
    assert line(run(recipe, tables, "T1:A", "sample_id"), "T1:B").state == "tick"


@pytest.mark.parametrize("how", NOT_YET)
def test_a_plain_column_of_the_other_table_is_not_linked_to_the_key(how):
    recipe, tables = keyed(how)
    walk = run(recipe, tables, "T1:A", "country")
    assert line(walk, "T1:B") is None                                                     # B holds no `country`: nothing to say about it


# ----------------------------------------------------------------------------------------------------------------------------- remove from all the data

@pytest.mark.parametrize("other_name", ["sample_id", "isolate"])
@pytest.mark.parametrize("declared", ["A", "B", "AB"])
@pytest.mark.parametrize("how", NOT_YET)
def test_the_table_the_key_reaches_only_through_such_a_join_is_written_nowhere_and_listed_with_the_sentence(how, declared, other_name):
    recipe, tables = keyed(how, declared, other_name)
    option = described(recipe, tables)
    assert option.offered
    assert [p.table for p in option.places] == [t for t in "AB" if t in declared]       # written only where the key is declared (each holds it at its own start)
    stays = {m.table: m for m in option.may_stay}
    assert set(stays) == {"J"} | {t for t in "AB" if t not in declared}                  # every other table is listed, never silently absent
    for table, item in stays.items():
        if (how, other_name, table) == ("full", "isolate", "J"):                         # a full join on two names keeps BOTH key columns: the table says so (several columns), still listed
            assert not item.written and item.code == rfa.SEVERAL_COLUMNS
            assert rfa.may_stay_sentence(item).startswith("In the table 'J'")
            continue
        assert not item.written and item.code == rfa.UNCERTAIN_LINK and item.reason.code == JOIN_NOT_YET_FOLLOWED, table
        said = rfa.may_stay_sentence(item)
        assert said.startswith(f"In the table {table!r}") and said.count("YET") == 1 and how in said and said.rstrip().endswith("The selection may stay there."), said
    assert [n.table for n in option.not_reached if n.code == rfa.SAME_NAME_NOT_LINKED] == []   # no longer the silent code


@pytest.mark.parametrize("declared", ["A", "B"])
@pytest.mark.parametrize("how", NOT_YET)
def test_nothing_is_written_at_a_table_reached_only_through_such_a_link(how, declared):
    recipe, tables = keyed(how, declared)
    plans = O.replay(recipe, tables).plans
    option = rfa.describe(recipe, "sample_id", plans=plans)
    audit = audit_copy.start_audit(recipe, AUD)
    applied = rfa.apply(audit, option, ["S1"], "resequenced", plans=plans)
    written = {s.place for s in audit_copy.all_audit_steps(audit.recipe)}
    assert written == {f"T1:{declared}"} and len(applied.step_ids) == 1
    other = "B" if declared == "A" else "A"
    assert {m.table for m in applied.not_written} == {other, "J"}                         # the user is told, after the apply too


def selfjoin(how, declared=True):
    recipe = F.recipe({"A": F.schema(["sample_id", "country"], keys=["sample_id"] if declared else [])}, {"J": F.join(["A", "A"], [F.join_step("A", how=how, suffix="_r")])}, {"P": F.plot("J")})
    return recipe, {"A": F.table(sample_id=["S1", "S2"], country=["NO", "SE"])}


@pytest.mark.parametrize("how", ["left", "inner", "anti", "semi"])
def test_a_self_join_lists_the_joined_table_with_the_sentence_and_writes_only_at_the_declared_table(how):
    recipe, tables = selfjoin(how)
    option = described(recipe, tables)
    assert [p.table for p in option.places] == ["A"] and [m.table for m in option.may_stay] == ["J"]
    said = rfa.may_stay_sentence(option.may_stay[0])
    assert "YET" in said and "self-join" in said


def test_a_self_join_walk_lists_the_joined_table_as_red_from_either_side():
    recipe, tables = selfjoin("left")
    walk = run(recipe, tables, "T1:A", "sample_id")
    assert line(walk, "T1:A").state == "tick" and line(walk, "T1:J").state == "grey" and line(walk, "T1:J").reason.get("self_join") is True


def test_the_key_through_a_followed_join_is_still_written_at_both_tables():
    recipe, tables = keyed("left", "A")
    option = described(recipe, tables)
    assert [p.table for p in option.places] == ["A", "B", "J"] and option.may_stay == ()


# ----------------------------------------------------------------------------------------------------------------------------- no table is silently absent

def unfollowed_fixtures():
    out = []
    for how in NOT_YET + ["semi", "left"]:
        for declared in ("A", "B", "AB"):
            out.append((f"{how}_declared_{declared}", *keyed(how, declared)))
    for how in NOT_YET:
        out.append((f"{how}_other_name", *keyed(how, "A", "isolate")))
    out.append(("self_join_left", *selfjoin("left")))
    recipe, tables = keyed("anti", "A")                                                 # a third table that shares only the NAME of the key, and one that a plain join links
    recipe["data_schemas"]["N"] = F.schema(["sample_id", "note"])
    tables["N"] = F.table(sample_id=["S1"], note=["n"])
    out.append(("namesake_table", recipe, tables))
    return out


def fixture_cases():
    return unfollowed_fixtures() + [(name, recipe, tables) for name, recipe, tables in F.followed()]


def silent_tables(recipe, plans):
    """The tables of the recipe that hold a column with the name of the key at the end of their tier 1 and that "remove from all the data" says nothing about. [] is the rule."""
    graph = build_graph(recipe)
    index = LineageIndex(graph, plans)
    declared = {name for t in graph.collections() if graph.node(f"T1:{t}").collection_kind == "schema" for name in graph.declared_entity_keys(t)}
    missing = []
    for key in sorted(declared):
        option = rfa.describe(recipe, key, plans=plans)
        if not option.offered:
            continue
        written = {p.table for p in option.places}
        listed = {n.table: n for n in option.not_reached}
        assert not written & set(listed), "a table is both written and 'not reached'"
        for table in graph.collections():
            plan = index.plan_end(f"T1:{table}")
            if not hasattr(plan, "names") or not any(plan.has(name) for name in option.key_names):
                continue
            if table in written:
                continue
            item = listed.get(table)
            if item is None:
                missing.append((key, table))
                continue
            said = rfa.not_reached_sentence(item)
            assert said.startswith(f"In the table {table!r}") and said.strip().endswith("."), said
            if item.code in rfa.UNSURE_CODES:
                assert table in {m.table for m in option.may_stay}, (key, table, item.code)
    return missing


@pytest.mark.parametrize("name,recipe,tables", fixture_cases(), ids=lambda v: v if isinstance(v, str) else "")
def test_no_table_that_holds_the_key_name_is_silently_absent_on_the_fixtures(name, recipe, tables):
    assert silent_tables(recipe, O.replay(recipe, tables).plans) == []


def shipped_recipes():
    for base in ("config/data_analysis_recipes", "assets/gallery_data"):
        for path in sorted((ROOT / base).rglob("*.yaml")):
            raw, _ = load_recipe(path)
            if isinstance(raw, dict) and isinstance(raw.get("data_schemas"), dict):
                yield path, raw


@pytest.mark.parametrize("path,raw", list(shipped_recipes()), ids=lambda v: v.parent.name + "/" + v.name if isinstance(v, Path) else "")
def test_no_table_that_holds_the_key_name_is_silently_absent_on_the_shipped_recipes(path, raw):
    assert silent_tables(raw, declared_plan_book(build_graph(raw))) == []


def test_the_scan_finds_the_shipped_recipes():
    assert len(list(shipped_recipes())) >= 20


def test_a_table_that_shares_only_the_name_is_listed_with_a_plain_sentence_not_written():
    recipe, tables = keyed("left", "A")
    recipe["data_schemas"]["N"] = F.schema(["sample_id", "note"])
    tables["N"] = F.table(sample_id=["S1"], note=["n"])
    option = described(recipe, tables)
    same = [n for n in option.not_reached if n.table == "N"]
    assert [n.code for n in same] == [rfa.SAME_NAME_NOT_LINKED] and "N" not in {p.table for p in option.places}
    said = rfa.not_reached_sentence(same[0])
    assert said.startswith("In the table 'N'") and "sample_id" in said and "no declaration and no join" in said
    assert "PROVISIONAL" in Path(rfa.__file__).read_text()


def test_every_code_of_the_closed_list_has_a_sentence():
    for code in rfa.NOT_REACHED_CODES:
        item = rfa.NotReached("T", "T1:T", code, Reason(code, (("names", ("sample_id",)),)))
        said = rfa.not_reached_sentence(item)
        assert said.startswith("In the table 'T'") and said.endswith("."), (code, said)


# ----------------------------------------------------------------------------------------------------------------------------- the sentence is true for every kind

def reason_of(how, self_join=False, right="B"):
    return Reason(JOIN_NOT_YET_FOLLOWED, (("node", "T1:J"), ("step", 2), ("action", action_names.JOIN), ("kind", how), ("how", how), ("right", right), ("self_join", self_join)))


def listed_kinds(sentence):
    return [part.strip() for part in re.split(r",| or ", re.search(r"this kind of join \(([^)]*)\)", sentence).group(1)) if part.strip()]


@pytest.mark.parametrize("how", ["anti", "right", "full", "cross", "banana"])
def test_the_sentence_names_the_kind_at_hand_in_its_list_and_says_YET_once(how):
    sentence = lineage_sentences.join_not_yet_followed_sentence(reason_of(how))
    assert how in listed_kinds(sentence), sentence                                       # the list the sentence gives holds the kind it then names
    assert sentence.count("YET") == 1 and f"the {how} join of step 2 of T1:J, which reads the table 'B'" in sentence
    assert "self-join" in listed_kinds(sentence)


def test_the_list_is_the_one_list_of_the_kinds_plus_the_self_join():
    sentence = lineage_sentences.join_not_yet_followed_sentence(reason_of("anti"))
    assert listed_kinds(sentence) == [*fx.NOT_YET_FOLLOWED_JOINS, "self-join"]            # a kind added to the list is in the sentence without a change here


def test_the_sentence_of_a_self_join_says_what_is_true_for_it():
    sentence = lineage_sentences.join_not_yet_followed_sentence(reason_of("left", self_join=True, right="A"))
    assert "self-join" in listed_kinds(sentence) and "the self-join (how: left) of step 2 of T1:J" in sentence
    assert "which reads the table" not in sentence                                        # the table is not a new table: it is one the join already holds
    assert "already holds" in sentence and "'A'" in sentence and sentence.count("YET") == 1


def test_an_unknown_kind_is_added_to_the_list_so_that_the_list_is_true():
    sentence = lineage_sentences.join_not_yet_followed_sentence(reason_of("banana"))
    assert listed_kinds(sentence) == [*fx.NOT_YET_FOLLOWED_JOINS, "self-join", "banana"]


# ----------------------------------------------------------------------------------------------------------------------------- one list, one behaviour

def engine_join_kinds():
    from app.modules.data_analysis_recipe_validator import checker_catalogs      # the registry is read by the app layer; libs/utils must not import the transformer
    return list(checker_catalogs()["actions"][action_names.JOIN]["params"]["how"]["options"])


def test_every_kind_the_engines_join_accepts_is_in_exactly_one_of_the_two_lists():
    kinds = engine_join_kinds()
    assert {"inner", "left", "right", "full", "semi", "anti", "cross"} <= set(kinds)       # the scan reads the real list
    for kind in kinds:
        assert (kind in fx.FOLLOWED_JOINS) != (kind in fx.NOT_YET_FOLLOWED_JOINS), kind
    assert set(fx.FOLLOWED_JOINS) | set(fx.NOT_YET_FOLLOWED_JOINS) <= set(kinds)         # and the lists name no kind the engine does not have


def test_the_behaviour_follows_the_lists_for_every_kind_and_an_unknown_kind_is_not_followed():
    for kind in engine_join_kinds() + ["banana", None]:
        effect = fx.effect_of({"action": action_names.JOIN, "right_ingredient": "B", "on": "k", "how": kind})
        followed = kind in fx.FOLLOWED_JOINS
        assert (effect.kind == fx.JOIN) is followed and (fx.not_yet_followed(effect) is None) is followed, kind
