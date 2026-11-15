"""The app of `test_join_preview_session_alive.py`: the real app with one staged fault.

The join preview function raises a NameError (a programming error), as a missing import once did. The fault is
injected here, in the test app; nothing in shipped code knows about it.
"""
from app.handlers import blueprint_handlers


def _fault(*args, **kwargs):
    raise NameError("name 'check_join_keys' is not defined (injected by the test)")


blueprint_handlers.run_join_preview = _fault

from app.src.main import app  # noqa: E402,F401  (imported after the fault is staged)
