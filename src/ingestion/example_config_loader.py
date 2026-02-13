import yaml
import polars as pl

class ConfigLoader:
    def __init__(self, config_path="config/species_rules.yaml"):
        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

    def get_species_logic(self, species_name: str, category: str):
        """Returns the specific columns and plot type for a species/category combo."""
        species_data = self._config.get(species_name, {})
        category_data = species_data.get("categories", {}).get(category, {})
        
        return {
            "columns": category_data.get("columns", []),
            "plot_type": category_data.get("plot_type", "default_bar"),
            "display_name": category_data.get("display_name", category)
        }

# Usage Example:
# loader = ConfigLoader()
# amr_info = loader.get_species_logic("E_coli", "AMR")
# print(amr_info["columns"]) -> ["bla_CTX-M", "ndm-1", "tetA"]