# copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/arch_check5.py of the main tree (not in git; written 2026-11-21 night by a step 4 viewpoint of this review); a probe, not a decision
import polars as pl, io, contextlib
from utils.recipe_loader import load_recipe
from ingestion.declared import apply_declared
from transformer.metadata_validator import MetadataValidator
from ingestion.ingestor import DataIngestor
rec,_ = load_recipe("config/data_analysis_recipes/templates/simple_template.yaml")
s = rec["data_schemas"]["primary_data"]; f = s["input_fields"]
def lf(h): return pl.LazyFrame({h[0]:["S1","S2"],h[1]:["1.5","2.5"],h[2]:["A","B"]})
for label, hdr in (("original headers (ID,Measurement,Group)", ["ID","Measurement","Group"]), ("slug headers (sample_id,value,group)", ["sample_id","value","group"])):
    d = lf(hdr)
    try: MetadataValidator().validate(d, f, "[t]"); a="Data Import check: accepted"
    except Exception as e: a="Data Import check: REFUSED"
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            DataIngestor._import_declared_columns(DataIngestor.__new__(DataIngestor), d, "primary_data", f); 
        b="ingestor strict import: accepted"
    except Exception as e: b="ingestor strict import: REFUSED"
    print(label, "|", a, "|", b)
