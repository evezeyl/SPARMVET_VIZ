exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings,time; warnings.filterwarnings("ignore")
from app.modules.audit_run import run_audit
from utils.audit_copy import start_audit, add_step
E="32557144"; STEP={"action":"modif_filter","column":"sample_id","op":"not_in","value":[E],"na":"keep"}
res=[t for t in tables if not [n for n in G.lineage_forward("T1:"+t) if G.node(n).kind=="T3"]]
print("result tables (no plot below):",res)
for t in res:
    print(t,"children of its T1:",G.children("T1:"+t),"| is parent of other table:",[n for n in G.lineage_forward("T1:"+t) if G.node(n).kind=="T1"])
for place in ("T1:Quality_metrics","T1:ResFinder_with_metadata","T1:AR1_MLST_Serotype_Virulence"):
    ad=Path("tmpAI/panel/lineage_scope/scratch/out_audit_run2"); shutil.rmtree(ad,ignore_errors=True)
    a=start_audit(raw0,"dddd1111"); add_step(a,place,dict(STEP),"t")
    run=quiet(run_audit,orch,RID,a.recipe,base_dir,ad)
    t=place.split(":")[1]; tr=run.tables[t]
    print(f"{place}: tables built {[k for k,v in run.tables.items() if v.t1=='built']}  plots affected {run.affected_plots}  T1 key changed {tr.t1_key_original!=tr.t1_key_audit}")
    b=base[place]; 
    import polars as pl
    a_=pl.read_parquet(tr.t1_path); print(f"    T1 rows {b.height}->{a_.height}  entities {ents(b)}->{ents(a_)}")
