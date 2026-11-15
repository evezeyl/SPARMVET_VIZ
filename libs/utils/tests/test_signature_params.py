"""The shared reader of a wrapped object's parameters: names, renames, defaults, and an error that names the owner."""
import inspect

import pytest

from utils.signature_params import ParameterReadError, call_arguments, read_parameters, widget_for_default


def _call(a, b=2, *rest, c=None, **extra):
    return a, b, rest, c, extra


class _Thing:
    def method(self, x, y=1.5):
        return x, y

    @classmethod
    def build(cls, z=True):
        return cls, z


def test_every_parameter_is_read_in_signature_order_with_its_kind_and_default():
    read = read_parameters(_call, "owner")
    assert [p.name for p in read] == ["a", "b", "rest", "c", "extra"]
    assert [p.required_by_signature for p in read] == [True, False, False, False, False]
    assert [p.variadic for p in read] == [False, False, True, False, True]
    assert read[1].default == 2 and read[1].has_default and not read[0].has_default


def test_self_and_cls_are_left_out():
    assert [p.name for p in read_parameters(_Thing.method, "owner")] == ["x", "y"]
    assert [p.name for p in read_parameters(_Thing.build, "owner")] == ["z"]


def test_a_rename_changes_the_recipe_name_and_keeps_the_signature_name():
    (first, *_) = read_parameters(_call, "owner", {"a": "alpha"})
    assert (first.name, first.source) == ("alpha", "a")


def test_a_positional_only_parameter_is_flagged():
    def f(a, /, b):
        return a, b
    assert [p.positional_only for p in read_parameters(f, "owner")] == [True, False]


def test_an_object_without_a_signature_is_an_error_that_names_the_owner():
    with pytest.raises(ParameterReadError, match="my_component"):
        read_parameters(5, "my_component")


def test_call_arguments_gives_the_step_values_under_the_signature_names():
    spec = {"alpha": 1, "b": None, "c": 3, "unknown": 9}
    assert call_arguments(_call, spec, "owner", {"a": "alpha"}) == {"a": 1, "c": 3}


def test_call_arguments_skips_the_named_parameters_and_kwargs():
    spec = {"a": 1, "rest": [1], "extra": {"q": 1}}
    assert call_arguments(_call, spec, "owner", skip=("rest",)) == {"a": 1}


def test_call_arguments_of_an_empty_step_is_empty():
    assert call_arguments(_call, {}, "owner") == {}


def test_widget_for_default():
    assert widget_for_default(True) == "bool"
    assert widget_for_default(0) == "number"
    assert widget_for_default(1.5) == "number"
    assert widget_for_default("x") is None
    assert widget_for_default(None) is None
    assert widget_for_default(inspect.Parameter.empty) is None
