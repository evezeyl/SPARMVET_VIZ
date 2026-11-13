# --- Auto-Load Strategy ---
# We explicitly import the sub-packages here.
# Importing them executes their code, which triggers the @register_action decorators
# defined in base.py, safely populating the AVAILABLE_WRANGLING_ACTIONS dictionary
# at system boot-up.
from transformer.actions import reshaping
from transformer.actions import cleaning
from transformer.actions import relational
from transformer.actions import persistence
from transformer.actions import performance
from transformer.actions import polars_calls  # noqa: F401  (the polars_ actions, W6)
from transformer.actions import modified  # noqa: F401  (the modif_ actions, W6)
from transformer.actions import composite  # noqa: F401  (the step_ actions, W6)
