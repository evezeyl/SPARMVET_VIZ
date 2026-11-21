# copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/arch_check4.py of the main tree (not in git; written 2026-11-21 night by a step 4 viewpoint of this review); a probe, not a decision
import polars as pl
from utils.recipe_loader import load_recipe
from ingestion.declared import apply_declared
from transformer.metadata_validator import MetadataValidator
rec,_ = load_recipe("config/data_analysis_recipes/templates/simple_template.yaml")
s = rec["data_schemas"]["primary_data"]; f = s["input_fields"]
lf = pl.scan_csv("tmpAI/panel/lab_step4/simple_data.tsv", separator="\t", infer_schema=False)
try:
    MetadataValidator().validate(lf, f, context="[primary_data]"); apply_declared(lf,"primary_data",s,f); print("DI check: accepted")
except Exception as e:
    print("DI check refused the file the recipe itself reads:", str(e)[:160])
