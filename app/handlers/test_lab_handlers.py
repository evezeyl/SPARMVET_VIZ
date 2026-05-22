# @deps
# provides: function:define_server (test_lab_handlers)
# consumes: app/modules/test_lab_studio.py, shiny, libs/test_lab/reformatter.py, libs/test_lab/aqua_synthesizer.py, libs/test_lab/anonymiser.py
# consumed_by: app/src/server.py
# doc: .claude/rules/rules_test_lab.md §6, .claude/design/spaces/TEST_LAB.md
# @end_deps
"""
TEST_LAB Shiny reactive wiring (test_lab_handlers.py).

Owns all @render.* and @reactive.* for the TEST_LAB workspace.
Two-Category Law (ADR-045): no pure-logic code here — all data operations
live in libs/test_lab/ and are called from render functions below.

Individual tool panel handlers are added by:
  TL-UI-RECONCILE-1, TL-UI-SCAFFOLD-1, TL-UI-SYNTH-1,
  TL-UI-ANON-1, TL-UI-REFORMAT-1.
"""

import io
import tempfile
from pathlib import Path

import polars as pl
from shiny import render, reactive, ui
from shiny import Inputs, Outputs, Session


def define_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    *,
    dev_studio,
    bootloader,
) -> None:
    """Register all @render.* and @reactive.* for the TEST_LAB workspace."""

    @output
    @render.ui
    def tl_reconcile_ui():
        return ui.p(
            "ID Reconciliation — not yet implemented (TL-UI-RECONCILE-1).",
            class_="text-muted small p-2",
        )

    @output
    @render.ui
    def tl_scaffold_ui():
        return ui.p(
            "Manifest Scaffolding — not yet implemented (TL-UI-SCAFFOLD-1).",
            class_="text-muted small p-2",
        )

    # ── Synthetic Data (TL-UI-SYNTH-1) ──────────────────────────────────

    @output
    @render.ui
    def tl_synth_ui():
        return ui.div(
            ui.input_file(
                "tl_synth_file",
                "Upload reference TSV (optional — schema inferred from headers)",
                accept=[".tsv", ".csv", ".txt"],
                multiple=False,
            ),
            ui.input_text(
                "tl_synth_columns",
                "Or enter column names (comma-separated)",
                placeholder="sample_id, species, year, country",
            ),
            ui.output_ui("tl_synth_source_status_ui"),
            ui.input_numeric("tl_synth_n_rows", "Number of rows", value=50, min=10, max=5000, step=10),
            ui.input_select(
                "tl_synth_mode",
                "Mode",
                choices={"demo": "Demo (clean data)", "stress_test": "Stress test (with errors)"},
                selected="demo",
            ),
            ui.output_ui("tl_synth_error_ui"),
            ui.input_action_button(
                "tl_synth_generate", "Generate",
                class_="btn btn-primary btn-sm mt-2",
            ),
            ui.output_ui("tl_synth_status_ui"),
            ui.output_data_frame("tl_synth_preview_table"),
            ui.download_button(
                "tl_synth_download", "Download TSV",
                class_="btn btn-primary btn-sm mt-1",
            ),
            class_="p-2",
        )

    @reactive.Calc
    def _synth_file_info():
        f = input.tl_synth_file()
        if not f:
            return None
        return f[0]

    @output
    @render.ui
    def tl_synth_source_status_ui():
        info = _synth_file_info()
        if info is not None:
            return ui.p(
                f"Source: {info['name']} (column names input ignored)",
                class_="text-muted small",
            )
        return ui.div()

    @output
    @render.ui
    def tl_synth_error_ui():
        if input.tl_synth_mode() != "stress_test":
            return ui.div()
        return ui.div(
            ui.input_slider(
                "tl_synth_missing_rate", "Missing values rate",
                min=0.0, max=0.5, value=0.05, step=0.01,
            ),
            ui.input_slider(
                "tl_synth_dup_rate", "Duplicate ID rate",
                min=0.0, max=0.3, value=0.05, step=0.01,
            ),
            class_="mt-1",
        )

    @reactive.Calc
    @reactive.event(input.tl_synth_generate)
    def _synth_result():
        from test_lab.aqua_synthesizer import AquaSynthesizer
        info = _synth_file_info()
        if info is not None:
            source = Path(info["datapath"])
        else:
            try:
                cols_text = input.tl_synth_columns()
            except Exception:
                return None
            cols = [c.strip() for c in (cols_text or "").split(",") if c.strip()]
            if not cols:
                return None
            source = cols

        n_rows = int(input.tl_synth_n_rows() or 50)
        mode = input.tl_synth_mode() or "demo"

        synth = AquaSynthesizer()
        config = synth.propose_config(source, n_rows=n_rows, mode=mode)

        if mode == "stress_test":
            try:
                config["error_injection"]["missing_values"]["rate"] = float(input.tl_synth_missing_rate())
                config["error_injection"]["duplicate_ids"]["rate"] = float(input.tl_synth_dup_rate())
            except Exception:
                pass

        return synth.generate(config)

    @output
    @render.ui
    def tl_synth_status_ui():
        if input.tl_synth_generate() == 0:
            return ui.p("Configure and click Generate.", class_="text-muted small mt-1")
        df = _synth_result()
        if df is None:
            return ui.p(
                "Enter column names or upload a file, then click Generate.",
                class_="text-warning small mt-1",
            )
        return ui.p(
            f"Generated {df.height} rows x {df.width} columns (preview: first 10 rows).",
            class_="text-muted small mt-1",
        )

    @output
    @render.data_frame
    def tl_synth_preview_table():
        if input.tl_synth_generate() == 0:
            return None
        df = _synth_result()
        if df is None:
            return None
        return render.DataGrid(df.head(10).to_pandas(), width="100%")

    @render.download(filename=lambda: _synth_download_filename())
    async def tl_synth_download():
        df = _synth_result()
        if df is None:
            yield b""
            return
        buf = io.BytesIO()
        df.write_csv(buf, separator="\t")
        yield buf.getvalue()

    def _synth_download_filename():
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"synthetic_{ts}.tsv"

    # ── end TL-UI-SYNTH-1 ────────────────────────────────────────────────

    # ── Anonymisation (TL-UI-ANON-1) ─────────────────────────────────────

    @output
    @render.ui
    def tl_anon_ui():
        return ui.div(
            ui.input_file(
                "tl_anon_file",
                "Upload TSV/CSV to anonymise",
                accept=[".tsv", ".csv", ".txt"],
                multiple=False,
            ),
            ui.output_ui("tl_anon_columns_ui"),
            ui.input_select(
                "tl_anon_pattern",
                "Anonymisation pattern",
                choices={
                    "sequential": "Sequential (ANON_0001)",
                    "hash": "Hash (ANON_A3F2B9C1)",
                    "custom": "Custom format string",
                },
                selected="sequential",
            ),
            ui.output_ui("tl_anon_prefix_ui"),
            ui.output_ui("tl_anon_custom_ui"),
            ui.input_action_button(
                "tl_anon_run", "Anonymise",
                class_="btn btn-primary btn-sm mt-2",
            ),
            ui.output_ui("tl_anon_status_ui"),
            ui.output_data_frame("tl_anon_preview_table"),
            ui.download_button(
                "tl_anon_download",
                "Download ZIP (anonymised + mapping + config)",
                class_="btn btn-primary btn-sm mt-1",
            ),
            class_="p-2",
        )

    @reactive.Calc
    def _anon_file_info():
        f = input.tl_anon_file()
        if not f:
            return None
        return f[0]

    @reactive.Calc
    def _anon_columns():
        info = _anon_file_info()
        if info is None:
            return []
        try:
            sep = "\t" if Path(info["name"]).suffix.lower() == ".tsv" else ","
            return pl.read_csv(info["datapath"], separator=sep, n_rows=0).columns
        except Exception:
            return []

    @output
    @render.ui
    def tl_anon_columns_ui():
        info = _anon_file_info()
        if info is None:
            return ui.p("Upload a file to configure columns.", class_="text-muted small")
        cols = _anon_columns()
        if not cols:
            return ui.p("Could not read columns.", class_="text-muted small")
        return ui.div(
            ui.input_select(
                "tl_anon_id_column",
                "ID column to anonymise",
                choices=cols,
                selected=cols[0],
            ),
            ui.input_checkbox_group(
                "tl_anon_personal_cols",
                "Personal columns to strip (moved to mapping TSV)",
                choices=cols,
                selected=[],
            ),
        )

    @output
    @render.ui
    def tl_anon_prefix_ui():
        if input.tl_anon_pattern() == "custom":
            return ui.div()
        return ui.input_text(
            "tl_anon_prefix", "Prefix", value="ANON",
            placeholder="e.g. SUBJ",
        )

    @output
    @render.ui
    def tl_anon_custom_ui():
        if input.tl_anon_pattern() != "custom":
            return ui.div()
        return ui.input_text(
            "tl_anon_custom_fmt", "Custom format string",
            value="SUBJ_{:05d}",
            placeholder="e.g. SUBJ_{:05d} or ANON_{original}",
        )

    @reactive.Calc
    @reactive.event(input.tl_anon_run)
    def _anon_result():
        from test_lab.anonymiser import Anonymiser
        info = _anon_file_info()
        if info is None:
            return None
        try:
            id_col = input.tl_anon_id_column()
        except Exception:
            return None
        try:
            personal = list(input.tl_anon_personal_cols() or [])
        except Exception:
            personal = []

        pattern = input.tl_anon_pattern() or "sequential"
        if pattern == "custom":
            try:
                pattern = input.tl_anon_custom_fmt() or "SUBJ_{:05d}"
            except Exception:
                pattern = "SUBJ_{:05d}"
        try:
            prefix = input.tl_anon_prefix() or "ANON"
        except Exception:
            prefix = "ANON"

        anon = Anonymiser()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            anon_df, mapping_df = anon.anonymise(
                info["datapath"],
                id_column=id_col,
                personal_columns=personal,
                pattern=pattern,
                prefix=prefix,
                out_dir=tmp_path,
            )
            # Collect all written files into a zip in-memory
            import zipfile
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in sorted(tmp_path.iterdir()):
                    zf.write(f, f.name)
            return {
                "anon_df": anon_df,
                "mapping_df": mapping_df,
                "zip_bytes": buf.getvalue(),
                "stem": Path(info["name"]).stem,
            }

    @output
    @render.ui
    def tl_anon_status_ui():
        if input.tl_anon_run() == 0:
            return ui.p("Upload a file and click Anonymise.", class_="text-muted small mt-1")
        result = _anon_result()
        if result is None:
            return ui.p("Upload a file first.", class_="text-warning small mt-1")
        df = result["anon_df"]
        mapping = result["mapping_df"]
        return ui.p(
            f"Anonymised {df.height} rows x {df.width} columns. "
            f"Mapping: {mapping.height} unique IDs (preview: anonymised data, first 10 rows).",
            class_="text-muted small mt-1",
        )

    @output
    @render.data_frame
    def tl_anon_preview_table():
        if input.tl_anon_run() == 0:
            return None
        result = _anon_result()
        if result is None:
            return None
        return render.DataGrid(result["anon_df"].head(10).to_pandas(), width="100%")

    @render.download(filename=lambda: _anon_download_filename())
    async def tl_anon_download():
        result = _anon_result()
        if result is None:
            yield b""
            return
        yield result["zip_bytes"]

    def _anon_download_filename():
        result = _anon_result()
        if result is None:
            return "anonymised.zip"
        return f"{result['stem']}_anonymised.zip"

    # ── end TL-UI-ANON-1 ─────────────────────────────────────────────────

    # ── File Reformatting (TL-UI-REFORMAT-1) ─────────────────────────────

    @output
    @render.ui
    def tl_reformat_ui():
        return ui.div(
            ui.input_file(
                "tl_reformat_file",
                "Upload file (XLSX, XLS, CSV, TSV)",
                accept=[".xlsx", ".xls", ".xlsm", ".csv", ".tsv", ".txt"],
                multiple=False,
            ),
            ui.output_ui("tl_reformat_sheet_ui"),
            ui.input_select(
                "tl_reformat_delimiter",
                "CSV delimiter (ignored for XLSX)",
                choices={"comma": "Comma (,)", "semicolon": "Semicolon (;)",
                         "tab": "Tab", "pipe": "Pipe (|)"},
                selected="comma",
            ),
            ui.download_button(
                "tl_reformat_download",
                "Convert & Download TSV",
                class_="btn btn-primary btn-sm mt-2",
            ),
            ui.output_ui("tl_reformat_status_ui"),
            class_="p-2",
        )

    @reactive.Calc
    def _reformat_file_info():
        f = input.tl_reformat_file()
        if not f:
            return None
        return f[0]

    @reactive.Calc
    def _reformat_is_xlsx():
        info = _reformat_file_info()
        if info is None:
            return False
        return Path(info["name"]).suffix.lower() in {".xlsx", ".xls", ".xlsm"}

    @reactive.Calc
    def _reformat_sheet_names():
        """Read sheet names from an uploaded XLSX without converting."""
        if not _reformat_is_xlsx():
            return []
        info = _reformat_file_info()
        try:
            import polars as pl
            sheets = pl.read_excel(info["datapath"], sheet_id=0)
            return list(sheets.keys())
        except Exception:
            return []

    @output
    @render.ui
    def tl_reformat_sheet_ui():
        if not _reformat_is_xlsx():
            return ui.div()
        sheets = _reformat_sheet_names()
        if not sheets:
            return ui.p("Could not read sheets.", class_="text-muted small")
        return ui.input_checkbox_group(
            "tl_reformat_sheets",
            "Sheets to extract (default: all)",
            choices=sheets,
            selected=sheets,
        )

    @output
    @render.ui
    def tl_reformat_status_ui():
        info = _reformat_file_info()
        if info is None:
            return ui.p("Upload a file to begin.", class_="text-muted small mt-1")
        if _reformat_is_xlsx():
            sheets = _reformat_sheet_names()
            return ui.p(
                f"XLSX detected — {len(sheets)} sheet(s): {', '.join(sheets)}",
                class_="text-muted small mt-1",
            )
        return ui.p(
            f"File ready: {info['name']}",
            class_="text-muted small mt-1",
        )

    @render.download(filename=lambda: _reformat_download_filename())
    async def tl_reformat_download():
        from test_lab.reformatter import DataReformatter
        info = _reformat_file_info()
        if info is None:
            yield b""
            return
        reformatter = DataReformatter()
        src = Path(info["datapath"])
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            if _reformat_is_xlsx():
                chosen = list(input.tl_reformat_sheets()) or None
                sheets = reformatter.convert_xlsx(src, out_dir=tmp_path, sheet_names=chosen)
                # Zip multiple TSVs into one archive
                import zipfile
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for tsv_file in sorted(tmp_path.glob("*.tsv")):
                        zf.write(tsv_file, tsv_file.name)
                yield buf.getvalue()
            else:
                delim_map = {"comma": ",", "semicolon": ";", "tab": "\t", "pipe": "|"}
                delim = delim_map.get(input.tl_reformat_delimiter(), ",")
                df = reformatter.convert_csv(src, delimiter=delim, out_dir=tmp_path)
                out_file = tmp_path / f"{src.stem}.tsv"
                yield out_file.read_bytes()

    def _reformat_download_filename():
        info = _reformat_file_info()
        if info is None:
            return "converted.tsv"
        stem = Path(info["name"]).stem
        return f"{stem}_converted.zip" if _reformat_is_xlsx() else f"{stem}.tsv"

    # ── end TL-UI-REFORMAT-1 ─────────────────────────────────────────────

    @output
    @render.ui
    def test_lab_workspace_ui():
        return ui.div()
