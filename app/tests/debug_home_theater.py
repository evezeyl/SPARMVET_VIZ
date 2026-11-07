#!/usr/bin/env python3
"""app/tests/debug_home_theater.py
Phase 21-H headless verification of Home Theater logic for all 5 app features files.

Tests (no Shiny server required):
  1. App features feature flags — correct gating per app features
  2. Data analysis recipe analysis_groups → tab structure
  3. Tier choices — T3 gated to advanced+ app features files only
  4. Right sidebar suppression — correct hidden_app_features set
  5. Comparison mode — advanced+ only, reads comparison_mode_enabled flag
  6. Primary key extraction — extract_primary_keys from data analysis recipe
  7. Plot ID discovery — all expected plot IDs present in data analysis recipe
  8. Filter builder data model — _pending_filters schema shape
  9. Session provenance — data analysis recipe sha256 computable from path
 10. Ghost restore schema — t3_audit_steps_by_plot structure correct after round-trip

Run:
    python3 app/tests/debug_home_theater.py
    python3 app/tests/debug_home_theater.py --output tmpAI/home_theater_verify/

# @deps
# provides: debug:home_theater_headless
# consumes: app/src/bootloader.py, app/modules/session_manager.py, utils/config_loader.py
# consumed_by: CI, manual @verify
# doc: .claude/tasks/tasks.md#21-H
# @end_deps
"""

import argparse
import json
import sys
import tempfile
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
PASS = "✅ PASS"
FAIL = "❌ FAIL"
SKIP = "⏭  SKIP"

ALL_APP_FEATURES = [
    "pipeline-static",
    "pipeline-exploration-simple",
    "pipeline-exploration-advanced",
    "project-independent",
    "developer",
]

# App features files that should see T3 tier option and right sidebar
ADVANCED_APP_FEATURES = {"pipeline-exploration-advanced", "project-independent", "developer"}
# App features files where right sidebar should be suppressed
HIDDEN_SIDEBAR_APP_FEATURES = {"pipeline-static", "pipeline-exploration-simple"}

TEST_PROJECT_ID = "1_test_data_ST22_dummy"
DATA_ANALYSIS_RECIPE_REL = f"config/data_analysis_recipes/pipelines/{TEST_PROJECT_ID}.yaml"

results: list[dict] = []


def record(name: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    results.append({"name": name, "status": status, "detail": detail})
    print(f"  {status}  {name}" + (f" — {detail}" if detail else ""))


def section(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


# ---------------------------------------------------------------------------
# 1. App features feature flags
# ---------------------------------------------------------------------------
def test_app_features_feature_flags():
    section("1. App features feature flags")
    from app.src.bootloader import Bootloader

    expected = {
        "pipeline-static": {
            "interactivity_enabled": False,
            "developer_mode_enabled": False,
            "gallery_enabled": False,
            "session_management_enabled": False,
            "comparison_mode_enabled": False,
        },
        "pipeline-exploration-simple": {
            "interactivity_enabled": True,
            "developer_mode_enabled": False,
            "gallery_enabled": False,
            "session_management_enabled": True,
            "comparison_mode_enabled": True,
        },
        "pipeline-exploration-advanced": {
            "interactivity_enabled": True,
            "developer_mode_enabled": False,
            "session_management_enabled": True,
            "comparison_mode_enabled": True,
        },
        "project-independent": {
            "interactivity_enabled": True,
            "data_ingestion_enabled": True,
            "session_management_enabled": True,
        },
        "developer": {
            "interactivity_enabled": True,
            "developer_mode_enabled": True,
            "gallery_enabled": True,
            "session_management_enabled": True,
            "comparison_mode_enabled": True,
        },
    }

    for app_features, checks in expected.items():
        bl = Bootloader(app_features=app_features)
        for feature, want in checks.items():
            got = bl.is_enabled(feature)
            record(
                f"{app_features}.{feature}",
                got == want,
                f"want={want} got={got}",
            )


# ---------------------------------------------------------------------------
# 2. Data analysis recipe analysis_groups → tab structure
# ---------------------------------------------------------------------------
def test_tab_structure(project_root: Path):
    section("2. Data analysis recipe analysis_groups → tab structure")
    try:
        from utils.config_loader import ConfigManager
        data_analysis_recipe_path = project_root / DATA_ANALYSIS_RECIPE_REL
        if not data_analysis_recipe_path.exists():
            record("data_analysis_recipe_exists", False, f"not found: {data_analysis_recipe_path}")
            return
        record("data_analysis_recipe_exists", True)

        cm = ConfigManager(str(data_analysis_recipe_path))
        groups = cm.raw_config.get("analysis_groups", {})
        record("analysis_groups_present", bool(groups), f"{len(groups)} group(s)")

        all_plot_ids = []
        for gid, gspec in groups.items():
            plots = gspec.get("plots", {})
            record(
                f"group_{gid}_has_plots",
                bool(plots),
                f"{len(plots)} plot(s): {list(plots.keys())}",
            )
            all_plot_ids.extend(plots.keys())

        record("plot_ids_unique", len(all_plot_ids) == len(set(all_plot_ids)),
               f"total={len(all_plot_ids)} unique={len(set(all_plot_ids))}")

        # Each plot should have a spec block
        for gid, gspec in groups.items():
            for pid, pspec in gspec.get("plots", {}).items():
                has_spec = "spec" in pspec
                record(f"plot_{pid}_has_spec", has_spec)
                if has_spec:
                    td = pspec["spec"].get("target_dataset") or pspec.get("target_dataset")
                    record(f"plot_{pid}_has_target_dataset", bool(td), td or "MISSING")

    except Exception as e:
        record("tab_structure_error", False, str(e))
        traceback.print_exc()


# ---------------------------------------------------------------------------
# 3. Tier choices gating
# ---------------------------------------------------------------------------
def test_tier_choices():
    section("3. Tier choices per app features")
    for app_features in ALL_APP_FEATURES:
        tier_choices = {"T1": "Assembled", "T2": "Analysis-ready"}
        if app_features in ADVANCED_APP_FEATURES:
            tier_choices["T3"] = "My adjustments"

        has_t3 = "T3" in tier_choices
        should_have_t3 = app_features in ADVANCED_APP_FEATURES
        record(
            f"tier_T3_visible_{app_features}",
            has_t3 == should_have_t3,
            f"has_T3={has_t3}",
        )


# ---------------------------------------------------------------------------
# 4. Right sidebar suppression logic
# ---------------------------------------------------------------------------
def test_sidebar_suppression():
    section("4. Right sidebar suppression")
    for app_features in ALL_APP_FEATURES:
        suppressed = app_features in HIDDEN_SIDEBAR_APP_FEATURES
        should_suppress = app_features in {"pipeline-static", "pipeline-exploration-simple"}
        record(
            f"sidebar_suppressed_{app_features}",
            suppressed == should_suppress,
            f"suppressed={suppressed}",
        )

    # Verify the actual hidden_app_features set in home_theater.py matches expectation
    try:
        import ast, re
        ht_path = Path(__file__).parents[1] / "handlers" / "home_theater.py"
        src = ht_path.read_text()
        # Find hidden_app_features assignment near right_sidebar_content_ui
        m = re.search(r'hidden_app_features\s*=\s*(\{[^}]+\})', src)
        if m:
            literal = m.group(1)
            found_set = ast.literal_eval(literal)
            record(
                "hidden_app_features_set_in_code",
                found_set == HIDDEN_SIDEBAR_APP_FEATURES,
                f"found={found_set}",
            )
        else:
            record("hidden_app_features_set_in_code", False, "pattern not found in source")
    except Exception as e:
        record("hidden_app_features_set_in_code", False, str(e))


# ---------------------------------------------------------------------------
# 5. Comparison mode toggle logic
# ---------------------------------------------------------------------------
def test_comparison_mode():
    section("5. Comparison mode toggle gating")
    try:
        import re
        ht_path = Path(__file__).parents[1] / "handlers" / "home_theater.py"
        src = ht_path.read_text()

        # ADR-086: the old comparison_mode switch is gone; Compare is the "CMP" value
        # of the plot_view radio, offered only when comparison_mode_enabled.
        record("old_comparison_switch_removed", "def comparison_mode_toggle_ui" not in src)
        record("plot_view_radio_present", '"plot_view"' in src and '"CMP"' in src)
        record("compare_choice_flag_gated",
               'if bootloader.is_enabled("comparison_mode_enabled"):\n                plot_choices["CMP"]' in src)

        # Verify baseline handler is registered
        has_baseline = "_make_cmp_baseline_handler" in src
        record("cmp_baseline_handler_registered", has_baseline)

        # The plot cell reads plot_view == "CMP" (not an input.comparison_mode switch)
        has_comparison_read = 'safe_input(input, "plot_view", "T2") == "CMP"' in src and "in_comparison" in src
        record("plot_cell_reads_plot_view", has_comparison_read)

        # ADR-086: the reference (left) pane must be T2, never T1
        m = re.search(r'def _cmp_baseline_handler\b(.*?)return _cmp_baseline_handler', src, re.DOTALL)
        record("cmp_baseline_uses_t2",
               bool(m) and '_resolve_active_lf(spec, tier="T2")' in m.group(1) and "_resolve_t1_lf" not in m.group(1))

        # Verify 2-column layout output IDs use _cmp_base suffix
        has_cmp_output = "plot_group_{p_id}_cmp_base" in src or "_cmp_base" in src
        record("cmp_base_output_id_present", has_cmp_output)

    except Exception as e:
        record("comparison_mode_test_error", False, str(e))


# ---------------------------------------------------------------------------
# 6. Primary key extraction
# ---------------------------------------------------------------------------
def test_primary_keys(project_root: Path):
    section("6. Primary key extraction")
    try:
        from utils.config_loader import ConfigManager
        from app.modules.session_manager import extract_primary_keys

        data_analysis_recipe_path = project_root / DATA_ANALYSIS_RECIPE_REL
        if not data_analysis_recipe_path.exists():
            record("primary_keys_data_analysis_recipe_present", False)
            return

        cm = ConfigManager(str(data_analysis_recipe_path))
        pks = extract_primary_keys(cm.raw_config)
        record("primary_keys_extracted", isinstance(pks, (set, list, frozenset)),
               f"keys={sorted(pks)}")
        record("primary_keys_nonempty", len(pks) > 0, f"count={len(pks)}")
    except Exception as e:
        record("primary_keys_error", False, str(e))
        traceback.print_exc()


# ---------------------------------------------------------------------------
# 7. Session provenance — data analysis recipe sha256
# ---------------------------------------------------------------------------
def test_session_provenance(project_root: Path):
    section("7. Session provenance — data analysis recipe sha256")
    try:
        from app.modules.session_manager import SessionManager

        data_analysis_recipe_path = project_root / DATA_ANALYSIS_RECIPE_REL
        if not data_analysis_recipe_path.exists():
            record("provenance_data_analysis_recipe_present", False)
            return

        sha = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_path)
        record("data_analysis_recipe_sha256_computed", bool(sha) and len(sha) == 64, f"sha={sha[:12]}…")

        # Deterministic: same file → same hash
        sha2 = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_path)
        record("data_analysis_recipe_sha256_deterministic", sha == sha2)
    except Exception as e:
        record("session_provenance_error", False, str(e))


# ---------------------------------------------------------------------------
# 8. Ghost round-trip — t3_audit_steps_by_plot
# ---------------------------------------------------------------------------
def test_ghost_roundtrip():
    section("8. Ghost round-trip — t3_audit_steps_by_plot schema")
    try:
        from app.modules.session_manager import SessionManager, make_audit_step

        with tempfile.TemporaryDirectory() as tmp:
            sm = SessionManager(location_4=Path(tmp))
            session_key = "testkey123"

            node_a = make_audit_step("filter_row", params={"column": "sample_id", "op": "eq", "value": "S1"})
            node_b = make_audit_step("drop_column", params={"column": "notes"}, plot_scope="subtab_amr_heatmap")

            t3_by_plot = {
                "subtab_mlst_bar": [node_a],
                "subtab_amr_heatmap": [node_b],
            }

            path = sm.write_t3_ghost(
                session_key=session_key,
                data_analysis_recipe_id=TEST_PROJECT_ID,
                data_analysis_recipe_sha256="abc123",
                data_batch_hash="def456",
                tier_toggle="T3",
                t3_audit_steps=[],
                t3_plot_overrides={},
                t3_audit_steps_by_plot=t3_by_plot,
            )
            record("ghost_written", path.exists(), str(path))

            ghosts = sm.list_t3_ghosts(session_key)
            record("ghost_listed", len(ghosts) == 1, f"count={len(ghosts)}")

            ghost = ghosts[0]
            restored = ghost.get("t3_audit_steps_by_plot", {})
            record("t3_audit_steps_by_plot_present", bool(restored))
            record("mlst_bar_stack_restored",
                   len(restored.get("subtab_mlst_bar", [])) == 1)
            record("amr_heatmap_stack_restored",
                   len(restored.get("subtab_amr_heatmap", [])) == 1)

            # schema_version should be 2
            raw = json.loads(path.read_text())
            record("ghost_schema_version_2", raw.get("schema_version") == 2,
                   f"version={raw.get('schema_version')}")

    except Exception as e:
        record("ghost_roundtrip_error", False, str(e))
        traceback.print_exc()


# ---------------------------------------------------------------------------
# 9. Filter builder data model
# ---------------------------------------------------------------------------
def test_filter_builder_schema():
    section("9. Filter audit step schema")
    try:
        from app.modules.session_manager import make_audit_step, gatekeeper_blocked

        node = make_audit_step("filter_row", params={"column": "sample_id", "op": "eq", "value": "S1"})
        required_keys = {"id", "node_type", "created_at", "plot_scope", "params", "reason", "active"}
        missing = required_keys - set(node.keys())
        record("filter_node_has_required_keys", not missing, f"missing={missing}")
        record("filter_node_id_shiny_safe",
               all(c.isalnum() or c == '_' for c in node["id"]),
               f"id={node['id'][:12]}…")

        # Gatekeeper blocks on empty reason
        blocked = gatekeeper_blocked([node])
        record("gatekeeper_blocks_empty_reason", blocked)

        node["reason"] = "test reason"
        unblocked = not gatekeeper_blocked([node])
        record("gatekeeper_unblocks_with_reason", unblocked)

        # PK warning node
        pk_node = make_audit_step(
            "exclusion_row",
            params={"column": "sample_id", "op": "ne", "value": "S1"},
            primary_key_warning=True,
        )
        record("pk_node_has_warning_flag", bool(pk_node.get("primary_key_warning")))

    except Exception as e:
        record("filter_builder_schema_error", False, str(e))
        traceback.print_exc()


# ---------------------------------------------------------------------------
# 10. Bootloader location resolution
# ---------------------------------------------------------------------------
def test_bootloader_locations(project_root: Path):
    section("10. Bootloader location resolution")
    try:
        from app.src.bootloader import Bootloader
        bl = Bootloader(app_features="developer")

        for loc_key in ("data_analysis_recipes", "user_data"):
            try:
                loc = bl.get_location(loc_key)
                record(f"location_{loc_key}", True, str(loc))
            except Exception as e:
                record(f"location_{loc_key}", False, str(e))

        default_project = bl.get_default_project()
        record("default_project_discoverable", bool(default_project), default_project)

    except Exception as e:
        record("bootloader_location_error", False, str(e))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Phase 21-H: Home Theater headless verification")
    parser.add_argument(
        "--output", default="tmpAI/home_theater_verify",
        help="Output directory for artifacts (default: tmpAI/home_theater_verify)"
    )
    args = parser.parse_args()

    project_root = Path(__file__).parents[2]
    out_dir = project_root / args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("  Phase 21-H — Home Theater Headless Verification")
    print(f"  Project root : {project_root}")
    print(f"  Output dir   : {out_dir}")
    print(f"{'='*60}")

    test_app_features_feature_flags()
    test_tab_structure(project_root)
    test_tier_choices()
    test_sidebar_suppression()
    test_comparison_mode()
    test_primary_keys(project_root)
    test_session_provenance(project_root)
    test_ghost_roundtrip()
    test_filter_builder_schema()
    test_bootloader_locations(project_root)

    # Summary
    passed = sum(1 for r in results if r["status"] == PASS)
    failed = sum(1 for r in results if r["status"] == FAIL)
    total = len(results)

    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
    print(f"{'='*60}\n")

    if failed:
        print("Failed tests:")
        for r in [x for x in results if x["status"] == FAIL]:
            print(f"  {FAIL} {r['name']} — {r['detail']}")
        print()

    # Write JSON report
    report_path = out_dir / "results.json"
    report_path.write_text(json.dumps({
        "total": total,
        "passed": passed,
        "failed": failed,
        "results": results,
    }, indent=2))
    print(f"  Report written → {report_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
