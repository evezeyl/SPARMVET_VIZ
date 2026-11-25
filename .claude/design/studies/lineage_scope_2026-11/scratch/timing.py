exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings,time; warnings.filterwarnings("ignore")
from app.modules.audit_run import run_audit
from utils.audit_copy import start_audit, add_step
E="32557144"
STEP={"action":"modif_filter","column":"sample_id","op":"not_in","value":[E],"na":"keep"}
ZERO={"action":"modif_filter","column":"identity","op":"gt","value":1000.0,"na":"remove"}
WS={"action":"modif_filter","column":"sample_id","op":"not_in","value":[" "+E],"na":"keep"}
for lab,step,places in (("remove E",STEP,["T3:amr_heatmap","T1:ResFinder","T1:metadata_schema"]),("filter removes ALL rows",ZERO,["T1:ResFinder","T3:amr_heatmap"]),("id typed with a leading space",WS,["T1:ResFinder"])):
  for place in places:
    ad=Path("tmpAI/panel/lineage_scope/scratch/out_audit_run"); shutil.rmtree(ad,ignore_errors=True)
    a=start_audit(raw0,"cccc0000"); add_step(a,place,dict(step),"t")
    t=time.time()
    try:
        run=quiet(run_audit,orch,RID,a.recipe,base_dir,ad); dt=time.time()-t
        built=[k for k,v in run.tables.items() if v.t1=="built" or v.t2=="built"]
        print(f"{lab:32s} at {place:22s} run_audit {dt:.2f}s  tables built {len(built)}  plots affected {len(run.affected_plots)} reused {sum(1 for p in run.plots.values() if p.reused)}/{len(run.plots)}")
        if lab.startswith("filter removes ALL"):
            fr=run.plot_table("amr_heatmap").collect() if "amr_heatmap" in run.affected_plots else None
            print("   amr_heatmap rows:", None if fr is None else fr.height, "| affected:", run.affected_plots)
    except Exception as e: print(lab,place,"ERR",type(e).__name__,str(e)[:200])
