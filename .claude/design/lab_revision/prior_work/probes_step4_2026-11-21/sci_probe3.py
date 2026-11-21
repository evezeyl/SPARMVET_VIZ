# copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/sci_probe3.py of the main tree (not in git; written 2026-11-21 night by a step 4 viewpoint of this review); a probe, not a decision
from id_reconciliation.core import IDReconciliationEngine
e=IDReconciliationEngine()
ref=["ISO-12","ISO-12","ISO 7","S1","ISO-101","ISO-1","Sample_A12"]
tgt=["ISO-12-rep2","iso-12","ISO-7B","s1 ","ISO-1010","ISO-10","Sample_A21"]
for r in e.reconcile(ref,tgt): print(r.ref_id,"->",r.target_id,r.match_type,r.certainty)
print("zero rows:", e.reconcile([],["a"]), e.reconcile(["a"],[]))
print("NaN:", [ (r.ref_id,r.target_id) for r in e.reconcile(["a",None],["a"])] if True else 0)
