# copied unchanged on 2026-11-21 from tmpAI/run/probe.py of the worktree .claude/worktrees/lab-review (not in git; written 2026-11-21 by step 1 of this review); a probe, not a decision
"""Read-only probe for TESTLAB-REVIEW-1 step 1. Writes only under tmpAI/run/ of the worktree.

Run from tmpAI/run with PYTHONPATH set to the worktree root.
"""
import io
import shutil
import zipfile
from pathlib import Path

import polars as pl

HERE = Path.cwd()
UP = HERE / "uploads"
shutil.rmtree(UP, ignore_errors=True)
UP.mkdir(parents=True)

# Shiny names uploads 0.tsv, 1.tsv (the user's names are only in `name`)
(UP / "0.tsv").write_text("sample_id\tyear\tcountry\n007\t2020\tNO\n008\t2021\tSE\n009\t2022\tDK\n")
(UP / "1.tsv").write_text("sample_id\tgene\n007\tblaTEM\n008\ttetA\n010\tsul1\n")
(UP / "2.csv").write_text("sample_id,year\nS001,2020\nS002,2021\n")


def scaffold_case(tag, infos, key):
    from app.modules.test_lab_studio import scaffold_from_uploads
    out = HERE / f"out_{tag}"
    shutil.rmtree(out, ignore_errors=True)
    data = scaffold_from_uploads(infos, f"proj_{tag}", key)
    zipfile.ZipFile(io.BytesIO(data)).extractall(out)
    master = out / f"proj_{tag}" / f"proj_{tag}.yaml"
    print(f"--- case {tag}: files", sorted(str(p.relative_to(out)) for p in out.rglob("*.yaml")))
    print(master.read_text())
    from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe
    for profile in ("build", "run"):
        probs = validate_data_analysis_recipe(master, profile)
        print(f"   profile {profile}: {len(probs)} problem(s)")
        for p in probs:
            print("    ", p)


scaffold_case("A", [{"name": "isolates.tsv", "datapath": str(UP / "0.tsv")},
                    {"name": "amr.tsv", "datapath": str(UP / "1.tsv")}], "sample_id")
scaffold_case("B", [{"name": "isolates.tsv", "datapath": str(UP / "0.tsv")}], "sample_id")

print("--- case C: ID cleaning step against ids that already matched")
from id_reconciliation import IDReconciliationEngine, apply_recode_step
eng = IDReconciliationEngine()
ref = ["ISOLATE_1", "ISOLATE_2", "sample_004", "sample_005"]
tgt = ["ISOLATE_1", "ISOLATE_2", "004", "005"]
res = eng.reconcile(ref, tgt)
print("   matches:", [(r.ref_id, r.target_id, r.match_type) for r in res])
tr = eng.generate_transformation(res, "ref", "tgt")
print("   steps:", tr.steps)
cleaned = apply_recode_step(pl.DataFrame({"ref": ref}), "ref", tr)["ref"].to_list()
print("   cleaned:", cleaned, "matching:", sum(c in tgt for c in cleaned), "of", len(ref))

print("--- case D: delimiter pattern, hyphen in ref, underscore in target")
ref = ["S-001", "S-002", "S-003"]
tgt = ["S_001", "S_002", "S_003"]
res = eng.reconcile(ref, tgt)
print("   matches:", [(r.ref_id, r.target_id, r.match_type) for r in res])
tr = eng.generate_transformation(res, "ref", "tgt")
print("   steps:", tr.steps)
cleaned = apply_recode_step(pl.DataFrame({"ref": ref}), "ref", tr)["ref"].to_list()
print("   cleaned:", cleaned, "matching:", sum(c in tgt for c in cleaned), "of", len(ref))

print("--- case E: synthesizer on a comma file")
from test_lab.aqua_synthesizer import AquaSynthesizer
cfg = AquaSynthesizer().propose_config(UP / "2.csv", n_rows=5)
print("   columns:", [c["name"] for c in cfg["columns"]])

print("--- case F: anonymiser with an empty id")
(UP / "3.tsv").write_text("sample_id\tx\nA\t1\n\t2\nB\t3\n")
from test_lab.anonymiser import Anonymiser
try:
    Anonymiser().anonymise(UP / "3.tsv", "sample_id")
    print("   no error")
except Exception as exc:
    print("   raised", type(exc).__name__, exc)
