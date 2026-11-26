"""The plain words of a filter: its value and what happens to the rows with no value (display only)."""
import math

import pytest

from utils.filter_words import no_value_words, value_text


@pytest.mark.parametrize("value, text", [
    (2024.0, "2024"), (2024, "2024"), (-3.0, "-3"), (0.0, "0"), (2.5, "2.5"), (0.1, "0.1"), ("2024.0", "2024.0"), ("abc", "abc"),
    (True, "True"), (None, "None"), (float("nan"), "nan"), (math.inf, "inf"), (1e20, "1e+20"), (123456789012345.0, "123456789012345"),
])
def test_value_text(value, text):
    assert value_text(value) == text


def test_a_text_that_looks_like_a_decimal_is_not_rewritten():
    assert value_text("2024.0") == "2024.0"          # a text column's value is shown as it is


def test_no_value_words_name_the_column_and_the_fate():
    assert no_value_words("remove", "year") == "rows with no year record are removed"
    assert no_value_words("keep", "Collection Year") == "rows with no Collection Year record are kept"


def test_an_unknown_choice_is_refused_never_guessed():
    with pytest.raises(ValueError):
        no_value_words("maybe", "year")
