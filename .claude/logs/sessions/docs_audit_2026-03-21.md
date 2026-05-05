# Audit: Documentation Flagging (JSON & Mode B)
# Auditor: @dasharch
# Date: 2026-03-21

The following files in `./docs/` contain outdated terminology that conflicts with the current **YAML-Driven** and **Manual Upload** strategy. These sections are flagged for immediate correction in the next documentation cycle:

1. **[docs/architecture/core_architecture.qmd](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/docs/architecture/core_architecture.qmd)**
   - Flags: Mentions "JSON Schema" for Pillar 4.
   - Flags: Mentions "Mode B (API Connection)" as an active pillar.
   - Flagged as: **OUTDATED**.

2. **[docs/architecture/core_architecture_code.qmd](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/docs/architecture/core_architecture_code.qmd)**
   - Flags: Mentions "Pydantic/JSON" validation strategies.
   - Flagged as: **OUTDATED**.

3. **[docs/guide/testing.qmd](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/docs/guide/testing.qmd)**
   - Flags: Mentions "Schema testing against JSON files."
   - Flagged as: **OUTDATED**.

4. **[docs/appendix/DashBoard_Architect_v1.qmd](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/docs/appendix/DashBoard_Architect_v1.qmd)**
   - Flags: Legacy architecture diagrams showing JSON endpoints.
   - Flagged as: **OUTDATED**.

5. **[docs/modules/_config_mermaid.mmd](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/docs/modules/_config_mermaid.mmd)**
   - Flags: Mermaid diagram showing 'Mode B' connections.
   - Flagged as: **OUTDATED**.

**Decision:** Purge these mentions and replace with "YAML Manifest" and "Manual/Local Orchestration" respectively.
