"""HOME-WALK G: the HOME help page says what is built and no longer says that exploration filters are saved with a session."""
from pathlib import Path

HELP = (Path(__file__).resolve().parents[1] / "src" / "help" / "home.md").read_text(encoding="utf-8")


def test_the_help_does_not_say_that_filter_state_is_saved():
    assert "filter state" not in HELP
    assert "Exploration filters are never saved" in HELP


def test_the_help_names_what_is_on_the_screen():
    for needle in ("seed", "Reshuffle", "Remove the pinned seed", "**Info**", "**Alerts**", "Import a bundle"):
        assert needle in HELP, needle
