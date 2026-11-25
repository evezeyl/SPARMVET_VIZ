import json
from utils.recipe_graph import build_graph
from app.modules.cache_keys import load_data_analysis_recipe as load
g=build_graph(load('config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml').raw)
nodes=[{"id":n,"kind":g.node(n).kind,"name":g.node(n).name,"read":g.node(n).read_by_plot} for n in g.nodes()]
json.dump({"nodes":nodes,"edges":[list(e) for e in g.edges()]},open('tmpAI/panel/lineage_scope/scratch/real_graph.json','w'),indent=1)
print(len(nodes))
# subset: around ResFinder, MLST, metadata
keep=set()
for s in [n for n in g.nodes() if g.node(n).name in("ResFinder","MLST","metadata_schema")]:
    keep|={s}|set(g.lineage_back(s))
print(sorted(g.node(n).name+":"+g.node(n).kind for n in g.nodes() if g.node(n).kind=="DS"))
print([ (n) for n in g.nodes() if g.node(n).kind=="T3"])
print([n for n in g.nodes() if g.node(n).kind=="T1" and g.node(n).collection_kind=="join"])
