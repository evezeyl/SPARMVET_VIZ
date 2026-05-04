# SPARMVET_VIZ — Demo Cheatsheet (2026-05-04)

```bash
ROOT=/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
export PYTHONPATH=$ROOT:$PYTHONPATH
```

---

## Pre-demo: launch all 3 instances

Open 3 terminals, run one per terminal, then load **1_test_data_ST22_dummy** in each before starting.

```bash
# ── Phase 1: NVI branded view (clean, no controls) ──────────────────────────
cd $ROOT && \
SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/demo-vetinst_template.yaml \
  $ROOT/.venv/bin/python -m shiny run app/src/main.py --port 8001

# ── Phase 2: Exploration + T3 sandbox ───────────────────────────────────────
cd $ROOT && \
SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/pipeline-exploration-advanced_template.yaml \
  $ROOT/.venv/bin/python -m shiny run app/src/main.py --port 8002

# ── Phase 3: Developer (all features) ───────────────────────────────────────
cd $ROOT && \
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python -m shiny run app/src/main.py --port 8003
```

*Note: Phase 1 & 2 use `pipeline_test_profile` (mirrors Galaxy/IRIDA — discovers data by schema ID). Phase 3 uses local dev profile (default).*

---

## URLs

| | URL | Notes |
|---|---|---|
| Phase 1 — NVI demo | http://localhost:8001 | NVI teal/gold banner, no controls |
| Phase 2 — Exploration | http://localhost:8002 | T3 sandbox, audit panel |
| Phase 3 — Developer | http://localhost:8003 | All features |
| Slides | `presentation/sparmvet_viz_demo_2026-05-04.html` | |
| Docs | `_book/index.html` | |
| Dep graph | `assets/dep_graph.html` | |

---

## Demo flow

### Phase 1 — Branding / static view (~3 min) → port 8001

**Goal:** show it can be adapted for any deployment context

- NVI banner: teal background, gold accent, "AMR Surveillance — Overview · Norwegian Veterinary Institute"
- Navigate between plot groups — everything renders, no sidebar controls visible
- *"This is what a Galaxy or IRIDA user sees. Same tool, YAML-configured skin. No code change."*
- Optional: show `assets/demo/demo_vetinst.css` — it's ~50 lines of CSS deltas on top of the base theme

---

### Phase 2 — Exploration + T1/T2/T3 (~12 min) → port 8002

**Slides on second screen: persona matrix (slide 4), then T1/T2/T3 (slide from Part B)**

**Open sidebar / show pipeline-exploration-advanced features:**
- Left sidebar: Manifest Choice, Filters, Global Project Export, Session Management visible
- Right sidebar: Pipeline Audit visible
- *Point to persona matrix: "this persona has T3 sandbox, session save, metadata upload — but no Gallery, no Test Lab"*

**T1 → T2 toggle:**
- Results → **MLST Bar** → toggle T1 ↔ T2
- Row count drops; `era` column appears
- *"T1 = raw pipeline output, persisted as Parquet on first load. T2 = analysis-ready — wrangling defined in the YAML manifest. Not in this UI."*

**T3 filters + propagation:**
- Filters accordion → column `year`, operator `gt`, value `2010` → Add Row
- Propagate → modal: which plots have `year` (✅ apply) vs. which don't (⚠️ skip)
- Confirm → compatible plots update
- Pipeline Audit right sidebar → add reason:
  *"Pre-2010 isolates sequenced under earlier QC protocol — excluded from prevalence trend"*
- *"This is your methods section. When you publish, the export bundle contains every decision + reasoning."*

**Export bundle:**
- Global Project Export accordion → Export ZIP
- *"T1/T2/T3 data TSVs + recipe YAML + audit trail + filter trace. The ZIP is a reproducible methods package."*

---

### Phase 3 — Developer (~8 min) → port 8003

**Gallery (finished — 34 recipes):**
- Gallery in left nav → 6-axis taxonomy sidebar (Family, Pattern, Difficulty, Geom, Show, Sample size)
- Filter: Distribution + 2 Categorical → show matching recipes
- Click a recipe → preview + guidance pane
- *"Community recipe library. A recipe added for one species pipeline is instantly available to all others."*

**Cat 🐱 / Miaou:**
- Project → Cat 🐱 group → Miaou → violin plot
- *"We added a cat group to the test data. Violin for the boss."*

**QC → Virulence Variants:**
- Quality Control → Virulence Variants dotplot
- *"This is the DEMO-1/2 proof — complex multi-source join, no Python written for this specific chart"*

**Blueprint Architect (in development):**
- Blueprint in sidebar → TubeMap rendering (ST22 lineage DAG)
- *"Visual manifest editor — in development. Goal: scientists wire new pipelines without writing YAML by hand."*
- *Honest: show it, note it's not finished*

**Test Lab (developer only):**
- Test Lab tab → AquaSynthesizer, registry
- *"This is where we test new plot types before adding them to the gallery"*

---

## Part B slides → for Q&A / second screen

Open slides and navigate to Part B (after demo slide):
- T1/T2/T3 data architecture
- Hash schema + reproducibility (SHA-256 cache invalidation)
- System architecture (4-layer mermaid)
- ST22 TubeMap
- How we build it (ADRs, rules, testing)
- Roadmap

---

## Pre-demo checklist (run the evening before)

```bash
cd $ROOT

# 1. Clear old parquet cache so T1 cold-start is visible on Phase 2
rm -f $ROOT/tmp/*.parquet

# 2. Smoke-test all 3 personas
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python -c "from app.src.main import app; print('developer OK')"

SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/pipeline-exploration-advanced_template.yaml \
  $ROOT/.venv/bin/python -c "from app.src.main import app; print('advanced OK')"

SPARMVET_PROFILE=$ROOT/config/deployment/pipeline_test/pipeline_test_profile.yaml \
SPARMVET_PERSONA=$ROOT/config/ui/templates/demo-vetinst_template.yaml \
  $ROOT/.venv/bin/python -c "from app.src.main import app; print('vetinst OK')"
```

**Verify in Phase 2 (port 8002) before the demo:**

- [ ] Load `1_test_data_ST22_dummy` → plots render
- [ ] T1 ↔ T2 toggle on MLST bar works
- [ ] Add filter → Propagate → Confirm → plots update
- [ ] Session Management accordion → Save session → note the session key
- [ ] Re-import that session → T3 state restored
- [ ] Global Project Export → Export ZIP → check ZIP opens and has TSV + YAML + audit + README.txt with all 3 hashes (Manifest SHA256, Data SHA256, Recipe hash)
- [ ] Metadata upload (left sidebar → Import helper) — *colleagues know this is in-progress; just show the upload field, no need for full flow*

---

## Crash recovery

```bash
cd $ROOT

# Clear T1 parquet cache (forces recompute on next load)
rm -f $ROOT/tmp/*.parquet

# Kill a port
fuser -k 8001/tcp   # or 8002/tcp, 8003/tcp

# Quick import check
SPARMVET_PERSONA=$ROOT/config/ui/templates/developer_template.yaml \
  $ROOT/.venv/bin/python -c "from app.src.main import app; print('OK')"
```

---

## Persona capability matrix (reference)

| Persona | T3 audit | Blueprint | Gallery | Test Lab | Session | Export bundle |
|---|---|---|---|---|---|---|
| `developer` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `project-independent` | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ |
| `pipeline-exploration-advanced` | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `pipeline-exploration-simple` | passive | ❌ | ❌ | ❌ | ❌ | ✅ |
| `pipeline-static` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `demo-vetinst` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ← no export, no controls, clean presentation view |

*passive = T1/T2 filter scratchpad only, no audit trail, no right sidebar*
