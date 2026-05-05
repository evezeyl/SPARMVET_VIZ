# Testing the different UI personas

## Simple: pipeline-static

```bash
# 1. Environment variables set the UI Profile and Backend
# 2. PYTHONPATH ensures all modular libraries and the app package are discovered
# 3. Running via 'shiny run' to activate the reactive dashboard

SPARMVET_PERSONA=pipeline-static \
SPARMVET_CONNECTOR=local \
PYTHONPATH=.:libs/ingestion/src:libs/transformer/src:libs/utils/src:libs/viz_factory/src \
./.venv/bin/python -m shiny run app/src/main.py
```

## Superuser persona

```bash
PYTHONPATH=libs/utils/src:libs/transformer/src:libs/ingestion/src:libs/viz_factory/src ./.venv/bin/python /tmp/test_nested_plot.py
```
