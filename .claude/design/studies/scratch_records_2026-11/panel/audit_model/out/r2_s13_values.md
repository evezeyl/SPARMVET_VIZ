## Value changes of columns that keep name and type through a step (distinct values of the column after a step not all in the column before, or more nulls with the same row count)
- MLST T1:3 polars_fill_null column `sequence_type`: NEW VALUES ['Non Determined']
- VirulenceFinder T1:9 polars_str_strip_chars column `VF_protein`: NEW VALUES ['ABC transporter protein MchF', 'Adherence protein', 'Aerobactin synthetase', 'Avian E.coli haemolysin']

## Actions used in recipe 1 (steps at T1 and T2 of all 28 tables, recipe steps only): {'polars_unpivot': 3, 'polars_with_columns': 12, 'polars_explode': 2, 'polars_str_strip_chars': 3, 'polars_unique': 2, 'polars_str_splitn': 2, 'polars_unnest': 2, 'polars_rename': 5, 'polars_cast': 3, 'modif_filter': 5, 'polars_drop': 2, 'polars_sort': 2, 'polars_select': 10, 'polars_fill_null': 1, 'polars_join': 21, 'polars_group_by': 4}
