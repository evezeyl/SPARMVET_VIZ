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


#TODO this should be expended to do maybe some : data type transformation / check for minimal set of required columns
# TODO in case of failure (joint, reading data) : it should inform
# TODO it should remove formatting errors eg space, windows characters osv 