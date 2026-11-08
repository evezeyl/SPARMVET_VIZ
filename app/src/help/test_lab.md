## Test Lab — Quick Reference

**Test Lab** is a toolbox of stateless data-preparation utilities — each tool runs to completion and returns a downloadable result. Closing a tool resets it; nothing persists between runs except files you explicitly save.

### ID Reconciliation
Match two ID sets from different files (exact + fuzzy matching, pattern-based transformation suggestions), then save the result as a named ID transformation. One key column per run — composite keys belong in Blueprint's Joint Designer.

### Data analysis recipe Scaffolding
Generate a boilerplate data analysis recipe from uploaded files: inferred field types, primary-key candidate hints, and empty wrangling/plot stubs for you to fill in. Optionally bakes in ID Reconciliation steps produced above.

### Synthetic Data
Generate synthetic test data matching a schema (AquaSynthesizer), including named error scenarios, for testing data analysis recipes without real data.

### Anonymisation
Anonymise a column in an uploaded file, producing an anonymised output plus a mapping file for later de-anonymisation (join the mapping back in Blueprint).

### File Reformatting
Upload an XLSX/XLS/CSV/TSV file and convert it to TSV. For XLSX, pick which sheet(s) to extract; each becomes its own TSV.

### Access
Test Lab is gated by `test_lab_enabled` — available in developer and qa app features only, not visible to scientist-facing app features files.
