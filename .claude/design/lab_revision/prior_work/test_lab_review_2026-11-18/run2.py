# copied unchanged on 2026-11-21 from tmpAI/panel/test_lab_review/run2.py of the main tree (not in git; file dated 2026-11-18); a run of the earlier review, not a decision
import sys
from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe
for d in ["out_sample_id","out_Sample_ID"]:
    p = f"tmpAI/panel/test_lab_review/{d}/proj/proj.yaml"
    try:
        for pr in validate_data_analysis_recipe(p, "run"):
            print(d, "|", str(pr)[:500])
        print(d,"done")
    except BaseException as e:
        print(d,"EXC",type(e).__name__, str(e)[:600])
