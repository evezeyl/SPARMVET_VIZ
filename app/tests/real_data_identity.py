"""The identity of the data the browser test app really opens, computed the way the app computes it (one helper for the browser tests that seed sessions).

G1 guard (Eve 2026-11-28): a Restore is refused unless the session was made on the data now on disk, so a seeded session must carry the REAL per-file
hashes. `data_identity(recipe_id)` returns `(data_batch_hash, source_files)` where `source_files` is `{table: path}`: the files `DataOrchestrator.get_source_files`
finds for the recipe (the call `_sync_session_provenance` makes) and the hash `batch_hash_of(dataset_file_hashes(...))` (the same call). Used only in the test process:
the bootloader and the deployment are the ones of the test app.
"""
from pathlib import Path


def data_identity(recipe_id: str) -> tuple[str, dict[str, str]]:
    from app.modules.cache_keys import batch_hash_of, dataset_file_hashes
    from app.modules.orchestrator import DataOrchestrator
    from app.src.bootloader import bootloader
    orchestrator = DataOrchestrator(
        data_analysis_recipes_dir=bootloader.get_location("data_analysis_recipes"),
        raw_data_dir=bootloader.get_location("raw_data"),
        data_lookup=bootloader.data_lookup,
        imports_dir=bootloader.get_imports_dir(),
    )
    files = orchestrator.get_source_files(recipe_id)
    return batch_hash_of(dataset_file_hashes(files)), {k: str(Path(v)) for k, v in files.items()}
