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

#TODO here we need to consider secondary keys maybe - see the example manifest config/manifests/pipelines/1_test_data_ST22_dummy.yaml - need to verify the blueprint implementation seems now we have implemented composite key joints  - can this be reused ? 
#TODO also for the broiler plate - need to allow the !include and pre-split the bolerplate manifest in the main manifest and include fields - there is a file that describe the manifest structure - find and add information for the specifications

### Anonymisation (PROCESS 1: Real Data → Reversible Mapping)

Anonymisation takes a data file with an ID column and replaces all ID values with consistent synthetic equivalents. The same original ID always maps to the same anonymised ID. #TODO REVIEW : Mappings are output in tsv file - no specific acess control but plan for it if we can eventually implement later without refactoring. **Anonymisation handles ID/key columns only** — the rest of the data is passed through unchanged.

| Functionality | What the user can do |
|---|---|
| **Anonymise ID column** | Take a file with an ID column; replace all ID values with consistent synthetic equivalents. Same original_id always → same anon_id (preserves joins across files). Safe to share, reversible by authorized users |
| **Access-controlled mapping storage** | Store original_id → anon_id mapping (TSV). #TODO - [Not now : with user role restrictions (admin only, researchers, specific users)]; TSV can be joined with anonymised data to deidentify results |
#TODO -> maybe we need a "de-annomisation functionality then also
| **ID pattern for synthetic IDs** | Choose how synthetic IDs are generated: simple sequencing (ANON_0001, ANON_0002, ...), hash-based, or custom pattern |
| **Ensure ID consistency across files** | When anonymising multiple related files with the same ID column, same original_id maps to same anon_id everywhere (required for joins to remain valid post-anonymisation) |

### Synthetic / Test Data Generation (PROCESS 2: Schema → Fresh Data)

Synthetic data generation creates independent, fresh data matching a schema. No mapping to originals — used for testing or safe sharing without reversibility concerns.

| Functionality | What the user can do |
|---|---|
| **Generate clean synthetic data from schema** | Define column names, types, constraints; system generates plausible synthetic data matching that schema | #TODO read the data files and create synthetic data - there is already a script that does part of this - see maybe in assets/scripts or scripts? 
| **Generate synthetic data from example** | Upload real data; system learns schema, distributions, patterns; generates synthetic data mimicking structure without linking to originals |
| **Control synthetic distributions** | Set min/max, categorical allowed values, ID patterns, string format per column | #TODO Allow adding categorical values for increasing diversity dataset
| **Inject controlled errors / edge cases** | Generate datasets with intentional defects (missing values, wrong types, duplicate IDs, out-of-range values, 7 empty groups, single-row groups, non-matching IDs) for testing | #TODO should we add wrong types also and other schema errors ? #TODO we need to think about possibility to add later other edge cases if necessary  
| **Named error scenarios** | Save & reload named edge-case scenario definitions to use as regression test suite |

### ID Reconciliation Engine (for Manifest Scaffolding & Data Ingestion)

| Functionality | What the user can do |
|---|---|
| **Multi-file ID alignment** | Upload 2–6 files with candidate ID columns; the engine analyzes format compatibility, groups compatible files, and suggests matching sequence |
| **Pairwise ID matching** | For each file pair, view side-by-side table of IDs with match status (exact, pattern-based, unmatched); certainty score per pair (not global) |
| **Pattern-based matching suggestions** | Engine suggests transformation rules (prefix/suffix removal, delimiter extraction, case normalization, substring extraction, regex); user verifies each match < 100% certainty |
| **Recode workflow** | If pattern matching insufficient, user can clean problematic IDs (trim, extract, normalize, custom regex); engine re-runs matching after cleaning |
| **Transformation recipe storage** | Save declarative recipe (YAML format) with audit log for reuse on future imports of same file types | #TODO audit log is more to have it human understandable of the steps that were necessary - easier to read
| **Progressive processing** | Handle large files via sample-based preview → full-file matching; user verifies preview, then engine processes all rows | #TODO IMPORTANT! this is not what I think we had decided, we had decided we can do bach after baches if necessary so not do all at once but do all if necessary 
| **Many-to-many detection & suppression** | Flag if one ID maps to multiple others (indicates data error); offer option to suppress and continue if user confirms intentional |

#TODO - we need to be able to use this and then create the boilerplate manifest - we need to think how to allow standalone and continuation of workflow ? 
---

## ID Reconciliation Engine — Detailed Design

### Purpose & Scope

The ID Reconciliation Engine is the foundational tool for **Manifest Scaffolding**. Before TEST_LAB can generate a boilerplate manifest, join keys must be validated across all input files. The engine:

1. Analyzes ID formats across multiple files
2. Suggests compatible file pairs and matching order
3. Performs pairwise matching with per-pair certainty scores
4. Requires user verification for all matches < 100%> - #TODO 100% certainty is exact string match
5. Generates reusable transformation recipes
6. Flags data quality issues (many-to-many relationships) #TODO think about secondary key possibilities ? 

**Integration point:** Manifest Scaffolding workflow calls the ID Reconciliation Engine as step 1 before boilerplate generation.

### Workflow: Pairwise Matching Example

```
User uploads: metadata.tsv (sample_id column) + amr_results.tsv (S_id column)
              │
              ├─ PRE-CHECK: Analyze formats
              │   - metadata: "sample_S001", "sample_S002", "sample_S999"
              │   - amr_results: "S001", "S002", "S999_QC_pass"
              │   ✓ Formats are compatible (IDs are present in both)
              #TODO type detection ? or where ? 
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
              │   100% matches → auto-accept (user can override) #TODO defined as exact string match
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

#TODO option for review - unmatched ? keep or delete ? 

### Design Decisions Locked

#### 1. Certainty Scoring (Per Pair, Not Global)

Each ID pair receives an individual certainty score:

| Score | Meaning | User Action |
|---|---|---|
| **100%** | Exact string match | Auto-accept (user can override/reject) |
| **95%** | Pattern match (e.g., remove prefix, extract from delimiter) | MUST manually verify each pair | #TODO after verify ? update match to 100% ? in case we need a second round ? 
| **80%** | Fuzzy match (e.g., Levenshtein distance, substring similarity) | MUST manually verify each pair |
| **0%** | No match found | User decides: leave unmatched, try manual pairing, recode, or remove |

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
#TODO we need to check that the audit_log: key is supported by ingest, but that is a good idea yes to it - best would be to have the audit log always as !include file - so it can eventually be used separately - new rule in manifest ADRs ? 


Recipe is reusable: future imports of the same file types apply these steps automatically.

#### 3. Visualization: Side-by-Side Table

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
```
#TODO Here I think user should first check all those 100% matched and then bulk accept those. Then procede in decreaseing "certainty" accepting match, or manually maching other samples so the review step. I think the app should be smart eg to find eventuall new patterns matching ? solutions ? So basically we fix the easier first and then go to the difficilt cases
User can:
- Click "Review" → see transformation steps that produced the match
- Click "❌" → choose "Leave unmatched" | "Manual pick" | "Recode"
- Bulk-accept all 100% matches or review individually

#### 4. Progressive Matching (Large Files)

For files with > 1000 rows:
1. Show sample-based preview (first 100 rows, random 100 rows, worst-case sample) #TODO we need a systematic sorting -> by matching decreasing - so we can validate sequentially and fix the most problematic at the end - with manual help
2. User verifies preview #TODO will need a verify button ? associated with each preview ? how can/will this work - I need proposals
3. Engine processes full file in background, shows progress #TODO we need to think about load/time - can it be chunked or not ? how to make that as efficiently compute/memory RAM as possible ? options ? 
4. User reviews final unmatched set #TODO - might also need to be chunked if there are many unmatched

#### 5. Many-to-Many Detection & Suppression

**Default:** Flag as data error (suggests duplicate or misaligned data). #TODO Warning - Need to check intent - is it supposed to be unique or is it supposed to allow many -> usually we can have one to many I do not think we will see much cases with many to many We need to think here 

**Example:**
```
sample_S001 matches → S001 AND S001_replicate (many-to-many detected)
                      ↓
                      Banner: "⚠️ Many-to-many relationship detected.
                               This usually indicates duplicate or misaligned data.
                               Review before proceeding. [Suppress & Continue]"
```

If user confirms "Suppress & Continue," the engine: #TODO Yes good ! important to show that use decided to buypass a warning - maybe user could have to write a reason for bypassing ? that would help clarify why ? 
- Logs the warning in audit trail
- Keeps the many-to-many pair (user's responsibility now)
- Proceeds with matching

**Future use case (deferred):** Internal joins based on results (e.g., same gene detected multiple times). Assess at usage time if needed. #TODO - maybe we should not defer afterwards . as this in a way works with the warning above no ? 

#### 6. Recode Workflow (If Pattern Matching Fails)

If pattern detection + user manual pairing insufficient:
#TODO - we might also have an option to suggest the user to clean the names correctly if there are many different patterns and then start again the process - afterall user should also allow some consistency - this might allow to limit special cases - they are allowed to verify their data before retrying (eg. we do not want to have to treat large amount of manual cases eg max 100 ? or is it even too much ? )


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

---

## Manifest Scaffolding — Primary Key Selection & Recipe Integration

### Workflow: From ID Reconciliation to Manifest Boilerplate

After ID reconciliation is complete and user has verified matches, the scaffolding workflow:

```
1. User identifies primary keys in input_fields
   - For each file/schema, which columns are the join keys?
   - E.g., metadata_schema → sample_id
   - E.g., amr_schema → sample_id
   - User confirms these are unique (or will become unique after cleaning)

2. System validates primary key uniqueness
   - Check if columns have duplicate values (before cleaning)
   - Flag problematic duplicates (data quality warning)

3. System generates boilerplate manifest with ID recipes baked into tier1
   - Input fields: column names, types, descriptions from actual data
   - Tier1 wrangling: includes ID reconciliation recipes (transformations)
   - Tier1 wrangling: includes validation checks (drop duplicates on primary key, filter missing)
   - Joins: uses verified join keys from ID reconciliation
   - Output fields: inherited from input after wrangling

4. User downloads boilerplate manifest
   - Ready to edit in BLUEPRINT
   - Primary keys already defined in input_fields
   - ID cleaning (recipes) already configured in tier1 wrangling
   - Validation checks already in place
   - Join logic with verified keys already sketched
```

### Example Boilerplate Manifest (with recipes baked in)

```yaml
info:
  id: sample_amr_pipeline
  description: "Sample metadata + AMR results"

input_schemas:
  metadata_schema:
    # PRIMARY KEY defined in input_fields
    input_fields:
      sample_id:
        type: categorical
        description: "Sample identifier (PRIMARY KEY — must be unique)"
      collection_date: {type: string, description: "Collection date"}
      site: {type: categorical}
      age: {type: string}
    
    wrangling:
      tier1:
        # ID Reconciliation recipe (step 1: clean the primary key)
        - action: remove_prefix
          columns: [sample_id]
          pattern: "sample_"
        
        # Optional: normalize other fields
        - action: cast
          columns: [collection_date]
          dtype: String
        
        # Validation (step 2: ensure primary key uniqueness)
        - action: drop_duplicates
          columns: [sample_id]
        
        # Filter missing/empty primary key values
        - action: filter_eq
          column: sample_id
          value: ""
          negate: true

  amr_schema:
    # PRIMARY KEY defined in input_fields
    input_fields:
      sample_id:
        type: categorical
        description: "Sample ID (PRIMARY KEY — must be unique)"
      amr_gene: {type: categorical}
      phenotype: {type: categorical}
    
    wrangling:
      tier1:
        # ID Reconciliation recipe (normalize to match metadata_schema.sample_id)
        - action: extract_delimiter
          column: sample_id
          delimiter: "_"
          position: 0
        
        # Validation
        - action: drop_duplicates
          columns: [sample_id]
        
        - action: filter_eq
          column: sample_id
          value: ""
          negate: true

join_manifests:
  sample_amr_joint:
    left_ingredient: metadata_schema
    recipe:
      - action: join
        right_ingredient: amr_schema
        'on': sample_id  # Both PRIMARY KEYs cleaned, now aligned
        how: inner

output_fields:
  # (Generated from input after wrangling)
  sample_id: {type: categorical}
  collection_date: {type: string}
  site: {type: categorical}
  age: {type: string}
  amr_gene: {type: categorical}
  phenotype: {type: categorical}
```

**Key points:**
- Primary keys defined in `input_fields` for each schema
- ID cleaning (from reconciliation) in `tier1` wrangling
- Duplicate/missing-value checks also in `tier1`
- Join uses the cleaned, validated primary keys
- User can edit this boilerplate in BLUEPRINT to add analysis_groups, plots, etc.

---

## Anonymisation — Design & Workflow (PROCESS 1)

### Design Decisions Locked

**Q1: ID Mapping & Reversibility** → **Scenario B (Reversible with Access Control)**
- Store original_id → anon_id mapping (YAML file)
- Access-controlled: admin/researcher/specific users can deidentify
- User/role who performs anonymisation decides access level

**Q2: Access Control** → **By User Role**
- Admin: sees original data + mapping
- Researcher (if authorized): sees anonymised data + mapping
- Public/Other: sees anonymised data only, no mapping
- Access control handled by deployment profile + persona flags (not by TEST_LAB itself)

**Q3: ID Pattern for Synthetic IDs** → **Simple Sequencing (with options)**
- Default: ANON_0001, ANON_0002, ANON_0003, ... (simple sequencing)
- Option: User can choose custom pattern or hash-based
- Consistency required: all synthetic IDs in anonymised dataset follow the same pattern

**Q5: ID Alignment Across Files** → **Same Anon ID for Same Original ID**
- When anonymising multiple related files, same original_id always maps to same anon_id
- Ensures joins remain valid post-anonymisation
- Use ID Reconciliation Engine to validate join keys before & after anonymisation

### Workflow: Anonymising ID Column Across Files

```
1. User uploads files to anonymise (1+ files with same ID column)
   - E.g., metadata.tsv (sample_id) + results.tsv (sample_id)

2. System runs ID reconciliation (optional, if IDs don't match between files)
   - Validates that ID columns are correctly aligned
   - Identifies primary key column name

3. User configures anonymisation
   - Select ID column: sample_id
   - Choose ID pattern: ANON_0001, ANON_0002, ... (or custom)
   - Confirm: "apply to all selected files"

4. System generates anonymised datasets
   - Same original_id → same anon_id across all files (preserves joins)
   - All other columns: unchanged, passed through
   - Output:
     * anonymised_metadata.tsv (with anon_sample_id)
     * anonymised_results.tsv (with anon_sample_id)
     * mapping_sample_id.tsv (access-controlled; for deidentification)

5. User assigns access level to mapping file
   - Who can access the mapping? (admin / researcher / public)
   - (Handled by deployment profile, not TEST_LAB)

6. Anonymised datasets are safe to share
   - IDs replaced, other columns unchanged
   - Authorized users can deidentify via join with mapping_sample_id.tsv:
     ```
     anonymised_results.tsv ← JOIN ← mapping_sample_id.tsv
     (on anon_sample_id)
     → results with original_sample_id restored
     ```
```

### Example Anonymisation Configuration

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
3. **mapping_sample_id.tsv** — Joinable TSV: original_sample_id ↔ anon_sample_id (access-controlled)

Example mapping_sample_id.tsv:
```
original_sample_id	anon_sample_id
S001	ANON_0001
S002	ANON_0002
S003	ANON_0003
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

### Workflow: Generate Synthetic Data

```
1. User chooses input source:
   Option A: Upload schema (column names, types, constraints)
   Option B: Upload example real data (system learns schema + distributions)

2. User configures per-column generation strategy
   - Numeric: min, max, distribution (uniform, normal, etc.)
   - Categorical: allowed_values
   - ID: pattern (sequencing, hash, custom)
   - String: length, format, freetext variety
   - Error injection: % missing, % wrong type, % duplicates, etc.

3. System generates synthetic dataset
   - Independent from any original data (no mapping)
   - Matches schema & distributions
   - Ready for testing

4. User can save error scenario
   - Name: "edge_case_duplicates_10pct"
   - Definition: {columns, error_rates, constraints}
   - Reusable for regression testing
```

### Example Synthetic Data Configuration (YAML)

```yaml
synthetic_data_config:
  source: schema  # or "example_data"
  
  columns:
    sample_id:
      type: categorical
      pattern: "SAMPLE_{:05d}"
      size: 100  # Generate 100 unique samples
    
    collection_date:
      type: numeric  # Unix timestamp
      min: 1704067200  # 2024-01-01
      max: 1735689599  # 2024-12-31
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
    
    test_result:
      type: categorical
      allowed_values: ["positive", "negative"]
    
    # Error injection
    missing_value_columns:
      - {column: age, rate: 0.02}  # 2% missing
      - {column: test_result, rate: 0.01}
    
    wrong_type_columns:
      - {column: age, rate: 0.01}  # 1% will be string instead of numeric
    
    duplicate_ids:
      rate: 0.00  # 0% duplicates (0 = no duplicates)
  
  output:
    rows: 100
    filename: "synthetic_test_data.tsv"
```

### Named Error Scenarios (Saved & Reusable)

Users can save scenario definitions for regression testing:

```yaml
error_scenario:
  name: "edge_case_duplicates_10pct"
  description: "10% duplicate sample IDs to test join error handling"
  
  columns:
    sample_id:
      type: categorical
      pattern: "SAMPLE_{:05d}"
      size: 100
      # Override: force duplicates
      duplicate_ids:
        rate: 0.10  # 10% will be duplicates
    
    collection_date:
      type: numeric
      min: 1704067200
      max: 1735689599
    
    # ... other columns ...
  
  output:
    rows: 100
    filename: "synthetic_edge_case_duplicates_10pct.tsv"
```

When user later wants to run the same test:
```bash
TEST_LAB.generate_synthetic_data(scenario_name="edge_case_duplicates_10pct")
# Generates: synthetic_edge_case_duplicates_10pct.tsv (identical structure, same error patterns)
```

---

## Non-Goals

- TEST_LAB does not run the main analysis — that is HOME.
- TEST_LAB does not build or edit manifests beyond generating a boilerplate scaffold — that is BLUEPRINT.
- TEST_LAB does not curate or share recipes — that is GALLERY.
- TEST_LAB does not permanently store anonymised data on behalf of the user — it produces files the user downloads.

---

## Key Design Constraints

- **Stateless tools**: each TEST_LAB utility runs to completion and returns a file or a result. No persistent session state between tool invocations (except named test scenarios, which are saved as files).
- **No data leaves the server**: anonymisation and synthetic generation happen server-side; the user downloads the result. Raw data is never sent to an external service.
- **Pattern helper shared with BLUEPRINT**: the ID/column pattern matching logic should be the same component. Design for reuse from the start.
- **Positive inclusion** (ADR-071): TEST_LAB panel is only mounted when `test_lab_enabled` is true in persona config.
- **Audit trail**: file-generation operations should log what was produced (filename, schema, row count, generation parameters) to the session audit log.

---

## Code Modules

| Code module | Role |
|---|---|
| `test_lab_studio.py` | UI and server handlers for all TEST_LAB tools |

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

- **Pattern helper**: shared component with BLUEPRINT, or separate implementations? Needs a decision before building either (to avoid duplication).
- **Anonymisation fidelity**: how closely should synthetic distributions match the real data? Full distributional match (harder, slower) vs. same types + plausible ranges (simpler, sufficient for most cases)?
- **Test scenario format**: how are named error scenarios stored? A JSON schema + generation params file seems cleanest. Where does it live (session dir? dedicated test_lab dir?)?
- **Boilerplate manifest scope**: should the scaffold include suggested wrangle steps, or only the column references? Starting with column references only keeps scope tight.
- **UI structure**: one tab per tool category, or a single list with a category filter? Start with tabs given the distinct tool types.
