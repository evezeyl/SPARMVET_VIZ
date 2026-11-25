exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings; warnings.filterwarnings("ignore")
lk=base["T1:APEC_STEC_virulence_genes"]; print(lk.columns, lk.height); print(lk.head(3))
col="Gene_name"; keep=lk[col].to_list()[:6]
STEP={"action":"modif_filter","column":col,"op":"in","value":keep,"na":"remove"}
r=run("keep only 6 of 11 look-up genes at T1:APEC_STEC_virulence_genes",[("T1:APEC_STEC_virulence_genes",STEP)],"c6")
if r:
    fr,ch=r
    for k in ch: 
        b,a=base[k],fr[k]; print(f"   {k:44s} rows {b.height}->{a.height} ents {ents(b)}->{ents(a)}")
