# copied unchanged on 2026-11-21 from tmpAI/panel/lab_step4/arch_check3.py of the main tree (not in git; written 2026-11-21 night by a step 4 viewpoint of this review); a probe, not a decision
from utils.recipe_loader import load_recipe
from pathlib import Path
p = Path("config/data_analysis_recipes/templates/simple_template.yaml")
rec, problems = load_recipe(p)
print("problems:", [str(x)[:80] for x in problems][:3])
for sid, s in rec["data_schemas"].items():
    print(sid, "null_values", s.get("null_values"), "strip", s.get("strip"), "src", s.get("source"))
    for f, d in list(s["input_fields"].items())[:5]:
        print("  ", f, d)
