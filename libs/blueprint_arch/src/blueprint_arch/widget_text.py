"""
Text for the `list` and `mapping` widgets of the Blueprint form: a value is shown as one line of YAML and read back.

# @deps
# provides: function:value_to_text, function:text_to_value
# consumes: libs/utils/src/utils/ui_schema.py, libs/utils/src/utils/strict_yaml.py
# consumed_by: app/modules/wrangle_studio.py, app/handlers/blueprint_handlers.py
# doc: .claude/design/recipe_format_spec.md (section 8, R1)
# @end_deps

Headless (no Shiny). Before these widgets existed, parameters such as `rename.mapping` were declared `string`: the
form showed the Python repr of the dictionary and saved the typed text as a string, which the action cannot use.
"""
from typing import Any, Optional

import yaml

from utils.strict_yaml import DuplicateKeyError, load_strict
from utils.ui_schema import shape_problem


def value_to_text(param_def: dict, value: Any) -> str:
    """The value as one line of YAML: `[a, b]`, `{old: new}`; a string is shown as it is; None is empty."""
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value
    return yaml.safe_dump(value, default_flow_style=True, sort_keys=False, allow_unicode=True, width=10**6).strip()


def text_to_value(param_def: dict, text: Optional[str]) -> Any:
    """Read the typed text as a list or a mapping. Blank text is None. A wrong form raises ValueError with the fix."""
    text = (text or "").strip()
    if not text:
        return None
    hint = param_def.get("hint")
    try:
        value = load_strict(text)
    except DuplicateKeyError as err:
        raise ValueError(str(err))
    except yaml.YAMLError:
        raise ValueError("this is not valid YAML" + (f"; write it like {hint}" if hint else ""))
    problem = shape_problem(param_def, value)
    if problem:
        raise ValueError(problem + (f" (like {hint})" if hint else ""))
    return value
