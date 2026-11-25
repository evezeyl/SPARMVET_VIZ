exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings; warnings.filterwarnings("ignore")
M="ResFinder_not_in_original_data"; M2="metadata_schema_not_in_original_data"
for m in (M,M2):
    pres=G.column_presence(m)
    real={k for k,v in base.items() if m in v.columns}
    wrong=[k for k,v in pres.items() if k in real and v=="no"]
    print(m,"walk says no but table holds it:",wrong[:8],len(wrong),"| walk says yes:",[k for k,v in pres.items() if v=="yes"][:5])
# general: walk 'yes'/'no' vs reality for all columns
bad=0;tot=0;unk=0
for k,v in base.items():
    if not G.has_node(k): continue
    ci=G.column_info(k)
    if ci.names is None: unk+=1; continue
    tot+=1
    if set(ci.names)!=set(v.columns): bad+=1; print("  MISMATCH",k,sorted(set(ci.names)^set(v.columns))[:4])
print("nodes with known walk:",tot,"mismatch with real table:",bad,"unknown:",unk)
