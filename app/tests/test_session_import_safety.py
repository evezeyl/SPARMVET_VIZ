"""Importing a session zip: the key that exists is asked, the member names are checked, the size is limited (D-0281, D-0283).

D-0281: "the app never overwrites silently"; the member names of the zip are checked before anything is written.
D-0283: "The size limit of the session zip is read from the deployment file" (zip size and unpacked size, before unpacking).
D-0050: "No silent error that is the rule." (a refusal names the member, the sizes, the limit and where it is set).

Every crafted zip is harmless: names only, written under a scratch folder; the tests check that nothing outside it appears.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION M1  import writes over an existing key without asking (the on_exists check is skipped)
  MUTATION M2  a member name with `..` is not refused
  MUTATION M3  a link member is not refused
  MUTATION M4  the declared unpacked size is not checked
  MUTATION M5  the zip file size is not checked
  MUTATION M6  the limit is not read from the deployment file (the default is always used)
  MUTATION M7  the handler imports straight away when the key exists (no question)
  MUTATION M8  cancel does not clear the waiting zip / writes it

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_import_safety.py -q

# @deps
# provides: test:session_import_safety
# consumes: app/modules/session_manager.py, app/handlers/session_handlers.py, app/src/bootloader.py
# consumed_by: CI
# doc: .claude/rules/ui_implementation_contract.md#12d
# @end_deps
"""
import hashlib
import io
import json
import zipfile
from types import SimpleNamespace

import pytest
import yaml
from shiny import reactive, render, ui

import app.handlers.session_handlers as session_handlers
from app.modules.session_manager import (
    DEFAULT_SESSION_IMPORT_MAX_UNPACKED_MB,
    DEFAULT_SESSION_IMPORT_MAX_ZIP_MB,
    SessionImportLimits,
    SessionImportRefused,
    SessionKeyExists,
    SessionManager,
    session_import_limits_from,
)
from app.tests.test_session_errors_visible import FakeInput

KEY = "aaaaaaaaaaaa:bbbbbbbbbbbb"
BIG = SessionImportLimits(max_zip_bytes=10**7, max_unpacked_bytes=10**8, where="the test")


def _session_zip(label="first", key=KEY):
    """A real session zip made by a real manager on a scratch folder (the export path of the app)."""
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as td:
        sm = SessionManager(Path(td))
        sm.write_assembly_ghost(key, "tiny", "a" * 64, "b" * 64, {}, {}, label=label)
        sm.write_t3_ghost(key, "tiny", "a" * 64, "b" * 64, "T3", [], {})
        return sm.export_session_zip(key)


def _zip_of(members):
    """members: list of (name, bytes) or (ZipInfo, bytes)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in members:
            zf.writestr(name, data)
    return buf.getvalue()


def _tree(root):
    return sorted((str(p.relative_to(root)), hashlib.sha256(p.read_bytes()).hexdigest())
                  for p in root.rglob("*") if p.is_file())


@pytest.fixture()
def sm(tmp_path):
    return SessionManager(tmp_path / "user")


# --------------------------------------------------------------------------- key exists

def test_a_normal_import_still_works(sm):
    assert sm.import_session_zip(_session_zip(), limits=BIG) == KEY
    assert sm.read_assembly_ghost(KEY)["data_analysis_recipe_id"] == "tiny"


def test_a_zip_whose_key_exists_writes_nothing_before_the_choice(sm):
    """MUTATION M1 fails here."""
    sm.import_session_zip(_session_zip("original"), limits=BIG)
    before = _tree(sm.root)
    with pytest.raises(SessionKeyExists) as err:
        sm.import_session_zip(_session_zip("incoming"), limits=BIG)
    assert err.value.session_key == KEY
    assert _tree(sm.root) == before, "nothing may change before the user chooses"
    assert not [p for p in sm.root.iterdir() if p.name.startswith(".")], "no temporary folder left"


def test_replace_replaces(sm):
    sm.import_session_zip(_session_zip("original"), limits=BIG)
    assert sm.import_session_zip(_session_zip("incoming"), limits=BIG, on_exists="replace") == KEY
    assert sm.read_assembly_ghost(KEY)["label"] == "incoming"
    assert [p.name for p in sm.root.iterdir()] == [KEY], "no backup or temporary folder left"


def test_keep_both_stores_a_second_session_under_another_key_and_lists_both(sm):
    sm.import_session_zip(_session_zip("original"), limits=BIG)
    new_key = sm.import_session_zip(_session_zip("incoming"), limits=BIG, on_exists="keep_both")
    assert new_key != KEY and new_key.startswith(KEY)
    assert sm.read_assembly_ghost(KEY)["label"] == "original", "the first session is untouched"
    copy = sm.read_assembly_ghost(new_key)
    assert copy["session_key"] == new_key, "the copy knows its own key, so restore and delete reach its own folder"
    assert "incoming" in copy["label"] and "Imported" in copy["label"] and KEY in copy["label"]
    assert {s["session_key"] for s in sm.list_all_sessions()} == {KEY, new_key}
    assert sm.list_t3_ghosts(new_key), "the saves of the copy are listed under the copy"
    sm.delete_session(new_key)
    assert sm.read_assembly_ghost(KEY) is not None, "deleting the copy leaves the first session"


def test_two_keep_both_imports_do_not_collide(sm):
    sm.import_session_zip(_session_zip(), limits=BIG)
    a = sm.import_session_zip(_session_zip(), limits=BIG, on_exists="keep_both")
    b = sm.import_session_zip(_session_zip(), limits=BIG, on_exists="keep_both")
    assert len({KEY, a, b}) == 3


def test_an_unknown_choice_is_refused_and_writes_nothing(sm):
    sm.import_session_zip(_session_zip(), limits=BIG)
    before = _tree(sm.root)
    with pytest.raises(ValueError):
        sm.import_session_zip(_session_zip(), limits=BIG, on_exists="overwrite")
    assert _tree(sm.root) == before


# --------------------------------------------------------------------------- member names

GOOD = (f"{KEY}/assembly.json", json.dumps({"session_key": KEY, "data_analysis_recipe_id": "t"}))


@pytest.mark.parametrize("bad", ["../escape.txt", f"{KEY}/../../escape.txt", "/abs/escape.txt", "C:/escape.txt",
                                 f"{KEY}\\..\\escape.txt", "other_key/assembly.json"])
def test_a_crafted_member_name_refuses_the_whole_zip_and_names_the_member(tmp_path, bad):
    """MUTATION M2 fails here."""
    sm = SessionManager(tmp_path / "user")
    data = _zip_of([GOOD, (bad, "x")])
    with pytest.raises(SessionImportRefused) as err:
        sm.import_session_zip(data, limits=BIG)
    assert bad in str(err.value), str(err.value)
    assert not [p for p in sm.root.rglob("*")], "nothing of the zip is written"
    assert not (tmp_path / "escape.txt").exists() and not (tmp_path / "user" / "escape.txt").exists()


def test_a_link_member_refuses_the_whole_zip_and_names_the_member(tmp_path):
    """MUTATION M3 fails here."""
    sm = SessionManager(tmp_path / "user")
    link = zipfile.ZipInfo(f"{KEY}/link")
    link.external_attr = (0o120777 << 16)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(GOOD[0], GOOD[1])
        zf.writestr(link, "/etc/passwd")
    with pytest.raises(SessionImportRefused) as err:
        sm.import_session_zip(buf.getvalue(), limits=BIG)
    assert f"{KEY}/link" in str(err.value) and "link" in str(err.value)
    assert not [p for p in sm.root.rglob("*")]


def test_the_first_bad_member_is_the_one_named(tmp_path):
    sm = SessionManager(tmp_path / "user")
    data = _zip_of([GOOD, ("../first.txt", "x"), ("../second.txt", "x")])
    with pytest.raises(SessionImportRefused) as err:
        sm.import_session_zip(data, limits=BIG)
    assert "../first.txt" in str(err.value) and "second.txt" not in str(err.value)


def test_a_zip_that_is_not_a_zip_is_refused_in_words(sm):
    with pytest.raises(SessionImportRefused) as err:
        sm.import_session_zip(b"not a zip", limits=BIG)
    assert "zip" in str(err.value).lower()


# --------------------------------------------------------------------------- size limit

def test_a_zip_over_the_file_size_limit_is_refused_with_both_sizes_and_the_place(sm):
    """MUTATION M5 fails here."""
    data = _session_zip()
    limits = SessionImportLimits(max_zip_bytes=100, max_unpacked_bytes=10**8,
                                 where="session_import.max_zip_mb in the deployment file /x/dep.yaml")
    with pytest.raises(SessionImportRefused) as err:
        sm.import_session_zip(data, limits=limits)
    text = str(err.value)
    assert str(len(data)) in text.replace(",", "") or f"{len(data) / 1e6:.3f}" in text or "KB" in text or "MB" in text
    assert "100" in text.replace(",", "") or "limit" in text.lower()
    assert "session_import.max_zip_mb in the deployment file /x/dep.yaml" in text
    assert not [p for p in sm.root.rglob("*")]


def test_a_small_zip_that_declares_a_large_unpacked_size_is_refused_before_unpacking(sm):
    """MUTATION M4 fails here: 5 MB of zeros packs to a few KB, under the file limit but over the unpacked limit."""
    data = _zip_of([GOOD, (f"{KEY}/t3_x.json", "0" * 5_000_000)])
    assert len(data) < 100_000
    limits = SessionImportLimits(max_zip_bytes=10**6, max_unpacked_bytes=1_000_000,
                                 where="session_import.max_unpacked_mb in the deployment file /x/dep.yaml")
    with pytest.raises(SessionImportRefused) as err:
        sm.import_session_zip(data, limits=limits)
    text = str(err.value)
    assert "unpacked" in text.lower() and "5" in text and "session_import.max_unpacked_mb" in text
    assert not [p for p in sm.root.rglob("*")]


def test_a_zip_at_the_limit_is_accepted(sm):
    data = _session_zip()
    limits = SessionImportLimits(max_zip_bytes=len(data), max_unpacked_bytes=10**8, where="x")
    assert sm.import_session_zip(data, limits=limits) == KEY


# --------------------------------------------------------------------------- where the limit comes from

def _write_deployment(tmp_path, block):
    path = tmp_path / "dep.yaml"
    path.write_text(yaml.safe_dump({"deployment_type": "filesystem", **block}))
    return path


def test_the_limit_is_read_from_the_deployment_file(tmp_path):
    """MUTATION M6 fails here."""
    path = _write_deployment(tmp_path, {"session_import": {"max_zip_mb": 2, "max_unpacked_mb": 7.5}})
    config = yaml.safe_load(path.read_text())
    limits = session_import_limits_from(config, str(path))
    assert limits.max_zip_bytes == 2 * 1024 * 1024 and limits.max_unpacked_bytes == int(7.5 * 1024 * 1024)
    assert str(path) in limits.where and "session_import.max_zip_mb" in limits.where


def test_the_default_is_used_when_the_key_is_absent(tmp_path):
    limits = session_import_limits_from({"deployment_type": "filesystem"}, "dep.yaml")
    assert limits.max_zip_bytes == int(DEFAULT_SESSION_IMPORT_MAX_ZIP_MB * 1024 * 1024)
    assert limits.max_unpacked_bytes == int(DEFAULT_SESSION_IMPORT_MAX_UNPACKED_MB * 1024 * 1024)
    assert "default" in limits.where.lower() and "session_import" in limits.where


def test_one_key_given_the_other_default(tmp_path):
    limits = session_import_limits_from({"session_import": {"max_zip_mb": 3}}, "dep.yaml")
    assert limits.max_zip_bytes == 3 * 1024 * 1024
    assert limits.max_unpacked_bytes == int(DEFAULT_SESSION_IMPORT_MAX_UNPACKED_MB * 1024 * 1024)


@pytest.mark.parametrize("bad", [{"max_zip_mb": 0}, {"max_zip_mb": -1}, {"max_zip_mb": "big"}, {"max_unpacked_mb": True},
                                 {"max_zip_mb": None}, {"typo_mb": 1}, "text"])
def test_a_wrong_value_or_unknown_key_is_refused_naming_the_key(bad):
    with pytest.raises(ValueError) as err:
        session_import_limits_from({"session_import": bad}, "dep.yaml")
    assert "session_import" in str(err.value) and "dep.yaml" in str(err.value)


def test_the_bootloader_gives_the_limits_of_its_deployment_and_the_shipped_files_are_valid():
    from pathlib import Path
    import glob
    for f in glob.glob("config/deployment/**/*.yaml", recursive=True):
        config = yaml.safe_load(Path(f).read_text()) or {}
        session_import_limits_from(config, f)
    from app.src.bootloader import Bootloader
    assert hasattr(Bootloader, "get_session_import_limits")


# --------------------------------------------------------------------------- the screen

class Screen:
    """`define_session_server` with plain functions, a real manager and a fake modal (as test_session_errors_visible)."""

    def __init__(self, tmp_path, monkeypatch, limits=BIG):
        self.functions, self.notes, self.modals = {}, [], []
        monkeypatch.setattr(reactive, "Effect", lambda fn: self.functions.setdefault(fn.__name__, fn))
        monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(render, "ui", lambda fn: self.functions.setdefault(fn.__name__, fn))
        monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(ui, "notification_show", lambda message, **kw: self.notes.append((kw.get("type"), str(message))))
        monkeypatch.setattr(ui, "modal_show", lambda m: self.modals.append(str(m)))
        monkeypatch.setattr(ui, "modal_remove", lambda: self.modals.append("REMOVED"))
        monkeypatch.setattr(session_handlers, "bootloader",
                            SimpleNamespace(is_enabled=lambda flag: True, get_session_import_limits=lambda: limits))
        self.manager = SessionManager(tmp_path / "user")
        self.upload = tmp_path / "upload.zip"
        self.input = FakeInput(session_import_upload=None, session_delete_all_btn=None, session_delete_all_confirm=None,
                               session_import_replace=None, session_import_keep=None, session_import_cancel=None)
        self.session = SimpleNamespace(on_flushed=lambda fn, once=True: fn())
        session_handlers.define_session_server(
            self.input, lambda fn: fn, self.session, session_manager=self.manager, current_app_features=None,
            home_state=reactive.Value({}), notification_log=reactive.Value([]),
            session_processing_issues=reactive.Value([]))

    def upload_zip(self, data):
        self.upload.write_bytes(data)
        self.input.values["session_import_upload"] = [{"datapath": str(self.upload), "name": "s.zip"}]
        self.run("_handle_session_import")

    def run(self, name):
        with reactive.isolate():
            return self.functions[name]()

    def texts(self, kind=None):
        return [m for t, m in self.notes if kind is None or t == kind]


def test_the_screen_asks_when_the_key_exists_and_writes_nothing(tmp_path, monkeypatch):
    """MUTATION M7 fails here."""
    screen = Screen(tmp_path, monkeypatch)
    screen.upload_zip(_session_zip("original"))
    assert screen.manager.read_assembly_ghost(KEY)["label"] == "original"
    screen.notes.clear()
    before = _tree(screen.manager.root)
    screen.upload_zip(_session_zip("incoming"))
    assert _tree(screen.manager.root) == before
    assert len(screen.modals) == 1
    assert "A session with this key already exists. Replace it, keep both, or cancel?" in screen.modals[0]
    assert KEY in screen.modals[0]
    assert not screen.texts("error")


def test_the_screen_replace_keep_and_cancel(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch)
    screen.upload_zip(_session_zip("original"))
    screen.upload_zip(_session_zip("incoming"))
    screen.input.values["session_import_replace"] = 1
    screen.run("_handle_import_replace")
    assert screen.manager.read_assembly_ghost(KEY)["label"] == "incoming"
    assert any("replaced" in m.lower() for m in screen.texts("message"))

    screen.upload_zip(_session_zip("third"))
    screen.run("_handle_import_keep")
    keys = {s["session_key"] for s in screen.manager.list_all_sessions()}
    assert len(keys) == 2 and KEY in keys
    assert screen.manager.read_assembly_ghost(KEY)["label"] == "incoming"


def test_cancel_leaves_the_store_byte_identical_and_forgets_the_zip(tmp_path, monkeypatch):
    """MUTATION M8 fails here."""
    screen = Screen(tmp_path, monkeypatch)
    screen.upload_zip(_session_zip("original"))
    screen.upload_zip(_session_zip("incoming"))
    before = _tree(screen.manager.root)
    screen.run("_handle_import_cancel")
    assert _tree(screen.manager.root) == before
    assert not [p for p in screen.manager.root.iterdir() if p.name.startswith(".")]
    # a later click on Replace with nothing waiting writes nothing and says so
    screen.notes.clear()
    screen.run("_handle_import_replace")
    assert _tree(screen.manager.root) == before
    assert screen.texts("error") or screen.texts("warning")


def test_the_screen_refusal_is_told_in_words(tmp_path, monkeypatch):
    limits = SessionImportLimits(max_zip_bytes=100, max_unpacked_bytes=10**8,
                                 where="session_import.max_zip_mb in the deployment file /x/dep.yaml")
    screen = Screen(tmp_path, monkeypatch, limits=limits)
    screen.upload_zip(_session_zip())
    errors = screen.texts("error")
    assert len(errors) == 1 and "session_import.max_zip_mb" in errors[0], screen.notes
    assert not list(screen.manager.root.rglob("*"))
