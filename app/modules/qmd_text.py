"""Make a text harmless for Quarto and Markdown before it goes into `report.qmd` (PLOT-TEXT-RUNS-CODE-1, fix round).

The export writes `report.qmd` from texts that a recipe, an audit step, a session or a label supplies (a plot title, a
reason, a column name, a dataset id), then runs `quarto render` on it. A text with a new line and a fenced `{python}` cell,
or an inline `` `{python} expr` ``, was a code cell for Quarto and ran with the app's rights (proved 2026-11-16 with a
harmless marker). A text of a recipe must never run code (Eve, 2026-11-13). Every text that comes from outside goes through one of
these functions; `app/tests/test_export_report_texts.py` scans the handler so that a new raw insertion fails.

What each function does, and what it keeps: the text must READ the same in the rendered report.

- `plain(text)`: a text inside a line of Markdown (a sentence, a table cell, a heading). One line; a backslash before every
  character that Markdown, a table, a Pandoc attribute `{...}`, a shortcode `{{< >}}`, a citation `@x`, a formula `$`, raw HTML `<`
  or a Quarto code fence could read as syntax; an underscore only where it could start or end emphasis (`a_b` is left as it
  is). A backslash before punctuation shows the character itself, so the rendered text is the original.
- `code(text)`: a text inside an inline code span: one line, a delimiter longer than any run of backticks in the text, and a
  space on both sides when the text could be read as an inline expression (`` `{python} x` ``) or touches a backtick;
  a shortcode is defused. In a table cell (`table=True`) a text with a `|` is written as `plain` text.
- `yaml_string(text)`: a text as a double-quoted YAML string (the front matter): quotes, backslashes and new lines escaped.
- `mermaid_label(text)`: a text inside the quotes of a Mermaid node: no quote, no backtick, no angle bracket, one line.

# @deps
# provides: function:plain, function:code, function:yaml_string, function:mermaid_label, function:one_line
# consumed_by: app/handlers/export_handlers.py, app/tests/test_export_report_texts.py
# doc: .claude/design/recipe_format_spec.md (section 15, plot texts and the report)
# @end_deps
"""
import json
import re
import unicodedata

# Characters that start a new line for a Markdown reader, or that are not text at all
_LINE_BREAKS = re.compile(r"[\r\n\v\f\u0085  ]+")
_ALWAYS = re.compile(r"[\\`*\[\]{}<|$@^~]")
_LEADING = re.compile(r"^(\s*)([#>:+\-=]|\d+[.)])")
_UNDERSCORE = re.compile(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])")
_ENTITY = re.compile(r"&(?=#|[A-Za-z]+;)")


def one_line(text) -> str:
    """The text as one line: new lines and tabs become a space, other control characters are dropped."""
    text = _LINE_BREAKS.sub(" ", str(text)).replace("\t", " ")
    return "".join(c for c in text if unicodedata.category(c) not in ("Cc", "Cs") or c == " ")


def plain(text) -> str:
    """A text inside a line of Markdown, harmless to Quarto and Markdown and reading the same (see the module text)."""
    t = one_line(text)
    t = _ALWAYS.sub(lambda m: "\\" + m.group(), t)
    t = _UNDERSCORE.sub(r"\\_", t)
    t = _ENTITY.sub(r"\\&", t)
    t = t.replace("--", "-\\-").replace("...", ".\\..")      # Pandoc "smart" typography would change them
    match = _LEADING.match(t)
    if match:
        marker = match.group(2)
        if marker[0].isdigit():           # `1. x` is a list: escape the dot
            t = t[:match.start(2) + len(marker) - 1] + "\\" + t[match.start(2) + len(marker) - 1:]
        else:
            t = t[:match.start(2)] + "\\" + t[match.start(2):]
    return t


def code(text, table: bool = False) -> str:
    """A text as an inline code span: the same text shows, nothing in it is read as code or syntax.

    Quarto reads a shortcode `{{< ... >}}` (`include` reads a file, `env` reads a variable) even inside a code span, so a
    zero-width space is put between `{{` and `<`. In a table cell a `|` cannot be shown inside a code span (a backslash
    would show), so such a text is written with `plain` there (it reads the same, without the monospace font).
    """
    t = one_line(text)
    if table and "|" in t:
        return plain(t)
    t = t.replace("{{<", "{{\u200b<")
    longest = max((len(run) for run in re.findall(r"`+", t)), default=0)
    fence = "`" * (longest + 1)
    pad = " " if t.startswith(("{", "`", " ")) or t.endswith(("`", " ")) else ""
    if not t:
        return "` `"
    return f"{fence}{pad}{t}{pad}{fence}"


def yaml_string(text) -> str:
    """A text as a double-quoted YAML scalar (a JSON string is one)."""
    return json.dumps(str(text), ensure_ascii=False)


def mermaid_label(text) -> str:
    """A text for the inside of the quotes of a Mermaid node label: one line, no quote, no backtick, no angle bracket."""
    t = one_line(text)
    return t.replace('"', "'").replace("`", "'").replace("<", "#lt;").replace(">", "#gt;")
