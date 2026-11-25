from collections import Counter
from utils.recipe_graph import build_graph
import importlib
m=None
for mod in ("app.modules.cache_keys",):
    m=importlib.import_module(mod)
load=m.load_data_analysis_recipe
g=build_graph(load('config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml').raw)
nodes=g.nodes()
print(len(nodes),Counter(g.node(n).kind for n in nodes))
print("edges",len(g.edges()),"places",len(g.places()),"plots",len(g.plots()))
roots=[n for n in nodes if not g.parents(n)];print("roots",roots)
# depth
d={}
for n in nodes:
    d[n]=0 if not g.parents(n) else 1+max(d[p] for p in g.parents(n))
lv=Counter(d.values());print("levels",sorted(lv.items()),"max depth",max(d.values()))
print("max fanout",max((len(g.children(n)),n) for n in nodes))
nr=[n for n in nodes if g.node(n).kind=="T1" and not g.children(n)];print("T1 leaf (no child)",nr)

un=[t for t in g.collections() if not [n for n in g.lineage_forward("T1:"+t) if g.node(n).kind=="T3"]]
print("tables no plot reads",un)
print("T2 read by plot",sum(1 for n in nodes if g.node(n).kind=="T2" and g.node(n).read_by_plot))
print("T2 not read",[n for n in nodes if g.node(n).kind=="T2" and not g.node(n).read_by_plot][:30])
print("collections",len(g.collections()))
print("descendants of T1:ResFinder",[n for n in g.lineage_forward("T1:ResFinder")])
print("back of a plot", g.lineage_back("T3:"+g.plots()[0]), g.plots()[:3])
print({n:len(g.lineage_forward(n)) for n in nodes if g.node(n).kind=='T1'})
