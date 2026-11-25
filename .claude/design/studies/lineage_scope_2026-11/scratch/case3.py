exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings; warnings.filterwarnings("ignore")
def build_tol(loaded,d):
    d.mkdir(parents=True,exist_ok=True); keys=quiet(orch.compute_data_analysis_recipe_keys,RID,loaded=loaded); fr={}; err={}
    for t in tables:
        try:
            quiet(orch.materialize_tier1,RID,t,d/f"{t}.parquet",keys=keys,loaded=loaded); fr["T1:"+t]=pl.read_parquet(d/f"{t}.parquet")
            fr["T2:"+t]=quiet(orch.materialize_tier2,RID,t,d/f"{t}.parquet",keys=keys,loaded=loaded).collect() if has_t2(t,loaded.raw) else fr["T1:"+t]
        except Exception as e: err["T1:"+t]=str(e)[:160]
    for p in plots:
        try: fr["T3:"+p]=quiet(orch.materialize_tier3,RID,p,d,keys=keys,loaded=loaded).collect()
        except Exception as e: err["T3:"+p]=str(e)[:160]
    return fr,err
def drop(cols): return {"action":"polars_drop","columns":cols}
for label,place,cols in [("drop gene (a recipe-used column) at T1:ResFinder","T1:ResFinder",["gene"]),
                          ("drop gene at T2:ResFinder","T2:ResFinder",["gene"]),
                          ("drop gene at T3:amr_heatmap","T3:amr_heatmap",["gene"]),
                          ("drop identity at T1:ResFinder","T1:ResFinder",["identity"]),
                          ("drop country at T1:metadata_schema","T1:metadata_schema",["country"]),
                          ("drop sample_id at T1:ResFinder","T1:ResFinder",["sample_id"])]:
    d=Path("tmpAI/panel/lineage_scope/scratch/out_c3"); shutil.rmtree(d,ignore_errors=True)
    try: fr,err=build_tol(audit([(place,drop(cols))]),d)
    except Exception as e: print("##",label,"-> refused before build:",type(e).__name__,str(e)[:250]); continue
    ch=[k for k in fr if dg(fr[k])!=bh.get(k)]
    print(f"## {label}: {len(ch)} nodes differ, {len(err)} nodes fail")
    for k,v in list(err.items())[:12]: print("    FAIL",k,"|",v[:130].replace("\n"," "))
    print("    changed plots:",[k for k in ch if k.startswith("T3")])
