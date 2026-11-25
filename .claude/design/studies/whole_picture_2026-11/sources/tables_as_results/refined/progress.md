# progress (builder-opus, tables as results, refined proposal, 2026-11-22)
Done: read principles, compliance, M555, round 5 files, ledger lines, demo slice files, spec/tiers/graph/check.
Slice chosen: MLST + metadata_schema -> join MLST_with_metadata (real tier1 + tier2) -> plot mlst_bar; derived table from MLST_with_metadata after tier 2 = QA_aggregated_no_key steps (year_label, group_by) -> plot + table results. Appendix: reads summary (FastP_with_metadata).
Next: today's file in try/today, validate + build; routes; new-form files + check; write PROPOSAL_FOR_THE_OWNER.md.
Done (2): today file passes validate + data check and builds (T1 42, T2 33, summary 6 rows); routes 1=2=3 equal; reads summary routes equal (9 rows); audit walk run (i, ii, iii); new-form checks run (outputs in try/out/); duplicate plot id across groups: not refused by a plain rule (finding).
Next: write PROPOSAL_FOR_THE_OWNER.md from PROPOSAL.template.md (placeholders filled by fill_doc.py), check every yaml block loads.
Done (3): PROPOSAL_FOR_THE_OWNER.md written by try/fill_doc.py from PROPOSAL.template.md (1202 lines, 5 yaml blocks, each loaded with yaml.safe_load). All scripts rerun after the last file change; outputs in try/out/.
Next: nothing; report sent to the coordinator. Nothing outside refined/ was changed.
