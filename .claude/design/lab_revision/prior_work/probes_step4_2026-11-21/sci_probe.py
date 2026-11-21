# copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/sci_probe.py of the main tree (not in git; written 2026-11-21 night by a step 4 viewpoint of this review); a probe, not a decision
import hashlib, itertools, random
from test_lab.anonymiser import Anonymiser, _make_hash_id
# 1 hash collisions with 8 hex = 32 bits
seen={}; coll=0
for i in range(200000):
    h=_make_hash_id(f"S{i}","ANON")
    if h in seen: coll+=1
    seen[h]=i
print("collisions in 200k ids:",coll)
# 2 reversal by dictionary
target=_make_hash_id("ISO-2023-0417","ANON")
found=[f"ISO-2023-{n:04d}" for n in range(10000) if _make_hash_id(f"ISO-2023-{n:04d}","ANON")==target]
print("dictionary reversal:",found)
# 3 sequential mapping depends on row order
a=Anonymiser()
m1=a._extend_mapping(["A","B","C"],{}, "sequential","ANON") if hasattr(a,"_extend_mapping") else None
print(m1)
m2=a._extend_mapping(["C","B","A"],{}, "sequential","ANON")
print(m2)
# 4 whitespace/case variants -> distinct anon ids
m3=a._extend_mapping(["S1","S1 ","s1"],{}, "hash","ANON"); print(m3)
