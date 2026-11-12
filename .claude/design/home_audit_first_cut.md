# A smaller first audit version (PROPOSAL, not decided)

> **PARKED (2026-11-12, Eve):** a build plan written before the design is agreed. Input for the plan stage, not the plan.

**Written for:** Eve, for the audit-planning review of 2026-11-12. **Status:** proposal. Nothing here is built or decided; it only makes
the "smaller first version" of `home_audit_reading_guide.md` section 6 concrete so that the review can accept, change or drop it.
**Sources:** `home_audit_steps.md` sections 5, 14, 16, 19 and 20 (D1-D14); issues #60, #61, #62, #63, #64.

## 1. Why a cut at all

The full design (audit mode, reach selector, levels 0-3, separate audit cache, lineage map, three-step dialog) is large. The demo needs figures
that are scientifically safe, not the whole screen. The cut keeps today's **per-plot audit steps** (nothing is replaced, nothing is orphaned)
and adds the safeguards that matter most for correctness and for the reader of the published figure. Every piece of the cut is a **pure module
that the full design reuses**, so nothing built here has to be undone later (this is the test of the cut: a piece that the full design would
throw away is not in it).

## 2. What is in the cut (in build order; each piece shippable alone)

| # | Piece | Source in the design | Reused later as | Needs from Eve |
|---|---|---|---|---|
| 0 | Engine correctness: #62 integer thresholds, #61 keys, one shared filter implementation; NA information (#63 step 1); QA canaries as the safety net | brief WP1-WP3a, section 18 | the base of everything | nothing |
| 1 | **NA rule** (#63 step 2): "NA (missing)" is a visible value; an optional `na` parameter on the filter actions (default = today's behaviour, passed explicitly by the audit engine, VizFactory and the translator); the step records it | section 19 NA rule | step compiler (D3) | **decision 2** (default) |
| 2 | **Entities, not only rows** (I1): in the existing "Send to Audit" dialog show rows and samples before/after and the samples that lose all their rows | section 19 I1 | the check list of the three-step dialog | decision 5 (keys) |
| 3 | **"Which plots does this reach" (I2, S3b)**: before Apply, say "N plots contain this column, M do not: the sample stays visible there" and ask for "I understand". This is the honest answer to the core flaw of #60 inside the old per-plot model | sections 18, 19 I2 | reach selector (section 5) | decision 11 (first checks) |
| 4 | **Guard-rail registry, first entries**: C1 (samples removed downstream of population statistics), C3 (incomplete exclusion: the value or a look-alike is still there), W4 (drop of a used column, #59). One pure module, one entry per check (id, level, message, test) | section 19 | the full registry | decisions 11, 12 |
| 5 | **Reason category** (technical failure, contamination, duplicate, out of scope, outlier by value, other) + free text where required, stored in the step | section 19 | step record | decision 3 |
| 6 | **Event log** (append-only; the step list is derived; undo is an event) with `schema_version` | D2, D13 | event store | decision 9 (touches the session format: confirm) |
| 7 | **Pre-export review screen**: methods paragraph, attrition table, acknowledged warnings and overrides, broken steps; the user attests | D5 | the same screen | decision 12 |

## 3. What is NOT in the cut (stays as today, or waits)

Audit mode and the mode switch; the reach selector and levels 0-2 (a sample removed "everywhere" at the sources); the separate audit cache; the lineage map and
the project overview; the three-step dialog with the before/after plot preview; removal of My view, Compare and "Plot to show"; background computation.
**Honest limit:** with per-plot steps only, "remove this sample from every plot" is still a set of per-plot steps. The cut reduces the risk (pieces 2-4 tell
the user what happens and what does not) but does **not** remove the structural problem of #60. That needs levels 0-2, i.e. the full design.

## 4. How it is tested (uses what exists)

- Canaries (`app/tests/test_qa_canaries.py`, brief section 0b): `QA_AMR_per_sample` for stage and for plots that lack the column, `QA_ST_with_NA` for the NA rule,
  `QA_L50_integer` for thresholds, `QA_year_types` for value types.
- Each piece: a headless test with an independent oracle (Polars on the same frame), a mutation check, and for pieces 2-4, 7 a browser test with a screenshot looked at.
- Property tests (`hypothesis`, D9) only for pieces 0, 1 and 6 in this cut, and only if Eve accepts the new dev dependency (decision 12).
- The impact list of `home_audit_steps.md` section 14 is retested for every piece that changes a saved or exported file (piece 6 and 7).

## 5. Decisions the cut needs (all in the reading guide, section 3)

2 NA default; 3 reason categories; 5 keys (`is_primary_key` + join steps, inferred when missing); 9 event log (and that the session format changes); 11 the first check
list and the thresholds (20 %, fewer than 3 entities); 12 D1-D14 in part (`hypothesis`, policy block); 13 legacy names kept. **Not needed for the cut:** 1 stage and
reach, 4 caption, 6 reach selector, 7 audit table selector, 8 trial computation, 10 lineage map.

## 6. Risks and how the review can reduce them

- The cut may look "done" to a user and hide the limit of section 3: say it in the help ("Before you audit") and in the dialog text of piece 3.
- Piece 6 changes the session format: confirm decision 9 first; old sessions map to plot-level events (section 4 of the audit design).
- Warning fatigue (section 20): pieces 3 and 4 add warnings; keep them few, specific and numbered, and test the wording with two or three scientists before it is final.

## 7. After the cut

Build the recipe graph (D1) from the key mapping of piece 0, the step compiler (D3) from pieces 1, 4 and 5, then audit mode, the cache and the lineage map in the
order of D14. Everything above is reused; the replaced items are listed in `tasks.md` (`AUDIT-REPLACE-1`).
