exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings; warnings.filterwarnings("ignore")
print("ResFinder columns T1:",base["T1:ResFinder"].columns); print("T2:",base["T2:ResFinder"].columns); print("T3 amr_heatmap:",base["T3:amr_heatmap"].columns)
print(base["T1:ResFinder"].filter(pl.col("ResFinder_not_in_original_data")).select("sample_id","gene","identity","status"))
print("identity nulls T1:",base["T1:ResFinder"]["identity"].null_count(), "min/max",base["T1:ResFinder"]["identity"].min(),base["T1:ResFinder"]["identity"].max())
print("where is the marker column kept:",[k for k,v in base.items() if any(c.endswith('_not_in_original_data') for c in v.columns)])
F=lambda op,v,na:{"action":"modif_filter","column":"identity","op":op,"value":v,"na":na}
for na in ("remove","keep"):
  for place in ("T1:ResFinder","T2:ResFinder","T3:amr_heatmap"):
    r=run(f"identity ge 98 na={na} at {place}",[(place,F("ge",98.0,na))],"c2_%s_%s"%(na,place.replace(":","_")))
    if r:
        fr,ch=r
        for k in ("T1:ResFinder","T3:amr_heatmap","T1:ST22_Anchor","T3:virulence_bar","T3:qa_amr_genes_per_sample","T3:qa_fanout_rows_per_sample"):
            b,a=base[k],fr[k]; print(f"   {k:34s} rows {b.height}->{a.height} ents {ents(b)}->{ents(a)}")
