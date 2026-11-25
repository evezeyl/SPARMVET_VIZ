import sys; sys.path.insert(0,"tmpAI/panel/lineage_scope/scratch")
from ds_lib import *
print("collections",G.collections()); print("plots",G.plots())
for t in G.collections():
    n=G.node("T1:"+t); print(t, n.collection_kind, "parents T1:",G.parents("T1:"+t))
for p in G.plots(): print(p, "target",G.plot_target(p), "parents",G.parents("T3:"+p))
print([n for n in G.nodes() if n.startswith("DS:")][:30])
