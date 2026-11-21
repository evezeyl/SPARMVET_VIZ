# copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/arch_check2.py of the main tree (not in git; written 2026-11-21 night by a step 4 viewpoint of this review); a probe, not a decision
import hashlib, io
from test_lab.aqua_synthesizer import AquaSynthesizer
s = AquaSynthesizer()
cfg = s.propose_config(["sample_id","species","n_reads"], n_rows=50, mode="stress_test")
cfg["error_injection"]["duplicate_ids"] = {"rate":0.1}
df = s.generate(cfg, seed=7)
print(hashlib.sha256(df.write_csv(separator="\t").encode()).hexdigest()[:16])
