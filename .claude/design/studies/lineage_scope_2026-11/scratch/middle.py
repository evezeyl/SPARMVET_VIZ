exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings,time; warnings.filterwarnings("ignore")
from app.modules.audit_places import plots_below
E="32557144"; STEP={"action":"modif_filter","column":"sample_id","op":"not_in","value":[E],"na":"keep"}
for pl_ in ("T1:ResFinder","T1:metadata_schema","T1:MLST","T1:ST22_Anchor","T1:Quality_metrics"):
    bl=G.below(pl_); print(f"{pl_:24s} tables below {sum(1 for n in bl if G.node(n).kind=='T1')}  plots below {len(plots_below(G,[pl_]))}  nodes below {len(bl)}")
# middle: count at the chosen place only (one table, with the step), time it
for place in ("T1:ResFinder","T1:metadata_schema"):
    t=time.time(); d=Path("tmpAI/panel/lineage_scope/scratch/out_mid"); shutil.rmtree(d,ignore_errors=True); d.mkdir(parents=True)
    loaded=audit([(place,STEP)]); keys=quiet(orch.compute_data_analysis_recipe_keys,RID,loaded=loaded); tb=place.split(":")[1]
    quiet(orch.materialize_tier1,RID,tb,d/f"{tb}.parquet",keys=keys,loaded=loaded)
    a=pl.read_parquet(d/f"{tb}.parquet"); print(f"count at the chosen place only {place}: rows {base[place].height}->{a.height} in {time.time()-t:.3f}s (this includes the sources it reads, not the tables below)")
# plots below metadata that differ vs plots below
import itertools
