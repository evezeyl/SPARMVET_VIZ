from r5_lib import *
schemas=[t for t in G.collections() if G.node("T1:"+t).collection_kind=="schema"]
data=[t for t in schemas if t not in ("metadata_schema","APEC_STEC_virulence_genes")]
def left(fr): return {k:has(v) for k,v in fr.items() if has(v)}
def show(name,places):
    realplace(G,places); fr=run([(p,STEP) for p in places],name)
    L=left(fr); print(f"\n### {name}: nodes still holding E: {len(L)} of {len(fr)}")
    print("  T3:",{k:v for k,v in L.items() if k.startswith('T3')})
    print("  T1/T2 (non-original):",{k:v for k,v in L.items() if not k.startswith('T3') and k[3:] not in schemas})
    print("  originals T1:",{k:v for k,v in L.items() if k.startswith('T1') and k[3:] in schemas})
    return fr
show("data12",["T1:"+t for t in data])
show("data12+meta",["T1:"+t for t in data]+["T1:metadata_schema"])
show("metadata only",["T1:metadata_schema"])
# every original but ResFinder
show("data except ResFinder",["T1:"+t for t in data if t!="ResFinder"])
# E per original T1 and whether the completion line exists (marker True) for E in base
for t in data:
    df=base["T1:"+t]; m=[c for c in df.columns if c.endswith("_not_in_original_data")]
    print(t,"E rows",has(df),"E rows marked as added:",df.filter(pl.col("sample_id")==E).filter(pl.col(m[0])).height if m else None)
print("E in metadata T1 markers:",base["T1:metadata_schema"].filter(pl.col("sample_id")==E).select([c for c in base["T1:metadata_schema"].columns if c.endswith("not_in_original_data")]).rows())
