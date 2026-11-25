from r5_lib import *
schemas=[t for t in G.collections() if G.node("T1:"+t).collection_kind=="schema"]
data=[t for t in schemas if t not in ("metadata_schema","APEC_STEC_virulence_genes")]
for drop in data:
    fr=run([("T1:"+t,STEP) for t in data if t!=drop],"n_"+drop)
    L={k:has(v) for k,v in fr.items() if has(v) and k.startswith("T3") or (has(v) and k[3:] not in schemas)}
    print(f"data12 minus {drop:22s}: figures still showing E: {[k[3:] for k in L if k.startswith('T3')]} ; derived tables {sorted({k[3:] for k in L if not k.startswith('T3')})}")
