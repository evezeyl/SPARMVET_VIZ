from r5_lib import *
from app.modules.audit_run import run_audit
from utils.audit_copy import start_audit, add_step
schemas=[t for t in G.collections() if G.node("T1:"+t).collection_kind=="schema"]
data=[t for t in schemas if t not in ("metadata_schema","APEC_STEC_virulence_genes")]
def ra(places,step,tag):
    ad=Path("tmpAI/panel/lineage_scope/scratch/out_r5ra_"+tag); shutil.rmtree(ad,ignore_errors=True)
    a=start_audit(raw0,"dddd0000")
    for p in places: add_step(a,p,dict(step),"t")
    run=quiet(run_audit,orch,RID,a.recipe,base_dir,ad)
    return run
def plotsE(run,e):
    out={}
    for p in G.plots():
        lf=run.plot_table(p); df=lf.collect() if lf is not None else base["T3:"+p]
        out[p]=(has(base["T3:"+p],e),has(df,e),base["T3:"+p].height,df.height)
    return out
def rep(label,run,e):
    r=plotsE(run,e); still=[p for p,v in r.items() if v[1]]
    print(f"## {label}: affected {len(run.affected_plots)}; plots still showing {e}: {len(still)} {still}; plots that held it before: {sum(1 for v in r.values() if v[0])}")
    fr=run.audited_frames()
    held=[(t,tier) for t,d in fr.items() for tier,df in d.items() if has(df,e)]
    print("   audited result tables still holding it:",held)
    return r
run=ra(["T1:"+t for t in data],STEP,"data12"); rep("(a) data12 E",run,E)
run=ra(["T1:"+t for t in data]+["T1:metadata_schema"],STEP,"data12m"); rep("(a) data12+meta E",run,E)
# which nodes unchanged in (a)
fr=quiet(build,audit([("T1:"+t,STEP) for t in data]),Path("tmpAI/panel/lineage_scope/scratch/out_r5_x"))[0]
print("unchanged nodes:",[k for k in fr if dg(fr[k])==bh[k]])
# completion-line entity: X is not in original ResFinder (added line)
X="40503315"
print("X real rows per original:", {t:(has(base['T1:'+t],X)) for t in data+['metadata_schema']})
print("X marked-added rows in ResFinder:",base["T1:ResFinder"].filter((pl.col("sample_id")==X)).select("sample_id","ResFinder_not_in_original_data").rows())
STX={**STEP,"value":[X]}
run=ra(["T1:"+t for t in data],STX,"X12"); rep("(a) data12 X (X is a completion line in ResFinder)",run,X)
run=ra(["T1:"+t for t in data if t!="ResFinder"],STX,"X11"); rep("(a') data minus ResFinder, X",run,X)
run=ra(["T1:ResFinder"],STX,"Xrf"); rep("(b) T1:ResFinder only, X",run,X)
# (b) E at T1:ResFinder, (c) tier 3
run=ra(["T1:ResFinder"],STEP,"Erf"); r=rep("(b) T1:ResFinder E",run,E)
for p,v in r.items():
    if v[0]: print("    ",p,v)
run=ra(["T3:amr_heatmap"],STEP,"Eh"); rep("(c) T3 amr_heatmap E",run,E)
