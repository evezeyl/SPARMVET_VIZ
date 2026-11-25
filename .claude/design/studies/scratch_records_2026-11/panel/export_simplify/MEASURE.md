# Export cost on the demo recipe 1_test_data_ST22_dummy (17 plots, 5 groups)

Branch dev, head 0a1541c3, qa features, real browser download (Playwright, Chromium headless, app started by my script on port 8765, a second one on 8766 for the PDF-report run; both stopped). One app session, recipe loaded once, runs in a row. Scope "global" in all runs. Every number below says "ran" (taken from my runs; the zips are in `measure/`, listings in `measure/listing_<tag>.txt`, raw rows in `measure/runs.jsonl` and `runs_pdfreport.jsonl`).

Timing: from the click on Export to the finished download (`expect_download` + `path()`). Fields were set, then I waited for Shiny idle, 1.5 s, idle again, then pressed. Each bundle was checked: README shows the plot format and preset; the reproducibility folders are present only when the tick was on. The machine was NOT idle (another agent runs suites): load is the 1-minute load average read just before the run (always under 10, so no wait was needed).

## Table (all ran; mode = reproducibility tick)

| Plot format | Quality | Mode | Load | Seconds | Zip | Plots folder (raw / zipped) | Reproducibility part (raw / zipped) |
|---|---|---|---|---|---|---|---|
| PNG | web | tick on | 6.55 | 43.1 | 6,663,443 | 2,950,795 / 2,499,086 | 1,020,651 / 71,648 |
| PNG | publication | tick on | 8.20 | 47.6 | 12,471,675 | 6,737,510 / 5,309,796 | 1,020,651 / 71,648 |
| SVG | web | tick on | 6.34 | 26.4 | 2,631,724 | 3,619,704 / 437,105 | 1,020,651 / 71,648 |
| SVG | publication | tick on | 5.79 | 27.3 | 2,632,500 | 3,619,704 / 437,075 | 1,020,651 / 71,648 |
| PDF | web | tick on | 5.28 | 43.7 | 4,547,208 | 477,250 / 391,723 | 1,020,651 / 71,648 |
| PDF | publication | tick on | 4.30 | 51.7 | 7,545,207 | 477,250 / 391,723 | 1,020,651 / 71,648 |
| PNG | web | tick OFF (today's default) | 3.63 | 28.8 | 6,589,071 | 2,950,795 / 2,499,083 | none |
| SVG (report PDF) | web | tick on | 3.07 | 73.3 | 3,657,828 | 3,619,704 / 437,040 | 1,020,651 / 71,648 |

The reproducibility part = the two folders `data_analysis_recipes_reproducibility/` (the frozen recipe, 46,868 raw) and `data_reproducibility/` (the raw data tables). `effective_run.yaml` (2,572 bytes) is written with or without the tick and is not counted here.

Other parts of a bundle (ran, PNG web tick on, zipped): data folders T1/T2 tables 231,543 raw / 28,114 zipped; `report.html` 8,583,904 raw / about 4.0 MB zipped (the biggest single part of the PNG bundles, it embeds the pictures); `report.qmd` 25,910; `lineage/` 20,820; README 8,174.
Report size per bundle: PNG web 8.6 MB, PNG publication 13.6 MB, SVG 9.5 MB (either quality), PDF plots web 8.6 MB and publication 13.6 MB (all `report.html`); with the report format PDF: `report.pdf` 3.6 MB.

Observations (ran): quality has NO effect on SVG (identical plot bytes in web and publication) and none on PDF plots (identical); it changes PNG and, through the PNG pictures embedded, the HTML report. SVG was the fastest (26 to 27 s). Differences of a few seconds are inside the noise of a busy machine; the load differs from run to run (3 to 8).

## (d) All 17 plots, errors, warnings

Ran: every one of the 7 + 1 bundles holds 17 plot files in the chosen format; no `_ERROR.txt` stub in any bundle; no `EXPORT_NOT_CREATED.txt`. README warning lines: only the note about `effective_run.yaml`'s `t3_translation_skipped` (present with the tick on, information only). Nothing else.

## (c) The three biggest pictures per format (raw bytes; rows = rows of the plotted dataset table in the bundle, T2 file if the folder has one, else T1)

| Format | Quality | Picture | Bytes | Rows of its table |
|---|---|---|---|---|
| PNG | web | `Summary_phenotype_length_fragmentation/phenotype_genome_length_fragmentation.png` | 339,716 | 126 |
| PNG | web | `QA_fanout_exhibit/qa_fanout_rows_per_sample.png` | 269,883 | 42 |
| PNG | web | `QC_Reads_Anchor/qc_reads_horizontal_barplot.png` | 269,345 | 42 |
| PNG | publication | same phenotype plot | 772,779 | 126 |
| PNG | publication | `qa_fanout_rows_per_sample.png` | 617,736 | 42 |
| PNG | publication | `Quast_with_metadata/miaou.png` | 616,908 | 126 |
| SVG | both | `QC_Reads_Anchor/qc_reads_horizontal_barplot.svg` | 2,015,757 | 42 |
| SVG | both | `Quast_with_metadata/miaou.svg` | 523,543 | 126 |
| SVG | both | `ST22_Anchor/virulence_variants.svg` | 203,296 | 617 |
| PDF | both | `Quast_with_metadata/miaou.pdf` | 176,558 | 126 |
| PDF | both | phenotype plot `.pdf` | 42,813 | 126 |
| PDF | both | `qc_reads_horizontal_barplot.pdf` | 24,063 | 42 |

The SVG concern: in the demo the biggest SVG (2.0 MB) has only 42 rows (4,915 `<path>` elements, 431 `<use>`); it is not the table with the most rows (the 617-row plot is 203 KB). So the size here does not follow the row count; I did NOT find out why that plot has so many paths (not checked; the plot kind or its labels, not examined). The demo tables are small (126 rows at most plotted, one 617), so this says nothing about a recipe with thousands of points.

## What the tick adds (PNG web, ran, not the same load: 6.55 vs 3.63)

Tick on 43.1 s, 6,663,443 bytes; tick off 28.8 s, 6,589,071 bytes. The tick adds about 14 s and 74 KB zipped (the frozen recipe plus the raw data tables: 1,020,651 bytes raw, 71,648 zipped). On this demo data the size is small because the raw tables are small; it grows with the raw data. The time difference was taken at different loads and from one run each: read it as "some seconds", not as a measured 14 s.

## SVG: can it be opened and resized without loss?

Read from the SVG files in the bundle: yes for lines and shapes (pure vector, `viewBox 0 0 576 360`, width/height in pt, no embedded bitmap). Text is NOT kept as text: 0 `<text>` elements; each letter is a glyph outline drawn as a `<path>` (from DejaVu Sans, defined once in `<defs>` and reused with `<use>`). No font is embedded or named (no `font-family`, no `@font-face`). So: it opens and scales without loss and looks the same on any machine (no font needed), but the words cannot be selected, searched or edited in a vector editor as text. This is the matplotlib backend default (the file says "Matplotlib v3.10.9"). The PDF plots were not inspected for text.

## Report format: what does the field change?

Read in `export_handlers.py` and checked in the bundles: the export DOES render the report. Line 1949 to 1975: it runs `quarto render report.qmd --to <html|pdf|docx>` (timeout 120 s) and puts the result into the bundle next to `report.qmd`. In my runs: HTML bundles hold `report.html` (8.6 to 13.6 MB, self-contained); the PDF-report run holds `report.pdf` (3.6 MB) and no `report.html`. `report.qmd` is in both, and its YAML header lists html, pdf and docx formats. The README line names which rendered report is inside.

## SVG pictures in a PDF report

`rsvg-convert` is NOT on this machine (`command -v rsvg-convert` gave nothing; ran). The code (lines 1155 to 1168) allows SVG in a PDF report only when it is present; otherwise the report uses PNG pictures. Ran, plot format SVG + report format PDF: the zip's `plots/` holds SVG, `report.pdf` was made, but `report.qmd` points at `_render/<plot>.png` for all 17 plots, so the PDF report holds PNG pictures, not the SVG ones. The README says "Plot format: svg" and shows no notice of the fallback (read: README lines; I did not look at the app's on-screen notification). That run took 73.3 s (load 3.07) against 26.4 s with the HTML report, so a PDF report costs about 47 s more here (one run each).

Two more reads on `report.qmd` (all bundles, ran): it links figures as `_render/<plot>.<ext>`, a folder that is NOT in the zip (checked: no `_render` entry), while the README says the report "contains relative links to the dataset subfolders". So re-running `quarto render report.qmd` from the unzipped bundle will not find the pictures (I did not run that render; the rendered HTML/PDF made at export time is fine). Worth a decision, not mine.

## Discarded and repeated

0 runs discarded in the 8 measured runs (every one had the right format and the tick state in its README and the right folders). One earlier probe run (PNG web, tick on, 41.0 s, load 3.11) was only a test of my script; I removed its zip and repeated it inside the full series. It is in `measure/runs_probe.jsonl`.

## Not checked

- Why the QC reads SVG has 4,915 paths.
- The visual look of the pictures; the PDF plots' text; a re-render of `report.qmd` from an unzipped bundle.
- Timing under an idle machine and a cold app (the first run was in a session where the recipe was already loaded; each run is single; no repeat to give a spread).
- The row count is the rows of the dataset table in the bundle's folder; I did not check it against the exact table the plot reads (a plot can use a joined or filtered table).
- Whether the on-screen app tells the user about the PDF-report PNG fallback.
- The `info.contact` address: not copied anywhere; no README line quoted.
