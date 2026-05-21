# TEST_LAB — Data Utility & Testing Suite

**Type:** User space  
**Status:** Partial build (`test_lab_studio.py` exists; most utilities not yet implemented)  
**Last updated:** 2026-05-05

---

## Purpose

TEST_LAB is a collection of small, focused utilities that help users prepare data for the app and test the app itself. It is not a single coherent workflow — it is a toolbox. Each tool solves one specific preparation or validation problem.

Primary audiences:
- **Data stewards** who need to reformat, clean, or anonymise data before loading into HOME.
- **Developers / testers** who need synthetic datasets (with controlled errors and edge cases) to validate the app's behaviour.
- **Manifest authors** who want a boilerplate starting point generated from their actual file structure.

---

## User Functionalities

### Data Reformatting

| Functionality | What the user can do |
|---|---|
| **XLSX → TSV** | Convert a multi-sheet Excel file to individual TSV |
| **CSV → TSV** | Reformat CSV files to TSV (standardise delimiter) |
| **Bulk reformat** | Process a folder of files in one operation |

### Manifest Scaffolding

| Functionality | What the user can do |
|---|---|
| **Boilerplate manifest from files** | Point TEST_LAB at a set of data files; it reads column names and types and generates a skeleton manifest YAML with correct column references, recognizing data types, ready to edit in BLUEPRINT |
| **ID reconciliation + primary key selection** | After reconciling IDs across files, user selects which columns are primary keys (ID as join keys, must be unique). ID cleaning recipes are automatically baked into the boilerplate manifest as tier1 wrangling steps |

**Composite / secondary keys:** BLUEPRINT's Join Designer already supports composite keys (`"on": ["col1", "col2"]` or asymmetric `left_on` / `right_on`). TEST_LAB's ID Reconciliation Engine handles **single-key matching only** — composite key scenarios are defined directly in BLUEPRINT's Join Designer after boilerplate generation.

**Boilerplate output format:** The boilerplate is a **ZIP archive** following the basename mirroring standard (`rules_manifest_structure.md §1`). Contents: a master YAML with `!include` tags + subdirectory fragments (`input_fields/`, `wrangling/`, `assembly/`). Structure is identical to the reference manifest `config/manifests/pipelines/1_test_data_ST22_dummy.yaml`. Single flat YAML is not used for manifests that include join recipes.

### Anonymisation (PROCESS 1: Real Data → Reversible Mapping)

Anonymisation takes a data file with an ID column and replaces all ID values with consistent synthetic equivalents. The same original ID always maps to the same anonymised ID. Mappings are output as TSV files (no access control system built in — deferred future enhancement; TSV format chosen to remain compatible when access control is added). **Anonymisation handles ID/key columns only** — the rest of the data is passed through unchanged (except personal info columns, which are stripped from anonymised output and bundled into the mapping TSV).

| Functionality | What the user can do |
|---|---|
| **Anonymise ID column** | Take a file with an ID column; replace all ID values with consistent synthetic equivalents. Same original_id always → same anon_id (preserves joins across files). Safe to share, reversible by authorized users |
| **Mapping TSV storage** | Store original_id → anon_id mapping (TSV), including any stripped personal info columns (name, address, etc.). No access control system built in — user keeps this file and shares only the anonymised output |
| **De-anonymisation via BLUEPRINT** | No dedicated de-anonymisation tool needed — restore original IDs by joining anonymised data with mapping TSV in BLUEPRINT (join on anon_id). Instructions provided in TEST_LAB output summary |
| **ID pattern for synthetic IDs** | Choose how synthetic IDs are generated: simple sequencing (ANON_0001, ANON_0002, ...), hash-based, or custom pattern |
| **Ensure ID consistency across files** | When anonymising multiple related files with the same ID column, same original_id maps to same anon_id everywhere (required for joins to remain valid post-anonymisation) |

### Synthetic / Test Data Generation (PROCESS 2: Schema → Fresh Data)

Synthetic data generation creates independent, fresh data matching a schema. No mapping to originals — used for testing or safe sharing without reversibility concerns.

| Functionality | What the user can do |
|---|---|
| **Generate synthetic data from schema** | Define column names, types, constraints — system generates plausible synthetic data. Built on `AquaSynthesizer` (`libs/test_lab/`). Two modes: **Demo** (clean realistic data) and **Stress test** (with controlled error injection) |
| **Generate synthetic data from example** | Upload real data — system learns schema + distributions per column (type, range, allowed values), proposes a generation config for user review; user adjusts, then generates. No link to original data |
| **Control synthetic distributions per column** | Two-step flow: system proposes config → user adjusts before generating. Extend allowed values beyond source data (diversity). YAML config saved for reproducibility and human adjustment after experience |
| **Inject controlled errors / edge cases** | Error types: missing values (null, messy strings like "-", "N/A"), wrong types (string in numeric column), duplicate IDs, PK mismatches across files, out-of-range values, empty groups, single-row groups. Schema-level errors: missing column, wrong column name, extra column. All error types configurable by rate/column |
| **Named error scenarios** | Save full generation config (schema + distributions + error injection) as named YAML file. Reload by name to reproduce exactly — regression test suite for the app |

### ID Reconciliation Engine (for Manifest Scaffolding & Data Ingestion)

| Functionality | What the user can do |
|---|---|
| **Multi-file ID alignment** | Upload 2–6 files with candidate ID columns; the engine analyzes format compatibility, groups compatible files, and suggests matching sequence |
| **Pairwise ID matching** | For each file pair, view side-by-side table of IDs with match status (exact, pattern-based, unmatched); certainty score per pair (not global) |
| **Pattern-based matching suggestions** | Engine suggests transformation rules (prefix/suffix removal, delimiter extraction, case normalization, substring extraction, regex); user verifies each match < 100% certainty |
| **Recode workflow** | If pattern matching insufficient, user can clean problematic IDs (trim, extract, normalize, custom regex); engine re-runs matching after cleaning |
| **Transformation recipe storage** | Save declarative recipe (YAML format) with human-readable audit log for reuse on future imports of same file types |
| **Progressive processing** | Process full file using Polars LazyFrame streaming (memory-efficient); display results in manageable chunks sorted by certainty descending; verify button per chunk; user can bulk-accept 100% exact matches or review individually; engine re-runs pattern detection on remaining unmatched after each acceptance round |
| **Many-to-many detection & suppression** | Flag true many-to-many (one source ID matches multiple distinct target IDs); offer option to suppress and continue — user must provide written reason for bypassing the warning |

**Workflow modes:** Standalone tool (user starts from ID reconciliation and downloads recipe + outputs) or **continuation** (engine output feeds directly into Manifest Scaffolding boilerplate generation without re-upload).
---

## ID Reconciliation Engine — Detailed Design

### Purpose & Scope

The ID Reconciliation Engine is the foundational tool for **Manifest Scaffolding**. Before TEST_LAB can generate a boilerplate manifest, join keys must be validated across all input files. The engine:

1. Analyzes ID formats across multiple files
2. Suggests compatible file pairs and matching order
3. Performs pairwise matching with per-pair certainty scores
4. Requires user verification for all matches < 100% (100% = exact string match only)
5. Generates reusable transformation recipes
6. Flags data quality issues (many-to-many relationships)

**Integration point:** Manifest Scaffolding workflow calls the ID Reconciliation Engine as step 1 before boilerplate generation.

### Workflow: Pairwise Matching Example

```
User uploads: metadata.tsv (sample_id column) + amr_results.tsv (S_id column)
              │
              ├─ PRE-CHECK: Analyze formats
              │   - Detect column types (displayed for info; ID columns always
              │     processed as categorical/text for matching regardless of type)
              │   - metadata: "sample_S001", "sample_S002", "sample_S999"
              │   - amr_results: "S001", "S002", "S999_QC_pass"
              │   ✓ Formats are compatible (IDs are present in both)
              │
              ├─ PHASE 1: Exact Match
              │   Left ID          │ Certainty │ Right ID
              │   sample_S001      │    100%   │ S001 ✓
              │   sample_S002      │    100%   │ S002 ✓
              │   sample_S999      │      0%   │ ??? (unmatched)
              │
              ├─ PHASE 2: Pattern Detection
              │   Engine suggests: "Left has 'sample_' prefix"
              │   Applied transformation: remove_prefix("sample_")
              │   sample_S999 → S999 → ??? (still no match in right)
              │
              │   Engine suggests next: "Right has '_' delimiters; extract first field"
              │   Applied transformation: extract_delimiter("_", position=0)
              │   S999_QC_pass → S999 → MATCH with transformed left ID
              │   Certainty: 87% (pattern-based, not exact)
              │
              ├─ PHASE 3: User Verification
              │   100% matches (exact string match) → auto-accept (user can override)
              │   87% match → MUST verify:
              │     "sample_S999 → S999_QC_pass. Is this correct? [Yes/No/Manual Pick]"
              │   Unmatched → User choice:
              │     "Leave unmatched" | "Manual pick from list" | "Needs cleaning"
              │
              └─ OUTPUT: Transformation Recipe (YAML)
                 - Matched pairs: 452/455
                 - Unmatched source: 3
                 - Transformation steps applied
                 - Audit log of user decisions
                 - Recipe saved for reuse on future imports
```

### Design Decisions Locked

#### 1. Certainty Scoring (Per Pair, Not Global)

Each ID pair receives an individual certainty score:

| Score | Meaning | User Action |
|---|---|---|
| **100%** | Exact string match | Auto-accept (user can override/reject). Promoted to "verified" status. Unverify option available if false positive later detected. |
| **95%** | Pattern match (e.g., remove prefix, extract from delimiter) | MUST manually verify each pair. On confirmation → promoted to "verified" status. Unverify option available. |
| **80%** | Fuzzy match (e.g., Levenshtein distance, substring similarity) | MUST manually verify each pair. On confirmation → promoted to "verified" status. Unverify option available. |
| **0%** | No match found | User decides: leave unmatched, discard this ID, try manual pairing, or recode |

**Critical rule:** No false positives allowed. Any match < 100% requires explicit user confirmation.

#### 2. Transformation Recipe Format (Declarative + Audit)

Stored as YAML for reusability and auditability:

```yaml
id_transformation_recipe:
  metadata:
    source_file: "metadata.tsv"
    target_file: "amr_results.tsv"
    source_id_column: "sample_id"
    target_id_column: "S_id"
    created_at: "2026-05-20T14:30:00"
    verified_by: "eve"
  
  transformation_steps:
    - step: 1
      action: "remove_prefix"
      pattern: "sample_"
      applied_to: "source"
    - step: 2
      action: "normalize_case"
      applied_to: "source"
    - step: 3
      action: "extract_delimiter"
      delimiter: "_"
      position: 0
      applied_to: "target"
  
  match_summary:
    total_source_ids: 455
    total_target_ids: 454
    matched_pairs: 452
    unmatched_source: 3
    unmatched_target: 2
  
  audit_log:
    - "Step 1: Removed 'sample_' prefix from 455 source IDs"
    - "Step 2: Normalized case (no IDs changed)"
    - "Step 3: Extracted first field from 454 target IDs"
    - "Exact matches after transformation: 452"
    - "User manually verified 452 matches (all >= 95% certainty)"
    - "Unmatched source IDs: S998, S997, S996 (no corresponding target)"
    - "Unmatched target IDs: CONTROL_001, BLANK_001 (expected — not samples)"
    - "User decision: Leave unmatched IDs as-is (data quality note added)"
```
Recipe is reusable: future imports of the same file types apply these steps automatically.

#### 3. Visualization: Side-by-Side Table

Table is **sorted by certainty descending** (100% first). Results are displayed in chunks (default 50 rows per chunk, configurable).

```
╔════════════════════════╦════════════════════════╦════════════╦══════════════╗
║  Source ID (left)      ║  Target ID (right)     ║ Certainty  ║  Action      ║
╠════════════════════════╬════════════════════════╬════════════╬══════════════╣
║ sample_S001            ║ S001                   ║  100%      ║ ✓ Verified   ║
║ sample_S002            ║ S002                   ║  100%      ║ ✓ Verified   ║
║ sample_S999            ║ S999_QC_pass           ║   87%      ║ ? Review     ║
║ sample_S998            ║ ❌ UNMATCHED          ║    0%      ║ ? Action req ║
║ sample_S997            ║ ❌ UNMATCHED          ║    0%      ║ ? Action req ║
╚════════════════════════╩════════════════════════╩════════════╩══════════════╝
  [ Bulk-accept all 100% matches ]    [ Accept chunk ]
```

**Review strategy:** Accept the easy cases first (100% exact matches), then work down through lower certainty. After each acceptance round, the engine re-runs pattern detection on remaining unmatched — new patterns may emerge as the problem space narrows.

User can:
- **"Bulk-accept all 100%"** → accept all exact matches at once, promoted to "verified"
- **"Accept chunk"** → accept all verified decisions in the current chunk and advance to next chunk
- Click "Review" → see transformation steps that produced the match
- Click "❌" → choose "Leave unmatched" | "Discard this ID" | "Manual pick" | "Recode"
- **Unverify** any previously accepted match if a false positive is detected

#### 4. Progressive Matching (Chunked Processing)

The engine **always processes the full file** — no sampling. Efficiency is achieved through Polars LazyFrame streaming (not by processing less data).

1. **Full processing via streaming**: Engine runs matching on the complete file using Polars LazyFrame (`scan_parquet` / lazy evaluation). Memory stays bounded regardless of file size — results are streamed as computed.
2. **Sorted chunk display**: Results presented sorted by certainty descending (100% first) in chunks of 50 rows (configurable in persona config). User sees the easiest cases first.
3. **Verify button per chunk**: Each displayed chunk has an explicit "Accept chunk" button. User reviews decisions in the chunk, adjusts any individual action, then accepts to advance to the next chunk.
4. **Iterative re-run**: After each acceptance round, the engine re-runs pattern detection on remaining unmatched IDs. Pattern space narrows with each round, making new patterns detectable.
5. **Unmatched chunking**: If many unmatched IDs remain after all rounds, they are also presented in chunks of 50 for manageable review rather than one overwhelming list.

#### 5. Many-to-Many Detection & Suppression

**Distinction:**
- **One-to-many** (one source ID matches one target ID, but target has multiple result rows): normal — not flagged. Expected in long-format data (e.g., same sample, multiple genes).
- **True many-to-many** (one source ID matches multiple *distinct* target IDs at the ID-alignment level): flagged as a data error. This almost always indicates duplicates or misaligned data.

**Example:**
```
sample_S001 matches → S001 AND S001_replicate (true many-to-many detected)
                      ↓
                      Banner: "⚠️ Many-to-many relationship detected.
                               This usually indicates duplicate or misaligned data.
                               Review before proceeding.
                               [Suppress & Continue — requires written reason]"
```

If user confirms "Suppress & Continue":
- User **must provide written reason** (free-text field, mandatory — cannot be empty)
- Reason logged in audit trail alongside the warning
- Many-to-many pair kept (user's responsibility)
- Engine proceeds with matching

**Warning system covers all use cases** (including future internal join scenarios where the same entity appears multiple times). No deferral needed — the warning + reason requirement is sufficient for all known cases.

#### 6. Recode Workflow (If Pattern Matching Fails)

If pattern detection + user manual pairing insufficient:

**Threshold rule (C11):** If more than **50 unmatched IDs** remain after all pattern rounds (threshold configurable in persona config), the engine suggests: *"You have [N] unmatched IDs with no consistent pattern detected. Consider standardising your ID format and retrying — this will produce better results than manual case-by-case resolution."* User can accept this advice (download a list of unmatched IDs, clean externally, re-upload) or continue with manual resolution.


```
User selects: "sample_S999 needs cleaning"
              ↓
              Engine offers menu:
              - Trim whitespace
              - Remove special characters
              - Extract substring (specify range or delimiters)
              - Case normalize
              - Custom regex replace
              ↓
              User applies: extract_substring(0, 4)  # "sample_" → "S999"
              ↓
              Engine re-runs matching on cleaned IDs
              ↓
              sample_S999 (cleaned to S999) → S999 ✓ Match found
              ↓
              User verifies result
              ↓
              Recode step added to transformation recipe
```

#### 7. Multi-File Smart Sequencing (Pre-Check)

When user uploads 3+ files:

```
Input: Files A, B, C, D, E (5 files total)

PRE-CHECK analyzes ID formats:
  A & B: identical format ("S001", "S002", ...) → exact match expected
  C & D: similar format ("S_001", "S_002", ...) → pattern match expected
  E: different format ("run1-S001", "run2-S002") → needs extraction

SUGGEST SEQUENCE:
  1. Match A ↔ B (trivial — build confidence)
  2. Match (A↔B result) ↔ C (introduce variation)
  3. Match result ↔ D (more variation)
  4. Match result ↔ E (complex transformation)

RATIONALE: Start easy, build pattern understanding, tackle hardest last.
```

**Complexity warning:** If pre-check detects that the expected transformation between two files is multi-step or involves complex pattern extraction (e.g., regex with capture groups, multiple delimiter operations in sequence), the engine shows: *"Complex transformation detected between [File A] and [File C]. Consider standardising your ID format before matching — this will produce more reliable results."* User can proceed or clean data first. (Exact definition of "complex" is to be specified during implementation based on pattern classifier outputs.)

---

## Manifest Scaffolding — Primary Key Selection & Recipe Integration

### Workflow: From ID Reconciliation to Manifest Boilerplate

After ID reconciliation is complete and user has verified matches, the scaffolding workflow:

```
1. User identifies join keys in input_fields
   - For each schema, which column is the join key (used to link files)?
   - E.g., metadata_schema → sample_id
   - E.g., amr_schema → sample_id
   - User confirms these will be unique after cleaning
   - (Composite keys defined later in BLUEPRINT Join Designer — not in TEST_LAB)

2. System validates join key uniqueness
   - Check if columns have duplicate values before cleaning
   - Flag problematic duplicates (data quality warning)

3. System generates boilerplate manifest ZIP (basename mirroring format)
   - Master YAML: data_schemas, join_manifests stubs with !include tags
   - Fragment files: input_fields per schema (columns, types from actual data)
   - Fragment files: wrangling per schema (ID reconciliation recipes in tier1)
   - Fragment files: join wrangling file pre-filled with verified join keys
   - Validation checks in tier1: drop_duplicates, null_if + drop_nulls on join keys

4. User downloads ZIP and opens master manifest in BLUEPRINT
   - Join key alignment already done (from ID reconciliation)
   - ID cleaning recipes in tier1 — ready to verify/extend
   - Stub join recipe already wired to the correct key
   - analysis_groups stub: user adds plots and groups in BLUEPRINT
```

### Example Boilerplate Manifest (with recipes baked in)

The boilerplate is downloaded as a **ZIP** containing a master manifest + fragment files.
All paths follow the basename mirroring standard (`rules_manifest_structure.md §1`).

```yaml
# ── FILE: sample_amr_pipeline.yaml  (master manifest) ──────────────────────────

id: sample_amr_pipeline
type: sample
info:
  display_name: "Sample AMR Pipeline"
  description: "Sample metadata + AMR results"

# ── Data Schemas ────────────────────────────────────────────────────────────────
data_schemas:
  metadata_schema:
    source:
      type: local_tsv
      path: ./data/metadata.tsv  # placeholder — user updates path
    input_fields: !include 'sample_amr_pipeline/input_fields/metadata_schema_input_fields.yaml'
    wrangling: !include 'sample_amr_pipeline/wrangling/metadata_schema_wrangling.yaml'
    output_fields: {}  # identity passthrough — define in BLUEPRINT if needed

  amr_schema:
    source:
      type: local_tsv
      path: ./data/amr_results.tsv  # placeholder — user updates path
    input_fields: !include 'sample_amr_pipeline/input_fields/amr_schema_input_fields.yaml'
    wrangling: !include 'sample_amr_pipeline/wrangling/amr_schema_wrangling.yaml'
    output_fields: {}

# ── Join Manifests ──────────────────────────────────────────────────────────────
join_manifests:
  sample_amr_joint:
    description: "Metadata + AMR results — join key: sample_id (verified by TEST_LAB)"
    ingredients:
      - dataset_id: metadata_schema
      - dataset_id: amr_schema
    recipe: !include 'sample_amr_pipeline/wrangling/sample_amr_joint_wrangling.yaml'

# ── Analysis Groups — stub, define in BLUEPRINT ─────────────────────────────────
analysis_groups: {}
```

```yaml
# ── FILE: sample_amr_pipeline/input_fields/metadata_schema_input_fields.yaml ───

sample_id:
  type: categorical
  description: "Sample identifier (join key — cleaned in tier1)"
collection_date:
  type: string
  description: "Collection date"
site:
  type: categorical
age:
  type: string
```

```yaml
# ── FILE: sample_amr_pipeline/wrangling/metadata_schema_wrangling.yaml ─────────
# ID Reconciliation recipe baked in from TEST_LAB matching session

tier1:
  # Step 1: Remove 'sample_' prefix (reconciliation recipe: remove_prefix)
  - action: regex_replace
    column: sample_id
    pattern: "^sample_"
    replacement: ""

  # Step 2: Cast other fields
  - action: cast
    columns: [collection_date]
    dtype: String

  # Step 3: Join key integrity — drop duplicates and nulls
  - action: drop_duplicates
    columns: [sample_id]
  - action: null_if
    column: sample_id
    value: ""
  - action: drop_nulls
    columns: [sample_id]
```

```yaml
# ── FILE: sample_amr_pipeline/input_fields/amr_schema_input_fields.yaml ────────

sample_id:
  type: categorical
  description: "Sample ID (join key — cleaned in tier1)"
amr_gene:
  type: categorical
phenotype:
  type: categorical
```

```yaml
# ── FILE: sample_amr_pipeline/wrangling/amr_schema_wrangling.yaml ───────────────
# ID Reconciliation recipe baked in from TEST_LAB matching session

tier1:
  # Step 1: Extract first field before '_' delimiter (reconciliation recipe: extract_delimiter)
  - action: mutate
    column: sample_id
    expression: "pl.col('sample_id').str.split('_').list.first()"

  # Step 2: Join key integrity — drop duplicates and nulls
  - action: drop_duplicates
    columns: [sample_id]
  - action: null_if
    column: sample_id
    value: ""
  - action: drop_nulls
    columns: [sample_id]
```

```yaml
# ── FILE: sample_amr_pipeline/wrangling/sample_amr_joint_wrangling.yaml ────────
# Pre-filled with verified join key from ID reconciliation

tier1:
  - action: join
    right_ingredient: amr_schema
    'on': ["sample_id"]   # Both sides cleaned; join key verified in TEST_LAB
    how: left             # placeholder — choose inner / left / outer in BLUEPRINT
```

**Key points:**
- `data_schemas:` is the correct top-level key (not `input_schemas:`)
- `source:` block is required per schema (user updates path before loading in BLUEPRINT)
- Join defined via `ingredients:` list + `recipe: !include` — never inline in the master
- ID cleaning in `tier1` uses registered transformer actions (`regex_replace`, `mutate`, `drop_duplicates`, `null_if`, `drop_nulls`)
- `output_fields: {}` = identity passthrough (ADR-014) — user adds contracts in BLUEPRINT
- `analysis_groups: {}` = stub — user fills in BLUEPRINT with plots and groups

---

## Anonymisation — Design & Workflow (PROCESS 1)

### Design Decisions Locked

**Q1: ID Mapping & Reversibility** → **Reversible with manual access control**
- Store original_id → anon_id mapping as **TSV file** (joinable, not YAML)
- No access control system built into TEST_LAB now — one designated person runs the anonymisation, shares the anonymised files, and keeps the mapping TSV for themselves
- Access control (admin/role system) is a **future enhancement** — deferred

**Q2: Access Control** → **Deferred (manual for now)**
- Current model: person who runs anonymisation holds the mapping TSV; they decide what to share
- No persona flags or deployment profile controls for this in the current build
- Plan for access control system in a future enhancement without needing to refactor the output format (TSV is already compatible)

**Q3: ID Pattern for Synthetic IDs** → **Simple Sequencing (with options)**
- Default: ANON_0001, ANON_0002, ANON_0003, ... (simple sequencing)
- Option: User can choose custom pattern or hash-based
- Consistency required: all synthetic IDs in anonymised dataset follow the same pattern

**Q5: ID Alignment Across Files** → **Same Anon ID for Same Original ID**
- When anonymising multiple related files, same original_id always maps to same anon_id
- Ensures joins remain valid post-anonymisation
- Use ID Reconciliation Engine to validate join keys before & after anonymisation

### Recommended Workflow (visual)

```
BEFORE ANONYMISING:
  ┌──────────────────────────────────────────────────────┐
  │ STEP 0 (Recommended): Run ID Reconciliation first    │
  │  → validate IDs match across all files               │
  │  → ensures anonymisation preserves join validity     │
  └──────────────────────────────────────────────────────┘
                         ↓

ANONYMISATION WORKFLOW:
  1. Upload files          2. Select columns          3. Configure & run
  ─────────────────        ──────────────────         ─────────────────────
  metadata.tsv      →      ID column: sample_id  →    Pattern: ANON_{:04d}
  results.tsv              Personal columns to         Apply to: all files
                           strip: name, address,
                           phone → go to mapping TSV
                         ↓
  4. Outputs
  ────────────────────────────────────────────────────────
  anonymised_metadata.tsv   (sample_id → ANON_0001, personal cols removed)
  anonymised_results.tsv    (sample_id → ANON_0001, personal cols removed)
  mapping_sample_id.tsv     (original_id | anon_id | name | address | phone)
  anonymisation_config.yaml (audit record — NOT a pipeline manifest)
                         ↓
  5. Share
  ────────────────────────────────────────────────────────
  Share → anonymised files (safe to distribute)
  Keep  → mapping_sample_id.tsv (you hold this; no built-in access control)
                         ↓
  6. De-anonymise later (via BLUEPRINT)
  ────────────────────────────────────────────────────────
  Join anonymised_results.tsv ← mapping_sample_id.tsv (on anon_sample_id)
  → original IDs + personal columns restored
  (TEST_LAB output includes copy-paste BLUEPRINT join recipe)
```

### Workflow Steps Detail

```
1. Upload files to anonymise (1+ files with same ID column)

2. (Recommended) Run ID reconciliation pre-check
   - Validates ID columns are aligned across files
   - Ensures same original_id maps to same anon_id after anonymisation

3. User configures anonymisation
   - Select ID column: sample_id
   - Select personal info columns to strip (name, address, phone, email, etc.)
     → these will be REMOVED from anonymised output
     → and ADDED as extra columns in mapping TSV
   - Choose ID pattern: ANON_0001, ANON_0002, ... (or custom)
   - Confirm: "apply to all selected files"

4. System generates anonymised datasets
   - Same original_id → same anon_id across all files (preserves joins)
   - Personal info columns: stripped from output, bundled into mapping TSV
   - Output:
     * anonymised_metadata.tsv
     * anonymised_results.tsv
     * mapping_sample_id.tsv (original_id + anon_id + personal columns)
     * anonymisation_config.yaml (audit/transparency record, not a pipeline manifest)

5. Access control
   - No system built in — user keeps mapping TSV, shares anonymised files only
   - Future enhancement: role-based access control (deferred)

6. Anonymised datasets safe to share
   - De-anonymise later via BLUEPRINT join (recipe included in TEST_LAB output)
```

### Example Anonymisation Configuration

**Note:** The YAML below is an **audit/transparency record only** — it is NOT a pipeline manifest and is never processed by the SPARMVET engine. It documents what was done, with what settings, on what date. Stored alongside the output files so the run can be understood or repeated months later.

**Input:** Files to anonymise with ID column
- metadata.tsv (sample_id column)
- results.tsv (sample_id column)

**Configuration:**
```yaml
anonymisation:
  id_column: sample_id
  id_pattern: "ANON_{:04d}"  # ANON_0001, ANON_0002, ANON_0003, ...
  apply_to_files: [metadata.tsv, results.tsv]
  output_mapping_file: mapping_sample_id.tsv
  mapping_access_level: admin_and_researchers
```

**What happens:**
- All rows in metadata.tsv: sample_id "S001" → "ANON_0001"
- All rows in results.tsv: sample_id "S001" → "ANON_0001" (same mapping)
- All other columns passed through unchanged
- Mapping stored in TSV: `original_sample_id \t anon_sample_id`

### Output Files

1. **anonymised_metadata.tsv** — Real data with anonymised values, same structure
2. **anonymised_results.tsv** — Real data with anonymised values, same structure
3. **mapping_sample_id.tsv** — Joinable TSV: original_sample_id ↔ anon_sample_id + any personal info columns stripped from the anonymised output (name, address, phone, etc.)

Example mapping_sample_id.tsv (with personal info columns stripped from anonymised data):
```
original_sample_id	anon_sample_id	patient_name	address	phone
S001	ANON_0001	Jane Doe	Oslo, Norway	+47 123 45 678
S002	ANON_0002	John Smith	Bergen, Norway	+47 987 65 432
S003	ANON_0003	Anna Hansen	Tromsø, Norway	+47 555 12 345
```

**Use case:** Authorized user can join this with anonymised_results.tsv to restore original IDs:
```
JOIN anonymised_results ON anon_sample_id
     WITH mapping_sample_id ON anon_sample_id
     → SELECT original_sample_id, ... FROM results (deidentified)
```

---

## Synthetic / Test Data Generation — Design & Workflow (PROCESS 2)

### Purpose

Generate fresh, independent data matching a schema. Used for:
- Testing app behavior with edge cases
- Safe sharing when true anonymity (not reversibility) is required
- Developing & validating manifests without real data

### Two Modes

**Demo mode** — clean, realistic synthetic data for sharing and visualization development. No injected errors. Distributions match the real data or schema ranges.

**Stress test mode** — same data with controlled error injection to validate app behavior (ingest failures, join mismatches, malformed fields, schema errors). Used for regression testing and edge-case exploration.

### Workflow: Generate Synthetic Data

```
1. User chooses input source:
   Option A: Upload schema (column names, types, constraints)
   Option B: Upload example real data (system learns schema + distributions)

2. System proposes generation config (two-step flow):
   - Inspects columns → proposes types, ranges, and distribution parameters
   - For Option B: matches observed distributions (min/max for numerics,
     unique values for categoricals, null rates)
   - User reviews the proposed config and adjusts as needed:
     - Change distribution (uniform → normal, etc.)
     - Extend allowed_values for categoricals
     - Set ID pattern (sequential, hash, custom prefix)
     - Switch to Demo or Stress test mode

3. User presses Generate
   - For Demo mode: clean output matching schema + distributions
   - For Stress test mode: user configures error injection before generating:
       • missing values (per column, configurable rate)
       • wrong type (e.g. string in numeric column, rate)
       • duplicate IDs (rate)
       • PK mismatches (IDs in one file not in another, rate)
       • schema-level errors (missing column, wrong column name, extra column)
       • malformed fields (unparseable dates, out-of-range values)
   - Output: TSV + accompanying synthetic_data_config.yaml (see below)

4. User can save as a named scenario
   - Name: "edge_case_duplicates_10pct"
   - Saves full config: schema + distributions + error injection params
   - Reusable for regression testing across app versions
```

### Synthetic Data Config YAML — Purpose and Format

> **This YAML is NOT a pipeline manifest.** It is an archive/transparency record saved
> alongside the generated TSV. It is never loaded by the HOME or BLUEPRINT data engine
> and never goes through the wrangling/ingestion pipeline. Its only purpose is to document
> what was generated and how, so the generation can be reproduced exactly.
>
> This is distinct from the analysis manifests used in HOME and BLUEPRINT, which define
> data schemas, wrangling steps, and join recipes for actual data processing.

```yaml
# synthetic_data_config.yaml
# Archive record — saved alongside the generated TSV.
# NOT a pipeline manifest. NOT processed by the SPARMVET data engine.

metadata:
  generated_at: "2026-05-21T14:30:00"
  source: "example_data"      # or "schema"
  source_file: "real_metadata.tsv"   # if source=example_data
  n_rows: 100
  mode: demo                  # demo | stress_test
  output_file: "synthetic_test_data.tsv"

columns:
  sample_id:
    type: id
    pattern: "SAMPLE_{:05d}"    # sequential ID pattern
    unique: true

  collection_date:
    type: date
    min: "2024-01-01"
    max: "2024-12-31"
    distribution: uniform

  age:
    type: numeric
    min: 18
    max: 90
    distribution: normal
    mean: 45
    stdev: 15

  site_name:
    type: categorical
    allowed_values: ["Site_A", "Site_B", "Site_C", "Site_D"]
    # extend_with: ["Site_E"]   # add values beyond observed set

  test_result:
    type: categorical
    allowed_values: ["positive", "negative"]

# error_injection block is only present for mode: stress_test
error_injection:
  missing_values:
    - {column: age, rate: 0.02}
    - {column: test_result, rate: 0.01}
  wrong_type:
    - {column: age, rate: 0.01}   # string injected into numeric column
  duplicate_ids:
    column: sample_id
    rate: 0.05                     # 5% of IDs will be duplicated
  pk_mismatches:
    rate: 0.03                     # 3% of IDs will not match the join partner file
  schema_errors:
    missing_column: null           # name of column to drop entirely, or null
    wrong_column_name: null        # {from: old_name, to: typo_name}, or null
    extra_column: null             # name of extra column to inject, or null
```

### Named Error Scenarios (Saved & Reusable)

Users can save a named scenario: the full config (schema + distributions + error injection params)
is saved as a YAML file in the `test_lab/scenarios/` directory. The file is the same format as
above, with an added `name:` and `description:` in the `metadata:` block.

```yaml
# scenario: edge_case_duplicates_10pct.yaml
metadata:
  name: "edge_case_duplicates_10pct"
  description: "10% duplicate sample IDs — tests join error handling in ingest layer"
  generated_at: "2026-05-21T14:30:00"
  source: "schema"
  n_rows: 100
  mode: stress_test
  output_file: "synthetic_edge_case_duplicates_10pct.tsv"

columns:
  sample_id:
    type: id
    pattern: "SAMPLE_{:05d}"
    unique: true
  collection_date:
    type: date
    min: "2024-01-01"
    max: "2024-12-31"

error_injection:
  duplicate_ids:
    column: sample_id
    rate: 0.10
```

Saved scenarios are listed in the TEST_LAB UI and can be re-run with one click to regenerate
the same TSV (identical structure and error patterns) for regression testing across app versions.

---

## Non-Goals

- TEST_LAB does not run the main analysis — that is HOME.
- TEST_LAB does not build or edit manifests beyond generating a boilerplate scaffold — that is BLUEPRINT.
- TEST_LAB does not curate or share recipes — that is GALLERY.
- TEST_LAB does not permanently store anonymised data on behalf of the user — it produces files the user downloads. Session state (in-progress reconciliation, unsaved config) is held in memory for the duration of the browser session only. If the user closes the tab, work is lost. Named test scenarios are the exception — these are saved as YAML files and persist across sessions.

---

## Key Design Constraints

- **Stateless tools**: each TEST_LAB utility runs to completion and returns a file (or several files), or displays a result in the UI (e.g. ID reconciliation match table before the user downloads the recipe). No persistent session state between tool invocations, except named test scenarios (saved as YAML files) and ID reconciliation recipes (saved as YAML files). New tools can be added later by adding a new panel to the left sidebar accordion — the architecture is open for extension.

- **No data leaves the server**: anonymisation and synthetic generation happen server-side; the user downloads the result. Raw data is never sent to an external service.
- **Pattern helper shared with BLUEPRINT**: the ID/column pattern matching logic should be the same component. Design for reuse from the start.
- **Positive inclusion** (ADR-071): TEST_LAB panel is only mounted when `test_lab_enabled` is true in persona config.
- **Audit trail**: file-generation operations should log what was produced (filename, schema, row count, generation parameters) to the session audit log.

---

## Code Modules

| Code module | Role |
|---|---|
| `test_lab_studio.py` | UI and server handlers for all TEST_LAB tools |
| `libs/test_lab/` | Existing library — `aqua_synthesizer.py`, `reconciler.py`, `bootstrapper.py` are the foundations to build on |
| `libs/id_reconciliation/` | New library (to be created) — pure ID matching logic, pattern detection, recipe generation. Tier 1 only (utils + polars). See `id_reconciliation_module_sketch.md`. |

---

## Current State

- `test_lab_studio.py` exists as a module stub.
- Synthetic data generation: early experiment exists (referenced in recent commits as "test lab for synthetic data generation").
- Reformatting utilities: not yet built.
- Manifest scaffolding: not yet built.
- Pattern matching helper: not yet built.
- Named test scenarios: not yet built.

---

## Open Questions

- **Pattern helper placement**: shared component with BLUEPRINT to avoid duplication. Placed in `libs/utils/` (Tier 1) — the only cross-lib import allowed by the Clear Lines policy. Both `libs/id_reconciliation/` and `libs/blueprint_arch/` can then import it without violating peer-import rules.
- **Anonymisation fidelity**: plausible ranges sufficient (same types + realistic value ranges). Full distributional matching deferred — can be improved later without refactoring.
- **Test scenario storage**: YAML format (human-readable for user adjustment). Lives in `libs/test_lab/` under a `scenarios/` subdirectory. Not processed by the data engine.
- **Boilerplate manifest scope**: structure only (input_fields, output_fields, primary key definitions, verified join keys). The exception is ID cleaning recipes from ID reconciliation — those are baked in because they are required prerequisites, not analysis logic. All other wrangling belongs in BLUEPRINT.
- **UI structure**: left sidebar accordion with one panel per tool category (ID Reconciliation, Manifest Scaffolding, Synthetic Data, Anonymisation). Each panel expands in place. This matches the sidebar pattern used in HOME and BLUEPRINT and avoids a separate tab-switching layer inside the TEST_LAB workspace.

---

## Build Tasks (Phase 34)

Task IDs mirror the tasks.md entries. Dependencies within the phase are noted.

### 34-A — ID Reconciliation Library (`libs/id_reconciliation/`)

New Tier 1 library. Zero imports from other domain libs — only `polars` + `utils`.

- **TL-IDLIB-1** `[haiku/low]`: Scaffold `libs/id_reconciliation/` — `pyproject.toml` (deps: `polars`, `utils`), module structure (`__init__.py`, empty module files), editable install, empty `tests/conftest.py`. Gate: `from id_reconciliation import IDReconciliationEngine` succeeds.

- **TL-IDLIB-MATCH-1** `[sonnet/high]`: Core matching engine — `data_structures.py` (`IDPair`, `MatchResult`, `PatternSuggestion`, `TransformationRecipe` dataclasses) + `matcher.py` (exact string match → certainty 1.0; fuzzy/substring → certainty scored; unmatched → certainty 0.0). Builds on existing `reconciler.py` logic (do not duplicate — import or port). Gate: `test_exact_match` passes; `test_pattern_match` passes.

- **TL-IDLIB-PATTERN-1** `[sonnet/high]`: Pattern detector — `pattern_detector.py` (prefix/suffix removal, delimiter extraction, case normalisation, substring extraction, regex; patterns ranked by `(expected_matches DESC, expected_certainty DESC, simplicity ASC)`). Builds on `suggest_regex` in `reconciler.py`. Gate: `test_pattern_suggestion` passes (prefix `"sample_"` detected and ranked first).

- **TL-IDLIB-RECIPE-1** `[sonnet/medium]`: Recode workflow + recipe persistence — `recipe.py` (`apply_recode_step` for actions: `regex_replace`, `mutate` via Polars expression, `drop_duplicates`, `null_if`, `drop_nulls`; `TransformationRecipe.to_yaml` / `from_yaml`). Gate: `test_recipe_persistence` passes (save + load round-trip); `test_recode_workflow` passes (prefix removal + delimiter extraction).

- **TL-IDLIB-CORE-1** `[sonnet/high]`: IDReconciliationEngine orchestrator — `core.py` (`precheck_compatibility`, `match_pair`, `suggest_patterns`, `apply_pattern`, `generate_recipe`, `detect_many_to_many`, `format_match_table`). Progressive matching: full file via Polars LazyFrame, display in sorted chunks (default 50 rows, configurable in persona config). Multi-file sequencing: suggest matching order based on format compatibility. Recode threshold: 50 unmatched IDs triggers "clean first" suggestion (configurable). Gate: `test_many_to_many_detection` passes; progressive chunking unit test passes; `format_match_table` returns parseable string.  
  Depends: TL-IDLIB-MATCH-1, TL-IDLIB-PATTERN-1, TL-IDLIB-RECIPE-1.

- **TL-IDLIB-TESTS-1** `[sonnet/medium]`: Full test suite for `libs/id_reconciliation/tests/` — unit tests per module + `id_reconciliation_integrity_suite.py` orchestrator. Include: exact match, pattern suggestion, many-to-many detection, recipe round-trip, recode step (all 5 action types), multi-file sequencing suggestion. Gate: `pytest libs/id_reconciliation/tests/ -q` all pass.  
  Depends: TL-IDLIB-CORE-1.

### 34-B — Pattern Helper in `libs/utils/`

Shared component; both `id_reconciliation` and `blueprint_arch` import from here to avoid duplication.

- **TL-UTILS-PATTERN-1** `[sonnet/low]`: Extract ID pattern matching primitives (prefix/suffix detection, delimiter extraction, regex generalisation) into `libs/utils/src/utils/id_patterns.py`. Update `libs/id_reconciliation/` to import from there. Update `libs/blueprint_arch/` Join Designer (`join_designer.py`) to also use this helper where applicable. Gate: both libs import cleanly; no duplication of pattern logic between the two.  
  Depends: TL-IDLIB-PATTERN-1 (to know what to extract).

### 34-C — ManifestBootstrapper Fixes (`libs/test_lab/`)

Three known bugs + new capability.

- **TL-BOOTSTRAP-FIX-1** `[sonnet/low]`: Fix `libs/test_lab/src/test_lab/bootstrapper.py`:
  1. `"plotting"` key → `"analysis_groups"` (wrong key name)
  2. Remove hardcoded spurious `metadata_schema:` entry in output
  3. Add `join_manifests: {}` stub (empty placeholder for BLUEPRINT)
  4. Accept optional `id_cleaning_recipes: dict` param — when provided (from ID reconciliation output), bake valid cleaning actions (`regex_replace`, `mutate`, `drop_duplicates`, `null_if`, `drop_nulls`) into `tier1:` wrangling of the relevant `data_schemas:` entry.
  Gate: `debug_sdk.py` (or new headless test) generates a valid manifest that matches the boilerplate example in this design doc. Verified by running `debug_assembler.py` on the output.  
  Depends: TL-IDLIB-RECIPE-1 (to know the recipe format to inject).

### 34-D — Manifest Scaffolding ZIP

End-to-end output from files → verified IDs → boilerplate ZIP.

- **TL-SCAFFOLD-1** `[sonnet/medium]`: Implement manifest scaffolding ZIP output in `libs/test_lab/src/test_lab/bootstrapper.py` (or a new `scaffolder.py`). Input: list of TSV paths + `TransformationRecipe` objects from ID reconciliation. Output: ZIP archive following basename mirroring standard — master YAML with `!include` tags + `input_fields/`, `wrangling/`, `assembly/` fragment files. Master manifest: `data_schemas:` per file + `join_manifests:` with one entry per verified file pair (pre-filled join key from recipe) + `analysis_groups: {}`. Fragment `wrangling/` files include ID cleaning steps from recipe.
  Gate: unzip output → `debug_assembler.py` runs without error on the generated manifest (no plot specs needed — `analysis_groups: {}` is valid). Verify `data_schemas:` key (not `input_schemas:`), `ingredients:` format (not `left_ingredient:`), quoted `'on':` join key.  
  Depends: TL-BOOTSTRAP-FIX-1, TL-IDLIB-CORE-1.

### 34-E — Synthetic Data Upgrade

Upgrade `AquaSynthesizer` — do not rewrite; extend.

- **TL-SYNTH-1** `[sonnet/high]`: Upgrade `libs/test_lab/src/test_lab/aqua_synthesizer.py`:
  - **Two-step flow**: `propose_config(source)` → returns `SynthConfig` dict (inferred from schema or real data); `generate(config)` → produces TSV + `synthetic_data_config.yaml` (archive record, NOT a pipeline manifest — add prominent header comment).
  - **Two modes**: `mode: demo` (clean output) vs `mode: stress_test` (with error injection block).
  - **Error injection block** (stress_test only): `missing_values` (per column, rate), `wrong_type` (per column, rate), `duplicate_ids` (column + rate), `pk_mismatches` (rate), `schema_errors` (missing_column / wrong_column_name / extra_column), `malformed_fields` (out-of-range, unparseable dates, rate).
  - **Named scenarios**: `save_scenario(config, name, description)` → writes to `libs/test_lab/scenarios/<name>.yaml`; `load_scenario(name)` → returns `SynthConfig`; `list_scenarios()` → list of names.
  - **YAML config output**: saved alongside generated TSV. Add prominent comment header: `# synthetic_data_config.yaml — Archive record. NOT a pipeline manifest. NOT processed by the SPARMVET data engine.`
  Gate: demo mode generates clean TSV matching schema; stress_test injects stated error rate ±2%; scenario round-trip (save → load → generate produces same schema); `pytest libs/test_lab/tests/test_aqua_synthesizer.py -q` passes.

### 34-F — Anonymisation Tool

- **TL-ANON-1** `[sonnet/medium]`: Implement `libs/test_lab/src/test_lab/anonymiser.py`:
  - `anonymise(filepath, id_column, personal_columns, pattern)` → writes anonymised TSV + mapping TSV.
  - `anonymise_batch(filepaths, id_column, ...)` → multi-file consistency (same original_id always maps to same anon_id).
  - ID patterns: sequential (`ANON_{:05d}`), hash-based (SHA256 truncated), custom prefix.
  - Mapping TSV columns: `original_id`, `anon_id` + any stripped personal columns.
  - Output summary: instructions for de-anonymisation via BLUEPRINT join.
  Gate: round-trip test (anonymise → de-anonymise via join → original IDs restored); multi-file consistency test (same original_id maps identically across two files); personal column stripping verified.

### 34-G — Reformatting Tools

- **TL-REFORMAT-1** `[haiku/low]`: Wire `ExcelHandler` (already exists in `libs/ingestion/`) into a TEST_LAB-accessible function in `libs/test_lab/src/test_lab/reformatter.py`. Add CSV→TSV. Add bulk folder processing. Output: TSV files + summary of sheets/files converted. Gate: multi-sheet XLSX converts to N TSV files; CSV with non-tab delimiter converts correctly.

### 34-H — UI (gates on library tasks)

- **TL-UI-SHELL-1** `[sonnet/medium]`: TEST_LAB UI shell in `test_lab_studio.py` — left sidebar accordion with panels for each tool (ID Reconciliation, Manifest Scaffolding, Synthetic Data, Anonymisation, Reformatting). View title banner. Gated by `test_lab_enabled` persona flag (ADR-071). Sidebar slot type: `test_lab` — add to sidebar registry. Gate: app starts with `test_lab_enabled: true`; accordion panels render; `test_lab_enabled: false` shows no TEST_LAB nav.

- **TL-UI-REFORMAT-1** `[haiku/low]`: Reformatting panel — file upload (XLSX/CSV), sheet assignment UI for XLSX (sheet → TSV name), convert button, download TSVs.  
  Depends: TL-REFORMAT-1, TL-UI-SHELL-1.

- **TL-UI-RECONCILE-1** `[sonnet/high]`: ID Reconciliation panel — multi-file upload (2–6 files), PRE-CHECK result display (compatibility groups, suggested matching order), pairwise match table (side-by-side, sorted by certainty descending, chunked 50 rows, bulk-accept 100% button, per-row verify/reject), pattern suggestion panel (ranked suggestions with expected match count, apply button), recode workflow (action picker, cleaned ID preview, re-run matching), many-to-many flag dialog (mandatory written reason), recipe download (YAML).  
  Depends: TL-IDLIB-CORE-1, TL-UI-SHELL-1.

- **TL-UI-SCAFFOLD-1** `[sonnet/medium]`: Manifest Scaffolding panel — file upload, "Continue from ID Reconciliation" mode (uses session-held reconciliation output), join key selection, boilerplate ZIP download. Displays what was baked in (ID cleaning steps, join keys, file count).  
  Depends: TL-SCAFFOLD-1, TL-UI-RECONCILE-1.

- **TL-UI-SYNTH-1** `[sonnet/medium]`: Synthetic Data panel — schema/file upload, proposed config review table (per-column editable params), mode toggle (Demo / Stress test), error injection config block (shown only in stress_test mode), n_rows input, generate button, scenario save/load controls, download TSV + YAML config.  
  Depends: TL-SYNTH-1, TL-UI-SHELL-1.

- **TL-UI-ANON-1** `[sonnet/medium]`: Anonymisation panel — file upload (multi-file), ID column selector, personal column selector (to strip), pattern picker (sequential/hash/custom), generate button, download anonymised TSV(s) + mapping TSV + de-anonymisation instructions.  
  Depends: TL-ANON-1, TL-UI-SHELL-1.
