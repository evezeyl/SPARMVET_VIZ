import sys,io,contextlib,shutil
sys.path.insert(0,"tmpAI/panel/lineage_scope/scratch")
from ds_lib import *
from app.modules.audit_places import plots_below
def quiet(f,*a,**k):
    with contextlib.redirect_stdout(io.StringIO()): return f(*a,**k)
base_dir=Path("tmpAI/panel/lineage_scope/scratch/out_base")
base,bkeys=quiet(build,loaded0,base_dir)
def dg(df): return hashlib.sha256(df.write_csv().encode()).hexdigest()[:10]
bh={k:dg(v) for k,v in base.items()}
E="32557144"
STEP={"action":"modif_filter","column":"sample_id","op":"not_in","value":[E],"na":"keep"}
def has(df,e=E):
    return "sample_id" in df.columns and df.filter(pl.col("sample_id").cast(pl.Utf8)==e).height
def run(steps,tag):
    d=Path("tmpAI/panel/lineage_scope/scratch/out_r5_"+tag); shutil.rmtree(d,ignore_errors=True)
    fr,keys=quiet(build,audit(steps),d); return fr
def realplace(G,places): 
    assert G.chosen_places_problem(places) is None, G.chosen_places_problem(places)
