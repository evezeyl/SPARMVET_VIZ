"""
Automated tests for join_designer.py (BP-JOINT-1, ADR-082 Q5).

Verifies:
- compute_key_match: full / partial / no overlap, composite keys, type verdict as the build,
  arity mismatch, empty inputs.
- build_join_step: symmetric single, asymmetric single, composite symmetric/asymmetric,
  comment + how passthrough, the YAML "on" key contract, validation errors.
- parse_join_step: round-trips with build_join_step; the YAML boolean-trap (True key);
  how default fallback.

Run from project root:
    PYTHONPATH=. .venv/bin/python -m pytest libs/blueprint_arch/tests/test_join_designer.py -v
"""
import pytest

from blueprint_arch.join_designer import (
    JOIN_HOW_OPTIONS,
    check_join_keys,
    compute_key_match,
    build_join_step,
    parse_join_step,
)


# ── compute_key_match ────────────────────────────────────────────────────────

class TestComputeKeyMatch:
    def test_full_overlap_single_key(self):
        left = [("S1",), ("S2",), ("S3",)]
        right = [("S1",), ("S2",), ("S3",)]
        r = compute_key_match(left, right)
        assert r["left_total"] == 3
        assert r["right_total"] == 3
        assert r["matched"] == 3
        assert r["left_only"] == 0
        assert r["right_only"] == 0
        assert r["match_rate"] == 1.0
        assert r["left_only_sample"] == []

    def test_partial_overlap(self):
        left = [("S1",), ("S2",), ("S3",), ("S4",), ("S5",)]
        right = [("S1",), ("S2",), ("S3",), ("X9",)]
        r = compute_key_match(left, right)
        assert r["matched"] == 3
        assert r["left_only"] == 2          # S4, S5
        assert r["right_only"] == 1         # X9
        assert r["match_rate"] == pytest.approx(3 / 5)
        assert ("S4",) in r["left_only_sample"]
        assert ("X9",) in r["right_only_sample"]

    def test_no_overlap(self):
        r = compute_key_match([("A",), ("B",)], [("C",), ("D",)])
        assert r["matched"] == 0
        assert r["match_rate"] == 0.0
        assert r["left_only"] == 2
        assert r["right_only"] == 2

    def test_composite_keys(self):
        left = [("S1", "blaTEM"), ("S1", "mecA"), ("S2", "blaTEM")]
        right = [("S1", "blaTEM"), ("S2", "blaTEM"), ("S9", "vanA")]
        r = compute_key_match(left, right)
        assert r["matched"] == 2
        assert r["left_only"] == 1
        assert r["right_only"] == 1

    def test_the_keys_are_compared_as_they_are_no_cast(self):
        # the number 2022 and the text "2022" are different keys: nothing is cast to text (JOIN-PREVIEW-STRICT-1)
        r = compute_key_match([(2022,), (2023,)], [("2022",), ("2023",)])
        assert r["matched"] == 0

    def test_mixed_types_in_the_samples_do_not_crash(self):
        r = compute_key_match([(1,), ("a",)], [(2,)])
        assert r["left_only"] == 2

    def test_empty_left(self):
        r = compute_key_match([], [("S1",)])
        assert r["left_total"] == 0
        assert r["match_rate"] == 0.0
        assert r["matched"] == 0

    def test_dedup_rows(self):
        r = compute_key_match([("S1",), ("S1",), ("S2",)], [("S1",)])
        assert r["left_total"] == 2
        assert r["matched"] == 1


# ── check_join_keys: the same verdicts as the build (libs/transformer/tests/test_join_key_types.py) ─────

L = lambda **cols: dict(cols)  # noqa: E731


class TestCheckJoinKeys:
    @pytest.mark.parametrize("dtype", ["Categorical", "String", "Int64"])
    def test_equal_types_are_joinable(self, dtype):
        r = check_join_keys(L(sample_id=dtype), L(sample_id=dtype), ["sample_id"], ["sample_id"])
        assert r["ok"] is True and r["kind"] is None

    @pytest.mark.parametrize("left,right", [("String", "Categorical"), ("Categorical", "String")])
    def test_string_against_categorical_is_not_joinable_both_ways(self, left, right):
        r = check_join_keys(L(sample_id=left), L(sample_id=right), ["sample_id"], ["sample_id"], right_id="R")
        assert r["ok"] is False and r["kind"] == "type"
        assert f"{left} in the left table and {right} in 'R'" in r["problem"]

    def test_the_fix_says_a_step_before_the_join_changes_only_the_left_table(self):
        r = check_join_keys(L(sample_id="String"), L(sample_id="Categorical"), ["sample_id"], ["sample_id"], right_id="R")
        for part in ("only the left table", "'R'", "its own input_fields", "its own wrangling", "input_fields of both tables"):
            assert part in r["fix"]

    def test_number_against_text_is_not_joinable(self):
        r = check_join_keys(L(sample_id="Int64"), L(sample_id="String"), ["sample_id"], ["sample_id"], right_id="R")
        assert r["kind"] == "type" and "Int64 in the left table and String" in r["problem"]

    def test_left_on_right_on_of_different_types_name_both_columns(self):
        r = check_join_keys(L(VF_gene="String"), L(Gene_name="Categorical"), ["VF_gene"], ["Gene_name"])
        assert r["kind"] == "type" and "'VF_gene' (left) and 'Gene_name' (right)" in r["problem"]

    def test_with_two_keys_only_the_column_that_differs_is_named(self):
        r = check_join_keys(L(sample_id="String", gene="Categorical"), L(sample_id="String", gene="String"),
                            ["sample_id", "gene"], ["sample_id", "gene"])
        assert r["kind"] == "type" and "'gene'" in r["problem"] and "'sample_id'" not in r["problem"]
        assert [p["same"] for p in r["type_pairs"]] == [True, False]

    def test_several_equal_keys_are_joinable(self):
        r = check_join_keys(L(a="String", b="Int64"), L(a="String", b="Int64"), ["a", "b"], ["a", "b"])
        assert r["ok"] is True

    def test_missing_on_the_left_only_says_which_side(self):
        r = check_join_keys(L(sample_id="String"), L(other="String", year="Int64"), ["no_such"], ["other"], right_id="R")
        assert r["kind"] == "missing" and "missing in the left table" in r["problem"] and "missing in 'R'" not in r["problem"]
        assert "sample_id" in r["problem"]

    def test_missing_on_the_right_only_says_which_side(self):
        r = check_join_keys(L(sample_id="String"), L(sample_id="String", year="Int64"), ["sample_id"], ["no_such"], right_id="R")
        assert r["kind"] == "missing" and "missing in 'R'" in r["problem"] and "missing in the left table" not in r["problem"]
        assert "year" in r["problem"]

    def test_missing_on_both_sides_names_both(self):
        r = check_join_keys(L(a="String"), L(a="String"), ["x"], ["x"], right_id="R")
        assert "missing in the left table" in r["problem"] and "missing in 'R'" in r["problem"]

    def test_unequal_key_lists_are_not_joinable(self):
        r = check_join_keys(L(a="String", b="String"), L(a="String"), ["a", "b"], ["a"])
        assert r["kind"] == "length" and "2" in r["problem"] and "1" in r["problem"]

    def test_no_key_at_all_is_not_joinable(self):
        assert check_join_keys(L(a="String"), L(a="String"), [], [])["ok"] is False

    def test_length_is_checked_before_missing_columns(self):
        # same order as the build: lengths, then missing columns, then types
        assert check_join_keys(L(a="String"), L(a="String"), ["x", "a"], ["a"])["kind"] == "length"
        assert check_join_keys(L(a="String"), L(a="Int64"), ["x"], ["a"])["kind"] == "missing"


# ── build_join_step ──────────────────────────────────────────────────────────

class TestBuildJoinStep:
    def test_symmetric_single_key_emits_on(self):
        step = build_join_step("metadata", ["sample_id"], ["sample_id"], how="inner")
        assert step == {
            "action": "polars_join",
            "right_ingredient": "metadata",
            "on": ["sample_id"],
            "how": "inner",
            "maintain_order": "left_right",
        }

    def test_a_right_join_keeps_the_order_of_the_right_table(self):
        assert build_join_step("metadata", ["sample_id"], ["sample_id"], how="right")["maintain_order"] == "right_left"

    def test_asymmetric_single_key_emits_left_right_on(self):
        step = build_join_step("metadata", ["isolate_id"], ["sample_id"], how="left")
        assert step["left_on"] == ["isolate_id"]
        assert step["right_on"] == ["sample_id"]
        assert "on" not in step
        assert step["how"] == "left"

    def test_composite_symmetric_emits_list_on(self):
        step = build_join_step(
            "resfinder", ["sample_id", "gene_id"], ["sample_id", "gene_id"], how="inner")
        assert step["on"] == ["sample_id", "gene_id"]

    def test_composite_asymmetric(self):
        step = build_join_step(
            "resfinder", ["sid", "gid"], ["sample_id", "gene_id"], how="inner")
        assert step["left_on"] == ["sid", "gid"]
        assert step["right_on"] == ["sample_id", "gene_id"]

    def test_comment_included_when_present(self):
        step = build_join_step("metadata", ["sample_id"], ["sample_id"],
                               comment="merge sample annotations")
        assert step["comment"] == "merge sample annotations"

    def test_comment_omitted_when_empty(self):
        step = build_join_step("metadata", ["sample_id"], ["sample_id"], comment="")
        assert "comment" not in step

    def test_on_key_is_string_not_bool(self):
        # Guards the YAML boolean trap at the source: the dict key must be the str "on".
        step = build_join_step("metadata", ["sample_id"], ["sample_id"])
        assert "on" in step
        assert True not in step

    def test_empty_keys_raises(self):
        with pytest.raises(ValueError):
            build_join_step("metadata", [], [], how="inner")

    def test_arity_mismatch_raises(self):
        with pytest.raises(ValueError):
            build_join_step("metadata", ["a", "b"], ["a"], how="inner")


# ── parse_join_step ──────────────────────────────────────────────────────────

class TestParseJoinStep:
    def test_round_trip_symmetric_single(self):
        step = build_join_step("metadata", ["sample_id"], ["sample_id"], how="inner",
                               comment="why")
        p = parse_join_step(step)
        assert p["right_ingredient"] == "metadata"
        assert p["left_keys"] == ["sample_id"]
        assert p["right_keys"] == ["sample_id"]
        assert p["how"] == "inner"
        assert p["comment"] == "why"

    def test_round_trip_asymmetric(self):
        step = build_join_step("metadata", ["isolate_id"], ["sample_id"], how="left")
        p = parse_join_step(step)
        assert p["left_keys"] == ["isolate_id"]
        assert p["right_keys"] == ["sample_id"]

    def test_round_trip_composite(self):
        step = build_join_step("rf", ["s", "g"], ["s", "g"], how="inner")
        p = parse_join_step(step)
        assert p["left_keys"] == ["s", "g"]
        assert p["right_keys"] == ["s", "g"]

    def test_round_trip_is_idempotent(self):
        step = build_join_step("rf", ["sid", "gid"], ["sample_id", "gene_id"], how="inner")
        p = parse_join_step(step)
        rebuilt = build_join_step(
            p["right_ingredient"], p["left_keys"], p["right_keys"], how=p["how"])
        assert rebuilt == step

    def test_yaml_boolean_trap_true_key(self):
        # Simulates an unquoted `on: sample_id` reloaded by PyYAML as {True: 'sample_id'}.
        step = {"action": "polars_join", "right_ingredient": "metadata", True: "sample_id",
                "how": "inner"}
        p = parse_join_step(step)
        assert p["left_keys"] == ["sample_id"]
        assert p["right_keys"] == ["sample_id"]

    def test_how_defaults_to_left_when_absent(self):
        step = {"action": "polars_join", "right_ingredient": "metadata", "on": "sample_id"}
        p = parse_join_step(step)
        assert p["how"] == "left"

    def test_non_dict_returns_empty(self):
        p = parse_join_step(None)
        assert p["left_keys"] == []
        assert p["right_ingredient"] is None


def test_join_how_options_match_action_enum():
    # Designer offers exactly the strategies the transformer join action declares.
    assert set(JOIN_HOW_OPTIONS) == {"inner", "left", "outer", "semi", "anti", "cross"}
