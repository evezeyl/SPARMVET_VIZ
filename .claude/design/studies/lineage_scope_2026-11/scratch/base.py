import sys,time,shutil,pickle
sys.path.insert(0,"tmpAI/panel/lineage_scope/scratch")
from ds_lib import *
out=Path("tmpAI/panel/lineage_scope/scratch/out_base"); shutil.rmtree(out,ignore_errors=True)
t=time.time(); fr,keys=build(loaded0,out); print("base full build s",round(time.time()-t,2))
for k,v in fr.items():
    if k.startswith("T1:") : print(k,v.shape)
print([k for k in fr if k.startswith("T3")][:3])
print(fr["T1:ResFinder"].head(3)); print(fr["T1:ResFinder"].columns)
print(fr["T1:metadata_schema"].columns, fr["T1:metadata_schema"].shape)
