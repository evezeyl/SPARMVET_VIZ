---
tags:
  - data_types
  - wrangling
  - input_fields
  - output_fields
  - transformer
aliases:
  - Authorized data types
---



For the `input_fields` (and `output_fields`) in a manifest, the following data types are authorized for representing string-based data:

### 1. `categorical` (Recommended)

This is the standard type for most string data in the project (e.g., `sample_id`, `taxon`, `country`, `gene`).

- **Behavior**: It maps to Polars' `pl.Categorical` during the final contract phase.
- **Use Case**: Use this for any column with repeating values or for primary identifiers to ensure they are handled as discrete categories rather than raw text.

### 2. `string` (or `utf8`)

This maps directly to a raw Polars `pl.String` (formerly `Utf8`).

- **Behavior**: It treats the data as unregulated text.
- **Use Case**: Use this for high-cardinality data or descriptions where categorization doesn't provide a performance benefit.

---

### Internal Mapping Summary

Based on the `DataIngestor` and `debug_wrangler.py` logic, the system translates your manifest types as follows:

|Manifest Type|Polars Interpretation (Ingestion)|Polars Type (Output Contract)|
|---|---|---|
|**`categorical`**|`pl.String` (Internal Load)|**`pl.Categorical`**|
|**`string`**|`pl.String`|**`pl.String`**|
|**`utf8`**|`pl.String`|**`pl.String`**|

TIP

**Primary Keys**: Ensure that `sample_id` is always set to `type: categorical`. Using `numeric` for IDs often causes join mismatches during assembly because the engine expects strict type parity across datasets.