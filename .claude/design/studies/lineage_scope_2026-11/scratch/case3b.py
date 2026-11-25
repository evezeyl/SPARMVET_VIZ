exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings; warnings.filterwarnings("ignore")
from collections import Counter
for c in ("gene","identity","country","sample_id","ResFinder_not_in_original_data","year"):
    pres=G.column_presence(c); print(c, Counter(pres.values()))
    print("   unknown at:",[k for k,v in pres.items() if v not in ("present","absent")][:6] if True else "")
print("nodes with unknown columns:",len(G.nodes_with_unknown_columns()),"of",len(G.nodes()))
print(G.column_info("T1:ResFinder"))
print(G.column_info("T1:ST22_Anchor"))
fr,_=quiet(build,audit([("T2:ResFinder",{"action":"polars_drop","columns":["gene"]})]),Path("tmpAI/panel/lineage_scope/scratch/out_c3b"))
print("amr_heatmap columns after drop gene at T2:",fr["T3:amr_heatmap"].columns, "| plot mapping columns:",G.plot_columns("amr_heatmap"))
