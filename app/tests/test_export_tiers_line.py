"""HOME-WALK F: the "Tiers" line of the README names the tiers whose tables are in the bundle (T2 was missing when T2 files were written)."""
from app.handlers.export_handlers import exported_tiers


def test_the_tiers_line_names_every_tier_that_has_a_table_in_the_bundle():
    assert exported_tiers(has_t2=False, has_t3=False) == ["T1"]
    assert exported_tiers(has_t2=True, has_t3=False) == ["T1", "T2"]
    assert exported_tiers(has_t2=False, has_t3=True) == ["T1", "T3"]
    assert exported_tiers(has_t2=True, has_t3=True) == ["T1", "T2", "T3"]
