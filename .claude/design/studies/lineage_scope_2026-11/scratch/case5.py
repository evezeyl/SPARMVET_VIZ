exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings; warnings.filterwarnings("ignore")
E="32557144"; STEP={"action":"modif_filter","column":"sample_id","op":"not_in","value":[E],"na":"keep"}
k="T3:qa_population_zscore"
for place in ("T1:Quast","T1:QA_population_zscore","T3:qa_population_zscore"):
    r=run("remove E at "+place,[(place,STEP)],"c5_"+place.replace(":","_"))
    if not r: continue
    fr,ch=r; a,b=fr[k],base[k]
    print("   zscore plot ents",ents(b),"->",ents(a),"| other entities whose n50_zscore changed:", others_changed(b,a,E))
    j=b.join(a,on="sample_id",suffix="_a").filter(pl.col("sample_id")!=E)
    if "n50_zscore_a" in j.columns and j.height: print("   max |dz| over others:", (j["n50_zscore"]-j["n50_zscore_a"]).abs().max())
    print("   other plots changed:",[x for x in ch if x.startswith("T3")])
