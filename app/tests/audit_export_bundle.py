import polars as pl
from app.modules.exporter import SubmissionExporter
from pathlib import Path
import zipfile
import yaml


def audit_export():
    print("--- 📦 Global Export Audit Simulation ---")
    exporter = SubmissionExporter("tmp/audit_exports")

    # 1. Mock Data
    tiers = {
        "tier1_anchor": pl.DataFrame({"id": [1], "val": ["A"]}).lazy(),
        "tier2_reference": pl.DataFrame({"id": [1], "val": ["A"]}).lazy(),
        "tier3_leaf": pl.DataFrame({"id": [1], "val": ["A"]})
    }

    data_analysis_recipe = {
        "data_analysis_recipe": "AUDIT_TEST",
        "plots": {"test_plot": {"mapping": {"x": "id"}, "layers": [{"name": "geom_point"}]}}
    }

    audit_trail = [
        "rename: Adjusted headers for clarity.",
        "filter: Removed control samples."
    ]

    # 2. Bundle
    zip_path = exporter.bundle_global_export(
        data_analysis_recipe_id="AUDIT_PROJ",
        plot_path="tmp/audit_plot.png",  # Simulated
        tiers={k: v.collect().to_pandas() if hasattr(v, "collect")
               else v.to_pandas() for k, v in tiers.items()},
        data_analysis_recipe=data_analysis_recipe,
        audit_trail=audit_trail
    )

    print(f"Zip created at: {zip_path}")

    # 3. Verify Contents
    print("\n--- 🔍 Verifying ZIP Contents ---")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        contents = zipf.namelist()
        for f in contents:
            print(f"  [FOUND] {f}")

        # Check audit log readability
        with zipf.open("audit_log.txt") as f:
            log_content = f.read().decode()
            print("\nAudit Log snippet:")
            print("-" * 20)
            print(log_content[:200])
            print("-" * 20)

        # Check data analysis recipe format
        with zipf.open("session_data_analysis_recipe.yaml") as f:
            man_content = yaml.safe_load(f)
            print(f"\nDataAnalysisRecipe: {man_content.get("data_analysis_recipe")}")


if __name__ == "__main__":
    # Create mock plot file
    Path("tmp/audit_plot.png").write_text("dummy plot")
    audit_export()
