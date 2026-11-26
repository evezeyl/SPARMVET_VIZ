Probes (scratch): probe_a.py (tables), probe_b.py (data facts), probe_c.py (plot layer data), probe_d.py (order/dtypes).
Recipe 2_test_data_ST22_dummy: AMR tier1 hand==engine (70 rows, 16 multi-resistant of 38 samples, order equal).
Plot multi_resistance_by_country: counts per (Country,Year,fill) equal to hand ggplot; facet order differs (engine France,Norway,Germany; hand alphabetical).
Shipped data clean: filters remove 0 rows; 4/42 metadata samples vanish from AMR (inner join), 1 from plasmid; plot counts 70 gene rows not 38 samples.
