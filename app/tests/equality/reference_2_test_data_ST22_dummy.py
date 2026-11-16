"""The tables of the recipe `2_test_data_ST22_dummy`, written BY HAND in plain Polars and plotnine (EQUALITY-CHECK-1).

PROVISIONAL (Eve's rule of 2026-11-15).

Independence rule: this file was written from the MEANING of the recipe (the recipe files, the format spec, the user
documentation of the actions, the Polars documentation), not from the engine's code. It imports only `polars`,
`plotnine` and the standard library: nothing from `libs/` or `app/`. Do not "fix" it to match the engine: a
difference between this file and the engine is a finding (`FINDINGS.md`).

Each step quotes, in a comment, the recipe line it implements (`recipe:` lines). Where the recipe is silent, the
comment says "recipe silent" and what was chosen.
"""
from pathlib import Path

import plotnine as p9
import polars as pl

# recipe: input_fields/*.yaml -- slug: type, original_name (the exact header in the file)
METADATA_FIELDS = {"sample_id": ("sample_id", pl.String), "Source": ("Source", pl.String),
                   "Year": ("Year", pl.Float64), "Country": ("Country", pl.String)}
AMR_FIELDS = {"sample_id": ("sample_id", pl.String), "gene": ("Gene", pl.String),
              "predicted_phenotype": ("Predicted Phenotype", pl.String), "identity": ("%Identity", pl.Float64),
              "overlap": ("%Overlap", pl.Float64), "accession": ("Accession", pl.String)}
PLASMID_FIELDS = {"sample_id": ("sample_id", pl.String), "plasmid_name": ("Plasmid", pl.String),
                  "identity": ("%Identity", pl.Float64), "overlap": ("%Overlap", pl.Float64),
                  "accession": ("Accession", pl.String)}


def read_schema(path: Path, fields: dict, null_values: list[str], strip: bool = True) -> pl.DataFrame:
    """Read one data file as the recipe says: read text, strip it, make the null texts missing, then give the types.

    recipe: `strip: true` (before the null texts), `null_values: [...]` (exact texts that mean missing),
    `input_fields` (only the declared columns are read, named by their slug, typed as declared).
    """
    # Everything is read as text; an empty cell stays "" (the recipe, not the reader, says what is missing).
    text = pl.read_csv(path, separator="\t", infer_schema=False, missing_utf8_is_empty_string=True,
                       quote_char=None)
    out = {}
    for slug, (original_name, dtype) in fields.items():
        col = pl.col(original_name)
        if strip:
            col = col.str.strip_chars()
        col = pl.when(col.is_in(null_values)).then(None).otherwise(col)
        out[slug] = col.cast(dtype)
    return text.select(**out)


def schema_table(name: str, files: dict[str, Path], null_values: list[str]) -> pl.DataFrame:
    """The tier 1 table of one data schema (metadata_schema, amr_data, plasmid_data)."""
    if name == "metadata_schema":
        # recipe: wrangling: {tier1: []}
        return read_schema(files["metadata"], METADATA_FIELDS, null_values)
    if name == "amr_data":
        amr = read_schema(files["amr"], AMR_FIELDS, null_values)
        # recipe (wrangling/amr_data.yaml): modif_filter identity ge 90, na: remove
        #   keep identity >= 90; a missing identity is removed (what a comparison does in Polars); a NaN is a number
        #   (docs: "A NaN is a number, not a missing value, and `na` does not touch it"), so NaN >= 90 is true.
        amr = amr.filter(pl.col("identity") >= 90)
        # recipe: modif_filter overlap ge 60, na: remove (same rule)
        return amr.filter(pl.col("overlap") >= 60)
    if name == "plasmid_data":
        plasmid = read_schema(files["plasmid"], PLASMID_FIELDS, null_values)
        # recipe (wrangling/plasmid_data.yaml): the same two filters
        return plasmid.filter(pl.col("identity") >= 90).filter(pl.col("overlap") >= 60)
    raise KeyError(name)


def _sort_year_source_country(frame: pl.DataFrame) -> pl.DataFrame:
    # recipe: polars_sort by [Year, Source, Country], maintain_order: true
    #   Meaning: ascending on the written value of each column, ties keep the order of the rows before the sort.
    #   Source and Country are sorted by their text, not by the order in which the categories were first seen.
    #   recipe silent: where a missing value goes. Polars' default is first (nulls_last=False); chosen here.
    return frame.sort(
        [pl.col("Year"), pl.col("Source").cast(pl.String), pl.col("Country").cast(pl.String)],
        maintain_order=True,
    )


def _year_to_text(frame: pl.DataFrame) -> pl.DataFrame:
    """recipe: polars_cast Year Int64 then String ("2022", not "2022.0").

    Meaning: the Year is a whole number written without ".0". A year that is not whole (2023.5) has no such reading,
    so it is refused here (plain Polars `cast(Int64)` would drop the decimals without a message).
    """
    years = frame["Year"].drop_nulls()
    if (years != years.floor()).any():
        raise ValueError("Year holds a value that is not a whole number")
    return frame.with_columns(pl.col("Year").cast(pl.Int64)).with_columns(pl.col("Year").cast(pl.String))


def amr_join(amr: pl.DataFrame, metadata: pl.DataFrame) -> pl.DataFrame:
    """recipe: joins.AMR_Profile_Joint (assembly/AMR_Profile_Joint.yaml), tier1 steps in order."""
    # Step 1: predicted_phenotype_clean = predicted_phenotype as text, stripped, lower case
    t = amr.with_columns(
        predicted_phenotype_clean=pl.col("predicted_phenotype").cast(pl.String).str.strip_chars().str.to_lowercase())
    # Step 2: polars_join right_ingredient metadata_schema, on [sample_id], how inner, maintain_order left_right
    #   The base table is amr_data (first ingredient). A row whose key has no match, or whose key is missing, is dropped.
    t = t.join(metadata, on="sample_id", how="inner", maintain_order="left_right")
    # Step 3: Year float -> Int64 -> String ("2022", not "2022.0")
    t = _year_to_text(t)
    # Step 4: is_multi_resistant_bool: "sample carries >1 distinct resistance class" (comment of the recipe;
    #   README: "isolates resistant to >= 2 antimicrobial classes"). A missing phenotype is not a class, so it is not
    #   counted. The flag is computed on the rows that survived the filters and the join (the steps' order).
    t = t.with_columns(
        is_multi_resistant_bool=pl.col("predicted_phenotype_clean").drop_nulls().n_unique().over("sample_id") > 1)
    # Step 5: Multiresistant = "Yes" when the flag is true, else "No"
    t = t.with_columns(Multiresistant=pl.when(pl.col("is_multi_resistant_bool")).then(pl.lit("Yes")).otherwise(pl.lit("No")))
    # Step 6: sort Year, Source, Country (stable)
    t = _sort_year_source_country(t)
    # polars_select: the eight columns, in this order
    return t.select("Year", "Source", "Country", "gene", "predicted_phenotype_clean", "sample_id", "accession",
                    "Multiresistant")


def plasmid_join(plasmid: pl.DataFrame, metadata: pl.DataFrame) -> pl.DataFrame:
    """recipe: joins.Plasmid_Profile_Joint (assembly/Plasmid_Profile_Joint.yaml), tier1 steps in order."""
    # Step 1: inner join metadata on sample_id, left rows keep their order
    t = plasmid.join(metadata, on="sample_id", how="inner", maintain_order="left_right")
    # Step 2: Year float -> Int64 -> String
    t = _year_to_text(t)
    # Step 3: sort Year, Source, Country (stable)
    t = _sort_year_source_country(t)
    return t.select("Year", "Source", "Country", "plasmid_name", "sample_id", "accession")


def reference_table(name: str, files: dict[str, Path], null_values: list[str]) -> pl.DataFrame:
    """One table of the recipe by name. The tier 2 of every table is its tier 1 (no `tier2` step in this recipe).

    Raises when the data cannot be read or cast as the recipe says (an input of a join that cannot be built makes the
    join impossible).
    """
    if name in ("metadata_schema", "amr_data", "plasmid_data"):
        return schema_table(name, files, null_values)
    metadata = schema_table("metadata_schema", files, null_values)
    if name == "AMR_Profile_Joint":
        return amr_join(schema_table("amr_data", files, null_values), metadata)
    if name == "Plasmid_Profile_Joint":
        return plasmid_join(schema_table("plasmid_data", files, null_values), metadata)
    raise KeyError(name)


# ---- the plots -------------------------------------------------------------------------------------------------

# recipe: analysis_groups -> plot id -> (target table, mapping, labs)
PLOT_TARGETS = {
    "multi_resistance_by_country": "AMR_Profile_Joint",
    "multi_resistance_by_source": "AMR_Profile_Joint",
    "plasmid_prevalence_by_country": "Plasmid_Profile_Joint",
}


def reference_plot(plot_id: str, table: pl.DataFrame) -> p9.ggplot:
    """The plot written directly in plotnine from `plots/<file>.yaml`.

    recipe: layers geom_bar, position_dodge (side by side bars), scale_x_discrete, labs; mapping x, fill,
    facet_by -> one panel per value; theme theme_light. No filter is stated in any plot: it draws the whole table.
    """
    data = table.to_pandas()
    if plot_id == "multi_resistance_by_country":
        return (p9.ggplot(data, p9.aes(x="Year", fill="Multiresistant")) + p9.geom_bar(position=p9.position_dodge())
                + p9.scale_x_discrete() + p9.labs(title="Multi-Resistance by Country", fill="Multiresistant", x="Year")
                + p9.facet_wrap("Country") + p9.theme_light())
    if plot_id == "multi_resistance_by_source":
        return (p9.ggplot(data, p9.aes(x="Year", fill="Multiresistant")) + p9.geom_bar(position=p9.position_dodge())
                + p9.scale_x_discrete() + p9.labs(title="Multi-Resistance by Source", fill="Multiresistant", x="Year")
                + p9.facet_wrap("Source") + p9.theme_light())
    if plot_id == "plasmid_prevalence_by_country":
        return (p9.ggplot(data, p9.aes(x="Year", fill="plasmid_name")) + p9.geom_bar(position=p9.position_dodge())
                + p9.scale_x_discrete() + p9.labs(title="Plasmid Prevalence by Country", fill="Plasmid Type", x="Year")
                + p9.facet_wrap("Country") + p9.theme_light())
    raise KeyError(plot_id)
