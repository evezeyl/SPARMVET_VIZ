"""A user folder that cannot be written is a warning, not a stop (D-0581)."""
import os

import pytest

from app.modules.session_manager import SessionManager, SessionsNotWritable

pytestmark = pytest.mark.skipif(os.geteuid() == 0, reason="root ignores folder permissions, so the folder cannot be made read-only")


@pytest.fixture
def ro_folder(tmp_path):
    tmp_path.chmod(0o500)
    yield tmp_path
    tmp_path.chmod(0o700)


def _write(sm):
    return sm.write_assembly_ghost("k1", "r", "a" * 12, "b" * 12, source_files={}, parquet_paths={})


def test_unwritable_folder_does_not_stop_the_manager(ro_folder):
    sm = SessionManager(ro_folder)
    assert sm.writable is False
    assert str(ro_folder) in sm.not_writable_text()


def test_unwritable_writes_nothing_and_raises_nothing(ro_folder):
    sm = SessionManager(ro_folder)
    assert _write(sm) is None
    assert sm.write_t3_ghost("k1", "r", "a" * 12, "b" * 12) is None
    assert sm.set_session_label("k1", "x") is None
    sm.delete_session("k1")
    assert sm.delete_all_sessions() == 0
    assert not (ro_folder / SessionManager.SESSIONS_DIR).exists()


def test_unwritable_lists_empty_and_export_import_say_so(ro_folder):
    sm = SessionManager(ro_folder)
    assert sm.list_all_sessions() == []
    assert sm.scan_sessions() == ([], [])
    with pytest.raises(SessionsNotWritable):
        sm.export_session_zip("k1")
    with pytest.raises(SessionsNotWritable):
        sm.import_session_zip(b"")


def test_writable_folder_behaves_as_before(tmp_path):
    sm = SessionManager(tmp_path)
    assert sm.writable is True
    path = _write(sm)
    assert path is not None and path.exists()
    assert [s["session_key"] for s in sm.list_all_sessions()] == ["k1"]
    assert not (tmp_path / SessionManager.SESSIONS_DIR / ".write_probe").exists()
