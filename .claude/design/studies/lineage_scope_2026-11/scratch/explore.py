import sys
sys.path.insert(0,"tmpAI/panel/lineage_scope/scratch")
from ds_lib import *
import shutil
out=Path("tmpAI/panel/lineage_scope/scratch/out_base")
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    fr,keys=build(loaded0,out)
# markers
print("--- completion markers per table: rows total, rows marked, distinct sample_id")
for t in tables:
    d=fr["T1:"+t]; m=[c for c in d.columns if c.endswith("_not_in_original_data")]
    sid="sample_id" in d.columns
    print(f"{t:40s} rows {d.height:5d} ents {d['sample_id'].n_unique() if sid else '-':>4} marked {d[m[0]].sum() if m else '-'} cols {len(d.columns)}")
print("--- plots: target + columns")
for p in plots: print(p, G.plot_target(p), G.plot_columns(p))
print(raw0.get("analysis_groups",{}).keys())
