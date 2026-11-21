# copied unchanged on 2026-11-21 from tmpAI/panel/test_lab_review/run1.py of the main tree (not in git; file dated 2026-11-18); a run of the earlier review, not a decision
import zipfile, io, sys, pathlib
from app.modules.test_lab_studio import scaffold_from_uploads
up = pathlib.Path('tmpAI/panel/test_lab_review/up')
(up/"0.tsv").write_text("Sample ID\tspecies\n007\tE. coli\n008\tS. aureus\n009\tE. coli\n")
(up/"1.tsv").write_text("sample_id\tgene\n007\tblaTEM\n007\ttetA\n009\tsul1\n")
(up/"2.tsv").write_text("sample_id,gene\n7,a\n8,b\n")   # comma file given a tsv reader
infos=[{"name":"isolates.tsv","datapath":str(up/"0.tsv")},{"name":"amr results.tsv","datapath":str(up/"1.tsv")}]
for jk in ["sample_id","Sample ID"]:
    zb = scaffold_from_uploads(infos,"proj",jk)
    out = pathlib.Path('tmpAI/panel/test_lab_review'+'/out_'+jk.replace(" ","_")); 
    zipfile.ZipFile(io.BytesIO(zb)).extractall(out)
    print(jk, sorted(n for n in zipfile.ZipFile(io.BytesIO(zb)).namelist()))
