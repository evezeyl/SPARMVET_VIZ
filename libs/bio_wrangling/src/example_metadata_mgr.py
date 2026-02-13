# Handles the "Data Contract" and join data_tier1 to metadata
# Returns data_tier2
import polars as pl

class MetadataManager:
    def __init__(self, bio_data: pl.DataFrame):
        self.bio_data = bio_data  # The 'reduced' data from Layer 1

    def join_and_filter(self, user_metadata: pl.DataFrame, species_filter: str):
        # 1. Validation: Ensure ID columns match
        # 2. Server-side join
        joined = self.bio_data.join(user_metadata, on="sample_id", how="inner")
        
        # 3. Server-side filter (The 'Scalability' part)
        return joined.filter(pl.col("species") == species_filter)