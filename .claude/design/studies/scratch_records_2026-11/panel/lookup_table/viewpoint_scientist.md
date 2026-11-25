Verdict: I do not oppose the design, but it needs the additions below. I ran the real join (Polars, rebuilding VF_gene with the recipe's split and strip steps) on assets/test_data/2_VIGAS-P_ST22_dummy/test_data_VIGAS_VirulenceFinder_20260307_105756.tsv and assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv. I did not run the app. Script: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/lookup_table/a.py

(a) What I ran
- The lookup has 11 rows with 11 unique keys, not 10.
- The long table has 984 rows, 42 samples and 48 distinct genes.
- The inner join leaves 342 rows. All 42 samples survive. 11 of the 48 genes are kept and 37 are dropped by design. All 11 lookup keys are found.
- A left join would keep 984 rows, so the filter would be lost silently.
- If the gene names were uppercase, the inner join gives 0 rows and no error.
- If the lookup keys had a trailing space, the inner join gives 0 rows and no error.
- If the lookup had one duplicated key (iss), the rows grow from 342 to 384 and no error is raised.
- Point 4 ("n matched, m not found") would catch the 0-row cases. Point 2 would catch the duplicate. Both are needed.

(b) Additions
1. Report both sides: data rows kept and dropped, distinct genes kept and dropped, and lookup keys never seen. A lookup key never seen, such as a typo, is the real silent error.
2. Make a zero-row result after the join a hard stop that names the lookup.
3. Refuse how: left with a lookup used as a filter, or require the recipe to say it is an annotation. Inner means filter and left means annotate. State this in the docs.
4. Check that the lookup key has no leading or trailing whitespace and no empty values. Case stays the user's choice. Show the case-folded overlap as information only.
5. Write the filtered result into the export bundle: the lookup file hash, the number of genes kept, and the list of genes dropped.

(c) Other table kinds (not run, from experience)

| Kind | What the id means | Check |
|---|---|---|
| Recode dictionary | the "from" value is the key | "from" unique; report unmapped values |
| Thresholds or ranges | a rule name, or a range per group | no overlapping ranges; min <= max; group unique |
| Many-to-many link | the pair (sample, X) is the key | pair unique; both sides exist |
| Long format | sample_id repeats | sample_id present; (sample, gene) unique |

(d) Clash
- is_entity_key is documented as informational: "the column that identifies the entity of the table" (docs/appendix/Standards_yaml.qmd, which I read). Gene_name identifies a gene, not a sample, so it does not clash.
- I would name the lookup field lookup_key, not key. D-0082 uses "keys" for join keys, so a bare key is ambiguous.
- I did not check how kind is used elsewhere.
