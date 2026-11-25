exec(open("tmpAI/panel/lineage_scope/scratch/cases.py").read())
import warnings; warnings.filterwarnings("ignore")
M="ResFinder_not_in_original_data"
neg=base["T1:ResFinder"].filter(pl.col(M))["sample_id"].to_list(); print("4 completed (no ResFinder line) entities:",neg)
STEP={"action":"modif_filter","column":M,"op":"eq","value":False,"na":"keep"}
for place in ("T1:ResFinder","T2:ResFinder","T3:amr_heatmap","T1:ResFinder_with_metadata","T1:ST22_Anchor"):
    r=run(f"remove completion lines at {place}",[(place,STEP)],"c4_"+place.replace(":","_"))
    if not r: continue
    fr,ch=r
    for k in ("T1:ResFinder","T1:ResFinder_with_metadata","T3:amr_heatmap","T1:QA_AMR_per_sample","T3:qa_amr_genes_per_sample","T3:qa_fanout_rows_per_sample","T3:virulence_bar"):
        b,a=base[k],fr[k]; print(f"   {k:34s} rows {b.height}->{a.height} ents {ents(b)}->{ents(a)}")
    if "T3:qa_amr_genes_per_sample" in ch:
        a=fr["T3:qa_amr_genes_per_sample"]; b=base["T3:qa_amr_genes_per_sample"]
        print("   n_amr_genes for the 4:", b.filter(pl.col('sample_id').is_in(neg)).select('n_amr_genes').to_series().to_list() if 'sample_id' in b.columns else b.columns, "->", a.filter(pl.col('sample_id').is_in(neg)).select('n_amr_genes').to_series().to_list() if 'sample_id' in a.columns else a.columns)
