"""A repeated key in one mapping is an error at any depth (check T10 of the recipe format specification).

PyYAML keeps the last of two identical keys without a message; `load_strict` refuses them and names both lines.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_strict_yaml.py -q
"""
import pytest
import yaml

from utils.strict_yaml import DuplicateKeyError, load_strict


def test_a_normal_document_loads_like_safe_load():
    text = "a: 1\nb: [x, y]\nc: {d: 2}\n"
    assert load_strict(text) == yaml.safe_load(text)


def test_the_file_order_of_keys_is_kept():
    assert list(load_strict("z: 1\na: 2\nm: 3\n")) == ["z", "a", "m"]


def test_a_repeated_key_is_refused_and_both_lines_are_named():
    with pytest.raises(DuplicateKeyError) as err:
        load_strict("a: 1\nb: 2\na: 3\n")
    assert "'a'" in str(err.value) and "line 1" in str(err.value) and "line 3" in str(err.value)


def test_a_repeated_key_inside_a_flow_mapping_is_refused():
    with pytest.raises(DuplicateKeyError):
        load_strict("mapping: {old: x, old: y}\n")


def test_a_repeated_key_deep_inside_a_list_of_mappings_is_refused():
    with pytest.raises(DuplicateKeyError):
        load_strict("steps:\n  - action: join\n    how: left\n    how: inner\n")


def test_the_same_key_in_different_mappings_is_fine():
    """Identical keys in different mappings are normal (sample_id in every table)."""
    assert load_strict("t1: {sample_id: {type: categorical}}\nt2: {sample_id: {type: categorical}}\n")["t2"]


def test_a_yaml_error_is_still_a_yaml_error():
    with pytest.raises(yaml.YAMLError):
        load_strict("a: [1, 2\n")
    assert issubclass(DuplicateKeyError, yaml.YAMLError)


def test_an_empty_text_is_none():
    assert load_strict("") is None
