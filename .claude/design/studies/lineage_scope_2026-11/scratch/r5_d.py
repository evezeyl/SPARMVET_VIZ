from r5_lib import *
fr=run([("T1:ResFinder",STEP)],"d")
a=fr["T1:ST22_Anchor"].filter(pl.col("sample_id")==E); b=base["T1:ST22_Anchor"].filter(pl.col("sample_id")==E)
print(a.columns); 
print("base rows",b.height,"after",a.height)
for c in ("gene","identity","predicted_phenotype"):
    if c in a.columns: print(c,"base non-null",b[c].drop_nulls().len(),"after non-null",a[c].drop_nulls().len())
