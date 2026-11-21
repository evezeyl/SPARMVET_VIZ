# copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/sci_probe2.py of the main tree (not in git; written 2026-11-21 night by a step 4 viewpoint of this review); a probe, not a decision
import polars as pl, tempfile, pathlib, random, numpy as np
from test_lab.anonymiser import Anonymiser, _make_hash_id
# find colliding pair
seen={}
for i in range(200000):
    h=_make_hash_id(f"S{i}","A")
    if h in seen: pair=(seen[h],f"S{i}"); break
    seen[h]=f"S{i}"
print(pair)
d=pathlib.Path(tempfile.mkdtemp()); f=d/"t.tsv"
pl.DataFrame({"id":list(pair),"v":[1,2]}).write_csv(f,separator="\t")
import inspect
print(inspect.signature(Anonymiser.anonymise))
try:
    an,mp=Anonymiser().anonymise(f,"id",[],"hash","A",out_dir=d/"out")
    print(an); print(mp)
except Exception as e: print("ERR",type(e),e)
# seed global state
from test_lab.aqua_synthesizer import AquaSynthesizer
print(inspect.signature(AquaSynthesizer.__init__))
np.random.seed(5); a=np.random.rand()
np.random.seed(5); s=AquaSynthesizer()
p=d/"in.tsv"; pl.DataFrame({"sample_id":["a","b","c"],"x":[1.0,2.0,3.0]}).write_csv(p,separator="\t"); cfg=s.propose_config(p)
s.generate(cfg,seed=99)
print("global numpy state changed:", np.random.rand()!=a)
d1=s.generate(cfg,seed=1); d2=s.generate(cfg,seed=1); print("same seed equal:",d1.equals(d2))
d3=s.generate(cfg); d4=s.generate(cfg); print("no seed equal:",d3.equals(d4))
