import sys,io,contextlib,json,time
sys.path.insert(0,"tmpAI/panel/lineage_scope/scratch")
from ds_lib import *
import shutil
base_dir=Path("tmpAI/panel/lineage_scope/scratch/out_base")
def quiet(f,*a,**k):
    with contextlib.redirect_stdout(io.StringIO()): return f(*a,**k)
base,bkeys=quiet(build,loaded0,base_dir)
def dg(df): return hashlib.sha256(df.write_csv().encode()).hexdigest()[:10]
bh={k:dg(v) for k,v in base.items()}
def ents(df): return df["sample_id"].n_unique() if "sample_id" in df.columns else None
def run(label, steps, tag):
    d=Path("tmpAI/panel/lineage_scope/scratch/out_"+tag); shutil.rmtree(d,ignore_errors=True)
    t=time.time()
    try:
        fr,keys=quiet(build,audit(steps),d)
    except Exception as e:
        print(f"## {label}: ERROR {type(e).__name__}: {str(e)[:300]}"); return None
    dt=time.time()-t
    ch=[k for k in fr if dg(fr[k])!=bh[k]]
    print(f"## {label}  (build {dt:.2f}s; {len(ch)} of {len(fr)} nodes differ)")
    return fr,ch
def report(fr,ch,only=None,E=None):
    for k in ch:
        if k.startswith("T2:") and base[k] is base["T1:"+k[3:]] : pass
        b,a=base[k],fr[k]
        if only and not only(k): continue
        e=f" ents {ents(b)}->{ents(a)}" if ents(b) is not None else ""
        extra=""
        if E and "sample_id" in a.columns:
            extra=f" rows_of_E {b.filter(pl.col('sample_id')==E).height}->{a.filter(pl.col('sample_id')==E).height}"
        print(f"   {k:48s} rows {b.height}->{a.height}{e}{extra}  cols {len(b.columns)}->{len(a.columns)}")

def others_changed(b,a,E):
    """rows (of entities other than E) that are in base and not in after, and vice versa; same column set only"""
    if "sample_id" not in b.columns or set(b.columns)!=set(a.columns): return None
    bb=b.filter(pl.col("sample_id")!=E); aa=a.filter(pl.col("sample_id")!=E)
    cols=[c for c in bb.columns if c in aa.columns]
    try:
        x=bb.select(cols).join(aa.select(cols),on=cols,how="anti",join_nulls=True).height
        y=aa.select(cols).join(bb.select(cols),on=cols,how="anti",join_nulls=True).height
    except Exception as e: return "?"
    return (x,y)
def report2(fr,ch,E=None):
    for k in ch:
        b,a=base[k],fr[k]
        e=f" ents {ents(b)}->{ents(a)}" if ents(b) is not None else ""
        ex=""
        if E and "sample_id" in a.columns:
            ex=f" E {b.filter(pl.col('sample_id')==E).height}->{a.filter(pl.col('sample_id')==E).height} others_rows_changed(-,+)={others_changed(b,a,E)}"
        print(f"   {k:44s} rows {b.height}->{a.height}{e}{ex} cols {len(b.columns)}->{len(a.columns)}")
