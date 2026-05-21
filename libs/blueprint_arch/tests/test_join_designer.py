"""
Automated tests for join_designer.py (BP-JOINT-1, ADR-082 Q5).

Verifies:
- compute_key_match: full / partial / no overlap, composite keys, dtype-family advisory,
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
    compute_key_match,
    build_join_step,
    parse_join_step,
)


# ── compute_key_match ────────────────────────────────────────────────────────

class TestComputeKeyMatch:
    def test_full_overlap_single_key(self):
        left = [("S1",), ("S2",), ("S3",)]
        right = [("S1",), ("S2",), ("S3",)]
        r = compute_key_match(left, right, ["Categorical"], ["Categorical"])
        assert r["arity_ok"] is True
        assert r["left_total"] == 3
        assert r["right_total"] == 3
        assert r["matched"] == 3
        assert r["left_only"] == 0
        assert r["right_only"] == 0
        assert r["match_rate"] == 1.0
        assert r["dtype_compatible"] is True
        assert r["left_only_sample"] == []

    def test_partial_overlap(self):
        left = [("S1",), ("S2",), ("S3",), ("S4",), ("S5",)]
        right = [("S1",), ("S2",), ("S3",), ("X9",)]
        r = compute_key_match(left, right, ["String"], ["String"])
        assert r["matched"] == 3
        assert r["left_only"] == 2          # S4, S5
        assert r["right_only"] == 1         # X9
        assert r["match_rate"] == pytest.approx(3 / 5)
        assert ("S4",) in r["left_only_sample"]
        assert ("S5",) in r["left_only_sample"]
        assert ("X9",) in r["right_only_sample"]

    def test_no_overlap(self):
        left = [("A",), ("B",)]
        right = [("C",), ("D",)]
        r = compute_key_match(left, right, ["String"], ["String"])
        assert r["matched"] == 0
        assert r["match_rate"] == 0.0
        assert r["left_only"] == 2
        assert r["right_only"] == 2

    def test_composite_keys(self):
        # (sample_id, gene_id) long-format join
        left = [("S1", "blaTEM"), ("S1", "mecA"), ("S2", "blaTEM")]
        right = [("S1", "blaTEM"), ("S2", "blaTEM"), ("S9", "vanA")]
        r = compute_key_match(left, right, ["String", "String"], ["String", "String"])
        assert r["arity_ok"] is True
        assert r["matched"] == 2            # (S1,blaTEM) and (S2,blaTEM)
        assert r["left_only"] == 1          # (S1,mecA)
        assert r["right_only"] == 1         # (S9,vanA)

    def test_dtype_family_advisory_mismatch(self):
        # Float64 vs Int64 — the classic '2022.0' vs '2022' trap; flagged incompatible.
        left = [("2022",), ("2023",)]
        right = [("2022",), ("2023",)]
        r = compute_key_match(left, right, ["Float64"], ["Int64"])
        assert r["dtype_compatible"] is False
        assert r["dtype_pairs"][0]["family_match"] is False
        # overlap still computed on the String-cast rows the caller supplied
        assert r["matched"] == 2

    def test_text_family_cross_compat(self):
        # Categorical vs String/Utf8 are the same advisory family ('text').
        left = [("S1",)]
        right = [("S1",)]
        r = compute_key_match(left, right, ["Categorical"], ["Utf8"])
        assert r["dtype_compatible"] is True

    def test_arity_mismatch(self):
        left = [("S1", "g1")]
        right = [("S1",)]
        r = compute_key_match(left, right, ["String", "String"], ["String"])
        assert r["arity_ok"] is False
        assert r["matched"] == 0

    def test_empty_left(self):
        r = compute_key_match([], [("S1",)], ["String"], ["String"])
        assert r["left_total"] == 0
        assert r["match_rate"] == 0.0
        assert r["matched"] == 0

    def test_dedup_rows(self):
        # duplicate raw rows collapse to distinct keys
        left = [("S1",), ("S1",), ("S2",)]
        right = [("S1",)]
        r = compute_key_match(left, right, ["String"], ["String"])
        assert r["left_total"] == 2
        assert r["matched"] == 1


# ── build_join_step ──────────────────────────────────────────────────────────

class TestBuildJoinStep:
    def test_symmetric_single_key_emits_on(self):
        step = build_join_step("metadata", ["sample_id"], ["sample_id"], how="inner")
        assert step == {
            "action": "join",
            "right_ingredient": "metadata",
            "on": "sample_id",
            "how": "inner",
        }

    def test_asymmetric_single_key_emits_left_right_on(self):
        step = build_join_step("metadata", ["isolate_id"], ["sample_id"], how="left")
        assert step["left_on"] == "isolate_id"
        assert step["right_on"] == "sample_id"
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
        step = {"action": "join", "right_ingredient": "metadata", True: "sample_id",
                "how": "inner"}
        p = parse_join_step(step)
        assert p["left_keys"] == ["sample_id"]
        assert p["right_keys"] == ["sample_id"]

    def test_how_defaults_to_left_when_absent(self):
        step = {"action": "join", "right_ingredient": "metadata", "on": "sample_id"}
        p = parse_join_step(step)
        assert p["how"] == "left"

    def test_non_dict_returns_empty(self):
        p = parse_join_step(None)
        assert p["left_keys"] == []
        assert p["right_ingredient"] is None


def test_join_how_options_match_action_enum():
    # Designer offers exactly the strategies the transformer join action declares.
    assert set(JOIN_HOW_OPTIONS) == {"inner", "left", "outer", "semi", "anti", "cross"}
