# The two export modes: what is decided, what is drawn, what is built, and the one question for Eve

Coordinator, 2026-11-18, 16:58 by the clock. Digest of a scout's read-only survey (`dev`, `5496b9b1`): every line below was READ at the place named; nothing was run. Asked for by the review session (channel M316).

## Her words so far (ledger)

- 2026-11-09, ADR-097, "Decided by Eve, with @dasharch" (D-0013): two export modes, a standard one and an opt-in reproducibility bundle; `effective_run.yaml` always. Her correction in the ADR: the two modes are "complements, not alternatives".
- 2026-11-16 (D-0190): "publication and reproducibility fits well".
- 2026-11-16 (D-0192): "add the recipe to the reproducibility mode 2 - And I suggest to remove the recipe from the mode 1".
- 2026-11-16 (D-0187, D-0188): with an audit, both modes use the audit recipe and the data used; without an audit, the original recipe and the data used.
- 2026-11-18 (D-0295): "Mode 1 and mode 2 EXP-MODES Export bundle contents by mode are our main choices for export publication and reproducibility. Within those 2 modes we have the plots exported - all exported."

No ledger line says how the user CHOOSES between the modes, nor whether there is one download or two.

## The four descriptions, side by side

| | Her decisions (ledger, ADR-097) | Design pages for the audit mode (not built) | The UML picture "EXP-MODES" | What is built today |
|---|---|---|---|---|
| How many | Two, complements | One bundle with one tick | Three ways out of "Mode selected?": Publication, Reproducibility, "Both (recommended)" | One bundle with one tick |
| How the user chooses | not said | a tick "include recipe and raw data", off by default | a choice of three | a tick "Also include a reproducibility/reimport bundle", off by default |
| Publication part | plots, report, README, the audited steps, the run record | plots, data, steps, the tables of the audit | named "the paper-facing facet", contents not drawn | plots, report, README, the tier 1 and tier 2 tables, the audited tables, the audited steps, the run record |
| Reproducibility part | the recipe (audited steps written in as real steps) and the data files | the recipe and the raw data files | "frozen recipe" and "actual data files, copied" | the recipe and the copied data files, only with the tick |
| Warning about sensitive data | one notice that does not block (ADR-097 point 8); a later question of hers on a warning is "asked, not decided" | next to the tick | none | a notice at the moment of the export; nothing next to the tick |
| One download or two | not decided | one | "one zip" for Both | one |

Where the "one bundle and one tick box" comes from: the design page `home_audit_steps.md:346` says "decided 2026-11-12, Eve, P4b". There is NO ledger line for it (searched: "P4b" has no hit in the ledger). The page that calls the UML picture "partly outdated" is an agent's review, not her words.

## Two small differences found on the way

1. ADR-097 says the publication part holds only the report, the plots, the README and the audited steps. The code also writes the tier 1 and tier 2 TABLES into it, and the user guide says so ("Every export always contains the plots, the Tier 1/Tier 2 data tables, ..."). Records, code and docs differ on the tables.
2. Her sentence of 11-16 "remove the recipe from the mode 1" is what the code does today: without the tick the recipe file is not in the bundle.

## The one question (options from the evidence; no recommendation asked of the scout)

"Today the export is ONE download. A tick, off by default, adds the reproducibility part (the recipe and the data files). Which of these is the export you mean by the two modes?"

- **A. As built.** One download. Publication is always there; the tick adds Reproducibility. What changes now is only what she already decided: no scope, SVG as default. Matches ADR-097 and "complements".
- **B. A choice of three, as the UML picture draws it:** Publication, Reproducibility, or Both (one zip). New: a bundle that holds ONLY the recipe and the data, with no plots and no report. Changes: the tick becomes a three-way choice, and the bundle build is split in two parts.
- **C. Two separate downloads,** one per mode (two buttons). Nothing in the records or the picture says this; it is one possible reading of "the 2 export bundle".

And one small point with it: should the warning about sensitive data stand next to the tick (as the audit design pages say), or stay a notice at the moment of the export (as built)?

## My suggestion (the coordinator's, marked as mine)

A. Reasons: it is what she decided on 11-09 with the word "complements", it is what her sentence of today describes ("within those 2 modes ... all exported"), and it is built and tested. B adds a bundle without pictures that nobody has asked for in words; if she wants it, it is a clean later addition. The UML picture would then be corrected to show one tick, not three ways (a UML task, with her yes).
For the warning: next to the tick as well as at the export. A user reads the text beside a tick before ticking it; a notice after the press comes late.
