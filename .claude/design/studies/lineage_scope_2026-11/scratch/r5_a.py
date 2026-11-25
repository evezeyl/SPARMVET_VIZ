from r5_lib import *
schemas=[t for t in G.collections() if G.node("T1:"+t).collection_kind=="schema"]
# forth: which originals feed what
for t in schemas:
    f=G.lineage_forward("T1:"+t)
    print(f"{t:28s} plots_below={len(plots_below(G,['T1:'+t]))} nodes_below={len(f)}")
data=[t for t in schemas if t not in ("metadata_schema","APEC_STEC_virulence_genes")]
print("E rows per original T1:",{t:has(base["T1:"+t]) for t in schemas})
print("E in T1 of non-schema:",{k:has(v) for k,v in base.items() if k.startswith("T1:") and k[3:] not in schemas})
# sets
sets={"all12data":["T1:"+t for t in data],"all12data+metadata":["T1:"+t for t in schemas if t!="APEC_STEC_virulence_genes"]}
for name,pl_ in sets.items():
    realplace(G,pl_)
    fr=run([(p,STEP) for p in pl_],name)
    print("\n###",name,"derived:",len(G.derived_places(pl_)))
    chg=[k for k in fr if dg(fr[k])!=bh[k]]; print("nodes differ",len(chg),"of",len(fr))
    print("plots with E base->after:")
    for p in G.plots():
        k="T3:"+p; print(f"  {p:34s} {has(base[k])}->{has(fr[k])}  rows {base[k].height}->{fr[k].height}")
    print("T1 tables (non schema) with E:")
    for t in G.collections():
        if t in schemas: continue
        b,a=has(base["T1:"+t]),has(fr["T1:"+t]); marker=[c for c in fr["T1:"+t].columns if c.endswith("_not_in_original_data")]
        print(f"  {t:36s} {b}->{a} markers {marker} E-rows-marked={fr['T1:'+t].filter(pl.col('sample_id')==E).select(marker).rows() if (a and marker) else '-'}")
