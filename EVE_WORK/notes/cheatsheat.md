
# Launching the app with a persona

Set `SPARMVET_PERSONA` to the persona ID before starting the app.

> **`SPARMVET_PERSONA` accepts a file path OR a shortname.**
> Path: `SPARMVET_PERSONA=/path/to/my_persona.yaml` → loaded directly (any location).
> Shortname: `SPARMVET_PERSONA=developer` → `config/ui/templates/developer_template.yaml` (backward compat).
> UI shows `display_name` from the config file, not the path.
> Terminal prints the resolved absolute path at startup — use that to confirm which file was loaded.
> Full reference: `docs/reference/environment_variables.qmd` | ADR-054 in architecture_decisions.md

```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
export PYTHONPATH=$ROOT:$PYTHONPATH

# ── Dev / analysis personas (use local dev profile — data via manifest source.path) ──

# Full-access developer mode (Blueprint Architect, Gallery, all tiers, session mgmt, Test Lab)
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8004

# Project-independent user (T3 audit, Gallery, session mgmt, export — no Blueprint, no Test Lab)
SPARMVET_PERSONA=$ROOT/config/ui/templates/project-independent_template.yaml \
  $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8005

# Advanced exploration (T3 audit, session mgmt, metadata upload — no Blueprint, no Gallery)
SPARMVET_PERSONA=$ROOT/config/ui/templates/pipeline-exploration-advanced_template.yaml \
  $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8001

# QA / Test Harness: every flag ON, ghost_save OFF — use for Playwright smoke tests
SPARMVET_PERSONA=$ROOT/config/ui/templates/qa_template.yaml \
  $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8001

# ── Pipeline personas (use pipeline_test_profile — data injected by connector, not manifest) ──
# prefer_discovery=true: ingestor finds files by schema ID name in raw_data_dir.
# Mirrors production Galaxy/IRIDA behaviour. Test data: duplicated_1_test_data_ST22_dummy/

# Simple exploration (T1/T2 filter scratchpad — no T3 audit, no Gallery, no upload)
SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/pipeline-exploration-simple_template.yaml \
  $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8001

# DEMO ! Static pipeline (read-only — export bundle only, no interactivity, no session mgmt)
SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/pipeline-static_template.yaml \
  $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8003

# ── Demo personas (NVI banner, no import/export panels, no persona badge) ──

# DEMO ! VetInst branded demo (NVI colours + logo, no badge, no data import, no export)
SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/demo-vetinst_template.yaml \
  $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8002

# OK - BUT css bad ... Web demo (clean exploration view - simple)
SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/web-demo_template.yaml \
  $ROOT/.venv/bin/python -m shiny run $ROOT/app/src/main.py --port 8001


# ── Headless connector test (debug before launching UI) ──
PYTHONPATH=$ROOT $ROOT/.venv/bin/python app/tests/debug_pipeline_connector.py
```

## Persona capability matrix (updated ADR-052, 2026-05-01)

| Persona | T3 audit | Blueprint | Gallery | Test Lab | Session mgmt | Export bundle | Export graph | Metadata upload | Data ingestion |
|---|---|---|---|---|---|---|---|---|---|
| `developer` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `project-independent` | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `pipeline-exploration-advanced` | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `pipeline-exploration-simple` | passive only | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `pipeline-static` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `qa` (test harness) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `demo-vetinst` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `web-demo` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

> **passive only**: T1/T2 filter scratchpad — plot updates temporarily, nothing saved, no audit trail. No T3 right sidebar.
> **Test Lab** = canonical name (formerly "Developer Studio"). Nav pill + banner heading both updated (ADR-056, 2026-05-02). Python module stays `dev_studio.py`.
> **Gallery** now enabled for `project-independent` (ADR-052, 25-A config change).
> **Export bundle** — full ZIP with all plots + T1/T2/T3 data + manifest + Quarto report + T3 audit trail + t3_steps.yaml + filters trace. 3-way scope toggle: Global project / Active group / Active plot. Single Graph Export accordion removed (2026-05-04 redesign) — use "Active plot" scope instead.
---

# Tests

```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
export PYTHONPATH=$ROOT:$PYTHONPATH
```

# Env

[Plotnine version 0.15.3](https://plotnine.org/)

```bash
#python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install polars numpy pyyaml

python3 -m venv .venv && source .venv/bin/activate
source .venv/bin/activate
python3 -m venv .venv && source .venv/bin/activate

# From any other location ...
source /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.venv/bin/activate
```

### Launching the ui app

export PYTHONPATH=.:$PYTHONPATH && ./.venv/bin/python -m shiny run app/src/main.py

### Viewing parquet files

./.venv/bin/python -c "import polars as pl; print(pl.read_parquet('tmp/session_anchor_test.parquet').glimpse())"

- export to tsv
./.venv/bin/python -c "import polars as pl; pl.read_parquet('tmp/session_anchor_test.parquet').write_csv('tmp/FULL_EXPORT_debug.tsv', separator='\t')"

To check if the file exists and its shape: ls -lh tmp/*.parquet && ./.venv/bin/python -c "import polars as pl; print(pl.read_parquet('tmp/session_anchor_test.parquet').shape)"

To view the full content (TSV):  ./.venv/bin/python -c "import polars as pl; pl.read_parquet('tmp/session_anchor_test.parquet').write_csv('tmp/USER_FULL_VIEW.tsv', separator='\t')"

### Cleaning and reinstalling python env

1. Clean

```bash
# Kill any lingering Python/Pip processes
pkill -9 python
pkill -9 pip
# Remove the broken venv and all legacy build metadata
rm -rf .venv/
rm -rf libs/*/*.egg-info
rm -rf libs/*/build/
rm -rf libs/*/dist/
```

1. create and insall

```bash
# Create the environment
python3 -m venv .venv

# Upgrade foundational build tools first
./.venv/bin/python -m pip install --upgrade pip setuptools wheel

# Install all libraries in editable mode
./.venv/bin/pip install -e libs/transformer/ \
                       -e libs/viz_factory/ \
                       -e libs/ingestion/ \
                       -e libs/connector/ \
                       -e libs/utils/ \
                       -e libs/generator_utils/
```

1. Control

``` bash
# Check if the package is importable and pointing to the correct physical path
./.venv/bin/python -c "import transformer; print(f'Success: {transformer.__file__}')"

# Run the automated suite to verify all 21+ actions
./.venv/bin/python libs/transformer/tests/transformer_integrity_suite.py
```

### Killing python process running in the environment

```bash
# This shows all python processes running from your .venv
ps aux | grep .venv

# To kill all python processes in one go (be careful if you have other apps running)
pkill -f python
```

If the IDE Agent is reporting "stuck terminals," it might be a socket or lock file in the Antigravity config directory.

Check for Locks: Look in ~/.config/Antigravity/ for any .lock or .socket files that might be lingering from a crashed session.

Clean tmp/: Since we are starting the "Triple-Threat" recipe, manually wipe your local tmp/ directory to ensure no old file-locks exist:

```bash
cd .config/Antigravity 
# Find all files ending in .lock in the config directory
find ~/.config/Antigravity -name "*.lock"

# Alternatively, check for files with .tmp extension
find ~/.config/Antigravity -name "*.tmp"

#rm -rf ./tmp/*
```

## Preparing prompt context for AI : repomix

```bash
DATE_LOG=$(date +%Y-%m-%d)
cd /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/EVE_WORK/daily/$DATE_LOG

bash /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/EVE_WORK/scr/SPARMVET_GEM_context.sh
```

## Testing wrangling and assembly from manifest

```bash
./.venv/bin/python libs/transformer/tests/assembler_debug.py \
  --manifest [PATH_TO_MANIFEST] \
  --data [PATH_TO_ASSETS_DIR] \
  --output [PATH_TO_RESULT]


./.venv/bin/python libs/transformer/tests/assembler_debug.py \
  --manifest config/manifests/pipelines/Abromics_Resistence_pipeline.yaml
```

## Creating manifests from data

For a single file

./.venv/bin/python ./assets/scripts/SF_create_manifest.py \
  --data ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv \
  --output tmp/EVE_manifest.yaml

```

For many files in a directory 

```bash
# Update the command 
./.venv/bin/python ./assets/scripts/create_manifest.py \
  --data ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv \
  --output tmp/EVE_manifest.yaml
```

## Testing manifests

- virulence finder - reference data

```bash
./.venv/bin/python ./libs/transformer/tests/test_wrangler.py \
  --data ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv \
  --manifest ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_manifest.yaml \
  --output tmp/EVE_TEST.tsv
```

```bash
./.venv/bin/python ./libs/transformer/tests/test_wrangler.py \
  --data ./assets/test_data/2_VIGAS-P/VIGAS_VirulenceFinder/VIGAS_VirulenceFinder_test.tsv \
  --manifest ./config/manifests/VIGAS-P/VIGAS_VirulenceFinder.yaml \
  --output tmp/EVE_TEST.tsv
```

## Gettin logs - if seems to hang

ls -la /home/evezeyl/.config/Antigravity/logs/

- check the directory then
 tail -f /home/evezeyl/.config/Antigravity/logs/$(date)*/rendererPerf.log

# REPMIX extracting info

cd ./EVE_WORK/reference/
distrobox enter repomix-env --name repomix-env --no-tty -- repomix --include "plotnine/geoms/*.py,plotnine/stats/*.py,plotnine/scales/*.py,plotnine/themes/*.py,plotnine/facets/*.py,plotnine/coords/*.py,plotnine/positions/*.py" --output plotnine_api_context.md

# The Distinction: Indexing vs. Reading

to use `.aiignore` (embedding) to save your tokens while keeping the agent fully functional.

| **Action**               | **Controlled by .aiignore?** | **Token Cost**     | **When it happens**                  |
| ------------------------ | ---------------------------- | ------------------ | ------------------------------------ |
| **Embedding (Indexing)** | **YES**                      | Background/Storage | Proactively, to "learn" the project. |
| **Direct Reading**       | **NO**                       | Active Context     | Only when you say "Read this file."  |
| **Writing (Output)**     | **NO**                       | Generation         | When the agent creates code or logs. |


## Test command reference

> **Preamble** — run once per terminal session before any command below:
> ```bash
> ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
> export PYTHONPATH=$ROOT:$PYTHONPATH
> ```

---

### T0 — App import check (~1s)
No persona needed. Confirms Python path and imports are intact.
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT \
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python -c "from app.src.main import app; print('app import: OK')"
```

---

### T1 — Unit tests / pytest baseline (~2s, run before every commit)
No profile, no persona. Safe baseline — skips broken libs.
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT $ROOT/.venv/bin/python -m pytest \
  app/tests/test_filter_operators.py \
  libs/connector/tests/ \
  libs/viz_factory/tests/test_deco2_components.py \
  -q
```
Expected: **90/90 pass**.
> Do NOT use `pytest libs/ app/tests/ -q` — hits broken libs and reports spurious failures.

---

### T2 — Headless connector test — pipeline personas (~2s)
Verifies production connector path (prefer_discovery) before launching the UI.
Profile: pipeline_test | Persona: pipeline-static
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT \
SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/pipeline-static_template.yaml \
  $ROOT/.venv/bin/python app/tests/debug_pipeline_connector.py
```
Expected: **9 pass, 0 warn, 0 fail** — 12/12 schemas discovered, anchor assembled.

---

### T3 — Headless home theater — dev mode (~3s)
Profile: local dev (default) | Persona: developer
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT \
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python app/tests/debug_home_theater.py
```

---

### T4 — Playwright smoke tests — headless browser (~35s)
Profile: local dev (default) | Persona: qa (all flags ON, ghost_save OFF)
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT \
SPARMVET_PERSONA=$ROOT/config/ui/templates/qa_template.yaml \
  $ROOT/.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v
```
Expected: **10 pass, 2 skip** (Gallery tests skipped — correct for non-developer persona).
Covers: app startup, persona masking, filter pipeline (T1/T2), data grid.

---

### T5 — Session ghost flow (~2s)
Profile: local dev (default) | Persona: developer
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT \
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python app/tests/debug_session_flow.py
```

---

### T6 — Long: viz_factory integrity suite (renders all *_test.yaml → PNG)
Profile: local dev (default) | Persona: developer
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT \
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python libs/viz_factory/tests/viz_factory_integrity_suite.py \
  --output_dir tmp/viz_factory/
```

---

### T7 — Long: transformer integrity suite (all manifest+TSV through wrangler/assembler)
Profile: local dev (default) | No persona needed
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT \
  $ROOT/.venv/bin/python libs/transformer/tests/transformer_integrity_suite.py \
  --output_dir tmp/transformer/
```

---

### Demo-readiness check — T0 + T1 + T4 in sequence
Safe to push if all three pass.
```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
PYTHONPATH=$ROOT \
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python -c "from app.src.main import app; print('app import: OK')" && \
PYTHONPATH=$ROOT $ROOT/.venv/bin/python -m pytest \
  app/tests/test_filter_operators.py \
  libs/connector/tests/ \
  libs/viz_factory/tests/test_deco2_components.py \
  -q && \
PYTHONPATH=$ROOT \
SPARMVET_PERSONA=$ROOT/config/ui/templates/qa_template.yaml \
  $ROOT/.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -q
```

