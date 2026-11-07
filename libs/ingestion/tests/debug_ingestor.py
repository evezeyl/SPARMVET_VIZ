#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# ADR-016: Use Package-First Authority (Editable Installs)
project_root = Path(__file__).resolve().parent.parent.parent.parent
# if str(project_root) not in sys.path:
# STRICT BAN: sys.path.append / sys.path.insert are explicitly forbidden. Rely on pip install -e.

try:
    from ingestion.ingestor import DataIngestor
    from utils.config_loader import ConfigManager
except ImportError as e:
    print(f"❌ ERROR: Ingestion imports failed. Check .venv install. {e}")
    sys.exit(1)


def test_ingestion(data_analysis_recipe_path: str, data_dir: str):
    """
    A developer utility for the Ingestion layer. 
    It tests loading data from disk and comparing raw columns to the declared _fields schema.
    It DOES NOT execute data wrangling (Transformer layer).
    """
    print(f"\n[{'*'*40}]")
    print(f" TESTING INGESTION LAYER")
    print(f"[{'*'*40}]\n")

    try:
        config = ConfigManager(data_analysis_recipe_path)
    except Exception as e:
        print(f"❌ Failed to load data analysis recipe configuration: {e}")
        sys.exit(1)

    schemas = config.get_data_schemas()
    if not schemas:
        print("❌ No 'data_schemas' found in the configuration.")
        sys.exit(1)

    try:
        ingestor = DataIngestor(data_dir)
    except Exception as e:
        print(f"❌ Failed to initialize DataIngestor: {e}")
        sys.exit(1)

    for dataset_name, definitions in schemas.items():
        print(f"\n[{dataset_name.upper()}]")

        # 1. Use the official Ingestor to load the data
        try:
            lf, tsv_path = ingestor.ingest(dataset_name, definitions)
            print(f"  └── 📥 Successfully ingested {tsv_path.name}")
        except FileNotFoundError as e:
            print(f"  └── ⚠️ {e}")
            continue
        except Exception as e:
            print(f"  └── ❌ {e}")
            continue

        # ADR-013: Map and validate against 'input_fields'
        fields_schema = definitions.get(
            "input_fields") or definitions.get("fields") or {}
        raw_cols = lf.columns
        print(
            f"  └── Found {len(raw_cols)} columns on disk vs {len(fields_schema)} declared in YAML.")

        # 3. Preview Data (Raw)
        print("\n  [RAW INGESTED PREVIEW:]")
        print(lf.head(5).collect())
        print("\n" + "-"*40)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Dashboard Ingestion.")
    parser.add_argument("--yaml", type=str, required=True,
                        help="Path to the master data analysis recipe YAML file.")
    parser.add_argument("--data", type=str, required=True,
                        help="Path to the folder containing the raw TSV files.")

    args = parser.parse_args()
    test_ingestion(args.yaml, args.data)
