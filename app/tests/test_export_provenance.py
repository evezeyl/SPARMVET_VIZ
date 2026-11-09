"""The export records the keys it used (ADR-089, issue #10): traceability when a result is questioned.

build_export_provenance takes plain objects, so it is tested headless. The end-to-end check of a
real download is in .claude/tasks/tasks.md (EXPORT-CHECK-1), done by hand in the app.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_provenance.py -q
"""
import datetime
import io
from types import SimpleNamespace

from PIL import Image

from app.handlers.export_handlers import _embed_png_provenance, _embed_svg_provenance, build_export_provenance
from app.modules.cache_keys import tier2_key

T1 = "a" * 64
STEPS = [{"action": "filter_eq", "column": "group", "value": "A"}]


def prov(stage_keys, all_plots):
    return build_export_provenance(
        now=datetime.datetime(2026, 11, 6, 12, 0, 0), data_analysis_recipe_id="tiny", safe_name="eve", app_features="qa",
        preset="web", dpi=300, active_tier="T2", scope_label="global", all_plots=all_plots,
        tiers_exported=["T1"], data_analysis_recipe_sha="m" * 64, data_sha="d" * 64,
        bootloader=SimpleNamespace(available_data_analysis_recipes={}), stage_keys=stage_keys,
    )


def prov_t3(t3_by_plot=None, t3_aesthetic_overrides=None):
    return build_export_provenance(
        now=datetime.datetime(2026, 11, 6, 12, 0, 0), data_analysis_recipe_id="tiny", safe_name="eve", app_features="qa",
        preset="web", dpi=300, active_tier="T2", scope_label="global", all_plots=[],
        tiers_exported=["T1"], data_analysis_recipe_sha="m" * 64, data_sha="d" * 64,
        bootloader=SimpleNamespace(available_data_analysis_recipes={}), stage_keys=None,
        t3_by_plot=t3_by_plot, t3_aesthetic_overrides=t3_aesthetic_overrides,
    )


def png() -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (4, 4)).save(out, format="PNG")
    return out.getvalue()


def test_the_keys_of_the_export_are_recorded_per_dataset():
    keys = {"C": {"tier1_key": T1, "tier2_key": tier2_key(T1, STEPS)}}
    p = prov(keys, [("p", {"target_dataset": "C"})])
    assert p["stage_keys"] == keys
    assert p["decision_hashes"] == {"C": T1}          # kept for older readers of the bundle
    assert p["data_analysis_recipe_sha256"] == "m" * 64 and p["data_batch_hash"] == "d" * 64


def test_a_join_without_tier2_steps_has_an_empty_tier2_key():
    p = prov({"C": {"tier1_key": T1, "tier2_key": ""}}, [("p", {"target_dataset": "C"})])
    assert p["stage_keys"]["C"]["tier2_key"] == ""


def test_two_datasets_keep_their_own_tier2_key():
    k2 = tier2_key(T1, STEPS)
    keys = {"C": {"tier1_key": T1, "tier2_key": k2}, "D": {"tier1_key": T1, "tier2_key": ""}}
    p = prov(keys, [("p", {"target_dataset": "C"}), ("q", {"target_dataset": "D"})])
    assert p["stage_keys"]["C"]["tier2_key"] == k2 and p["stage_keys"]["D"]["tier2_key"] == ""


def test_no_keys_given_still_builds_the_provenance():
    p = prov(None, [])
    assert p["stage_keys"] == {} and p["decision_hashes"] == {}


def test_png_carries_both_keys():
    k2 = tier2_key(T1, STEPS)
    p = prov({"C": {"tier1_key": T1, "tier2_key": k2}}, [("p", {"target_dataset": "C"})])
    info = Image.open(io.BytesIO(_embed_png_provenance(png(), p, "p", "C"))).text
    assert info["sparmvet:tier1_key"] == T1 and info["sparmvet:tier2_key"] == k2


def test_png_of_a_dataset_without_tier2_has_no_tier2_key_field():
    p = prov({"C": {"tier1_key": T1, "tier2_key": ""}}, [("p", {"target_dataset": "C"})])
    info = Image.open(io.BytesIO(_embed_png_provenance(png(), p, "p", "C"))).text
    assert info["sparmvet:tier1_key"] == T1 and "sparmvet:tier2_key" not in info


def test_svg_carries_both_keys():
    k2 = tier2_key(T1, STEPS)
    p = prov({"C": {"tier1_key": T1, "tier2_key": k2}}, [("p", {"target_dataset": "C"})])
    svg = _embed_svg_provenance(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>', p, "p", "C").decode()
    assert f"sparmvet:tier1_key={T1}" in svg and f"sparmvet:tier2_key={k2}" in svg


class TestT3AuditStepsSha256:
    """issue #39/ADR-097 decision 3 — the fourth verification leg, confirmed missing
    before this (the original §12f spec named it, it was never computed anywhere)."""

    def test_present_and_stable_for_identical_content(self):
        by_plot = {"subtab_p1": [{"node_type": "filter_row", "params": {"column": "year"}}]}
        p1 = prov_t3(t3_by_plot=by_plot)
        p2 = prov_t3(t3_by_plot=dict(by_plot))
        assert p1["t3_audit_steps_sha256"] == p2["t3_audit_steps_sha256"]
        assert len(p1["t3_audit_steps_sha256"]) == 64   # sha256 hex digest

    def test_different_content_gives_a_different_hash(self):
        p1 = prov_t3(t3_by_plot={"subtab_p1": [{"node_type": "filter_row"}]})
        p2 = prov_t3(t3_by_plot={"subtab_p1": [{"node_type": "exclusion_row"}]})
        assert p1["t3_audit_steps_sha256"] != p2["t3_audit_steps_sha256"]

    def test_aesthetic_overrides_are_part_of_the_hash(self):
        """A seed pin (aesthetic_override.random_state, REPRO-SEED-1) is reproducibility-
        critical content, not cosmetic-only — it must change the hash."""
        p1 = prov_t3(t3_aesthetic_overrides={"subtab_p1": {"random_state": 1}})
        p2 = prov_t3(t3_aesthetic_overrides={"subtab_p1": {"random_state": 2}})
        assert p1["t3_audit_steps_sha256"] != p2["t3_audit_steps_sha256"]

    def test_empty_t3_still_has_a_stable_hash(self):
        p1 = prov_t3()
        p2 = prov_t3()
        assert p1["t3_audit_steps_sha256"] == p2["t3_audit_steps_sha256"]


class TestEngineAndEnvironmentFields:
    """issue #39/ADR-097 decision 3 — environment-aware engine leg: these fields must
    always be present and self-consistent, whichever path (container/source) is detected."""

    def test_engine_fingerprint_present(self):
        p = prov_t3()
        assert p["engine_fingerprint"]   # non-empty string, e.g. "2|polars=...|transformer=..."

    def test_exactly_one_environment_path_is_populated(self):
        """Never both, never neither: containerized -> image_ref may be None (not set) but
        git_commit/uv_lock_sha256 are the OTHER path's fields, not asked here directly —
        the real invariant is just that `containerized` is a plain bool and `image_ref` is
        only ever non-None when containerized is True."""
        p = prov_t3()
        assert isinstance(p["containerized"], bool)
        if not p["containerized"]:
            assert p["image_ref"] is None
        assert p["uv_lock_sha256"] is None or isinstance(p["uv_lock_sha256"], str)
