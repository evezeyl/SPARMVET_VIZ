# ensures that user-uploaded metadata never breaks 
# the app. It uses a **Namespacing** strategy.

import polars as pl

def sanitize_and_join(bio_df: pl.DataFrame, user_df: pl.DataFrame, join_key: str = "sample_id"):
    """
    Ensures bio-data and user-data can coexist without column name collisions.
    """
    # 1. Prefix Bio-Data to protect internal variables
    # Ex: 'serotype' -> 'bio_serotype'
    bio_df = bio_df.rename({col: f"bio_{col}" for col in bio_df.columns if col != join_key})
    
    # 2. Identify Collisions in User Data
    # If user uploaded a 'bio_...' column, we rename it to protect our namespace
    user_renames = {col: f"user_{col}" for col in user_df.columns if col.startswith("bio_")}
    user_df = user_df.rename(user_renames)
    
    # 3. The 'Strict' Join
    # We use an 'inner' join to ensure we only plot samples that exist in both
    final_df = bio_df.join(user_df, on=join_key, how="inner")
    
    return final_df

import pandas as pd

def validate_metadata(df, schema_config):
    """
    The 'Strict Doorman' logic.
    df: The uploaded metadata (pandas DataFrame)
    schema_config: The 'fields' section from your species.yaml
    """
    errors = []
    
    # 1. Check for Mandatory Columns
    for field_name, rules in schema_config.items():
        if rules.get('mandatory', False) and field_name not in df.columns:
            errors.append(f"CRITICAL: Missing mandatory column: '{field_name}'")
            continue
        
        # 2. If column exists, check the values
        if field_name in df.columns:
            # Check for allowed options (The 'Strict' part)
            if 'options' in rules:
                allowed = rules['options']
                # Find values not in the allowed list
                invalid_rows = df[~df[field_name].isin(allowed)].index.tolist()
                for row in invalid_rows:
                    bad_val = df.loc[row, field_name]
                    errors.append(f"Row {row+2}: '{field_name}' has invalid value '{bad_val}'. Expected: {allowed}")

            # Check for Date Formats
            if rules.get('type') == 'date':
                try:
                    pd.to_datetime(df[field_name], format=rules.get('format'))
                except Exception:
                    errors.append(f"Column '{field_name}': Some dates do not match format {rules.get('format')}")

    # Return results
    is_valid = len(errors) == 0
    return is_valid, errors 
# Placeholder — extend to: data type transformation, minimal required column check,
# strip formatting errors (whitespace, Windows line endings), and surface failures via
# PipelineError (see ADR-079) rather than bare return values.




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manual execution hook for testing.")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    args = parser.parse_args()
    if args.test:
        print(f"Executing {__file__} in test mode.")
