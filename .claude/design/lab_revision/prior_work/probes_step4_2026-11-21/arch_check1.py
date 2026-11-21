# copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/arch_check1.py of the main tree (not in git; written 2026-11-21 night by a step 4 viewpoint of this review); a probe, not a decision
import random, numpy as np, polars as pl
from test_lab.aqua_synthesizer import AquaSynthesizer
from ingestion.declared import apply_declared
s = AquaSynthesizer()
cfg = s.propose_config(["sample_id","species","n_reads"], n_rows=20, mode="stress_test")
print([ (c["name"],c.get("dtype"),c.get("is_pk")) for c in cfg["columns"]])
cfg["error_injection"]["wrong_type"] = {"rate":0.3,"columns":["n_reads"]}
cfg["error_injection"]["missing_values"] = {"rate":0.2,"columns":["species"]}
a = s.generate(cfg, seed=7); b = s.generate(cfg, seed=7)
print("same seed equal:", a.equals(b))
c = s.generate(cfg); d = s.generate(cfg)
print("no seed equal:", c.equals(d))
# global state side effect
random.seed(1); x = random.random(); random.seed(1)
s.generate(cfg, seed=7); y = random.random()
print("global random state changed by generate(seed):", x != y)
# what the recipe's ingestion says about the stress file
lf = a.with_columns(pl.all().cast(pl.String)).lazy()
schema = {"null_values": [], "strip": True}
fields = {"sample_id":{"type":"String"},"species":{"type":"String"},"n_reads":{"type":"Int64"}}
try:
    apply_declared(lf, "t", schema, fields); print("ingestion accepted")
except Exception as e:
    print("ingestion refused:", str(e)[:200])
print(a["n_reads"].to_list()[:10])
