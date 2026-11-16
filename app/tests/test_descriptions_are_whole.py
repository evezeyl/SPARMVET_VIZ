"""Every description of every shipped recipe, retest recipe, template, fragment and gallery example is whole (RECIPE-FIXES-1).

A plain (unquoted) text in YAML stops at ' #': what follows is a comment. Three descriptions were cut that way ("... (issue").
This test reads the YAML source, not the loaded text, so a cut is seen: (1) a plain description is not followed by a comment
on its line, (2) the text the loader reads is the text written in the file, (3) its brackets close, (4) it ends as a sentence
(a full stop, '!', '?', a closing bracket or quote) unless it is a short title (8 words or fewer) or ends with a link.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_descriptions_are_whole.py -q
"""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
FILES = sorted(set((ROOT / "config/data_analysis_recipes").rglob("*.yaml")) | set((ROOT / "assets/gallery_data").rglob("*.yaml")))


def descriptions(text: str):
    """(line number, loaded text, rest of the line after a plain text) of every `description:` key whose value is text."""
    root = yaml.compose(text, Loader=yaml.SafeLoader)
    lines = text.split("\n")
    found = []

    def walk(node):
        if isinstance(node, yaml.MappingNode):
            for key, value in node.value:
                if getattr(key, "value", None) == "description" and isinstance(value, yaml.ScalarNode):
                    after = lines[value.end_mark.line][value.end_mark.column:].strip() if value.style is None else ""
                    found.append((value.start_mark.line + 1, value.value, after))
                walk(value)
        elif isinstance(node, yaml.SequenceNode):
            for item in node.value:
                walk(item)

    if root is not None:
        walk(root)
    return found


def problems(text: str):
    out = []
    for line, value, after in descriptions(text):
        value = value.strip()
        if after.startswith("#"):
            out.append(f"line {line}: an unquoted ' #' starts a comment and cuts the text: {value[-40:]!r}")
        if value.count("(") != value.count(")"):
            out.append(f"line {line}: the brackets do not close: {value[-40:]!r}")
        title = len(value.split()) <= 8
        if value and value[-1] not in ".!?)\"'" and not title and "https://" not in value.split()[-1]:
            out.append(f"line {line}: the text does not end as a sentence: {value[-40:]!r}")
    return out


def test_there_are_files_to_read():
    assert len(FILES) > 100


@pytest.mark.parametrize("path", FILES, ids=[str(p.relative_to(ROOT)) for p in FILES])
def test_every_description_is_whole(path):
    assert problems(path.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("text, expected", [
    ("a:\n  description: Bars count rows (issue #68).\n", "cuts the text"),
    ("a:\n  description: \"Bars count rows (issue\"\n", "brackets do not close"),
    ("a:\n  description: Bars count rows for each sequence type and country of origin here\n", "does not end as a sentence"),
])
def test_the_check_can_fail(text, expected):
    assert any(expected in p for p in problems(text))


def test_a_quoted_text_with_a_hash_and_a_short_title_are_fine():
    assert problems('a:\n  description: "Bars count rows (issue #68)."\n  other:\n    description: Quality Control\n') == []
