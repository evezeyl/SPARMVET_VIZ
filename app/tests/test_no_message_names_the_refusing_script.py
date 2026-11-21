"""No runtime text of the app, the libraries or the audit scripts tells a user to run `migrate_plot_specs.py`.

That script refuses to run (D-0236, D-0237). A message that sends the user to it is a half fix: the user follows the
instruction and meets a refusal. Rule files are not scanned here: their wording is Eve's to change.
The one exemption: the list of engine places names source files, so an entry of that list that opens with the script's own
path is data naming a file, not a message to a user; any other text of that file that names the script is still flagged.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_no_message_names_the_refusing_script.py -q
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCANNED = [ROOT / "app", *sorted((ROOT / "libs").glob("*/src")), ROOT / "scripts"]
NAME = "migrate_plot_specs"
LIST_FILE = "libs/utils/src/utils/engine_boundary.py"
LIST_ENTRY_START = f'("assets/scripts/{NAME}.py",'


def is_list_entry(relative, line):
    return relative == LIST_FILE and line.lstrip().startswith(LIST_ENTRY_START)


def python_files():
    for base in SCANNED:
        for path in base.rglob("*.py"):
            if "tests" in path.relative_to(ROOT).parts or path.name.startswith("test_"):
                continue
            yield path


def offending_lines():
    found = []
    for path in python_files():
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            relative = str(path.relative_to(ROOT))
            if is_list_entry(relative, line):
                continue
            if NAME in line and not line.lstrip().startswith("#") and "mirrors" not in line:
                found.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    return found


def test_no_runtime_message_names_the_refusing_script():
    assert offending_lines() == []


def test_the_scan_sees_files():
    assert len(list(python_files())) > 100


def test_the_scan_can_fail(tmp_path, monkeypatch):
    bad = tmp_path / "m.py"
    bad.write_text(f'MSG = "Run assets/scripts/{NAME}.py --apply"\n', encoding="utf-8")
    monkeypatch.setattr(__import__(__name__), "SCANNED", [tmp_path], raising=False)
    import sys
    module = sys.modules[__name__]
    monkeypatch.setattr(module, "SCANNED", [tmp_path])
    monkeypatch.setattr(module, "ROOT", tmp_path)
    assert offending_lines() != []


def test_the_list_exemption_is_narrow(tmp_path, monkeypatch):
    import sys
    module = sys.modules[__name__]
    listing = tmp_path / LIST_FILE
    listing.parent.mkdir(parents=True)
    listing.write_text(
        f'    ("assets/scripts/{NAME}.py", _G, X, "data"),\n'
        f'MSG = "Run {NAME}.py to fix this"\n'
        f'    ("other/{NAME}.py", _G, X, "data"),\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "SCANNED", [tmp_path])
    monkeypatch.setattr(module, "ROOT", tmp_path)
    found = offending_lines()
    assert len(found) == 2
    assert all("Run " in f or "other/" in f for f in found)
