exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings,time; warnings.filterwarnings("ignore")
from app.modules.plan_composer import compose_plan_book
from utils.plan_book import Plan
t=time.time(); book=quiet(compose_plan_book,orch,RID,loaded0,G); print("plan book s",round(time.time()-t,2))
# for each T1 and T2-with-steps place: does the plan hold the column + type
def holds(c):
    out={}
    for n in G.places():
        node=G.node(n)
        if node.kind=="T3": continue
        p=book.get(n,len(node.steps))
        out[n]=(p.type_of(c) if isinstance(p,Plan) and p.has(c) else ("failure" if not isinstance(p,Plan) else None))
    return out
for c in ("identity","gene","country","sample_id","ResFinder_not_in_original_data","n_amr_genes"):
    h=holds(c); 
    print(c,"present at",[ (k,v) for k,v in h.items() if v and v!="failure"][:8],"... n=",sum(1 for v in h.values() if v and v!="failure"),"failures",sum(1 for v in h.values() if v=="failure"))
# does plan agree with real tables?
bad=0;n=0
for k,v in base.items():
    node=k
    if not G.has_node(k) or k.startswith("T3") : continue
    nd=G.node(k)
    if k not in G.places(): continue
    p=book.get(k,len(nd.steps))
    if not isinstance(p,Plan): continue
    n+=1
    names=set(c for c in v.columns)
    pn=set(c for c in v.columns if p.has(c))
    if pn!=names: bad+=1; print(" plan misses",k,sorted(names-pn)[:3])
print("places with a plan:",n,"mismatch",bad)
