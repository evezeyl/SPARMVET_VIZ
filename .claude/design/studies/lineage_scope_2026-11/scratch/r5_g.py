from r5_lib import *
fr=run([("T1:ResFinder",STEP)],"g")
X="40503315"
for lab,df,e in (("base E",base["T1:ST22_Anchor"],E),("after(b) E",fr["T1:ST22_Anchor"],E),("base X (completion line in ResFinder)",base["T1:ST22_Anchor"],X)):
    d=df.filter(pl.col("sample_id")==e); print(lab,d.height,d.group_by("status","gene",maintain_order=True).len().rows()[:4])
print("T3 virulence_bar cols",fr["T3:virulence_bar"].columns)
