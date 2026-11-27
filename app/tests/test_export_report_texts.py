"""The export report: a text of a recipe, an audit step, a session or a label can never run code (PLOT-TEXT-RUNS-CODE-1, fix round).

`app/handlers/export_handlers.py` writes `report.qmd` and runs `quarto render` on it. Until 2026-11-16 a plot title, a label, the
reason or the parameters of an audit step were inserted raw: a new line followed by a fenced `{python}` cell, or an inline
`{python} expr`, ran with the app's rights when Quarto could execute Python (proved with a marker file; the reason typed in the audit
panel also arrives in a session file and in an imported bundle). Closed two ways: every inserted text goes through
`app/modules/qmd_text.py`, and the render command carries `--no-execute`.

Tests that need Quarto skip with the reason when it is missing; the ones that execute a cell need an interpreter with Jupyter
(`QUARTO_PYTHON`, default `/usr/bin/python3`). Markers are written only under `tmpAI/`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_report_texts.py -q
"""
import ast
import html
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

from app.modules.qmd_text import code, mermaid_label, one_line, plain, yaml_string

ROOT = Path(__file__).resolve().parents[2]
HANDLER = ROOT / "app" / "handlers" / "export_handlers.py"
WORK = ROOT / "tmpAI" / "report_text_probe"


# ---- the text functions, without Quarto -----------------------------------------------------------------------------

HOSTILE = [
    "x\n\n```{python}\nopen('m','w').write('a')\n```\n",
    "`{python} open('m','w').write('a')`",
    "{{< include /etc/hostname >}}",
    "{{< env HOME >}}",
    "<script>alert(1)</script>",
    "<div class='x'>raw html</div>",
    "---\ntitle: broken\n---",
    "# a heading\n## and another",
    "| a | b |\n|---|---|",
    "line1\r\nline2 line3\x00\x07",
    "```",
    "[link](http://x)",
    "$$ x $$ and $5",
    "@cite and [@key]",
    "::: {.callout-note}\ninside\n:::",
]


@pytest.mark.parametrize("text", HOSTILE)
def test_plain_text_is_one_line_with_nothing_that_markdown_or_quarto_reads(text):
    out = plain(text)
    assert "\n" not in out and "\r" not in out and "\x00" not in out
    for token in ("`", "{", "<", "|", "$", "[", "*", "@"):
        assert all(out[i - 1:i] == "\\" for i, c in enumerate(out) if c == token and i), (token, out)
        assert not out.startswith(token)
    assert not re.match(r"^\s*(#|>|:|-|\+|\d+[.)])", out)


@pytest.mark.parametrize("text", ["`{python} 1+1`", "a ` {r} x` b", "{python} 1", "  {python} 1", "x`{julia}y`"])
def test_a_text_with_a_backtick_and_an_opening_brace_is_never_returned_as_a_code_span(text):
    out = code(text)
    assert out == plain(text) and "`{" not in out.replace("\\`", "")


@pytest.mark.parametrize("text", HOSTILE)
def test_a_code_span_is_one_line_and_cannot_be_closed_or_read_as_an_inline_expression(text):
    out = code(text)
    assert "\n" not in out
    if not out.startswith("`"):   # a text that could be read as an inline expression is written as plain text
        assert out == plain(text)
        return
    opening = re.match(r"^(`+)", out).group(1)
    assert out.endswith(opening)
    inner = out[len(opening):-len(opening)]
    assert not re.search(r"`{%d,}" % len(opening), inner)           # nothing inside can close it
    assert not inner.startswith("{") and "{{<" not in inner         # no inline `{python}`, no shortcode


@pytest.mark.parametrize("text", ["a|b", "x | y | z"])
def test_a_pipe_in_a_table_cell_is_written_as_plain_text_because_a_code_span_cannot_show_it(text):
    assert "|" not in code(text, table=True).replace("\\|", "")
    assert code(text, table=True).startswith(text.split("|")[0])


def test_yaml_string_is_one_valid_double_quoted_scalar_holding_the_plain_text():
    import yaml
    for text in HOSTILE + ['a "quoted" title', "back\\slash", "unicode \u2014 dash", "\\input{/etc/hostname}", "{{< include /etc/hostname >}}"]:
        value = yaml_string(text)
        assert "\n" not in value and yaml.safe_load("t: " + value)["t"] == plain(text)


def test_an_ordinary_id_is_the_same_in_the_front_matter():
    import yaml
    for text in ["Results Report \u2014 1_test_data_ST22_dummy", "Results Report \u2014 figshare_integration", "my-bundle_01"]:
        assert yaml.safe_load("t: " + yaml_string(text))["t"] == text


def test_mermaid_label_has_no_quote_backtick_or_angle_bracket():
    out = mermaid_label('a "b" `c` <d>\nnext')
    assert '"' not in out and "`" not in out and "<" not in out and ">" not in out and "\n" not in out


@pytest.mark.parametrize("text", ["multi_resistance_by_country", "Sample ID", "Year 2020 (QC)", "Results: 50% done", "a-b.c", "K. pneumoniae"])
def test_an_ordinary_text_is_not_changed_by_plain(text):
    assert plain(text) == text


def test_the_pieces_of_a_report_for_ordinary_texts_hold_no_backslash():
    from app.handlers.export_handlers import _build_methods_section, plot_report_lines
    lines = plot_report_lines("amr_plot", "Multi-resistance by country", "Multi-resistance by country — dataset: `joined`", "fig-amr-plot", "png", None)
    assert lines[0] == "### Multi-resistance by country"
    assert lines[2] == "![Multi-resistance by country — dataset: `joined`](_render/amr_plot.png){#fig-amr-plot width=95%}"
    methods = _build_methods_section(
        all_plots=[("amr_plot", {"ui_label": "Multi-res"})],
        audit_steps=[{"node_type": "exclusion_row", "params": {"column": "sample_id", "op": "in", "value": ["S2"], "na": "remove"},
                      "reason": "Failed QC (coverage below 30x).", "place": "T3:amr_plot"}],
        ds_to_plots={}, tiers_exported=["T1"], t3_aesthetic_overrides=None)
    joined = "\n".join(methods)
    assert "\\" not in joined
    assert 'where **sample_id** is one of "S2"' in joined and "*Reason: Failed QC (coverage below 30x).*" in joined


# ---- reading the same, and not running, in a real Quarto render ------------------------------------------------------

QUARTO = shutil.which("quarto")
JUPYTER_PYTHON = os.environ.get("QUARTO_PYTHON", "/usr/bin/python3")


def _has_jupyter() -> bool:
    try:
        return subprocess.run([JUPYTER_PYTHON, "-c", "import jupyter_core, nbformat, yaml, ipykernel"], capture_output=True, timeout=30).returncode == 0
    except Exception:
        return False


needs_quarto = pytest.mark.skipif(QUARTO is None, reason="quarto is not installed")
needs_jupyter = pytest.mark.skipif(QUARTO is None or not _has_jupyter(),
                                   reason=f"no Quarto, or {JUPYTER_PYTHON} has no Jupyter, yaml and ipykernel: a cell cannot run here, so a marker cannot prove it")


def _render(name: str, qmd: str, *, execute: bool, timeout: int = 120, to: str = "html"):
    folder = WORK / f"{name}_{uuid.uuid4().hex[:8]}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "report.qmd").write_text(qmd, encoding="utf-8")
    command = ["quarto", "render", str(folder / "report.qmd"), "--to", to] + ([] if execute else ["--no-execute"])
    result = subprocess.run(command, capture_output=True, text=True, cwd=folder, timeout=timeout,
                            env={**os.environ, "QUARTO_PYTHON": JUPYTER_PYTHON})
    return folder, result


def _text_of(page: Path) -> str:
    body = page.read_text(encoding="utf-8")
    body = body[body.index("<main"):body.index("</main>")]
    return html.unescape(re.sub(r"<[^>]+>", "\n", body))


READ_SAME = ["multi_resistance_by_country", "_emph_ x", "a *star* b", "50% of $5", "a `tick` b", "a | pipe", "# not a heading", "1. not a list",
             "[a](b) and @c", "x^2^ y~2~", "{braces} and <angle>", "back\\slash", "title: with colon", "---"]


@needs_quarto
def test_every_text_reads_the_same_in_the_rendered_report_in_a_paragraph_a_table_cell_a_heading_and_a_code_span():
    lines = ["---", f"title: {yaml_string('T')}", "---", ""]
    for i, t in enumerate(READ_SAME):
        lines += [f"### H{i} {plain(t)}", "", f"P{i} {plain(t)}", "", "| k | v |", "|---|---|", f"| C{i} | {plain(t)} |", f"| K{i} | {code(t, True)} |", "", f"Q{i} {code(t)}", ""]
    folder, result = _render("same", "\n".join(lines), execute=False)
    assert result.returncode == 0, result.stderr[-500:]
    text = _text_of(folder / "report.html")
    flat = re.sub(r"\s+", " ", text)
    for i, t in enumerate(READ_SAME):
        shown = re.sub(r"\s+", " ", t)
        assert re.search(rf"P{i} {re.escape(shown)}", flat), (i, t)
        assert re.search(rf"C{i} {re.escape(shown)}", flat), (i, t)
        assert re.search(rf"K{i} {re.escape(shown)}", flat), (i, t)
        assert re.search(rf"Q{i} {re.escape(shown)}", flat), (i, t)
        assert re.search(rf"H{i} {re.escape(shown)}", flat), (i, t)


@needs_quarto
def test_a_shortcode_a_script_and_a_front_matter_break_show_as_text_and_do_nothing():
    texts = ["{{< meta title >}}", "{{< include /etc/hostname >}}", "<script>window.pwned=1</script>", "---\ntitle: broken\n---"]
    lines = ["---", f"title: {yaml_string('Real title')}", "---", ""]
    for i, t in enumerate(texts):
        lines += [f"P{i} {plain(t)}", "", f"Q{i} {code(t)}", ""]
    folder, result = _render("inert", "\n".join(lines), execute=False)
    assert result.returncode == 0, result.stderr[-500:]
    page = (folder / "report.html").read_text(encoding="utf-8")
    assert "<script>window.pwned=1</script>" not in page
    flat = re.sub(r"\s+", " ", _text_of(folder / "report.html"))
    assert "{{< meta title >}}" in flat.replace("​", "") and "{{< include /etc/hostname >}}" in flat.replace("​", "")
    assert "Real title" in page


EXECUTING = {
    "fence": "x\n\n```{{python}}\n#| echo: false\nopen({m!r}, 'w').write('fence')\n```\n",
    "inline": "`{{python}} open({m!r}, 'w').write('inline')`",
    "inline_in_text": "before `{{python}} open({m!r}, 'w').write('inline2')` after",
    "spaced": "x ` {{python}} open({m!r}, 'w').write('spaced')` y",
}
# a text that is a code span's whole content: raw (no backticks of its own) it is not code, but a code span around it must not make it one
SPAN_CONTENT = {"brace_first": "{{python}} open({m!r}, 'w').write('brace')", "brace_after_space": "  {{python}} open({m!r}, 'w').write('brace2')"}


def _marker_report(kind: str, wrap, marker: Path) -> str:
    text = {**EXECUTING, **SPAN_CONTENT}[kind].format(m=str(marker))
    # `jupyter: python3` puts the Python engine on, as an injected fenced cell elsewhere in a report would: an inline expression is only
    # evaluated when the engine is on, so the control and the safe cases are judged in that worst case
    return "\n".join(["---", f"title: {yaml_string('t')}", "jupyter: python3", "---", "", "| a | b |", "|---|---|", f"| row | {wrap(text)} |", "", f"Line: {wrap(text)}", ""])


@needs_jupyter
@pytest.mark.parametrize("kind", [k for k in EXECUTING if k != "spaced"])   # `spaced` has a space after the backtick: not code even raw, a safe-case only
def test_the_control_a_raw_text_runs_when_quarto_may_execute(kind):
    """Without this the other tests prove nothing: the raw text DOES write the marker when Quarto executes."""
    WORK.mkdir(parents=True, exist_ok=True)
    marker = WORK / f"control_{kind}_{uuid.uuid4().hex[:8]}.txt"
    _render("control", _marker_report(kind, lambda t: t, marker), execute=True, timeout=110)
    assert marker.exists(), "the control did not run: this machine cannot prove anything about execution"
    marker.unlink()


@needs_jupyter
@pytest.mark.parametrize("kind", list(EXECUTING) + list(SPAN_CONTENT))
@pytest.mark.parametrize("how", ["plain", "code", "code_table"])
def test_a_text_made_harmless_does_not_run_even_when_quarto_may_execute(kind, how):
    WORK.mkdir(parents=True, exist_ok=True)
    marker = WORK / f"safe_{kind}_{how}_{uuid.uuid4().hex[:8]}.txt"
    wrap = {"plain": plain, "code": code, "code_table": lambda t: code(t, True)}[how]
    _render("safe", _marker_report(kind, wrap, marker), execute=True, timeout=110)
    assert not marker.exists(), "a text ran as code"


@needs_jupyter
@pytest.mark.parametrize("kind", list(EXECUTING))
def test_even_a_raw_text_does_not_run_when_the_render_has_no_execute(kind):
    WORK.mkdir(parents=True, exist_ok=True)
    marker = WORK / f"noexec_{kind}_{uuid.uuid4().hex[:8]}.txt"
    _render("noexec", _marker_report(kind, lambda t: t, marker), execute=False)
    assert not marker.exists()


@needs_quarto
def test_the_lineage_diagram_is_still_drawn_when_nothing_is_executed():
    """A `{mermaid}` cell is drawn by Quarto itself (a script in the page), not by an execution engine."""
    qmd = "\n".join(["---", "title: t", "format:", "  html:", "    self-contained: true", "---", "", "## Data Lineage", "", "```{mermaid}", "flowchart LR",
                     f'    a[("{mermaid_label("source one")} / source")] --> b["{mermaid_label("plot <one>")} / plot"]', "```", ""])
    folder, result = _render("mermaid", qmd, execute=False)
    assert result.returncode == 0, result.stderr[-500:]
    page = (folder / "report.html").read_text(encoding="utf-8")
    assert 'class="mermaid mermaid-js"' in page and "flowchart LR" in page   # the diagram source is in the page, for Quarto's own script
    playwright = pytest.importorskip("playwright.sync_api", reason="no browser library: the drawn diagram cannot be looked at")
    with playwright.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:  # no browser installed
            pytest.skip(f"no headless browser: {type(exc).__name__}")
        try:
            tab = browser.new_page()
            tab.goto(f"file://{folder / 'report.html'}")
            tab.wait_for_timeout(4000)
            assert tab.locator("svg").count() >= 1, "the diagram was not drawn"
            assert tab.locator("svg >> text=source one").count() >= 1 and tab.locator("svg >> text=plot #lt;one#gt;").count() + tab.locator("svg >> text=plot <one>").count() >= 1
        finally:
            browser.close()


# ---- the handler: every insertion goes through the functions, and the command has --no-execute -----------------------

SAFE_FUNCTIONS = {"_qp", "_qc", "_qm", "_qy", "_quote"}
# names that may be interpolated as they are, with the reason (a new raw name fails the scan)
TRUSTED = {
    "plot_ext": "a file extension chosen by the code (png, svg, pdf)",
    "fig_id": "built from the plot id with a regular expression that keeps only letters, digits and hyphens",
    "caption": "built in the caller from _qp and _qc (checked there)",
    "tier": "one of the tiers exported, constants of the code (T1, T2, T3)",
    "tier_label": "a constant of a dictionary in the code",
    "_i": "a counter",
    "_open": "a constant of a dictionary in the code (Mermaid node shapes)",
    "_close": "a constant of a dictionary in the code (Mermaid node shapes)",
    "_tlbl": "a constant of a dictionary in the code (Mermaid type names)",
    "verb": "a constant of a dictionary in the code",
    "item": "a sentence of prose_items, every one built from checked pieces in the same function",
}


def _assignments(function: ast.AST, name: str):
    """Every expression that gives `name` a value: `name = x`, `name += x`, `name.append(x)`, `name.extend(x)`, a loop `for name in x`."""
    for node in ast.walk(function):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            yield node.value
        elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            yield node.value
        elif isinstance(node, ast.NamedExpr) and node.target.id == name:
            yield node.value
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("append", "extend", "insert")
              and isinstance(node.func.value, ast.Name) and node.func.value.id == name and node.args):
            yield ast.List(elts=[node.args[-1]], ctx=ast.Load()) if node.func.attr in ("append", "insert") else node.args[0]


def _is_safe(expr: ast.AST, function: ast.AST, seen=()) -> bool:
    if isinstance(expr, ast.Constant):
        return True
    if isinstance(expr, ast.Call):
        func = expr.func
        if isinstance(func, ast.Name) and func.id in SAFE_FUNCTIONS:
            return True
        # re.sub(<pattern>, <replacement>, x) with a pattern that keeps only safe characters (checked below), and ints
        if isinstance(func, ast.Attribute) and func.attr == "sub" and ast.unparse(expr).startswith("_re.sub('[^A-Za-z0-9"):
            return True
        if isinstance(func, ast.Name) and func.id in ("len", "int", "str") and all(isinstance(a, (ast.Constant, ast.Call, ast.Attribute)) for a in expr.args):
            return func.id in ("len", "int")
        if isinstance(func, ast.Attribute) and func.attr == "join" and isinstance(func.value, ast.Constant):
            arg = expr.args[0]
            return _is_safe(arg.elt, function, seen) if isinstance(arg, (ast.GeneratorExp, ast.ListComp)) else False
        if isinstance(func, ast.Name) and func.id == "_mmd_id":
            return True   # keeps only letters, digits and underscores
        if isinstance(func, ast.Attribute) and func.attr in ("strftime",):
            return False
        return False
    if isinstance(expr, ast.JoinedStr):
        return all(_is_safe(v.value, function, seen) for v in expr.values if isinstance(v, ast.FormattedValue))
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
        return _is_safe(expr.left, function, seen) and _is_safe(expr.right, function, seen)
    if isinstance(expr, ast.IfExp):
        return _is_safe(expr.body, function, seen) and _is_safe(expr.orelse, function, seen)
    if isinstance(expr, ast.Attribute) and ast.unparse(expr) == "df_preview.height":
        return True
    if isinstance(expr, ast.Name):
        if expr.id in TRUSTED:
            return True
        if expr.id in seen:
            return True
        values = list(_assignments(function, expr.id))
        return bool(values) and all(_is_safe(v, function, seen + (expr.id,)) for v in values)
    return False


def _walk_outside_safe_calls(node: ast.AST):
    """Every node below `node`, except what is inside a call of one of the safe functions (that text is made harmless as a whole)."""
    yield node
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCTIONS:
        return
    for child in ast.iter_child_nodes(node):
        yield from _walk_outside_safe_calls(child)


def _unsafe_insertions(function: ast.FunctionDef, lo: int = 0, hi: int = 10 ** 9):
    found = []
    for node in _walk_outside_safe_calls(function):
        if isinstance(node, ast.JoinedStr) and lo <= node.lineno <= hi:
            for part in node.values:
                if isinstance(part, ast.FormattedValue) and not _is_safe(part.value, function):
                    found.append((node.lineno, ast.unparse(part.value)))
    return found


LINE_BUILDERS = {"plot_report_lines", "_build_methods_section"}   # their own bodies are scanned too


def _line_is_safe(expr: ast.AST, function: ast.AST, seen=()) -> bool:
    """A line, or a list of lines, that goes into the report: only text that is constant, made harmless, or built from such parts.

    Any other way of making a line (`"x " + name`, `"x {}".format(name)`, `"x %s" % name`, a bare variable that was given a raw
    value) is refused. Lists, `+` of lists, list comprehensions and names that hold lists are read through.
    """
    if isinstance(expr, ast.List):
        return all(_line_is_safe(e, function, seen) for e in expr.elts)
    if isinstance(expr, ast.Starred):
        return _line_is_safe(expr.value, function, seen)
    if isinstance(expr, ast.ListComp):
        return _line_is_safe(expr.elt, function, seen)
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
        return _line_is_safe(expr.left, function, seen) and _line_is_safe(expr.right, function, seen)
    if isinstance(expr, ast.IfExp):
        return _line_is_safe(expr.body, function, seen) and _line_is_safe(expr.orelse, function, seen)
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in LINE_BUILDERS:
        return True
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "join":
        arg = expr.args[0]
        return isinstance(expr.func.value, ast.Constant) and isinstance(arg, (ast.GeneratorExp, ast.ListComp)) and _line_is_safe(arg.elt, function, seen)
    if isinstance(expr, ast.Name) and expr.id not in TRUSTED:
        if expr.id in seen:
            return True
        values = list(_assignments(function, expr.id))
        return bool(values) and all(_line_is_safe(v, function, seen + (expr.id,)) for v in values)
    return _is_safe(expr, function)


def _sinks(function: ast.FunctionDef, names: set, lo: int = 0, hi: int = 10 ** 9):
    """The expressions that are put into the lists named in `names`: `x = [...]`, `x += ...`, `x.append(...)`."""
    for node in ast.walk(function):
        if not lo <= getattr(node, "lineno", lo) <= hi:
            continue
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            yield node.lineno, node.value
        elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id in names:
            yield node.lineno, node.value
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("append", "extend")
              and isinstance(node.func.value, ast.Name) and node.func.value.id in names and node.args):
            yield node.lineno, node.args[0] if node.func.attr == "extend" else ast.List(elts=[node.args[0]], ctx=ast.Load())


def _unsafe_lines(function: ast.FunctionDef, names: set, lo: int = 0, hi: int = 10 ** 9):
    """The lines added to the report lists in `names` by any form other than parts made harmless."""
    return [(line, ast.unparse(expr)[:80]) for line, expr in _sinks(function, names, lo, hi) if not _line_is_safe(expr, function)]


def _handler_tree():
    tree = ast.parse(HANDLER.read_text(encoding="utf-8"))
    functions = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    start = next(n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "qmd_lines" for t in n.targets))
    end = next(n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "qmd_source" for t in n.targets))
    return tree, functions, start, end


def test_every_text_inserted_into_the_report_goes_through_the_functions():
    """Scans the three places that write the report: a raw `{value}` in an f-string, and any other way to add a line.

    What it sees: every f-string of the three places, and every expression that is put into a list of report lines
    (`qmd_lines = [...]`, `+=`, `.append`, `.extend`; `lines` and `prose_items` in the two helpers). A line built with `"x " + name`,
    `.format(...)`, `%`, or a variable that holds raw text is refused, as is any call that is not one of the text functions.
    What it cannot see: text that reaches a line through a function it does not know (it refuses every unknown call, so a new
    helper must be added to LINE_BUILDERS, and its own body is scanned), and text that never goes through these three places.
    """
    _, functions, start, end = _handler_tree()
    assert _unsafe_insertions(functions["plot_report_lines"]) == []
    assert _unsafe_insertions(functions["_build_methods_section"]) == []
    assert _unsafe_insertions(functions["define_export_server"], start, end) == []
    assert _unsafe_lines(functions["plot_report_lines"], {"lines"}) == []
    assert _unsafe_lines(functions["_build_methods_section"], {"lines", "prose_items"}) == []
    assert _unsafe_lines(functions["define_export_server"], {"qmd_lines", "_dh_qmd_rows"}, start, end) == []


@pytest.mark.parametrize("body", [
    'qmd_lines.append("x " + name)',
    'qmd_lines.append("x {}".format(name))',
    'qmd_lines.append("x %s" % name)',
    'qmd_lines.append(name)',
    'qmd_lines += [name]',
    'row = name\n    qmd_lines.append(row)',
    'qmd_lines += ["a", "b " + name]',
    'qmd_lines.extend(["x " + name])',
    'qmd_lines += [fmt(name)]',
    'qmd_lines += ["| " + " | ".join(parts) + " |"]',
])
def test_the_scan_refuses_every_other_way_to_add_a_raw_line(body):
    function = ast.parse(f"def f(name, parts):\n    qmd_lines = []\n    {body}\n").body[0]
    assert _unsafe_lines(function, {"qmd_lines"}), body


@pytest.mark.parametrize("body", [
    'qmd_lines.append("x " + _qp(name))',
    'qmd_lines.append(f"| {_qc(name, True)} |")',
    'row = f"a {_qp(name)}"\n    qmd_lines.append(row)',
    'qmd_lines += plot_report_lines(1, 2, 3, 4, 5, 6)',
    'qmd_lines += ["| " + " | ".join(_qp(p) for p in parts) + " |"]',
    'qmd_lines.extend([f"{_qp(name)}", "---"])',
])
def test_the_scan_lets_a_made_harmless_line_through(body):
    function = ast.parse(f"def f(name, parts):\n    qmd_lines = []\n    {body}\n").body[0]
    assert _unsafe_lines(function, {"qmd_lines"}) == [], body


def test_the_scan_can_fail_a_raw_insertion_is_found():
    source = ast.parse('def f(label, reason):\n    return [f"### {label}", f"| {_qp(reason)} |", f"{_qc(label)}"]\n')
    function = source.body[0]
    assert _unsafe_insertions(function) == [(2, "label")]


def test_the_scan_covers_the_whole_report_region():
    _, _, start, end = _handler_tree()
    assert end - start > 200   # from the front matter to the join of the lines


def test_the_render_command_has_no_execute():
    tree, _, _, _ = _handler_tree()
    commands = [n for n in ast.walk(tree) if isinstance(n, ast.List) and any(isinstance(e, ast.Constant) and e.value == "render" for e in n.elts)
                and any(isinstance(e, ast.Constant) and e.value == "quarto" for e in n.elts)]
    assert len(commands) == 1
    assert any(isinstance(e, ast.Constant) and e.value == "--no-execute" for e in commands[0].elts)


def test_the_handler_writes_no_code_cell_of_its_own():
    """Why `--no-execute` changes nothing a user sees: the only fenced cell the handler writes is the Mermaid diagram."""
    source = HANDLER.read_text(encoding="utf-8")
    cells = set(re.findall(r"```\{(\w+)\}", source))
    assert cells == {"mermaid"}, cells


# ---- the front matter: the title is Markdown, and TeX for a PDF ---------------------------------------------------------

import json
import zipfile

needs_pdf = pytest.mark.skipif(QUARTO is None or shutil.which("xelatex") is None or shutil.which("pdftotext") is None,
                               reason="a PDF cannot be made and read here (needs quarto, xelatex and pdftotext)")


def _secret_file() -> tuple:
    WORK.mkdir(parents=True, exist_ok=True)
    token = "SECRETCONTENT" + uuid.uuid4().hex[:10]
    path = WORK / f"file_{uuid.uuid4().hex[:10]}.txt"   # the file name does not hold the token: seeing the token means the file was read
    path.write_text(token, encoding="utf-8")
    return path, token


def _titles(path: Path) -> dict:
    return {"input": "\\input{%s}" % path, "include": "{{< include %s >}}" % path, "inputtex": "Results \\input{%s} end" % path}


def _front(title_value: str, author_value: str = '"x"') -> str:
    return "\n".join(["---", f"title: {title_value}", f"author: {author_value}", "---", "", "## Overview", "", "Body.", ""])


def _document_text(folder: Path, to: str) -> str:
    if to == "html":
        return html.unescape(re.sub(r"<[^>]+>", " ", (folder / "report.html").read_text(encoding="utf-8")))
    if to == "pdf":
        return subprocess.run(["pdftotext", str(folder / "report.pdf"), "-"], capture_output=True, text=True).stdout
    with zipfile.ZipFile(folder / "report.docx") as z:
        return html.unescape(re.sub(r"<[^>]+>", " ", z.read("word/document.xml").decode("utf-8")))


@needs_quarto
@pytest.mark.parametrize("to", ["html", pytest.param("pdf", marks=needs_pdf), "docx"])
@pytest.mark.parametrize("kind", ["input", "include", "inputtex"])
def test_the_control_a_title_that_is_only_yaml_safe_reads_a_file_or_stops_the_render(kind, to):
    """Without this the next test proves nothing: with a title that is only a valid YAML string, a TeX command or a shortcode takes effect."""
    path, token = _secret_file()
    title = _titles(path)[kind]
    folder, result = _render("fm_control", _front(json.dumps(title)), execute=False, to=to, timeout=118)
    if to == "html" and kind in ("input", "inputtex"):
        pytest.skip("a TeX command is only read by TeX: the HTML control for it is the shortcode case")
    if to == "docx" and kind in ("input", "inputtex"):
        pytest.skip("a TeX command is only read by TeX: Word shows it as text")
    took_effect = result.returncode != 0 or (folder / f"report.{to}").exists() and token in _document_text(folder, to)
    assert took_effect, f"the control did nothing: nothing is proved ({kind}, {to})"


@needs_quarto
@pytest.mark.parametrize("to", ["html", pytest.param("pdf", marks=needs_pdf), "docx"])
@pytest.mark.parametrize("kind", ["input", "include", "inputtex"])
def test_a_title_made_harmless_shows_as_text_in_html_pdf_and_word_and_reads_no_file(kind, to):
    path, token = _secret_file()
    title = _titles(path)[kind]
    folder, result = _render("fm_safe", _front(yaml_string(title), yaml_string("an author")), execute=False, to=to, timeout=118)
    assert result.returncode == 0, result.stderr[-600:]
    shown = re.sub(r"\s+", "", _document_text(folder, to))
    assert token not in shown, "the file was read into the document"
    assert "include" in shown if kind == "include" else "input" in shown   # the text itself is shown


@needs_quarto
def test_an_ordinary_title_and_author_read_the_same():
    folder, result = _render("fm_plain", _front(yaml_string("Results Report \u2014 1_test_data_ST22_dummy"), yaml_string("my-bundle_01")), execute=False)
    assert result.returncode == 0
    text = re.sub(r"\s+", " ", _document_text(folder, "html"))
    assert "Results Report \u2014 1_test_data_ST22_dummy" in text and "my-bundle_01" in text


# ---- a shortcode in a code span, at render level (the defusing of `{{<` in `code()`) ----------------------------------------

def _shortcode_report(wrap, token: str) -> str:
    """`{{< meta secret >}}` prints a metadata value that is shown nowhere else; the token is that value."""
    text = "see {{< meta secret >}}"
    return "\n".join(["---", "title: t", f"secret: {token}", "---", "", f"Line: {wrap(text)}", "", "| a | b |", "|---|---|", f"| row | {wrap(text)} |", ""])


@needs_quarto
def test_the_control_a_shortcode_inside_a_raw_code_span_is_run_by_quarto():
    token = "SHORTCODEVALUE" + uuid.uuid4().hex[:8]
    folder, result = _render("sc_control", _shortcode_report(lambda t: f"`{t}`", token), execute=False)
    assert result.returncode == 0 and token in _document_text(folder, "html"), "the control did nothing: nothing is proved"


@needs_quarto
@pytest.mark.parametrize("table", [False, True])
def test_a_shortcode_inside_the_code_span_of_code_is_shown_and_not_run(table):
    token = "SHORTCODEVALUE" + uuid.uuid4().hex[:8]
    folder, result = _render("sc_safe", _shortcode_report(lambda t: code(t, table), token), execute=False)
    assert result.returncode == 0, result.stderr[-400:]
    assert token not in _document_text(folder, "html")
