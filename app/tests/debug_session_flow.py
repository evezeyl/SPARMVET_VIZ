#!/usr/bin/env python3
"""app/tests/debug_session_flow.py
CLI end-to-end verification of the SessionManager flow.

Creates a full session lifecycle: assembly ghost, T3 ghosts, export zip,
import zip into a separate store, and label update. Outputs artifacts to
tmp/session_test/ for @verify review.

Run:
    ./.venv/bin/python app/tests/debug_session_flow.py
    ./.venv/bin/python app/tests/debug_session_flow.py --output tmp/my_session_test/

# @deps
# provides: debug:session_flow
# consumes: app/modules/session_manager.py
# consumed_by: CI, manual @verify
# doc: .claude/rules/ui_implementation_contract.md#12d, .claude/tasks/tasks.md#22-G
# @end_deps
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

from app.modules.session_manager import (
    SessionManager,
    make_recipe_node,
    gatekeeper_blocked,
    recipe_sha256,
)
from app.modules.exporter import generate_methods_text


PASS = "✅ PASS"
FAIL = "❌ FAIL"


def run(output_dir: Path) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # ── Fixture files ────────────────────────────────────────────────
        manifest_file = tmp / "my_pipeline.yaml"
        manifest_file.write_text("id: my_pipeline\nversion: 1\n")
        data_a = tmp / "metadata.tsv"
        data_b = tmp / "amr.tsv"
        data_a.write_text("sample_id\tspecies\nS1\tcat\nS2\tdog\n")
        data_b.write_text("sample_id\tgene\nS1\tblaZ\nS2\tblaZ\n")
        source_files = {"metadata": data_a, "amr": data_b}

        sm = SessionManager(tmp / "user_sessions")

        # ── Step 1: Compute hashes ───────────────────────────────────────
        msig = SessionManager.compute_manifest_sha256(manifest_file)
        dbh = SessionManager.compute_data_batch_hash(source_files)
        key = SessionManager.compute_session_key(msig, dbh)
        ok = len(msig) == 64 and len(dbh) == 64 and ":" in key
        results.append(("Compute session_key", PASS if ok else FAIL))

        # ── Step 2: T1/T2 restore — new session ─────────────────────────
        r = sm.restore_t1t2(manifest_file, source_files)
        ok = r["status"] == "new_session"
        results.append(("restore_t1t2 new_session", PASS if ok else FAIL))

        # ── Step 3: Write assembly ghost ─────────────────────────────────
        p1 = tmp / "EVE_assembly.parquet"
        p2 = tmp / "EVE_contracted.parquet"
        p1.write_bytes(b"PAR1")
        p2.write_bytes(b"PAR1")
        sm.write_assembly_ghost(
            key, "my_pipeline", msig, dbh,
            {k: str(v) for k, v in source_files.items()},
            {"assembly": str(p1), "contracted": str(p2)},
        )
        ghost = sm.read_assembly_ghost(key)
        ok = ghost is not None and ghost["manifest_id"] == "my_pipeline"
        results.append(("Write/read assembly ghost", PASS if ok else FAIL))

        # ── Step 4: T1/T2 restore — fast path ───────────────────────────
        r = sm.restore_t1t2(manifest_file, source_files)
        ok = r["status"] == "fast_path"
        results.append(("restore_t1t2 fast_path", PASS if ok else FAIL))

        # ── Step 5: T1/T2 restore — reassemble (Parquets deleted) ───────
        p1.unlink()
        p2.unlink()
        r = sm.restore_t1t2(manifest_file, source_files)
        ok = r["status"] == "reassemble"
        results.append(("restore_t1t2 reassemble (Parquet missing)", PASS if ok else FAIL))

        # ── Step 6: Write T3 ghosts ──────────────────────────────────────
        recipe = [
            make_recipe_node("filter_row",
                             {"column": "species", "op": "in", "value": ["cat"]},
                             reason="Only feline samples in scope."),
            make_recipe_node("exclusion_row",
                             {"column": "sample_id", "op": "eq", "value": "S2"},
                             reason="S2 has instrument error noted in lab book."),
        ]
        g1 = sm.write_t3_ghost(key, "my_pipeline", msig, dbh, "T3", recipe, {}, label="batch-A v1")
        g2 = sm.write_t3_ghost(key, "my_pipeline", msig, dbh, "T3", recipe, {}, label="batch-A v2")
        ghosts = sm.list_t3_ghosts(key)
        ok = len(ghosts) == 2 and ghosts[0]["saved_at"] >= ghosts[1]["saved_at"]
        results.append(("Write 2 T3 ghosts, newest-first order", PASS if ok else FAIL))

        # ── Step 7: Gatekeeper ───────────────────────────────────────────
        bad_recipe = [make_recipe_node("filter_row", {}, reason="")]
        blocked = gatekeeper_blocked(bad_recipe)
        ok = len(blocked) == 1
        results.append(("Gatekeeper blocks empty reason", PASS if ok else FAIL))

        good_recipe = [make_recipe_node("filter_row", {}, reason="Justified.")]
        ok = len(gatekeeper_blocked(good_recipe)) == 0
        results.append(("Gatekeeper passes filled reason", PASS if ok else FAIL))

        # ── Step 8: recipe_sha256 (active only) ─────────────────────────
        mixed = recipe + [{**make_recipe_node("drop_column", {"column": "x"},
                           reason="not needed"), "active": False}]
        h1 = recipe_sha256(mixed)
        h2 = recipe_sha256(recipe)
        ok = h1 == h2  # deactivated node ignored
        results.append(("recipe_sha256 ignores active:False nodes", PASS if ok else FAIL))

        # ── Step 9: generate_methods_text ────────────────────────────────
        methods, discarded = generate_methods_text(mixed)
        ok = (len(methods) == 2 and
              any("feline" in m for m in methods) and
              any("instrument error" in m for m in methods) and
              len(discarded) == 1)
        results.append(("generate_methods_text active+discarded split", PASS if ok else FAIL))

        # ── Step 10: Label update ────────────────────────────────────────
        sm.set_session_label(key, "My final batch-A")
        ok = sm.get_session_label(key) == "My final batch-A"
        results.append(("set/get session label", PASS if ok else FAIL))

        # ── Step 11: List all sessions ───────────────────────────────────
        sessions = sm.list_all_sessions()
        ok = any(s["session_key"] == key for s in sessions)
        results.append(("list_all_sessions finds session", PASS if ok else FAIL))

        # ── Step 12: Export zip ──────────────────────────────────────────
        zip_bytes = sm.export_session_zip(key)
        ok = len(zip_bytes) > 100
        results.append(("export_session_zip produces bytes", PASS if ok else FAIL))

        # Save zip to output_dir for @verify
        zip_out = output_dir / f"session_{key[:24]}.zip"
        zip_out.write_bytes(zip_bytes)

        # ── Step 13: Import zip into fresh SessionManager ────────────────
        sm2 = SessionManager(tmp / "user_sessions_import")
        restored_key = sm2.import_session_zip(zip_bytes)
        ok = restored_key == key and sm2.read_assembly_ghost(key) is not None
        results.append(("import_session_zip roundtrip", PASS if ok else FAIL))

        # ── Step 14: Delete session ──────────────────────────────────────
        sm.delete_session(key)
        ok = sm.read_assembly_ghost(key) is None
        results.append(("delete_session removes files", PASS if ok else FAIL))

    # ── Report ───────────────────────────────────────────────────────────
    report_lines = [
        "=" * 60,
        "SPARMVET SessionManager Debug Flow",
        "=" * 60,
    ]
    all_pass = True
    for name, status in results:
        report_lines.append(f"  {status}  {name}")
        if status != PASS:
            all_pass = False

    report_lines += [
        "=" * 60,
        f"Result: {'ALL PASSED' if all_pass else 'FAILURES DETECTED'}  "
        f"({sum(1 for _, s in results if s == PASS)}/{len(results)})",
        f"Artifacts written to: {output_dir}",
        "=" * 60,
    ]
    report_text = "\n".join(report_lines)
    print(report_text)
    (output_dir / "debug_session_flow_report.txt").write_text(report_text)
    return all_pass


def main():
    parser = argparse.ArgumentParser(
        description="End-to-end CLI verification of the SPARMVET SessionManager."
    )
    parser.add_argument(
        "--output", default="tmp/session_test/",
        help="Directory for output artifacts (default: tmp/session_test/)",
    )
    args = parser.parse_args()
    ok = run(Path(args.output))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
