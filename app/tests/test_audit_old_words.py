"""The old-words audit (ADR-091) counts what it must and skips what it must."""
import importlib.util
import re
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "audit_old_words", Path(__file__).resolve().parents[2] / "assets" / "scripts" / "audit_old_words.py"
)
audit = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(audit)


def _rx(*names):
    return {n: re.compile(audit.WORDS[n], re.IGNORECASE) for n in names}


def test_counts_word_in_path_and_content(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "persona_notes.md").write_text("a Persona and another PERSONA\nnothing\n")
    counts, hits, _ = audit.scan(["persona_notes.md"], _rx("persona"), False)
    assert counts[("persona", "path", "persona_notes.md")] == 1
    assert counts[("persona", "content", "persona_notes.md")] == 2
    assert [h[3] for h in hits if h[1] == "content"] == [1]


def test_new_term_is_not_counted_as_old_recipe(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("data_analysis_recipe is new\na recipe is old\n")
    counts, _, _ = audit.scan(["a.txt"], _rx("recipe"), False)
    assert counts[("recipe", "content", "a.txt")] == 1


def test_nothing_found_in_a_clean_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "clean.txt").write_text("deployment and app features only\n")
    counts, hits, _ = audit.scan(["clean.txt"], _rx("persona", "manifest", "recipe", "profile"), False)
    assert not counts and not hits


def test_excluded_history_is_skipped_unless_asked(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    hist = tmp_path / ".claude" / "logs"
    hist.mkdir(parents=True)
    (hist / "old.md").write_text("persona\n")
    path = ".claude/logs/old.md"
    assert audit.is_excluded(path)
    counts, _, _ = audit.scan([path], _rx("persona"), False)
    assert not counts
    counts, _, _ = audit.scan([path], _rx("persona"), True)
    assert counts


def test_binary_file_is_skipped_not_crashed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "b.bin").write_bytes(b"\xff\xfe\x00persona")
    counts, _, skipped = audit.scan(["b.bin"], _rx("persona"), False)
    assert skipped == 1 and not counts
