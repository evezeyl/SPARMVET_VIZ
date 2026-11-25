exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
rf=base["T1:ResFinder"]; print(rf.group_by("sample_id").len().sort("len",descending=True).head(5))
E="32557144"
print("E rows in tables:", {k:v.filter(pl.col('sample_id')==E).height for k,v in base.items() if k.startswith("T1") and "sample_id" in v.columns})
STEP={"action":"modif_filter","column":"sample_id","op":"not_in","value":[E],"na":"keep"}
for place in ("T1:ResFinder","T3:amr_heatmap","T1:metadata_schema"):
    r=run("remove E at "+place,[(place,STEP)],"c1_"+place.replace(":","_"))
    if r: report(*r,only=lambda k:not k.startswith("T2:") or True,E=E)
