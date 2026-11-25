import hashlib, os, sys, time
from pathlib import Path
import polars as pl
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe, loaded_from_resolved
from app.modules.orchestrator import DataOrchestrator
from utils.audit_copy import add_step, start_audit
from utils.recipe_graph import build_graph
ROOT=Path.cwd(); RID="1_test_data_ST22_dummy"; P=ROOT/"config/data_analysis_recipes/pipelines"
clear_data_analysis_recipe_cache(); orch=DataOrchestrator(P, ROOT/"assets/test_data")
loaded0=load_data_analysis_recipe(P/f"{RID}.yaml"); raw0=loaded0.raw
G=build_graph(raw0)
tables=G.collections(); plots=G.plots()
def has_t2(t,raw):
    n=G.node("T2:"+t) if G.has_node("T2:"+t) else None
    b=G._bodies.get(t) if hasattr(G,'_bodies') else None
    x=(b or {}).get("tier2") or {}
    return bool(x.get("steps") or x.get("audit_steps"))
def build(loaded,d):
    d.mkdir(parents=True,exist_ok=True); keys=orch.compute_data_analysis_recipe_keys(RID,loaded=loaded); fr={}
    for t in tables:
        orch.materialize_tier1(RID,t,d/f"{t}.parquet",keys=keys,loaded=loaded); fr["T1:"+t]=pl.read_parquet(d/f"{t}.parquet")
        fr["T2:"+t]=orch.materialize_tier2(RID,t,d/f"{t}.parquet",keys=keys,loaded=loaded).collect() if has_t2(t,loaded.raw) else fr["T1:"+t]
    for p in plots: fr["T3:"+p]=orch.materialize_tier3(RID,p,d,keys=keys,loaded=loaded).collect()
    return fr,keys
def audit(steps_at, tag="aaaabbbb"):
    a=start_audit(raw0,tag)
    for place,step in steps_at: add_step(a,place,dict(step),"scratch")
    return loaded_from_resolved(loaded0,a.recipe)
