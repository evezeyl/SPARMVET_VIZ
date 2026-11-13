"""
YAML loading that refuses a repeated key in one mapping, at any depth.

# @deps
# provides: function:load_strict, class:DuplicateKeyError
# consumed_by: libs/blueprint_arch/src/blueprint_arch/widget_text.py
# doc: .claude/design/recipe_format_spec.md (check T10)
# @end_deps

PyYAML keeps the last of two identical keys and says nothing, so `{old: x, old: y}` silently drops a rename and a
recipe with the same slug twice silently loses a field. The recipe format refuses it (check T10); this is the
building block. It is a plain `yaml.SafeLoader` otherwise: the file order of keys is kept.
"""
import yaml


class DuplicateKeyError(yaml.YAMLError):
    """The same key appears twice in one mapping."""


class _StrictLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: yaml.SafeLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    seen = {}
    for key_node, _value_node in node.value:
        try:
            key = loader.construct_object(key_node, deep=deep)
            hash(key)
        except TypeError:
            continue  # an unhashable key is an error that SafeLoader reports itself
        line = key_node.start_mark.line + 1
        if key in seen:
            raise DuplicateKeyError(
                f"the key '{key}' appears twice in one mapping (line {seen[key]} and line {line}); keep one"
            )
        seen[key] = line
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_strict(text: str):
    """Load one YAML document; raise `DuplicateKeyError` naming both lines when a mapping repeats a key."""
    return yaml.load(text, Loader=_StrictLoader)
