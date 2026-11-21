# copied unchanged on 2026-11-21 from tmpAI/run/probe2.py of the worktree .claude/worktrees/lab-review (not in git; written 2026-11-21 by step 1 of this review); a probe, not a decision
import io, zipfile, shutil
from pathlib import Path
from app.modules.test_lab_studio import scaffold_from_uploads
from app.modules.data_analysis_recipe_validator import engine_load_problems, validate_data_analysis_recipe
up = Path("uploads"); (up/"5.tsv").write_text("sample_id\tyear\nS001\t2020\nS002\t2021\n")
out = Path("out_G"); shutil.rmtree(out, ignore_errors=True)
zipfile.ZipFile(io.BytesIO(scaffold_from_uploads([{"name": "isolates.tsv", "datapath": str(up/"5.tsv")}], "proj_G", "sample_id"))).extractall(out)
m = out/"proj_G"/"proj_G.yaml"
print("build:", validate_data_analysis_recipe(m, "build"))
print("engine load:", engine_load_problems(m))
