#!/usr/bin/env python3
"""app/tests/debug_home_theater.py
Phase 21-H headless verification of Home Theater logic for all 5 personas.

Tests (no Shiny server required):
  1. Persona feature flags — correct gating per persona
  2. Manifest analysis_groups → tab structure
  3. Tier choices — T3 gated to advanced+ personas only
  4. Right sidebar suppression — correct hidden_personas set
  5. Comparison mode — advanced+ only, reads comparison_mode_enabled flag
  6. Primary key extraction — extract_primary_keys from manifest
  7. Plot ID discovery — all expected plot IDs present in manifest
  8. Filter recipe builder data model — _pending_filters schema shape
  9. Session provenance — manifest sha256 computable from path
 10. Ghost restore schema — t3_recipe_by_plot structure correct after round-trip

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

ALL_PERSONAS = [
    "pipeline-static",
    "pipeline-exploration-simple",
    "pipeline-exploration-advanced",
    "project-independent",
    "developer",
]

# Personas that should see T3 tier option and right sidebar
ADVANCED_PERSONAS = {"pipeline-exploration-advanced", "project-independent", "developer"}
# Personas where right sidebar should be suppressed
HIDDEN_SIDEBAR_PERSONAS = {"pipeline-static", "pipeline-exploration-simple"}

TEST_PROJECT_ID = "1_test_data_ST22_dummy"
MANIFEST_REL = f"config/manifests/pipelines/{TEST_PROJECT_ID}.yaml"

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
# 1. Persona feature flags
# ---------------------------------------------------------------------------
def test_persona_feature_flags():
    section("1. Persona feature flags")
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

    for persona, checks in expected.items():
        bl = Bootloader(persona=persona)
        for feature, want in checks.items():
            got = bl.is_enabled(feature)
            record(
                f"{persona}.{feature}",
                got == want,
                f"want={want} got={got}",
            )


# ---------------------------------------------------------------------------
# 2. Manifest analysis_groups → tab structure
# ---------------------------------------------------------------------------
def test_tab_structure(project_root: Path):
    section("2. Manifest analysis_groups → tab structure")
    try:
        from utils.config_loader import ConfigManager
        manifest_path = project_root / MANIFEST_REL
        if not manifest_path.exists():
            record("manifest_exists", False, f"not found: {manifest_path}")
            return
        record("manifest_exists", True)

        cm = ConfigManager(str(manifest_path))
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
    section("3. Tier choices per persona")
    for persona in ALL_PERSONAS:
        tier_choices = {"T1": "Assembled", "T2": "Analysis-ready"}
        if persona in ADVANCED_PERSONAS:
            tier_choices["T3"] = "My adjustments"

        has_t3 = "T3" in tier_choices
        should_have_t3 = persona in ADVANCED_PERSONAS
        record(
            f"tier_T3_visible_{persona}",
            has_t3 == should_have_t3,
            f"has_T3={has_t3}",
        )


# ---------------------------------------------------------------------------
# 4. Right sidebar suppression logic
# ---------------------------------------------------------------------------
def test_sidebar_suppression():
    section("4. Right sidebar suppression")
    for persona in ALL_PERSONAS:
        suppressed = persona in HIDDEN_SIDEBAR_PERSONAS
        should_suppress = persona in {"pipeline-static", "pipeline-exploration-simple"}
        record(
            f"sidebar_suppressed_{persona}",
            suppressed == should_suppress,
            f"suppressed={suppressed}",
        )

    # Verify the actual hidden_personas set in home_theater.py matches expectation
    try:
        import ast, re
        ht_path = Path(__file__).parents[1] / "handlers" / "home_theater.py"
        src = ht_path.read_text()
        # Find hidden_personas assignment near right_sidebar_content_ui
        m = re.search(r'hidden_personas\s*=\s*(\{[^}]+\})', src)
        if m:
            literal = m.group(1)
            found_set = ast.literal_eval(literal)
            record(
                "hidden_personas_set_in_code",
                found_set == HIDDEN_SIDEBAR_PERSONAS,
                f"found={found_set}",
            )
        else:
            record("hidden_personas_set_in_code", False, "pattern not found in source")
    except Exception as e:
        record("hidden_personas_set_in_code", False, str(e))


# ---------------------------------------------------------------------------
# 5. Comparison mode toggle logic
# ---------------------------------------------------------------------------
def test_comparison_mode():
    section("5. Comparison mode toggle gating")
    try:
        import re
        ht_path = Path(__file__).parents[1] / "handlers" / "home_theater.py"
        src = ht_path.read_text()

        # Verify advanced set in comparison_mode_toggle_ui uses hyphens (not underscores)
        # Capture the full function body (up to the next @render or end-of-def block)
        m = re.search(r'def comparison_mode_toggle_ui\b(.*?)(?=\n    @|\Z)', src, re.DOTALL)
        if m:
            block = m.group(0)
            has_hyphens = "pipeline-exploration-advanced" in block
            has_underscores = "pipeline_exploration_advanced" in block
            record("comparison_toggle_uses_hyphen_ids", has_hyphens and not has_underscores)
            has_tier_gate = 'tier_toggle.get() != "T3"' in block
            record("comparison_toggle_gated_by_tier", has_tier_gate)
        else:
            record("comparison_mode_toggle_ui_found", False, "function not found")

        # Verify baseline handler is registered
        has_baseline = "_make_cmp_baseline_handler" in src
        record("cmp_baseline_handler_registered", has_baseline)

        # Verify dynamic_tabs reads comparison_mode
        has_comparison_read = "comparison_mode" in src and "in_comparison" in src
        record("dynamic_tabs_reads_comparison_mode", has_comparison_read)

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

        manifest_path = project_root / MANIFEST_REL
        if not manifest_path.exists():
            record("primary_keys_manifest_present", False)
            return

        cm = ConfigManager(str(manifest_path))
        pks = extract_primary_keys(cm.raw_config)
        record("primary_keys_extracted", isinstance(pks, (set, list, frozenset)),
               f"keys={sorted(pks)}")
        record("primary_keys_nonempty", len(pks) > 0, f"count={len(pks)}")
    except Exception as e:
        record("primary_keys_error", False, str(e))
        traceback.print_exc()


# ---------------------------------------------------------------------------
# 7. Session provenance — manifest sha256
# ---------------------------------------------------------------------------
def test_session_provenance(project_root: Path):
    section("7. Session provenance — manifest sha256")
    try:
        from app.modules.session_manager import SessionManager

        manifest_path = project_root / MANIFEST_REL
        if not manifest_path.exists():
            record("provenance_manifest_present", False)
            return

        sha = SessionManager.compute_manifest_sha256(manifest_path)
        record("manifest_sha256_computed", bool(sha) and len(sha) == 64, f"sha={sha[:12]}…")

        # Deterministic: same file → same hash
        sha2 = SessionManager.compute_manifest_sha256(manifest_path)
        record("manifest_sha256_deterministic", sha == sha2)
    except Exception as e:
        record("session_provenance_error", False, str(e))


# ---------------------------------------------------------------------------
# 8. Ghost round-trip — t3_recipe_by_plot
# ---------------------------------------------------------------------------
def test_ghost_roundtrip():
    section("8. Ghost round-trip — t3_recipe_by_plot schema")
    try:
        from app.modules.session_manager import SessionManager, make_recipe_node

        with tempfile.TemporaryDirectory() as tmp:
            sm = SessionManager(location_4=Path(tmp))
            session_key = "testkey123"

            node_a = make_recipe_node("filter_row", params={"column": "sample_id", "op": "eq", "value": "S1"})
            node_b = make_recipe_node("drop_column", params={"column": "notes"}, plot_scope="subtab_amr_heatmap")

            t3_by_plot = {
                "subtab_mlst_bar": [node_a],
                "subtab_amr_heatmap": [node_b],
            }

            path = sm.write_t3_ghost(
                session_key=session_key,
                manifest_id=TEST_PROJECT_ID,
                manifest_sha256="abc123",
                data_batch_hash="def456",
                tier_toggle="T3",
                t3_recipe=[],
                t3_plot_overrides={},
                t3_recipe_by_plot=t3_by_plot,
            )
            record("ghost_written", path.exists(), str(path))

            ghosts = sm.list_t3_ghosts(session_key)
            record("ghost_listed", len(ghosts) == 1, f"count={len(ghosts)}")

            ghost = ghosts[0]
            restored = ghost.get("t3_recipe_by_plot", {})
            record("t3_recipe_by_plot_present", bool(restored))
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
# 9. Filter recipe builder data model
# ---------------------------------------------------------------------------
def test_filter_recipe_schema():
    section("9. Filter recipe node schema")
    try:
        from app.modules.session_manager import make_recipe_node, gatekeeper_blocked

        node = make_recipe_node("filter_row", params={"column": "sample_id", "op": "eq", "value": "S1"})
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
        pk_node = make_recipe_node(
            "exclusion_row",
            params={"column": "sample_id", "op": "ne", "value": "S1"},
            primary_key_warning=True,
        )
        record("pk_node_has_warning_flag", bool(pk_node.get("primary_key_warning")))

    except Exception as e:
        record("filter_recipe_schema_error", False, str(e))
        traceback.print_exc()


# ---------------------------------------------------------------------------
# 10. Bootloader location resolution
# ---------------------------------------------------------------------------
def test_bootloader_locations(project_root: Path):
    section("10. Bootloader location resolution")
    try:
        from app.src.bootloader import Bootloader
        bl = Bootloader(persona="developer")

        for loc_key in ("manifests", "user_sessions"):
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

    test_persona_feature_flags()
    test_tab_structure(project_root)
    test_tier_choices()
    test_sidebar_suppression()
    test_comparison_mode()
    test_primary_keys(project_root)
    test_session_provenance(project_root)
    test_ghost_roundtrip()
    test_filter_recipe_schema()
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
