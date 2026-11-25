from r5_lib import *
from app.modules.audit_run import run_audit
schemas=[t for t in G.collections() if G.node("T1:"+t).collection_kind=="schema"]
def originals_back(node):
    return [n[3:] for n in G.lineage_back(node) if n.startswith("T1:") and n[3:] in schemas]
def fwd_t3(t): return plots_below(G,["T1:"+t])
def tables_below(t): return sorted({n[3:] for n in G.lineage_forward("T1:"+t) if n.startswith("T1:")})
starts={"plot amr_heatmap":"T3:amr_heatmap","plot virulence_bar":"T3:virulence_bar","table AR1_MLST_Serotype_Virulence (no plot reads)":"T1:AR1_MLST_Serotype_Virulence"}
for name,n in starts.items():
    back=originals_back(n)
    print("\n#####",name); print("back (original parents):",back)
    allp=set(); allt=set()
    for t in back:
        p=fwd_t3(t); tb=tables_below(t); allp|=set(p); allt|=set(tb)
        print(f"  forth from {t}: plots {len(p)} {p}; tables {tb}")
    print("  union forward: plots",len(allp),"tables",len(allt))
    # what stays outside
    outp=[p for p in G.plots() if p not in allp]; outt=[t for t in G.collections() if t not in allt and t not in schemas]
    print("  outside plots:",outp); print("  outside derived tables:",outt)
    print("  chosen together valid:",G.chosen_places_problem(["T1:"+t for t in back]))
print("\nplots not below ANY original:",[p for p in G.plots() if not any(p in fwd_t3(t) for t in schemas)])
# FastP-only for virulence_bar
def aff(places,e=E):
    ad=Path("tmpAI/panel/lineage_scope/scratch/out_r5e"); shutil.rmtree(ad,ignore_errors=True)
    from utils.audit_copy import start_audit, add_step
    a=start_audit(raw0,"eeee0000")
    for p in places: add_step(a,p,dict(STEP),"t")
    run=quiet(run_audit,orch,RID,a.recipe,base_dir,ad)
    out={}
    for p in G.plots():
        lf=run.plot_table(p); df=lf.collect() if lf is not None else base["T3:"+p]
        out[p]=has(df,e)
    return run.affected_plots,[p for p,v in out.items() if v]
for places in (["T1:FastP"],["T1:ResFinder"],["T1:metadata_schema"],["T1:Quast"],["T1:MLST"],["T1:VirulenceFinder"],["T1:FastP","T1:ResFinder","T1:MLST","T1:VirulenceFinder"],["T1:FastP","T1:ResFinder","T1:MLST","T1:VirulenceFinder","T1:metadata_schema"]):
    a,s=aff(places); print(places,"affected",len(a),"| still show E:",len(s),[p for p in s if p in ("virulence_bar","virulence_variants","amr_heatmap")])
