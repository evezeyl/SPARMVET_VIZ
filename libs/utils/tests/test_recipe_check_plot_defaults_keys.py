"""`plot_defaults_keys` gives the allowed and the removed keys of `plot_defaults` from the specification."""
from utils.recipe_check import plot_defaults_keys, spec


def test_allowed_and_removed_come_from_the_spec():
    allowed, removed = plot_defaults_keys()
    assert tuple(allowed) == tuple(spec()["elements"]["plot_defaults"]["optional"])
    assert tuple(removed) == tuple(spec()["removed"]["plot_defaults"])


def test_no_key_is_both_allowed_and_removed():
    allowed, removed = plot_defaults_keys()
    assert not set(allowed) & set(removed)
    assert allowed and removed
