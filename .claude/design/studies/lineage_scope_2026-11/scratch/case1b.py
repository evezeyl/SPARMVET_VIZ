exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
E="32557144"
STEP={"action":"modif_filter","column":"sample_id","op":"not_in","value":[E],"na":"keep"}
# metadata: what changed in E's row
r=run("remove E at T1:metadata_schema",[("T1:metadata_schema",STEP)],"c1m")
fr,ch=r
print("E in T1:ResFinder_with_metadata before:", base["T1:ResFinder_with_metadata"].filter(pl.col("sample_id")==E).select("sample_id","source","year","country").head(2))
print("after:", fr["T1:ResFinder_with_metadata"].filter(pl.col("sample_id")==E).select("sample_id","source","year","country").head(2))
for k in ("T3:qa_population_zscore","T3:qa_amr_genes_per_sample","T3:mlst_bar","T3:virulence_bar"):
    print(k, "others",others_changed(base[k],fr[k],E))
print("zscore E before/after:", base["T3:qa_population_zscore"].filter(pl.col("sample_id")==E) if "sample_id" in base["T3:qa_population_zscore"].columns else base["T3:qa_population_zscore"].columns)
print(base["T3:qa_population_zscore"].head(3)); print(fr["T3:qa_population_zscore"].filter(pl.col("sample_id")==E))
print("ResFinder place:")
r=run("remove E at T1:ResFinder",[("T1:ResFinder",STEP)],"c1r"); report2(*r,E=E)
