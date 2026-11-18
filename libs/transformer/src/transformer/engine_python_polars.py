"""The entry of the data engine `python-polars`: the one small file that names the engine and exposes `ENTRY` (D-0247).

The app (`app/modules/engine_registry.py`) imports this file and nothing else of the library to choose the engine of a tier:
`ENTRY.wrangler` runs a list of steps and reads the steps of a tier, `ENTRY.assembler` assembles a join. The code of the engine
stays where it is (`data_wrangler.py`, `data_assembler.py`, `actions/`); a second engine is its own library with a file of the
same kind. The libraries do not import each other, so this file imports only this library and the names of `utils.engines`.

Consumed by: `app/modules/engine_registry.py`. If deleted: the app has no data engine and refuses every recipe at the first tier.

# @deps
# provides: constant:ENTRY, constant:ENGINE
# consumes: libs/utils/src/utils/engines.py (DATA_ENGINE, DataEngineEntry), libs/transformer/src/transformer/data_wrangler.py, libs/transformer/src/transformer/data_assembler.py
# consumed_by: app/modules/engine_registry.py, libs/transformer/tests/test_action_engine_field.py
# doc: .claude/knowledge/decision_ledger.md (D-0247)
# @end_deps
"""
from transformer.data_assembler import DataAssembler
from transformer.data_wrangler import DataWrangler
from utils.engines import DATA_ENGINE, DataEngineEntry

ENGINE = DATA_ENGINE
ENTRY = DataEngineEntry(engine=ENGINE, wrangler=DataWrangler, assembler=DataAssembler)
